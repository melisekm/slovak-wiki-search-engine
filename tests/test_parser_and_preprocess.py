import unittest


import utils
from text_preprocessor import TextPreprocessor
from wiki_parser import WikiParser


def run(parsed_documents, preprocessor_components, conf, pbar_position):
    text_preprocessor = TextPreprocessor(preprocessor_components, conf)
    text_preprocessor.preprocess(parsed_documents, pbar_position=pbar_position)


class TestParserPreprocess(unittest.TestCase):
    def test_parser_and_preprocess(self):
        wikipedia_data_path = '../data/sk_wikipedia_dump_small_100k.xml'
        workers = 6

        wiki_parser = WikiParser()
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

        conf = utils.DEFAULT_CONF
        preprocessor_components = conf['preprocessor_components']

        # text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        # text_preprocessor.preprocess(parsed_documents)
        utils.generic_parallel_execution(parsed_documents, run,
                                         preprocessor_components, conf,
                                         workers=workers, executor='process')

        # text_preprocessor.preprocess(parsed_documents)

        pass

if __name__ == '__main__':
    unittest.main()