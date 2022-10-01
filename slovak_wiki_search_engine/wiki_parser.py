import itertools
import logging
import random
import re
from collections import defaultdict
from timeit import default_timer as timer
from typing import Optional, Union

from tqdm import tqdm

import utils

logger = logging.getLogger(__name__)


class Infobox:
    def __init__(self, name):
        self.name = name
        self.properties = {}

    def __str__(self):
        return f'Infobox(name={self.name})'

    def __repr__(self):
        return str(self)


class WikiPage:
    def __init__(self, doc_id: int, title: str, text: str, infobox: Optional[Infobox] = None):
        self.doc_id = doc_id
        self.title = title
        self.raw_text = text
        self.infobox = infobox
        self.infobox_title = infobox.name if infobox else None
        self.terms: Optional[list[str]] = None
        self.vector: Optional[list[float]] = None

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

        self.stats = {}

    def parse_infobox(self, text: str):
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

            infobox.properties[infobox_attr_name] = infobox_attr_value
        if not infobox.properties:
            return None

        return infobox

    def _parse_attr(self, text: str, pattern: re.Pattern) -> str:
        attr_grp = pattern.search(text)
        if attr_grp:
            return attr_grp.group(1)
        return ''

    def parse_pages(self, pages: tuple[int, str], pbar_position=0) -> tuple[list[WikiPage],
                                                                            dict[Union[int, list, defaultdict]]]:
        parsed_pages = []
        infobox_types = defaultdict(list)
        for page, idx in tqdm(pages, desc=f"{pbar_position}", position=pbar_position):
            title = self._parse_attr(page, self.TITLE_PATTERN)
            text = self._parse_attr(page, self.TEXT_PATTERN)
            infobox = self.parse_infobox(text)

            parsed_page = WikiPage(idx, title, text, infobox)
            parsed_pages.append(parsed_page)
            if infobox:
                infobox_types[infobox.name].append(parsed_page)

        stats = {
            'pages': len(pages),
            'parsed_pages': len(parsed_pages),
            'pages_with_infobox': [page for page in parsed_pages if page.infobox],
            'infobox_types': infobox_types
        }

        return parsed_pages, stats

    def get_pages(self, wikipedia_data_path: str) -> list[tuple[int, str]]:
        logger.info(f'Parsing pages from {wikipedia_data_path}')
        read_time = timer()
        with open(wikipedia_data_path, 'r', encoding='UTF-8') as wikipedia_data_file:
            wiki_data = wikipedia_data_file.read()
        pages = self.PAGE_PATTERN.findall(wiki_data)
        logger.info(f'Read {len(pages)} pages in {timer() - read_time:.2f}s')
        return [(page, idx) for idx, page in enumerate(pages)]

    def parse_wiki(self, wikipedia_data_path: str, workers=4) -> list[WikiPage]:
        pages = self.get_pages(wikipedia_data_path)
        results = utils.generic_parallel_execution(pages, self.parse_pages, workers=workers, executor='process')
        merged_parsed_documents: list[WikiPage] = list(itertools.chain.from_iterable(x[0] for x in results))
        self.merge_stats(results)
        random.shuffle(merged_parsed_documents)
        return merged_parsed_documents

    def merge_stats(self, results: tuple[list[WikiPage], dict[Union[int, list, defaultdict]]]):
        for stat in (x[1] for x in results):
            for key, value in stat.items():
                if key not in self.stats:
                    self.stats[key] = value
                else:
                    if isinstance(value, defaultdict):
                        for k, v in value.items():
                            self.stats[key][k].extend(v)
                    else:
                        self.stats[key] += value

        logger.info(f"Total pages: {self.stats['pages']}")
        logger.info(f"Successfully parsed pages: {self.stats['parsed_pages']}")
        logger.info(f"Pages with infobox: {len(self.stats['pages_with_infobox'])}")
        logger.info(f"Infobox types: {len(self.stats['infobox_types'])}")


if __name__ == '__main__':
    utils.setup_logging()
    wiki_parser = WikiParser()
    results_t = wiki_parser.parse_wiki('../data/sk_wikipedia_dump_small_350k_articles.xml', workers=4)
    pass
