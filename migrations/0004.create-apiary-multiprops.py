"""
This table is used to store property values for websites that may
contain multiple results. For example, the database version number
used in a wiki farm may be different if there are multiple database
backends. Using multiprops we can store all of the various versions
used as well as the time periods involved.

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
	"CREATE TABLE `apiary_multiprops` ( \
		`website_id` int(11) NOT NULL, \
		`t_name` varchar(255) NOT NULL, \
		`t_value` varchar(255) NOT NULL, \
		`first_date` datetime NOT NULL, \
		`last_date` datetime NOT NULL, \
		`occurrences` int(11) NOT NULL, \
		PRIMARY KEY (`website_id`,`t_name`,`t_value`) \
	) ENGINE=InnoDB DEFAULT CHARSET=utf8",
	"DROP TABLE `apiary_multiprops`",
)