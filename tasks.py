from celery import Celery
import urllib.request
import time
import os
import base64
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
    with open(filename, 'wb') as fh:
        fh.write(base64.decodebytes(buffer_bytes))

    result = pytesseract.image_to_string(Image.open(filename))

    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')

    return {
        'status': 'Task completed.',
        'result': result
    }
