import logging
import re
import sys
from enum import Enum


class QueryBooleanOperator(Enum):
    AND = 1
    OR = 2

    def __eq__(self, other):
        return other.value == self.value


DEFAULT_BOOLEAN_OPERATOR = QueryBooleanOperator.AND
DEFAULT_RESULTS_COUNT = 10
DEFAULT_RELEAVNT_DOCS_COUNT = 1000


class ArgParser:
    def __init__(self):
        self.query = None
        self.boolean_operator = DEFAULT_BOOLEAN_OPERATOR
        self.results_count = DEFAULT_RESULTS_COUNT
        self.relevant_documents_count = DEFAULT_RELEAVNT_DOCS_COUNT

    def parse(self, args, validate=True):
        if isinstance(args, list):
            args = " ".join(args[1:])

        query_match = re.search('^([^-]*)', args)
        if query_match:
            self.query = query_match.group(1).strip()

        self.boolean_operator = QueryBooleanOperator.OR if re.search('-o', args) else QueryBooleanOperator.AND
        number_of_results_match = re.search(r'-n (\d+)', args)
        if number_of_results_match:
            self.results_count = int(number_of_results_match.group(1))
        else:
            self.results_count = DEFAULT_RESULTS_COUNT
        number_of_relevant_documents_match = re.search(r'-x (\d+)', args)
        if number_of_relevant_documents_match:
            self.relevant_documents_count = int(number_of_relevant_documents_match.group(1))
        else:
            self.relevant_documents_count = DEFAULT_RELEAVNT_DOCS_COUNT

        if validate:
            self.validate_params()
        return self.get_params()

    def validate_params(self):
        errors = []
        if not self.query:
            errors.append('Query is empty. Please enter a question.')
        if not isinstance(self.results_count, int):
            errors.append('Results count is not an integer')
        if not isinstance(self.relevant_documents_count, int):
            errors.append('Relevant documents count is not an integer')

        for error in errors:
            logging.error(error)
        if errors:
            sys.exit(1)

    def get_params(self):
        return self.__dict__
