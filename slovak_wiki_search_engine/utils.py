import json
import logging
import os
import timeit
import traceback
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor
from os.path import exists
from pathlib import Path
from timeit import default_timer as timer

import numpy as np
import pandas as pd

import wiki_parser

logger = logging.getLogger(__name__)

DEFAULT_CONF = {
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
    "workers": 4,
    "verbose": True
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
            json.dump(DEFAULT_CONF, conf_file, indent=4)
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


def load_or_create_csv(name: str, column_names: list[str]) -> pd.DataFrame:
    if exists(name):
        df = pd.read_csv(name, encoding='utf-8')
    else:
        df = pd.DataFrame(columns=column_names)
        df.to_csv(name, index=False)
    return df


def generic_parallel_execution(data, func, *args, workers=4, executor='process', **kwargs):
    if executor == 'process':
        executor_type = ProcessPoolExecutor
    elif executor == 'thread':
        executor_type = ThreadPoolExecutor
    else:
        raise Exception(f"Executor {executor} not supported")

    space = np.linspace(0, len(data), workers + 1, dtype=int)
    results = []
    start_time = timer()
    with executor_type(max_workers=workers) as executor:
        futures = set()
        for i in range(workers):
            kwargs['pbar_position'] = i
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


def cosine_similarity(query: 'wiki_parser.WikiPage',
                      relevant_docs: list['wiki_parser.WikiPage']) -> list[tuple['wiki_parser.WikiPage', float]]:
    score_map = {}
    for doc in relevant_docs:
        score = 0.0
        for token in query.terms:
            token_id = query.terms.index(token)
            try:
                doc_token_id = doc.terms.index(token)
                doc_token_vector_val = doc.vector[doc_token_id]
            except ValueError:
                doc_token_vector_val = 0
            score += query.vector[token_id] * doc_token_vector_val
        score_map[doc] = score
        doc.terms = None
    return sorted(score_map.items(), key=lambda x: x[1], reverse=True)


def format_results(results: list[tuple['wiki_parser.WikiPage', float]]):
    results = results[::-1]
    for idx, result in enumerate(results):
        document = result[0]
        score = result[1]
        idx = len(results) - idx
        logger.info(f"Result {idx}: {document.title} - {score}")
        logger.info(f"URL: https://sk.wikipedia.org/wiki/{document.title.replace(' ', '_')}")
        if document.infobox_title:
            logger.info(f"Category: {document.infobox_title}")
        logger.info("-" * 100)
    prompt = "\nEnter result number to learn more about the document which has a Category. [Q] to go back.: "
    msg = "-" * 100 + prompt
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
