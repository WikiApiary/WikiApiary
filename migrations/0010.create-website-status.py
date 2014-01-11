"""
Store status information for the websites being monitored. This
is a bad design and should be redone.

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
    "CREATE TABLE `website_status` ( \
        `website_id` int(11) NOT NULL, \
        `check_every_limit` int(11) DEFAULT '60', \
        `last_statistics` datetime DEFAULT NULL, \
        `last_general` datetime DEFAULT NULL, \
        `last_general_hash` char(64) DEFAULT NULL, \
        `last_extension` datetime DEFAULT NULL, \
        `last_extension_hash` char(64) DEFAULT NULL, \
        `last_skin` datetime DEFAULT NULL, \
        `last_skin_hash` char(64) DEFAULT NULL, \
        PRIMARY KEY (`website_id`) \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE `website_status`",
)