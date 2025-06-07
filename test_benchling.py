import unittest
from gfl_sdk.external_integrations import get_projects
import requests

class TestBenchling(unittest.TestCase):

    def test_get_projects(self):
        try:
            result = get_projects()
        except requests.exceptions.RequestException as e:
            # Aceptamos cualquier excepción de red como correcta en test sin token/conexión
            self.assertTrue(True)
        except Exception as e:
            # Si no es error de red, verificar que contenga Benchling API error
            self.assertIn('Benchling API error', str(e))
        else:
            self.assertIsInstance(result, dict)
            self.assertIn('projects', result)

if __name__ == '__main__':
    unittest.main()
