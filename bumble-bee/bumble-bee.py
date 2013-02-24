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
import re
import HTMLParser
sys.path.append('../lib')
from apiary import ApiaryBot


class BumbleBee(ApiaryBot):
    """Bot that collects statistics for sits."""

    def record_statistics(self, site):
        # Go out and get the statistic information
        data_url = site['Has API URL'] + '?action=query&meta=siteinfo&siprop=statistics&format=json'
        if self.args.verbose >= 2:
            print "Pulling statistics info from %s." % data_url
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        if status:
            # Record the new data into the DB
            if self.args.verbose >= 2:
                print "JSON: %s" % data
                print "Duration: %s" % duration

            if 'query' in data:
                # Record the data received to the database
                sql_command = """
                    INSERT INTO statistics
                        (website_id, capture_date, response_timer, articles, jobs, users, admins, edits, activeusers, images, pages, views)
                    VALUES
                        (%s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                data = data['query']['statistics']
                if 'articles' in data:
                        articles = "%s" % data['articles']
                else:
                        articles = 'null'
                if 'jobs' in data:
                        jobs = "%s" % data['jobs']
                else:
                        jobs = 'null'
                if 'users' in data:
                        users = "%s" % data['users']
                else:
                        users = 'null'
                if 'admins' in data:
                        admins = "%s" % data['admins']
                else:
                        admins = 'null'
                if 'edits' in data:
                        edits = "%s" % data['edits']
                else:
                        edits = 'null'
                if 'activeusers' in data:
                        activeusers = "%s" % data['activeusers']
                else:
                        activeusers = 'null'
                if 'images' in data:
                        images = "%s" % data['images']
                else:
                        images = 'null'
                if 'pages' in data:
                        pages = "%s" % data['pages']
                else:
                        pages = 'null'
                if 'views' in data:
                        views = "%s" % data['views']
                else:
                        views = 'null'

                sql_command = sql_command % (
                    site['Has ID'],
                    self.sqlutcnow(),
                    duration,
                    articles,
                    jobs,
                    users,
                    admins,
                    edits,
                    activeusers,
                    images,
                    pages,
                    views)

                if self.args.verbose >= 3:
                    print "SQL: %s" % sql_command

                cur = self.apiary_db.cursor()
                cur.execute(sql_command)
                cur.close()
                self.apiary_db.commit()

                self.stats['statistics'] += 1
            else:
                message = "[[%s]] Statistics returned unexpected JSON." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)

        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)

        # Update the status table that we did our work!
        self.update_status(site, 'statistics')

    def record_smwinfo(self, site):
        # Go out and get the statistic information
        data_url = site['Has API URL'] + '?action=smwinfo&info=propcount%7Cusedpropcount%7Cdeclaredpropcount%7Cproppagecount&format=json'
        if self.args.verbose >= 2:
            print "Pulling SMW info from %s." % data_url
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        if status:
            # Record the new data into the DB
            if self.args.verbose >= 2:
                print "JSON: %s" % data
                print "Duration: %s" % duration

            if 'info' in data:
                # Record the data received to the database
                sql_command = """
                    INSERT INTO smwinfo
                        (website_id, capture_date, response_timer, propcount, proppagecount, usedpropcount, declaredpropcount)
                    VALUES
                        (%d, '%s', %s, %s, %s, %s, %s)
                    """

                if 'propcount' in data['info']:
                        propcount = data['info']['propcount']
                else:
                        propcount = 'null'
                if 'proppagecount' in data['info']:
                        proppagecount = data['info']['proppagecount']
                else:
                        proppagecount = 'null'
                if 'usedpropcount' in data['info']:
                        usedpropcount = data['info']['usedpropcount']
                else:
                        usedpropcount = 'null'
                if 'declaredpropcount' in data['info']:
                        declaredpropcount = data['info']['declaredpropcount']
                else:
                        declaredpropcount = 'null'

                sql_command = sql_command % (
                    site['Has ID'],
                    self.sqlutcnow(),
                    duration,
                    propcount,
                    proppagecount,
                    usedpropcount,
                    declaredpropcount)

                if self.args.verbose >= 3:
                    print "SQL: %s" % sql_command

                cur = self.apiary_db.cursor()
                cur.execute(sql_command)
                cur.close()
                self.apiary_db.commit()

                self.stats['smwinfo'] += 1
            else:
                message = "[[%s]] SMWInfo returned unexpected JSON." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)

        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)

        # Update the status table that we did our work!
        # TODO: Commenting out. There is a bug that if this updates at the same time as the previous one
        # there is no change to the row, and my check for rows_affected in update_status will
        # not work as intended. Going to assume that smwinfo slaves off of regular statistics.
        #self.update_status(site, 'statistics')

    def build_general_template(self, x, server):
        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        template_block += "{{General siteinfo\n"
        template_block += "|HTTP server=%s\n" % (server)
        template_block += "|MediaWiki version=%s\n" % (x['generator'])
        if 'timezone' in x:
            template_block += "|Timezone=%s\n" % (x['timezone'])
        if 'timeoffset' in x:
            template_block += "|Timeoffset=%s\n" % (x['timeoffset'])
        if 'sitename' in x:
            template_block += "|Sitename=%s\n" % (x['sitename'])
        if 'rights' in x:
            template_block += "|Rights=%s\n" % (x['rights'])
        if 'phpversion' in x:
            template_block += "|PHP Version=%s\n" % (x['phpversion'])
        if 'lang' in x:
            template_block += "|Language=%s\n" % (x['lang'])
        if 'dbtype' in x:
            template_block += "|Database type=%s\n" % (x['dbtype'])
        if 'dbversion' in x:
            template_block += "|Database version=%s\n" % (x['dbversion'])
        if 'wikiid' in x:
            template_block += "|Wiki ID=%s\n" % (x['wikiid'])
        template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block

    def record_general(self, site):
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=general&format=json"
        if self.args.verbose >= 2:
            print "Pulling general info info from %s." % data_url
        (success, data, duration) = self.pull_json(site['pagename'], data_url)
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/General" % site['pagename']
                template_block = self.build_general_template(data['query']['general'], '')
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['general'] += 1
            else:
                message = "[[%s]] Returned unexpected JSON when general info." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)

        # Update the status table that we did our work! It doesn't matter if this was an error.
        self.update_status(site, 'general')

    def build_extensions_template(self, ext_obj):
        h = HTMLParser.HTMLParser()

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        for x in ext_obj:
            template_block += "{{Extension in use\n"
            template_block += "|Extension name=%s\n" % (x['name'])
            if 'version' in x:
                template_block += "|Extension version=%s\n" % (x['version'])
            if 'author' in x:
                # Authors can have a lot of junk in them, wikitext and such.
                # We'll try to clean that up.
                temp_author = x['author']
                # Wikilinks with names
                # "[[Foobar | Foo Bar]]"
                temp_author = re.sub(r'\[\[.*\|(.*)\]\]', r'\1', temp_author)
                # Simple Wikilinks
                temp_author = re.sub(r'\[\[(.*)\]\]', r'\1', temp_author)
                # Hyperlinks as wikiext
                # "[https://www.mediawiki.org/wiki/User:Jeroen_De_Dauw Jeroen De Dauw]"
                temp_author = re.sub(r'\[\S+\s+([^\]]+)\]', r'\1', temp_author)
                # Misc text
                temp_author = re.sub(r'\sand\s', r', ', temp_author)
                temp_author = re.sub(r'\.\.\.', r'', temp_author)
                temp_author = re.sub(r'&nbsp;', r' ', temp_author)
                # Lastly, there could be HTML encoded stuff in these
                temp_author = h.unescape(temp_author)

                template_block += "|Extension author=%s\n" % (temp_author)

            if 'type' in x:
                template_block += "|Extension type=%s\n" % (x['type'])
            if 'url' in x:
                template_block += "|Extension URL=%s\n" % (x['url'])
            template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block

    def record_extensions(self, site):
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=extensions&format=json"
        if self.args.verbose >= 2:
            print "Pulling extensions from %s." % data_url
        (success, data, duration) = self.pull_json(site['pagename'], data_url)
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/Extensions" % site['pagename']
                template_block = self.build_extensions_template(data['query']['extensions'])
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['extensions'] += 1
            else:
                message = "[[%s]] Returned unexpected JSON when requesting extension data." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)

    def build_skins_template(self, ext_obj):
        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        for x in ext_obj:
            template_block += "{{Skin in use\n"
            template_block += "|Skin name=%s\n" % (x['*'])
            template_block += "|Skin code=%s\n" % (x['code'])
            template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block

    def record_skins(self, site):
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=skins&format=json"
        if self.args.verbose >= 2:
            print "Pulling skin info from %s." % data_url
        (success, data, duration) = self.pull_json(site['pagename'], data_url)
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/Skins" % site['pagename']
                template_block = self.build_skins_template(data['query']['skins'])
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['skins'] += 1
            else:
                message = "[[%s]] Returned unexpected JSON when requesting skin data." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)

    def main(self):
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
        sites = self.get_websites(self.args.segment)

        i = 0
        for site in sites:
            i += 1
            if self.args.verbose >= 1:
                print "\n\n%d: Processing %s (ID %d)" % (i, site['pagename'], site['Has ID'])
            req_statistics = False
            req_general = False
            (req_statistics, req_general) = self.get_status(site)
            if req_statistics:
                if site['Collect statistics']:
                    self.record_statistics(site)
                if site['Collect semantic statistics']:
                    self.record_smwinfo(site)
            if req_general:
                if site['Collect general data']:
                    self.record_general(site)
                if site['Collect extension data']:
                    self.record_extensions(site)
                if site['Collect skin data']:
                    self.record_skins(site)

        duration = time.time() - start_time
        if self.args.segment is not None:
            message = "Completed processing for segment %d." % int(self.args.segment)
        else:
            message = "Completed processing for all websites."
        message += " Processed %d websites." % i
        self.botlog(bot='Bumble Bee', duration=float(duration), message=message)
        message = "Stats: statistics %d smwinfo %d general %d extensions %d skins %d skipped_stats: %d skipped_general: %d" % (
            self.stats['statistics'], self.stats['smwinfo'], self.stats['general'],
            self.stats['extensions'], self.stats['skins'], self.stats['skippedstatistics'], self.stats['skippedgeneral'])
        self.botlog(bot='Bumble Bee', message=message)


# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
