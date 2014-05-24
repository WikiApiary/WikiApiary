"""Connect Redis."""
# pylint: disable=C0301,C0103,W1201

import logging
import redis


LOGGER = logging.getLogger()

LOGGER.info("Opening Redis connection")
redis_db = redis.StrictRedis(host='localhost', port='6379')
