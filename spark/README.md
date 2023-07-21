# Description
Parses and preprocesses texts from xml of Slovak wiki and saves them to csv.

Project: Parse and search on Slovak Wiki with lemmatization and natural queries  
Data: skwiki-latest-pages-articles.xml  
Framework: Spark (PySpark)

# Tested on
- Docker Image: iisas/hadoop-spark-pig-hive:2.9.2
- Python: 3.6.9
- Spark: 2.4.3
- Hadoop: 2.9.2

# How to run
- cd to project directory that contains main files (`run.sh`, `src`, `main.py`...) on local file system
- Setup all parameters in `conf.json`
  - spark.master, spark.executor.memory, spark.driver.memory, spark.cores.max, partitions
  - RDD is used, which at my machine has 1 partition by default, so I set partitions to a higher number (e.g. 32)
  - Others should be default
- Run `run.sh <input to HDFS> <output folder on HDFS> src.zip SK_stopwords.txt,conf.json main.py`
  - e.g. `run.sh skwiki-latest-pages-articles.xml melisekm/result src.zip SK_stopwords.txt,conf.json main.py`
- If the script finishes, in `./results` folder should be the results

# Further description
- It is expected that `skwiki-latest-pages-articles.xml` is already on HDFS. 
- Folder `<output folder on HDFS>` is created automatically, where results are placed in form of `part*.csv` files
- `spark-xml_2.12-0.15.0.jar` is copied to `$SPARK_HOME/jars` for XML parsing
- `python3-pip` is installed
- `python3-venv` is installed
- New env called `melisekm_vinf` is created and activated
- `pip` version is upgraded
- `requirements.txt` are installed
- `spark-submit` is used to execute script `main.py` from `src.zip` archive and util files `SK_stopwords.txt` and `conf.json`
- Each of the executors will use python interpreter `melisekm_vinf/bin/python3`
- To local folder `./results` are copied all result folders from `melisekm/result/data`, that should contain part*.csv files and 4 columns, `title`, `raw_text`, `infobox`, `terms`.

## main.py description
- Load XML
- Convert RDD and test partitions
- Parse data
- On each executor load model for lemmatization from file `text_preprocessor.py`
- Preprocess data
- Convert to DataFrame
- Save csv to HDFS

## Notes
- I am not sure about compatibility between versions.
- On 3 local executors, where each had 2 cores and 32 partitions 64MB was processed in 30 minutes.
- The `main.py` uses `collect()` on RDD, which is not recommended, so the driver can run out of memory.
