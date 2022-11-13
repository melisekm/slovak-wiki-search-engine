import sys
from pyspark.sql import SparkSession
from src.wiki_parser import WikiParser
import src.text_preprocessor as text_preprocessor
import json

if __name__ == '__main__':
    with open('conf.json', 'r') as conf_file:
        conf = json.load(conf_file)
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    spark = SparkSession.builder
    for key, value in conf['spark'].items():
        spark = spark.config(key, value)

    spark = spark.getOrCreate()

    df = spark.read.format("xml") \
        .option("rowTag", "page") \
        .option("inferSchema", "false") \
        .option("valueTag", "data") \
        .load(input_path)


    parser = WikiParser()

    rdd = df.rdd.repartition(conf['partitions'])

    data = (
        rdd
        .map(parser.parse_page)
        .filter(lambda x: x is not None and x.raw_text is not None)
        .map(lambda x: text_preprocessor.text_processor.preprocess(x))
    )

    split = [
        (x.title, x.raw_text, x.infobox.to_string() if x.infobox else None, " ".join(x.terms) if x.terms else "")
        for x in data.collect()
    ]
    df = spark.createDataFrame(split, ["title", "raw_text", "infobox", "terms"])

    df.write \
        .option("header", "true") \
        .format("com.databricks.spark.csv") \
        .option('quote', '"') \
        .option('escape', '"') \
        .option('multiLine', True) \
        .option("delimiter", ",") \
        .mode("overwrite") \
        .save(output_path + "/data")

    spark.stop()
