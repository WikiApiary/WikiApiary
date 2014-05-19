"""
Base class for all WikiApiary bots. To make another bot, create a new class derived
from this class.
"""

import sys
import time
import datetime
import pytz
import ConfigParser
import argparse
import socket
import MySQLdb as mdb
import simplejson
import urllib2
import random
import re
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki


class Bot(object):
    """Base class for all WikiApiary bots."""

    def noop(self):
        """This class no longer seems to have a use?"""
        pass
