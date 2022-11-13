import json
import re
from abc import ABC

import spacy_udpipe
import unicodedata

DEFAULT_NORMALIZATION_METHOD = "NFKC"
DEFAULT_ALLOWED_POSTAGS = ["NOUN", "ADJ", "VERB", "ADV"]
REMOVE_ACCENTS = False


class PreprocessorComponent(ABC):
    def process(self, document):
        raise NotImplementedError


class Normalizer(PreprocessorComponent):
    def __init__(self):
        self.normalization_type = DEFAULT_NORMALIZATION_METHOD

    def process(self, document):
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
    def __init__(self, stopwords):
        self.stop_words_list = stopwords

    def process(self, document):
        document.terms = [word for word in document.terms if word not in self.stop_words_list and len(word) > 1]


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

    def process(self, document):
        document.terms = [
            token for token in self._tokenize(document.terms) if
            self.min_len <= len(token) <= self.max_len and not token.startswith('_')
        ]


class Lemmatizer(PreprocessorComponent):
    def __init__(self):
        self.allowed_postags = DEFAULT_ALLOWED_POSTAGS
        self.lemmatizer = spacy_udpipe.load("sk")

    def process(self, document):
        doc = self.lemmatizer(" ".join(document.terms))
        document.terms = [
            token.lemma_
            for token in doc
            if token.pos_ in self.allowed_postags and len(token.lemma_) > 1
        ]


class TextPreprocessor:
    def __init__(self, preprocessor_components, stopwords):
        self.component_names = preprocessor_components
        self.stopwords = stopwords
        if 'lemmatize' in self.component_names:
            spacy_udpipe.download("sk")
        self.components = self.init_components()

    def init_components(self):
        components: dict[str, PreprocessorComponent] = {}
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

    def preprocess(self, document):
        for name, component in self.components.items():
            component.process(document)
        return document


def load():
    with open('conf.json', 'r') as conf_file:
        conf = json.load(conf_file)
    with open(conf["stop_words_path"], encoding="UTF-8") as stopwords_file:
        stop_words_list = [line.strip() for line in stopwords_file]
    return TextPreprocessor(conf.get("preprocessor_components"), stop_words_list)


text_processor = load()
