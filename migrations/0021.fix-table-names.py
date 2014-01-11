"""
Initial version of the database had a lot of inconsistencies
with table names. Let's fix those.
"""

from yoyo import step, transaction
transaction(
	step(
		"RENAME TABLE smwinfo TO apiary_smwinfo",
		"RENAME TABLE apiary_smwinfo TO smwinfo",
	),
	step(
		"RENAME TABLE statistics TO apiary_statistics",
		"RENAME TABLE apiary_statistics TO statistics",
	),
	step(
		"RENAME TABLE statistics_daily TO apiary_statistics_daily",
		"RENAME TABLE apiary_statistics_daily TO statistics_daily",
	),
	step(
		"RENAME TABLE statistics_weekly TO apiary_statistics_weekly",
		"RENAME TABLE apiary_statistics_weekly TO statistics_weekly",
	),
	step(
		"RENAME TABLE website_status TO apiary_website_status",
		"RENAME TABLE apiary_website_status TO website_status",
	),
)