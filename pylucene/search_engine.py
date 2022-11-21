import sys

import lucene
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import NIOFSDirectory

from common import get_analyzer, get_config
from text_preprocessor import TextPreprocessor, Tokenizer


class PyLuceneSearchEngine:
    def __init__(self, config_path):
        self.conf = get_config(config_path)

        with open(self.conf['stop_words_path'], encoding="UTF-8") as stopwords_file:
            stopwords = [line.strip() for line in stopwords_file]
        self.text_preprocessor = TextPreprocessor(self.conf['preprocessor_components'], stopwords)

        store = NIOFSDirectory(Paths.get(self.conf['index_path']))
        self.searcher = IndexSearcher(DirectoryReader.open(store))
        self.boosts = self.conf.get('boosts', {})
        self.analyzer = get_analyzer()
        self.query_parser = QueryParser("<default field>", self.analyzer)
        self.tokenizer = Tokenizer()

    def search(self, user_query):
        parsed_terms_query = self.text_preprocessor.preprocess(user_query)
        query_string = ""

        for term in self.tokenizer.process(user_query):
            for key, value in self.boosts.items():
                query_string += f'{key}:{term}^{value} '


        for term in parsed_terms_query:
            query_string += f"+terms:{term} "

        query = self.query_parser.parse(query_string)

        score_docs = self.searcher.search(query, 10).scoreDocs
        print(f"{len(score_docs)} total matching documents.")

        for scoreDoc in reversed(score_docs):
            doc = self.searcher.doc(scoreDoc.doc)
            print('title:', doc.get("title"), " score: ", scoreDoc.score)


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    search_engine = PyLuceneSearchEngine("conf.json")
    search_engine.search(" ".join(sys.argv[1:]))
