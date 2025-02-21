from urllib import request
from flask import Flask, render_template, jsonify # type: ignore
import lorem

app = Flask(__name__)

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

@app.route('/api/post_data', methods=['POST'])
def post_data():
    # Отримання даних з POST-запиту
    data = request.get_json()
    # Обробка даних
    message = f"Отримано дані: {data}"
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)