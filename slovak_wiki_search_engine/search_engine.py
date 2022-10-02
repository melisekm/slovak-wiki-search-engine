import logging
from typing import Union

from arg_parser import QueryBooleanOperator
from indexer import InvertedIndex
from text_preprocessor import TextPreprocessor
from utils import cosine_similarity
from vectorizer import TfIdfVectorizer
from wiki_parser import WikiPage

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self, inverted_index: InvertedIndex, conf: dict[str, Union[str, int, list[str]]], **kwargs):
        self.inverted_index = inverted_index
        self.query = kwargs['query']
        self.boolean_operator = kwargs.get('boolean_operator', QueryBooleanOperator.AND)
        self.results_count = kwargs.get('results_count', 10)
        self.relevant_documents_count = kwargs.get('relevant_documents_count', 100)
        self.conf = conf
        preprocessor_components: list = conf.get("preprocessor_components")
        if preprocessor_components and 'document_saver' in preprocessor_components:
            preprocessor_components.remove("document_saver")
        self.text_preprocessor = TextPreprocessor(preprocessor_components, self.conf)
        self.vectorizer = TfIdfVectorizer(self.inverted_index)

    def search(self) -> list[tuple[WikiPage, float]]:
        query = WikiPage(-1, None, self.query)
        logger.info(f'Original Query: {self.query}')
        query = self.text_preprocessor.preprocess([query], workers=1)[0]
        if self.boolean_operator == QueryBooleanOperator.AND:
            logger.info(f'Query Terms: {" AND ".join(query.terms)}')
        elif self.boolean_operator == QueryBooleanOperator.OR:
            logger.info(f'Query Terms: {" OR ".join(query.terms)}')

        relevant_documents = set()
        for term in query.terms:
            try:
                documents = self.inverted_index.get(term).documents
                if self.boolean_operator == QueryBooleanOperator.AND:
                    relevant_documents = relevant_documents.intersection(documents)
                elif self.boolean_operator == QueryBooleanOperator.OR:
                    relevant_documents = relevant_documents.union(documents)
            except AttributeError as e:
                logger.warning(e)

        logger.info(f'Relevant documents count: {len(relevant_documents)}')

        query.vector = self.vectorizer.vectorize_terms(query.terms)
        # calculate cosine similarity between query and relevant documents
        relevant_documents = cosine_similarity(query, relevant_documents)[:self.results_count]
        logger.info(f'Relevant documents count after limit: {len(relevant_documents)}')
        return relevant_documents
