"""
Update the total edits that WikiApiary knows about.
"""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging


LOGGER = logging.getLogger()

class UpdateTotalEditsTask(BaseApiaryTask):
    """Update the total number of edits across all wikis."""

    def run(self):
        """Run the task."""
        sql_query = """
SELECT
    SUM(a.edits) AS total_edits,
    SUM(a.activeusers) AS total_active_users,
    SUM(a.pages) AS total_pages
FROM statistics a
INNER JOIN (
    SELECT
        website_id, MAX(capture_date) AS max_date
    FROM
        statistics
    GROUP BY
        website_id) as b
ON
    a.website_id = b.website_id AND
    a.capture_date = b.max_date
"""

        # Get the total edit count
        cur = self.apiary_db.cursor()
        cur.execute(sql_query)
        data = cur.fetchone()
        LOGGER.info("Total edits: %d Total active users: %d Total pages: %d", data[0], data[1], data[2])

        # Update the wiki with the new value
        c = self.bumble_bee.call({
            'action': 'edit',
            'title': 'WikiApiary:Total edits',
            'text': data[0],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.bumble_bee_token
        })
        LOGGER.debug(c)

        # Update the wiki with the new value
        c = self.bumble_bee.call({
            'action': 'edit',
            'title': 'WikiApiary:Total active users',
            'text': data[1],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.bumble_bee_token
        })
        LOGGER.debug(c)

        # Update the wiki with the new value
        c = self.bumble_bee.call({
            'action': 'edit',
            'title': 'WikiApiary:Total pages',
            'text': data[2],
            'bot': True,
            'summary': 'Updating total edit count.',
            'minor': True,
            'token': self.bumble_bee_token
        })
        LOGGER.debug(c)

        return True
