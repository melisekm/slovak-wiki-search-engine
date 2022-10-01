import os
import unittest

import utils
import indexer
from text_preprocessor import TextPreprocessor
from wiki_parser import WikiParser


def mock(wikipedia_data_path):
    workers = 6

    wiki_parser = WikiParser()
    parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

    conf = utils.DEFAULT_CONF
    preprocessor_components = conf['preprocessor_components']

    text_preprocessor = TextPreprocessor(preprocessor_components, conf)
    return text_preprocessor.preprocess(parsed_documents, workers)


class TestIndexer(unittest.TestCase):
    def test_parser_and_preprocess(self):
        parsed_documents = mock('../data/sk_wikipedia_dump_small_100k.xml')
        main_page = next((page for page in parsed_documents if page.title == 'Hlavná stránka'), None)
        self.assertIsNotNone(main_page)
        self.assertEqual(main_page.doc_id, 0)
        self.assertEqual(main_page.title, 'Hlavná stránka')
        self.assertEqual(len(parsed_documents), 1213)

    def test_indexer(self):
        conf = utils.DEFAULT_CONF
        conf['sk_wikipedia_dump_path'] = '../data/sk_wikipedia_dump_small_100k.xml'
        inverted_index_path = conf.get('inverted_index_path')
        workers = 4

        inverted_index = indexer.InvertedIndex()
        if os.path.exists(inverted_index_path):
            inverted_index.load(inverted_index_path)
        else:
            inverted_index.create(conf, workers)


if __name__ == '__main__':
    unittest.main()
