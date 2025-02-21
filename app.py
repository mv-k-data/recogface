from flask import Flask, request, render_template, jsonify  # type: ignore
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
ORIGINAL_FILE_NAME = "original"
REQUESTS_FOLDER = "requests"
ALLOWED_EXTENSIONS = ["gif", "jpg", "jpeg", "png"]
app.config["REQUESTS_FOLDER"] = REQUESTS_FOLDER


def allowed_file(filename):
    return (
        "." in filename 
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    items = [
        {
            "image": "img1.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img2.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img1.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img2.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img1.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img2.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
        {
            "image": "img1.png",
            "title": "bla bla bla",
            "url": "https://www.example.com/result1",
        },
    ]
    return render_template("index.html", items=items)


@app.route("/history")
def about():
    l = [
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img2.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img2.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
    ]
    return render_template("history.html", l=l)


@app.route("/api/data")
def get_data():
    return jsonify({"message": "Дані отримано з сервера!"})


@app.route("/upload", methods=["POST"])
def upload_file():
    response = {"error": "", "content": ""}

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
        path = os.path.join(app.config["REQUESTS_FOLDER"], request_id)
        os.mkdir(path)
        file.save(
            os.path.join(path, ORIGINAL_FILE_NAME + "." + filename.split(".")[-1])
        )

        # тут має бути код Миколи
        items = [
            {
                "image": "img1.png",
                "title": "bla bla bla",
                "url": "https://www.example.com/result1",
            },
            {
                "image": "img2.png",
                "title": "bla bla bla",
                "url": "https://www.example.com/result1",
            },
            {
                "image": "img1.png",
                "title": "bla bla bla",
                "url": "https://www.example.com/result1",
            },
        ]
        response["content"] = render_template(
            "includes/_list_items_cards.html", items=items
        )
        return jsonify(response), 200
    else:
        response["error"] = "Only type file: " + ", ".join(ALLOWED_EXTENSIONS)
        return jsonify(response), 200


if __name__ == "__main__":
    if not os.path.exists(REQUESTS_FOLDER):
        os.makedirs(REQUESTS_FOLDER)

    app.run(debug=True)
