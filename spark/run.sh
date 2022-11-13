set -e

if [ "$#" -ne 5 ]; then
    echo "Usage: run.sh <input_path> <output_path> <py_files.zip> <other_file,otherfile2> <main_script>"
    echo "Make sure conf.json is correctly configured"
    exit 1
fi

input_path=$1
output_path=$2
py_files=$3
other_files=$4
main_script=$5

hadoop fs -mkdir -p $output_path
cp spark-xml_2.12-0.15.0.jar $SPARK_HOME/jars

apt-get update
apt-get install -y python3-pip
apt-get install -y python3-venv

python3 -m venv melisekm_vinf
source melisekm_vinf/bin/activate
python3 -m pip install --upgrade --force pip

pip install -r requirements.txt
PYTHONIOENCODING="utf8"

spark-submit \
 --conf spark.pyspark.python=`which python3` \
 --py-files $py_files \
 --files=$other_files \
 $main_script $input_path $output_path

hadoop fs -copyToLocal $output_path/data ./results

