"""Get skin data."""
# pylint: disable=C0301,R0201

from WikiApiary.apiary.tasks import BaseApiaryTask
from WikiApiary.apiary.utils import filter_illegal_chars
import requests
import logging
import operator


LOGGER = logging.getLogger()

class RecordNamespacesTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        """Pull namespace data from website and write to WikiApiary."""
        data_url = api_url + '?action=query&meta=siteinfo&siprop=namespaces&format=json'

        try:
            req = requests.get(data_url, timeout = 15)
            data = req.json()
        except Exception, e:
            LOGGER.error(e)
            return False

        if req.status_code == 200:
            if 'query' in data:
                template_block = self.generate_template(data['query']['namespaces'])
                wiki_return = self.bumble_bee.call({
                    'action': 'edit',
                    'title': "%s/Namespaces" % sitename,
                    'text': template_block,
                    'token': self.bumble_bee_token,
                    'bot': 'true'})
                LOGGER.debug(wiki_return)
                if 'error' in wiki_return:
                    LOGGER.warn(wiki_return)
                    return False
                else:
                    return True
            else:
                self.record_error(
                    site=sitename,
                    log_message='Returned unexpected JSON when requesting namespace data.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                return False
        return False

    def generate_template(self, ext_obj):
        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            '*': 'Namespace'
        }

        template_block = "<noinclude>{{Namespaces subpage}}</noinclude><includeonly>"

        for x in ext_obj:
            # Start the template instance
            template_block += "{{Namespace in use\n"
            for item in ext_obj[x]:
                # Loop through all the items in the namespace data and build the instance
                if item not in ignore_keys:
                    name = key_names.get(item, item)
                    value = ext_obj[x][item]

                    if item in ['subpages', 'content']:
                        # This parameter won't appear unless it is true
                        value = True

                    template_block += "|%s=%s\n" % (name, value)

            # Now end the template instance
            template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block
