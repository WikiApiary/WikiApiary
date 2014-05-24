"""
Maintenance task to keep apiary_bot_log clean. This is run daily.
"""
# pylint: disable=C0301,C0103,W1201

from WikiApiary.apiary.tasks import BaseApiaryTask
import logging
import datetime


LOGGER = logging.getLogger()

class DeleteBotLogsTask(BaseApiaryTask):
    """Delete old data out of the apiary_bot_log table."""

    def run(self):
        """Run the task."""
        sql_query = """
DELETE FROM
    apiary_bot_log
WHERE
    log_date < '%s'
"""
        delete_before = datetime.datetime.utcnow() - datetime.timedelta(weeks=4)
        delete_before_str = delete_before.strftime('%Y-%m-%d %H:%M:%S')
        LOGGER.info ("Deleting apiary_bot_log before %s." % delete_before_str)
        my_sql = sql_query % (delete_before_str)

        (success, rows_deleted) = self.runSql(my_sql)

        LOGGER.info ("Deleted %d rows." % rows_deleted)

        return rows_deleted
