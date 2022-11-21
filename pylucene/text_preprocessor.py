import re
from abc import ABC

import spacy_udpipe
import unicodedata

DEFAULT_NORMALIZATION_METHOD = "NFKC"
DEFAULT_ALLOWED_POSTAGS = ["NOUN", "ADJ", "VERB", "ADV"]
REMOVE_ACCENTS = False


class PreprocessorComponent(ABC):
    def process(self, query):
        raise NotImplementedError


class Normalizer(PreprocessorComponent):
    def __init__(self):
        self.normalization_type = DEFAULT_NORMALIZATION_METHOD

    def process(self, query):
        # Remove new lines from texts
        # raw_data = [text.replace("\n", " ") for text in raw_data] # lepsia metoda?
        normalized_data = re.sub('\s+', ' ', query)

        # Remove whitespace unicode characters
        normalized_data = re.sub(u'\u200b', ' ', normalized_data)

        # Remove URLS
        normalized_data = re.sub(r'http\S+', '', normalized_data)

        # Normalize text
        normalized_data = unicodedata.normalize(self.normalization_type, normalized_data)

        return normalized_data


class StopWordsRemover(PreprocessorComponent):
    def __init__(self, stopwords):
        self.stop_words_list = stopwords

    def process(self, query):
        return [word for word in query if word not in self.stop_words_list and len(word) > 1]


class Tokenizer(PreprocessorComponent):
    def __init__(self):
        self.deacc = REMOVE_ACCENTS
        self.pat = re.compile(r'(((?![\d])\w)+)', re.UNICODE)
        self.min_len = 2
        self.max_len = 15

    def _tokenize(self, text):
        text = text.lower()
        for match in self.pat.finditer(text):
            yield match.group()

    def process(self, query):
        return [
            token for token in self._tokenize(query) if
            self.min_len <= len(token) <= self.max_len and not token.startswith('_')
        ]


class Lemmatizer(PreprocessorComponent):
    def __init__(self):
        self.allowed_postags = DEFAULT_ALLOWED_POSTAGS
        self.lemmatizer = spacy_udpipe.load("sk")

    def process(self, query):
        doc = self.lemmatizer(" ".join(query))
        return [
            token.lemma_
            for token in doc
            if token.pos_ in self.allowed_postags and len(token.lemma_) > 1
        ]


class TextPreprocessor:
    def __init__(self, component_names, stopwords):
        self.stopwords = stopwords
        self.component_names = component_names
        if 'lemmatize' in self.component_names:
            spacy_udpipe.download("sk")
        self.components = self.init_components()

    def init_components(self):
        components = {}
        if 'normalize' in self.component_names:
            components['normalizer'] = Normalizer()
        if 'tokenize' in self.component_names:
            components['tokenizer'] = Tokenizer()
        if 'remove_stopwords' in self.component_names:
            components['stopwords_remover'] = StopWordsRemover(self.stopwords)
        if 'lemmatize' in self.component_names:
            components['lemmatizer'] = Lemmatizer()
        if 'stop_words_cleaner' in self.component_names:
            # after lemmatize we want to remove stop words again
            components['stopwords_cleaner'] = StopWordsRemover(self.stopwords)
        return components

    def preprocess(self, query):
        print(f"Preprocessing query: {query}")
        for name, component in self.components.items():
            query = component.process(query)
            print(f"Running {name}..." + f" Result: {query}")
        return query
