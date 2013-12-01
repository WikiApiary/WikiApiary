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


class RelatedExtensions(ApiaryBot):
    def __init__(self):
        ApiaryBot.__init__(self)

    def set_related(self, pagename, name, value, comment):
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

    def get_extensions(self, site):
        my_query = ''.join([
            "[[Has extension::+]]",
            "[[Has website::%s]]" % site,
            "|?Has extension",
            "|limit=500"])

        extensions = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(extensions['query']['results']) > 0:
            return len(extensions['query']['results']), extensions['query']['results'].items()
        else:
            return 0, None

    def build_list(self, start, limit):
        my_query = ''.join([
            "[[Category:Website]]",
            "[[Is audited::True]]",
            "[[Is active::True]]",
            "|sort=Creation date",
            "|order=asc",
            "|offset=%d" % start,
            "|limit=%d" % limit])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(sites['query']['results']) > 0:
            return len(sites['query']['results']), sites['query']['results'].items()
        else:
            return 0, None

    def main(self):
        # Setup our connection to the wiki too
        self.connectwiki('Bumble Bee')

        start = 0
        limit = 500
        site_total = 0
        site_total_ext = 0

        f = open('extrec-list.basket', 'w')

        while True:
            print "Requesting %d sites starting at %d." % (limit, start)
            (site_count, sites) = self.build_list(start, limit)
            if site_count > 0:
                print "Received %d sites." % site_count
                for site in sites:
                    site_total += 1
                    (ext_count, extensions) = self.get_extensions(site[0])
                    if ext_count > 0:
                        site_total_ext += 1
                        print "%d (%d): [%s] Found %d extensions." % (site_total_ext, site_total, site[0], ext_count)
                        comma = False
                        for ext in extensions:
                            ext_name = "%s" % ext[1]['printouts']['Has extension'][0]['fulltext']
                            ext_name = string.replace(ext_name, 'Extension:', '')
                            if comma:
                                ext_name = ', ' + ext_name
                            f.write (ext_name.encode('utf8'))
                            comma = True
                        f.write ("\n")
                    else:
                        print "[%s] No extensions." % (site[0])
                start += limit
            else:
                break

        f.close()


# Run
if __name__ == '__main__':
    bot = RelatedExtensions()
    bot.main()
