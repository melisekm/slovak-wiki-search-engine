import os
import unittest
import indexer
import utils
from arg_parser import QueryBooleanOperator
from search_engine import SearchEngine

utils.setup_logging()


class TestSearchEngine(unittest.TestCase):
    def test_search_engine(self):
        conf = utils.DEFAULT_CONF
        conf['sk_wikipedia_dump_path'] = '../data/sk_wikipedia_dump_small_100k.xml'
        inverted_index_path = conf.get('inverted_index_path')
        workers = 6

        if os.path.exists(inverted_index_path):
            inverted_index = indexer.load(inverted_index_path)
        else:
            inverted_index = indexer.InvertedIndex()
            inverted_index.create(conf, workers)

        params = {
            'query': 'prezident Slovensko',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 30,
            'relevant_documents_count': 100,
        }

        search_engine = SearchEngine(inverted_index, conf, **params)
        results = search_engine.search()
        utils.format_results(results)


if __name__ == '__main__':
    unittest.main()
