from celery import Celery
import urllib.request
import time
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
    image_url = data['image_url']
    filename = image_url.split('/')[-1] + '.png'

    urllib.request.urlretrieve(image_url, filename)

    print('Performing OCR for ' + filename)
   
    start_time = time.time()
    result = pytesseract.image_to_string(Image.open(filename))
    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')

    return result




