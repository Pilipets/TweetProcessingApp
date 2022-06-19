
# Start Zookeper + Kafka broker
cd ~/Downloads/kafka_2.13-3.2.0/  
bin/zookeeper-server-start.sh config/zookeeper.properties  
bin/kafka-server-start.sh config/server.properties  

# Setup python env
Install python dependencies from deploy/requirements.txt  
Install twint separately  
Install javac for Apache Spark  

# Run the UI logic
python client_app.py  
open localhost:10000 in browser  

# Run the core logic 
python tweet_reader.py

# Run the streaming logic
python twint_tweet_streamer.py or python tweepy_tweet_streamer.py