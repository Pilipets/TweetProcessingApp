import kafka
import tweepy
import configparser

def GetTokensV1(fpath):
    config = configparser.ConfigParser()
    config.read(fpath)

    main_config = config['MAIN']
    consumer_key = main_config['consumer_key']
    consumer_secret = main_config['consumer_secret']
    access_key = main_config['access_token']
    access_secret = main_config['access_token_secret']

    return consumer_key, consumer_secret, access_key, access_secret

def GetTokenV2(fpath):
    return open(fpath).read()

class TweetStreamer(tweepy.StreamingClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')

    def on_errors(self, errors):
        print("Error received", errors)
        return super().on_errors(errors)

    def on_tweet(self, tweet):
        print("On tweet:", tweet.data)
        self.producer.send('tweet-stream', tweet.text.encode('utf-8'))
        return super().on_tweet(tweet)

def test1():
    token = GetTokenV2('credentials_v2.txt')
    client = tweepy.Client(token)

    resp = client.get_user(username='gleb_pilipets')
    print(resp)

def test2():
    token = GetTokenV2('credentials_v2.txt')
    stream = TweetStreamer(token)

    stream.sample()

if __name__ == '__main__':
    test2()