"""Pull in statistics for sites."""
# pylint: disable=C0301

from apiary.tasks import BaseApiaryTask
import logging
import requests
import datetime
import re


LOGGER = logging.getLogger()

class GetStatisticsTask(BaseApiaryTask):
    """Collect statistics on usage from site."""

    def run(self, site_id, site, method, api_url = None, stats_url = None):
        """Run the task."""
        
        LOGGER.info("Retrieve get_statistics_stats for %d" % site_id)

        if method == 'API':
            # Go out and get the statistic information
            data_url = api_url + '?action=query&meta=siteinfo&siprop=statistics&format=json'
            LOGGER.info("Pulling statistics info from %s." % data_url)
            status = False

            try:
                req = requests.get(
                    data_url,
                    timeout = 15,
                    verify = False,
                    headers = {
                        'User-Agent': 'Bumble Bee'
                    }
                )
                if req.status_code == requests.codes.ok:
                    data = req.json()
                    duration = req.elapsed.total_seconds()
                    status = True
                else:
                    raise Exception('Did not get OK status code from API request')
            except Exception, e:
                raise Exception(e)                
        elif method == 'Statistics':
            # Get stats the old fashioned way
            data_url = stats_url
            if "?" in data_url:
                data_url += "&action=raw"
            else:
                data_url += "?action=raw"
            LOGGER.info("Pulling statistics from %s." % data_url)

            try:
                # Get CSV data via raw Statistics call
                req = requests.get(
                    data_url,
                    timeout = 30,
                    verify = False,
                    headers = {
                        'User-Agent': 'Bumble Bee'
                    }
                )
                duration = req.elapsed.total_seconds()
            except Exception, e:
                self.record_error(
                    site_id=site_id,
                    sitename=site,
                    log_message="%s" % e,
                    log_type='error',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                raise Exception('Invalid response from request for statistics from Statistics page')
            else:
                # Create an object that is the same as that returned by the API
                ret_string = req.text.strip()
                if re.match(r'(\w+=\d+)\;?', ret_string):
                    # The return value looks as we expected
                    status = True
                    data = {}
                    data['query'] = {}
                    data['query']['statistics'] = {}
                    items = ret_string.split(";")
                    for item in items:
                        (name, value) = item.split("=")
                        try:
                            # Convert the value to an int, if this fails we skip it
                            value = int(value)
                            if name == "total":
                                name = "pages"
                            if name == "good":
                                name = "articles"
                            LOGGER.debug("Transforming %s to %s" % (name, value))
                            data['query']['statistics'][name] = value
                        except:
                            LOGGER.warn("Illegal value '%s' for %s." % (value, name))
                else:
                    status = False # The result didn't match the pattern expected
                    self.record_error(
                        site_id=site_id,
                        sitename=site,
                        log_message="Unexpected response to statistics call",
                        log_type='error',
                        log_severity='normal',
                        log_bot='Bumble Bee',
                        log_url=data_url
                    )
                    LOGGER.info("Result from statistics was not formatted as expected:\n%s" % ret_string)

        ret_value = True
        if status:
            # Record the new data into the DB
            LOGGER.info("JSON: %s" % data)
            LOGGER.info("Duration: %s" % duration)

            if 'query' in data:
                # Record the data received to the database
                sql_command = """
                    INSERT INTO statistics
                        (website_id, capture_date, response_timer, articles, jobs, users, admins, edits, activeusers, images, pages, views)
                    VALUES
                        (%s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                data = data['query']['statistics']
                if 'articles' in data:
                    articles = "%s" % data['articles']
                else:
                    articles = 'null'
                if 'jobs' in data:
                    jobs = "%s" % data['jobs']
                else:
                    jobs = 'null'
                if 'users' in data:
                    users = "%s" % data['users']
                else:
                    users = 'null'
                if 'admins' in data:
                    admins = "%s" % data['admins']
                else:
                    admins = 'null'
                if 'edits' in data:
                    edits = "%s" % data['edits']
                else:
                    edits = 'null'
                if 'activeusers' in data:
                    if data['activeusers'] < 0:
                        data['activeusers'] = 0
                    activeusers = "%s" % data['activeusers']
                else:
                    activeusers = 'null'
                if 'images' in data:
                    images = "%s" % data['images']
                else:
                    images = 'null'
                if 'pages' in data:
                    pages = "%s" % data['pages']
                else:
                    pages = 'null'
                if 'views' in data:
                    views = "%s" % data['views']
                else:
                    views = 'null'

                sql_command = sql_command % (
                    site_id,
                    self.sqlutcnow(),
                    duration,
                    articles,
                    jobs,
                    users,
                    admins,
                    edits,
                    activeusers,
                    images,
                    pages,
                    views)

                self.runSql(sql_command)
            else:
                self.record_error(
                    site_id=site_id,
                    sitename=site,
                    log_message='Statistics returned unexpected JSON.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                raise Exception('Statistics returned unexpected JSON.')

        else:
            LOGGER.info("Did not receive valid data from %s" % (data_url))
            raise Exception("Did not receive valid data from %s" % (data_url))

        return ret_value



