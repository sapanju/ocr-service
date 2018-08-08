from flask import Flask, request, url_for, jsonify
import tasks

app = Flask(__name__)

def get_app():
    return app

@app.route('/', methods=['GET'])
def hello():
    return 'Server is up.'

@app.route('/ocr', methods=['POST'])
def do_ocr():
    data = request.get_json()
    task = tasks.perform_ocr.delay(data)
    result = task.wait()
    return result