import unittest
from gfl_sdk.external_integrations import get_crispor_guides

class TestCRISPOR(unittest.TestCase):

    def test_get_crispor_guides(self):
        seq = 'GAGTCCGAGCAGAAGAAGA'  # Ejemplo secuencia corta
        result = get_crispor_guides(seq)
        self.assertIsInstance(result, dict)
        self.assertIn('guides', result)

if __name__ == '__main__':
    unittest.main()
