import os
import sys
# insert to sys path slovak_wiki_search_engine directory
sys.path.insert(0, 'slovak_wiki_search_engine')
sys.path.insert(0, 'data')
DEFAULT_TEST_CONF = {
    'inverted_index_path': 'data/inverted_index_1m.pickle',
    'sk_wikipedia_dump_path': 'data/sk_wikipedia_dump_small_1m.xml',
    'stop_words_path': 'data/SK_stopwords.txt',
    'already_processed_path': 'data/already_parsed.csv',
    "preprocessor_components": [
        "normalize",
        "tokenize",
        "remove_stopwords",
        "lemmatize",
        "stop_words_cleaner",
        "document_saver"
    ],
    "workers": 6,
    "verbose": True
}
