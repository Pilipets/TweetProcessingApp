from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql import streaming as S
import requests
from textblob import TextBlob

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 pyspark-shell'


def send_top_count_words(df, epoch_id, num, api):
    df = df.orderBy(F.col("count").desc()).head(num)

    words, counts = [], []
    for row in df:
        row = row.asDict()
        words.append(row.get('word'))
        counts.append(row.get('count'))

    stats_json = {'words': words, 'count': counts}
    print('Sent data at epoch_id=', epoch_id, ',data=', stats_json)

    response = requests.post(api, json=stats_json)
    print('Sent response', response)


def remove_punctuation(column):
    punct_string = ''.join(r'\{}'.format(ch)
                           for ch in r"""()[]{}""'':;,.!?\-/+*<=>&|""")
    return F.lower(F.trim(F.regexp_replace(column, '[{}]'.format(punct_string), '')))


def get_top_hashtags(df):
    words = df \
        .select(F.explode(F.split(remove_punctuation(df.value), " +")).alias("word")) \
        .filter("word like '#%'")

    words = words.groupBy("word").count()

    query = words\
        .writeStream \
        .outputMode("complete") \
        .foreachBatch(lambda df, epoch_id: send_top_count_words(df, epoch_id, 10, 'http://localhost:10000/update_hashtags_count')) \
        .trigger(processingTime='2 seconds')\
        .start()

    return query


def get_sentiment(text):
    sent = TextBlob(text).sentiment.polarity
    neutral_threshold = 0

    if sent >= neutral_threshold:
        return (1, 0, 0)  # positive

    elif sent > -neutral_threshold:
        return (0, 1, 0)  # neutral

    else:
        return (0, 0, 1)  # negative


def send_sentiment_counter(df, epoch_id, api):
    pos, neutral, neg = df.first()[0]

    total = pos + neutral + neg
    sentiment_json = {'positive': pos/total, 'neutral': neutral /
                      total, 'negative': neg/total, 'total': total}
    print('Sent data at epoch_id=', epoch_id, ',data=', sentiment_json)

    response = requests.post(api, json=sentiment_json)
    print('Sent response', response)


def get_sentiment_counter(df):

    get_sentiment_udf = F.udf(
        get_sentiment, T.ArrayType(T.IntegerType(), False))

    tweets_sentiment_df = df \
        .select(get_sentiment_udf('value').alias('sentiment')) \

    sum_sentiment = tweets_sentiment_df \
        .agg(F.array(*[F.sum(F.col("sentiment").getItem(i)) for i in range(3)]))

    query = sum_sentiment\
        .writeStream \
        .outputMode("complete") \
        .foreachBatch(lambda df, epoch_id: send_sentiment_counter(df, epoch_id, 'http://localhost:10000/update_sentiment_counters')) \
        .trigger(processingTime='2 seconds')\
        .start()

    return query


def main():

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

    query1 = get_top_hashtags(df)
    query2 = get_sentiment_counter(df)

    query1.awaitTermination()
    query2.awaitTermination()


if __name__ == '__main__':
    main()
