from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

from concurrent.futures import ThreadPoolExecutor
from libs.search_engines import SearchEngineFactory
from libs.database import SqliteDatabaseHelper
from loguru import logger

app = Flask(__name__)
ORIGINAL_FILE_NAME = "original"
UPLOAD_FOLDER = "static/requests"
ALLOWED_EXTENSIONS = ["gif", "jpg", "jpeg", "png"]
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SEARCHES_ENGINES"] = {
    "google": {"is_enabled": True, "is_selected": True, "lable": "Google", "color": "#ff7f50"},
    "bing": {"is_enabled": True, "is_selected": False, "lable": "Bing", "color": "#5a76ef"},
    "yandex": {"is_enabled": False, "is_selected": False, "lable": "Yandex", "color": "#dc7373"},
    "tineye": {"is_enabled": True, "is_selected": False, "lable": "TinEye", "color": "#52bfbf"},
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def search_result_and_save(uuid, original_image_path, engine="google"):
    is_ok = True
    try:
        search_engine = SearchEngineFactory.get_search_engine(engine, uuid, original_image_path)
        result_list = search_engine.search_images()
    except Exception as e:
        is_ok = False
        raise f"Error: {str(e)}"

    if is_ok:
        search_results = [
            (
                i["uuid"],
                i["search_engine"],
                i["image_name"],
                i["image_url"],
                i["image_text"],
                i["full_image_name"],
            )
            for i in result_list
        ]
        db.save_search_result(search_results=search_results)


def perform_search(item):
    search_result_and_save(**item)


def get_results_from_history(uuid):
    result = {"error": None}
    history_details = db.get_history_details(uuid=uuid)
    history_details = [
        {
            "original_image": i[0],
            "search_engine": i[1],
            "image_text": i[2],
            "image_url": i[3],
            "full_image_name": i[4],
        }
        for i in history_details
    ]
    result["result"] = history_details
    return result


@app.route("/")
def index():
    return render_template(
        "index.html.j2", items=get_results_from_history(uuid=request.args.get("history_id", default=""))["result"]
    )


@app.route("/history")
def history():
    history = db.get_search_history()
    history = [
        {
            "uuid": i[0],
            "image_name": i[1],
            "created_at": i[2],
            "search_engines": i[3],
            "count": i[4],
        }
        for i in history
    ]
    return render_template("history.html.j2", items=history)


@app.route("/upload", methods=["POST"])
def upload_file():
    response = {"error": "", "content": "", "original_image": "static/images/img1.png"}
    selected_engines = request.form.get("selected_engines", "").split(",")

    request_id = str(uuid.uuid4())

    if "file" not in request.files:
        response["error"] = "File not found"
        return jsonify(response), 200

    file = request.files["file"]

    if file.filename == "":
        response["error"] = "File not found"
        return jsonify(response), 200

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], request_id)
        os.mkdir(path)
        original_image_path = os.path.join(path, ORIGINAL_FILE_NAME + "." + filename.split(".")[-1])
        file.save(original_image_path)
        response["original_image"] = original_image_path
        db.save_original_image(uuid=request_id, image_name=original_image_path)

        app.logger.debug("Start searching...")
        engines = [
            {"uuid": request_id, "original_image_path": original_image_path, "engine": e} for e in selected_engines
        ]
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(perform_search, engines)
        app.logger.debug("End searching")
        result_dict = get_results_from_history(uuid=request_id)

        response["content"] = render_template("includes/_list_items_cards.html.j2", items=result_dict["result"])
        return jsonify(response), 200
    else:
        response["error"] = "Only type file: " + ", ".join(ALLOWED_EXTENSIONS)
        return jsonify(response), 200


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    db = SqliteDatabaseHelper()
    app.run(debug=True)
