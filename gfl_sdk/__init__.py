from .parser import parse

from .external_integrations import get_crispor_guides, get_projects

def simulate_edit(edit: dict) -> dict:
    # Simulated basic edit function placeholder
    return {"edit": edit, "result": "simulated"}

def simulate_advanced_edit(edit: dict) -> dict:
    result = simulate_edit(edit)
    result['effect'] = 'complex simulation placeholder'
    return result

parse_phrase = parse
from .external_integrations.enhancers import Enhancer, AAVVector, simulate_enhancer_expression
