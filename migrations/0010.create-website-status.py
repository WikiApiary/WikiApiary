#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
    "CREATE TABLE `website_status` (\
  `website_id` int(11) NOT NULL\
    COMMENT 'Website ID to match back to the wiki.',\
  `check_every_limit` int(11) DEFAULT '60'\
    COMMENT 'The check every value is stored in the wiki but the bot should not query any more often than this value allows, regardless of what the wiki is set to.',\
  `last_statistics` datetime DEFAULT NULL\
    COMMENT 'The timestamp for the most recent statistics data. (This is shared for both general statistics and smwinfo).',\
  `last_general` datetime DEFAULT NULL COMMENT 'The timestamp for the most recent general website data.',\
  `last_general_hash` char(64) DEFAULT NULL,\
  `last_extension` datetime DEFAULT NULL,\
  `last_extension_hash` char(64) DEFAULT NULL,\
  `last_skin` datetime DEFAULT NULL,\
  `last_skin_hash` char(64) DEFAULT NULL,\
  PRIMARY KEY (`website_id`)\
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `website_status`",
)