import logging
from timeit import default_timer as timer
from typing import Union

from arg_parser import QueryBooleanOperator
from indexer import InvertedIndex
from text_preprocessor import TextPreprocessor
from utils import cosine_similarity
from vectorizer import TfIdfVectorizer
from wiki_parser import WikiPage

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self, inverted_index: InvertedIndex, conf: dict[str, Union[str, int, list[str]]]):
        self.inverted_index = inverted_index
        self.conf = conf
        preprocessor_components: list = conf.get("preprocessor_components")
        if preprocessor_components and 'document_saver' in preprocessor_components:
            preprocessor_components.remove("document_saver")
        self.text_preprocessor = TextPreprocessor(preprocessor_components, self.conf, load_docs=False)
        self.vectorizer = TfIdfVectorizer(self.inverted_index)

    def search(self, query: str,
               boolean_operator=QueryBooleanOperator.AND,
               results_count=10) -> list[tuple[WikiPage, float]]:

        logger.info(f'Original Query: {query}')

        start = timer()
        query_doc = WikiPage(-1, None, query)
        query_doc = self.text_preprocessor.preprocess([query_doc], workers=1)[0]


        if boolean_operator == QueryBooleanOperator.AND:
            logger.info(f'Query Terms: {" AND ".join(query_doc.terms)}')
        elif boolean_operator == QueryBooleanOperator.OR:
            logger.info(f'Query Terms: {" OR ".join(query_doc.terms)}')
        else:
            raise ValueError(f'Unknown boolean operator {boolean_operator}')

        relevant_documents = set()
        for term in list(query_doc.terms):
            try:
                documents = self.inverted_index.get(term).documents
            except AttributeError:
                logger.info(f"Term {term} not found in inverted index.")
                query_doc.terms.remove(term)
                continue

            if not relevant_documents:
                relevant_documents = documents
            else:
                try:
                    if boolean_operator == QueryBooleanOperator.AND:
                        relevant_documents = relevant_documents.intersection(documents)
                    elif boolean_operator == QueryBooleanOperator.OR:
                        relevant_documents = relevant_documents.union(documents)
                except AttributeError as e:
                    logger.warning(e)

        logger.info(f'Relevant documents count: {len(relevant_documents)}')

        query_doc.vector = self.vectorizer.vectorize_terms(query_doc.terms)
        # calculate cosine similarity between query_doc and relevant documents
        relevant_documents = cosine_similarity(query_doc, relevant_documents)[:results_count]
        run_time = timer() - start
        logger.info(f'Relevant documents count after limit: {len(relevant_documents)}')
        logger.info(f'Search time: {run_time:.2f}s')

        return relevant_documents
