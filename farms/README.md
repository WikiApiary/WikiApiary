### Farmers

Farmers are bots that WikiApiary runs on a schedule to automatically populate wikis on popular wiki farms like Wikia or Wikkii, as well as established organizations like Wikimedia.

Farmer bots should inherit from the Farm class and have a main method that invokes them. They must be idempotent and allow running as frequent as desired.
