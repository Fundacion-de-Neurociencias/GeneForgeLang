# GeneForgeLang (GFL) - Python SDK and External Integrations

## Overview
GeneForgeLang is a symbolic generative language for DNA, RNA, and protein design with AI-compatible logic.

## Python SDK
- parse_phrase(phrase: str) -> dict: Parse GFL phrase into AST.
- simulate_edit(edit: dict) -> dict: Simulate a genetic edit (basic).
- simulate_advanced_edit(edit: dict) -> dict: Advanced simulation placeholder.

## External Integrations

### CRISPOR API
- Function: get_crispor_guides(sequence: str, genome: str = 'hg38') -> dict
- Returns CRISPR guide predictions for input DNA sequence.

### Benchling API
- Function: get_projects() -> dict
- Fetches project list from Benchling (requires API token).

## Testing
Run tests with:
python -m unittest test_sdk.py
python -m unittest test_crispor.py
python -m unittest test_benchling.py
