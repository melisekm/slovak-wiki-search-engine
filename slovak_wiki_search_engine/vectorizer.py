import logging
import math

from tqdm import tqdm

import indexer
from wiki_parser import WikiPage

logger = logging.getLogger(__name__)


class TfIdfVectorizer:
    def __init__(self, inverted_index: 'indexer.InvertedIndex'):
        self.inverted_index = inverted_index

    def vectorize_documents(self, documents: list[WikiPage]) -> list[WikiPage]:
        logger.info(f"Vectorizing {len(documents)} documents")
        for document in tqdm(documents, desc="Vectorizing documents"):
            document.vector = self.vectorize_terms(document.terms)
            document.raw_text = None
            document.terms = None
        return documents

    def vectorize_terms(self, document: list[str]) -> list[float]:
        if not document:
            return []
        return [self._tfidf(term, document) for term in document]

    def _tfidf(self, term: str, document: list[str]) -> float:
        tf = self._tf(term, document)
        idf = self._idf(term)
        return tf * idf

    def _tf(self, term: str, document: list[str], sublinear_tf=False) -> float:
        if sublinear_tf:
            return 1 + math.log10(document.count(term))

        return document.count(term) / len(document)

    def _idf(self, term: str, smooth_idf=False) -> float:
        index_record = self.inverted_index.get(term)
        if smooth_idf:
            return math.log10(
                (1 + self.inverted_index.documents_count) / (1 + index_record.document_frequency)) + 1

        return math.log10(self.inverted_index.documents_count / index_record.document_frequency)
