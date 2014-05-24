"""Connect to ApiaryDB database."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
import os
import MySQLdb as mdb
import logging
import redis


LOGGER = logging.getLogger()

# Set default connection details for localhost dev
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

LOGGER.info("Opening MySQL connection")
apiary_db = mdb.connect(
    host=APIARYDB_HOSTNAME,
    db=APIARYDB_DATABASE,
    user=APIARYDB_USERNAME,
    passwd=APIARYDB_PASSWORD,
    charset='utf8')

