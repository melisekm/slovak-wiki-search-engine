import unittest

import utils
from text_preprocessor import TextPreprocessor
from wiki_parser import WikiParser


class TestParserPreprocess(unittest.TestCase):
    def test_parser_and_preprocess(self):
        wikipedia_data_path = '../data/sk_wikipedia_dump_small_100k.xml'
        workers = 6

        wiki_parser = WikiParser()
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

        conf = utils.DEFAULT_CONF
        preprocessor_components = conf['preprocessor_components']

        text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        text_preprocessor.preprocess(parsed_documents, workers)

        main_page = next((page for page in parsed_documents if page.title == 'Hlavná stránka'), None)
        self.assertIsNotNone(main_page)
        self.assertEqual(main_page.doc_id, 0)
        self.assertEqual(main_page.title, 'Hlavná stránka')
        self.assertEqual(len(parsed_documents), 1213)


if __name__ == '__main__':
    unittest.main()
