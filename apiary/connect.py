"""Open connections to all resources."""
# pylint: disable=C0301,C0103,W1201,W0611

from WikiApiary.apiary.connect_mysql import apiary_db
from WikiApiary.apiary.connect_wikiapiary import bumble_bee, bumble_bee_token, audit_bee, audit_bee_token
from WikiApiary.apiary.connect_redis import redis_db

