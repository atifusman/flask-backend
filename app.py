from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to my backend!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"data": "This is a sample response", "status": "success"})

if __name__ == '__main__':
    app.run(debug=True)