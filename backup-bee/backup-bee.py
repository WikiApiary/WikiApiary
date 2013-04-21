#!/usr/bin/python
"""
Backup Bee

This bot should be ran once every hour. On each run it will check for websites
that have a Has day segment and Has hour segment set to the current day of week
and hour (UTC time). It will then take backup actions against the websites in
that group.

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
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
import subprocess as sub
import shlex
sys.path.append('../lib')
from apiary import ApiaryBot


class BackupBee(ApiaryBot):
    def __init__(self):
        ApiaryBot.__init__(self)
        # Initialize stats
        self.stats['backup_count'] = 0
        self.stats['backup_success'] = 0
        self.stats['backup_failure'] = 0

    def build_log_page(self, message, output, errors):
        template = """
'''Status:''' %s

=== Output ===
<pre>
%s
</pre>

=== Errors ===
<pre>
%s
</pre>
"""
        return template % (message, output, errors)

    def update_backup_status(self, pagename, message, output, errors):
        self.stats['backup_success'] += 1
        # Backup completed
        if self.args.verbose >= 2:
            print "%s backup completed, updating backup date." % pagename

        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': pagename,
            'Website[Backup date]': time.strftime('%B %d, %Y %I:%M:%S %p', time.gmtime()),
            'wpSummary': 'Backup completed.'})
        if self.args.verbose >= 3:
            print c

        logpage = "%s/Backup log" % pagename
        socket.setdefaulttimeout(30)
        page_text = self.build_log_page(message, output, errors)
        c = self.apiary_wiki.call({'action': 'edit', 'title': logpage, 'text': page_text, 'token': self.edit_token, 'bot': 'true'})

    def backup_site(self, site):
        if self.args.verbose >= 3:
            print "\n\nSite: ", site

        start_time = time.time()

        api_url = site[1]['printouts']['Has API URL'][0]

        # TODO: Should probably do something here to make sure the API is at least
        # responding before we attempt to backup.

        site_id = site[1]['printouts']['Has ID'][0]
        backup_type = site[1]['printouts']['Has backup type'][0]
        backup_path = "%s/%d/%d/%s" % (
            self.config.get('Backup Bee', 'dumppath'),
            site_id / 100,
            site_id,
            time.strftime('%Y%m%d-%H%M%S', time.gmtime()))
        if self.args.verbose >= 2:
            print "Backup path is %s" % backup_path

        # Build the dump command
        dump_cmd = "%s --xml --curonly --api=%s --path=%s" % (
            self.config.get('Backup Bee', 'dumpgenerator'),
            api_url,
            backup_path)
        if self.args.verbose >= 2:
            print "Dump command is %s" % dump_cmd

        message = "[[%s]] Starting %s backup using %s." % (site[0], backup_type, api_url)
        self.botlog(bot='Backup Bee', type='info', message=message)

        p = sub.Popen(shlex.split(dump_cmd), stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()

        duration = time.time() - start_time
        message = "Last backup at %s took %s minutes." % (
            time.strftime('%B %d, %Y %I:%M:%S %p', time.gmtime()),
            float(duration/60))
        self.update_backup_status(site[0], message, output, errors)

        message = "[[%s]] Completed %s backup." % (site[0], backup_type)
        self.botlog(bot='Backup Bee', type='info', message=message, duration=duration)

    def get_backup_list(self, count=20):
        my_query = ''.join([
            #"[[Has day segment:%s]]" % time.strftime('%w', time.gmtime()),
            #"[[Has hour segment::%s]]" % time.strftime('%H', time.gmtime()),
            #"[[Has farm::Farm:thingelstad.com]]",     # For debugging only use my sites
            "[[wiki_thing]]",     # For debugging only one site
            "[[Is active::True]]",
            "[[Is defunct::False]]",
            "[[Has backup type::+]]",
            "|?Has backup type",
            "|?Has ID",
            '|?Has API URL',
            '|sort=Creation date',
            '|order=rand',
            "|limit=%d" % count])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(sites['query']['results']) > 0:
            return len(sites['query']['results']), sites['query']['results'].items()
        else:
            return 0, None

    def main(self):
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Backup Bee')

        # Get list of sites to backup
        (site_count, sites) = self.get_backup_list(count=20)
        if site_count > 0:
            message = "Starting backups for %d sites." % site_count
            self.botlog(bot='Backup Bee', message=message)
            for site in sites:
                self.stats['backup_count'] += 1
                self.backup_site(site)

        duration = time.time() - start_time
        if self.stats['backup_count'] > 0:
            message = "Completed backup %d sites %d succeeded %d failed" % (
                self.stats['backup_count'],
                self.stats['backup_success'],
                self.stats['backup_failure'])
            if self.args.verbose >= 1:
                print message
            self.botlog(bot='Backup Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = BackupBee()
    bee.main()
