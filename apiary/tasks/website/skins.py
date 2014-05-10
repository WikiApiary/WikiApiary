from WikiApiary.apiary.tasks import BaseApiaryTask
import requests
import logging
import urlparse


LOGGER = logging.getLogger()

class RecordSkinsTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        """Pull skin data from website and write to WikiApiary."""
        data_url = api_url + '?action=query&meta=siteinfo&siprop=skins&format=json'

        req = requests.get(data_url, timeout = 30)
        data = req.json()

        if req.status_code == 200:
            # Successfully pulled data
            if 'query' in data:
                datapage = "%s/Skins" % sitename
                template_block = generate_template(data['query']['skins'])
                c = self.bumble_bee.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.bumble_bee_token, 'bot': 'true'})
                LOGGER.debug(c)
                return True
            else:
                self.record_error(
                    site=sitename,
                    log_message='Returned unexpected JSON when requesting skin data.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
        return False

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

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

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
                            value = filter_illegal_chars(value)

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