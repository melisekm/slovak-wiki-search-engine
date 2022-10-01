import math

import indexer
from wiki_parser import WikiPage


class TfIdfVectorizer:
    def __init__(self, document_count: int, inverted_index: 'indexer.InvertedIndex'):
        self.document_count = document_count
        self.inverted_index = inverted_index

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

    def _tf(self, term: str, document: WikiPage) -> float:
        return document.terms.count(term) / len(document.terms)

    def _idf(self, term: str) -> float:
        return math.log10(self.document_count / self.inverted_index.get(term).count)
