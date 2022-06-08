import json
import os
from datetime import date, datetime

import requests
from firebase_admin import credentials, firestore, initialize_app, storage
from flask import Flask, jsonify, request
from PIL import Image
from werkzeug.utils import secure_filename

from src import analyze, preprocess, segments

UPLOAD_FOLDER = "./temp/images"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

app = Flask(__name__)
app.debug = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

cred = credentials.Certificate("./tea-firebase.json")
initialize_app(
    cred,
    {
        "storageBucket": "aracadia-leaf-analysis.appspot.com",
        "databaseURL": "https://arcadia-leaf-analysis.firebaseio.com",
    },
)

db = firestore.client()


@app.route("/", methods=["GET"])
def start():
    return "Hello Love v0.0.2"


@app.route("/test/<filename>", methods=["GET"])
def test(filename):
    result = segment_leaves(filename)
    return jsonify(result)


@app.route("/analyze", methods=["POST"])
def analysis_photo():
    if request.method == "POST":
        file = request.files["photo"]
        try:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.seek(0)

                file.save(os.path.join("./temp/", filename))
                path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "./temp", filename
                )

                asst_manage_name = request.form.get("asst_manage_name")
                estate_name = request.form.get("estate_name")
                manager_name = request.form.get("manager_name")
                slot = request.form.get("slot")
                mode = request.form.get("mode")
                type = request.form.get("type")

            # upload image to firebase storage
            try:
                img_url = upload_firebase_storage(path, filename)
            except Exception as e:
                return f"An error occured {e}"

            segment_leaves(filename)
            path = os.getcwd() + "/temp/images"
            directory = os.fsencode(path)
            resultArr = []
            for file in os.listdir(path):
                chunk_file_name = os.fsdecode(file)
                analyzed_results = predict(chunk_file_name)
                print(analyzed_results, "analysis")
                sorted_results = sorted(
                    analyzed_results.items(), key=lambda x: x[1], reverse=True
                )
                result_object = {}
                for result in sorted_results:
                    result_object[result[0]] = result[1]
                    print(result, "tup")
                resultArr.append(result_object)
                os.remove(os.path.join(path + "/" + chunk_file_name))
                os.remove(os.path.join(path + "/" + "converted-" + chunk_file_name))
            data = {
                "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "asst_manage_name": asst_manage_name,
                "estate_name": estate_name,
                "manager_name": manager_name,
                "slot": slot,
                "img_url": img_url,
                "mode": mode,
                "type": type,
                "resultArr": resultArr,
            }
            try:
                if mode == "multiple":
                    newResultRef = db.collection("results").document()
                    newResultRef.set(data)
                else:
                    newResultRef = db.collection("test-results").document()
                    newResultRef.set(
                        {
                            "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": type,
                            "resultArr": resultArr,
                            "img_url": img_url,
                        }
                    )
            except Exception as e:
                return f"An error occured {e}"

            path = os.getcwd() + "/temp"
            os.remove(os.path.join(path + "/" + filename))
        except Exception as e:
            return f"Error occured {e}"

    return jsonify({"data": data}), 201


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_firebase_storage(path, filename):
    img = Image.open(path)
    # img.size(200, 374)
    img = img.resize((500, 400), Image.ANTIALIAS)
    resized_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "./temp", "resized-" + filename
    )
    img.save(resized_path, optimize=True, quality=95)
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    # blob.upload_from_filename(path)
    #  blob.upload_from_file(img)
    with open(resized_path, "rb") as my_file:
        blob.upload_from_file(my_file)
    blob.make_public()
    os.remove(os.path.join(resized_path))
    return blob.public_url
    # return "demu url"


def predict(filename):
    original_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER, filename
    )
    converted_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        UPLOAD_FOLDER,
        "converted-" + filename,
    )
    preprocess.convert_image(original_path, converted_path)
    result = analyze.analyze(converted_path)
    return result


def segment_leaves(filename):
    original_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "temp",
        filename,
    )
    converted_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        UPLOAD_FOLDER,
        "converted-" + filename,
    )

    results = segments.segments(original_path)

    # print(results)
    return str(results)
