#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
    "CREATE TABLE `apiary_website_logs` (\
  `log_id` int(11) NOT NULL AUTO_INCREMENT,\
  `website_id` int(11) NOT NULL,\
  `log_date` datetime NOT NULL,\
  `website_name` varchar(255) NOT NULL,\
  `log_type` varchar(30) NOT NULL,\
  `log_severity` varchar(30) NOT NULL,\
  `log_message` varchar(255) NOT NULL,\
  `log_bot` varchar(30) DEFAULT NULL,\
  `log_url` varchar(255) DEFAULT NULL,\
  PRIMARY KEY (`log_id`),\
  KEY `idx_log_date` (`log_date`) USING BTREE,\
  KEY `idx_website_id_log_date` (`website_id`,`log_date`) USING BTREE\
) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `apiary_website_logs`",
)