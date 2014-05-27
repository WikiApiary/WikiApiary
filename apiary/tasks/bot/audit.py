"""
Audit a specific website
"""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging
import re
import time
import dateutil

LOGGER = logging.getLogger()

class Audit(BaseApiaryTask):
    """Audit a specific website."""

    def update_audit_status(self, sitename):
        """Helper function to update audit status."""

        LOGGER.info("%s audit completed, updating audit date." % sitename)

        wiki_return = self.audit_bee.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': sitename,
            'Website[Audited]': 'Yes',
            'Website[Audited date]': time.strftime('%Y/%m/%d %I:%M:%S %p', time.gmtime()),
            'wpSummary': 'audited'})
        LOGGER.debug(wiki_return)

    def set_flag(self, sitename, name, value, comment):
        """Helper function to set a flag quickly for a website."""

        LOGGER.debug("%s setting %s to %s (%s)." % (sitename, name, value, comment))

        property_name = "Website[%s]" % name
        wiki_return = self.audit_bee.call({
            'action': 'sfautoedit',
            'form': 'Website',
            'target': sitename,
            property_name: value,
            'wpSummary': comment})
        LOGGER.debug(wiki_return)

    def set_audit_extensions(self, site, extensions):
        """Set optional flags based on extensions installed."""

        for extension in extensions:
            # Semantic statistics requires Semantic MediaWiki 1.6 or later.
            if extension.get('name', "") == 'Semantic MediaWiki':
                match = re.search(r'(\d+)\.(\d+)', extension['version'])
                (smw_version_major, smw_version_minor) = (int(match.group(1)), int(match.group(2)))

                if (smw_version_major >= 1) and (smw_version_minor >= 6) and (site['Collect semantic statistics'] is False):
                    self.set_flag(site['pagename'], 'Collect semantic statistics', 'Yes', "Enabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))
                if (smw_version_major >= 1) and (smw_version_minor < 6) and (site['Collect semantic statistics'] is True):
                    self.set_flag(site['pagename'], 'Collect semantic statistics', 'Yes', "Disabling statistics collection for Semantic MediaWiki %d.%d." % (smw_version_major, smw_version_minor))

    def set_audit(self, site_id, sitename, data):
        """Get the major and minor version numbers of MediaWiki"""

        match = re.search(r'\s(\d+)\.(\d+)', data['generator'])
        if match != None:
            (mw_version_major, mw_version_minor) = (int(match.group(1)), int(match.group(2)))

            LOGGER.info(
                "Website: %s  Generator: %s  Major: %d  Minor: %d" %
                (sitename, data['generator'], mw_version_major, mw_version_minor)
            )

            # General data requires MediaWiki 1.8 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 8) and (site['Collect general data'] is False):
                self.set_flag(sitename, 'Collect general data', 'Yes', "MediaWiki %d.%d supports general collection" % (mw_version_major, mw_version_minor))

            # Extension data requires MediaWiki 1.14 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 14) and (site['Collect extension data'] is False):
                self.set_flag(sitename, 'Collect extension data', 'Yes', "Enabling extension collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 14) and (site['Collect extension data'] is True):
                self.set_flag(sitename, 'Collect extension data', 'No', "Disabling extensions collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # Skin data requires MediaWiki 1.18 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 18) and (site['Collect skin data'] is False):
                self.set_flag(sitename, 'Collect skin data', 'Yes', "Enabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 18) and (site['Collect skin data'] is True):
                self.set_flag(sitename, 'Collect skin data', 'No', "Disabling skin collection for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # General statistics requires MediaWiki 1.11 or later.
            if (mw_version_major >= 1) and (mw_version_minor >= 11) and (site['Collect statistics'] is False):
                self.set_flag(sitename, 'Collect statistics', 'Yes', "Enabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))
            if (mw_version_major >= 1) and (mw_version_minor < 11) and (site['Collect statistics'] is True):
                self.set_flag(sitename, 'Collect statistics', 'No', "Disabling statistics for MediaWiki %d.%d." % (mw_version_major, mw_version_minor))

            # Return if extension data is available to check as well
            if (mw_version_major >= 1) and (mw_version_minor >= 14):
                return True
            else:
                return False

        else:
            # Unable to determine the version of MediaWiki. This is probably because the
            # wiki has been altered to hide its version.
            LOGGER.info("%s returnd version %s which cannot be parsed." % (sitename, data['generator']))
            self.record_error(
                site_id=site_id,
                sitename=sitename,
                log_message="Unable to determine version from %s. Auditing without confirming any flags. Operator please check." % data['generator'],
                log_type='info',
                log_severity='normal',
                log_bot='Audit Bee'
            )
            return False

    def run(self, site_id, sitename, api_url):
        """Conduct audit of a specific website."""

        # my_query = ''.join([
        #     "[[Concept:%s]]" % concept,
        #     '|?Has ID',
        #     '|?Has API URL',
        #     '|?Check every',
        #     '|?Collect general data',
        #     '|?Collect extension data',
        #     '|?Collect skin data',
        #     '|?Collect statistics',
        #     '|?Collect semantic statistics',
        #     '|?Collect statistics stats',
        #     '|?Collect logs',
        #     '|?Collect recent changes',
        #     '|?Creation date',
        #     '|?Is audited',
        #     '|?Is active',
        #     '|sort=Creation date',
        #     '|order=rand',
        #     "|limit=%d" % count])


        LOGGER.info("Auditing: %s", sitename)

        data_url = api_url + "?action=query&meta=siteinfo&siprop=general&format=json"
        LOGGER.debug ("Pulling general info info from %s." % data_url)
        (success, data, duration) = self.pull_json(site, data_url, bot='Audit Bee')

        audit_complete = False
        audit_extensions_complete = False
        do_audit_extensions = False

        if success:
            if 'query' in data:
                do_audit_extensions = self.set_audit(site_id, sitename, data['query']['general'])
                audit_complete = True
            elif 'error' in data:
                if 'code' in data['error']:
                    if data['error']['code'] == 'readapidenied':
                        # This website will not let us talk to it, defunct it.
                        self.set_flag(sitename, 'Defunct', 'Yes', 'Marking defunct because readapidenied')
                        self.record_error(
                            site_id=site_id,
                            sitename=sitename,
                            log_message="readapidenied, marking defunct",
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=data_url
                        )
                    else:
                        self.record_error(
                            site_id=site_id,
                            sitename=sitename,
                            log_message="Returned error %s" % data['error']['code'],
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=data_url
                        )
                else:
                    self.record_error(
                        site_id=site_id,
                        sitename=sitename,
                        log_message="An unknown error was returned from site info",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=data_url
                    )
            else:
                self.record_error(
                    site_id=site_id,
                    sitename=sitename,
                    log_message="Returned unexpected JSON while requesting general site info",
                    log_type='warn',
                    log_severity='important',
                    log_bot='Audit Bee',
                    log_url=data_url
                )

        # Pull extension information for audit too!
        if do_audit_extensions:
            data_url = api_url + "?action=query&meta=siteinfo&siprop=extensions&format=json"
            LOGGER.info("Pulling extension info info from %s." % data_url)
            (success, data, duration) = self.pull_json(sitename, data_url, bot='Audit Bee')

            if success:
                if 'query' in data:
                    self.set_audit_extensions(sitename, data['query']['extensions'])
                    audit_extensions_complete = True
                else:
                    self.record_error(
                        site_id=site_id,
                        sitename=sitename,
                        log_message="Returned unexpected JSON while requesting extensions",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=data_url
                    )

        if (audit_complete):
            # Let's see if we need to update the Founded date
            my_query = ''.join([
                "[[%s]]" % sitename,
                '|?Founded date'
            ])

            LOGGER.debug ("Query: %s" % my_query)

            check_date = self.apiary_wiki.call({
                'action': 'ask',
                'query': my_query
            })

            LOGGER.debug ("Response: %s" % check_date)

            if len(check_date['query']['results'][sitename]['printouts']['Founded date']) > 0:
                update_founded_date = False
            else:
                update_founded_date = True

            if (update_founded_date):
                # ?action=query&prop=revisions&revids=1&rvprop=timestamp&format=json
                first_date_url = api_url + "?action=query&prop=revisions&revids=1&rvprop=timestamp&format=json"
                (success, first_change, duration) = self.pull_json(sitename, first_date_url, bot='Audit Bee')
                if success:
                    try:
                        timestamp = first_change['query']['pages']['1']['revisions'][0]['timestamp']
                        # timestamp is ISO 8601 format
                        first_edit = dateutil.parser.parse(timestamp)
                        self.set_flag(sitename, 'Founded date', first_edit.strftime('%Y/%m/%d %I:%M:%S %p'), 'Setting founded date to timestamp of first edit')
                    except Exception, e:
                        self.record_error(
                            site_id=site_id,
                            sitename=sitename,
                            log_message="Failed to get timestamp of first revision to wiki.",
                            log_type='warn',
                            log_severity='important',
                            log_bot='Audit Bee',
                            log_url=first_date_url
                        )
                else:
                    self.record_error(
                        site_id=site_id,
                        sitename=sitename,
                        log_message="Failed to get timestamp for first edit.",
                        log_type='warn',
                        log_severity='important',
                        log_bot='Audit Bee',
                        log_url=first_date_url
                    )
            else:
                LOGGER.info("Date founded is already set, not checking.")

        if (audit_complete) and (do_audit_extensions == audit_extensions_complete):
            # Activate the site, but only if the site has not been audited before
            # if this is a re-audit, leave these flags alone.
            if not site['Is audited']:
                if not site['Is active']:
                    if self.args.verbose >= 2:
                        LOGGER.info("Activating %s." % sitename)
                    self.set_flag(sitename, 'Active', 'Yes', "Activated.")

        # Update audit status, wether success or failure
        self.update_audit_status(sitename)
