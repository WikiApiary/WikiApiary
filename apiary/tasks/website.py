from WikiApiary.apiary.tasks import BaseApiaryTask
import requests
from WikiApiary.apiary.utils import build_general_template, build_skins_template, build_extensions_template
from WikiApiary.apiary.utils import BuildMaxmindTemplate
import logging
import urlparse


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
                template_block = build_general_template(site_id, data['query']['general'])
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
                template_block = build_skins_template(data['query']['skins'])
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


class RecordExtentionsTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        """Get extensions from the website and write them to WikiApiary."""

        data_url = api_url + '?action=query&meta=siteinfo&siprop=extensions&format=json'

        req = requests.get(data_url, timeout = 30)
        data = req.json()

        if req.status_code == 200:
            # Successfully pulled data
            if 'query' in data:
                # Looks like a valid response
                datapage = "%s/Extensions" % sitename
                template_block = build_extensions_template(data['query']['extensions'])
                print template_block
                c = self.bumble_bee.call({
                    'action': 'edit',
                    'title': datapage,
                    'text': template_block,
                    'token': self.bumble_bee_token,
                    'bot': 'true'
                    })
                LOGGER.debug(c)
                return True
            else:
                self.record_error(
                    site=sitename,
                    log_message='Returned unexpected JSON when requesting extension data.',
                    log_type='warn',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
        return False


class MaxmindTask(BaseApiaryTask):
    def run(self, site_id, sitename, api_url):
        """Get MaxMind data for website and write to WikiApiary."""

        datapage = "%s/Maxmind" % sitename
        hostname = urlparse.urlparse(api_url).hostname
        template_block = BuildMaxmindTemplate(hostname)

        c = self.bumble_bee.call({'action': 'edit', 'title': datapage, 'text': template_block, 'token': self.bumble_bee_token, 'bot': 'true'})
        LOGGER.debug(c)
        return True

