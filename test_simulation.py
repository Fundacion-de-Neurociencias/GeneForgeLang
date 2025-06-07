import unittest
from gfl_sdk import simulate_edit

class TestSimulation(unittest.TestCase):

    def test_simulate_edit(self):
        edit = {'type': 'EDIT', 'details': 'Base(A→G@1001)'}
        result = simulate_edit(edit)
        self.assertIn('result', result)
        self.assertEqual(result['result'], 'simulated')

if __name__ == '__main__':
    unittest.main()
