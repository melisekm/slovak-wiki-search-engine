import os
import re
import sys
from timeit import default_timer as timer

import slovak_wiki_search_engine as swse

if __name__ == '__main__':
    arg_parser = swse.arg_parser.ArgParser()
    arg_parser.parse(sys.argv)
    arg_parser.validate_params()
    params = arg_parser.get_params()

    conf = swse.utils.get_conf('data/conf.json')
    inverted_index_path = conf.get('inverted_index_path')
    preprocessor_components = conf.get('preprocessor_components')
    workers = conf.get('workers')

    if os.path.exists(inverted_index_path):
        inverted_index = swse.indexer.load(inverted_index_path)
    else:
        inverted_index = swse.indexer.InvertedIndex()
        inverted_index.create(conf, workers)

    search_engine = swse.search_engine.SearchEngine(inverted_index, conf, **params)
    start = timer()
    results = search_engine.search()[::-1]
    end = timer()

    swse.utils.format_results(results)
    print(f'Search time: {end - start:.2f}s')

    msg = """Enter result number to learn more about the document which has a Category. [Q] to exit.: """
    while True:
        try:
            num_to_show = input(msg)
            if num_to_show.lower() == 'q':
                break
            num_to_show = int(num_to_show)
        except ValueError:
            print('Invalid input.')
            continue
        if num_to_show > len(results) or num_to_show < 1:
            print('Invalid input.')
            continue
        result_to_show = results[len(results) - num_to_show][0]
        if result_to_show.infobox:
            print('\n'.join("{}: {}".format(k, v) for k, v in result_to_show.infobox.properties.items()))
        else:
            print('Please select result which has category.')
