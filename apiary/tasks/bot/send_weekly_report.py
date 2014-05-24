"""Process a website segment."""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging


LOGGER = logging.getLogger()

class SendWeeklyReport(BaseApiaryTask):
    """Send the weekly report for a website to the users that have requested."""

    def send_notification(self, user, subject, message):
        """Send the actual notification via the MediaWiki API."""
        LOGGER.debug ("Notifying %s" % user)

        wiki_return = self.audit_bee.call({
            'action': 'emailuser',
            'target': user,
            'subject': subject,
            'text': message,
            'token': self.audit_bee_token
        })
        LOGGER.debug (wiki_return)

    def get_notify_list(self, sitename):
        """Return the list of users to send the weekly report to."""
        my_query = ''.join([
            "[[Has notification user::+]]",
            "[[Has notification weekly report::True]]"
            "[[Has website::%s]]" % sitename,
            "|?Has notification user",
            "|limit=1000"])

        LOGGER.debug ("Query: %s" % my_query)

        notifications = self.audit_bee.call({
            'action': 'ask',
            'query': my_query
        })
        LOGGER.debug(notifications)

        userlist = []
        for user in notifications['query']['results']:
            wikiuser = notifications['query']['results'][user]['printouts']['Has notification user'][0]['fulltext']
            username = wikiuser.split(':')[1]
            userlist.append(username)
        return userlist

    def generate_weekly_report(self, sitename):
        """Create the message body of the weekly report for a site."""

        my_query = ''.join([
            "[[%s]]" % sitename,
            "|?Has MediaWiki version",
            "|?Has active users count",
            "|?Has statistic active users change"
        ])

        wiki_return = self.audit_bee.call({
            'action': 'ask',
            'query': my_query
        })

        mediawiki_version = wiki_return['query']['results'][sitename]['printouts']['Has MediaWiki version'][0]

        message_template = """
MediaWiki version is %s.
"""

        return message_template % mediawiki_version

    def run(self, sitename):
        """Send weekly reports for a specific site."""
        LOGGER.info("Sending notifications for %s" % sitename)

        userlist = self.get_notify_list(sitename)

        message_body = self.generate_weekly_report(sitename)

        for username in userlist:
            LOGGER.info("Sending %s notification." % username)
            self.send_notification(username, "Weekly Report for %s" % sitename, message_body)


