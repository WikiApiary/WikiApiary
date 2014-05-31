"""Record Ohloh data for extensions."""
# pylint: disable=C0301,R0201,R0904

from apiary.tasks import BaseApiaryTask
import logging
import requests
import ConfigParser
from xml.etree import ElementTree
import os

LOGGER = logging.getLogger()

class OhlohTask(BaseApiaryTask):
    """Retrieve data from Ohloh to add to extensions."""

    def get_ohloh_name(self, extension_name):
        try:
            wiki_return = self.bumble_bee.call({
                'action': 'ask',
                'query': ''.join([
                    "[[%s]]" % extension_name,
                    "|?Has Ohloh project"
                ])
            })
        except Exception, e:
            raise Exception("Error while querying for Ohloh project name for %s (%s)." % (extension_name, e))

        try:
            return wiki_return['query']['results'][extension_name]['printouts']['Has Ohloh project'][0]
        except Exception, e:
            return None


    def run(self, extension_name):
        """Get Ohloh data for extension and write to WikiApiary."""

        APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')
        if os.path.isfile(APIARY_CONFIG):
            LOGGER.info("Detected configuration at %s" % APIARY_CONFIG)
            config = ConfigParser.SafeConfigParser()
            config.read(APIARY_CONFIG)
            OHLOH_API_KEY = config.get('Ohloh', 'API Key')
        else:
            raise Exception("No configuration file detected to get Ohloh API key")

        # TODO: Find the Ohloh name via the property for the given extension
        ohloh_name = self.get_ohloh_name(extension_name)

        ohloh_url = "https://www.ohloh.net/p/%s.xml?api_key=%s" % (ohloh_name, OHLOH_API_KEY)
        response = requests.get(ohloh_url)
        ohloh_data = ElementTree.fromstring(response.content)

        datapage = "%s/Ohloh" % extension_name
        template_block = self.generate_template(ohloh_data)

        wiki_return = self.bumble_bee.call({
            'action': 'edit',
            'title': datapage,
            'text': template_block,
            'token': self.bumble_bee_token,
            'bot': 'true'
        })
        LOGGER.debug(wiki_return)
        if 'error' in wiki_return:
            raise Exception(wiki_return)

        return wiki_return

    def generate_template(self, ohloh_data):
        """Build a the wikitext for the Ohloh subpage."""

        template_block = "<noinclude>{{Ohloh subpage}}</noinclude><includeonly>"
        template_block += "{{Ohloh\n"

        project = ohloh_data.find("result").find("project")
        analysis = project.find("analysis")

        template_block += "|rating_count=%s\n" % project.find("rating_count").text
        template_block += "|average_rating=%s\n" % project.find("average_rating").text
        template_block += "|updated_at=%s\n" % analysis.find("updated_at").text
        template_block += "|twelve_month_contributor_count=%s\n" % analysis.find("twelve_month_contributor_count").text
        template_block += "|total_contributor_count=%s\n" % analysis.find("total_contributor_count").text
        template_block += "|twelve_month_commit_count=%s\n" % analysis.find("twelve_month_commit_count").text
        template_block += "|total_commit_count=%s\n" % analysis.find("total_commit_count").text
        template_block += "|total_code_lines=%s\n" % analysis.find("total_code_lines").text

        template_block += "}}\n</includeonly>\n"

        return template_block




