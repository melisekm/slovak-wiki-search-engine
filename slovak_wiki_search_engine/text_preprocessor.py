from abc import ABC

from wiki_parser import WikiPage


class PreprocessorComponent(ABC):
    def process(self, document: WikiPage):
        raise NotImplementedError


class Normalizer(PreprocessorComponent):
    def __init__(self):
        pass

    def process(self, document: WikiPage):
        pass


class Lemmatizer(PreprocessorComponent):
    def __init__(self):
        pass

    def process(self, document: WikiPage):
        pass


class StopWordsRemover(PreprocessorComponent):
    def __init__(self):
        pass

    def process(self, document: WikiPage):
        pass


class Tokenizer(PreprocessorComponent):
    def __init__(self):
        pass

    def process(self, document: WikiPage):
        pass


class TextPreprocessor:
    def __init__(self, component_names: list[str]):
        self.component_names = component_names
        self.components = self.init_components()

    def init_components(self) -> list[PreprocessorComponent]:
        components = []
        if 'normalize' in self.component_names:
            components.append(Normalizer())
        if 'tokenize' in self.component_names:
            components.append(Tokenizer())
        if 'remove_stopwords' in self.component_names:
            components.append(StopWordsRemover())
        if 'lemmatize' in self.component_names:
            components.append(Lemmatizer())
        return components

    def preprocess(self, documents: list[WikiPage]):
        for document in documents:
            for component in self.components:
                component.process(document)
