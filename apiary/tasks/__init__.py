"""
baseclass for tasks
"""
# pylint: disable=C0301

from celery.task import Task
from apiary.connect import bumble_bee, bumble_bee_token, audit_bee, audit_bee_token, mworg_bee, mworg_bee_token, apiary_db, redis_db
from apiary.celery import app
import logging
import datetime
import pytz
import re

LOGGER = logging.getLogger()

class BaseApiaryTask(Task):
    bumble_bee = None
    bumble_bee_token = None
    audit_bee = None
    audit_bee_token = None
    mworg_bee = None
    mworg_bee_token = None
    apiary_db = None
    redis_db = None

    def filter_illegal_chars(self, pre_filter):
        """Utility function to make sure that strings are okay for page titles"""
        return re.sub(r'[#<>\[\]\|{}]', '', pre_filter).replace('=', '-')

    def sqlutcnow(self):
        """Returns the UTC time in format SQL likes."""
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        now = now.replace(microsecond=0)
        return now.strftime('%Y-%m-%d %H:%M:%S')

    def ProcessMultiprops(self, site_id, key, value):
        # Here we deal with properties that change frequently and we care about all of them.
        # For example, dbversion in a wiki farm will often have multiple values
        # and we will get different values each time, rotating between a set.
        # This function will take the value and return a more complex data structure.

        # First update the timestamp for seeing the current name/value
        temp_sql = "UPDATE apiary_multiprops SET last_date=\'%s\', occurrences = occurrences + 1 WHERE website_id = %d AND t_name = \'%s\' AND t_value = \'%s\'" % (
            self.sqlutcnow(),
            site_id,
            key,
            value)
        success, rows_returned = self.apiary_db.runSql(temp_sql)

        # No rows returned, we need to create this value
        if rows_returned == 0:
            temp_sql = "INSERT apiary_multiprops (website_id, t_name, t_value, first_date, last_date, occurrences) VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (
                site_id,
                key,
                value,
                self.sqlutcnow(),
                self.sqlutcnow(),
                1)
            self.apiary_db.runSql(temp_sql)

        # Now build the return value
        multivalue = ""
        temp_sql = "SELECT t_value, last_date, occurrences FROM apiary_multiprops WHERE website_id = %d AND last_date > \'%s\' AND t_name = \'%s\' ORDER BY occurrences DESC" % (
            site_id,
            '2013-04-26 18:23:01',
            key)
        rows = self.apiary_db.fetchall(temp_sql)
        for row in rows:
            if len(multivalue) > 0:
                multivalue += ","
            multivalue += "%s" % row[0]

        return multivalue

    def record_error(self, site_id, sitename, log_message, log_type='info', log_severity='normal', log_bot=None, log_url=None):
        """
        If a task encounters an error while collecting from a website it can record that
        error into the ApiaryDB so it is then displayed to the users on WikiApiary. This
        allows people that are not administrators on the machines running the bots to
        correct collection errors.
        """

        LOGGER.debug("New log message for %s" % sitename)

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
            site_id,
            self.sqlutcnow(),
            sitename,
            log_type,
            log_severity,
            log_message,
            log_bot,
            log_url
        )

        self.runSql(temp_sql)

    def __init__(self):
        self.bumble_bee = bumble_bee
        self.bumble_bee_token = bumble_bee_token
        self.audit_bee = audit_bee
        self.audit_bee_token = audit_bee_token
        self.mworg_bee = mworg_bee
        self.mworg_bee_token = mworg_bee_token
        self.apiary_db = apiary_db
        self.redis_db = redis_db
