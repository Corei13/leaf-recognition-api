from flask import Flask
import json
from flask import jsonify
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/get-photo',  methods=['POST', 'GET'])
def analysis_photo():
    print(request.json['url'])
    data = {
        'url': request.json['url'],
        'status': 'ok' 
    }
    return jsonify({'data': data}), 201
