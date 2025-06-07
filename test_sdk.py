import unittest
from gfl_sdk import parse_phrase, simulate_edit

class TestGflSdk(unittest.TestCase):

    def test_parse_phrase(self):
        result = parse_phrase('EDIT:Base(A→G@1001)')
        self.assertTrue(result.get('parsed', False))
        self.assertIn('input', result)

    def test_simulate_edit(self):
        edit = {'type': 'base_change', 'pos': 1001, 'from': 'A', 'to': 'G'}
        result = simulate_edit(edit)
        self.assertEqual(result.get('result'), 'simulated')

if __name__ == '__main__':
    unittest.main()
