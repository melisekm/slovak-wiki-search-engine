import os
import sys
import utils
from arg_parser import ArgParser
from indexer import InvertedIndex
from search_engine import SearchEngine


if __name__ == '__main__':
    utils.setup_logging()
    arg_parser = ArgParser()
    arg_parser.parse(sys.argv)
    arg_parser.validate_params()
    params = arg_parser.get_params()

    conf = utils.get_conf('drive/conf.json')
    inverted_index_path = conf.get('inverted_index_path')
    preprocessor_components = conf.get('preprocessor_components')
    workers = conf.get('workers')

    inverted_index = InvertedIndex()
    if os.path.exists(inverted_index_path):
        load(inverted_index_path)
    else:
        inverted_index.create(conf, workers)

    search_engine = SearchEngine(inverted_index, conf, **params)
    results = search_engine.search()

    utils.format_results(results)
