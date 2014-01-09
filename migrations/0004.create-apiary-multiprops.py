#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
    "CREATE TABLE `apiary_multiprops` (\
  `website_id` int(11) NOT NULL,\
  `t_name` varchar(255) NOT NULL,\
  `t_value` varchar(255) NOT NULL,\
  `first_date` datetime NOT NULL,\
  `last_date` datetime NOT NULL,\
  `occurrences` int(11) NOT NULL,\
  PRIMARY KEY (`website_id`,`t_name`,`t_value`)\
) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `apiary_multiprops`",
)