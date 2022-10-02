import logging
import pickle
from typing import Optional, Union

import vectorizer
from text_preprocessor import TextPreprocessor
from wiki_parser import WikiPage, WikiParser

logger = logging.getLogger(__name__)


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


def load(inverted_index_path: str):
    logger.info(f'Loading inverted index from {inverted_index_path}')
    with open(inverted_index_path, 'rb') as inverted_index_file:
        return pickle.load(inverted_index_file)


class InvertedIndex:
    def __init__(self):
        self.inverted_index_path: Optional[str] = None
        self._index: dict[str, IndexRecord] = None
        self.documents_count: int = 0

    def save(self, inverted_index_path: str):
        logger.info(f'Saving inverted index to {inverted_index_path}')
        self.inverted_index_path = inverted_index_path
        with open(inverted_index_path, 'wb') as inverted_index_file:
            pickle.dump(self, inverted_index_file)

    def get(self, term: str) -> Optional[IndexRecord]:
        if self._index is None:
            raise Exception('Inverted index does not exist.')
        indexrecord = self._index.get(term)
        if not indexrecord:
            raise AttributeError(f'Inverted index does not contain term {term}.')
        return indexrecord

    def _create_index(self, parsed_documents: list[WikiPage]):
        logger.info("Adding terms to inverted index...")
        self._index = {}
        for document in parsed_documents:
            for term in document.terms:
                if term not in self._index:
                    self._index[term] = IndexRecord(term)
                self._index[term].add_document(document)
        self.documents_count = len(parsed_documents)
        logger.info(f"Index created. Total terms in index: {len(self._index)}")

    def create(self, conf: dict[str, Union[str, int, list[str]]], workers=4):
        wikipedia_data_path: str = conf['sk_wikipedia_dump_path']
        inverted_index_path: str = conf['inverted_index_path']
        preprocessor_components: list[str] = conf['preprocessor_components']

        logger.info(
            f'Creating inverted index. {wikipedia_data_path=}, {inverted_index_path=}')

        wiki_parser = WikiParser()
        parsed_documents = wiki_parser.parse_wiki(wikipedia_data_path, workers)

        text_preprocessor = TextPreprocessor(preprocessor_components, conf)
        parsed_documents = text_preprocessor.preprocess(parsed_documents, workers)

        self._create_index(parsed_documents)

        tfidf_vectorizer = vectorizer.TfIdfVectorizer(self)
        tfidf_vectorizer.vectorize_documents(parsed_documents)

        self.save(inverted_index_path)
        logger.info("Inverted index created.")
