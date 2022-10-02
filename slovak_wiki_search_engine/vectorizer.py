import logging
import math

import indexer
from wiki_parser import WikiPage

logger = logging.getLogger(__name__)


class TfIdfVectorizer:
    def __init__(self, inverted_index: 'indexer.InvertedIndex'):
        self.inverted_index = inverted_index

    def vectorize(self, documents: list[WikiPage]) -> list[WikiPage]:
        logger.info(f"Vectorizing {len(documents)} documents")
        for document in documents:
            document.vector = self.vectorize_document(document)
        return documents

    def vectorize_document(self, document: WikiPage) -> list[float]:
        vector = []
        if not document.terms:
            return vector

        for term in document.terms:
            tfidf = self._tfidf(term, document)
            vector.append(tfidf)
        return vector

    def _tfidf(self, term: str, document: WikiPage) -> float:
        tf = self._tf(term, document)
        idf = self._idf(term)
        return tf * idf

    def _tf(self, term: str, document: WikiPage, sublinear_tf=False) -> float:
        if sublinear_tf:
            return 1 + math.log10(document.terms.count(term))
        return document.terms.count(term) / len(document.terms)

    def _idf(self, term: str, smooth_idf=False) -> float:
        if smooth_idf:
            return math.log10(
                (1 + self.inverted_index.documents_count) / (1 + self.inverted_index.get(term).document_frequency)) + 1
        return math.log10(self.inverted_index.documents_count / self.inverted_index.get(term).document_frequency)
