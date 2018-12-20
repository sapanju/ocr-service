import json
import time
import re
from pdf2image import convert_from_path
import pytesseract

try:
    import Image
except ImportError:
    from PIL import Image

class HaematopathologyTemplate:
    def __init__(self):
        # Sample row: * MCHC 32.8 310—355 g/L
        self.typical_result_regex = r'^\*\s+(.*)\s+(\d*\.?\d*)\s+([^\s]+)\s+(.*$)'

        # Sample row: * EOSINOPHIL 0.02 L 0.09—0.90 X 10*9/L
        self.low_result_regex = r'^\*\s+(.*)\s+(\d*\.?\d*)\s+l\s+([^\s]+)\s+(.*$)'

        # Sample row: * EOSINOPHIL 0.02 H 0.09—0.90 X 10*9/L
        self.high_result_regex = r'^\*\s+(.*)\s+(\d*\.?\d*)\s+h\s+([^\s]+)\s+(.*$)'

    def parse_rows(self, rows):
        records = []
        # Only parse rows beginning with a bullet point
        for row in rows:
            # Strip whitespace after decimals
            row = re.sub('(\d*)\. +', r'\1.', row)

            match = re.match(self.low_result_regex, row, re.I) or \
                    re.match(self.high_result_regex, row, re.I) or \
                    re.match(self.typical_result_regex, row, re.I)

            if not match:
                continue

            groups = match.groups()

            record = {
                'test_name': groups[0],
                'result': groups[1],
                'range': groups[2],
                'unit': groups[3]
            }

            if re.match(self.low_result_regex, row, re.I):
                record['flag'] = 'Low'

            if re.match(self.high_result_regex, row, re.I):
                record['low'] = 'High'

            records.append(record)

        return records


class TemplateFactory:
    def __init__(self):
        self.TEMPLATES = {'Haematopathology': HaematopathologyTemplate}

    def get_template_parser(self, template_name):
        return self.TEMPLATES[template_name]


def perform_ocr_for_pdf(filename):
    print('Performing OCR for ' + filename)
    start_time = time.time()

    pages = convert_from_path(filename + '.pdf', 500)
    for page in pages:
        page.save(filename + '.png', 'PNG')

    result = pytesseract.image_to_string(Image.open(filename + '.png'))

    end_time = time.time()

    total_time = end_time - start_time
    print('Finished OCR in ' + str(round(total_time, 4)) + 's')
    return result


def parse(filename, detected_template):
    result = perform_ocr_for_pdf(filename)
    result_rows = result.split('\n')
    parser = TemplateFactory().get_template_parser(detected_template)()
    return parser.parse_rows(result_rows)


OCR_URL = 'https://ocr-processor.herokuapp.com'

TEMPLATE_REGEXES = {
    'Haematopathology': r'(test\s+name)\s+(resu.ts)\s+(f.ag\s+reference)\s+(un.ts)'
}


def add_golden(filename, records):
    golden_file = open('expected_results/' + filename + '.txt', 'w+')
    golden_file.write(str(records))
    golden_file.close()


def main():
    data = {
        'filename': '/record_input/test_blood_work',
    }

    filename = data['filename']

    result = perform_ocr_for_pdf(filename)
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

    parser = TemplateFactory().get_template_parser(detected_template)()

    records = parser.parse_rows(result_rows)

    print('Found ' + str(len(records)) + ' records:')
    for record in records:
        print(record)

    return records


# main()