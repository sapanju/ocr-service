from celery import Celery
import urllib.request
import os
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

celery = Celery('celeryApp')
celery.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                   CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

@celery.task
def perform_ocr(data):
    image_url = data['image_url']
    filename = image_url.split('/')[-1] + '.png'

    urllib.request.urlretrieve(image_url, filename)

    print('Performing OCR for image ' + filename)

    return pytesseract.image_to_string(Image.open(filename))




