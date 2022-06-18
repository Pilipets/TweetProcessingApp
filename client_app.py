from flask import Flask, jsonify, request
from flask import render_template

app = Flask('twitter-stats')
hashtags_count = {'words': [], 'count': []}
sentiment_counters = {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0}


@app.route("/")
def get_chart_page():
    global hashtags_count
    global sentiment_counters

    return render_template('stats.html', hashtags_count=hashtags_count, sentiment_counters=sentiment_counters)


@app.route('/hashtags_count', methods=['GET'])
def refresh_chart_data():
    print("Hashtags count now:", hashtags_count)
    return jsonify(hashtags_count)


@app.route('/sentiment_counters', methods=['GET'])
def refresh_hashtags_count():
    print("Sentiment_counters now:", sentiment_counters)
    return jsonify(sentiment_counters)


@app.route('/update_hashtags_count', methods=['POST'])
def update_hashtags_count():
    global hashtags_count
    hashtags_count = request.get_json()

    print("Received hashtags_count:", hashtags_count)
    return "success", 201


@app.route('/update_sentiment_counters', methods=['POST'])
def update_sentiment_counters():
    global sentiment_counters
    sentiment_counters = request.get_json()

    print("Received sentiment_counters:", sentiment_counters)
    return "success", 201


if __name__ == "__main__":
    app.run(host='localhost', port=10000)
