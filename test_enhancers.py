import unittest
from gfl_sdk.external_integrations.enhancers import Enhancer, AAVVector, simulate_enhancer_expression

class TestEnhancers(unittest.TestCase):

    def test_enhancer_info(self):
        enhancer = Enhancer('ATCGATCG', cell_type='interneuron', species='mouse')
        info = enhancer.info()
        self.assertEqual(info['sequence'], 'ATCGATCG')
        self.assertEqual(info['cell_type'], 'interneuron')
        self.assertEqual(info['species'], 'mouse')

    def test_aav_vector_description(self):
        enhancer = Enhancer('GGCTAGCT', cell_type='pyramidal_neuron')
        vector = AAVVector('AAV-PHP.B', enhancer, 'GFP', target_species='mouse')
        desc = vector.description()
        self.assertIn('capsid', desc)
        self.assertIn('enhancer', desc)
        self.assertIn('cargo_gene', desc)
        self.assertEqual(desc['cargo_gene'], 'GFP')

    def test_simulate_expression_specific(self):
        enhancer = Enhancer('AAAAGGGG', cell_type='striatal_interneuron')
        vector = AAVVector('AAV9', enhancer, 'ChR2')
        result = simulate_enhancer_expression(vector, 'striatal_interneuron')
        self.assertEqual(result['predicted_expression'], 'high')
        self.assertEqual(result['specificity'], 'specific')

    def test_simulate_expression_off_target(self):
        enhancer = Enhancer('TTTTCCCC', cell_type='cortical_pyramidal')
        vector = AAVVector('AAV9', enhancer, 'ChR2')
        result = simulate_enhancer_expression(vector, 'microglia')
        self.assertEqual(result['predicted_expression'], 'low')
        self.assertEqual(result['specificity'], 'off-target or minimal')

if __name__ == '__main__':
    unittest.main()
