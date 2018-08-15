from celery import Celery
import urllib.request
import time
import io
import os
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
        flaskApp = app.get_app()
        with flaskApp.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

@celery.task
def perform_ocr(data):
    image_buffer = data['image_buffer']
    image = io.BytesIO(image_buffer)

    filename = data['filename'];
    print('Performing OCR for ' + filename)
   
    start_time = time.time()
    result = pytesseract.image_to_string(Image.open(image))
    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')

    return result




