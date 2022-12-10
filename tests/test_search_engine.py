import os
import unittest

from slovak_wiki_search_engine import utils, indexer, QueryBooleanOperator, SearchEngine
from tests import DEFAULT_TEST_CONF

utils.setup_logging()


class TestSearchEngine(unittest.TestCase):
    def test_search_engine(self):
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

        params = {
            'query': 'Kto je prezidentom Ruskej federácie?',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 30,
            'relevant_documents_count': 100,
        }

        search_engine = SearchEngine(inverted_index, conf)
        results = search_engine.search(params['query'], params['boolean_operator'], params['results_count'])

        self.assertEqual(len(results), 30)
        self.assertIn('Rusko', [result[0].title for result in results])
        self.assertIn('Vladimir Vladimirovič Putin', [result[0].title for result in results])


if __name__ == '__main__':
    unittest.main()
