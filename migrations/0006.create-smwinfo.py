"""
Store the raw statistics collected from SMW.

This migration implements part of the manually created Apiary DB
that WikiApiary launched with.
"""

from yoyo import step
step(
    "CREATE TABLE `smwinfo` ( \
        `website_id` int(11) NOT NULL, \
        `capture_date` datetime NOT NULL, \
        `response_timer` float DEFAULT NULL, \
        `propcount` bigint(20) NOT NULL, \
        `proppagecount` int(11) NOT NULL, \
        `usedpropcount` int(11) NOT NULL, \
        `declaredpropcount` int(11) NOT NULL, \
        `querycount` int(11) DEFAULT NULL, \
        `querysize` int(11) DEFAULT NULL, \
        `conceptcount` int(11) DEFAULT NULL, \
        `subobjectcount` int(11) DEFAULT NULL, \
        PRIMARY KEY (`website_id`,`capture_date`) \
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `smwinfo`",
)