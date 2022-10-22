import ast
import itertools
import logging
import multiprocessing
import re
import sys
from abc import ABC
from typing import Union

import pandas as pd
import spacy_udpipe
import unicodedata
from tqdm import tqdm

import utils
from utils import get_file_path
from wiki_parser import WikiPage

logger = logging.getLogger(__name__)

DEFAULT_NORMALIZATION_METHOD = "NFKC"
DEFAULT_ALLOWED_POSTAGS = ["NOUN", "ADJ", "VERB", "ADV"]
CUSTOM_WORDS = {
    'eý': 'eú',
    'urť': 'url',
    'adries': 'adresa',
}
REMOVE_ACCENTS = False


class PreprocessorComponent(ABC):
    def process(self, document: WikiPage):
        raise NotImplementedError


class Normalizer(PreprocessorComponent):
    def __init__(self):
        self.normalization_type = DEFAULT_NORMALIZATION_METHOD

    def process(self, document: WikiPage):
        # Remove new lines from texts
        # raw_data = [text.replace("\n", " ") for text in raw_data] # lepsia metoda?
        normalized_data = re.sub('\s+', ' ', document.raw_text)

        # Remove whitespace unicode characters
        normalized_data = re.sub(u'\u200b', ' ', normalized_data)

        # Remove URLS
        normalized_data = re.sub(r'http\S+', '', normalized_data)

        # Normalize text
        normalized_data = unicodedata.normalize(self.normalization_type, normalized_data)

        document.terms = normalized_data


class StopWordsRemover(PreprocessorComponent):
    def __init__(self, stop_words_path: str):
        self.stop_words_path = get_file_path(stop_words_path)
        with open(self.stop_words_path, encoding="UTF-8") as stopwords_file:
            self.stop_words_list = [line.strip() for line in stopwords_file]

    def process(self, document: WikiPage):
        document.terms = [word for word in document.terms if word not in self.stop_words_list and len(word) > 1]


class Tokenizer(PreprocessorComponent):
    def __init__(self):
        self.deacc = REMOVE_ACCENTS
        self.pat = re.compile(r'(((?![\d])\w)+)', re.UNICODE)
        self.min_len = 2
        self.max_len = 15

    def _tokenize(self, text: str):
        text = text.lower()
        for match in self.pat.finditer(text):
            yield match.group()

    def process(self, document: WikiPage):
        document.terms = [
            token for token in self._tokenize(document.terms) if
            self.min_len <= len(token) <= self.max_len and not token.startswith('_')
        ]


class Lemmatizer(PreprocessorComponent):
    def __init__(self):
        self.allowed_postags = DEFAULT_ALLOWED_POSTAGS
        self.lemmatizer = spacy_udpipe.load("sk")

    def process(self, document: WikiPage):
        doc = self.lemmatizer(" ".join(document.terms))
        document.terms = [
            CUSTOM_WORDS[token.lemma_] if token.lemma_ in CUSTOM_WORDS else token.lemma_
            for token in doc
            if token.pos_ in self.allowed_postags and len(token.lemma_) > 1
        ]


class DocumentSaver(PreprocessorComponent):
    def __init__(self, already_processed_path: str, lock: multiprocessing.Lock):
        self.already_processed_path = already_processed_path
        self.lock = lock

    def process(self, document: WikiPage):
        with self.lock:
            pd.DataFrame([[document.doc_id, document.title, document.terms]]).to_csv(
                self.already_processed_path, index=False, header=False, mode='a', encoding='utf-8'
            )


class TextPreprocessor:
    def __init__(self, component_names: list[str], conf: dict[str, Union[str, int, list[str]]], load_docs=True):
        self.component_names = component_names
        self.already_processed_path = conf.get('already_processed_path')
        self.docs = set() if not load_docs else utils.load_or_create_csv(
            self.already_processed_path, ['doc_id', 'title', 'terms']
        ).set_index('title')['terms'].to_dict()
        self.conf = conf
        if 'lemmatize' in component_names:
            spacy_udpipe.download("sk")
        self.lock = multiprocessing.Manager().Lock()

    def init_components(self) -> dict[str, PreprocessorComponent]:
        components: dict[str, PreprocessorComponent] = {}
        if 'normalize' in self.component_names:
            components['normalizer'] = Normalizer()
        if 'tokenize' in self.component_names:
            components['tokenizer'] = Tokenizer()
        if 'remove_stopwords' in self.component_names:
            components['stopwords_remover'] = StopWordsRemover(self.conf.get('stop_words_path'))
        if 'lemmatize' in self.component_names:
            components['lemmatizer'] = Lemmatizer()
        if 'stop_words_cleaner' in self.component_names:
            # after lemmatize we want to remove stop words again
            components['stopwords_cleaner'] = StopWordsRemover(self.conf.get('stop_words_path'))
        if 'document_saver' in self.component_names:
            components['document_saver'] = DocumentSaver(self.already_processed_path, self.lock)
        return components

    def _preprocess(self, documents: list[WikiPage], pbar_position=0):
        logger.info(f"Preprocessing {len(documents)} documents.")
        components = self.init_components()

        for document in tqdm(documents, desc=f"{pbar_position}", position=pbar_position, leave=False):
            for name, component in components.items():
                component.process(document)
            document.raw_text = None
            # document.terms = None
        return documents

    def preprocess(self, documents: list[WikiPage], workers=4, query=False) -> list[WikiPage]:
        if query:
            return self._preprocess(documents)
        already_parsed = set()
        for document in tqdm(documents, desc="Reading already processed documents", position=0, leave=False):
            if document.title in self.docs:
                document.terms = ast.literal_eval(self.docs[document.title])
                document.raw_text = None
                already_parsed.add(document)

        to_parse = list(set(documents) - already_parsed)
        logger.info(f"Already parsed {len(already_parsed)} documents.")
        logger.info(f"Need to parse {len(to_parse)} documents.")
        if workers == 1 or len(to_parse) < 100:
            return self._preprocess(to_parse) + list(already_parsed)

        preprocessed_documents = utils.generic_parallel_execution(
            to_parse, self._preprocess, workers=workers, executor='process'
        )
        preprocessed_documents = list(itertools.chain.from_iterable(preprocessed_documents))
        preprocessed_documents.extend(already_parsed)
        return preprocessed_documents
