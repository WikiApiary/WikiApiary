#! /usr/bin/env python

import os
import sys
import datetime
import pytz
import ConfigParser
import argparse
import socket
import MySQLdb as mdb
import simplejson
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from simplemediawiki import MediaWiki


def get_config(config_file='apiary.cfg'):
    try:
        config = ConfigParser.ConfigParser()
        config.read(config_file)
    except IOError:
        print "Cannot open %s." % config_file

    return config


def get_args():
    parser = argparse.ArgumentParser(prog="Bumble Bee",
                        description="retrieves usage and statistic information for WikiApiary")
    parser.add_argument("-s", "--segment",
                help="only work on websites in defined segment")
    parser.add_argument("-d", "--debug", action="store_true",
                help="do not write any changes to wiki or database")
    parser.add_argument("--config", default="apiary.cfg",
                help="use an alternative config file")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                help="increase output verbosity")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")

    # All set, now get the arguments
    args = parser.parse_args()

    return args


def sqlutcnow():
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    now = now.replace(microsecond=0)
    return now.strftime('%Y-%m-%d %H:%M:%S')

def pull_json(data_url):
    # Get JSON data via API and return the JSON structure parsed
    global args
    global config

    req = urllib2.Request(data_url)
    req.add_header('User-Agent', config.get('Bumble Bee', 'User-Agent'))
    opener = urllib2.build_opener()

    try:
        t1 = datetime.datetime.now()
        f = opener.open(req)
        duration = datetime.datetime.now() - t1
    except socket.timeout:
        print "Socket timeout!"
    except HTTPError as e:
        print "Error code ", e.code
    except URLError as e:
        print "Reason: ", e.reason
    else:
        # It all worked!
        data = simplejson.load(f)
        return data, duration

def get_websites(wiki, segment):
    global config
    global args

    segment_string = ""
    if segment is not None:
        if args.verbose >= 1:
            print "Only retrieving segment %s." % args.segment
        segment_string = "[[Has bot segment::%d]]" % int(args.segment)

    # Build query for sites
    my_query = "[[Category:Website]][[Is validated::True]][[Is active::True]][[Collect statistics::+]][[Collect semantic statistics::+]]"
    my_query += segment_string
    my_query += "|?Has API URL|?Check every|?Creation date|?Has ID|?Collect statistics|?Collect semantic statistics"
    my_query += "|sort=Creation date|order=asc|limit=500"

    sites = wiki.call({'action': 'ask', 'query': my_query})

    # We could just return the raw JSON object from the API, however instead we are going to clean it up into an
    # easier to deal with array of dictionary objects.
    # To keep things sensible, we'll use the same name as the properties
    if len(sites['query']['results']) > 0:
        my_sites = []
        for pagename, site in sites['query']['results'].items():
            if args.verbose >= 2:
                print "Adding %s." % pagename.encode('utf8')
            my_sites.append({
                'pagename':pagename.encode('utf8'),
                'Has API URL':site['printouts']['Has API URL'][0],
                'fullurl':site['fullurl'].encode('utf8'),
                'Check every':int(site['printouts']['Check every'][0]),
                'Collect statistics':(site['printouts']['Collect statistics'][0]=="t"), # This is a boolean but it's returned as t or f, let's make it a boolean again
                'Has ID':int(site['printouts']['Has ID'][0]),
                'Collect semantic statistics':(site['printouts']['Collect semantic statistics'][0]=="t") # This is a boolean but it's returned as t or f, let's make it a boolean again
                })

        return my_sites
    else:
        raise Exception("No sites were returned to work on.")


def get_status(db, site):
    """
    get_status will query the website_status table in ApiaryDB. It makes the decision if new
    data should be retrieved for a given website. Two booleans are returned, the first to
    tell if new statistics information should be requested and the second to pull general information.
    """
    global args
    # Get the timestamps for the last statistics and general pulls
    cur = db.cursor()
    temp_sql = "SELECT last_statistics, last_general, check_every_limit FROM website_status WHERE website_id = %d" % site['Has ID']
    cur.execute(temp_sql)
    rows_returned = cur.rowcount

    if rows_returned == 1:
        # Let's see if it's time to pull information again
        data = cur.fetchone()
        cur.close()

        (last_statistics, last_general, check_every_limit) = data[0:3]
        if args.verbose >= 3:
            print "last_stats: %s" % last_statistics
            print "last_general: %s" % last_general
            print "check_every_limit: %s" % check_every_limit

        #TODO: make this check the times!
        return (True, True)

    elif rows_returned == 0:
        cur.close()
        # This website doesn't have a status, so we should check everything
        if args.verbose >= 3:
            print "website has never been checked before"
        return (True, True)

    else:
        raise Exception("Status check returned multiple rows.")


def update_status(db, site):
    global args
    cur = db.cursor()

    # Update the website_status table
    my_now = sqlutcnow()
    temp_sql = "UPDATE website_status SET last_statistics = '%s' WHERE website_id = %d" % (my_now, site['Has ID'])
    if args.verbose >= 3:
        print "SQL: %s" % temp_sql
    cur.execute(temp_sql)
    rows_affected = cur.rowcount
    if rows_affected == 0:
        # No rows were updated, this website likely didn't exist before, so we need to insert the first time
        if args.verbose >= 2:
            print "No website_status record exists for ID %d, creating one" % site['Has ID']
        temp_sql = "INSERT website_status (website_id, last_statistics, last_general, check_every_limit) "
        temp_sql += "VALUES (%d, \"%s\", \"%s\", %d)" % (site['Has ID'], my_now, my_now, 240)
        if args.verbose >= 3:
            print "SQL: %s" % temp_sql
        cur.execute(temp_sql)

    cur.close()
    db.commit()



def record_statistics(db, site):

    # Go out and get the statistic information
    data_url = site['Has API URL'] + "?action=query&meta=siteinfo&siprop=statistics&format=json"
    (data, duration) = pull_json(data_url)

    # Record the new data into the DB
    print "Duration: %s" % duration
    print data

    # Update the status table that we did our work!
    update_status(db, site)

def record_smwinfo(db, site):
    print "In get_smwinfo"
    print site


def record_general(wiki, site):
    print "In get_general"
    print site


def record_extensions(wiki, site):
    print "In get_extensions"
    print site


def main():
    # Set global socket timeout for all our web requests
    socket.setdefaulttimeout(5)

    # Get command line options
    global args
    args = get_args()

    # Get configuration settings
    global config
    config = get_config(args.config)

    # Setup our database connection and get a cursor to work with
    apiarydb = mdb.connect(
        host=config.get('ApiaryDB', 'hostname'),
        db=config.get('ApiaryDB', 'database'),
        user=config.get('ApiaryDB', 'username'),
        passwd=config.get('ApiaryDB', 'password'))

    # Setup our connection to the wiki too
    wiki = MediaWiki(config.get('WikiApiary', 'API'))
    wiki.login(config.get('WikiApiary', 'Username'), config.get('WikiApiary', 'Password'))

    sites = get_websites(wiki, args.segment)

    for site in sites[0:2]:
        req_statistics = False
        req_general = False
        (req_statistics, req_general) = get_status(apiarydb, site)
        if req_statistics:
            record_statistics(apiarydb, site)
            record_smwinfo(apiarydb, site)
        if req_general:
            record_general(wiki, site)
            record_extensions(wiki, site)


# Run main
if __name__ == '__main__':
    main()
