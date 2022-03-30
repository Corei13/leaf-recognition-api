import os

import requests
from flask import Flask, jsonify, request
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "./temp"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

AIRTABLE_BASE_ID = "appTjCVPvyujwYVh8"
AIRTABLE_API_KEY = "keysdvFSVMD8PvvPE"
AIRTABLE_TABLE_NAME = "results-table"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


endpoint = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/analyze", methods=["POST", "GET"])
def analysis_photo():
    if request.method == "POST":
        file = request.files["photo"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.seek(0)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "temp", filename
            )
            # todos
            # catch other fields data
            # add to airtable
            analyzed_results = analyze(path)
            # add result to airtable
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return jsonify({"data": "data"}), 201


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze(path):
    im = Image.open(path)
    witdth, height = im.size

    print(witdth, height)

    return [("2.5", 0.7), ("1.5", 0.2)]


def add_to_airtable(id="", date="", result=""):
    if result is None:
        return
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"records": [{"fields": {"id": id, "date": date, "result": result}}]}
    r = requests.post(endpoint, json=data, headers=headers)
    return r.status_code == 200
