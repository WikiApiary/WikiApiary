"""
Initial version of the database had some bad ideas. Let's drop those.
"""

from yoyo import step, transaction
transaction(
	step(
		"DROP TABLE smwextinfo",
	),
	step(
		"DROP TABLE smwinfo_formats",
	),
    ignore_errors='rollback', # This table is dropped in migration 20.
)