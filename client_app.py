from flask import Flask, jsonify, request
from flask import render_template

def get_empty_stats():
	return {'labels':[], 'values':[]}

app = Flask('twitter-hashtags')
stats_data = get_empty_stats()

@app.route("/")
def get_chart_page():
	global stats_data
	stats_data = get_empty_stats()
	return render_template('stats.html', labels=stats_data.get('labels'), values=stats_data.get('values'))

@app.route('/refreshData')
def refresh_chart_data():
	print("Stats data now:", stats_data)
	return jsonify(stats_data)

@app.route('/updateData', methods=['POST'])
def update_chart_data():
	global stats_data
	stats_data = request.get_json()

	print("Received data:", stats_data)
	return "success", 201

if __name__ == "__main__":
	app.run(host='localhost', port=10000)