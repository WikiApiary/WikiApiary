#! /usr/bin/env python

"""
Bumble Bee is responsible for collecting statistics and other information from
sites registered on WikiApiary. See http://wikiapiary.com/wiki/User:Bumble_Bee
for more information.

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
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
sys.path.append('../lib')
from apiary import ApiaryBot


class BumbleBee(ApiaryBot):
    """Bot that collects statistics for sits."""

    def record_statistics(self, db, site):

        # Go out and get the statistic information
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=statistics&format=json"
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        if status:
            # Record the new data into the DB
            if self.args.verbose >= 2:
                print data
                print "Duration: %s" % duration

            # Record the data received to the database

            # Update the status table that we did our work!
            self.update_status(site)
        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)

    def record_smwinfo(self, db, site):
        if self.args.verbose >= 3:
            print "In get_smwinfo"
            print site

    def record_general(self, wiki, site):
        if self.args.verbose >= 3:
            print "In get_general"
            print site

    def record_extensions(self, wiki, site):
        if self.args.verbose >= 3:
            print "In get_extensions"
            print site

    def main(self):
        # Setup database connection
        self.connectdb()

        if self.args.segment is not None:
            message = "Starting processing for segment %d." % int(self.args.segment)
        else:
            message = "Starting processing for all websites."
        self.botlog(bot='Bumble Bee', message=message)

        # Record time at beginning
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Bumble Bee')

        # Get list of websites to work on
        sites = self.get_websites(self.wiki, self.args.segment)

        i = 0
        for site in sites:
            i += 1
            req_statistics = False
            req_general = False
            (req_statistics, req_general) = self.get_status(site)
            if req_statistics:
                self.record_statistics(self.apiarydb, site)
                self.record_smwinfo(self.apiarydb, site)
            if req_general:
                self.record_general(self.wiki, site)
                self.record_extensions(self.wiki, site)

        duration = time.time() - start_time
        if self.args.segment is not None:
            message = "Completed processing for segment %d." % int(self.args.segment)
        else:
            message = "Completed processing for all websites."
        message += " Processed %d websites." % i
        self.botlog(bot='Bumble Bee', duration=float(duration), message=message)

# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
