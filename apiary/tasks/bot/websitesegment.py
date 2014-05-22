"""Process a website segment."""
# pylint: disable=C0301,C0103,W1201

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging
import datetime
from WikiApiary.apiary.tasks.website.extensions import RecordExtensionsTask
from WikiApiary.apiary.tasks.website.general import RecordGeneralTask
from WikiApiary.apiary.tasks.website.interwikimap import RecordInterwikimapTask
from WikiApiary.apiary.tasks.website.maxmind import MaxmindTask
from WikiApiary.apiary.tasks.website.namespaces import RecordNamespacesTask
from WikiApiary.apiary.tasks.website.skins import RecordSkinsTask
from WikiApiary.apiary.tasks.website.smwinfo import GetSMWInfoTask
from WikiApiary.apiary.tasks.website.whoislookup import RecordWhoisTask
from WikiApiary.apiary.tasks.website.statistics import GetStatisticsTask


LOGGER = logging.getLogger()

class ProcessWebsiteSegment(BaseApiaryTask):
    """Bot function to retrieve a segment and issue the tasks."""

    def check_timer(self, site_id, token, expire_timer):
        """Determine if this task should be run again."""

        my_token = "wikiapiary_%d_%s" % (site_id, token)
        LOGGER.debug("Checking cache token %s" % my_token)

        current_time = int(datetime.datetime.now().strftime("%s"))
        try:
            stored_time = int(self.redis_db.get(my_token))
        except:
            stored_time = 0
        LOGGER.debug("Stored time for %s of %d" % (my_token, stored_time))

        time_since = current_time - stored_time
        if time_since > expire_timer:
            # Update the timer regardless of success
            self.redis_db.set(
                my_token,
                int(datetime.datetime.now().strftime("%s")),
                60*60*24*7    # Expire these tokens after 1 week
            )
            LOGGER.debug("check_timer %d %s is %d old, check it." % (site_id, token, time_since))
            return True
        else:
            LOGGER.debug("check_timer %d %s is %d old, skip." % (site_id, token, time_since))
            return False


    def run(self, segment):
        """Run a segment for processing."""
        LOGGER.info("Processing segment %d" % segment)

        # TODO: It is very expensive to get the segment everytime. It would be better
        # to cache the segment in redis and just check the most recent "Modification date"
        # from the wiki. If that date hasn't changed, use the cached version from redis.

        my_query = ''.join([
            '[[Category:Website]]',
            '[[Is defunct::False]]',
            '[[Is active::True]]',
            "[[Has bot segment::%d]]" % segment,
            '|?Has API URL',
            '|?Has statistics URL',
            '|?Check every',
            '|?Creation date',
            '|?Page ID',
            '|?Collect general data',
            '|?Collect extension data',
            '|?Collect skin data',
            '|?Collect statistics',
            '|?Collect semantic statistics',
            '|?Collect logs',
            '|?Collect recent changes',
            '|?Collect statistics stats',
            '|sort=Creation date',
            '|order=asc',
            '|limit=1000'])
        
        LOGGER.debug("Query: %s" % my_query)

        sites = self.bumble_bee.call({
            'action': 'ask',
            'query': my_query
        })

        i = 0
        if len(sites['query']['results']) > 0:
            for pagename, site in sites['query']['results'].items():
                i += 1
                LOGGER.info("Processing %s" % pagename)

                site_id = int(site['printouts']['Page ID'][0])
                try:
                    stats_url = site['printouts']['Has statistics URL'][0]
                except Exception, e:
                    stats_url = None

                try:
                    api_url = site['printouts']['Has API URL'][0]
                except Exception, e:
                    api_url = None

                try:
                    check_every = int(site['printouts']['Check every'][0])
                except Exception, e:
                    check_every = 60*60*4

                # Get the statistical data
                try:
                    if (site['printouts']['Collect semantic statistics'][0] == "t") and \
                    self.check_timer(site_id, 'smwinfo', check_every):
                        GetSMWInfoTask.delay(site_id, pagename, api_url)
                except Exception, e:
                    LOGGER.warn(e)

                try:
                    if (site['printouts']['Collect statistics'][0] == "t") and \
                    self.check_timer(site_id, 'statistics', check_every):
                        GetStatisticsTask.delay(site_id, pagename, 'API', api_url, self.__has_stats_url)
                except Exception, e:
                    LOGGER.warn(e)


                try:
                    if (site['printouts']['Collect statistics stats'][0] == "t") and \
                    self.check_timer(site_id, 'statistics', check_every):
                        GetStatisticsTask.delay(site_id, pagename, 'Statistics', api_url, stats_url)
                except Exception, e:
                    LOGGER.warn(e)

                # Get the metadata
                try:
                    if (site['printouts']['Collect general data'][0] == "t") and \
                    self.check_timer(site_id, 'general', 24*60*60):
                        RecordGeneralTask.delay(site_id, pagename, api_url)
                        # TODO: Interwikimap and Namespaces should be moved to their own sections
                        # (see below) but the wiki needs to have fields added for those.
                        RecordInterwikimapTask.delay(site_id, pagename, api_url)
                        RecordNamespacesTask.delay(site_id, pagename, api_url)
                        RecordWhoisTask.delay(site_id, pagename, api_url)
                        MaxmindTask.delay(site_id, pagename, api_url)
                except Exception, e:
                    LOGGER.warn(e)

                try:
                    if (site['printouts']['Collect extension data'][0] == "t") and \
                    self.check_timer(site_id, 'extension', 24*60*60):
                        RecordExtensionsTask.delay(site_id, pagename, api_url)
                except Exception, e:
                    LOGGER.warn(e)

                try:
                    if (site['printouts']['Collect skin data'][0] == "t") and \
                    self.check_timer(site_id, 'skin', 3*24*60*60):
                        RecordSkinsTask.delay(site_id, pagename, api_url)
                except Exception, e:
                    LOGGER.warn(e)

                # try:
                #     if (site['printouts']['Collect interwikimap'][0] == "t") and \
                #     self.check_timer(site_id, 'interwikimap', 5*24*60*60):
                #         my_website.record_interwikimap()
                # except Exception, e:
                #     LOGGER.warn(e)

                # try:
                #     if (site['printouts']['Collect namespaces'][0] == "t") and \
                #     self.check_timer(site_id, 'namespaces', 5*24*60*60):
                #         my_website.record_namespaces()
                # except Exception, e:
                #     LOGGER.warn(e)

                # try:
                #     if (site['printouts']['Collect logs'][0] == "t") and \
                #     self.check_timer(site_id, 'general', 24*60*60):
                #         self.check_timer(site_id, 'logs', 60*60)
                # except Exception, e:
                #     pass

                # try:
                #     if (site['printouts']['Collect recent changes'][0] == "t") and \
                #     self.check_timer(site_id, 'general', 24*60*60):
                #         self.check_timer(site_id, 'recentchanges', 60*60)
                # except Exception, e:
                #     pass

            return i
