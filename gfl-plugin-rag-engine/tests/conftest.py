"""
Pytest Configuration and Fixtures
==================================

Shared fixtures for the RAG Engine plugin test suite.
Provides temporary GFL files, mock data, and test configurations.
"""

import pytest


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def valid_hypothesis_gfl(temp_dir):
    """
    Create a temporary GFL file with valid hypothesis syntax.

    Returns:
        Path to the temporary GFL file
    """
    gfl_content = """
# Valid GFL file with multiple hypotheses

hypothesis:
  id: "H_TP53_LungCancer"
  description: "Test association between TP53 and Lung Cancer"
  if:
    - entity_is:
        gene: "TP53"
    - entity_is:
        disease: "Lung Cancer"
  then:
    - relationship_is: "association"

hypothesis:
  id: "H_BRCA1_BreastCancer"
  description: "Test BRCA1 role in Breast Cancer"
  if:
    - entity_is:
        gene: "BRCA1"
    - entity_is:
        disease: "Breast Cancer"
  then:
    - relationship_is: "causal"

hypothesis:
  id: "H_CFTR_CysticFibrosis"
  description: "CFTR variants in Cystic Fibrosis"
  if:
    - entity_is:
        gene: "CFTR"
    - entity_is:
        disease: "Cystic Fibrosis"
  then:
    - relationship_is: "causal"
"""

    gfl_file = temp_dir / "valid_hypotheses.gfl"
    gfl_file.write_text(gfl_content)
    return gfl_file


@pytest.fixture
def empty_gfl(temp_dir):
    """
    Create an empty GFL file.

    Returns:
        Path to empty GFL file
    """
    gfl_file = temp_dir / "empty.gfl"
    gfl_file.write_text("")
    return gfl_file


@pytest.fixture
def gfl_without_hypotheses(temp_dir):
    """
    Create a valid GFL file without hypothesis blocks.

    Returns:
        Path to GFL file without hypotheses
    """
    gfl_content = """
# Valid GFL file but no hypothesis blocks

loci:
  - id: "BRCA1_locus"
    chromosome: "chr17"
    start: 43044295
    end: 43125483

sequences:
  - id: "test_sequence"
    source: "file://test.fasta"
"""

    gfl_file = temp_dir / "no_hypotheses.gfl"
    gfl_file.write_text(gfl_content)
    return gfl_file


@pytest.fixture
def malformed_gfl(temp_dir):
    """
    Create a malformed GFL file with syntax errors.

    Returns:
        Path to malformed GFL file
    """
    gfl_content = """
# Malformed GFL with invalid syntax
hypothesis:
  id: "broken_hypothesis"
  if: [this is not valid YAML syntax
  then: missing closing bracket
"""

    gfl_file = temp_dir / "malformed.gfl"
    gfl_file.write_text(gfl_content)
    return gfl_file


@pytest.fixture
def mock_pubmed_response():
    """
    Provide mock data simulating a PubMed API response.

    Returns:
        Dictionary with mock PubMed data
    """
    return {
        "PubmedArticle": [
            {
                "MedlineCitation": {
                    "PMID": "12345678",
                    "Article": {
                        "ArticleTitle": "TP53 mutations in lung cancer: molecular mechanisms",
                        "Abstract": {
                            "AbstractText": [
                                "TP53 is frequently mutated in lung cancer. "
                                "This study investigates the molecular mechanisms "
                                "underlying TP53-mediated tumorigenesis in lung tissue."
                            ]
                        },
                    },
                }
            },
            {
                "MedlineCitation": {
                    "PMID": "87654321",
                    "Article": {
                        "ArticleTitle": "Clinical implications of TP53 status in NSCLC",
                        "Abstract": {
                            "AbstractText": [
                                "Non-small cell lung cancer patients with TP53 mutations "
                                "show distinct clinical outcomes. We analyzed 500 cases "
                                "to determine prognostic significance."
                            ]
                        },
                    },
                }
            },
        ]
    }


@pytest.fixture
def mock_pubmed_search_results():
    """
    Provide mock PubMed search results (ID list).

    Returns:
        Dictionary with mock search results
    """
    return {"IdList": ["12345678", "87654321"], "Count": "2", "RetMax": "2"}


@pytest.fixture
def mock_abstracts():
    """
    Provide mock abstract data for testing.

    Returns:
        List of mock abstract dictionaries
    """
    return [
        {
            "pmid": "12345678",
            "title": "TP53 mutations in lung cancer: molecular mechanisms",
            "abstract": (
                "TP53 is frequently mutated in lung cancer. "
                "This study investigates the molecular mechanisms "
                "underlying TP53-mediated tumorigenesis in lung tissue."
            ),
            "gene": "TP53",
            "disease": "Lung Cancer",
        },
        {
            "pmid": "87654321",
            "title": "Clinical implications of TP53 status in NSCLC",
            "abstract": (
                "Non-small cell lung cancer patients with TP53 mutations "
                "show distinct clinical outcomes. We analyzed 500 cases "
                "to determine prognostic significance."
            ),
            "gene": "TP53",
            "disease": "Lung Cancer",
        },
    ]


@pytest.fixture
def plugin_config():
    """
    Provide a standard plugin configuration for testing.

    Returns:
        Configuration dictionary
    """
    return {
        "email": "test@example.com",
        "db_path": ":memory:",  # In-memory database for testing
        "max_results": 10,
    }


@pytest.fixture
def sample_hypothesis():
    """
    Provide a sample hypothesis dictionary.

    Returns:
        Hypothesis dictionary
    """
    return {
        "id": "H_Test_Hypothesis",
        "gene": "TP53",
        "disease": "Lung Cancer",
        "description": "Test hypothesis for TP53 and Lung Cancer association",
        "raw_node": {
            "id": "H_Test_Hypothesis",
            "if": [{"entity_is": {"gene": "TP53"}}, {"entity_is": {"disease": "Lung Cancer"}}],
            "then": [{"relationship_is": "association"}],
        },
    }


@pytest.fixture
def mock_evidence_high_confidence():
    """
    Provide mock evidence with high confidence (low semantic distance).

    Returns:
        List of evidence dictionaries
    """
    return [
        {
            "document": "TP53 mutations are strongly associated with lung cancer development.",
            "metadata": {
                "pmid": "12345678",
                "gene": "TP53",
                "disease": "Lung Cancer",
                "title": "TP53 in lung cancer",
            },
            "distance": 0.15,  # Low distance = high similarity
        },
        {
            "document": "Lung cancer patients frequently harbor TP53 genetic alterations.",
            "metadata": {
                "pmid": "87654321",
                "gene": "TP53",
                "disease": "Lung Cancer",
                "title": "Genetic alterations in lung cancer",
            },
            "distance": 0.18,
        },
    ]


@pytest.fixture
def mock_evidence_low_confidence():
    """
    Provide mock evidence with low confidence (high semantic distance).

    Returns:
        List of evidence dictionaries
    """
    return [
        {
            "document": "General overview of cell biology and DNA structure.",
            "metadata": {
                "pmid": "99999999",
                "gene": "Unknown",
                "disease": "General",
                "title": "Introduction to molecular biology",
            },
            "distance": 0.85,  # High distance = low similarity
        },
        {
            "document": "Unrelated topic about plant genetics and agriculture.",
            "metadata": {
                "pmid": "88888888",
                "gene": "Unknown",
                "disease": "N/A",
                "title": "Plant genetic engineering",
            },
            "distance": 0.92,
        },
    ]


@pytest.fixture
def expected_validation_report_structure():
    """
    Provide the expected structure of a validation report.

    Returns:
        Dictionary with expected report keys
    """
    return {
        "plugin": str,
        "version": str,
        "timestamp": str,
        "input_file": str,
        "hypotheses_total": int,
        "hypotheses_validated": int,
        "evidence_threshold": float,
        "results": list,
    }


@pytest.fixture
def expected_result_structure():
    """
    Provide the expected structure of a single validation result.

    Returns:
        Dictionary with expected result keys
    """
    return {
        "hypothesis_id": str,
        "gene": str,
        "disease": str,
        "description": str,
        "evidence_count": int,
        "top_evidence": list,
        "confidence": float,
        "validated_at": str,
    }
