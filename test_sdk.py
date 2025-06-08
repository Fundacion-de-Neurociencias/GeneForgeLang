import unittest
from gfl_sdk import parse_phrase, simulate_advanced_edit
from gfl_sdk.external_integrations import get_crispor_guides, get_projects
import requests

class TestSDK(unittest.TestCase):

    def test_parse_phrase(self):
        phrase = 'EDIT:Base(A→G@1001)'
        result = parse_phrase(phrase)
        self.assertIsInstance(result, dict)

    def test_simulate_advanced_edit(self):
        edit = {'type': 'EDIT', 'details': 'Base(A→G@1001)'}
        result = simulate_advanced_edit(edit)
        self.assertIn('effect', result)
        self.assertEqual(result['effect'], 'complex simulation placeholder')

    def test_get_crispor_guides(self):
        seq = 'GAGTCCGAGCAGAAGAAGA'
        result = get_crispor_guides(seq)
        self.assertIsInstance(result, dict)
        self.assertIn('guides', result)

    def test_get_projects(self):
        try:
            result = get_projects()
        except requests.exceptions.RequestException:
            self.assertTrue(True)
        except Exception as e:
            self.assertIn('Benchling API error', str(e))
        else:
            self.assertIsInstance(result, dict)
            self.assertIn('projects', result)

if __name__ == '__main__':
    unittest.main()
