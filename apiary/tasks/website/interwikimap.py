"""Get skin data."""
# pylint: disable=C0301,R0201

from WikiApiary.apiary.tasks import BaseApiaryTask
from WikiApiary.apiary.utils import filter_illegal_chars
import requests
import logging
import operator


LOGGER = logging.getLogger()

class RecordInterwikimapTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        """Pull skin data from website and write to WikiApiary."""
        data_url = api_url + '?action=query&meta=siteinfo&siprop=interwikimap&format=json'

        try:
            req = requests.get(data_url, timeout = 30)
            data = req.json()
        except Exception, e:
            LOGGER.error(e)
            return False

        if req.status_code == 200:
            if 'query' in data:
                template_block = self.generate_template(data['query']['interwikimap'])
                wiki_return = self.bumble_bee.call({
                    'action': 'edit',
                    'title': "%s/Interwikimap" % sitename,
                    'text': template_block,
                    'token': self.bumble_bee_token,
                    'bot': 'true'})
                LOGGER.debug(wiki_return)
                return True
            else:
                self.record_error(
                    site=sitename,
                    log_message='Returned unexpected JSON when requesting interwikimap data.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                return False
        return False

    def generate_template(self, ext_obj):
        """Build a the wikitext for the skin subpage."""

        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {}

        template_block = "<noinclude>{{Interwikimap subpage}}</noinclude><includeonly>"

        # Skins are returned in random order so we need to sort them before
        # making the template, otherwise we generate a lot of edits
        # that are just different ordering
        interwiki_sorted = sorted(ext_obj, key=operator.itemgetter('prefix'))

        for x in interwiki_sorted:
            if 'prefix' in x:
                # Start the template instance
                template_block += "{{Interwiki link\n"
                for item in x:
                    # Loop through all the items in the interwiki data and build the instance
                    if item not in ignore_keys:
                        name = key_names.get(item, item)
                        value = x[item]

                        if item == 'local':
                            # This parameter won't appear unless it is true
                            value = True

                        template_block += "|%s=%s\n" % (name, value)

                # Now end the template instance
                template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block
