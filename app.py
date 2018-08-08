from flask import Flask, request, url_for, jsonify
import urllib.request

try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract


app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return 'Server is up.'

@app.route('/ocr', methods=['POST'])
def do_ocr():
    data = request.get_json()
    image_url = data['image_url']
    filename = image_url.split('/')[-1] + '.png'

    urllib.request.urlretrieve(image_url, filename)

    print('Performing OCR for image ' + filename)

    return pytesseract.image_to_string(Image.open(filename))