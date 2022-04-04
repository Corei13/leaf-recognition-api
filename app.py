import os
from datetime import date

import requests
from firebase_admin import credentials, initialize_app, storage
from flask import Flask, jsonify, request
from PIL import Image
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "./temp"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
AIRTABLE_BASE_ID = "appb7gS3ne4YyBIf4"
AIRTABLE_API_KEY = "keysdvFSVMD8PvvPE"
AIRTABLE_TABLE_NAME = "results"

endpoint = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

app = Flask(__name__)
app.debug = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cred = credentials.Certificate("./tea-firebase.json")
initialize_app(cred, {"storageBucket": "tea-leaf-86440.appspot.com"})


@app.route("/")
def hello_world():
    return "Hello, Love!"


@app.route("/analyze", methods=["POST", "GET"])
def analysis_photo():
    if request.method == "POST":
        file = request.files["photo"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.seek(0)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "./temp", filename
            )

            asst_manage_name = request.form.get("asst_manage_name")
            estate_name = request.form.get("estate_name")
            manager_name = request.form.get("manager_name")
            slot = request.form.get("slot")

            # upload image to firebase storage
            img_url = upload_firebase_storage(path, filename)
            analyzed_results = analyze(path)
            add_to_airtable(
                asst_manage_name,
                estate_name,
                manager_name,
                slot,
                img_url,
                analyzed_results,
            )
            data = {
                "Created": date.today(),
                "asst_manage_name": asst_manage_name,
                "estate_name": estate_name,
                "manager_name": manager_name,
                "slot": slot,
                "img_url": img_url,
                "type1": analyzed_results[0][0],
                "value1": str(analyzed_results[0][1]),
                "type2": analyzed_results[1][0],
                "value2": str(analyzed_results[1][1]),
                "type3": analyzed_results[2][0],
                "value3": str(analyzed_results[2][1]),
            }
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return jsonify({"data": data}), 201


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_firebase_storage(path, filename):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    # blob.upload_from_filename(path)
    with open(path, "rb") as my_file:
        blob.upload_from_file(my_file)
    blob.make_public()

    return blob.public_url


def analyze(path):
    im = Image.open(path)
    width, height = im.size
    print(width, height)

    return [("Two & half", 0.7), ("Three & half", 0.2), ("Four & half", 0.1)]


def add_to_airtable(
    asst_manage_name, estate_name, manager_name, slot, img_url, analyzed_results
):

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "records": [
            {
                "fields": {
                    "asst_manage_name": asst_manage_name,
                    "estate_name": estate_name,
                    "manager_name": manager_name,
                    "slot": slot,
                    "img_url": img_url,
                    "analyzed_results": str(analyzed_results),
                    "type1": analyzed_results[0][0],
                    "value1": str(analyzed_results[0][1]),
                    "type2": analyzed_results[1][0],
                    "value2": str(analyzed_results[1][1]),
                    "type3": analyzed_results[2][0],
                    "value3": str(analyzed_results[2][1]),
                }
            }
        ]
    }
    r = requests.post(endpoint, json=data, headers=headers)

    return r.status_code == 200
