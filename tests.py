import unittest
import os
import lab_results_parser

class TestGoldens(unittest.TestCase):
    def test_ocr(self):
        # TODO implement
        return


    def test_parser(self):
        for file in os.listdir('expected_results'):
            with open('expected_results/' + file, 'r') as f:
                expected_result = f.read()

            base_filename = os.path.splitext(file)[0]
            result = lab_results_parser.parse('record_input/' + base_filename, 'Haematopathology')
            self.assertEqual(str(result), expected_result)

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()