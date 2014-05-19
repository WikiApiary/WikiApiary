"""
This is a daily aggregation table to collect raw statistics data
into daily summary information.

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
    "CREATE TABLE `statistics_daily` ( \
        `website_id` int(11) NOT NULL, \
        `website_date` date NOT NULL, \
        `users_min` bigint(20) NOT NULL, \
        `users_max` bigint(20) NOT NULL, \
        `activeusers_max` bigint(20) NOT NULL, \
        `admins_max` bigint(20) NOT NULL, \
        `articles_min` bigint(20) NOT NULL, \
        `articles_max` bigint(20) NOT NULL, \
        `edits_min` bigint(20) NOT NULL, \
        `edits_max` bigint(20) NOT NULL, \
        `jobs_max` bigint(20) NOT NULL, \
        `pages_min` bigint(20) NOT NULL, \
        `pages_max` bigint(20) NOT NULL, \
        `pages_last` bigint(20) NOT NULL, \
        `views_min` bigint(20) NOT NULL, \
        `views_max` bigint(20) NOT NULL, \
        `smw_propcount_min` bigint(20) NOT NULL, \
        `smw_propcount_max` bigint(20) NOT NULL, \
        `smw_proppagecount_last` int(11) NOT NULL, \
        `smw_usedpropcount_last` int(11) NOT NULL, \
        `smw_declaredpropcount_last` int(11) NOT NULL, \
        PRIMARY KEY (`website_id`,`website_date`) \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE `statistics_daily`",
)