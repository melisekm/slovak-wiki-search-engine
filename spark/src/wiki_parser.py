import re


class Infobox:
    def __init__(self, name):
        self.name = name
        self.properties = {}

    def __str__(self):
        return f'Infobox(name={self.name})'

    def __repr__(self):
        return str(self)

    def to_string(self):
        return f'{self.name}\t{self.properties}'


class WikiPage:
    def __init__(self, title, text, infobox=None):
        self.title = title
        self.raw_text = text
        self.infobox = infobox
        self.infobox_title = infobox.name if infobox else None
        # self.terms: list[str] = []
        # self.vector: list[float] = []

    def __str__(self):
        return f'WikiPage(title={self.title}, infobox={self.infobox_title})'

    def __repr__(self):
        return str(self)

    def to_string(self):
        return f'{self.title}\t{self.raw_text}\t{self.infobox_title}\t{self.infobox.to_string() if self.infobox else ""}'


class WikiParser:
    def __init__(self):
        self.TITLE_PATTERN = re.compile(r'<title>(.*?)</title>', re.DOTALL)
        self.TEXT_PATTERN = re.compile(r'<text.*?>(.*?)</text>', re.DOTALL)
        self.INFBOX_PATTERN = re.compile(r'{{Infobox(.*?)[\n|](.*?)}}', re.DOTALL)
        self.INFBOX_ATTR_PATTERN = re.compile(
            r'\|\s*([^=]+?)\s*=\s*((?:<[^<>]*>|\[\[(?:(?!\]\]).)*\]\]|{{(?:(?!}}).)*}}|[^|{}\[\]<>]+)+)', re.DOTALL)
        self.LINK_PATTERN = re.compile(r'\[\[(?:(.+?)\|)?(.+?)\]\]')

        self.DISALLOWED_PAGES = ["Wikipédia:", "MediaWiki:"]

        self.ESCAPED_TAGS_PATTERN = re.compile(r'(\&lt\;).*?(\&gt\;)')

    def parse_infobox(self, text):
        infoboxes_all = self.INFBOX_PATTERN.findall(text)
        if not infoboxes_all:
            return None

        # pick only the first one
        infobox_match = infoboxes_all[0]
        if len(infobox_match) != 2:
            return None
        # Captialized infobox name
        infobox_name = infobox_match[0].strip().title()
        # get only first two words
        infobox_name = ' '.join(infobox_name.split(' ')[:2]).replace(' ', '')
        # remove non alphanumeric characters
        infobox_name = re.sub(r'\W+', '', infobox_name)

        infobox_attributes_raw = infobox_match[1]
        infobox_attributes_groups = self.INFBOX_ATTR_PATTERN.findall(infobox_attributes_raw)
        infobox = Infobox(infobox_name)
        for infobox_attr_grp in infobox_attributes_groups:
            if len(infobox_attr_grp) != 2:
                continue

            infobox_attr_name = infobox_attr_grp[0].strip()
            infobox_attr_value = infobox_attr_grp[1].strip()
            # replace [[link|text]] or [[text]] with text, \2 marks the second group
            infobox_attr_value = re.sub(self.LINK_PATTERN, r'\2', infobox_attr_value)
            if not infobox_attr_value:
                continue

            infobox.properties[infobox_attr_name] = re.sub(
                self.ESCAPED_TAGS_PATTERN, '', infobox_attr_value
            ).replace('&amp;amp;', '&')
        if not infobox.properties:
            return None

        return infobox

    def _parse_attr(self, text, pattern):
        attr_grp = pattern.search(text)
        if attr_grp:
            return attr_grp.group(1)
        return ''

    def parse_page(self, page):
        # title = self._parse_attr(page, self.TITLE_PATTERN)
        title = page['title']
        if title and any(title.startswith(disallowed_page) for disallowed_page in self.DISALLOWED_PAGES):
            return None
        revision = page['revision']
        if not revision:
            return WikiPage(title, '', '')
        text = revision['text']
        if not text:
            return WikiPage(title, '', '')
        text = text['data']
        if not text:
            return WikiPage(title, '', '')

        # text = page.get('revision', {}).get('text', {}).get('_VALUE', '')
        # text = self._parse_attr(page, self.TEXT_PATTERN)
        infobox = self.parse_infobox(text)
        return WikiPage(title, text, infobox)
