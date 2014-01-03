#!/usr/bin/python
"""
Bumble Bee is responsible for collecting statistics and other information from
sites registered on WikiApiary. See http://wikiapiary.com/wiki/User:Bumble_Bee
for more information.

Jamie Thingelstad <jamie@thingelstad.com>
http://wikiapiary.com/wiki/User:Thingles
http://thingelstad.com/
"""

from apiary import bot
from apiary import website


# Code snippet for what this *should* look like
# when it is refactored right
# bot = new Bot(
#     name="Bumble Bee",
#     api_url="http://wikiapiary.com/w/api.php",
#     username="Bumble Bee",
#     password="1234",
#     debug=True)

# bot.log(
#     message="Starting run for segment 1",
#     severity="Info")

# segment = bot.get-segment(1)

# for website in segment:
#     website.get-data()
#     website.update-information()

# bot.log("Completed run for segment 1")


class BumbleBee(bot.Bot):
    """Bot that collects statistics for sites."""
    def __init__(self):
        super(BumbleBee, self).__init__()

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

    def record_statistics(self, site, method):
        if method == 'API':
            # Go out and get the statistic information
            data_url = site['Has API URL'] + '?action=query&meta=siteinfo&siprop=statistics&format=json'
            if self.args.verbose >= 2:
                print "Pulling statistics info from %s." % data_url
            (status, data, duration) = self.pull_json(site, data_url)
        elif method == 'Statistics':
            # Get stats the old fashioned way
            data_url = site['Has statistics URL']
            if "?" in data_url:
                data_url += "&action=raw"
            else:
                data_url += "?action=raw"
            if self.args.verbose >= 2:
                print "Pulling statistics from %s." % data_url

            # This is terrible and should be put into pull_json somewhow
            socket.setdefaulttimeout(15)

            # Get CSV data via raw Statistics call
            req = urllib2.Request(data_url)
            req.add_header('User-Agent', self.config.get('Bumble Bee', 'User-Agent'))
            opener = urllib2.build_opener()

            try:
                start_time = datetime.datetime.now()
                f = opener.open(req)
                duration = (datetime.datetime.now() - start_time).total_seconds()
            except Exception, e:
                self.record_error(
                    site=site,
                    log_message="%s" % e,
                    log_type='error',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                status = False
            else:
                # Create an object that is the same as that returned by the API
                ret_string = f.read()
                ret_string = ret_string.strip()
                if re.match(r'(\w+=\d+)\;?', ret_string):
                    # The return value looks as we expected
                    status = True
                    data = {}
                    data['query'] = {}
                    data['query']['statistics'] = {}
                    items = ret_string.split(";")
                    for item in items:
                        (name, value) = item.split("=")
                        try:
                            # Convert the value to an int, if this fails we skip it
                            value = int(value)
                            if name == "total":
                                name = "pages"
                            if name == "good":
                                name = "articles"
                            if self.args.verbose >= 3:
                                print "Transforming %s to %s" % (name, value)
                            data['query']['statistics'][name] = value
                        except:
                            if self.args.verbose >= 3:
                                print "Illegal value '%s' for %s." % (value, name)
                else:
                    status = False # The result didn't match the pattern expected
                    self.record_error(
                        site=site,
                        log_message="Unexpected response to statistics call",
                        log_type='error',
                        log_severity='normal',
                        log_bot='Bumble Bee',
                        log_url=data_url
                    )
                    if self.args.verbose >= 3:
                        print "Result from statistics was not formatted as expected:\n%s" % ret_string

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
                    if data['activeusers'] < 0:
                        data['activeusers'] = 0
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

                self.runSql(sql_command)
                self.stats['statistics'] += 1
            else:
                self.record_error(
                    site=site,
                    log_message='Statistics returned unexpected JSON.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
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
        (status, data, duration) = self.pull_json(site, data_url)

        if status:
            try:
                data_block = data['parse']['text']['*']
                data_soup = BeautifulSoup.BeautifulSoup(data_block)
                json_block = data_soup.find("div", {"id": "wikiapiary-semantic-usage-data"})
                json_data = simplejson.loads(json_block.text)
            except Exception, e:
                self.record_error(
                    site=site,
                    log_message="Semantic usage failed parsing: %s" % e,
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
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

            self.runSql(sql_command)
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
        (status, data, duration) = self.pull_json(site, data_url)

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

                self.runSql(sql_command)
                self.stats['smwinfo'] += 1
            else:
                self.record_error(
                    site=site,
                    log_message='SMWInfo returned unexpected JSON.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
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

    def build_general_template(self, site_id, x):

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
                if key == 'dbversion':
                    value = self.ProcessMultiprops(site_id, key, value)

                template_block += "|%s=%s\n" % (name, value)

        template_block += "}}\n</includeonly>\n"

        return template_block

    def BuildMaxmindTemplate(self, hostname):
        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"
        template_block += "{{Maxmind\n"

        gi = pygeoip.GeoIP('../vendor/GeoLiteCity.dat')
        data = gi.record_by_name(hostname)

        for val in data:
            template_block += "|%s=%s\n" % (val, data[val])

        template_block += "}}\n</includeonly>\n"

        return template_block

    def record_general(self, site):
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=general&format=json"
        if self.args.verbose >= 2:
            print "Pulling general info info from %s." % data_url
        (success, data, duration) = self.pull_json(site, data_url)
        ret_value = True
        if success:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/General" % site['pagename']
                template_block = self.build_general_template(site['Has ID'], data['query']['general'])

                socket.setdefaulttimeout(30)
                c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
                if self.args.verbose >= 3:
                    print c
                self.stats['general'] += 1
            else:
                self.record_error(
                    site=site,
                    log_message='Returned unexpected JSON when general info.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                ret_value = False

        # Update the status table that we did our work! It doesn't matter if this was an error.
        self.update_status(site, 'general')
        return ret_value

    def record_whois(self, site):
        # Now that we successfully got the data, we can make a quick query to get the server info
        hostname = urlparse.urlparse(site['Has API URL']).hostname
        addr = socket.gethostbyname(hostname)

        datapage = "%s/Whois" % site['pagename']
        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"
        template_block += "{{Whois\n"

        template_block += "|HTTP server=%s\n" % ('')
        try:
            template_block += "|IP address=%s\n" % (self.ProcessMultiprops(site['Has ID'], 'addr', addr))
        except:
            pass

        try:
            reverse_host = socket.gethostbyaddr(addr)[0]
            template_block += "|Reverse lookup=%s\n" % (self.ProcessMultiprops(site['Has ID'], 'reverse_host', reverse_host))
        except:
            pass

        # Now lets get the netblock information
        try:
            whois = Whois()
            netblock_owner = whois.getNetworkRegistrationRelatedToIP(addr, format='json')['net']['orgRef']['@name']
            netblock_owner_handle = whois.getNetworkRegistrationRelatedToIP(addr, format='json')['net']['orgRef']['@handle']
            template_block += "|Netblock organization=%s\n" % (netblock_owner)
            template_block += "|Netblock organization handle=%s\n" % netblock_owner_handle
        except:
            pass

        template_block += "}}\n</includeonly>\n"

        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
        if self.args.verbose >= 3:
            print c
        self.stats['whois'] += 1


    def record_maxmind(self, site):
        # Create the Maxmind page to put all the geographic data in
        datapage = "%s/Maxmind" % site['pagename']
        hostname = urlparse.urlparse(site['Has API URL']).hostname
        template_block = self.BuildMaxmindTemplate(hostname)

        socket.setdefaulttimeout(30)
        c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
        if self.args.verbose >= 3:
            print c
        self.stats['maxmind'] += 1


    def build_extensions_template(self, ext_obj):
        h = HTMLParser.HTMLParser()

        # Some keys we do not want to store in WikiApiary
        ignore_keys = ['descriptionmsg']
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
                            # Before unescaping 'regular' unicode characters, first deal with spaces
                            # because they cause problems when converted to unicode non-breaking spaces
                            value = value.replace('&nbsp;', ' ').replace('&#160;', ' ').replace('&160;', ' ')
                            value = h.unescape(value)

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
        (success, data, duration) = self.pull_json(site, data_url)
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
                self.record_error(
                    site=site,
                    log_message='Returned unexpected JSON when requesting extension data.',
                    log_type='warn',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                ret_value = False
        return ret_value

    def build_skins_template(self, ext_obj):

        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            '*': 'Skin name',
            'code': 'Skin code',
            'default': 'Default skin',
            'unusable': 'Skipped skin'
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

                        if item == 'default':
                            # This parameter won't appear unless it is true
                            value = True

                        if item == 'unusable':
                            # This paramter won't appear unless it is true
                            value = True

                        template_block += "|%s=%s\n" % (name, value)

                # Now end the template instance
                template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block

    def record_skins(self, site):
        data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=skins&format=json"
        if self.args.verbose >= 2:
            print "Pulling skin info from %s." % data_url
        (success, data, duration) = self.pull_json(site, data_url)
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
                self.record_error(
                    site=site,
                    log_message='Returned unexpected JSON when requesting skin data.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                ret_value = False
        return ret_value

    def main(self):
        if self.args.site is not None:
            message = "Starting processing for site %d." % int(self.args.site)
        elif self.args.segment is not None:
            message = "Starting processing for segement %d." % int(self.args.segment)
        else:
            message = "Starting processing for all websites."
        self.botlog(bot='Bumble Bee', message=message)

        # Record time at beginning
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Bumble Bee')

        # Get list of websites to work on
        sites = self.get_websites(self.args.segment, self.args.site)

        i = 0
        for site in sites:
            i += 1
            if self.args.verbose >= 1:
                print "\n\n%d: Processing %s (ID %d)" % (i, site['pagename'], site['Has ID'])
            req_statistics = False
            req_general = False
            if self.args.force:
                (req_statistics, req_general) = (True, True)
            else:
                (req_statistics, req_general) = self.get_status(site)

            # Put this section in a try/catch so that we can proceed even if a single site causes a problem
            try:
                process = "unknown"
                if req_statistics:
                    if site['Collect statistics']:
                        process = "collect statistics (API)"
                        status = self.record_statistics(site, 'API')
                    if site['Collect statistics stats']:
                        process = "collect statistics (Statistics)"
                        status = self.record_statistics(site, 'Statistics')
                    if site['Collect semantic statistics']:
                        process = "collect semantic statistics"
                        status = self.record_smwinfo(site)
                    if site['Collect semantic usage']:
                        process = "collect semantic usage"
                        status = self.record_smwusage(site)
                if req_general:
                    time.sleep(2)  # TODO: this is dumb, doing to not trigger a problem with update_status again due to no rows being modified if the timestamp is the same. Forcing the timestamp to be +1 second
                    self.record_whois(site)
                    self.record_maxmind(site)
                    if site['Collect general data']:
                        process = "collect general data"
                        status = self.record_general(site)
                    if site['Collect extension data']:
                        process = "collect extension data"
                        status = self.record_extensions(site)
                    if site['Collect skin data']:
                        process = "collect skin data"
                        status = self.record_skins(site)
            except Exception, e:
                self.record_error(
                    site=site,
                    log_message='Unhandled exception %s during %s' % (str(e), process),
                    log_type='error',
                    log_severity='normal',
                    log_bot='Bumble Bee'
                )

        duration = time.time() - start_time
        if self.args.segment is not None:
            message = "Completed processing for segment %d." % int(self.args.segment)
        else:
            message = "Completed processing for all websites."
        message += " Processed %d websites." % i
        message += " Counters statistics %d smwinfo %d smwusage %d general %d extensions %d skins %d skipped_stats: %d skipped_general: %d whois: %d maxmind: %d" % (
            self.stats['statistics'], self.stats['smwinfo'], self.stats['smwusage'], self.stats['general'],
            self.stats['extensions'], self.stats['skins'], self.stats['skippedstatistics'], self.stats['skippedgeneral'],
            self.stats['whois'], self.stats['maxmind'])
        self.botlog(bot='Bumble Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
