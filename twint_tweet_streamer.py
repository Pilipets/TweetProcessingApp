import twint
import kafka
import os
import pandas
import time
class TweetStreamer:
    def __init__(self, request_period):
        self.request_period = request_period

    def get_tweets_df(self, search, limit=3):
        c = twint.Config()
        c.Search = search
        c.Limit = limit
        c.Pandas = True
        c.Pandas_clean = True
        
        twint.run.Search(c)
        return twint.output.panda.Tweets_df[["username", "tweet"]]

    def stream_data(self, search, limit):
        producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')

        while True:
            df = self.get_tweets_df(search, limit)

            for tweet_text in df['tweet']:
                producer.send('tweet-stream', tweet_text.encode('utf-8'))

            time.sleep(self.request_period)

def test1():
    TweetStreamer(15).stream_data("ukraine war", 5)

def get_big_data_csv(search, limit, out_path):
    if not os.path.exists(out_path):
        c = twint.Config()
        c.Store_csv = True
        c.Search = search
        c.Limit = limit
        c.Lang = 'en'
        #c.Custom = ["username", "tweet"]
        c.Output = out_path

        twint.run.Search(c)

    df = pandas.read_csv(out_path)
    return df

def test2():
    df = get_big_data_csv('ukraine war', 10, 'data/ukraine_war_ds.csv')
    producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')

    for tweet_text in df.tweet:
        producer.send('tweet-stream', tweet_text.encode('utf-8'))
        print(tweet_text)

if __name__ == '__main__':
    #test1()
    test2()
