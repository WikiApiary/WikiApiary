"""Open connections to all resources."""
# pylint: disable=C0301,C0103,W1201,W0611

from apiary.connect_mysql import apiary_db
from apiary.connect_wikiapiary import bumble_bee, bumble_bee_token, audit_bee, audit_bee_token
from apiary.connect_redis import redis_db

