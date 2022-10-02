import sys
# insert to sys path slovak_wiki_search_engine directory
sys.path.insert(0, 'slovak_wiki_search_engine')

from .utils import *
from .arg_parser import *
from .indexer import *
from .search_engine import *




setup_logging()
