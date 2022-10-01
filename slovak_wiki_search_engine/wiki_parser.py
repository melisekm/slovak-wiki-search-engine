import re
from typing import Optional


class Infobox:
    def __init__(self, name):
        self.name = name
        self.properties = {}

    def __str__(self):
        return f'Infobox(name={self.name})'

    def __repr__(self):
        return str(self)


class WikiPage:
    def __init__(self, title: str, text: str, infobox: Optional[list[Infobox]] = None):
        self.title = title
        self.raw_text = text
        self.infobox = infobox
        self.infobox_title = infobox[0].name if infobox and len(infobox) > 0 else None
        self.terms: Optional[list[str]] = None
        self.tfidf_vector: Optional[list[float]] = None

    def __str__(self):
        return f'WikiPage(title={self.title}, infobox={self.infobox_title})'

    def __repr__(self):
        return str(self)


class WikiParser:
    def __init__(self):
        self.PAGE_PATTERN = re.compile(r'<page>(.*?)</page>', re.DOTALL)
        self.TITLE_PATTERN = re.compile(r'<title>(.*?)</title>', re.DOTALL)
        self.TEXT_PATTERN = re.compile(r'<text.*?>(.*?)</text>', re.DOTALL)
        self.INFBOX_PATTERN = re.compile(r'{{Infobox(.*?)[\n|](.*?)}}', re.DOTALL)
        # self.INFBOX_ATTR_PATTERN = re.compile(r'\|(.+?)\s*=\s*(.+?)\n', re.DOTALL)
        # https://stackoverflow.com/questions/21796698/wikipedia-infobox-trouble-matching-pattern
        self.INFBOX_ATTR_PATTERN = re.compile(
            r'\|\s*([^=]+?)\s*=\s*((?:<[^<>]*>|\[\[(?:(?!\]\]).)*\]\]|{{(?:(?!}}).)*}}|[^|{}\[\]<>]+)+)', re.DOTALL)
        self.LINK_PATTERN = re.compile(r'\[\[(?:(.+?)\|)?(.+?)\]\]')

    def parse_infobox(self, text: str):
        infoboxes_all = self.INFBOX_PATTERN.findall(text)
        if not infoboxes_all:
            return []

        parsed_infoboxes = []

        for infobox_match in infoboxes_all:
            if len(infobox_match) != 2:
                continue
            infobox_name = infobox_match[0].strip().title()
            # get only first two words
            infobox_name = ' '.join(infobox_name.split(' ')[:2]).replace(' ', '')
            # remove non alphanumeric characters
            infobox_name = re.sub(r'\W+', '', infobox_name)

            infobox_attrs_raw = infobox_match[1]
            infobox_attrs_grps = self.INFBOX_ATTR_PATTERN.findall(infobox_attrs_raw)
            infobox = Infobox(infobox_name)
            for infobox_attr_grp in infobox_attrs_grps:
                if len(infobox_attr_grp) != 2:
                    continue

                infobox_attr_name = infobox_attr_grp[0].strip()
                infobox_attr_value = infobox_attr_grp[1].strip()
                # replace [[link|text]] or [[text]] with text, \2 marks the second group
                infobox_attr_value = re.sub(self.LINK_PATTERN, r'\2', infobox_attr_value)
                if not infobox_attr_value:
                    continue

                infobox.properties[infobox_attr_name] = infobox_attr_value

            parsed_infoboxes.append(infobox)
        return parsed_infoboxes

    def _parse_attr(self, text: str, pattern: re.Pattern) -> str:
        attr_grp = pattern.search(text)
        if attr_grp:
            return attr_grp.group(1)
        return ''

    def parse(self, wikipedia_data_path) -> list[WikiPage]:
        with open(wikipedia_data_path, 'r', encoding='UTF-8') as wikipedia_data_file:
            wiki_data = wikipedia_data_file.read()

        pages = self.PAGE_PATTERN.findall(wiki_data)
        parsed_pages = []
        for page in pages:
            title = self._parse_attr(page, self.TITLE_PATTERN)
            text = self._parse_attr(page, self.TEXT_PATTERN)
            infobox = self.parse_infobox(text)
            parsed_pages.append(WikiPage(title, text, infobox))

        with_infobox = [page for page in parsed_pages if page.infobox]
        more_than_one_infobox = [page for page in with_infobox if len(page.infobox) > 1]
        pass


if __name__ == '__main__':
    wiki_parser = WikiParser()
    import timeit
    start_time = timeit.default_timer()
    wiki_parser.parse('../data/sk_wikipedia_dump_small_1m.xml')
    print(f'Elapsed time: {timeit.default_timer() - start_time}')
