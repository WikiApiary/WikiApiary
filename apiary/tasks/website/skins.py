"""Get skin data."""
# pylint: disable=C0301,R0201

from apiary.tasks import BaseApiaryTask
import requests
import logging
import operator


LOGGER = logging.getLogger()

class RecordSkinsTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        """Pull skin data from website and write to WikiApiary."""
        LOGGER.info("Retrieve record_skins for %d" % site_id)

        data_url = api_url + '?action=query&meta=siteinfo&siprop=skins&format=json'

        try:
            req = requests.get(data_url, timeout = 15, verify=False)
            data = req.json()
        except Exception, e:
            LOGGER.error(e)
            raise(e)

        if req.status_code == 200:
            if 'query' in data:
                template_block = self.generate_template(data['query']['skins'])
                wiki_return = self.bumble_bee.call({
                    'action': 'edit',
                    'title': "%s/Skins" % sitename,
                    'text': template_block,
                    'token': self.bumble_bee_token,
                    'bot': 'true'})
                LOGGER.debug(wiki_return)
                if 'error' in wiki_return:
                    LOGGER.warn(wiki_return)
                    raise
                else:
                    return True
            else:
                self.record_error(
                    site_id=site_id,
                    sitename=sitename,
                    log_message='Returned unexpected JSON when requesting skin data.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                raise
        raise

    def generate_template(self, ext_obj):
        """Build a the wikitext for the skin subpage."""

        # Some keys we do not want to store in WikiApiary
        ignore_keys = []
        # Some keys we turn into more readable names for using inside of WikiApiary
        key_names = {
            '*': 'Skin name',
            'code': 'Skin code',
            'default': 'Default skin',
            'unusable': 'Skipped skin'
        }

        template_block = "<noinclude>{{Skins subpage}}</noinclude><includeonly>"

        # Skins are returned in random order so we need to sort them before
        # making the template, otherwise we generate a lot of edits
        # that are just different ordering
        skins_sorted = sorted(ext_obj, key=operator.itemgetter('*'))

        for skin in skins_sorted:
            if '*' in skin:
                # Start the template instance
                template_block += "{{Skin in use\n"
                for item in skin:
                    # Loop through all the items in the skin data and build the instance
                    if item not in ignore_keys:
                        name = key_names.get(item, item)
                        value = skin[item]

                        if item == '*':
                            value = self.filter_illegal_chars(value)

                        if item == 'default':
                            # This parameter won't appear unless it is true
                            value = True

                        if item == 'unusable':
                            # This paramter won't appear unless it is true
                            value = True

                        template_block += "|%s=%s\n" % (name, value)

                # Now end the template instance
                template_block += "}}\n"

        template_block += "</includeonly>"

        return template_block
