"""
After applying all migrations create views.
"""

from yoyo import step
step(
    "CREATE VIEW `apiary_website_logs_summary` AS \
        SELECT `apiary_website_logs`.`website_id` AS `website_id`, \
            count(0) AS `log_count`, \
            max(`apiary_website_logs`.`log_date`) AS `log_date_last`, \
            min(`apiary_website_logs`.`log_date`) AS `lot_date_first` \
            FROM `apiary_website_logs` \
            GROUP BY `apiary_website_logs`.`website_id`;",
    "DROP VIEW IF EXISTS `apiary_website_logs_summary`;"
)