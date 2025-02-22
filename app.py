from flask import Flask, request, render_template, jsonify  # type: ignore
from werkzeug.utils import secure_filename
import os
import uuid

# import shutil
# import concurrent.futures
from search_engines import SearchEngineFactory
from database import SqliteDatabaseHelper


app = Flask(__name__)
ORIGINAL_FILE_NAME = "original"
UPLOAD_FOLDER = "static/requests"
ALLOWED_EXTENSIONS = ["gif", "jpg", "jpeg", "png"]
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return (
        "." in filename 
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def search_result_and_save(uuid, original_image_path, engine="google"):
    is_ok = True
    try:
        search_engine = SearchEngineFactory.get_search_engine(
            engine, uuid, original_image_path
        )
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


def get_results_from_history(uuid):
    result = { "error": None}
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
    items = []
    return render_template("index.html", items=items)


@app.route("/history")
def about():
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
    # return jsonify(history)
    return render_template("history.html", items=history)


@app.route("/api/data")
def get_data():
    return jsonify({"message": "Дані отримано з сервера!"})


# @app.route('/api/post_data', methods=['POST'])
# def post_data():
#     # Отримання даних з POST-запиту
#     data = request.get_json()
#     # Обробка даних
#     message = f"Отримано дані: {data}"
#     return jsonify({'message': message})


@app.route("/upload", methods=["POST"])
def upload_file():
    response = {"error": "", "content": "", "original_image": "static/images/img1.png"}

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
        original_image_path = os.path.join(
            path, ORIGINAL_FILE_NAME + "." + filename.split(".")[-1]
        )
        file.save(original_image_path)
        response["original_image"] = original_image_path
        db.save_original_image(uuid=request_id, image_name=original_image_path)

        search_result_and_save(
            uuid=request_id, original_image_path=original_image_path
        )
        
        result_dict = get_results_from_history(uuid=request_id)
        
        response["content"] = render_template(
            "includes/_list_items_cards.html", items=result_dict["result"]
        )
        # response["content"] = result_list
        return jsonify(response), 200
    else:
        response["error"] = "Only type file: " + ", ".join(ALLOWED_EXTENSIONS)
        return jsonify(response), 200


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    db = SqliteDatabaseHelper()
    app.run(debug=True)
