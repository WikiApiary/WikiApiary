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

    def UpdateTagline(self):
        tagline_template = """{{#switch: {{NAMESPACENUMBER}}
| 0 = From WikiApiary, monitoring {{PAGENAME}} and over {{formatnum:%d}} other wikis
| 800 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other extensions
| 802 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other farms
| 804 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other skins
| From WikiApiary, monitoring the MediaWiki universe
}}
"""

        count_wiki = 19400
        count_extensions = 4600
        count_farms = 100
        count_skins = 1300

        tagline_page = tagline_template % (count_wiki, count_extensions, count_farms, count_skins)

        # Update MediaWiki:Tagline
        c = self.apiary_wiki.call({
            'action': 'edit',
            'title': 'MediaWiki:Tagline',
            'text': tagline_page,
            'bot': True,
            'summary': 'Updating tagline with new values',
            'minor': True,
            'token': self.edit_token
        })
        print c

    def UpdateTotalEdits(self):
        sql_query = """
SELECT
    SUM(a.edits) AS total_edits,
    SUM(a.activeusers) AS total_active_users,
    SUM(a.pages) AS total_pages
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
        if self.args.verbose >= 1:
            print "Total edits: %d" % data[0]
            print "Total active users: %d" % data[1]
            print "Total pages: %d" % data[2]

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

        # Update the wiki with the new value
        c = self.apiary_wiki.call({
            'action': 'edit',
            'title': 'WikiApiary:Total active users',
            'text': data[1],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.edit_token
        })
        if self.args.verbose >= 3:
            print c

        # Update the wiki with the new value
        c = self.apiary_wiki.call({
            'action': 'edit',
            'title': 'WikiApiary:Total pages',
            'text': data[2],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.edit_token
        })
        if self.args.verbose >= 3:
            print c

        return True

    def DeleteOldBotLogs(self):
        sql_query = """
DELETE FROM
    apiary_bot_log
WHERE
    log_date < '%s'
"""
        delete_before = datetime.datetime.utcnow() - datetime.timedelta(weeks=4)
        delete_before_str = delete_before.strftime('%Y-%m-%d %H:%M:%S')
        if self.args.verbose >= 1:
            print "Deleting apiary_bot_log before %s." % delete_before_str
        my_sql = sql_query % (delete_before_str)

        (success, rows_deleted) = self.runSql(my_sql)

        if self.args.verbose >= 1:
            print "Deleted %d rows." % rows_deleted

        return True

    def DeleteOldWebsiteLogs(self):
        sql_query = """
DELETE FROM
   apiary_website_logs
WHERE
   log_date < '%s'
"""
        delete_before = datetime.datetime.utcnow() - datetime.timedelta(weeks=8)
        delete_before_str = delete_before.strftime('%Y-%m-%d %H:%M:%S')
        if self.args.verbose >= 1:
            print "Deleting apiary_website_logs before %s." % delete_before_str
        my_sql = sql_query % (delete_before_str)

        (success, rows_deleted) = self.runSql(my_sql)

        if self.args.verbose >= 1:
            print "Deleted %d rows." % rows_deleted

        return True

    def main(self):
        # Setup our connection to the wiki too
        self.connectwiki('Worker Bee')

        # Now perform our jobs
        #self.UpdateTotalEdits()
        self.UpdateTagline()

        # Delete old bot_log entries
        #self.DeleteOldBotLogs()

        # Delete old website_logs entries
        #self.DeleteOldWebsiteLogs()

# Run
if __name__ == '__main__':
    bot = WorkerBee()
    bot.main()
