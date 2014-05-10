"""Connect to database and open connections to WikiApiary."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
from simplemediawiki import MediaWiki
import os
import MySQLdb as mdb
import logging


LOGGER = logging.getLogger()

# Set default connection details for localhost dev
API_URL = 'https://wikiapiary.com/w/api.php'
APIARYDB_HOSTNAME = 'localhost'
APIARYDB_DATABASE = 'apiary'
APIARYDB_USERNAME = 'root'
APIARYDB_PASSWORD = ''

if os.environ.get("TRAVIS") == "true":
    LOGGER.info("Configuring for TravisCI")
    APIARYDB_USERNAME = 'travis'
    APIARYDB_PASSWORD = ''

APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'config/apiary.cfg')
if os.path.isfile(APIARY_CONFIG):
    LOGGER.info("Detected configuration at %s" % APIARY_CONFIG)
    config = ConfigParser.SafeConfigParser()
    config.read(APIARY_CONFIG)
    APIARYDB_USERNAME = config.get('ApiaryDB', 'username')
    APIARYDB_PASSWORD = config.get('ApiaryDB', 'password')
else:
    LOGGER.info("No configuration file detected.")

def open_connection(bot_name):
    """Open a connection to MediaWiki for a bot."""

    LOGGER.info("Opening MediaWiki connection for %s at %s" % (bot_name, API_URL))
    apiary_wiki = MediaWiki(API_URL)

    try:
        password = config.get('Passwords', bot_name)
        LOGGER.debug("Logging in as %s using %s" % (bot_name, password))
        apiary_wiki.login(bot_name, password)

        wiki_return = apiary_wiki.call({
            'action': 'tokens',
            'type': 'edit'
        })
        edit_token = wiki_return['tokens']['edittoken']
        LOGGER.info("%s has been given edit token %s" % (bot_name, edit_token))

    except:
        LOGGER.warn("Unable to login as %s. " % bot_name)
        edit_token = None

    return (apiary_wiki, edit_token)

LOGGER.info("Setting up Bumble Bee")
bumble_bee, bumble_bee_token = open_connection("Bumble Bee")

LOGGER.info("Setting up Audit Bee")
audit_bee, audit_bee_token = open_connection("Audit Bee")

LOGGER.info("Opening MySQL connection")
apiary_db = mdb.connect(
    host=APIARYDB_HOSTNAME,
    db=APIARYDB_DATABASE,
    user=APIARYDB_USERNAME,
    passwd=APIARYDB_PASSWORD,
    charset='utf8')
