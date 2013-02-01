#! /usr/bin/env python

import os
import sys
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
        (data, duration) = self.pull_json(data_url)

        # Record the new data into the DB
        print "Duration: %s" % duration
        print data

        # Update the status table that we did our work!
        self.update_status(db, site)

    def record_smwinfo(self, db, site):
        print "In get_smwinfo"
        print site

    def record_general(self, wiki, site):
        print "In get_general"
        print site

    def record_extensions(self, wiki, site):
        print "In get_extensions"
        print site

    def main(self):
        # Set global socket timeout for all our web requests
        socket.setdefaulttimeout(5)

        # Setup our database connection and get a cursor to work with
        apiarydb = mdb.connect(
            host=self.config.get('ApiaryDB', 'hostname'),
            db=self.config.get('ApiaryDB', 'database'),
            user=self.config.get('ApiaryDB', 'username'),
            passwd=self.config.get('ApiaryDB', 'password'))

        # Setup our connection to the wiki too
        wiki = MediaWiki(self.config.get('WikiApiary', 'API'))
        wiki.login(self.config.get('WikiApiary', 'Username'), self.config.get('WikiApiary', 'Password'))

        sites = self.get_websites(wiki, self.args.segment)

        for site in sites[0:2]:
            req_statistics = False
            req_general = False
            (req_statistics, req_general) = self.get_status(apiarydb, site)
            if req_statistics:
                self.record_statistics(apiarydb, site)
                self.record_smwinfo(apiarydb, site)
            if req_general:
                self.record_general(wiki, site)
                self.record_extensions(wiki, site)


# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
