#
# file: migrations/0001.create-foo.py
#

from yoyo import step
step(
    "CREATE TABLE `apiary_bot_log` (\
        `log_id` int(11) NOT NULL AUTO_INCREMENT,\
        `log_date` datetime NOT NULL,\
        `bot` varchar(30) NOT NULL,\
        `duration` float DEFAULT NULL,\
        `log_type` varchar(10) NOT NULL,\
        `message` varchar(255) NOT NULL,\
        PRIMARY KEY (`log_id`),\
        KEY `idx_log_date` (`log_date`) USING BTREE\
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8",
    "DROP TABLE IF EXISTS `apiary_bot_log`",
)