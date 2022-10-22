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
            document.vector = self.normalize_vector(self.vectorize_terms(document.terms))
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

    def _tf(self, term: str, document: list[str], sublinear_tf=True) -> float:
        """
        Term frequency, tf(t,d), is the relative frequency of term t within document d.
        """
        if sublinear_tf:  # log normalization
            return 1 + math.log10(document.count(term))  # 1 + log(f_{f_d})

        return document.count(term) / len(document)  # -> f_{t,d} / sum_{t' in d} f_{t',d}

    def _idf(self, term: str, smooth_idf=True) -> float:
        """
        The inverse document frequency is a measure of how much information the word provides
        """
        index_record = self.inverted_index.get(term)
        if smooth_idf:
            # log(1 + N / (1 + df_t)) + 1
            return math.log10(
                (1 + self.inverted_index.documents_count) / (1 + index_record.document_frequency)) + 1

        # log(N / df_t)
        return math.log10(self.inverted_index.documents_count / index_record.document_frequency)

    def normalize_vector(self, vector: list[float]) -> list[float]:
        """
        Normalizes vector to unit length.
        """
        vector_length = math.sqrt(sum([x ** 2 for x in vector]))
        return [x / vector_length for x in vector]
