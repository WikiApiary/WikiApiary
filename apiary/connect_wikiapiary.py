"""Connect to WikiApiary."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
from simplemediawiki import MediaWiki
import os
import logging


LOGGER = logging.getLogger()

# Set default connection details for localhost dev
API_URL = 'https://wikiapiary.com/w/api.php'

APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')
if os.path.isfile(APIARY_CONFIG):
    LOGGER.info("Detected configuration at %s" % APIARY_CONFIG)
    config = ConfigParser.SafeConfigParser()
    config.read(APIARY_CONFIG)
else:
    LOGGER.warn("No configuration file detected.")

def open_connection(bot_name, env_name):
    """Open a connection to MediaWiki for a bot."""

    LOGGER.info("Opening MediaWiki connection for %s at %s" % (bot_name, API_URL))
    apiary_wiki = MediaWiki(API_URL)

    try:
        # Passwords may be defined in the environment or in the config file
        # We prefer the environment variable if it is present
        password = os.environ.get(env_name, config.get('Passwords', bot_name))
        LOGGER.debug("Logging in as %s using %s" % (bot_name, password))
        apiary_wiki.login(bot_name, password)

        wiki_return = apiary_wiki.call({
            'action': 'tokens',
            'type': 'edit'
        })
        edit_token = wiki_return['tokens']['edittoken']
        LOGGER.info("%s has been given edit token %s" % (bot_name, edit_token))

    except Exception, e:
        LOGGER.error("Unable to login as %s. Error: %s" % (bot_name, e))
        edit_token = None

    return (apiary_wiki, edit_token)

LOGGER.info("Setting up Bumble Bee")
bumble_bee, bumble_bee_token = open_connection("Bumble Bee", "BUMBLEBEE")

LOGGER.info("Setting up Audit Bee")
audit_bee, audit_bee_token = open_connection("Audit Bee", "AUDITBEE")

