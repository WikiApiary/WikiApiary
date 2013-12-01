#!/usr/bin/python
"""
Notify Bee

This bot sends emails to users who have requested them.

"""

import sys
import time
import datetime
import pytz
import ConfigParser
import socket
import MySQLdb as mdb
import simplejson
import urllib2
from simplemediawiki import MediaWiki
from apiary import bot


class NotifyBee(Bot):
    def __init__(self):
        Bot.__init__(self)
        # Initialize stats
        self.stats['notify_count'] = 0
        self.stats['notify_admin_count'] = 0
        self.stats['notify_weekly_report'] = 0

    # Send an email to a MediaWiki user using the MediaWiki API.
    # This allows us to not worry about any of the email sending part
    # or even know the email address of the user.
    # The downside is it can only deal with plain text.
    def send_notification(self, user, subject, message):
        if self.args.verbose >= 3:
            print "Notifying %s" % user

        c = self.apiary_wiki.call({
            'action': 'emailuser',
            # 'target': user,
            'target': 'Thingles',
            'subject': subject,
            'text': message,
            'token': self.edit_token
        })
        if self.args.verbose >= 3:
            print c

    def get_notify_list(self, site):
        my_query = ''.join([
            "[[Has notification user::+]]",
            "[[Has website::%s]]" % site[0],
            "|?Has notification user",
            "|?Has notification admin",
            "|?Has notification weekly report"
            "|limit=500"])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(sites['query']['results']) > 0:
            return len(sites['query']['results']), sites['query']['results'].items()
        else:
            return 0, None

    def notify_site(self, site):
        if self.args.verbose >= 3:
            print "\n\nSite: ", site

        site_id = site[1]['printouts']['Has ID'][0]
        (notification_count, notifications) = self.get_notify_list(site)

        if notification_count > 0:
            if self.args.verbose >= 2:
                print "Sending %d notification." % notification_count
            for notification in notifications:
                if self.args.verbose >= 3:
                    print "Notification: ", notification

                notify_user = notification[1]['printouts']['Has notification user'][0]['fulltext']
                notify_admin = (notification[1]['printouts']['Has notification admin'][0] == 't')
                notify_report = (notification[1]['printouts']['Has notification weekly report'][0] == 't')

                if notify_admin:
                    self.stats['notify_admin_count'] += 1
                    subject = "WikiApiary Administrator Notification for %s" % site[0]
                    message = "This is the body"
                elif notify_report:
                    self.stats['notify_weekly_report'] += 1
                    subject = "WikiApiary Weekly Report for %s" % site[0]
                    message = "This is the body"

                self.send_notification(notify_user, subject, message)

    def get_notify_sites(self):
        my_query = ''.join([
            "[[Has day segment::%s]]" % time.strftime('%w', time.gmtime()),
            "[[Is active::True]]",
            "[[Is defunct::False]]",
            "[[Has notification count::>>0]]",
            "|?Has ID",
            '|?Has API URL',
            '|sort=Creation date',
            "|limit=500"])

        if self.args.verbose >= 3:
            print "Query: %s" % my_query

        socket.setdefaulttimeout(30)
        sites = self.apiary_wiki.call({'action': 'ask', 'query': my_query})

        if len(sites['query']['results']) > 0:
            return len(sites['query']['results']), sites['query']['results'].items()
        else:
            return 0, None

    def main(self):
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Notify Bee')

        # Get list of sites to send notifications for
        (site_count, sites) = self.get_notify_sites()
        if site_count > 0:
            message = "Sending notifations for %d sites." % site_count
            self.botlog(bot='Notify Bee', message=message)
            for site in sites:
                self.stats['notify_count'] += 1
                self.notify_site(site)

        duration = time.time() - start_time
        if self.stats['notify_count'] > 0:
            message = "Completed %d notifications %d admin %d reports." % (
                self.stats['notify_count'],
                self.stats['notify_admin_count'],
                self.stats['notify_weekly_report'])
            if self.args.verbose >= 1:
                print message
            self.botlog(bot='Notify Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = NotifyBee()
    bee.main()
