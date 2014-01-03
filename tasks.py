"""Celery tasks"""

# pylint: disable=C0301

from __future__ import absolute_import
from WikiApiary.celery import app
from WikiApiary.apiary.utils import *
import requests
import MySQLdb as mdb
import datetime


# Constants used later to call various API methods
EXTENSION_QUERY = '?action=query&meta=siteinfo&siprop=extensions&format=json'
STATISTICS_QUERY = '?action=query&meta=siteinfo&siprop=statistics&format=json'
GENERAL_QUERY = '?action=query&meta=siteinfo&siprop=general&format=json'
SKIN_QUERY = '?action=query&meta=siteinfo&siprop=skins&format=json'
SMWINFO_QUERY = ''.join([
    '?action=smwinfo',
    '&info=propcount%7Cusedpropcount%7Cdeclaredpropcount%7Cproppagecount%7Cquerycount%7Cquerysize%7Cconceptcount%7Csubobjectcount',
    '&format=json'
    ])


@app.task
def record_general(site_id, sitename, api_url):
    data_url = api_url + GENERAL_QUERY

    req = requests.get(data_url, timeout = 30)
    duration = req.elapsed
    data = req.json()

    if req.status_code == 200:
        # Successfully pulled data
        if 'query' in data:
            datapage = "%s/General" % sitename
            template_block = build_general_template(site_id, data['query']['general'])

            c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})

            # Update the status table that we did our work! It doesn't matter if this was an error.
            update_status(site_id, 'general')

        else:
            record_error(
                site=site,
                log_message='Returned unexpected JSON when general info.',
                log_type='info',
                log_severity='normal',
                log_bot='Bumble Bee',
                log_url=data_url
            )
            return False
    else:
        return False

@app.task
def record_skins(site_id, sitename, api_url):
    """Pull skin data from website and write to WikiApiary."""
    data_url = site['Has API URL'] + SKIN_QUERY

    req = requests.get(data_url, timeout = 30)
    duration = req.elapsed
    data = req.json()

    if req.status_code == 200:
        # Successfully pulled data
        if 'query' in data:
            datapage = "%s/Skins" % sitename
            template_block = build_skins_template(data['query']['skins'])
            c = self.apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})
            return True
        else:
            record_error(
                site=site,
                log_message='Returned unexpected JSON when requesting skin data.',
                log_type='info',
                log_severity='normal',
                log_bot='Bumble Bee',
                log_url=data_url
            )
            return False
    else:
        return False

@app.task
def record_extensions(site_id, sitename, api_url):
    """Get extensions from the website and write them to WikiApiary."""

    data_url = api_url + EXTENSION_QUERY

    req = requests.get(data_url, timeout = 30)
    duration = req.elapsed
    data = req.json()

    if req.status_code == 200:
        # Successfully pulled data
        if 'query' in data:
            # Looks like a valid response
            datapage = "%s/Extensions" % sitename
            template_block = build_extensions_template(data['query']['extensions'])
            print template_block
            c = apiary_wiki.call({
                'action': 'edit',
                'title': datapage,
                'text': template_block,
                'token': self.edit_token,
                'bot': 'true'
                })
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
def record_maxmind(site_id, sitename, api_url):
    """Get MaxMind data for website and write to WikiApiary."""

    datapage = "%s/Maxmind" % sitename
    hostname = urlparse.urlparse(api_url).hostname
    template_block = BuildMaxmindTemplate(hostname)

    c = apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})

@app.task
def record_whois(site_id, sitename, api_url):
    # Now that we successfully got the data, we can make a quick query to get the server info
    hostname = urlparse.urlparse(api_url).hostname
    addr = socket.gethostbyname(hostname)

    datapage = "%s/Whois" % sitename
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

    c = apiary_wiki.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.edit_token, 'bot': 'true'})

@app.task
def record_smwinfo(site_id, sitename, api_url):
    """Pull skin data from website and write to WikiApiary."""

    data_url = api_url + SMWINFO_QUERY

    req = requests.get(data_url, timeout = 30)
    duration = req.elapsed
    data = req.json()

    if req.status_code == 200:

        if 'info' in data:
            # Record the data received to the database
            sql_command = """
                INSERT INTO smwinfo
                    (website_id, capture_date, response_timer, propcount, proppagecount, usedpropcount, declaredpropcount,
                        querycount, querysize, conceptcount, subobjectcount)
                VALUES
                    (%d, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

            propcount = data['info'].get('propcount', 'null')
            proppagecount = data['info'].get('proppagecount', 'null')
            usedpropcount = data['info'].get('usedpropcount', 'null')
            declaredpropcount = data['info'].get('declaredpropcount', 'null')

            # Catch additional results returned in SMW 1.9
            querycount = data['info'].get('querycount', 'null')
            querysize = data['info'].get('querysize', 'null')
            conceptcount = data['info'].get('conceptcount', 'null')
            subobjectcount = data['info'].get('subobjectcount', 'null')

            sql_command = sql_command % (
                site_id,
                sqlutcnow(),
                duration,
                propcount,
                proppagecount,
                usedpropcount,
                declaredpropcount,
                querycount,
                querysize,
                conceptcount,
                subobjectcount)

            runSql(sql_command)

            return True
        else:
            record_error(
                site=site,
                log_message='SMWInfo returned unexpected JSON.',
                log_type='info',
                log_severity='normal',
                log_bot='Bumble Bee',
                log_url=data_url
            )
            return False

    else:
        return False
