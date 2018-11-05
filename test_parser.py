import json
import requests
import time
import re


def parse_haematopathology_results(rows):
    # Sample row: * MCHC 32.8 310—355 g/L
    typical_result_regex = r'^\*\s+([\w+\s?—?]*)\s+(\d*\.?\d*)\s+([^\s]+)\s+(.*$)'

    # Sample row: * EOSINOPHIL 0.02 L 0.09—0.90 X 10*9/L
    low_result_regex = r'^\*\s+([\w+\s?—?]*)\s+(\d*\.?\d*)\s+l\s+([^\s]+)\s+(.*$)'

    records = []
    # Only parse rows beginning with a bullet point
    for row in rows:
        match = re.match(low_result_regex, row, re.I) or re.match(typical_result_regex, row, re.I)

        if not match:
            continue

        groups = match.groups()

        record = {
            'test_name': groups[0],
            'result': groups[1],
            'flag_reference': groups[2],
            'units': groups[3]
        }

        if re.match(low_result_regex, row, re.I):
            record['low'] = True

        records.append(record)

    return records


OCR_URL = 'https://ocr-processor.herokuapp.com'

OPERATIONS_DICT = {
    'Haematopathology': parse_haematopathology_results
}

TEMPLATE_REGEXES = {
    'Haematopathology': r'(test\s+name)\s+(resu.ts)\s+(f.ag\s+reference)\s+(un.ts)'
}

def main():
    # Connect to server, wake up dyno
    test_request = requests.get(OCR_URL)
    if test_request.status_code != 200:
        print('Can\'t connect to OCR service. Exiting...')

    print('Connected to OCR service.')

    data = {
        'filename': 'test_blood_work',
    }

    request = requests.post(OCR_URL + '/ocr_pdf', json=data)
    print('Performing OCR for ' + data['filename'])

    start_time = time.time()
    response = get_result(request)
    end_time = time.time()
    total_time = end_time - start_time

    status = response['state']

    if status != 'SUCCESS':
        print('Failed to perform OCR: ' + response['status'])
        return

    print('Finished OCR in ' + str(round(total_time, 4)) + 's')
    result = response['result']
    result_rows = result.split('\n')

    templates = list(TEMPLATE_REGEXES.keys())
    index = 0
    found_template = False
    while not found_template:
        template = templates[index]
        regex = TEMPLATE_REGEXES.get(template)
        for row in result_rows:
            if re.match(regex, row, re.I):
                print(template + ' results record detected.')
                found_template = True
                break

        if not found_template:
            index += 1

    if not found_template:
        print('No template found.')
        return

    detected_template = templates[index]

    records = OPERATIONS_DICT[detected_template](result_rows)

    print('Found ' + str(len(records)) + ' records:')
    for record in records:
        print(record)

    return


def get_result(r):
    ping_url = r.headers['Location']

    response = requests.get(ping_url).json()
    status = response['state']

    while status == 'PENDING':
        print('Pending result...')
        time.sleep(2)
        response = requests.get(ping_url).json()
        status = response['state']

    return response


main()
