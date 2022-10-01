import os
import sys
import utils
from arg_parser import ArgParser
from indexer import InvertedIndex
from search_engine import SearchEngine

if __name__ == '__main__':
    arg_parser = ArgParser()
    arg_parser.parse(sys.argv)
    arg_parser.validate_params()
    params = arg_parser.get_params()

    conf = utils.get_conf('drive/conf.json')
    inverted_index_path = conf.get('inverted_index_path')
    wikipedia_path = conf.get('sk_wikipedia_dump_small_100k_path')
    preprocessor_components = conf.get('preprocessor_components')
    workers = conf.get('workers')

    inverted_index = InvertedIndex()
    if os.path.exists(inverted_index_path):
        inverted_index.load(inverted_index_path)
    else:
        inverted_index.create(wikipedia_path, inverted_index_path, preprocessor_components, workers)

    search_engine = SearchEngine(inverted_index, params)
    results = search_engine.get_results()

    utils.format_results(results)
