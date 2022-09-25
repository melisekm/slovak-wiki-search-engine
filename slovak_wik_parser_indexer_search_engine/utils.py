import json
import os

PATHS_FILE_PATH = 'drive/drive_paths.json'
DEFAULT_PATHS = {
    'data': 'data',
    'inverted_index': 'drive/inverted_index.pickle',
}


def get_paths(paths_file_path):
    if not os.path.exists(paths_file_path):
        os.makedirs(os.path.dirname(paths_file_path), exist_ok=True)
        with open(paths_file_path, 'w') as paths_file:
            json.dump(DEFAULT_PATHS, paths_file)
        return DEFAULT_PATHS
    with open(paths_file_path, 'r') as paths_file:
        paths = json.load(paths_file)
    for default_key in DEFAULT_PATHS.keys():
        if default_key not in paths:
            paths[default_key] = DEFAULT_PATHS[default_key]
    return paths


def format_results(results):
    pass
