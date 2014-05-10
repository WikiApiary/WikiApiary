"""Utils for WikiApiary."""

# pylint: disable=C0301

import HTMLParser
import re
import pygeoip
import datetime
import operator
import pytz
from WikiApiary.apiary.connect import apiary_db

def filter_illegal_chars(pre_filter):
    """Utility function to make sure that strings are okay for page titles"""
    return re.sub(r'[#<>\[\]\|{}]', '', pre_filter).replace('=', '-')

def sqlutcnow():
    """Returns the UTC time in format SQL likes."""
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    now = now.replace(microsecond=0)
    return now.strftime('%Y-%m-%d %H:%M:%S')

def ProcessMultiprops(site_id, key, value):
    # Here we deal with properties that change frequently and we care about all of them.
    # For example, dbversion in a wiki farm will often have multiple values
    # and we will get different values each time, rotating between a set.
    # This function will take the value and return a more complex data structure.

    # First update the timestamp for seeing the current name/value
    cur = apiary_db.cursor()
    temp_sql = "UPDATE apiary_multiprops SET last_date=\'%s\', occurrences = occurrences + 1 WHERE website_id = %d AND t_name = \'%s\' AND t_value = \'%s\'" % (
        sqlutcnow(),
        site_id,
        key,
        value)
    cur.execute(temp_sql)
    rows_returned = cur.rowcount

    # No rows returned, we need to create this value
    if rows_returned == 0:
        temp_sql = "INSERT apiary_multiprops (website_id, t_name, t_value, first_date, last_date, occurrences) VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (
            site_id,
            key,
            value,
            sqlutcnow(),
            sqlutcnow(),
            1)
        cur.execute(temp_sql)

    # Now build the return value
    multivalue = ""
    temp_sql = "SELECT t_value, last_date, occurrences FROM apiary_multiprops WHERE website_id = %d AND last_date > \'%s\' AND t_name = \'%s\' ORDER BY occurrences DESC" % (
        site_id,
        '2013-04-26 18:23:01',
        key)
    cur.execute(temp_sql)
    rows = cur.fetchall()
    for row in rows:
        if len(multivalue) > 0:
            multivalue += ","
        multivalue += "%s" % row[0]

    return multivalue






