#!/usr/bin/python
"""
Bumble Bee is responsible for collecting statistics and other information from
sites registered on WikiApiary. See http://wikiapiary.com/wiki/User:Bumble_Bee
for more information.

Jamie Thingelstad <jamie@thingelstad.com>
http://wikiapiary.com/wiki/User:Thingles
http://thingelstad.com/
"""

from apiary import bot
from apiary import website


class BumbleBee(bot.Bot):
    """Bot that collects statistics for sites."""
    def __init__(self):
        super(BumbleBee, self).__init__()

    def main(self):
        if self.args.site is not None:
            message = "Starting processing for site %d." % int(self.args.site)
        elif self.args.segment is not None:
            message = "Starting processing for segement %d." % int(self.args.segment)
        else:
            message = "Starting processing for all websites."
        self.botlog(bot='Bumble Bee', message=message)

        # Record time at beginning
        start_time = time.time()

        # Setup our connection to the wiki too
        self.connectwiki('Bumble Bee')

        # Get list of websites to work on
        sites = self.get_websites(self.args.segment, self.args.site)

        i = 0
        for site in sites:
            i += 1
            if self.args.verbose >= 1:
                print "\n\n%d: Processing %s (ID %d)" % (i, site['pagename'], site['Has ID'])
            req_statistics = False
            req_general = False
            if self.args.force:
                (req_statistics, req_general) = (True, True)
            else:
                (req_statistics, req_general) = self.get_status(site)

            # Put this section in a try/catch so that we can proceed even if a single site causes a problem
            try:
                process = "unknown"
                if req_statistics:
                    if site['Collect statistics']:
                        process = "collect statistics (API)"
                        status = self.record_statistics(site, 'API')
                    if site['Collect statistics stats']:
                        process = "collect statistics (Statistics)"
                        status = self.record_statistics(site, 'Statistics')
                    if site['Collect semantic statistics']:
                        process = "collect semantic statistics"
                        status = self.record_smwinfo(site)
                    if site['Collect semantic usage']:
                        process = "collect semantic usage"
                        status = self.record_smwusage(site)
                if req_general:
                    time.sleep(2)  # TODO: this is dumb, doing to not trigger a problem with update_status again due to no rows being modified if the timestamp is the same. Forcing the timestamp to be +1 second
                    self.record_whois(site)
                    self.record_maxmind(site)
                    if site['Collect general data']:
                        process = "collect general data"
                        status = self.record_general(site)
                    if site['Collect extension data']:
                        process = "collect extension data"
                        status = self.record_extensions(site)
                    if site['Collect skin data']:
                        process = "collect skin data"
                        status = self.record_skins(site)
            except Exception, e:
                self.record_error(
                    site=site,
                    log_message='Unhandled exception %s during %s' % (str(e), process),
                    log_type='error',
                    log_severity='normal',
                    log_bot='Bumble Bee'
                )

        duration = time.time() - start_time
        if self.args.segment is not None:
            message = "Completed processing for segment %d." % int(self.args.segment)
        else:
            message = "Completed processing for all websites."
        message += " Processed %d websites." % i
        message += " Counters statistics %d smwinfo %d smwusage %d general %d extensions %d skins %d skipped_stats: %d skipped_general: %d whois: %d maxmind: %d" % (
            self.stats['statistics'], self.stats['smwinfo'], self.stats['smwusage'], self.stats['general'],
            self.stats['extensions'], self.stats['skins'], self.stats['skippedstatistics'], self.stats['skippedgeneral'],
            self.stats['whois'], self.stats['maxmind'])
        self.botlog(bot='Bumble Bee', duration=float(duration), message=message)


# Run
if __name__ == '__main__':
    bee = BumbleBee()
    bee.main()
