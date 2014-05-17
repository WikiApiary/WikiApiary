"""
baseclass for tasks
"""
# pylint: disable=C0301

from celery.task import Task
from WikiApiary.apiary.connect import bumble_bee, bumble_bee_token, audit_bee, audit_bee_token, apiary_db, redis_db
from WikiApiary.celery import app
import logging
import datetime
import pytz


LOGGER = logging.getLogger()

class BaseApiaryTask(Task):
    bumble_bee = None
    bumble_bee_token = None
    audit_bee = None
    audit_bee_token = None
    apiary_db = None
    redis_db = None

    def update_status(self, site, checktype):
        """Update the website_status table"""
        my_now = self.sqlutcnow()

        if checktype == "statistics":
            temp_sql = "UPDATE website_status SET last_statistics = '%s' WHERE website_id = %d" % (my_now, site)

        if checktype == "general":
            temp_sql = "UPDATE website_status SET last_general = '%s' WHERE website_id = %d" % (my_now, site)

        (success, rows_affected) = self.runSql(temp_sql)

        if rows_affected == 0:
            # No rows were updated, this website likely didn't exist before, so we need to insert the first time
            print "No website_status record exists for ID %d, creating one" % site
            temp_sql = "INSERT website_status (website_id, last_statistics, last_general, check_every_limit) "
            temp_sql += "VALUES (%d, \"%s\", \"%s\", %d)" % (site, my_now, my_now, 240)
            self.runSql(temp_sql)

    def runSql(self, sql_command):
        """Helper to run a SQL command and catch errors"""
        print "SQL: %s" % sql_command
        try:
            cur = self.apiary_db.cursor()
            cur.execute(sql_command)
            cur.close()
            self.apiary_db.commit()
            return True, cur.rowcount
        except Exception, e:
            print "Exception generated while running SQL command."
            print "Command: %s" % sql_command
            print "Exception: %s" % e
            return False, 0

    def record_error(self, site, log_message, log_type='info', log_severity='normal', log_bot=None, log_url=None):
        """
        If a task encounters an error while collecting from a website it can record that
        error into the ApiaryDB so it is then displayed to the users on WikiApiary. This
        allows people that are not administrators on the machines running the bots to
        correct collection errors.
        """
        if 'pagename' not in site:
            if 'Has name' in site:
                site['pagename'] = site['Has name']

        LOGGER.debug("New log message for %s" % site['pagename'])

        LOGGER.debug(log_message)

        if log_bot is None:
            log_bot = "null"
        else:
            log_bot = "'%s'" % log_bot

        if log_url is None:
            log_url = "null"
        else:
            log_url = "'%s'" % log_url

        temp_sql = "INSERT  apiary_website_logs (website_id, log_date, website_name, log_type, log_severity, log_message, log_bot, log_url) "
        temp_sql += "VALUES (%d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s, %s)" % (
            site['Has ID'],
            self.sqlutcnow(),
            site['pagename'],
            log_type,
            log_severity,
            log_message,
            log_bot,
            log_url
        )

        self.runSql(temp_sql)

    def sqlutcnow(self):
        """Returns the UTC time in format SQL likes."""
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        now = now.replace(microsecond=0)
        return now.strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.bumble_bee = bumble_bee
        self.bumble_bee_token = bumble_bee_token
        self.audit_bee = audit_bee
        self.audit_bee_token = audit_bee_token
        self.apiary_db = apiary_db
        self.redis_db = redis_db
