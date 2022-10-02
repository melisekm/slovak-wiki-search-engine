import unittest

from indexer import InvertedIndex
from vectorizer import TfIdfVectorizer
from wiki_parser import WikiPage


class TestTfIdf(unittest.TestCase):
    def test_tfidf(self):
        document1 = WikiPage(-1, "Test", "This is a a sample")
        document1.terms = ["this", "is", "a", "a", "sample"]
        document2 = WikiPage(-1, "Test", "This is another another example example example")
        document2.terms = ["this", "is", "another", "another", "example", "example", "example"]
        inverted_index = InvertedIndex()
        inverted_index._create_index([document1, document2])

        vectorizer = TfIdfVectorizer(inverted_index)

        self.assertEqual(vectorizer._tf("this", document1), 0.2)
        self.assertEqual(round(vectorizer._tf("this", document2), 2), 0.14)

        self.assertEqual(vectorizer._idf("this"), 0)
        self.assertEqual(vectorizer._tfidf("this", document1), 0)
        self.assertEqual(vectorizer._tfidf("this", document2), 0)

        self.assertEqual(vectorizer._tf("example", document1), 0)
        self.assertEqual(round(vectorizer._tf("example", document2), 3), 0.429)
        self.assertEqual(round(vectorizer._idf("example"), 3), 0.301)

        self.assertEqual(round(vectorizer._tfidf("example", document1), 3), 0)
        self.assertEqual(round(vectorizer._tfidf("example", document2), 3), 0.129)
