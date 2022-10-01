import logging
import re

import spacy_udpipe
from abc import ABC

import gensim
from tqdm import tqdm

import unicodedata

from utils import get_file_path, calculate_stats
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

    @calculate_stats(name="Stop words remover")
    def process(self, document: WikiPage):
        with open(self.stop_words_path, encoding="UTF-8") as stopwords_file:
            stop_words_list = [line.strip() for line in stopwords_file]
        document.terms = [word for word in document.terms if word not in stop_words_list and len(word) > 1]


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
        spacy_udpipe.download("sk")
        self.lemmatizer = spacy_udpipe.load("sk")

        self.stats = {}

    @calculate_stats(name="Lemmatization")
    def process(self, document: WikiPage):
        doc = self.lemmatizer(" ".join(document.terms))
        document.terms = [
            CUSTOM_WORDS[token.lemma_] if token.lemma_ in CUSTOM_WORDS else token.lemma_
            for token in doc
            if token.pos_ in self.allowed_postags
        ]


class TextPreprocessor:
    def __init__(self, component_names: list[str], conf: dict[str, str]):
        self.component_names = component_names
        self.components = self.init_components(conf)

    def init_components(self, conf: dict[str, str]) -> list[PreprocessorComponent]:
        components = []
        if 'normalize' in self.component_names:
            components.append(Normalizer())
        if 'tokenize' in self.component_names:
            components.append(Tokenizer())
        if 'remove_stopwords' in self.component_names:
            components.append(StopWordsRemover(conf.get('stop_words_path')))
        if 'lemmatize' in self.component_names:
            components.append(Lemmatizer())
        if 'stop_words_cleaner' in self.component_names:
            # after lemmatize we want to remove stop words again
            components.append(StopWordsRemover(conf.get('stop_words_path')))
        return components

    def preprocess(self, documents: list[WikiPage]):
        logger.info(f"Preprocessing {len(documents)} documents.")
        for component in tqdm(self.components):
            for document in tqdm(documents, desc=component.__class__.__name__):
                component.process(document)
