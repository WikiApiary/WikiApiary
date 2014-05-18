"""Pull in whois information for sites."""
# pylint: disable=C0301

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging
import urlparse
import socket
import whois
from WikiApiary.apiary.utils import ProcessMultiprops


LOGGER = logging.getLogger()

class RecordWhoisTask(BaseApiaryTask):

    def run(self, site_id, sitename, api_url):
        # Now that we successfully got the data, we can make a quick query to get the server info
        hostname = urlparse.urlparse(api_url).hostname
        try:
            addr = socket.gethostbyname(hostname)
        except Exception, e:
            LOGGER.error(e)
            return False

        template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"
        template_block += "{{Whois\n"

        template_block += "|HTTP server=%s\n" % ('')
        try:
            template_block += "|IP address=%s\n" % (ProcessMultiprops(site_id, 'addr', addr))
        except Exception, e:
            pass

        try:
            reverse_host = socket.gethostbyaddr(addr)[0]
            template_block += "|Reverse lookup=%s\n" % (ProcessMultiprops(site_id, 'reverse_host', reverse_host))
        except Exception, e:
            pass

        # Now lets get the netblock information
        try:
            my_whois = whois.whois()
            netblock_owner = my_whois.getNetworkRegistrationRelatedToIP(addr, format='json')['net']['orgRef']['@name']
            netblock_owner_handle = my_whois.getNetworkRegistrationRelatedToIP(addr, format='json')['net']['orgRef']['@handle']
            template_block += "|Netblock organization=%s\n" % (netblock_owner)
            template_block += "|Netblock organization handle=%s\n" % netblock_owner_handle
        except Exception, e:
            pass

        template_block += "}}\n</includeonly>\n"

        wiki_return = self.bumble_bee.call({
            'action': 'edit',
            'title': "%s/Whois" % sitename,
            'text': template_block,
            'token': self.bumble_bee_token,
            'bot': 'true'
        })
        LOGGER.debug(wiki_return)
        if 'error' in wiki_return:
            LOGGER.warn(wiki_return)
            return False
        else:
            return True

        return True
