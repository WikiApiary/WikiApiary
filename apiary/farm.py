"""
Base class for WikiApiary farmer bots.
"""


class Farm(object):
    """Main class for WikiApiary farms."""

    def __init__(self, farm_id):
        self.farm_id = farm_id

    def status(self):
        """Get status for farm."""
        return self.farm_id

    def get_websites(self):
        """Retrieve the list of websites from the farm."""
        pass
