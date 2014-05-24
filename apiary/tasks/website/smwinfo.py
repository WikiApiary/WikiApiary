"""Pull in smw info for sites."""
# pylint: disable=C0301

from apiary.tasks import BaseApiaryTask
import logging
import requests


LOGGER = logging.getLogger()

class GetSMWInfoTask(BaseApiaryTask):
    """Collect statistics on usage from site."""

    def run(self, site_id, site, api_url):
        """Execute collection."""

        LOGGER.info("Retrieve smwinfo for %d" % site_id)

        data_url = ''.join([
            api_url,
            '?action=smwinfo',
            '&info=propcount%7Cusedpropcount%7Cdeclaredpropcount%7Cproppagecount%7Cquerycount%7Cquerysize%7Cconceptcount%7Csubobjectcount',
            '&format=json'
        ])

        try:
            req = requests.get(data_url, timeout = 15, verify=False)
            duration = req.elapsed.total_seconds()
            data = req.json()
        except Exception, e:
            LOGGER.error(e)
            raise Exception(e)

        if req.status_code == 200:

            if 'info' in data:
                # Record the data received to the database
                sql_command = """
                    INSERT INTO smwinfo
                        (website_id, capture_date, response_timer, propcount, proppagecount, usedpropcount, declaredpropcount,
                            querycount, querysize, conceptcount, subobjectcount)
                    VALUES
                        (%d, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                propcount = data['info'].get('propcount', 'null')
                proppagecount = data['info'].get('proppagecount', 'null')
                usedpropcount = data['info'].get('usedpropcount', 'null')
                declaredpropcount = data['info'].get('declaredpropcount', 'null')

                # Catch additional results returned in SMW 1.9
                querycount = data['info'].get('querycount', 'null')
                querysize = data['info'].get('querysize', 'null')
                conceptcount = data['info'].get('conceptcount', 'null')
                subobjectcount = data['info'].get('subobjectcount', 'null')

                sql_command = sql_command % (
                    site_id,
                    self.sqlutcnow(),
                    duration,
                    propcount,
                    proppagecount,
                    usedpropcount,
                    declaredpropcount,
                    querycount,
                    querysize,
                    conceptcount,
                    subobjectcount)

                self.runSql(sql_command)

                return True
            else:
                self.record_error(
                    site_id=site_id,
                    sitename=sitename,
                    log_message='SMWInfo returned unexpected JSON.',
                    log_type='info',
                    log_severity='normal',
                    log_bot='Bumble Bee',
                    log_url=data_url
                )
                raise Exception('SMWInfo returned unexpected JSON.')

        raise Exception()
