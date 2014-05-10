"""Record general information."""
# pylint: disable=C0301

from WikiApiary.apiary.tasks import BaseApiaryTask
import requests
import logging
from WikiApiary.apiary.utils import ProcessMultiprops


LOGGER = logging.getLogger()

class RecordGeneralTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        data_url = api_url + '?action=query&meta=siteinfo&siprop=general&format=json'

        req = requests.get(data_url, timeout = 30)
        data = req.json()

        if req.status_code == 200:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/General" % sitename
                template_block = self.generate_template(site_id, data['query']['general'])
                c = self.bumble_bee.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.bumble_bee_token, 'bot': 'true'})
                LOGGER.debug(c)
                # Update the status table that we did our work! It doesn't matter if this was an error.
                self.update_status(site_id, 'general')
                return True
            else:
                self.record_error(
                    site=sitename,
                    log_message='Returned unexpected JSON when general info.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
        return False

    def generate_template(self, site_id, data):
        """Build a the wikitext for the general subpage."""

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
        for key in data:
            # Make sure we aren't ignoring this key
            if key not in ignore_keys:
                # If we have a name for this key use that
                name = key_names.get(key, key)
                value = data[key]

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
                    value = ProcessMultiprops(site_id, key, value)

                template_block += "|%s=%s\n" % (name, value)

        template_block += "}}\n</includeonly>\n"

        return template_block
