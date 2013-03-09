#!/usr/bin/python
"""
Audit bee
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
    def __init__(self):
        ApiaryBot.__init__(self)
        # Initialize stats
        self.stats['audit_count'] = 0
        self.stats['audit_success'] = 0
        self.stats['audit_failure'] = 0

    def update_audit_status(self, pagename):
        self.stats['audit_success'] += 1
        # Audit completed
        if self.args.verbose >= 2:
            print "%s audit completed, updating audit status." % pagename

        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': pagename,
            'Website[Audited]': 'Yes',
            'Website[Audited date]': time.strftime('%B %d, %Y %I:%M:%S %p', time.gmtime()),
            'wpSummary': 'Audit completed.'})
        if self.args.verbose >= 3:
            print c

    def set_flag(self, pagename, name, value, comment):
        if self.args.verbose >= 2:
            print "%s setting %s to %s (%s)." % (pagename, name, value, comment)

        property = "Website[%s]" % name
        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': pagename,
            property: value,
            'wpSummary': comment})
        if self.args.verbose >= 3:
            print c

    def set_audit_extensions(self, site, extensions):
        for extension in extensions:
            # Semantic statistics requires Semantic MediaWiki 1.6 or later.
            if extension['name'] == 'Semantic MediaWiki':
                match = re.search(r'(\d+)\.(\d+)', extension['version'])
                (smw_version_major, smw_version_minor) = (int(match.group(1)), int(match.group(2)))

                if (smw_version_major >= 1) and (smw_version_minor >= 6) and (site[1]['printouts']['Collect semantic statistics'][0] == "f"):
                    self.set_flag(site[0], 'Collect semantic statistics', 'Yes', "Enabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))
                if (smw_version_major >= 1) and (smw_version_minor < 6) and (site[1]['printouts']['Collect semantic statistics'][0] == "t"):
                    self.set_flag(site[0], 'Collect semantic statistics', 'Yes', "Disabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))

    def set_audit(self, site, data):
        # Get the major and minor version numbers of MediaWiki
        match = re.search(r'\s(\d+)\.(\d+)', data['generator'])
        (mw_version_major, mw_version_minor) = (int(match.group(1)), int(match.group(2)))

        if self.args.verbose >= 2:
            print "Website: %s  Generator: %s  Major: %d  Minor: %d" % (site[0], data['generator'], mw_version_major, mw_version_minor)

        # General data requires MediaWiki 1.8 or later.
        if (mw_version_major >= 1) and (mw_version_minor >= 8) and (site[1]['printouts']['Collect general data'][0] == "f"):
            self.set_flag(site[0], 'Collect general data', 'Yes', "MediaWiki %d.%d supports general collection" % (mw_version_major, mw_version_minor))

        # Extension data requires MediaWiki 1.14 or later.
        if (mw_version_major >= 1) and (mw_version_minor >= 14) and (site[1]['printouts']['Collect extension data'][0] == "f"):
            self.set_flag(site[0], 'Collect extension data', 'Yes', "Enabling extension collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor < 14) and (site[1]['printouts']['Collect extension data'][0] == "t"):
            self.set_flag(site[0], 'Collect extension data', 'No', "Disabling extensions collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

        # Skin data requires MediaWiki 1.18 or later.
        if (mw_version_major >= 1) and (mw_version_minor >= 18) and (site[1]['printouts']['Collect skin data'][0] == "f"):
            self.set_flag(site[0], 'Collect skin data', 'Yes', "Enabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor < 18) and (site[1]['printouts']['Collect skin data'][0] == "t"):
            self.set_flag(site[0], 'Collect skin data', 'No', "Disabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

        # General statistics requires MediaWiki 1.11 or later.
        if (mw_version_major >= 1) and (mw_version_minor >= 11) and (site[1]['printouts']['Collect statistics'][0] == "f"):
            self.set_flag(site[0], 'Collect statistics', 'Yes', "Enabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
        if (mw_version_major >= 1) and (mw_version_minor < 11) and (site[1]['printouts']['Collect statistics'][0] == "t"):
            self.set_flag(site[0], 'Collect statistics', 'No', "Disabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

        # Return if extension data is available to check as well
        if (mw_version_major >= 1) and (mw_version_minor >= 14):
            return True
        else:
            return False

    def audit_site(self, site):
        if self.args.verbose >= 1:
            print "\n\nSite: ", site
        data_url = site[1]['printouts']['Has API URL'][0] + "?action=query&meta=siteinfo&siprop=general&format=json"
        if self.args.verbose >= 2:
            print "Pulling general info info from %s." % data_url
        (success, data, duration) = self.pull_json(site[0], data_url, bot='Audit Bee')

        audit_complete = False
        audit_extensions_complete = False
        do_audit_extensions = False

        if success:
            if 'query' in data:
                do_audit_extensions = self.set_audit(site, data['query']['general'])
                audit_complete = True
            else:
                message = "[[%s]] Returned unexpected JSON while requesting general site info (%s)." % (site[0], data_url)
                self.botlog(bot='Audit Bee', type='warn', message=message)

        # Pull extension information for audit too!
        if do_audit_extensions:
            data_url = site[1]['printouts']['Has API URL'][0] + "?action=query&meta=siteinfo&siprop=extensions&format=json"
            if self.args.verbose >= 2:
                print "Pulling extension info info from %s." % data_url
            (success, data, duration) = self.pull_json(site[0], data_url, bot='Audit Bee')

            if success:
                if 'query' in data:
                    self.set_audit_extensions(site, data['query']['extensions'])
                    audit_extensions_complete = True
                else:
                    message = "[[%s]] Returned unexpected JSON while requesting extensions (%s)." % (site[0], data_url)
                    self.botlog(bot='Audit Bee', type='warn', message=message)

        if (audit_complete) and (do_audit_extensions == audit_extensions_complete):
            # Activate and validate the site, but only if the site has not been audited before
            # if this is a re-audit, leave these flags alone.
            if site[1]['printouts']['Is audited'][0] == "f":
                if site[1]['printouts']['Is validated'][0] == "f":
                    if self.args.verbose >= 2:
                        print "Validating %s." % site[0]
                    self.set_flag(site[0], 'Validated', 'Yes', "Validated.")
                if site[1]['printouts']['Is active'][0] == "f":
                    if self.args.verbose >= 2:
                        print "Activating %s." % site[0]
                    self.set_flag(site[0], 'Active', 'Yes', "Activated.")

            # Update audit status
            self.update_audit_status(site[0])
        else:
            self.stats['audit_failure'] += 1

    def get_audit_list(self, group, count=20):
        my_query = ''.join([
            "[[Concept:%s]]" % group,
            '|?Has API URL',
            '|?Collect general data',
            '|?Collect extension data',
            '|?Collect skin data',
            '|?Collect statistics',
            '|?Collect semantic statistics',
            '|?Is audited',
            '|?Is validated',
            '|?Is active',
            '|?In error',
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
        self.botlog(bot='Audit Bee', message='Starting audit run.')
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Audit Bee')

        # Do never audited first
        (site_count, sites) = self.get_audit_list(group='Websites never audited', count=20)
        if site_count > 0:
            for site in sites:
                self.stats['audit_count'] += 1
                self.audit_site(site)

        # Do re-audits
        (site_count, sites) = self.get_audit_list(group='Websites exired audit', count=20)
        if site_count > 0:
            for site in sites:
                self.stats['audit_count'] += 1
                self.audit_site(site)

        duration = time.time() - start_time
        message = "Completed audit %d sites  %d succeeded  %d failed" % (self.stats['audit_count'], self.stats['audit_success'], self.stats['audit_failure'])
        self.botlog(bot='Audit Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = AuditBee()
    bee.main()
