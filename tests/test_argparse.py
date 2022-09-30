import unittest

from slovak_wiki_search_engine.arg_parser import ArgParser, QueryBooleanOperator


def arg_parser_mock(input_params):
    arg_parser = ArgParser()
    arg_parser.parse(input_params)
    return arg_parser.get_params()


class ArgParseTester(unittest.TestCase):

    def test_all(self):
        input_params = [None, 'Kto je prezident USA?', '-o', '-n', '5', '-x', '250']
        expected_params = {
            'query': 'Kto je prezident USA?',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 5,
            'relevant_documents_count': 250,
        }

        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_only(self):
        input_params = [None, 'kolko je 5+5?']
        expected_params = {
            'query': 'kolko je 5+5?',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_and_boolean_operator(self):
        input_params = [None, 'Som clovek?', '-o']
        expected_params = {
            'query': 'Som clovek?',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_and_results_count(self):
        input_params = [None, 'Kto je najlepsi?', '-n', '15']
        expected_params = {
            'query': 'Kto je najlepsi?',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 15,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_and_relevant_documents_count(self):
        input_params = [None, 'test', '-x', '250']
        expected_params = {
            'query': 'test',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 250,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_arg_parser_empty_query(self):
        input_params = [None, '']
        expected_params = {
            'query': '',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_arg_parser_empty_query_and_boolean_operator(self):
        input_params = [None, '', '-o']
        expected_params = {
            'query': '',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_incorrect_boolean_operator(self):
        input_params = [None, 'test', '-m']
        expected_params = {
            'query': 'test',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_incorrect_arg(self):
        input_params = [None, 'test', '-m', '5']
        expected_params = {
            'query': 'test',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_incorrect_arg_with_correct_arg(self):
        input_params = [None,
                        'Nezvyčajné kŕdle šťastných figliarskych ďatľov učia pri kótovanom ústí Váhu mĺkveho koňa Waldemara obžierať väčšie kusy exkluzívnej kôry s quesadillou',
                        '-m', '5', '-n', '15', '-o']
        expected_params = {
            'query': 'Nezvyčajné kŕdle šťastných figliarskych ďatľov učia pri kótovanom ústí Váhu mĺkveho koňa Waldemara obžierať väčšie kusy exkluzívnej kôry s quesadillou',
            'boolean_operator': QueryBooleanOperator.OR,
            'results_count': 15,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)

    def test_query_with_missing_numbers(self):
        input_params = [None, 'Kde byva elizabeth the second', '-n', '-x']
        expected_params = {
            'query': 'Kde byva elizabeth the second',
            'boolean_operator': QueryBooleanOperator.AND,
            'results_count': 10,
            'relevant_documents_count': 100,
        }
        self.assertEqual(arg_parser_mock(input_params), expected_params)
