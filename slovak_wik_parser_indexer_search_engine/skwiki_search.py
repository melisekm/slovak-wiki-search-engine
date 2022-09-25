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

    paths = utils.get_paths('drive/paths.json')

    inverted_index = InvertedIndex(paths)
    inverted_index.load()

    search_engine = SearchEngine(inverted_index, params)
    results = search_engine.get_results()

    utils.format_results(results)
