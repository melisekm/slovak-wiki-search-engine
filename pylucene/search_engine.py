import sys
import lucene
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
# from org.apache.lucene.analysis.standard import StandardAnalyzer
from text_preprocessor import load




def search(user_query):
    text_preprocessor = load()
    directory = NIOFSDirectory(Paths.get("skwiki_index"))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer()

    parsed_query = text_preprocessor.preprocess(user_query)
    query = QueryParser("terms", analyzer).parse(parsed_query)
    scoreDocs = searcher.search(query, 10).scoreDocs
    print("%s total matching documents." % len(scoreDocs))
    for scoreDoc in reversed(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        print('title:', doc.get("title"), " score: ", scoreDoc.score)


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    search(" ".join(sys.argv[1:]))
    # search("brankár")
