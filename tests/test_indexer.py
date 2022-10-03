import os
import unittest
import tests

import utils
import indexer

utils.setup_logging()


class TestIndexer(unittest.TestCase):
    def test_indexer(self):
        conf = utils.DEFAULT_CONF
        conf['sk_wikipedia_dump_path'] = 'data/sk_wikipedia_dump_small_100k.xml'
        inverted_index_path = 'data/inverted_index_100k.pickle'
        workers = 6

        if os.path.exists(inverted_index_path):
            inverted_index = indexer.load(inverted_index_path)
        else:
            inverted_index = indexer.InvertedIndex()
            inverted_index.create(conf, workers)

        self.assertEqual(64375, len(inverted_index._index))
        self.assertEqual(inverted_index.get('rusko').document_frequency, 58)
        self.assertEqual(inverted_index.get('prezident').document_frequency, 46)
        self.assertEqual(inverted_index.get('prezident').corpus_frequency, 191)
        self.assertEqual(inverted_index.get('súbor').corpus_frequency, 1549)


if __name__ == '__main__':
    unittest.main()
