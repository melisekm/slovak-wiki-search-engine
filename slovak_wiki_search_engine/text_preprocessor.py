import ast
import itertools
import logging
import re
from abc import ABC

import gensim
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

    # @calculate_stats(name="Stop words remover")
    def process(self, document: WikiPage):
        document.terms = [word for word in document.terms if word not in self.stop_words_list and len(word) > 1]


class Tokenizer(PreprocessorComponent):
    def __init__(self):
        self.deacc = REMOVE_ACCENTS

    def process(self, document: WikiPage):
        document.terms = gensim.utils.simple_preprocess(
            document.terms, deacc=self.deacc
        )  # deacc=True removes accents


class Lemmatizer(PreprocessorComponent):
    def __init__(self):
        self.allowed_postags = DEFAULT_ALLOWED_POSTAGS
        self.lemmatizer = spacy_udpipe.load("sk")

    # @calculate_stats(name="Lemmatization")
    def process(self, document: WikiPage):
        doc = self.lemmatizer(" ".join(document.terms))
        document.terms = [
            CUSTOM_WORDS[token.lemma_] if token.lemma_ in CUSTOM_WORDS else token.lemma_
            for token in doc
            if token.pos_ in self.allowed_postags and len(token.lemma_) > 1
        ]


class DocumentSaver(PreprocessorComponent):
    def __init__(self, already_processed_path: str):
        self.already_processed_path = already_processed_path

    def process(self, document: WikiPage):
        pd.DataFrame([[document.doc_id, document.title, document.terms]]).to_csv(
            self.already_processed_path, index=False, header=False, mode='a', encoding='utf-8'
        )


class TextPreprocessor:
    def __init__(self, component_names: list[str], conf: dict[str, object]):
        self.component_names = component_names
        self.already_processed_path = conf.get('already_processed_path')
        self.docs = utils.load_or_create_csv(
            self.already_processed_path, ['doc_id', 'title', 'terms']
        ).set_index('title')['terms'].to_dict()
        self.conf = conf
        if 'lemmatize' in component_names:
            spacy_udpipe.download("sk")

    def init_components(self) -> dict[str, PreprocessorComponent]:
        components = {}
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
            components['document_saver'] = DocumentSaver(self.already_processed_path)
        return components

    def _preprocess(self, documents: list[WikiPage], pbar_position=0):
        logger.info(f"Preprocessing {len(documents)} documents.")
        components = self.init_components()

        for document in tqdm(documents, desc=f"{pbar_position}", position=pbar_position, leave=False):
            if document.title in self.docs:
                document.terms = ast.literal_eval(self.docs[document.title])
            else:
                for name, component in components.items():
                    component.process(document)
        return documents

    def preprocess(self, documents: list[WikiPage], workers=4) -> list[WikiPage]:
        preprocessed_documents = utils.generic_parallel_execution(
            documents, self._preprocess, workers=workers, executor='process'
        )
        return list(itertools.chain.from_iterable(preprocessed_documents))
