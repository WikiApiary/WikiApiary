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
import dateutil.parser
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
sys.path.append('../lib')
from apiary import bot


class AuditBee(ApiaryBot):
    def __init__(self):
        ApiaryBot.__init__(self)
        # Initialize stats
        self.stats['audit_count'] = 0
        self.stats['audit_success'] = 0
        self.stats['audit_failure'] = 0

    def update_audit_status(self, pagename):
        if self.args.verbose >= 2:
            print "%s audit completed, updating audit date." % pagename

        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': pagename,
            'Website[Audited]': 'Yes',
            'Website[Audited date]': time.strftime('%Y/%m/%d %I:%M:%S %p', time.gmtime()),
            'wpSummary': 'audited'})
        if self.args.verbose >= 3:
            print c

    def set_flag(self, pagename, name, value, comment):
        if self.args.verbose >= 2:
            print "%s setting %s to %s (%s)." % (pagename, name, value, comment)

        property_name = "Website[%s]" % name
        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': pagename,
            property_name: value,
            'wpSummary': comment})
        if self.args.verbose >= 3:
            print c

    def set_audit_extensions(self, site, extensions):
        for extension in extensions:
            # Semantic statistics requires Semantic MediaWiki 1.6 or later.
            if extension.get('name', "") == 'Semantic MediaWiki':
                match = re.search(r'(\d+)\.(\d+)', extension['version'])
                (smw_version_major, smw_version_minor) = (int(match.group(1)), int(match.group(2)))

                if (smw_version_major >= 1) and (smw_version_minor >= 6) and (site['Collect semantic statistics'] is False):
                    self.set_flag(site['pagename'], 'Collect semantic statistics', 'Yes', "Enabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))
                if (smw_version_major >= 1) and (smw_version_minor < 6) and (site['Collect semantic statistics'] is True):
                    self.set_flag(site['pagename'], 'Collect semantic statistics', 'Yes', "Disabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))

    def set_audit(self, site, data):
        # Get the major and minor version numbers of MediaWiki
        match = re.search(r'\s(\d+)\.(\d+)', data['generator'])
        if match != None:
            (mw_version_major, mw_version_minor) = (int(match.group(1)), int(match.group(2)))

            if self.args.verbose >= 2:
                print "Website: %s  Generator: %s  Major: %d  Minor: %d" % (site['pagename'], data['generator'], mw_version_major, mw_version_minor)

            # General data requires MediaWiki 1.8 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 8) and (site['Collect general data'] is False):
                self.set_flag(site['pagename'], 'Collect general data', 'Yes', "MediaWiki %d.%d supports general collection" % (mw_version_major, mw_version_minor))

            # Extension data requires MediaWiki 1.14 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 14) and (site['Collect extension data'] is False):
                self.set_flag(site['pagename'], 'Collect extension data', 'Yes', "Enabling extension collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 14) and (site['Collect extension data'] is True):
                self.set_flag(site['pagename'], 'Collect extension data', 'No', "Disabling extensions collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # Skin data requires MediaWiki 1.18 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 18) and (site['Collect skin data'] is False):
                self.set_flag(site['pagename'], 'Collect skin data', 'Yes', "Enabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 18) and (site['Collect skin data'] is True):
                self.set_flag(site['pagename'], 'Collect skin data', 'No', "Disabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # General statistics requires MediaWiki 1.11 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 11) and (site['Collect statistics'] is False):
                self.set_flag(site['pagename'], 'Collect statistics', 'Yes', "Enabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 11) and (site['Collect statistics'] is True):
                self.set_flag(site['pagename'], 'Collect statistics', 'No', "Disabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # Return if extension data is available to check as well
            if (mw_version_major >= 1) and (mw_version_minor >= 14):
                return True
            else:
                return False

        else:
            # Unable to determine the version of MediaWiki. This is probably because the
            # wiki has been altered to hide its version.
            if self.args.verbose >= 2:
                print "%s returnd version %s which cannot be parsed." % (site['pagename'], data['generator'])
            self.record_error(
                site=site,
                log_message="Unable to determine version from %s. Auditing without confirming any flags. Operator please check." % data['generator'],
                log_type='info',
                log_severity='normal',
                log_bot='Audit Bee'
            )
            return False

    def audit_site(self, site):
        if self.args.verbose >= 1:
            print "\n\nSite: ", site
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=general&format=json"
        if self.args.verbose >= 2:
            print "Pulling general info info from %s." % data_url
        (success, data, duration) = self.pull_json(site, data_url, bot='Audit Bee')

        audit_complete = False
        audit_extensions_complete = False
        do_audit_extensions = False

        if success:
            if 'query' in data:
                do_audit_extensions = self.set_audit(site, data['query']['general'])
                audit_complete = True
            elif 'error' in data:
                if 'code' in data['error']:
                    if data['error']['code'] == 'readapidenied':
                        # This website will not let us talk to it, defunct it.
                        self.set_flag(site['pagename'], 'Defunct', 'Yes', 'Marking defunct because readapidenied')
                        self.record_error(
                            site=site,
                            log_message="readapidenied, marking defunct",
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=data_url
                        )
                    else:
                        self.record_error(
                            site=site,
                            log_message="Returned error %s" % data['error']['code'],
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=data_url
                        )
                else:
                    self.record_error(
                        site=site,
                        log_message="An unknown error was returned from site info",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=data_url
                    )
            else:
                self.record_error(
                    site=site,
                    log_message="Returned unexpected JSON while requesting general site info",
                    log_type='warn',
                    log_severity='important',
                    log_bot='Audit Bee',
                    log_url=data_url
                )

        # Pull extension information for audit too!
        if do_audit_extensions:
            data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=extensions&format=json"
            if self.args.verbose >= 2:
                print "Pulling extension info info from %s." % data_url
            (success, data, duration) = self.pull_json(site['pagename'], data_url, bot='Audit Bee')

            if success:
                if 'query' in data:
                    self.set_audit_extensions(site, data['query']['extensions'])
                    audit_extensions_complete = True
                else:
                    self.record_error(
                        site=site,
                        log_message="Returned unexpected JSON while requesting extensions",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=data_url
                    )

        if (audit_complete):
            # Let's see if we need to update the Founded date
            my_query = ''.join([
                "[[%s]]" % site['pagename'],
                '|?Founded date'
            ])

            if self.args.verbose >= 3:
                print "Query: %s" % my_query

            socket.setdefaulttimeout(30)
            check_date = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

            if self.args.verbose >= 3:
                print "Response: %s" % check_date

            if len(check_date['query']['results'][site['pagename']]['printouts']['Founded date']) > 0:
                update_founded_date = False
            else:
                update_founded_date = True

            if (update_founded_date):
                # ?action=query&prop=revisions&revids=1&rvprop=timestamp&format=json
                first_date_url = site['Has API URL'] + "?action=query&prop=revisions&revids=1&rvprop=timestamp&format=json"
                (success, first_change, duration) = self.pull_json(site, first_date_url, bot='Audit Bee')
                if success:
                    try:
                        timestamp = first_change['query']['pages']['1']['revisions'][0]['timestamp']
                        # timestamp is ISO 8601 format
                        first_edit = dateutil.parser.parse(timestamp)
                        self.set_flag(site['pagename'], 'Founded date', first_edit.strftime('%Y/%m/%d %I:%M:%S %p'), 'Setting founded date to timestamp of first edit')
                    except:
                        self.record_error(
                            site=site,
                            log_message="Failed to get timestamp of first revision to wiki.",
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=first_date_url
                        )
                else:
                    self.record_error(
                        site=site,
                        log_message="Failed to get timestamp for first edit.",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=first_date_url
                    )
            else:
                if self.args.verbose >= 2:
                    print "Date founded is already set, not checking."

        if (audit_complete) and (do_audit_extensions == audit_extensions_complete):
            # Activate the site, but only if the site has not been audited before
            # if this is a re-audit, leave these flags alone.
            if not site['Is audited']:
                if not site['Is active']:
                    if self.args.verbose >= 2:
                        print "Activating %s." % site['pagename']
                    self.set_flag(site['pagename'], 'Active', 'Yes', "Activated.")

            self.stats['audit_success'] += 1
        else:
            self.stats['audit_failure'] += 1

        # Update audit status, wether success or failure
        self.update_audit_status(site['pagename'])

    def get_audit_list(self, group, count=20):
        my_query = ''.join([
            "[[Concept:%s]]" % group,
            '|?Has ID',
            '|?Has API URL',
            '|?Check every',
            '|?Collect general data',
            '|?Collect extension data',
            '|?Collect skin data',
            '|?Collect statistics',
            '|?Collect semantic statistics',
            '|?Collect statistics stats',
            '|?Collect logs',
            '|?Collect recent changes',
            '|?Creation date',
            '|?Is audited',
            '|?Is active',
            '|sort=Creation date',
            '|order=rand',
            "|limit=%d" % count])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({
            'action': 'ask',
            'query': my_query
        })

        my_sites = []
        if len(sites['query']['results']) > 0:
            for pagename, site in sites['query']['results'].items():
                if self.args.verbose >= 3:
                    print "Adding %s." % pagename

                # Initialize the flags but do it carefully in case there is no value in the wiki yet
                try:
                    collect_general_data = (site['printouts']['Collect general data'][0] == "t")
                except:
                    collect_general_data = False

                try:
                    collect_extension_data = (site['printouts']['Collect extension data'][0] == "t")
                except:
                    collect_extension_data = False

                try:
                    collect_skin_data = (site['printouts']['Collect skin data'][0] == "t")
                except:
                    collect_skin_data = False

                try:
                    collect_statistics = (site['printouts']['Collect statistics'][0] == "t")
                except:
                    collect_statistics = False

                try:
                    collect_semantic_statistics = (site['printouts']['Collect semantic statistics'][0] == "t")
                except:
                    collect_semantic_statistics = False

                try:
                    collect_semantic_usage = (site['printouts']['Collect semantic usage'][0] == "t")
                except:
                    collect_semantic_usage = False

                try:
                    collect_statistics_stats = (site['printouts']['Collect statistics stats'][0] == "t")
                except:
                    collect_statistics_stats = False

                try:
                    collect_logs = (site['printouts']['Collect logs'][0] == "t")
                except:
                    collect_logs = False

                try:
                    collect_recent_changes = (site['printouts']['Collect recent changes'][0] == "t")
                except:
                    collect_recent_changes = False

                try:
                    has_statistics_url = site['printouts']['Has statistics URL'][0]
                except:
                    has_statistics_url = None

                try:
                    has_api_url = site['printouts']['Has API URL'][0]
                except:
                    has_api_url = None

                my_sites.append({
                    'pagename': pagename,
                    'fullurl': site['fullurl'],
                    'Has API URL': has_api_url,
                    'Has statistics URL': has_statistics_url,
                    'Check every': int(site['printouts']['Check every'][0]),
                    'Creation date': site['printouts']['Creation date'][0],
                    'Has ID': int(site['printouts']['Has ID'][0]),
                    'Collect general data': collect_general_data,
                    'Collect extension data': collect_extension_data,
                    'Collect skin data': collect_skin_data,
                    'Collect statistics': collect_statistics,
                    'Collect semantic statistics': collect_semantic_statistics,
                    'Collect semantic usage': collect_semantic_usage,
                    'Collect statistics stats': collect_statistics_stats,
                    'Collect logs': collect_logs,
                    'Collect recent changes': collect_recent_changes,
                    'Is audited': (site['printouts']['Is audited'][0] == "t"),
                    'Is active': (site['printouts']['Is active'][0] == "t")
                })
        return my_sites

    def main(self):
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Audit Bee')

        # Do never audited first
        sites = self.get_audit_list(group='Websites never audited', count=20)
        if len(sites) > 0:
            for site in sites:
                self.stats['audit_count'] += 1
                try:
                    self.audit_site(site)
                except Exception, e:
                    self.record_error(
                        site=site,
                        log_message="Unhandled exception %s." % e,
                        log_type='error',
                        log_severity='important',
                        log_bot='Audit Bee'
                    )

        # Do re-audits
        sites = self.get_audit_list(group='Websites expired audit', count=20)
        if len(sites) > 0:
            for site in sites:
                self.stats['audit_count'] += 1
                try:
                    self.audit_site(site)
                except Exception, e:
                    self.record_error(
                        site=site,
                        log_message="Unhandled exception %s." % e,
                        log_type='error',
                        log_severity='important',
                        log_bot='Audit Bee'
                    )

        duration = time.time() - start_time
        if self.stats['audit_count'] > 0:
            message = "Completed audit %d sites  %d succeeded  %d failed" % (self.stats['audit_count'], self.stats['audit_success'], self.stats['audit_failure'])
            self.botlog(bot='Audit Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = AuditBee()
    bee.main()
