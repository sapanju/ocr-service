import json
import requests

url = 'https://ocr-processor.herokuapp.com'
data = {
  'filename': 'test_blood_work',
}

# Blood work record regexes
r = requests.post(url + '/ocr_pdf', json=data)

ping_url = r.headers['Location']

response = requests.get(ping_url)
status = response.json()['state']

while status == 'PENDING':
    response = requests.get(ping_url)
    status = response.json()['state']

print(status)
print(response.json()['result'])