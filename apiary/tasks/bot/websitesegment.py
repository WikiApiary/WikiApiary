"""Process a website segment."""
# pylint: disable=C0301,C0103,W1201

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging


LOGGER = logging.getLogger()

class ProcessWebsiteSegment(BaseApiaryTask):

    def run(self, segment):
        LOGGER.info("Processing segment %d" % segment)
        my_query = ''.join([
            '[[Category:Website]]',
            '[[Is defunct::False]]',
            '[[Is active::True]]',
            "[[Has bot segment::%d]]" % segment,
            '|?Has API URL',
            '|?Has statistics URL',
            '|?Check every',
            '|?Creation date',
            '|?Has ID',
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

        # We could just return the raw JSON object from the API, however instead we are going to clean it up into an
        # easier to deal with array of dictionary objects.
        # To keep things sensible, we'll use the same name as the properties
        i = 0
        if len(sites['query']['results']) > 0:
            for pagename, site in sites['query']['results'].items():
                i += 1
                LOGGER.info("Processing %s" % pagename)

                site_id = int(site['printouts']['Has ID'][0])
                try:
                    stats_url = site['printouts']['Has statistics URL'][0]
                except Exception, e:
                    stats_url = None

                try:
                    api_url = site['printouts']['Has API URL'][0]
                except Exception, e:
                    api_url = None


                # Initialize the flags but do it carefully in case there is no value in the wiki yet
                try:
                    if (site['printouts']['Collect general data'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect extension data'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect skin data'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect statistics'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect semantic statistics'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect statistics stats'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect logs'][0] == "t"):
                        pass
                except Exception, e:
                    pass

                try:
                    if (site['printouts']['Collect recent changes'][0] == "t"):
                        pass
                except Exception, e:
                    pass

            return i
