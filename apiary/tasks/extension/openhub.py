"""Record OpenHub data for extensions."""
# pylint: disable=C0301,R0201,R0904

from apiary.tasks import BaseApiaryTask
import logging
import requests
import ConfigParser
from xml.etree import ElementTree
import os

LOGGER = logging.getLogger()

class OpenHubTask(BaseApiaryTask):
    """Retrieve data from OpenHub to add to extensions."""

    def get_openhub_name(self, extension_name):
        try:
            wiki_return = self.bumble_bee.call({
                'action': 'ask',
                'query': ''.join([
                    "[[%s]]" % extension_name,
                    "|?Has OpenHub project"
                ])
            })
        except Exception, e:
            raise Exception("Error while querying for OpenHub project name for %s (%s)." % (extension_name, e))

        try:
            return wiki_return['query']['results'][extension_name]['printouts']['Has OpenHub project'][0]
        except Exception, e:
            return None


    def run(self, extension_name):
        """Get OpenHub data for extension and write to WikiApiary."""

        APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')
        if os.path.isfile(APIARY_CONFIG):
            LOGGER.info("Detected configuration at %s" % APIARY_CONFIG)
            config = ConfigParser.SafeConfigParser()
            config.read(APIARY_CONFIG)
            OPENHUB_API_KEY = config.get('OpenHub', 'API Key')
        else:
            raise Exception("No configuration file detected to get OpenHub API key")

        # TODO: Find the OpenHub name via the property for the given extension
        openhub_name = self.get_openhub_name(extension_name)

        openhub_url = "https://www.openhub.net/p/%s.xml?api_key=%s" % (openhub_name, OPENHUB_API_KEY)
        response = requests.get(openhub_url)
        openhub_data = ElementTree.fromstring(response.content)

        datapage = "%s/OpenHub" % extension_name
        template_block = self.generate_template(openhub_data)

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

    def generate_template(self, openhub_data):
        """Build a the wikitext for the OpenHub subpage."""

        template_block = "<noinclude>{{OpenHub subpage}}</noinclude><includeonly>"
        template_block += "{{OpenHub\n"

        project = openhub_data.find("result").find("project")
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




