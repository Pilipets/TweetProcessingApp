from pyspark.sql import SparkSession
from pyspark.sql.functions import split, explode

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 pyspark-shell'

spark = SparkSession \
          .builder \
          .appName("APP") \
          .getOrCreate()

df = spark.readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", "tweet-stream") \
  .option("startingOffsets", "earliest") \
  .load()

df = df.selectExpr("CAST(value AS STRING)")

words = df \
.select(explode(split(df.value, " ")).alias("word")) \
.filter("word like '#%'")

words = words.groupBy("word").count()

query = words\
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .trigger(processingTime='2 seconds')\
    .start()

query.awaitTermination()