"""
Base class for WikiApiary websites.
"""
# pylint: disable=C0301

# Import the task classes associated with websites
from WikiApiary.apiary.tasks.website.extensions import RecordExtensionsTask
from WikiApiary.apiary.tasks.website.general import RecordGeneralTask
from WikiApiary.apiary.tasks.website.interwikimap import RecordInterwikimapTask
from WikiApiary.apiary.tasks.website.maxmind import MaxmindTask
from WikiApiary.apiary.tasks.website.namespaces import RecordNamespacesTask
from WikiApiary.apiary.tasks.website.skins import RecordSkinsTask
from WikiApiary.apiary.tasks.website.smwinfo import GetSMWInfoTask
from WikiApiary.apiary.tasks.website.whoislookup import RecordWhoisTask
from WikiApiary.apiary.tasks.website.statistics import GetStatisticsTask


class Website(object):
    """Class for websites in WikiApiary."""

    def __init__(self, website_id, website_name, api_url):
        """Initialize the instance."""
        self.__has_id = website_id
        self.__website_name = website_name
        self.__has_api_url = api_url

    def record_general(self):
        """Get general data."""
        RecordGeneralTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_extensions(self):
        """Get extension data."""
        RecordExtensionsTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_skins(self):
        """Get skin data."""
        RecordSkinsTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_interwikimap(self):
        """Get interwiki data."""
        RecordInterwikimapTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_namespaces(self):
        """Get namespace data."""
        RecordNamespacesTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_maxmind(self):
        """Get maxmind data."""
        MaxmindTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def record_whois(self):
        """Get whois data."""
        RecordWhoisTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def get_smwinfo(self):
        """Run SMWInfo Task."""
        GetSMWInfoTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

    def get_statistics(self):
        """Run the statistics task"""
        GetStatisticsTask.delay(self.__has_id, self.__website_name, self.__has_api_url)

