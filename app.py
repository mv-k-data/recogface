from flask import Flask, request, render_template, jsonify # type: ignore
from werkzeug.utils import secure_filename
import lorem
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    items = [
        {"image": "img1.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img2.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img1.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img2.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img1.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img2.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
        {"image": "img1.png", "title": "bla bla bla", "url": "https://www.example.com/result1"},
    ]
    return render_template('index.html', items=items)

@app.route('/history')
def about():
    l = [
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img2.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img2.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
        {"date": "2025-02-20", "image": "img1.png", "count": 10, "history_id": 10},
    ]
    return render_template('history.html', l=l)

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Дані отримано з сервера!'})

# @app.route('/api/post_data', methods=['POST'])
# def post_data():
#     # Отримання даних з POST-запиту
#     data = request.get_json()
#     # Обробка даних
#     message = f"Отримано дані: {data}"
#     return jsonify({'message': message})

@app.route('/upload', methods=['POST'])
def upload_file():
    response = {
        "error": "",
        "content": ""
    }

    request_id = str(uuid.uuid4())

    if 'file' not in request.files:
        response["error"] = "File not found"
        return jsonify(response), 400

    file = request.files['file']

    if file.filename == '':
        response["error"] = "File not found"
        return jsonify(response), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # ext = filename.
        # filename = 'origin'
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/" + request_id, filename))

        path = os.path.join(app.config['UPLOAD_FOLDER'], request_id) 
        os.mkdir(path)
        file.save(os.path.join(path, filename))

        # тут має бути код Миколи
        
        return jsonify({'message': 'Файл успішно завантажено'}), 200
    else:
        response["error"] = "Only type file: " + ", ".join(ALLOWED_EXTENSIONS) 
        return jsonify(response), 400
        

if __name__ == '__main__':
    app.run(debug=True)