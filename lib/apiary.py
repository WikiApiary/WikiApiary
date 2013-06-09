"""
Base class for all WikiApiary bots. To make another bot, create a new class derived
from this class.

Jamie Thingelstad <jamie@thingelstad.com>
http://wikiapiary.com/wiki/User:Thingles
http://thingelstad.com/
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
import random
import re
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki


class ApiaryBot:

    args = []
    config = []
    apiary_wiki = []
    apiary_db = []
    stats = {}
    edit_token = ''

    def __init__(self):
        # Get command line options
        self.get_args()
        # Get configuration settings
        self.get_config(self.args.config)
        # Connect to the database
        self.connectdb()
        # Initialize stats
        self.stats['statistics'] = 0
        self.stats['smwinfo'] = 0
        self.stats['smwusage'] = 0
        self.stats['general'] = 0
        self.stats['extensions'] = 0
        self.stats['skins'] = 0
        self.stats['skippedstatistics'] = 0
        self.stats['skippedgeneral'] = 0

    def get_config(self, config_file='../apiary.cfg'):
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read(config_file)
        except IOError:
            print "Cannot open %s." % config_file

    def get_args(self):
        parser = argparse.ArgumentParser(prog="Bumble Bee", description="retrieves usage and statistic information for WikiApiary")
        parser.add_argument("-s", "--segment", help="only work on websites in defined segment")
        parser.add_argument("--site", help="only work on this specific site id")
        parser.add_argument("-d", "--debug", action="store_true", help="do not write any changes to wiki or database")
        parser.add_argument("--config", default="../apiary.cfg", help="use an alternative config file")
        parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
        parser.add_argument("--version", action="version", version="%(prog)s 0.1")

        # All set, now get the arguments
        self.args = parser.parse_args()

    def filter_illegal_chars(self, pre_filter):
        # Utility function to make sure that strings are okay for page titles
        return re.sub(r'[#<>\[\]\|{}]', '', pre_filter).replace('=', '-')

    def sqlutcnow(self):
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        now = now.replace(microsecond=0)
        return now.strftime('%Y-%m-%d %H:%M:%S')

    def pull_json(self, sitename, data_url, bot='Bumble Bee'):
        socket.setdefaulttimeout(15)

        # Get JSON data via API and return the JSON structure parsed
        req = urllib2.Request(data_url)
        req.add_header('User-Agent', self.config.get('Bumble Bee', 'User-Agent'))
        opener = urllib2.build_opener()

        try:
            t1 = datetime.datetime.now()
            f = opener.open(req)
            duration = (datetime.datetime.now() - t1).total_seconds()
        except Exception, e:
            self.record_error(sitename, "%s from %s" % (str(e), data_url))
            self.botlog(bot=bot, type="error", message="[[%s]] %s calling %s" % (sitename, str(e), data_url))
            return False, None, None
        else:
            # It all worked!
            try:
                # Clean the returned string before we parse it, sometimes there are junky error messages
                # from PHP in here, or simply a newline that shouldn't be present
                # The regex here is really simple, but it seems to work fine.
                ret_string = f.read()
                json_match = re.search(r"({.*})", ret_string, flags=re.MULTILINE)
                if json_match.group(1) != None:
                    # Found JSON block
                    data = simplejson.loads(json_match.group(1))
                else:
                    # No JSON content in the response
                    self.record_error(sitename, "No JSON from %s." % data_url)
                    self.botlog(bot=bot, type="error", message="[[%s]] No JSON from %s." % (sitename, data_url))
                    return False, None, None
            except Exception, e:
                self.record_error(sitename, "%s from %s" % (str(e), data_url))
                self.botlog(bot=bot, type="error", message="[[%s]] %s from %s" % (sitename, str(e), data_url))
                return False, None, None
            return True, data, duration

    def record_error(self, sitename, error_message):
        # TODO: This function is disabled. It generated too many edits.
        # this will be moved into ApiaryDB shortly
        return True

        # This function updates the error properties for a wiki
        socket.setdefaulttimeout(30)

        if self.args.verbose >= 2:
            print "Updating error information for %s" % sitename

        my_query = ''.join([
            "[[%s]]" % sitename,
            '|?In error',
            '|?Has error count',
            '|?Has cumulative error count',
            '|?Has error date',
            '|?Has error message'])
        if self.args.verbose >= 3:
            print "Get current error info: %s" % my_query

        curr_status = self.apiary_wiki.call({'action': 'ask', 'query': my_query})
        if self.args.verbose >= 3:
            print curr_status

        try:
            in_error = (curr_status['query']['results'][sitename]['printouts']['In error'][0] == 't')
        except:
            in_error = False

        try:
            cumulative_error_count = curr_status['query']['results'][sitename]['printouts']['Has cumulative error count'][0] + 1
        except:
            cumulative_error_count = 1

        if not in_error:    # This is a new error, reset things

            c = self.apiary_wiki.call({
                'action': 'sfautoedit',
                'form': 'Website',
                'target': sitename,
                'Website[Error]': 'Yes',
                'Website[Error date]': time.strftime('%B %d, %Y %I:%M:%S %p', time.gmtime()),
                'Website[Error count]': '1',
                'Website[Cumulative error count]': cumulative_error_count,
                'Website[Error message]': error_message,
                'wpSummary': "recording initial error (%d cumulative)" % cumulative_error_count})

        else:       # This is the continuation of an existing error, update count and message but not date
            try:
                error_count = curr_status['query']['results'][sitename]['printouts']['Has error count'][0] + 1
                if error_count > cumulative_error_count:
                    cumulative_error_count = error_count
            except:
                error_count = 1

            c = self.apiary_wiki.call({
                'action': 'sfautoedit',
                'form': 'Website',
                'target': sitename,
                'Website[Error]': 'Yes',
                'Website[Error count]': error_count,
                'Website[Cumulative error count]': cumulative_error_count,
                'Website[Error message]': error_message,
                'wpSummary': "incrementing error count to %d (%d cumulative)" % (error_count, cumulative_error_count)})

        if self.args.verbose >= 3:
            print c

    def clear_error(self, sitename):
        # This function clears the error status of a meeting
        socket.setdefaulttimeout(30)

        if self.args.verbose >= 2:
            print "Clearing error for %s" % sitename

        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': sitename,
            'Website[Error]': 'No',
            'wpSummary': 'clearing error'})
        if self.args.verbose >= 3:
            print c

    def connectdb(self):
        # Setup our database connection
        # Use the account that can also insert and delete from the database
        self.apiary_db = mdb.connect(
            host=self.config.get('ApiaryDB', 'hostname'),
            db=self.config.get('ApiaryDB', 'database'),
            user=self.config.get('ApiaryDB RW', 'username'),
            passwd=self.config.get('ApiaryDB RW', 'password'),
            charset='utf8')

    def connectwiki(self, bot_name):
        self.apiary_wiki = MediaWiki(self.config.get('WikiApiary', 'API'))
        self.apiary_wiki.login(self.config.get(bot_name, 'Username'), self.config.get(bot_name, 'Password'))
        # We need an edit token
        c = self.apiary_wiki.call({'action': 'query', 'titles': 'Foo', 'prop': 'info', 'intoken': 'edit'})
        self.edit_token = c['query']['pages']['-1']['edittoken']

    def get_websites(self, segment, site):
        filter_string = ""
        if site is not None:
            if self.args.verbose >= 1:
                print "Processing site %d." % int(site)
            filter_string = "[[Has ID::%d]]" % int(site)
        elif segment is not None:
            if self.args.verbose >= 1:
                print "Only retrieving segment %d." % int(self.args.segment)
            filter_string = "[[Has bot segment::%d]]" % int(self.args.segment)

        # Build query for sites
        my_query = ''.join([
            '[[Category:Website]]',
            '[[Is defunct::False]]',
            '[[Is active::True]]',
            filter_string,
            '|?Has API URL',
            '|?Has statistics URL',
            '|?Check every',
            '|?Creation date',
            '|?Has ID',
            '|?In error',
            '|?Collect general data',
            '|?Collect extension data',
            '|?Collect skin data',
            '|?Collect statistics',
            '|?Collect semantic statistics',
            '|?Collect semantic usage',
            '|?Collect logs',
            '|?Collect recent changes',
            '|?Collect statistics stats',
            '|sort=Creation date',
            '|order=rand',
            '|limit=1000'])
        if self.args.verbose >= 3:
            print "Query: %s" % my_query
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        # We could just return the raw JSON object from the API, however instead we are going to clean it up into an
        # easier to deal with array of dictionary objects.
        # To keep things sensible, we'll use the same name as the properties
        if len(sites['query']['results']) > 0:
            my_sites = []
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
                    has_statistics_url = ''

                my_sites.append({
                    'pagename': pagename,
                    'fullurl': site['fullurl'],
                    'Has API URL': site['printouts']['Has API URL'][0],
                    'Has statistics URL': has_statistics_url,
                    'Check every': int(site['printouts']['Check every'][0]),
                    'Creation date': site['printouts']['Creation date'][0],
                    'Has ID': int(site['printouts']['Has ID'][0]),
                    'In error': (site['printouts']['In error'][0] == "t"),  # Boolean fields we'll convert from the strings we get back to real booleans
                    'Collect general data': collect_general_data,
                    'Collect extension data': collect_extension_data,
                    'Collect skin data': collect_skin_data,
                    'Collect statistics': collect_statistics,
                    'Collect semantic statistics': collect_semantic_statistics,
                    'Collect semantic usage': collect_semantic_usage,
                    'Collect statistics stats': collect_statistics_stats,
                    'Collect logs': collect_logs,
                    'Collect recent changes': collect_recent_changes
                })
            return my_sites
        else:
            raise Exception("No sites were returned to work on.")

    def get_status(self, site):
        """
        get_status will query the website_status table in ApiaryDB. It makes the decision if new
        data should be retrieved for a given website. Two booleans are returned, the first to
        tell if new statistics information should be requested and the second to pull general information.
        """
        # Get the timestamps for the last statistics and general pulls
        cur = self.apiary_db.cursor()
        temp_sql = "SELECT last_statistics, last_general, check_every_limit FROM website_status WHERE website_id = %d" % site['Has ID']
        cur.execute(temp_sql)
        rows_returned = cur.rowcount

        if rows_returned == 1:
            # Let's see if it's time to pull information again
            data = cur.fetchone()
            cur.close()

            (last_statistics, last_general, check_every_limit) = data[0:3]
            if self.args.verbose >= 3:
                print "last_stats: %s" % last_statistics
                print "last_general: %s" % last_general
                print "check_every_limit: %s" % check_every_limit

            #TODO: make this check the times!
            last_statistics_struct = time.strptime(str(last_statistics), '%Y-%m-%d %H:%M:%S')
            last_general_struct = time.strptime(str(last_general), '%Y-%m-%d %H:%M:%S')

            stats_delta = (time.mktime(time.gmtime()) - time.mktime(last_statistics_struct)) / 60
            general_delta = (time.mktime(time.gmtime()) - time.mktime(last_general_struct)) / 60

            if self.args.verbose >= 2:
                print "Delta from checks: stats %s general %s" % (stats_delta, general_delta)

            (check_stats, check_general) = (False, False)
            if stats_delta > (site['Check every'] + random.randint(0,15))  and stats_delta > check_every_limit:    # Add randomness to keep checks spread around
                check_stats = True
            else:
                if self.args.verbose >= 2:
                    print "Skipping stats..."
                self.stats['skippedstatistics'] += 1

            if general_delta > ((24 + random.randint(0,24)) * 60):   # General checks are always bound to 24 hours, plus a random offset to keep checks evenly distributed
                check_general = True
            else:
                if self.args.verbose >= 2:
                    print "Skipping general..."
                self.stats['skippedgeneral'] += 1

            return (check_stats, check_general)

        elif rows_returned == 0:
            cur.close()
            # This website doesn't have a status, so we should check everything
            if self.args.verbose >= 3:
                print "website has never been checked before"
            return (True, True)

        else:
            raise Exception("Status check returned multiple rows.")

    def update_status(self, site, checktype):
        cur = self.apiary_db.cursor()

        # Update the website_status table
        my_now = self.sqlutcnow()

        if checktype == "statistics":
            temp_sql = "UPDATE website_status SET last_statistics = '%s' WHERE website_id = %d" % (my_now, site['Has ID'])

        if checktype == "general":
            temp_sql = "UPDATE website_status SET last_general = '%s' WHERE website_id = %d" % (my_now, site['Has ID'])

        if self.args.verbose >= 3:
            print "SQL: %s" % temp_sql

        cur.execute(temp_sql)
        rows_affected = cur.rowcount
        if rows_affected == 0:
            # No rows were updated, this website likely didn't exist before, so we need to insert the first time
            if self.args.verbose >= 2:
                print "No website_status record exists for ID %d, creating one" % site['Has ID']
            temp_sql = "INSERT website_status (website_id, last_statistics, last_general, check_every_limit) "
            temp_sql += "VALUES (%d, \"%s\", \"%s\", %d)" % (site['Has ID'], my_now, my_now, 240)
            if self.args.verbose >= 3:
                print "SQL: %s" % temp_sql
            cur.execute(temp_sql)

        cur.close()
        self.apiary_db.commit()

    def botlog(self, bot, message, type='info', duration=0):
        if self.args.verbose >= 1:
            print message
        cur = self.apiary_db.cursor()

        temp_sql = "INSERT  apiary_bot_log (log_date, log_type, bot, duration, message) "
        temp_sql += "VALUES (\"%s\", \"%s\", \"%s\", %f, \"%s\")" % (self.sqlutcnow(), type, bot, duration, message)

        if self.args.verbose >= 3:
            print "SQL: %s" % temp_sql
        cur.execute(temp_sql)
        cur.close()
        self.apiary_db.commit()
