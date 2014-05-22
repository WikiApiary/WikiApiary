"""Record MaxMind data."""
# pylint: disable=C0301,R0201,R0904

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging
import urlparse
import pygeoip
import os

LOGGER = logging.getLogger()
GEODATA = '../vendor/GeoLiteCity.dat'

class MaxmindTask(BaseApiaryTask):
    """Use the MaxMind GeoIP database to associated geo data with websites."""

    def run(self, site_id, sitename, api_url):
        """Get MaxMind data for website and write to WikiApiary."""

        # Make sure we have the database to do this, if not just return
        # false immediately
        if not os.path.isfile(GEODATA):
            raise Exception("Unable to load MaxMind database at %s" % GEODATA)

        datapage = "%s/Maxmind" % sitename
        hostname = urlparse.urlparse(api_url).hostname
        template_block = self.generate_template(hostname)

        wiki_return = self.bumble_bee.call({
            'action': 'edit',
            'title': datapage,
            'text': template_block,
            'token': self.bumble_bee_token,
            'bot': 'true'
        })
        LOGGER.debug(wiki_return)
        if 'error' in wiki_return:
            LOGGER.warn(wiki_return)
            raise
        else:
            return True

    def generate_template(self, hostname):
        """Build a the wikitext for the maxmind subpage."""

        template_block = "<noinclude>{{Maxmind subpage}}</noinclude><includeonly>"
        template_block += "{{Maxmind\n"

        geoip = pygeoip.GeoIP(GEODATA)
        data = geoip.record_by_name(hostname)

        for val in data:
            template_block += "|%s=%s\n" % (val, data[val])

        template_block += "}}\n</includeonly>\n"

        return template_block

