"""Process weekly activities for extensions."""
# pylint: disable=C0301,C0103,W1201

from apiary.tasks import BaseApiaryTask
import logging
import datetime


LOGGER = logging.getLogger()

class ExtensionWeekly(BaseApiaryTask):
    """Kick off weekly tasks for extensions."""

    def run(self, curr_day = None, curr_hour = None):
        """Process the list of extensions."""

        # Allow these to be passed in for testing
        if curr_day is None:
            curr_day = int(datetime.datetime.now().strftime("%w"))
        if curr_hour is None:
            curr_hour = int(datetime.datetime.now().strftime("%H"))

        LOGGER.info ("Processing extensions for day segment %d and hour segment %d", curr_day, curr_hour)
        my_query = ''.join([
            "[[Category:Extension]]",
            "[[Has day segment::%d]]" % curr_day,
            "[[Has hour segment::%d]]" % curr_hour,
            "|sort=Creation date",
            "|limit=1000"])
        LOGGER.debug ("Query: %s" % my_query)

        extensions = self.bumble_bee.call({
            'action': 'ask',
            'query': my_query
        })

        i = 0
        for extension in extensions['query']['results'].items():
            i += 1
            LOGGER.info(extension)
            LOGGER.info("Processing extension %s", extension[1]['fulltext'])

            # Now call tasks to operate on extensions
            MediawikiTasks.run(extension)
            pass

        return i


