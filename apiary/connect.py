import ConfigParser
from simplemediawiki import MediaWiki
import os
import MySQLdb as mdb


APIARY_CONFIG = os.environ.get("APIARY_CONFIG", 'WikiApiary/config/apiary.cfg')
config = ConfigParser.ConfigParser()

try:
	config.read(APIARY_CONFIG)
except IOError:
    print "Cannot open %s." % APIARY_CONFIG


def open_connection(bot_name):
	apiary_wiki = MediaWiki(config.get('WikiApiary', 'API'))
	apiary_wiki.login(config.get(bot_name, 'Username'), config.get(bot_name, 'Password'))
	# We need an edit token
	c = apiary_wiki.call({'action': 'query', 'titles': 'Foo', 'prop': 'info', 'intoken': 'edit'})
	edit_token = c['query']['pages']['-1']['edittoken']
	return (apiary_wiki, edit_token)


bumble_bee, bumble_bee_token = open_connection("Bumble Bee")
audit_bee, audit_bee_token = open_connection("Audit Bee")


apiary_db = mdb.connect(
    host=config.get('ApiaryDB', 'hostname'),
    db=config.get('ApiaryDB', 'database'),
    user=config.get('ApiaryDB RW', 'username'),
    passwd=config.get('ApiaryDB RW', 'password'),
    charset='utf8')
