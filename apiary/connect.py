"""Connect to database and open connections to WikiApiary."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
from simplemediawiki import MediaWiki
import os
import MySQLdb as mdb
import logging


LOGGER = logging.getLogger()

APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')
config = ConfigParser.SafeConfigParser()

try:
    LOGGER.info("Reading configuration from %s" % APIARY_CONFIG)
    config.read(APIARY_CONFIG)
except IOError:
    print "Cannot open configuration file at %s." % APIARY_CONFIG
    raise

def open_connection(bot_name):
    """Open a connection to MediaWiki for a bot."""

    api_url = config.get('WikiApiary', 'API')
    username = config.get(bot_name, 'Username')
    password = config.get(bot_name, 'Password')

    LOGGER.info("Opening MediaWiki connection for %s at %s" % (bot_name, api_url))
    apiary_wiki = MediaWiki(api_url)
    LOGGER.debug("Logging in as %s with password %s" % (username, password))
    apiary_wiki.login(username, password)

    # Get the edit token for writes
    wiki_return = apiary_wiki.call({
        'action': 'tokens',
        'type': 'edit'
    })
    LOGGER.info(wiki_return)
    edit_token = wiki_return['tokens']['edittoken']

    # Perform a write to validate our connection to WikiApiary
    #c = apiary_wiki.call({'action': 'query', 'titles': 'Foo', 'prop': 'info', 'intoken': 'edit'})

    return (apiary_wiki, edit_token)

LOGGER.info("Setting up Bumble Bee")
bumble_bee, bumble_bee_token = open_connection("Bumble Bee")

LOGGER.info("Setting up Audit Bee")
audit_bee, audit_bee_token = open_connection("Audit Bee")

LOGGER.info("Opening MySQL connection")
apiary_db = mdb.connect(
    host=config.get('ApiaryDB', 'hostname'),
    db=config.get('ApiaryDB', 'database'),
    user=config.get('ApiaryDB', 'username'),
    passwd=config.get('ApiaryDB', 'password'),
    charset='utf8')
