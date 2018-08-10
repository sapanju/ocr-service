from flask import Flask, request, url_for, jsonify, make_response
from functools import wraps
import os
import tasks

app = Flask(__name__)

password = os.environ['BASIC_AUTH_TOKEN']


def auth_required(f):
    @wraps(f)
    def decorated():
        auth = request.authorization
        if auth and auth.password == password:
            return f()

        return 'Failed to authenticate'

    return decorated


def get_app():
    return app


@app.route('/', methods=['GET'])
@auth_required
def hello():
    return 'Server is up.'


@app.route('/ocr', methods=['POST'])
@auth_required
def do_ocr():
    data = request.get_json()
    task = tasks.perform_ocr.delay(data)
    result = task.wait()
    return result