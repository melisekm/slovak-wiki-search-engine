from collections import defaultdict
import os
import json
import logging
import pandas as pd

import lucene
from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import NIOFSDirectory

from common import get_analyzer, get_config, read_infobox_from_infobox_string
from text_preprocessor import TextPreprocessor, Tokenizer
import arg_parser


def setup_logging(verbose=True):
    log_handlers = [logging.StreamHandler()]
    formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(filename)s]: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S",
    )
    for handler in log_handlers:
        handler.setFormatter(formatter)
    if not verbose:
        for handler in log_handlers:
            handler.setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.DEBUG, handlers=log_handlers)
    logging.root.handlers = log_handlers


setup_logging()

logger = logging.getLogger(__name__)


class PyLuceneSearchEngine:
    def __init__(self, config_path):
        self.conf = get_config(config_path)

        with open(self.conf["stop_words_path"], encoding="UTF-8") as stopwords_file:
            stopwords = [line.strip() for line in stopwords_file]
        self.text_preprocessor = TextPreprocessor(self.conf["preprocessor_components"], stopwords)

        with open(self.conf["wiki_mapping_path"], encoding="UTF-8") as wiki_mapping_file:
            self.wiki_mapping = json.load(wiki_mapping_file)

        self.wiki_parts_path = self.conf["wiki_parts_path"]

        store = NIOFSDirectory(Paths.get(self.conf["index_path"]))
        self.searcher = IndexSearcher(DirectoryReader.open(store))
        self.boosts = self.conf.get("boosts", {})
        self.analyzer = get_analyzer()
        self.query_parser = QueryParser("<default field>", self.analyzer)
        self.tokenizer = Tokenizer()

    def load_full_results(self, documents):
        wiki_parts = defaultdict(list)
        for idx, document in enumerate(documents):
            title = document.get("title")
            wiki_parts[self.wiki_mapping[title]].append((title, len(documents) - idx))

        full_results = [None] * len(documents)
        for wiki_part, docs in wiki_parts.items():
            df = pd.read_csv(os.path.join(self.wiki_parts_path, wiki_part), encoding="utf-8")
            full_docs = df.loc[df["title"].isin([doc[0] for doc in docs])]
            full_docs = full_docs.set_index("title").to_dict(orient="index")
            for doc in docs:
                title, idx = doc
                full_results[idx - 1] = full_docs[title]

        return full_results

    def show_results(self, score_docs):
        score_docs = list(reversed(score_docs))
        docs = []
        results_full = self.load_full_results([self.searcher.doc(score_doc.doc) for score_doc in score_docs])

        for idx, score_doc_and_full_results in enumerate(zip(score_docs, results_full[::-1])):
            score_doc, full_result = score_doc_and_full_results
            doc = self.searcher.doc(score_doc.doc)
            docs.append(doc)
            score = score_doc.score
            title = doc.get("title")
            idx = len(score_docs) - idx
            logger.info(f"Result {idx}: {title} - {score}")
            logger.info(f"URL: https://sk.wikipedia.org/wiki/{title.replace(' ', '_')}")
            if not pd.isna(full_result["infobox"]):
                logger.info(f"Infobox: {read_infobox_from_infobox_string(full_result['infobox']).get('infobox_name', 'Not found :(')}")
            logger.info("-" * 100)

        prompt = "\nEnter result number to learn more about the document. [Q] to go back.: "
        msg = "-" * 100 + prompt
        while True:
            try:
                num_to_show = input(msg)
                if num_to_show.lower() == "q":
                    break
                num_to_show = int(num_to_show)
            except ValueError:
                print("Invalid input.")
                continue
            if num_to_show > len(results_full) or num_to_show < 1:
                print("Invalid input.")
                continue

            result_to_show = results_full[num_to_show - 1]
            if not pd.isna(result_to_show["infobox"]):
                infobox = read_infobox_from_infobox_string(result_to_show['infobox'])
                print("\n".join("{}: {}".format(k, v) for k, v in infobox['infobox_dict'].items()))
                print("Infobox name: ", infobox.get("infobox_name", "Infobox Name not found"))
            else:
                print("Sorry this Article doesn't have a infobox.")

    def search(self, user_query):
        parsed_terms_query = self.text_preprocessor.preprocess(user_query)
        query_string = ""

        for term in self.tokenizer.process(user_query):
            for key, value in self.boosts.items():
                query_string += f"{key}:{term}^{value} "

        for term in parsed_terms_query:
            query_string += f"+terms:{term} "

        query = self.query_parser.parse(query_string)

        score_docs = self.searcher.search(query, 10).scoreDocs
        print(f"{len(score_docs)} total matching documents.")

        self.show_results(score_docs)


if __name__ == "__main__":
    lucene.initVM(vmargs=["-Djava.awt.headless=true"])
    search_engine = PyLuceneSearchEngine("data/conf.json")
    arg_parser = arg_parser.ArgParser()
    while True:
        args = input("Enter the program arguments. [Q] to quit: ")
        if args.lower() == "q":
            break
        params = arg_parser.parse(args)
        search_engine.search(params["query"])
