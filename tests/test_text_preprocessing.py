import os

from slovak_wiki_search_engine import utils
from tests import DEFAULT_TEST_CONF
import unittest

from text_preprocessor import Normalizer, StopWordsRemover, Tokenizer, Lemmatizer, TextPreprocessor
from wiki_parser import WikiPage, WikiParser

utils.setup_logging(verbose=False)


class TestTextPreprocessing(unittest.TestCase):
    def test_normalizer(self):
        normalizer = Normalizer()
        document = WikiPage(-1, 'Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer.process(document)
        self.assertEqual(document.terms, 'Toto je test na odstranenie novych riadkov a URL adries. ')

    def test_tokenizer(self):
        document = WikiPage(-1, 'Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        # words of length less than 2 are removed
        self.assertEqual(document.terms,
                         ['toto', 'je', 'test', 'na', 'odstranenie', 'novych', 'riadkov', 'url', 'adries'])

    def test_stop_words_remover(self):
        document = WikiPage(-1, 'Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        stop_words_remover = StopWordsRemover('data/SK_stopwords.txt')
        stop_words_remover.process(document)
        self.assertEqual(document.terms, ['test', 'odstranenie', 'novych', 'riadkov', 'url', 'adries'])

    def test_lemmatizer(self):
        document = WikiPage(-1, 'Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        stop_words_remover = StopWordsRemover('data/SK_stopwords.txt')
        stop_words_remover.process(document)
        lemmatizer = Lemmatizer()
        lemmatizer.process(document)
        self.assertEqual(document.terms, ['test', 'odstranenie', 'novy', 'riadok', 'url', 'adresa'])

    def test_text_preprocessor(self):
        document = WikiPage(-1, 'Test',
                            'Nezvyčajné kŕdle šťastných figliarskych vtákov '
                            'učia pri kótovanom Váhu mĺkveho koňa Waldemara '
                            'obžierať väčšie kusy exkluzívnej kôry s quesadillou')

        conf = DEFAULT_TEST_CONF
        preprocessor_components = conf['preprocessor_components']
        if "document_saver" in preprocessor_components:
            preprocessor_components.remove("document_saver")

        parsed_documents = [document]
        text_preprocessor = TextPreprocessor(preprocessor_components, conf, load_docs=False)
        preprocessed_documents = text_preprocessor.preprocess(parsed_documents)
        self.assertEqual(preprocessed_documents[0].terms, [
            'nezvyčajný', 'kŕdlo', 'šťastný', 'figliarsky', 'vták', 'učiť', 'kótovaný', 'váha', 'mĺkvy', 'kôň',
            'obžierať', 'veľký', 'kus', 'exkluzívný', 'kôra', 'quesadilla'
        ])

    def test_parser_and_preprocess(self):
        wikipedia_data_path = 'data/sk_wikipedia_dump_small_100k.xml'
        workers = 6
        if not os.path.exists(wikipedia_data_path):
            self.skipTest('sk_wikipedia_dump_path does not exist. Skipping test.')

        wiki_parser = WikiParser()
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

        conf = DEFAULT_TEST_CONF
        preprocessor_components = conf['preprocessor_components']

        text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        parsed_documents = text_preprocessor.preprocess(parsed_documents, workers)

        main_page = next((page for page in parsed_documents if page.title == 'Hlavná stránka'), None)
        self.assertIsNotNone(main_page)
        self.assertEqual(main_page.doc_id, 0)
        self.assertEqual(main_page.title, 'Hlavná stránka')
        self.assertEqual(len(parsed_documents), 1105)
