import os
import unittest

from slovak_wiki_search_engine import indexer
from tests import DEFAULT_TEST_CONF


class TestIndexer(unittest.TestCase):
    def test_indexer(self):
        conf = DEFAULT_TEST_CONF
        conf['sk_wikipedia_dump_path'] = 'data/sk_wikipedia_dump_small_100k.xml'
        conf['inverted_index_path'] = 'data/inverted_index_100k.pickle'
        workers = 6

        if not os.path.exists(conf['sk_wikipedia_dump_path']):
            self.skipTest('sk_wikipedia_dump_path does not exist. Skipping test.')

        if os.path.exists(conf['inverted_index_path']):
            inverted_index = indexer.load(conf['inverted_index_path'])
        else:
            inverted_index = indexer.InvertedIndex()
            inverted_index.create(conf, workers)

        self.assertEqual(64367, len(inverted_index._index))
        self.assertEqual(inverted_index.get('rusko').document_frequency, 58)
        self.assertEqual(inverted_index.get('prezident').document_frequency, 46)
        self.assertEqual(inverted_index.get('prezident').corpus_frequency, 188)
        self.assertEqual(inverted_index.get('súbor').corpus_frequency, 1549)


if __name__ == '__main__':
    unittest.main()
