import sys
import lucene
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from java.util import HashMap
from org.apache.lucene.analysis.cz import CzechAnalyzer

from text_preprocessor import load




def search(user_query):
    text_preprocessor = load()
    directory = NIOFSDirectory(Paths.get("skwiki_index"))
    searcher = IndexSearcher(DirectoryReader.open(directory))

    # for terms field use whiespace analyzer
    # for others use czech analyzer
    analyzer_per_field = HashMap()
    analyzer_per_field.put("terms", WhitespaceAnalyzer())
    analyzer = PerFieldAnalyzerWrapper(CzechAnalyzer(), analyzer_per_field)

    parsed_terms_query = text_preprocessor.preprocess(user_query)

    
    queryParser = QueryParser("<default field>", analyzer)
    special = f'title:"{user_query}"^5.0 infobox_name:"{user_query}"^3.5 infobox_key:"{user_query}"^2.5 ' \
              f'infobox_value:"{user_query}"^1.5 terms:"{parsed_terms_query}"'
    query = queryParser.parse(special)


    scoreDocs = searcher.search(query, 10).scoreDocs
    print("%s total matching documents." % len(scoreDocs))
    for scoreDoc in reversed(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        print('title:', doc.get("title"), " score: ", scoreDoc.score)


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    search(" ".join(sys.argv[1:]))
