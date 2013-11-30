#!/usr/bin/python

"""
Pull configuration files from WikiMedia to update WikiApiary.

"""

import re
import requests
import ConfigParser
from simplemediawiki import MediaWiki


class wmbot:

    # Array to append sites to
    sites = []
    # This file is a list of all the database names used by wikimedia
    # we can use this to try and derive the names of various wikis
    source_list = 'http://noc.wikimedia.org/conf/all.dblist'
    # Blank reference to store mediawiki object in
    wikiapiary = {}
    # Edit token
    my_token = ""
    # Counter
    create_counter = 0
    # Regex pattern
    regex_pattern = r'^(\w+)(wiki|wikibooks|wikiquote|wiktionary|wikinews|wikisource|wikiversity|wikimedia|wikivoyage)$'

    # Site data
    siteData = {
        'wiki': {
            'domain': 'wikipedia.org',
            'name': 'Wikipedia (%s)',
            'farm': 'Wikipedia',
            'logo': 'Wikipedia-logo.png'
        },
        'wikibooks': {
            'domain': 'wikibooks.org',
            'name': 'Wikibooks (%s)',
            'farm': 'Wikibooks',
            'logo': 'Wikibooks Logo.png'
        },
        'wiktionary': {
            'domain': 'wiktionary.org',
            'name': 'Wiktionary (%s)',
            'farm': 'Wiktionary',
            'logo': '170px-Wiktportal.svg.png'
        },
        'wikiquote': {
            'domain': 'wikiquote.org',
            'name': 'Wikiquote (%s)',
            'farm': 'Wikiquote',
            'logo': 'Wikiquote Logo.png'
        },
        'wikinews': {
            'domain': 'wikinews.org',
            'name': 'Wikinews (%s)',
            'farm': 'Wikinews',
            'logo': '240px-Wikinews-logo.png'
        },
        'wikisource': {
            'domain': 'wikisource.org',
            'name': 'Wikisource (%s)',
            'farm': 'Wikisource',
            'logo': 'Wikisource Logo.png'
        },
        'wikiversity': {
            'domain': 'wikiversity.org',
            'name': 'Wikiversity (%s)',
            'farm': 'Wikiversity',
            'logo': 'Wikiversity Logo.png'
        },
        'wikivoyage': {
            'domain': 'wikivoyage.org',
            'name': 'Wikivoyage (%s)',
            'farm': 'Wikivoyage',
            'logo': 'WikivoyageOldLogoSmall.png'
        },
        'wikimedia': {
            'domain': 'wikimedia.org',
            'name': 'Wikimedia (%s)',
            'farm': 'Wikimedia',
            'logo': 'Wikimediafoundation-logo.png'
        }
    }

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('../apiary.cfg')

        self.wikiapiary = MediaWiki(config.get('WikiApiary', 'api'))
        self.wikiapiary.login(config.get('wmbot', 'Username'), config.get('wmbot', 'Password'))

        # We need an edit token on wiki2
        c = self.wikiapiary.call({
            'action': 'query',
            'titles': 'Foo',
            'prop': 'info',
            'intoken': 'edit'
        })
        self.my_token = c['query']['pages']['-1']['edittoken']

    def getList(self):
        self.sites = requests.get(self.source_list).text.split('\n')

    def validateApi(self, api_url):
        # Call http://st.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=general&format=json
        my_url = api_url + '?action=query&meta=siteinfo&siprop=general&format=json'
        try:
            result = requests.get(my_url).json()
            if 'generator' in result['query']['general']:
                print "Detected %s" % result['query']['general']['generator']
                return True
            else:
                return False
        except:
            print "ERROR: Failed call to API check."
            return False

    def createSite(self, lang, token):
        siteTemplate = """{{Website
|Name=%s
|URL=%s
|API URL=%s
|Image=%s
|Farm=%s
|Collect general data=Yes
|Collect extension data=Yes
|Collect skin data=Yes
|Check every=240
|Collect statistics=Yes
|Audited=No
|Curated=No
|Active=Yes
}}
"""
        my_name = self.siteData[token]['name'] % lang
        my_template = siteTemplate % (
            my_name,
            "http://%s.%s/" % (lang, self.siteData[token]['domain']),
            "http://%s.%s/w/api.php" % (lang, self.siteData[token]['domain']),
            self.siteData[token]['logo'],
            self.siteData[token]['farm'])
        print my_template

        self.wikiapiary.call({
            'action': 'edit',
            'title': my_name,
            'text': my_template,
            'token': self.my_token,
            'bot': 'true'
        })
        self.create_counter += 1

    def checkSite(self, lang, site_domain):
        # Build the API URL using Wikimedia's known convention
        api_url = "http://%s.%s/w/api.php" % (lang, site_domain)
        print "Testing %s" % api_url

        # First see if this is a valid API URL before we query WikiApiary
        isValid = self.validateApi(api_url)

        if isValid:
            # Construct Ask query for WikiApiary
            my_query = ''.join([
                "[[Has API URL::%s]]" % api_url
            ])
            # Execute the query against WikiApiary
            c = self.wikiapiary.call({
                'action': 'ask',
                'query': my_query
            })

            # Return the count of results for the query
            return True, int(c['query']['meta']['count'])
        else:
            return False, 0

    def processSite(self, token):
        match = re.findall(self.regex_pattern, token)
        if len(match[0]) == 2:
            return match[0]
        else:
            return (False, False)

    def main(self):
        # Get the list of tokens from the config file
        self.getList()

        # Now loop through the tokens
        for token in self.sites:
            print "\nProcessing %s" % token
            # First turn a token into a lang and site
            (lang, site) = self.processSite(token)
            lang = lang.replace('_', '-')
            # If we successfully got lang and site proceed
            if lang is not False and site is not False:
                # Use a guess of the API domain to see if
                (valid, siteCount) = self.checkSite(lang, self.siteData[site]['domain'])

                if valid:
                    if siteCount == 0:
                        print "%s appears to be untracked token." % token
                        # Now add it to WikiApiary
                        self.createSite(lang, site)
                    elif siteCount == 1:
                        print "%s already exists." % token
                    elif siteCount > 1:
                        print "%s found %d websites, which should never happen." % (token, siteCount)
                else:
                    print "%s did not resolve to a valid API URL." % token
            else:
                print "%s could not process token." % token

# Run
if __name__ == '__main__':
    myClass = wmbot()
    myClass.main()
