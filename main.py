from snscrape.modules.twitter import TwitterProfileScraper, TwitterTweetScraper

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
]

def _is_followed(username):
    # returns True if username is already being followed, False otherwise
    for user in USER_LIST:
        if user.lower() == username.lower():
            return True
    return False







if __name__ == '__main__':
    print("Startup")
    twitter_scraper = TwitterProfileScraper('jeff_foust')
    for tweet in twitter_scraper.get_items():
        if tweet.retweetedTweet:
            # No retweets
            continue
        if tweet.inReplyToTweetId:
            t = TwitterTweetScraper(tweet.inReplyToTweetId)
            replied_to_tweet = list(t.get_items())[0]
            print(_is_followed(replied_to_tweet.user.username))
        print(tweet.content)

    print("End")
