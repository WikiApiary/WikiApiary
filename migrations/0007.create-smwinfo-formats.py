"""
ddd

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
    "CREATE TABLE `smwinfo_formats` ( \
        `website_id` int(11) NOT NULL, \
        `capture_date` datetime NOT NULL, \
        `format_name` varchar(50) NOT NULL, \
        `format_count` int(11) NOT NULL, \
        PRIMARY KEY (`website_id`,`capture_date`) \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `smwinfo_formats`",
    ignore_errors='rollback', # This table is dropped in migration 20.
)