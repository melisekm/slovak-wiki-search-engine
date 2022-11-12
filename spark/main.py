from pyspark.sql import SparkSession
from src.wiki_parser import WikiParser

if __name__ == '__main__':
    spark_executor = "local[*]"

    spark = SparkSession \
        .builder \
        .appName("XML TEST") \
        .master(spark_executor) \
        .getOrCreate()

    df = spark.read.format("xml") \
        .option("rowTag", "page") \
        .option("inferSchema", "false") \
        .option("valueTag", "data") \
        .load("/user/root/sk_wikipedia_dump_small_1m.xml")
    df.printSchema()

    parser = WikiParser()


    data = (
        df.rdd
        .map(parser.parse_page)
        .filter(lambda x: x is not None and x.raw_text is not None)
        # .map(lambda x: x.to_string())
        # .distinct()
    )
    split = [(x.title, x.raw_text, x.infobox.to_string() if x.infobox else None) for x in data.collect()]
    df = spark.createDataFrame(split, ["title", "raw_text", "infobox"])
    df.printSchema()

    df.write\
        .option("header", "true") \
        .format("com.databricks.spark.csv") \
        .option('quote', '"') \
        .option('escape', '"') \
        .option('multiLine', True) \
        .option("delimiter", ",")\
        .mode("overwrite")\
        .save("/user/root/sk_wikipedia_dump_small_1m_parsed")

    spark.stop()
