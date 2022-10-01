import pickle
from typing import Optional

import vectorizer
from text_preprocessor import TextPreprocessor
from wiki_parser import WikiPage, WikiParser


class IndexRecord:
    def __init__(self, term: str):
        self.term = term
        self.document_frequency = 0
        self.corpus_frequency = 0
        self.documents: set[WikiPage] = set()

    def add_document(self, document: WikiPage):
        if document not in self.documents:
            self.document_frequency += 1
            self.documents.add(document)
        self.corpus_frequency += 1


class InvertedIndex:
    def __init__(self):
        self.inverted_index_path: Optional[str] = None
        self._index: dict[str, IndexRecord] = None

    def load(self, inverted_index_path: str):
        with open(inverted_index_path, 'rb') as inverted_index_file:
            self._index = pickle.load(inverted_index_file)
            self.inverted_index_path = inverted_index_path

    def save(self, inverted_index_path: str):
        with open(inverted_index_path, 'wb') as inverted_index_file:
            pickle.dump(self._index, inverted_index_file)
        self.inverted_index_path = inverted_index_path

    def get(self, term: str) -> Optional[IndexRecord]:
        if self._index is None:
            raise Exception('Inverted index does not exist.')
        indexrecord = self._index.get(term)
        if not indexrecord:
            raise Exception(f'Inverted index does not contain term {term}.')
        return indexrecord

    def create(self, conf: dict[str, object], workers=4):
        wikipedia_data_path: str = conf['sk_wikipedia_dump_path']
        inverted_index_path: str = conf['inverted_index_path']
        preprocessor_components: list[str] = conf['preprocessor_components']

        wiki_parser = WikiParser()
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

        text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        parsed_documents = text_preprocessor.preprocess(parsed_documents, workers)

        tfidf_vectorizer = vectorizer.TfIdfVectorizer(len(parsed_documents), self)

        self._create(parsed_documents)

        for document in parsed_documents:
            document.vector = tfidf_vectorizer.vectorize_document(document)

        # self.save(inverted_index_path)
        pass

    def _create(self, parsed_documents):
        self._index = {}
        for document in parsed_documents:
            for term in document.terms:
                if term not in self._index:
                    self._index[term] = IndexRecord(term)
                self._index[term].add_document(document)
