import json

from java.util import HashMap
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.cz import CzechAnalyzer
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper


def get_analyzer():
    analyzer_per_field = HashMap()
    analyzer_per_field.put("terms", WhitespaceAnalyzer())
    return PerFieldAnalyzerWrapper(CzechAnalyzer(), analyzer_per_field)


def get_config(path):
    with open(path, 'r') as conf_file:
        return json.load(conf_file)
