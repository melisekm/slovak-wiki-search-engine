from ast import literal_eval
import lucene
import json
import pandas
import os
from tqdm import tqdm
import pandas as pd

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


def create_wiki_mapping():
    conf = get_config("conf.json")
    wiki_parts_path = conf["wiki_parts_path"]
    wiki_parts = os.listdir(wiki_parts_path)
    wiki_mapping = {}
    for part in tqdm(wiki_parts):
        df = pandas.read_csv(os.path.join(wiki_parts_path, part), encoding="utf-8")
        for idx, row in df.iterrows():
            wiki_mapping[row["title"]] = part
    # save mapping as json

    with open("wiki_mapping.json", "w") as f:
        json.dump(wiki_mapping, f)

def read_infobox_from_infobox_string(infobox_string):
    res = {}
    infobox_split = infobox_string.split("\t")
    infobox_length = len(infobox_split)
    if infobox_length == 1 and infobox_split[0].startswith("{"):
        infobox_value_index = 0
    elif infobox_length == 2:
        infobox_value_index = 1
        infobox_name = infobox_split[0]
        res["infobox_name"] = infobox_name
    else:
        return res
    
    # dict of infobox key value pairs
    res['infobox_dict'] = literal_eval(infobox_split[infobox_value_index])
    return res

if __name__ == '__main__':
    create_wiki_mapping()