import json
import os

CONF_FILE_PATH = 'drive/conf.json'
DEFAULT_CONF = {
    'inverted_index_path': 'data/inverted_index.pickle',
    'sk_wikipedia_dump_small_1m_path': 'data/sk_wikipedia_dump_small_1m.xml',  # 14k pages
    'sk_wikipedia_dump_small_100k_path': 'data/sk_wikipedia_dump_small_100k.xml',  # 1213 pages
    'sk_wikipedia_dump_small_full_path': 'data/sk_wikipedia_dump_small_full.xml'  # 240k pages
}


def get_conf(conf_file_path):
    if not os.path.exists(conf_file_path):
        os.makedirs(os.path.dirname(conf_file_path), exist_ok=True)
        with open(conf_file_path, 'w') as conf_file:
            json.dump(DEFAULT_CONF, conf_file)
        return DEFAULT_CONF
    with open(conf_file_path, 'r') as conf_file:
        conf = json.load(conf_file)
    for default_key in DEFAULT_CONF.keys():
        if default_key not in conf:
            conf[default_key] = DEFAULT_CONF[default_key]
    return conf


def format_results(results):
    pass
