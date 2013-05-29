#!/usr/bin/python
"""
"""

import os
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
import string
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
sys.path.append('../lib')
from apiary import ApiaryBot


class WorkerBee(ApiaryBot):
    def __init__(self):
        ApiaryBot.__init__(self)

    def UpdateTotalEdits(self):
        sql_query = """
SELECT
    SUM(a.edits) AS total_edits
FROM statistics a
INNER JOIN (
    SELECT
        website_id, MAX(capture_date) AS max_date
    FROM
        statistics
    GROUP BY
        website_id) as b
ON
    a.website_id = b.website_id AND
    a.capture_date = b.max_date
"""

        # Get the total edit count
        cur = self.apiary_db.cursor()
        cur.execute(sql_query)
        data = cur.fetchone()
        if self.args.verbose >= 2:
            print "Total edits: %d" % data[0]

        # Update the wiki with the new value
        c = self.apiary_wiki.call({
            'action': 'edit',
            'title': 'WikiApiary:Total edits',
            'text': data[0],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.edit_token
        })
        if self.args.verbose >= 3:
            print c

        return True

    def main(self):
        # Setup our connection to the wiki too
        self.connectwiki('Worker Bee')

        # Now perform our jobs
        self.UpdateTotalEdits()

# Run
if __name__ == '__main__':
    bot = WorkerBee()
    bot.main()
