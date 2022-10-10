import os

import slovak_wiki_search_engine as swse

if __name__ == '__main__':
    conf = swse.utils.get_conf('data/conf.json')
    inverted_index_path = conf.get('inverted_index_path')
    preprocessor_components = conf.get('preprocessor_components')
    workers = conf.get('workers')
    arg_parser = swse.arg_parser.ArgParser()

    if os.path.exists(inverted_index_path):
        inverted_index = swse.indexer.load(inverted_index_path)
    else:
        inverted_index = swse.indexer.InvertedIndex()
        inverted_index.create(conf, workers)

    search_engine = swse.search_engine.SearchEngine(inverted_index, conf)

    while True:
        args = input("Enter the program arguments. [Q] to quit: ")
        if args.lower() == "q":
            break
        params = arg_parser.parse(args)
        results = search_engine.search(params['query'], params['boolean_operator'], params['results_count'])
        swse.utils.format_results(results)
