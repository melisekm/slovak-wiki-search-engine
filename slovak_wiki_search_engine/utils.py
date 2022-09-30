import json
import os

CONF_FILE_PATH = 'drive/conf.json'
DEFAULT_CONF = {
    'inverted_index_path': 'data/inverted_index.pickle',
    'wikipedia_dump_small_path': 'data/wikipedia_dump_small.xml',
    'wikipedia_dump_full_path': 'data/wikipedia_dump.xml'
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
