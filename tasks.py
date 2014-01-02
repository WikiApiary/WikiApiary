"""Celery tasks"""

from __future__ import absolute_import
from WikiApiary.celery import app
from WikiApiary.apiary.utils import *
import requests
import MySQLdb as mdb


@app.task
def update_general(has_api_url):
    """Async task to get siteinfo/general"""
    query_param = '?action=query&meta=siteinfo&siprop=general&format=json'

    try:
        req = requests.get(
            has_api_url + query_param,
            timeout = 10)
        if req.status_code == 200:
            print "SUCCESS!\n%s\n" % req.json()['query']['general']
            return True
        else:
            return False
    except Exception, err:
        print err
        return False

@app.task
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

@app.task
def update_skins(site):
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

@app.task
def record_extensions(site_id, sitename, api_url):
    data_url = api_url + "?action=query&meta=siteinfo&siprop=extensions&format=json"
    # (success, data, duration) = self.pull_json(site, data_url)
    req = requests.get(
            data_url,
            timeout = 10)
    data = req.json()
    success = True
    ret_value = True
    if success:
        # Successfully pulled data
        if 'query' in data:
            datapage = "%s/Extensions" % sitename
            template_block = build_extensions_template(data['query']['extensions'])
            print template_block
            c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
        else:
            # self.record_error(
            #     site=site,
            #     log_message='Returned unexpected JSON when requesting extension data.',
            #     log_type='warn',
            #     log_severity='normal',
            #     log_bot='Bumble Bee',
            #     log_url=data_url
            # )
            ret_value = False
    return ret_value

@app.task
def record_maxmind(site):
    # Create the Maxmind page to put all the geographic data in
    datapage = "%s/Maxmind" % site['pagename']
    hostname = urlparse.urlparse(site['Has API URL']).hostname
    template_block = self.BuildMaxmindTemplate(hostname)

    socket.setdefaulttimeout(30)
    c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
    if self.args.verbose >= 3:
        print c
    self.stats['maxmind'] += 1

@app.task
def record_whois(site):
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

@app.task
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
