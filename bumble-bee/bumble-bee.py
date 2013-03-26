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
import yaml
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki
import re
import HTMLParser
sys.path.append('../lib')
from apiary import ApiaryBot


class BumbleBee(ApiaryBot):
    """Bot that collects statistics for sits."""

    def parse_version(self, t):
        ver = {}

        if self.args.verbose >= 3:
            print "Getting version details for %s" % t

        try:
            # Do we have a x.y.z
            y = re.findall(r'^(?:(\d+)\.)?(?:(\d+)\.?)?(?:(\d+)\.?)?(?:(\d+)\.?)?', t)
            if y:
                if len(y[0][0]) > 0:
                    ver['major'] = y[0][0]
                if len(y[0][1]) > 0:
                    ver['minor'] = y[0][1]
                if len(y[0][2]) > 0:
                    ver['bugfix'] = y[0][2]

            if not ver.get('major', None):
                # Do we have a YYYY-MM-DD
                if re.match(r'\d{4}-\d{2}-\d{2}', t):
                    y = re.findall(r'(\d+)', t)
                    (ver['major'], ver['minor'], ver['bugfix']) = y

            if not ver.get('major', None):
                # Do we have a YYYYMMDD
                if re.match(r'\d{4}\d{2}\d{2}', t):
                    y = re.findall(r'(\d{4})(\d{2})(\d{2})', t)
                    (ver['major'], ver['minor'], ver['bugfix']) = y[0]

            # Do we have a flag
            y = re.match(r'.*(alpha|beta|wmf|CLDR|MLEB).*', t)
            if y:
                ver['flag'] = y.group(1)
        except Exception, e:
            self.botlog(bot='Bumble Bee', type="warn", message="Exception %s while parsing version string %s" % (e, t))

        if self.args.verbose >= 2:
            print "Version details: ", ver

        return ver

    def record_statistics(self, site):
        # Go out and get the statistic information
        data_url = site['Has API URL'] + '?action=query&meta=siteinfo&siprop=statistics&format=json'
        if self.args.verbose >= 2:
            print "Pulling statistics info from %s." % data_url
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        ret_value = True
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
                self.record_error(site['pagename'], 'Statistics returned unexpected JSON.')
                message = "[[%s]] Statistics returned unexpected JSON." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)
                ret_value = False

        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)
            ret_value = False

        # Update the status table that we did our work!
        self.update_status(site, 'statistics')
        return ret_value

    def record_smwusage(self, site):
        # Get the extended SMW usage
        data_url = site['Has API URL'] + '?action=parse&page=Project:SMWExtInfo&prop=text&disablepp=1&format=json'
        if self.args.verbose >= 2:
            print "Pulling semantic usage info from %s." % data_url
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        if status:
            try:
                data_block = data['parse']['text']['*']
                data_block = data_block.replace('; ', '\n')
                data_block = data_block.replace('....', '    ')
                data_block = data_block.replace('<p>', '')
                data_block = data_block.replace('</p>', '')
                data_block = re.sub(r'__\s+NOCACHE\s+__', '', data_block)
                data_block = re.sub(r'<!--.*?-->', '', data_block)

                # Use safe method to limit potential for YAML to do bad things
                y_data = yaml.safe_load(data_block)
            except Exception, e:
                self.record_error(site['pagename'], "Semantic usage failed parsing: %s" % e)
                message = "[[%s]] Semantic usage failed parsing: %s" % (site['pagename'], e)
                self.botlog(bot='Bumble Bee', type='error', message=message)
                return False

            sql = """INSERT INTO smwextinfo
        (website_id, capture_date, response_timer,
         query_count, query_pages, query_concepts, query_pageslarge,
         size1, size2, size3, size4, size5, size6, size7, size8, size9, size10plus,
         format_broadtable, format_csv, format_category, format_count, format_dsv, format_debug, format_embedded,
         format_feed, format_json, format_list, format_ol, format_rdf, format_table, format_template, format_ul)
    VALUES
        ( %d, '%s', %f,
          %d, %d, %d, %d,
          %d, %d, %d, %d, %d, %d, %d, %d, %d, %d,
          %d, %d, %d, %d, %d, %d, %d,
          %d, %d, %d, %d, %d, %d, %d, %d)"""

            sql_command = sql % (
                site['Has ID'],
                self.sqlutcnow(),
                duration,
                y_data['smwqueries']['count'],
                y_data['smwqueries']['pages'],
                y_data['smwqueries']['concepts'],
                y_data['smwqueries']['pageslarge'],
                y_data['smwquerysizes']['Size 1'],
                y_data['smwquerysizes']['Size 2'],
                y_data['smwquerysizes']['Size 3'],
                y_data['smwquerysizes']['Size 4'],
                y_data['smwquerysizes']['Size 5'],
                y_data['smwquerysizes']['Size 6'],
                y_data['smwquerysizes']['Size 7'],
                y_data['smwquerysizes']['Size 8'],
                y_data['smwquerysizes']['Size 9'],
                y_data['smwquerysizes']['Size 10+'],
                y_data['smwformats']['broadtable'],
                y_data['smwformats']['csv'],
                y_data['smwformats']['category'],
                y_data['smwformats']['count'],
                y_data['smwformats']['dsv'],
                y_data['smwformats']['debug'],
                y_data['smwformats']['embedded'],
                y_data['smwformats']['feed'],
                y_data['smwformats']['json'],
                y_data['smwformats']['list'],
                y_data['smwformats']['ol'],
                y_data['smwformats']['rdf'],
                y_data['smwformats']['table'],
                y_data['smwformats']['template'],
                y_data['smwformats']['ul'])

            if self.args.verbose >= 3:
                print "SQL: %s" % sql_command

            cur = self.apiary_db.cursor()
            cur.execute(sql_command)
            cur.close()
            self.apiary_db.commit()

            self.stats['smwusage'] += 1

        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)
            return False

    def record_smwinfo(self, site):
        # Go out and get the statistic information
        data_url = site['Has API URL'] + '?action=smwinfo&info=propcount%7Cusedpropcount%7Cdeclaredpropcount%7Cproppagecount&format=json'
        if self.args.verbose >= 2:
            print "Pulling SMW info from %s." % data_url
        (status, data, duration) = self.pull_json(site['pagename'], data_url)

        ret_value = True
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
                self.record_error(site['pagename'], 'SMWInfo returned unexpected JSON.')
                message = "[[%s]] SMWInfo returned unexpected JSON." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)
                ret_value = False

        else:
            if self.args.verbose >= 3:
                print "Did not receive valid data from %s" % (data_url)
            ret_value = False

        # Update the status table that we did our work!
        # TODO: Commenting out. There is a bug that if this updates at the same time as the previous one
        # there is no change to the row, and my check for rows_affected in update_status will
        # not work as intended. Going to assume that smwinfo slaves off of regular statistics.
        #self.update_status(site, 'statistics')
        return ret_value

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
        ret_value = True
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/General" % site['pagename']
                template_block = self.build_general_template(data['query']['general'], '')
                socket.setdefaulttimeout(30)
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['general'] += 1
            else:
                self.record_error(site['pagename'], 'Returned unexpected JSON when general info.')
                message = "[[%s]] Returned unexpected JSON when general info." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)
                ret_value = False

        # Update the status table that we did our work! It doesn't matter if this was an error.
        self.update_status(site, 'general')
        return ret_value

    def build_extensions_template(self, ext_obj):
        h = HTMLParser.HTMLParser()

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        for x in ext_obj:
            if 'name' in x:
                template_block += "{{Extension in use\n"
                template_block += "|Extension name=%s\n" % (x['name'])
                if 'version' in x:
                    template_block += "|Extension version=%s\n" % (x['version'])

                    # Breakdown the version information for more detailed analysis
                    ver_details = self.parse_version(x['version'])
                    if 'major' in ver_details:
                        template_block += "|Extension version major=%s\n" % ver_details['major']
                    if 'minor' in ver_details:
                        template_block += "|Extension version minor=%s\n" % ver_details['minor']
                    if 'bugfix' in ver_details:
                        template_block += "|Extension version bugfix=%s\n" % ver_details['bugfix']
                    if 'flag' in ver_details:
                        template_block += "|Extension version flag=%s\n" % ver_details['flag']

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
        ret_value = True
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/Extensions" % site['pagename']
                template_block = self.build_extensions_template(data['query']['extensions'])
                socket.setdefaulttimeout(30)
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['extensions'] += 1
            else:
                self.record_error(site['pagename'], 'Returned unexpected JSON when requesting extension data.')
                message = "[[%s]] Returned unexpected JSON when requesting extension data." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)
                ret_value = False
        return ret_value

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
        ret_value = True
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/Skins" % site['pagename']
                template_block = self.build_skins_template(data['query']['skins'])
                socket.setdefaulttimeout(30)
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['skins'] += 1
            else:
                self.record_error(site['pagename'], 'Returned unexpected JSON when requesting skin data.')
                message = "[[%s]] Returned unexpected JSON when requesting skin data." % site['pagename']
                self.botlog(bot='Bumble Bee', type='warn', message=message)
                ret_value = False
        return ret_value

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
            if site['In error'] and self.args.verbose >= 1:
                print "Site %s (ID %d) is flagged in error." % (site['pagename'], site['Has ID'])
            req_statistics = False
            req_general = False
            (req_statistics, req_general) = self.get_status(site)
            if req_statistics:
                if site['Collect statistics']:
                    status = self.record_statistics(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])
                if site['Collect semantic statistics']:
                    status = self.record_smwinfo(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])
                if site['Collect semantic usage']:
                    status = self.record_smwusage(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])
            if req_general:
                time.sleep(2)  # TODO: this is dumb, doing to not trigger a problem with update_status again due to no rows being modified if the timestamp is the same. Forcing the timestamp to be +1 second
                if site['Collect general data']:
                    status = self.record_general(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])
                if site['Collect extension data']:
                    status = self.record_extensions(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])
                #if site['Collect skin data']:
                    #status = self.record_skins(site)
                    #if site['In error'] and status:
                        #site['In error'] = False
                        #self.clear_error(site['pagename'])

        duration = time.time() - start_time
        if self.args.segment is not None:
            message = "Completed processing for segment %d." % int(self.args.segment)
        else:
            message = "Completed processing for all websites."
        message += " Processed %d websites." % i
        message += " Counters statistics %d smwinfo %d smwusage %d general %d extensions %d skins %d skipped_stats: %d skipped_general: %d" % (
            self.stats['statistics'], self.stats['smwinfo'], self.stats['smwusage'], self.stats['general'],
            self.stats['extensions'], self.stats['skins'], self.stats['skippedstatistics'], self.stats['skippedgeneral'])
        self.botlog(bot='Bumble Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
