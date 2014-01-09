#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
	"CREATE TABLE `smwextinfo` (\
  `website_id` int(11) NOT NULL,\
  `capture_date` datetime NOT NULL,\
  `response_timer` float DEFAULT NULL,\
  `query_count` int(11) NOT NULL,\
  `query_pages` int(11) NOT NULL,\
  `query_concepts` int(11) NOT NULL,\
  `query_pageslarge` int(11) NOT NULL,\
  `size1` int(11) NOT NULL,\
  `size2` int(11) NOT NULL,\
  `size3` int(11) NOT NULL,\
  `size4` int(11) NOT NULL,\
  `size5` int(11) NOT NULL,\
  `size6` int(11) NOT NULL,\
  `size7` int(11) NOT NULL,\
  `size8` int(11) NOT NULL,\
  `size9` int(11) NOT NULL,\
  `size10plus` int(11) NOT NULL,\
  `format_broadtable` int(11) NOT NULL,\
  `format_csv` int(11) NOT NULL,\
  `format_category` int(11) NOT NULL,\
  `format_count` int(11) NOT NULL,\
  `format_dsv` int(11) NOT NULL,\
  `format_debug` int(11) NOT NULL,\
  `format_embedded` int(11) NOT NULL,\
  `format_feed` int(11) NOT NULL,\
  `format_json` int(11) NOT NULL,\
  `format_list` int(11) NOT NULL,\
  `format_ol` int(11) NOT NULL,\
  `format_rdf` int(11) NOT NULL,\
  `format_table` int(11) NOT NULL,\
  `format_template` int(11) NOT NULL,\
  `format_ul` int(11) NOT NULL,\
  PRIMARY KEY (`website_id`,`capture_date`)\
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
  "DROP TABLE IF EXISTS `smwextinfo`"
)