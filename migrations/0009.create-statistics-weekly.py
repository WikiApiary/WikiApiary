#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
    "CREATE TABLE `statistics_weekly` (\
  `website_id` int(11) NOT NULL,\
  `website_date` date NOT NULL,\
  `users_min` bigint(20) NOT NULL,\
  `users_max` bigint(20) NOT NULL,\
  `activeusers_max` bigint(20) NOT NULL,\
  `admins_max` bigint(20) NOT NULL,\
  `articles_min` bigint(20) NOT NULL,\
  `articles_max` bigint(20) NOT NULL,\
  `edits_min` bigint(20) NOT NULL,\
  `edits_max` bigint(20) NOT NULL,\
  `jobs_max` bigint(20) NOT NULL,\
  `pages_min` bigint(20) NOT NULL,\
  `pages_max` bigint(20) NOT NULL,\
  `pages_last` bigint(20) NOT NULL,\
  `views_min` bigint(20) NOT NULL,\
  `views_max` bigint(20) NOT NULL,\
  `smw_propcount_min` bigint(20) NOT NULL,\
  `smw_propcount_max` bigint(20) NOT NULL,\
  `smw_proppagecount_last` int(11) NOT NULL,\
  `smw_usedpropcount_last` int(11) NOT NULL,\
  `smw_declaredpropcount_last` int(11) NOT NULL,\
  PRIMARY KEY (`website_id`,`website_date`)\
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT",
    "DROP TABLE IF EXISTS `statistics_weekly`",
)