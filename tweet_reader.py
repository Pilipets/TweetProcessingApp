from pyspark.sql import SparkSession
from pyspark.sql.functions import split, explode, col, lower, trim, regexp_replace
import requests

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 pyspark-shell'

def process_batch(df, epoch_id):
	df = df.orderBy(col("count").desc()).head(10)

	tags, tags_count = [], []
	for row in df:
		row = row.asDict()
		tags.append(row.get('word'))
		tags_count.append(row.get('count'))

	stats_json = {'labels': tags, 'values': tags_count}
	print('Sent data at epoch_id=', epoch_id,',data=', stats_json)

	response = requests.post('http://localhost:10000/updateData', json=stats_json)
	print('Sent response', response)

def removePunctuation(column):
	return lower(trim(regexp_replace(column,'\\p{Punct}',''))).alias('sentence')

if __name__ == '__main__':

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

	# TODO: Remove the punctuation before splitting
	words = df \
		.select(explode(split(df.value, " ")).alias("word")) \
		.filter("word like '#%'")

	words = words.groupBy("word").count()

	query = words\
		.writeStream \
		.outputMode("complete") \
		.foreachBatch(process_batch) \
		.trigger(processingTime='2 seconds')\
		.start()

	query.awaitTermination()