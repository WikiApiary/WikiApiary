"""
Find websites to audit and then launch audit tasks.
"""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging
from apiary.tasks.bot.audit import Audit


LOGGER = logging.getLogger()

class AuditWebsites(BaseApiaryTask):
    """Get websites that need an audit and then launch audit tasks."""

    def fire_audit_list(self, concept, count=20):
        """Get the list of sites from the segment and fire tasks."""

        my_query = ''.join([
            "[[Concept:%s]]" % concept,
            '|?Has ID',
            '|?Has API URL',
            '|sort=Has ID',
            '|order=asc',
            "|limit=%d" % count])

        LOGGER.debug("Query: %s" % my_query)

        sites = self.audit_bee.call({
            'action': 'ask',
            'query': my_query
        })

        for pagename, site in sites['query']['results'].items():
            LOGGER.info("Auditing %s." % pagename)

            site_id = int(site['printouts']['Page ID'][0])

            try:
                api_url = site['printouts']['Has API URL'][0]
            except Exception, e:
                api_url = None

            if api_url is not None:
                Audit.delay(site_id, pagename, api_url)

    def run(self):
        """Run the task."""
        self.fire_audit_list(concept='Websites never audited')
        self.fire_audit_list(concept='Websites expired audit')
