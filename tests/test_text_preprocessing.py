import unittest
import utils
from text_preprocessor import Normalizer, StopWordsRemover, Tokenizer, Lemmatizer, TextPreprocessor
from wiki_parser import WikiPage

utils.setup_logging(verbose=False)


class TestTextPreprocessing(unittest.TestCase):
    def test_normalizer(self):
        normalizer = Normalizer()
        document = WikiPage('Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer.process(document)
        self.assertEqual(document.terms, 'Toto je test na odstranenie novych riadkov a URL adries. ')

    def test_tokenizer(self):
        document = WikiPage('Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        # words of length less than 2 are removed
        self.assertEqual(document.terms,
                         ['toto', 'je', 'test', 'na', 'odstranenie', 'novych', 'riadkov', 'url', 'adries'])

    def test_stop_words_remover(self):
        document = WikiPage('Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        stop_words_remover = StopWordsRemover('../data/SK_stopwords.txt')
        stop_words_remover.process(document)
        self.assertEqual(document.terms, ['test', 'odstranenie', 'novych', 'riadkov', 'url', 'adries'])

    def test_lemmatizer(self):
        document = WikiPage('Test',
                            'Toto je test na\n odstranenie novych riadkov a URL adries. https://www.google.com')
        normalizer = Normalizer()
        normalizer.process(document)
        tokenizer = Tokenizer()
        tokenizer.process(document)
        stop_words_remover = StopWordsRemover('../data/SK_stopwords.txt')
        stop_words_remover.process(document)
        lemmatizer = Lemmatizer()
        lemmatizer.process(document)
        self.assertEqual(document.terms, ['test', 'odstranenie', 'novy', 'riadok', 'url', 'adresa'])

    def test_text_preprocessor(self):
        document = WikiPage('Test',
                            'Nezvyčajné kŕdle šťastných figliarskych vtákov '
                            'učia pri kótovanom Váhu mĺkveho koňa Waldemara '
                            'obžierať väčšie kusy exkluzívnej kôry s quesadillou')

        document.doc_id = -1

        conf = utils.DEFAULT_CONF
        preprocessor_components = conf['preprocessor_components']
        # preprocessor_components.remove("document_saver")

        parsed_documents = [document]
        text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        text_preprocessor.preprocess(parsed_documents)
        self.assertEqual(document.terms, [
            'nezvyčajný', 'kŕdlo', 'šťastný', 'figliarsky', 'vták', 'učiť', 'kótovaný', 'váha', 'mĺkvy', 'kôň',
            'obžierať', 'veľký', 'kus', 'exkluzívný', 'kôra', 'quesadilla'
        ])
