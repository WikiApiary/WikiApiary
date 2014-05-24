"""
Update the tagline of WikiApiary with current data.
"""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging


LOGGER = logging.getLogger()

class UpdateTaglineTask(BaseApiaryTask):
    """Update the tagline of the site with current stats."""

    def run(self):
        """Run the task."""

        tagline_template = """{{#switch: {{NAMESPACENUMBER}}
| 0 = From WikiApiary, monitoring {{PAGENAME}} and over {{formatnum:%d}} other wikis
| 800 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other extensions
| 802 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other farms
| 804 = From WikiApiary, tracking {{PAGENAME}} and over {{formatnum:%d}} other skins
| From WikiApiary, monitoring the MediaWiki universe
}}
"""
        # TODO: This is not working and is just hardcoded
        # These should be queries to get the right values
        count_wiki = 19400
        count_extensions = 4600
        count_farms = 100
        count_skins = 1300

        tagline_page = tagline_template % (count_wiki, count_extensions, count_farms, count_skins)

        # Update MediaWiki:Tagline
        wikireturn = self.bumble_bee.call({
            'action': 'edit',
            'title': 'MediaWiki:Tagline',
            'text': tagline_page,
            'bot': True,
            'summary': 'Updating tagline with new values',
            'minor': True,
            'token': self.bumble_bee_token
        })
        LOGGER.debug(wikireturn)
