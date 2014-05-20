"""
Clean up the website log table.
"""
# pylint: disable=C0301,C0103,W1201

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging
import datetime


LOGGER = logging.getLogger()

class DeleteWebsiteLogsTask(BaseApiaryTask):
    """Delete old entries from the bot_log."""

    def run(self):
        """Execute the task."""
        sql_query = """
DELETE FROM
   apiary_website_logs
WHERE
   log_date < '%s'
"""
        delete_before = datetime.datetime.utcnow() - datetime.timedelta(weeks=8)
        delete_before_str = delete_before.strftime('%Y-%m-%d %H:%M:%S')
        LOGGER.info("Deleting apiary_website_logs before %s." % delete_before_str)
        my_sql = sql_query % (delete_before_str)

        (success, rows_deleted) = self.runSql(my_sql)

        LOGGER.info("Deleted %d rows." % rows_deleted)

        return True
