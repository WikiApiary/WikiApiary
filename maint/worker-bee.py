#!/usr/bin/python
"""
Maintenance script that performs various routine tasks
to keep the database maintained and update the wiki
with some calculations.
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
from apiary import bot


class WorkerBee(Bot):
    def __init__(self):
        Bot.__init__(self)

    def UpdateTotalEdits(self):
        """Find total queries in database and update wiki value."""
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
        """Delete old records from the SQL log table."""
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
        """Delete old records for the SQL log table for websites."""
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
        """Do the work..."""
        # Setup our connection to the wiki too
        self.connectwiki('Worker Bee')

        # Now perform our jobs
        self.UpdateTotalEdits()

        # Delete old bot_log entries
        self.DeleteOldBotLogs()

        # Delete old website_logs entries
        self.DeleteOldWebsiteLogs()

# Run
if __name__ == '__main__':
    bot = WorkerBee()
    bot.main()
