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


    def pull_json(self, site, data_url, bot='Bumble Bee'):
        socket.setdefaulttimeout(10)

        # Get JSON data via API and return the JSON structure parsed
        req = urllib2.Request(data_url)
        req.add_header('User-Agent', self.config.get('Bumble Bee', 'User-Agent'))
        opener = urllib2.build_opener()

        try:
            t1 = datetime.datetime.now()
            f = opener.open(req)
            duration = (datetime.datetime.now() - t1).total_seconds()
        except Exception, e:
            self.record_error(
                site=site,
                log_message="%s" % str(e),
                log_type='info',
                log_severity='normal',
                log_bot='Bumble Bee',
                log_url=data_url
            )
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
                    self.record_error(
                        site=site,
                        log_message="No JSON found",
                        log_type='info',
                        log_severity='normal',
                        log_bot='Bumble Bee',
                        log_url=data_url
                    )
                    return False, None, None
            except Exception, e:
                self.record_error(
                    site=site,
                    log_message="%s" % str(e),
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                return False, None, None
            return True, data, duration


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
            if stats_delta > (site['Check every'] + random.randint(0, 15))  and stats_delta > check_every_limit:    # Add randomness to keep checks spread around
                check_stats = True
            else:
                if self.args.verbose >= 2:
                    print "Skipping stats..."
                self.stats['skippedstatistics'] += 1

            if general_delta > ((24 + random.randint(0, 24)) * 60):   # General checks are always bound to 24 hours, plus a random offset to keep checks evenly distributed
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
        # Update the website_status table
        my_now = self.sqlutcnow()

        if checktype == "statistics":
            temp_sql = "UPDATE website_status SET last_statistics = '%s' WHERE website_id = %d" % (my_now, site['Has ID'])

        if checktype == "general":
            temp_sql = "UPDATE website_status SET last_general = '%s' WHERE website_id = %d" % (my_now, site['Has ID'])

        (success, rows_affected) = self.runSql(temp_sql)

        if rows_affected == 0:
            # No rows were updated, this website likely didn't exist before, so we need to insert the first time
            if self.args.verbose >= 2:
                print "No website_status record exists for ID %d, creating one" % site['Has ID']
            temp_sql = "INSERT website_status (website_id, last_statistics, last_general, check_every_limit) "
            temp_sql += "VALUES (%d, \"%s\", \"%s\", %d)" % (site['Has ID'], my_now, my_now, 240)
            self.runSql(temp_sql)
