"""
Primary statistics table for storing data collected from the websites.
This table is partitioned by the website id. Changes to this table
need to be managed carefully. It is a very large table.

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
    "CREATE TABLE `statistics` ( \
        `website_id` int(11) NOT NULL, \
        `capture_date` datetime NOT NULL, \
        `response_timer` float DEFAULT NULL, \
        `users` bigint(20) NOT NULL, \
        `activeusers` bigint(20) DEFAULT NULL, \
        `admins` bigint(20) NOT NULL, \
        `articles` bigint(20) NOT NULL, \
        `edits` bigint(20) NOT NULL, \
        `images` bigint(20) DEFAULT NULL, \
        `jobs` bigint(20) DEFAULT NULL, \
        `pages` bigint(20) NOT NULL, \
        `views` bigint(20) DEFAULT NULL, \
        PRIMARY KEY (`website_id`,`capture_date`), \
        KEY `idx_capture_date` (`capture_date`) USING BTREE \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 \
    PARTITION BY HASH (website_id) PARTITIONS 15",
    "DROP TABLE IF EXISTS `statistics`",
)