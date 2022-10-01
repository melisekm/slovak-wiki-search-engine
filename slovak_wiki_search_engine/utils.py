import json
import logging
import os
import timeit
import traceback
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from timeit import default_timer as timer

import wiki_parser

logger = logging.getLogger(__name__)

CONF_FILE_PATH = 'drive/conf.json'
DEFAULT_CONF = {
    'inverted_index_path': 'data/inverted_index.pickle',
    'sk_wikipedia_dump_path': 'data/sk_wikipedia_dump_small_1m.xml',
    'stop_words_path': 'data/SK_stopwords.txt',
}


def setup_logging(verbose=True):
    log_handlers = [logging.StreamHandler()]
    formatter = logging.Formatter(fmt='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(filename)s]: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S')
    for handler in log_handlers:
        handler.setFormatter(formatter)
    if not verbose:
        for handler in log_handlers:
            handler.setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.DEBUG, handlers=log_handlers)
    logging.root.handlers = log_handlers


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


def get_file_path(file_path):
    if file_path is None:
        raise Exception(f"File path is None.")
    path = Path(file_path)
    if path.is_file():
        return file_path
    else:
        raise FileNotFoundError(f"File {file_path} not found")


def generic_parallel_execution(data, space, func, workers=4, executor='process', *args, **kwargs):
    if executor == 'process':
        executor_type = ProcessPoolExecutor
    elif executor == 'thread':
        executor_type = ThreadPoolExecutor
    else:
        raise Exception(f"Executor {executor} not supported")

    results = []
    start_time = timer()
    with executor_type(max_workers=workers) as executor:
        futures = set()
        for i in range(workers):
            future = executor.submit(func, data[space[i]:space[i + 1]], *args, **kwargs)
            logger.info(f"Starting worker {future}")
            futures.add(future)
    for future in as_completed(futures):
        try:
            results.append(future.result())
        except Exception as e:
            logger.error(f"{future} generated an exception: {e}")
            logger.error(traceback.format_exc())
        else:
            logger.info(f"Joining worker {future}")
    end_time = timer()
    logger.info(f"Runtime time: {end_time - start_time:.2f}s")
    return results


def calculate_stats(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if type(args[1]) == wiki_parser.WikiPage:
                document = args[1]
            else:
                raise Exception(f"Function {func.__name__} is not supported for {type(args[0])}")

            total_words = len(document.terms)
            start_time = timeit.default_timer()
            result = func(*args, **kwargs)
            elapsed_time = timeit.default_timer() - start_time
            logger.info(f"{name} took {elapsed_time:.2f} seconds")

            total_words_new = len(document.terms)
            new_words_ratio = 1 - (total_words_new / total_words)
            new_words_percentage = round(new_words_ratio * 100, 2)

            logger.info(f"Total words before: {total_words}")
            logger.info(f"Total words after: {total_words_new}")
            logger.info(f"Removed {new_words_percentage}% of words from documents.")

            return result

        return wrapper

    return decorator


def format_results(results):
    pass
