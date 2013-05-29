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
import simplejson
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
sys.path.append('../lib')
from apiary import ApiaryBot
import Orange


class SetRelated(ApiaryBot):
    ext = {}

    def __init__(self):
        ApiaryBot.__init__(self)

    def set_related(self, extension, related):
        ext_page = "Extension:%s" % extension
        c = self.apiary_wiki.call({
            'action': 'sfautoedit',
            'form': 'Extension',
            'target': ext_page,
            'Extension[Related]': related,
            'wpSummary': 'Updating related extensions.'})
        #print c

    def main(self):
        # Setup our connection to the wiki too
        self.connectwiki('Worker Bee')

        print "Loading data table..."
        data = Orange.data.Table("extrec-list.basket")

        print "Creating rules..."
        rules = Orange.associate.AssociationRulesSparseInducer(
            data,
            support=0.15,
            store_examples=False,
            max_item_sets=10000000)

        print "Mapping rules into dictionary..."
        for r in rules:
            # print "%6.3f %6.3f %s" % (r.support, r.confidence, r)

            # We only care about rules that have a single extension
            # related to another single extension
            if r.n_left == 1 and r.n_right == 1:
                # r can be a string like SimpleAntiSpam -> ParserFunctions
                # this should really be done using r.right and r.left
                # but that returns a whacky object that is confusing
                # so we hack away and avoid the confusion
                r_string = "%s" % r
                (from_ext, mid, to_ext) = r_string.partition(' -> ')

                if from_ext not in self.ext:
                    self.ext[from_ext] = {}
                self.ext[from_ext][to_ext] = r.confidence

        # Let's get rid of the rules object to free memory while the wiki is updated
        rules = None

        print "Updating WikiApiary..."
        for e in self.ext:
            related_val = ""
            for r in self.ext[e]:
                related_val += "%s," % r
            print "%s => %s" % (e, related_val)
            # Update the wiki!
            self.set_related(e, related_val)

# Run
if __name__ == '__main__':
    bot = SetRelated()
    bot.main()
