"""Connect to WikiApiary."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
from simplemediawiki import MediaWiki
import os
import logging


LOGGER = logging.getLogger()

# Set default connection details for localhost dev
APIARY_URL = 'https://wikiapiary.com/w/api.php'
MEDIAWIKI_URL = 'https://www.mediawiki.org/w/api.php'

APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')

if os.path.isfile(APIARY_CONFIG):
    LOGGER.info("Detected configuration at %s", APIARY_CONFIG)
    config = ConfigParser.SafeConfigParser()
    config.read(APIARY_CONFIG)
else:
    LOGGER.warn("No configuration file detected.")

def open_connection(bot_name, env_name, api_url):
    """Open a connection to MediaWiki for a bot."""

    LOGGER.info("Opening MediaWiki connection for %s at %s", bot_name, api_url)
    apiary_wiki = MediaWiki(api_url)
    edit_token = None

    try:
        # Passwords may be defined in the environment or in the config file
        # We prefer the environment variable if it is present
        password = os.environ.get(env_name, None)
        if password is None:
            try:
                config.get('Passwords', bot_name)
            except Exception as e:
                LOGGER.warn('No configuration file detected.')

        if password is not None:
            LOGGER.info("Logging in as %s using %s", bot_name, password)
            apiary_wiki.login(bot_name, password)

            LOGGER.info("Getting edit token for %s", bot_name)
            wiki_return = apiary_wiki.call({
                'action': 'tokens',
                'type': 'edit'
            })
            edit_token = wiki_return['tokens']['edittoken']
            LOGGER.info("%s has been given edit token %s", bot_name, edit_token)
        else:
            LOGGER.warn("No password was provided for %s. Queries allowed but editing will not work.", bot_name)

    except Exception as e:
        raise Exception("Unable to login as %s got '%s'", bot_name, e)

    return (apiary_wiki, edit_token)


LOGGER.info("Setting up Bumble Bee")
bumble_bee, bumble_bee_token = open_connection("Bumble Bee", "BUMBLEBEE", APIARY_URL)

LOGGER.info("Setting up Audit Bee")
audit_bee, audit_bee_token = open_connection("Audit Bee", "AUDITBEE", APIARY_URL)

LOGGER.info("Setting up MWorg Bee")
mworg_bee, mworg_bee_token = open_connection("WikiApiary", "MWORGBEE", MEDIAWIKI_URL)
