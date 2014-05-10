"""Utils for WikiApiary."""

# pylint: disable=C0301

import HTMLParser
import re
import pygeoip
import datetime
import operator
import pytz
from WikiApiary.apiary.connect import apiary_db

def filter_illegal_chars(pre_filter):
    """Utility function to make sure that strings are okay for page titles"""
    return re.sub(r'[#<>\[\]\|{}]', '', pre_filter).replace('=', '-')

def sqlutcnow():
    """Returns the UTC time in format SQL likes."""
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc)
    now = now.replace(microsecond=0)
    return now.strftime('%Y-%m-%d %H:%M:%S')

def ProcessMultiprops(site_id, key, value):
    # Here we deal with properties that change frequently and we care about all of them.
    # For example, dbversion in a wiki farm will often have multiple values
    # and we will get different values each time, rotating between a set.
    # This function will take the value and return a more complex data structure.

    # First update the timestamp for seeing the current name/value
    cur = apiary_db.cursor()
    temp_sql = "UPDATE apiary_multiprops SET last_date=\'%s\', occurrences = occurrences + 1 WHERE website_id = %d AND t_name = \'%s\' AND t_value = \'%s\'" % (
        sqlutcnow(),
        site_id,
        key,
        value)
    cur.execute(temp_sql)
    rows_returned = cur.rowcount

    # No rows returned, we need to create this value
    if rows_returned == 0:
        temp_sql = "INSERT apiary_multiprops (website_id, t_name, t_value, first_date, last_date, occurrences) VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\', %d)" % (
            site_id,
            key,
            value,
            sqlutcnow(),
            sqlutcnow(),
            1)
        cur.execute(temp_sql)

    # Now build the return value
    multivalue = ""
    temp_sql = "SELECT t_value, last_date, occurrences FROM apiary_multiprops WHERE website_id = %d AND last_date > \'%s\' AND t_name = \'%s\' ORDER BY occurrences DESC" % (
        site_id,
        '2013-04-26 18:23:01',
        key)
    cur.execute(temp_sql)
    rows = cur.fetchall()
    for row in rows:
        if len(multivalue) > 0:
            multivalue += ","
        multivalue += "%s" % row[0]

    return multivalue

def build_skins_template(ext_obj):
    """Build a the wikitext for the skin subpage."""

    # Some keys we do not want to store in WikiApiary
    ignore_keys = []
    # Some keys we turn into more readable names for using inside of WikiApiary
    key_names = {
        '*': 'Skin name',
        'code': 'Skin code',
        'default': 'Default skin',
        'unusable': 'Skipped skin'
    }

    template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

    # Skins are returned in random order so we need to sort them before
    # making the template, otherwise we generate a lot of edits
    # that are just different ordering
    skins_sorted = sorted(ext_obj, key=operator.itemgetter('*'))

    for skin in skins_sorted:
        if '*' in skin:
            # Start the template instance
            template_block += "{{Skin in use\n"
            for item in skin:
                # Loop through all the items in the skin data and build the instance
                if item not in ignore_keys:
                    name = key_names.get(item, item)
                    value = skin[item]

                    if item == '*':
                        value = filter_illegal_chars(value)

                    if item == 'default':
                        # This parameter won't appear unless it is true
                        value = True

                    if item == 'unusable':
                        # This paramter won't appear unless it is true
                        value = True

                    template_block += "|%s=%s\n" % (name, value)

            # Now end the template instance
            template_block += "}}\n"

    template_block += "</includeonly>"

    return template_block

def build_extensions_template(ext_obj):
    """Build a the wikitext for the extensions subpage."""

    h = HTMLParser.HTMLParser()

    # Some keys we do not want to store in WikiApiary
    ignore_keys = ['descriptionmsg']
    # Some keys we turn into more readable names for using inside of WikiApiary
    key_names = {
        'author': 'Extension author',
        'name': 'Extension name',
        'version': 'Extension version',
        'type': 'Extension type',
        'url': 'Extension URL'
    }

    template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

    for extension in ext_obj:
        if 'name' in extension:
            template_block += "{{Extension in use\n"

            for item in extension:
                if item not in ignore_keys:

                    name = key_names.get(item, item)
                    value = extension[item]

                    if item == 'name':
                        # Sometimes people make the name of the extension a hyperlink using
                        # wikitext links and this makes things ugly. So, let's detect that if present.
                        if re.match(r'\[(http[^\s]+)\s+([^\]]+)\]', value):
                            (possible_url, value) = re.findall(r'\[(http[^\s]+)\s+([^\]]+)\]', value)[0]
                            # If a URL was given in the name, and not given as a formal part of the
                            # extension definition (yes, this happens) then add this to the template
                            # it is up to the template to decide what to do with this
                            template_block += "|URL Embedded in name=%s" % possible_url

                        value = filter_illegal_chars(value)
                        # Before unescaping 'regular' unicode characters, first deal with spaces
                        # because they cause problems when converted to unicode non-breaking spaces
                        value = value.replace('&nbsp;', ' ').replace('&#160;', ' ').replace('&160;', ' ')
                        value = h.unescape(value)

                    # if item == 'version':
                    #     # Breakdown the version information for more detailed analysis
                    #     ver_details = self.parse_version(value)
                    #     if 'major' in ver_details:
                    #         template_block += "|Extension version major=%s\n" % ver_details['major']
                    #     if 'minor' in ver_details:
                    #         template_block += "|Extension version minor=%s\n" % ver_details['minor']
                    #     if 'bugfix' in ver_details:
                    #         template_block += "|Extension version bugfix=%s\n" % ver_details['bugfix']
                    #     if 'flag' in ver_details:
                    #         template_block += "|Extension version flag=%s\n" % ver_details['flag']

                    if item == 'author':
                        # Authors can have a lot of junk in them, wikitext and such.
                        # We'll try to clean that up.

                        # Wikilinks with names
                        # "[[Foobar | Foo Bar]]"
                        value = re.sub(r'\[\[.*\|(.*)\]\]', r'\1', value)
                        # Simple Wikilinks
                        value = re.sub(r'\[\[(.*)\]\]', r'\1', value)
                        # Hyperlinks as wikiext
                        # "[https://www.mediawiki.org/wiki/User:Jeroen_De_Dauw Jeroen De Dauw]"
                        value = re.sub(r'\[\S+\s+([^\]]+)\]', r'\1', value)
                        # Misc text
                        value = re.sub(r'\sand\s', r', ', value)
                        value = re.sub(r'\.\.\.', r'', value)
                        value = re.sub(r'&nbsp;', r' ', value)
                        # Lastly, there could be HTML encoded stuff in these
                        value = h.unescape(value)

                    if item == 'url':
                        # Seems some people really really love protocol agnostic URL's
                        # We detect them and add a generic http: protocol to them
                        if re.match(r'^\/\/', value):
                            value = 'http:' + value

                    template_block += "|%s=%s\n" % (name, value)

            template_block += "}}\n"

    template_block += "</includeonly>"

    return template_block


def BuildMaxmindTemplate(hostname):
    """Build a the wikitext for the maxmind subpage."""

    template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"
    template_block += "{{Maxmind\n"

    gi = pygeoip.GeoIP('../vendor/GeoLiteCity.dat')
    data = gi.record_by_name(hostname)

    for val in data:
        template_block += "|%s=%s\n" % (val, data[val])

    template_block += "}}\n</includeonly>\n"

    return template_block

def build_general_template(site_id, data):
    """Build a the wikitext for the general subpage."""

    # Some keys we do not want to store in WikiApiary
    ignore_keys = ['time', 'fallback', 'fallback8bitEncoding']
    # Some keys we turn into more readable names for using inside of WikiApiary
    key_names = {
        'dbtype': 'Database type',
        'dbversion': 'Database version',
        'generator': 'MediaWiki version',
        'lang': 'Language',
        'timezone': 'Timezone',
        'timeoffset': 'Timeoffset',
        'sitename': 'Sitename',
        'rights': 'Rights',
        'phpversion': 'PHP Version',
        'phpsapi': 'PHP Server API',
        'wikiid': 'Wiki ID'
    }

    template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"

    template_block += "{{General siteinfo\n"

    # Loop through all the keys provided and create the template block
    for key in data:
        # Make sure we aren't ignoring this key
        if key not in ignore_keys:
            # If we have a name for this key use that
            name = key_names.get(key, key)
            value = data[key]

            # For some items we may need to do some preprocessing
            if isinstance(value, basestring):
                # A pipe will break the template, try HTML entity encoding it instead
                value = value.replace('|', '&#124;')
            if key == 'lang':
                # Make sure language is all lowercase, and try to standardize structure
                value = value.lower().replace('_', '-').replace(' ', '-')
            if key == 'sitename':
                # Sometimes a : appears in sitename and messes up semantics
                # Try using an HTML entity instead
                value = value.replace(':', '&#58;')
            if key == 'dbversion':
                value = ProcessMultiprops(site_id, key, value)

            template_block += "|%s=%s\n" % (name, value)

    template_block += "}}\n</includeonly>\n"

    return template_block
