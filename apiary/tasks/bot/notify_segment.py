"""Process a website for notifications."""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging
from apiary.tasks.bot.send_weekly_report import SendWeeklyReport
import datetime


LOGGER = logging.getLogger()

class NotifySegment(BaseApiaryTask):
    """Send notifications for a group of websites."""

    def get_notify_sites(self, curr_day = None, curr_hour = None):
        """Get the list of sites to send notifications for."""

        # Allow these to be passed in for testing
        if curr_day is None:
            curr_day = int(datetime.datetime.now().strftime("%w"))
        if curr_hour is None:
            curr_hour = int(datetime.datetime.now().strftime("%H"))

        my_query = ''.join([
            "[[Has day segment::%d]]" % curr_day,
            "[[Has hour segment::%d]]" % curr_hour,
            "[[Is active::True]]",
            "[[Is defunct::False]]",
            "[[Has notification count::>>0]]",
            "|sort=Creation date",
            "|limit=1000"])

        LOGGER.debug ("Query: %s" % my_query)

        sites = self.audit_bee.call({
            'action': 'ask',
            'query': my_query
        })

        sitelist = []
        if len(sites['query']['results']) > 0:
            for site in sites['query']['results'].items():
                sitelist.append(site['pagename'])

        return sitelist

    def run(self):
        """Trigger notifications for websites"""
        sitelist = self.get_notify_sites()

        for site in sitelist:
            LOGGER.info ("Sending notifations for %s." % site)
            SendWeeklyReport.delay(site)

