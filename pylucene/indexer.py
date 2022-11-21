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

from common import get_analyzer, get_config


def add_doc_to_index(row_idx, row):
    doc = Document()
    doc.add(Field("title", row["title"], TextField.TYPE_STORED))
    doc.add(Field("terms", row["terms"], TextField.TYPE_STORED))
    if not pd.isna(row["infobox"]):
        infobox_split = row["infobox"].split("\t")
        infobox_length = len(infobox_split)
        if infobox_length == 1 and infobox_split[0].startswith("{"):
            infobox_value_index = 0
        elif infobox_length == 2:
            infobox_value_index = 1
            infobox_name = infobox_split[0]
            doc.add(Field("infobox_name", infobox_name, TextField.TYPE_STORED))
        else:
            print("SPLIT FAILED", row_idx)
            return doc

        # dict of infobox key value pairs
        infobox_value = literal_eval(infobox_split[infobox_value_index])  
        for key, value in infobox_value.items():
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

        wiki_parts = os.listdir(self.wiki_parts_path)[300:301]
        progress = tqdm(wiki_parts, total=len(wiki_parts), desc="Indexing")
        for part in progress:
            df = pd.read_csv(os.path.join(self.wiki_parts_path, part), encoding="utf-8")

            documents += df.shape[0]
            for row_idx, row in df.iterrows():
                doc = add_doc_to_index(row_idx, row)
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
    indexer = PyLuceneIndexer("conf.json")
    indexer.create_index()
