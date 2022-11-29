import os
from ast import literal_eval
from timeit import default_timer as timer

import lucene
import pandas as pd
from java.nio.file import Paths
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import NIOFSDirectory
from tqdm import tqdm

from common import get_analyzer, get_config, read_infobox_from_infobox_string


def add_doc_to_index(row):
    doc = Document()
    doc.add(Field("title", row["title"], TextField.TYPE_STORED))
    doc.add(Field("terms", row["terms"], TextField.TYPE_STORED))
    if not pd.isna(row["infobox"]):
        infobox_data = read_infobox_from_infobox_string(row)
        if "infobox_name" in infobox_data:
            doc.add(Field("infobox_name", infobox_data["infobox_name"], TextField.TYPE_STORED))
        if "infobox_dict" in infobox_data:
            for key, value in infobox_data["infobox_dict"].items():
                doc.add(Field("infobox_key", key, TextField.TYPE_STORED))
                doc.add(Field("infobox_value", value, TextField.TYPE_STORED))
    return doc

class PyLuceneIndexer:
    def __init__(self, config_path):
        self.conf = get_config(config_path)
        self.wiki_parts_path = self.conf["wiki_parts_path"]

    def create_index(self):
        store = NIOFSDirectory(Paths.get(self.conf.get("index_path", "skwiki_pylucene_index")))
        analyzer = get_analyzer()
        index_writer_config = IndexWriterConfig(analyzer)
        index_writer_config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
        index_writer = IndexWriter(store, index_writer_config)

        start_timer = timer()
        documents = 0

        doc_id = 0

        wiki_parts = os.listdir(self.wiki_parts_path)
        progress = tqdm(wiki_parts, total=len(wiki_parts), desc="Indexing")
        for part in progress:
            df = pd.read_csv(os.path.join(self.wiki_parts_path, part), encoding="utf-8")

            documents += df.shape[0]
            for row_idx, row in df.iterrows():
                doc = add_doc_to_index(row)
                index_writer.addDocument(doc)

            doc_id += 1
            if doc_id % 100 == 0:
                index_writer.commit()
            progress.set_postfix({"docs": documents, "current_doc_size": df.shape[0]})
        index_writer.commit()
        index_writer.close()

        print("Indexing took: ", timer() - start_timer)
        print("Indexed documents: ", documents)


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    indexer = PyLuceneIndexer("data/conf.json")
    indexer.create_index()
