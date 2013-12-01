#!/usr/bin/python

"""
Pull configuration files from WikiMedia to update WikiApiary.

"""

import requests
from BeautifulSoup import BeautifulSoup
import ConfigParser
import time
from simplemediawiki import MediaWiki
from apiary import farm


class wikkii(Farm):

    # Array to append sites to
    sites = []
    # This file is a list of all the database names used by wikimedia
    # we can use this to try and derive the names of various wikis
    source_list = 'http://wikkii.com/wiki/Special:Farmer/list'
    # Blank reference to store mediawiki object in
    wikiapiary = {}
    # Edit token
    my_token = ""
    # Counter
    create_counter = 0

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('../apiary.cfg')

        self.wikiapiary = MediaWiki(config.get('WikiApiary', 'api'))
        self.wikiapiary.login(config.get('wikkiibot', 'Username'), config.get('wikkiibot', 'Password'))

        # We need an edit token on wiki2
        c = self.wikiapiary.call({
            'action': 'query',
            'titles': 'Foo',
            'prop': 'info',
            'intoken': 'edit'
        })
        self.my_token = c['query']['pages']['-1']['edittoken']

    def getList(self):
        soup = BeautifulSoup(requests.get(self.source_list).text)
        i = 1
        for item in soup.findAll("a", {"class": "extiw"}):
            site = (item.contents[0], item["href"], item["title"])
            print i, site
            self.sites.append(site)
            i += 1

    def validateStats(self, url):
        my_url = "%s/wiki/Special:Statistics?action=raw" % url
        try:
            result = requests.get(my_url, timeout=10).text
            values = result.split(';')
            if len(values) == 9:
                print "Got %d values from stats" % len(values)
                return True
            else:
                return False
        except:
            print "ERROR: Failed call to Statistics URL."
            return False

    def createSite(self, name, url):
        siteTemplate = """{{Website
|Name=%s
|URL=%s
|Image=Default website image.png
|Farm=Wikkii
|Collection method=API, Special:Statistics
|API URL=%s
|Collect general data=No
|Collect extension data=No
|Collect skin data=No
|Collect statistics=No
|Collect semantic statistics=No
|Collect semantic usage=No
|Collect logs=No
|Collect recent changes=No
|Statistics URL=%s
|Collect statistics stats=Yes
|Check every=240
|Audited=No
|Validated=No
|Curated=No
|Active=Yes
|Demote=No
|Defunct=No
|Error=No
|Featured website vote=0
}}
"""
        api_url = "%sw/api.php" % url
        statistics_url = "%swiki/Special:Statistics" % url

        # Make sure a page doesn't exist with this name already
        c = self.wikiapiary.call({
            'action': 'query',
            'titles': name
        })
        try:
            if c['query']['pages']['-1']:
                print "No duplicate name detected."
        except:
            # Duplicate detected
            name = "%s (Wikkii)" % name

        my_template = siteTemplate % (name, url, api_url, statistics_url)
        print my_template

        c = self.wikiapiary.call({
            'action': 'edit',
            'title': name,
            'text': my_template,
            'token': self.my_token,
            'bot': 'true',
            'summary': 'Creating entry for %s' % name
        })
        print c
        self.create_counter += 1

    def checkSite(self, site):
        print "Checking %s" % site[1]

        # Construct Ask query for WikiApiary
        my_query = ''.join([
            "[[Has statistics URL::%swiki/Special:Statistics]]" % site[1]
        ])
        # Execute the query against WikiApiary
        c = self.wikiapiary.call({
            'action': 'ask',
            'query': my_query
        })

        # Return the count of results for the query
        return int(c['query']['meta']['count'])

    def main(self):
        # Get the list of tokens from the config file
        self.getList()

        for site in self.sites:
            # Limit the number of sites we make per run
            if self.create_counter > 1000:
                break

            print "\nProcessing %s" % site[0]

            # Use a guess of the API domain to see if we have it already
            siteCount = self.checkSite(site)

            if siteCount == 0:
                print "%s is not in WikiApiary, validating stats." % site[0]
                if self.validateStats(site[1]):
                    # Now add it to WikiApiary
                    self.createSite(site[0], site[1])
                    time.sleep(3)
                else:
                    print "%s did not resolve to a valid API URL." % site[0]
            elif siteCount == 1:
                print "%s already exists, skipping." % site[0]
            elif siteCount > 1:
                print "ERROR: %s found %d websites, which should never happen." % (site[0], siteCount)

# Run
if __name__ == '__main__':
    myClass = wikkii()
    myClass.main()
