/*
ApiaryDB database script.

This is cloned from the running Apiary database as of
12/8/2013. Make sure all changes are migrations off of this
schema, and note that some of these tables will have
millions of rows.
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `apiary_bot_log`
-- ----------------------------
DROP TABLE IF EXISTS `apiary_bot_log`;
CREATE TABLE `apiary_bot_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `log_date` datetime NOT NULL,
  `bot` varchar(30) NOT NULL,
  `duration` float DEFAULT NULL,
  `log_type` varchar(10) NOT NULL,
  `message` varchar(255) NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_log_date` (`log_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1215810 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `apiary_multiprops`
-- ----------------------------
DROP TABLE IF EXISTS `apiary_multiprops`;
CREATE TABLE `apiary_multiprops` (
  `website_id` int(11) NOT NULL,
  `t_name` varchar(255) NOT NULL,
  `t_value` varchar(255) NOT NULL,
  `first_date` datetime NOT NULL,
  `last_date` datetime NOT NULL,
  `occurrences` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`t_name`,`t_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `apiary_website_logs`
-- ----------------------------
DROP TABLE IF EXISTS `apiary_website_logs`;
CREATE TABLE `apiary_website_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `website_id` int(11) NOT NULL,
  `log_date` datetime NOT NULL,
  `website_name` varchar(255) NOT NULL,
  `log_type` varchar(30) NOT NULL,
  `log_severity` varchar(30) NOT NULL,
  `log_message` varchar(255) NOT NULL,
  `log_bot` varchar(30) DEFAULT NULL,
  `log_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_log_date` (`log_date`) USING BTREE,
  KEY `idx_website_id_log_date` (`website_id`,`log_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1723321 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `smwextinfo`
-- ----------------------------
DROP TABLE IF EXISTS `smwextinfo`;
CREATE TABLE `smwextinfo` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `query_count` int(11) NOT NULL,
  `query_pages` int(11) NOT NULL,
  `query_concepts` int(11) NOT NULL,
  `query_pageslarge` int(11) NOT NULL,
  `size1` int(11) NOT NULL,
  `size2` int(11) NOT NULL,
  `size3` int(11) NOT NULL,
  `size4` int(11) NOT NULL,
  `size5` int(11) NOT NULL,
  `size6` int(11) NOT NULL,
  `size7` int(11) NOT NULL,
  `size8` int(11) NOT NULL,
  `size9` int(11) NOT NULL,
  `size10plus` int(11) NOT NULL,
  `format_broadtable` int(11) NOT NULL,
  `format_csv` int(11) NOT NULL,
  `format_category` int(11) NOT NULL,
  `format_count` int(11) NOT NULL,
  `format_dsv` int(11) NOT NULL,
  `format_debug` int(11) NOT NULL,
  `format_embedded` int(11) NOT NULL,
  `format_feed` int(11) NOT NULL,
  `format_json` int(11) NOT NULL,
  `format_list` int(11) NOT NULL,
  `format_ol` int(11) NOT NULL,
  `format_rdf` int(11) NOT NULL,
  `format_table` int(11) NOT NULL,
  `format_template` int(11) NOT NULL,
  `format_ul` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `smwinfo`
-- ----------------------------
DROP TABLE IF EXISTS `smwinfo`;
CREATE TABLE `smwinfo` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `propcount` bigint(20) NOT NULL,
  `proppagecount` int(11) NOT NULL,
  `usedpropcount` int(11) NOT NULL,
  `declaredpropcount` int(11) NOT NULL,
  `querycount` int(11) DEFAULT NULL,
  `querysize` int(11) DEFAULT NULL,
  `conceptcount` int(11) DEFAULT NULL,
  `subobjectcount` int(11) DEFAULT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `smwinfo_formats`
-- ----------------------------
DROP TABLE IF EXISTS `smwinfo_formats`;
CREATE TABLE `smwinfo_formats` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `format_name` varchar(50) NOT NULL,
  `format_count` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `statistics`
-- ----------------------------
DROP TABLE IF EXISTS `statistics`;
CREATE TABLE `statistics` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `users` bigint(20) NOT NULL,
  `activeusers` bigint(20) DEFAULT NULL,
  `admins` bigint(20) NOT NULL,
  `articles` bigint(20) NOT NULL,
  `edits` bigint(20) NOT NULL,
  `images` bigint(20) DEFAULT NULL,
  `jobs` bigint(20) DEFAULT NULL,
  `pages` bigint(20) NOT NULL,
  `views` bigint(20) DEFAULT NULL,
  `smw_propcount` bigint(20) DEFAULT NULL,
  `smw_proppagecount` int(11) DEFAULT NULL,
  `smw_usedpropcount` int(11) DEFAULT NULL,
  `smw_declaredpropcount` int(11) DEFAULT NULL,
  PRIMARY KEY (`website_id`,`capture_date`),
  KEY `idx_capture_date` (`capture_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `statistics_daily`
-- ----------------------------
DROP TABLE IF EXISTS `statistics_daily`;
CREATE TABLE `statistics_daily` (
  `website_id` int(11) NOT NULL,
  `website_date` date NOT NULL,
  `users_min` bigint(20) NOT NULL,
  `users_max` bigint(20) NOT NULL,
  `activeusers_max` bigint(20) NOT NULL,
  `admins_max` bigint(20) NOT NULL,
  `articles_min` bigint(20) NOT NULL,
  `articles_max` bigint(20) NOT NULL,
  `edits_min` bigint(20) NOT NULL,
  `edits_max` bigint(20) NOT NULL,
  `jobs_max` bigint(20) NOT NULL,
  `pages_min` bigint(20) NOT NULL,
  `pages_max` bigint(20) NOT NULL,
  `pages_last` bigint(20) NOT NULL,
  `views_min` bigint(20) NOT NULL,
  `views_max` bigint(20) NOT NULL,
  `smw_propcount_min` bigint(20) NOT NULL,
  `smw_propcount_max` bigint(20) NOT NULL,
  `smw_proppagecount_last` int(11) NOT NULL,
  `smw_usedpropcount_last` int(11) NOT NULL,
  `smw_declaredpropcount_last` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`website_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `statistics_weekly`
-- ----------------------------
DROP TABLE IF EXISTS `statistics_weekly`;
CREATE TABLE `statistics_weekly` (
  `website_id` int(11) NOT NULL,
  `website_date` date NOT NULL,
  `users_min` bigint(20) NOT NULL,
  `users_max` bigint(20) NOT NULL,
  `activeusers_max` bigint(20) NOT NULL,
  `admins_max` bigint(20) NOT NULL,
  `articles_min` bigint(20) NOT NULL,
  `articles_max` bigint(20) NOT NULL,
  `edits_min` bigint(20) NOT NULL,
  `edits_max` bigint(20) NOT NULL,
  `jobs_max` bigint(20) NOT NULL,
  `pages_min` bigint(20) NOT NULL,
  `pages_max` bigint(20) NOT NULL,
  `pages_last` bigint(20) NOT NULL,
  `views_min` bigint(20) NOT NULL,
  `views_max` bigint(20) NOT NULL,
  `smw_propcount_min` bigint(20) NOT NULL,
  `smw_propcount_max` bigint(20) NOT NULL,
  `smw_proppagecount_last` int(11) NOT NULL,
  `smw_usedpropcount_last` int(11) NOT NULL,
  `smw_declaredpropcount_last` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`website_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;

-- ----------------------------
--  Table structure for `website_status`
-- ----------------------------
DROP TABLE IF EXISTS `website_status`;
CREATE TABLE `website_status` (
  `website_id` int(11) NOT NULL COMMENT 'Website ID to match back to the wiki.',
  `check_every_limit` int(11) DEFAULT '60' COMMENT 'The check every value is stored in the wiki but the bot should not query any more often than this value allows, regardless of what the wiki is set to.',
  `last_statistics` datetime DEFAULT NULL COMMENT 'The timestamp for the most recent statistics data. (This is shared for both general statistics and smwinfo).',
  `last_general` datetime DEFAULT NULL COMMENT 'The timestamp for the most recent general website data.',
  `last_general_hash` char(64) DEFAULT NULL,
  `last_extension` datetime DEFAULT NULL,
  `last_extension_hash` char(64) DEFAULT NULL,
  `last_skin` datetime DEFAULT NULL,
  `last_skin_hash` char(64) DEFAULT NULL,
  PRIMARY KEY (`website_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  View structure for `apiary_website_logs_summary`
-- ----------------------------
DROP VIEW IF EXISTS `apiary_website_logs_summary`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`192.168.189.13` SQL SECURITY DEFINER VIEW `apiary_website_logs_summary` AS select `apiary_website_logs`.`website_id` AS `website_id`,count(0) AS `log_count`,max(`apiary_website_logs`.`log_date`) AS `log_date_last`,min(`apiary_website_logs`.`log_date`) AS `lot_date_first` from `apiary_website_logs` group by `apiary_website_logs`.`website_id`;

SET FOREIGN_KEY_CHECKS = 1;
