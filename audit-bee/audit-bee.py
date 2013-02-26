#!/usr/bin/python
"""
General data requires MediaWiki 1.8 or later.
Extension data requires MediaWiki 1.14 or later.
Skin data requires MediaWiki 1.18 or later.
General statistics requires MediaWiki 1.11 or later.
Semantic statistics requires Semantic MediaWiki 1.6 or later.

Basic flow of Audit Bee:
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
sys.path.append('../lib')
from apiary import ApiaryBot

class AuditBee(ApiaryBot):
    def set_flag(self, pagename, name, value, comment):
        if self.args.verbose >= 3:
            print "%s setting %s to %s (%s)." % (pagename, name, value, comment)

    def set_audit(self, site, data):
        if self.args.verbose >= 3:
            print "Website: %s  Generator: %s" % (site[0], data['generator'])

        match = re.search(r'\s(\d+)\.(\d+)', data['generator'])

        (mw_version_major, mw_version_minor) = (int(match.group(1)), int(match.group(2)))

        print "Major: %d  Minor: %d" % (mw_version_major, mw_version_minor)

        if (mw_version_major >= 1) and (mw_version_minor >= 8) and (site[1]['printouts']['Collect general data'][0] == "f"):
            self.set_flag(site[0], 'Collect general data', 'Yes', "MediaWiki %d.%d supports data collection" % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor >= 14) and (site[1]['printouts']['Collect extension data'][0] == "f"):
            self.set_flag(site[0], 'Collect extension data', 'Yes', "Enabling extension collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor < 14) and (site[1]['printouts']['Collect extension data'][0] == "t"):
            self.set_flag(site[0], 'Collect extension data', 'No', "Disabling extensions collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor >= 18) and (site[1]['printouts']['Collect skin data'][0] == "f"):
            self.set_flag(site[0], 'Collect skin data', 'Yes', "MediaWiki %d.%d supports skin collection" % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor >= 11) and (site[1]['printouts']['Collect statistics'][0] == "f"):
            self.set_flag(site[0], 'Collect statistics', 'Yes', "MediaWiki %d.%d supports statistics collection" % (mw_version_major, mw_version_minor))


    def audit_site(self, site):
        if self.args.verbose >= 3:
            print "Site: ", site
        data_url = site[1]['printouts']['Has API URL'][0] + "?action=query&meta=siteinfo&siprop=general&format=json"
        if self.args.verbose >= 2:
            print "Pulling general info info from %s." % data_url
        (success, data, duration) = self.pull_json(site[0], data_url)

        if success:
            if 'query' in data:
                self.set_audit(site, data['query']['general'])
            else:
                message = "[[%s]] Returned unexpected JSON while auditing." % site[0]
                self.botlog(bot='Audit Bee', type='warn', message=message)

    def get_audit_list(self):
        my_query = ''.join(['[[Concept:Websites never audited]]',
            '|?Has API URL',
            '|?Collect general data', '|?Collect extension data', '|?Collect skin data',
            '|?Collect statistics|', '?Collect semantic statistics',
            '|sort=Creation date', '|order=rand', '|limit=1'])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        return len(sites['query']['results']), sites['query']['results'].items()

    def main(self):
        self.botlog(bot='Audit Bee', message='Starting audit run.')
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Audit Bee')

        (site_count, sites) = self.get_audit_list()
        
        i = 0
        if site_count > 0:
            i += 1
            for site in sites:
                self.audit_site(site)
        else:
            self.botlog(bot='Audit Bee', message='No sites to audit.')

        duration = time.time() - start_time
        message = "Completed audit of %d sites." % i
        self.botlog(bot='Audit Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = AuditBee()
    bee.main()

