import HTMLParser
import re


def filter_illegal_chars(pre_filter):
    """Utility function to make sure that strings are okay for page titles"""
    return re.sub(r'[#<>\[\]\|{}]', '', pre_filter).replace('=', '-')


def build_skins_template(self, ext_obj):

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

    for x in skins_sorted:
        if '*' in x:
            # Start the template instance
            template_block += "{{Skin in use\n"
            for item in x:
                # Loop through all the items in the skin data and build the instance
                if item not in ignore_keys:
                    name = key_names.get(item, item)
                    value = x[item]

                    if item == '*':
                        value = self.filter_illegal_chars(value)

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

    for x in ext_obj:
        if 'name' in x:
            template_block += "{{Extension in use\n"

            for item in x:
                if item not in ignore_keys:

                    name = key_names.get(item, item)
                    value = x[item]

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


def BuildMaxmindTemplate(self, hostname):
    template_block = "<noinclude>{{Notice bot owned page}}</noinclude><includeonly>"
    template_block += "{{Maxmind\n"

    gi = pygeoip.GeoIP('../vendor/GeoLiteCity.dat')
    data = gi.record_by_name(hostname)

    for val in data:
        template_block += "|%s=%s\n" % (val, data[val])

    template_block += "}}\n</includeonly>\n"

    return template_block

def build_general_template(x):

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
    for key in x:
        # Make sure we aren't ignoring this key
        if key not in ignore_keys:
            # If we have a name for this key use that
            name = key_names.get(key, key)
            value = x[key]

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
                value = self.ProcessMultiprops(site_id, key, value)

            template_block += "|%s=%s\n" % (name, value)

    template_block += "}}\n</includeonly>\n"

    return template_block