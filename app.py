from flask import Flask
import json
from flask import jsonify
from flask import request
import requests
app = Flask(__name__)


AIRTABLE_BASE_ID= "appTjCVPvyujwYVh8"
AIRTABLE_API_KEY= "keysdvFSVMD8PvvPE"
AIRTABLE_TABLE_NAME= "results-table"

endpoint=f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'


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

    add_to_airtable("THE_RANDOM_ID", "2/2/22", "fdsafasfdsafdasdfasdfasdfafdasdfasfds")
    
    return jsonify({'data': data}), 201


def add_to_airtable(id="", date="", result=""):
    if result is None:
        return
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
    "records": [
            {
            "fields": {
                "id": id,
                "date": date,
                "result": result
                }
            }
        ]
    }
    r = requests.post(endpoint, json=data, headers=headers)
    return r.status_code == 200
