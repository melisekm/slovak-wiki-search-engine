from timeit import default_timer as timer
from tqdm import tqdm
import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from org.apache.lucene.analysis.cz import CzechAnalyzer
from java.util import HashMap


import pandas as pd
from ast import literal_eval


def main():
    store = NIOFSDirectory(Paths.get("skwiki_index"))

    analyzer_per_field = HashMap()
    analyzer_per_field.put("terms", WhitespaceAnalyzer())
    analyzer = PerFieldAnalyzerWrapper(CzechAnalyzer(), analyzer_per_field)


    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    start = timer()

    df = pd.read_csv("datapart.csv", encoding="utf-8")
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Indexing"):
        doc = Document()
        doc.add(Field("title", row["title"], TextField.TYPE_STORED))
        doc.add(Field("terms", row["terms"], TextField.TYPE_STORED))
        if not pd.isna(row["infobox"]):
            infobox_split = row["infobox"].split("\t")
            infobox_name = infobox_split[0]
            if len(infobox_split) < 2:
                print("SPLIT FAILED", index)
                continue
            infobox_value = literal_eval(infobox_split[1])  # dict of infobox key value pairs
            doc.add(Field("infobox_name", infobox_name, TextField.TYPE_STORED))
            for key, value in infobox_value.items():
                doc.add(Field("infobox_key", key, TextField.TYPE_STORED))
                doc.add(Field("infobox_value", value, TextField.TYPE_STORED))

        writer.addDocument(doc)
    writer.commit()
    writer.close()
    end = timer()
    print("Indexing took: ", end - start)


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    main()
