from celery import Celery
import urllib.request
import time
import os
import base64
import tempfile
from pdf2image import convert_from_path

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

import app

celery = Celery('celeryApp')
celery.conf.update(
    BROKER_URL=os.environ['REDIS_URL'],
    CELERY_RESULT_BACKEND=os.environ['REDIS_URL']
)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        flask_app = app.get_app()
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

@celery.task
def perform_ocr(data):
    image_buffer = data['image_buffer']
    filename = data['filename'] + '.png'

    print('Performing OCR for ' + filename)
    start_time = time.time()

    buffer_string = urllib.parse.unquote(image_buffer)  # decode URI component to base64 string
    buffer_bytes = buffer_string.encode()  # encode to bytes
    with tempfile.NamedTemporaryFile(suffix='.png') as image_file:
        image_file.write(base64.decodebytes(buffer_bytes))
        image_file.flush()
        result = pytesseract.image_to_string(Image.open(image_file.name))

    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')

    return {
        'status': 'Task completed.',
        'result': result
    }

@celery.task
def perform_ocr_for_pdf(data):
    filename = data['filename']

    print('Performing OCR for ' + filename)
    start_time = time.time()

    pages = convert_from_path(filename + '.pdf', 500)
    for page in pages:
        page.save(filename + '.png', 'PNG')

    result = pytesseract.image_to_string(Image.open(filename + '.png'))

    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')

    return {
        'status': 'Task completed.',
        'result': result
    }
