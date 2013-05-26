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
import BeautifulSoup
import operator
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
            y = re.match(r'.*(alpha|beta|wmf|CLDR|MLEB|stable).*', t)
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
                data_soup = BeautifulSoup.BeautifulSoup(data_block)
                json_block = data_soup.find("div", {"id": "wikiapiary-semantic-usage-data"})
                json_data = simplejson.loads(json_block.text)
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
                json_data['smwqueries']['count'],
                json_data['smwqueries']['pages'],
                json_data['smwqueries']['concepts'],
                json_data['smwqueries']['pageslarge'],
                json_data['smwquerysizes']['size-1'],
                json_data['smwquerysizes']['size-2'],
                json_data['smwquerysizes']['size-3'],
                json_data['smwquerysizes']['size-4'],
                json_data['smwquerysizes']['size-5'],
                json_data['smwquerysizes']['size-6'],
                json_data['smwquerysizes']['size-7'],
                json_data['smwquerysizes']['size-8'],
                json_data['smwquerysizes']['size-9'],
                json_data['smwquerysizes']['size-10plus'],
                json_data['smwformats']['broadtable'],
                json_data['smwformats']['csv'],
                json_data['smwformats']['category'],
                json_data['smwformats']['count'],
                json_data['smwformats']['dsv'],
                json_data['smwformats']['debug'],
                json_data['smwformats']['embedded'],
                json_data['smwformats']['feed'],
                json_data['smwformats']['json'],
                json_data['smwformats']['list'],
                json_data['smwformats']['ol'],
                json_data['smwformats']['rdf'],
                json_data['smwformats']['table'],
                json_data['smwformats']['template'],
                json_data['smwformats']['ul'])

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
        data_url = site['Has API URL'] + ''.join([
            '?action=smwinfo',
            '&info=propcount%7Cusedpropcount%7Cdeclaredpropcount%7Cproppagecount%7Cquerycount%7Cquerysize%7Cconceptcount%7Csubobjectcount',
            '&format=json'])
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
                        (website_id, capture_date, response_timer, propcount, proppagecount, usedpropcount, declaredpropcount,
                            querycount, querysize, conceptcount, subobjectcount)
                    VALUES
                        (%d, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

                # Catch additional results returned in SMW 1.9
                if 'querycount' in data['info']:
                    querycount = data['info']['querycount']
                else:
                    querycount = 'null'
                if 'querysize' in data['info']:
                    querysize = data['info']['querysize']
                else:
                    querysize = 'null'
                if 'conceptcount' in data['info']:
                    conceptcount = data['info']['conceptcount']
                else:
                    conceptcount = 'null'
                if 'subobjectcount' in data['info']:
                    subobjectcount = data['info']['subobjectcount']
                else:
                    subobjectcount = 'null'

                sql_command = sql_command % (
                    site['Has ID'],
                    self.sqlutcnow(),
                    duration,
                    propcount,
                    proppagecount,
                    usedpropcount,
                    declaredpropcount,
                    querycount,
                    querysize,
                    conceptcount,
                    subobjectcount)

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

        # Some keys we do not want to store in WikiApiary
        ignore_keys = ['time', 'fallback', 'fallback8bitEncoding']
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            'dbtype': 'Database type',
            'dbversion': 'Database version',
            'generator': 'MediaWiki version',
            'lang': 'Language',
            'timezone': 'Timezone',
            'timeoffset': 'Timeoffset',
            'sitename': 'Sitename',
            'rights': 'Rights',
            'phpversion': 'PHP Version',
            'phpsapi': 'PHP Server API',
            'wikiid': 'Wiki ID'
        }

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        template_block += "{{General siteinfo\n"
        template_block += "|HTTP server=%s\n" % (server)

        # Loop through all the keys provided and create the template block
        for key in x:
            # Make sure we aren't ignoring this key
            if key not in ignore_keys:
                # If we have a name for this key use that
                name = key_names.get(key, key)
                value = x[key]

                # For some items we may need to do some preprocessing
                if isinstance(value, basestring):
                    # A pipe will break the template, try HTML entity encoding it instead
                    value = value.replace('|', '&#124;')
                if key == 'lang':
                    # Make sure language is all lowercase, and try to standardize structure
                    value = value.lower().replace('_', '-').replace(' ', '-')
                if key == 'sitename':
                    # Sometimes a : appears in sitename and messes up semantics
                    # Try using an HTML entity instead
                    value = value.replace(':', '&#58;')

                template_block += "|%s=%s\n" % (name, value)

        template_block += "}}\n</includeonly>"

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

        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            'author': 'Extension author',
            'name': 'Extension name',
            'version': 'Extension version',
            'type': 'Extension type',
            'url': 'Extension URL'
        }

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        for x in ext_obj:
            if 'name' in x:
                template_block += "{{Extension in use\n"

                for item in x:
                    if item not in ignore_keys:

                        name = key_names.get(item, item)
                        value = x[item]

                        if item == 'name':
                            # Sometimes people make the name of the extension a hyperlink using
                            # wikitext links and this makes things ugly. So, let's detect that if present.
                            if re.match(r'\[(http[^\s]+)\s+([^\]]+)\]', value):
                                (possible_url, value) = re.findall(r'\[(http[^\s]+)\s+([^\]]+)\]', value)[0]
                                # If a URL was given in the name, and not given as a formal part of the
                                # extension definition (yes, this happens) then add this to the template
                                # it is up to the template to decide what to do with this
                                template_block += "|URL Embedded in name=%s" % possible_url

                            value = self.filter_illegal_chars(value)

                        if item == 'version':
                            # Breakdown the version information for more detailed analysis
                            ver_details = self.parse_version(value)
                            if 'major' in ver_details:
                                template_block += "|Extension version major=%s\n" % ver_details['major']
                            if 'minor' in ver_details:
                                template_block += "|Extension version minor=%s\n" % ver_details['minor']
                            if 'bugfix' in ver_details:
                                template_block += "|Extension version bugfix=%s\n" % ver_details['bugfix']
                            if 'flag' in ver_details:
                                template_block += "|Extension version flag=%s\n" % ver_details['flag']

                        if item == 'author':
                            # Authors can have a lot of junk in them, wikitext and such.
                            # We'll try to clean that up.

                            # Wikilinks with names
                            # "[[Foobar | Foo Bar]]"
                            value = re.sub(r'\[\[.*\|(.*)\]\]', r'\1', value)
                            # Simple Wikilinks
                            value = re.sub(r'\[\[(.*)\]\]', r'\1', value)
                            # Hyperlinks as wikiext
                            # "[https://www.mediawiki.org/wiki/User:Jeroen_De_Dauw Jeroen De Dauw]"
                            value = re.sub(r'\[\S+\s+([^\]]+)\]', r'\1', value)
                            # Misc text
                            value = re.sub(r'\sand\s', r', ', value)
                            value = re.sub(r'\.\.\.', r'', value)
                            value = re.sub(r'&nbsp;', r' ', value)
                            # Lastly, there could be HTML encoded stuff in these
                            value = h.unescape(value)

                        if item == 'url':
                            # Seems some people really really love protocol agnostic URL's
                            # We detect them and add a generic http: protocol to them
                            if re.match(r'^\/\/', value):
                                value = 'http:' + value

                        template_block += "|%s=%s\n" % (name, value)

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

        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            '*': 'Skin name',
            'code': 'Skin code'
        }

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

        # Skins are returned in random order so we need to sort them before
        # making the template, otherwise we generate a lot of edits
        # that are just different ordering
        skins_sorted = sorted(ext_obj, key=operator.itemgetter('*'))

        for x in skins_sorted:
            if '*' in x:
                # Start the template instance
                template_block += "{{Skin in use\n"
                for item in x:
                    # Loop through all the items in the skin data and build the instance
                    if item not in ignore_keys:
                        name = key_names.get(item, item)
                        value = x[item]

                        if item == '*':
                            value = self.filter_illegal_chars(value)

                        template_block += "|%s=%s\n" % (name, value)

                # Now end the template instance
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
                if site['Collect skin data']:
                    status = self.record_skins(site)
                    if site['In error'] and status:
                        site['In error'] = False
                        self.clear_error(site['pagename'])

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
