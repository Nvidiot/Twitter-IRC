# coding=utf8
"""sopel-twitter
Twitter plugin for Sopel
"""
from __future__ import unicode_literals, absolute_import, division, print_function

# replace with `importlib_metadata` when updating for Sopel 8.0
import pkg_resources

from .twitter import *

__author__ = 'Nvidiot'
__email__ = 'no'
__version__ = pkg_resources.get_distribution('sopel_modules.twitter').version