import itertools
import logging
import re
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from timeit import default_timer as timer
import numpy as np
from collections import defaultdict
from typing import Optional, Union


class Infobox:
    def __init__(self, name):
        self.name = name
        self.properties = {}

    def __str__(self):
        return f'Infobox(name={self.name})'

    def __repr__(self):
        return str(self)


class WikiPage:
    def __init__(self, title: str, text: str, infobox: Optional[Infobox] = None):
        self.title = title
        self.raw_text = text
        self.infobox = infobox
        self.infobox_title = infobox.name if infobox else None
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

    def parse(self, pages) -> list[tuple[list[WikiPage], dict[Union[int, list, defaultdict]]]]:
        parsed_pages = []
        infobox_types = defaultdict(list)
        for page in pages:
            title = self._parse_attr(page, self.TITLE_PATTERN)
            text = self._parse_attr(page, self.TEXT_PATTERN)
            infobox = self.parse_infobox(text)

            parsed_page = WikiPage(title, text, infobox)
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

    def get_pages(self, wikipedia_data_path: str) -> list[str]:
        with open(wikipedia_data_path, 'r', encoding='UTF-8') as wikipedia_data_file:
            wiki_data = wikipedia_data_file.read()
        pages = self.PAGE_PATTERN.findall(wiki_data)
        return pages

    def parse_wiki(self, wikipedia_data_path: str, workers=4) -> list[WikiPage]:
        read_time = timer()
        data = self.get_pages(wikipedia_data_path)
        logging.info(f'Read {len(data)} pages in {timer() - read_time:.2f}s')
        space = np.linspace(0, len(data), workers + 1, dtype=int)
        results = []
        start_time = timer()
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = set()
            for i in range(workers):
                future = executor.submit(self.parse, data[space[i]:space[i + 1]])
                logging.info(f"Starting worker {future}")
                futures.add(future)
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logging.error(f"{future} generated an exception: {e}")
                logging.error(traceback.format_exc())
            else:
                logging.info(f"Joining worker {future}")
        result = list(itertools.chain.from_iterable(x[0] for x in results))
        logging.info(f"Parsed {len(result)} pages in {timer() - start_time:.2f}s")
        self.merge_stats(results)
        return results

    def merge_stats(self, results: list[tuple[list[WikiPage], dict[Union[int, list, defaultdict]]]]):
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    wiki_parser = WikiParser()
    results = wiki_parser.parse_wiki('../data/sk_wikipedia_dump_small_1m.xml', workers=4)
    pass
