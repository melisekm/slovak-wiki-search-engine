import unittest
import utils

from wiki_parser import WikiParser

utils.setup_logging(verbose=False)


class TestWikiParser(unittest.TestCase):

    def test_counts(self):
        wiki_parser = WikiParser()
        wikipedia_data_path = 'data/sk_wikipedia_dump_small_1m.xml'
        workers = 4
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)
        self.assertEqual(len(parsed_documents), 14108)
        self.assertEqual(wiki_parser.stats['pages'], 14108)
        self.assertEqual(wiki_parser.stats['parsed_pages'], 14108)
        self.assertEqual(len(wiki_parser.stats['pages_with_infobox']), 2877)
        self.assertEqual(len(wiki_parser.stats['infobox_types']), 108)
