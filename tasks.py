"""Celery tasks"""

from __future__ import absolute_import
from WikiApiary.celery import app
import requests


@app.task
def add(x, y):
    return x + y

@app.task
def mul(x, y):
    return x * y

@app.task
def xsum(numbers):
    return sum(numbers)

@app.task
def siteinfo(has_api_url):
    """Async task to get siteinfo/general"""
    query_param = '?action=query&meta=siteinfo&siprop=general&format=json'

    try:
        req = requests.get(
            has_api_url + query_param,
            timeout = 10)
        if req.status_code == 200:
            print "SUCCESS!\n%s\n" % req.json()['query']['general']
            return True
        else:
            return False
    except Exception, err:
        print err
        return False
