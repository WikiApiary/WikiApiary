"""Connect to ApiaryDB database."""
# pylint: disable=C0301,C0103,W1201

import ConfigParser
import os
import MySQLdb as mdb
import logging


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
    LOGGER.info("Detected configuration at %s", APIARY_CONFIG)
    config = ConfigParser.SafeConfigParser()
    config.read(APIARY_CONFIG)
    APIARYDB_USERNAME = config.get('ApiaryDB', 'username')
    APIARYDB_PASSWORD = config.get('ApiaryDB', 'password')
else:
    LOGGER.info("No configuration file detected.")



class ApiaryDB(object):

    def __init__(self, host, database, username, password):
        self.host = host
        self.database = database
        self.username = username
        self.password = password
        self.reconnect()

    def reconnect(self):
        LOGGER.info("Opening MySQL connection")
        self.apiary_db = mdb.connect(
            host=self.host,
            db=self.database,
            user=self.username,
            passwd=self.password,
            charset='utf8')

    def fetch_one(self, sql, retry_count=0):
        LOGGER.debug("SQL: %s", sql)
        try:
            cur = self.apiary_db.cursor()
            cur.execute(sql)
            return cur.fetchone()
        except mdb.OperationalError:
            if retry_count > 10: # seemed like a good count
                raise Exception("max retries...")
            self.reconnect()
            retry_count += 1
            return self.fetch_one(sql, retry_count)
        except Exception, e:
            cur.close()
            LOGGER.error("SQL Command: %s" % sql)
            raise Exception(e)

    def fetchall(self, sql, retry_count=0):
        LOGGER.debug("SQL: %s", sql)
        try:
            cur = self.apiary_db.cursor()
            cur.execute(sql)
            return cur.fetchall()
        except mdb.OperationalError:
            if retry_count > 10: # seemed like a good count
                raise Exception("max retries...")
            self.reconnect()
            retry_count += 1
            return self.fetch_one(sql, retry_count)
        except Exception, e:
            cur.close()
            LOGGER.error("SQL Command: %s" % sql)
            raise Exception(e)

    def runSql(self, sql_command, retry_count=0):
        """Helper to run a SQL command and catch errors"""
        LOGGER.debug("SQL: %s", sql_command)
        try:
            cur = self.apiary_db.cursor()
            cur.execute(sql_command)
            cur.close()
            self.apiary_db.commit()
            return True, cur.rowcount
        except mdb.OperationalError:
            if retry_count > 10: # seemed like a good count
                raise Exception("max retries...")
            self.reconnect()
            retry_count += 1
            return self.runSql(sql_command, retry_count)
        except Exception, e:
            cur.close()
            LOGGER.error("SQL Command: %s", sql_command)
            raise Exception(e)

apiary_db = ApiaryDB(APIARYDB_HOSTNAME, APIARYDB_DATABASE, APIARYDB_USERNAME, APIARYDB_PASSWORD)

