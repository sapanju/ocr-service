from flask import Flask, request, url_for, jsonify, make_response
from functools import wraps
import os
import tasks
from celery.result import AsyncResult

app = Flask(__name__)

password = os.environ['BASIC_AUTH_TOKEN']


def auth_required(f):
    @wraps(f)
    def decorated():
        auth = request.authorization
        if auth and auth.password == password:
            return f()

        return 'Failed to authenticate', 401, {}

    return decorated


def get_app():
    return app


@app.route('/', methods=['GET'])
def hello():
    return 'Server is up.'


@app.route('/ocr', methods=['POST'])
@auth_required
def do_ocr():
    data = request.get_json()
    task = tasks.perform_ocr.delay(data)
    return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}

@app.route('/ocr_pdf', methods=['POST'])
def do_ocr_pdf():
    data = request.get_json()
    task = tasks.pdf_to_string.delay(data)
    return jsonify({}), 202, {'Location': url_for('task_status', task_id=task.id)}

@app.route('/status/<task_id>')
def task_status(task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
