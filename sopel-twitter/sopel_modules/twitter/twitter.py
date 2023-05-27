# coding=utf8
"""Twitter plugin for Sopel"""
from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime, timezone, timedelta
from html import unescape

from sopel.plugin import interval
from sopel import tools
from snscrape.modules.twitter import TwitterProfileScraper, TwitterTweetScraper
from snscrape.base import ScraperException


CHANNEL = '#SpaceX'
USER_LIST = [
    'NASASpaceflight',
    'RGVaerialphotos',
    'RingWatchers',
    'SciGuySpace',
    'SpaceOffshore',
    'SpaceX',
    'SpaceflightNow',
    'blueorigin',
    'bocachicagal',
    'boringcompany',
    'daily_hopper',
    'flatoday_jdean',
    'jeff_foust',
    'lorengrush',
    'lrocket',
    'nasawebb',
    'nextspaceflight',
    'planet4589',
    'tesla',
    'thesheetztweetz',
    'torybruno',
]

UPDATE_INTERVAL = 60

LOGGER = tools.get_logger('twitter')


def _get_tweets(user, max_tweets=10):
    # returns a list of tweets, reverse order from the user, limited to max_tweets
    # retweets are ignored
    twitter_scraper = TwitterProfileScraper(user)
    last_tweets = []
    tweet_counter = 0
    try:
        for tweet in twitter_scraper.get_items():
            if tweet.retweetedTweet:
                # No retweets
                continue

            tweet_counter += 1
            if tweet_counter > max_tweets:
                # Only check the last 10 tweets
                break

            last_tweets.append(tweet)
    except (ScraperException, KeyError):
        LOGGER.exception(f'Failed to get tweets for: {user}')
        return []
    return reversed(last_tweets)


def _cleanup(tweet_content):
    # Cleans up tweet content for sending to IRC
    return unescape(tweet_content.replace('\n', '⏎'))


def _is_followed(username):
    # returns True if username is already being followed, False otherwise
    for user in USER_LIST:
        if user.lower() == username.lower():
            return True
    return False


def _say(bot, tweet, *, add_url=False):
    if add_url:
        bot.say(f'[Twitter] @{tweet.user.username}: '
                f'{_cleanup(tweet.rawContent)} '
                f'{tweet.url}',
                CHANNEL)
    else:
        bot.say(f'[Twitter] @{tweet.user.username}: '
                f'{_cleanup(tweet.rawContent)}',
                CHANNEL)


def setup(bot):
    LOGGER.info("Updating last seen timestamps for configured users")
    # Store most recent tweet timestamp from the last 10 tweets per-user
    for user in USER_LIST:
        # Default value for oldest seen tweet = 10 years ago
        bot.memory[f'last_tweet_ts_{user}'] = datetime.now(timezone.utc) - timedelta(days=10 * 365)
        for tweet in _get_tweets(user):
            if tweet.date > bot.memory[f'last_tweet_ts_{user}']:
                bot.memory[f'last_tweet_ts_{user}'] = tweet.date
    LOGGER.info("Plugin initialized")


@interval(UPDATE_INTERVAL)
def twitter_check(bot):
    check_start = datetime.now()

    for user in USER_LIST:
        for tweet in _get_tweets(user):
            if tweet.date > bot.memory[f'last_tweet_ts_{user}']:
                if tweet.inReplyToTweetId:
                    # Reply tweet
                    t = TwitterTweetScraper(tweet.inReplyToTweetId)
                    replied_to_tweet = list(t.get_items())[0]

                    if not _is_followed(replied_to_tweet.user.username):
                        # Not already following the replied-to tweet user, post replied-to tweet
                        _say(bot, replied_to_tweet, add_url=True)

                    _say(bot, tweet, add_url=False)
                elif tweet.quotedTweet:
                    # Quoted tweet
                    if not _is_followed(tweet.quotedTweet.user.username):
                        # Not already following the quoted tweet user, post quoted tweet
                        _say(bot, tweet.quotedTweet, add_url=True)

                    _say(bot, tweet, add_url=True)
                else:
                    # Regular tweet
                    _say(bot, tweet, add_url=False)
                bot.memory[f'last_tweet_ts_{user}'] = tweet.date

    check_end = datetime.now()
    if check_end - check_start > timedelta(seconds=UPDATE_INTERVAL):
        LOGGER.warning("Checking twitter took longer than configured UPDATE_INTERVAL")
