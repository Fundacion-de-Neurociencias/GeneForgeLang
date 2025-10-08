# GFL Plugin: Neuro-Symbolic RAG Engine

[![CI](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions/workflows/ci.yml/badge.svg)](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Fundacion-de-Neurociencias/GeneForgeLang/branch/main/graph/badge.svg)](https://codecov.io/gh/Fundacion-de-Neurociencias/GeneForgeLang)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

## 🎯 Overview

The **Neuro-Symbolic RAG Engine** is a first-class GeneForge Language (GFL) plugin that validates biological hypotheses by combining:

- **Symbolic Reasoning**: Formal hypothesis extraction from GFL AST
- **Neural Retrieval**: Semantic search using vector embeddings
- **Literature Evidence**: Real-time validation against PubMed scientific publications

This plugin transforms GFL from a static specification language into a **dynamic reasoning platform** capable of evidence-based hypothesis validation.

## 🚀 Installation

### From Source

```bash
# Clone the repository
cd GeneForgeLang/gfl-plugin-rag-engine

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Via pip (when published)

```bash
pip install gfl-plugin-rag-engine
```

## 📋 Dependencies

- **geneforgelang**: Official GFL parser and runtime
- **chromadb**: Vector database for semantic search
- **biopython**: PubMed/NCBI Entrez access
- **pyyaml**: Configuration file support

## 🔧 Usage

### As a Python Plugin

```python
from gfl_plugin_rag_engine import RAGEnginePlugin

# Initialize plugin
rag = RAGEnginePlugin(config={
    'email': 'your.email@research.org',
    'db_path': './chroma_db',
    'max_results': 10
})

# Run validation
result = rag.run(
    input_gfl='hypotheses.gfl',
    output_report='validation_report.json',
    params={
        'top_k_docs': 5,
        'evidence_threshold': 0.65
    }
)

print(result['status'])  # 'success'
print(result['hypotheses_validated'])  # Number of validated hypotheses
```

### In GFL Workflows

```yaml
# example_workflow.gfl
# Validate hypotheses using the RAG engine

analyze:
  tool: "rag-engine"
  input: "my_hypotheses.gfl"
  output: "evidence_report.json"
  params:
    top_k_docs: 10
    evidence_threshold: 0.70
```

### GFL Hypothesis Format

```yaml
# my_hypotheses.gfl

hypothesis:
  id: "H_TP53_Cancer"
  description: "Test association between TP53 mutations and cancer susceptibility"
  if:
    - entity_is:
        gene: "TP53"
    - entity_is:
        disease: "Lung Cancer"
  then:
    - relationship_is: "association"

hypothesis:
  id: "H_BRCA1_Breast"
  description: "Investigate BRCA1 as risk factor for breast cancer"
  if:
    - entity_is:
        gene: "BRCA1"
    - entity_is:
        disease: "Breast Cancer"
  then:
    - relationship_is: "causal"
```

## 📊 Output Format

The plugin generates a JSON report with validation results:

```json
{
  "plugin": "gfl-plugin-rag-engine",
  "version": "1.0.0",
  "timestamp": "2025-10-08T10:30:00",
  "hypotheses_total": 4,
  "hypotheses_validated": 3,
  "evidence_threshold": 0.65,
  "results": [
    {
      "hypothesis_id": "H_TP53_Cancer",
      "gene": "TP53",
      "disease": "Lung Cancer",
      "description": "Test association...",
      "evidence_count": 10,
      "confidence": 0.87,
      "top_evidence": [
        {
          "document": "Abstract text...",
          "metadata": {
            "pmid": "12345678",
            "title": "TP53 mutations in lung cancer...",
            "gene": "TP53",
            "disease": "Lung Cancer"
          },
          "distance": 0.23
        }
      ],
      "validated_at": "2025-10-08T10:30:15"
    }
  ]
}
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    GFL Hypothesis File                        │
│              (Parsed by official GFL parser)                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  RAGEnginePlugin.run()                        │
│         • Parse hypotheses from GFL AST                       │
│         • Extract gene-disease pairs                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              PubMed Literature Retrieval                      │
│      Query: "gene[Gene] AND disease[Title/Abstract]"          │
│            Fetch: Up to N abstracts via NCBI                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│          ChromaDB Vector Database Indexing                    │
│      • Embed abstracts using sentence transformers            │
│      • Store in persistent vector database                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              Semantic Search & Evidence Ranking               │
│      • Query: "Association between gene and disease"          │
│      • Rank: By embedding similarity                          │
│      • Return: Top-k most relevant documents                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              Confidence Score Computation                     │
│      confidence = f(evidence_count, semantic_distance)        │
│      Output: Score ∈ [0, 1] for each hypothesis              │
└──────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### 1. **Official GFL Parser Integration**
- Uses `gfl.parser.parse()` for robust hypothesis extraction
- Supports full GFL syntax and complex hypothesis structures
- Handles multiple hypotheses in a single file

### 2. **Intelligent Literature Retrieval**
- Real-time PubMed queries via NCBI Entrez API
- Gene-specific and disease-specific search strategies
- Configurable result limits and filtering

### 3. **Semantic Vector Search**
- ChromaDB for efficient similarity search
- Persistent storage across multiple runs
- Incremental indexing of new literature

### 4. **Evidence-Based Confidence Scoring**
- Combines evidence count with semantic relevance
- Configurable confidence thresholds
- Transparent scoring methodology

### 5. **Plugin Ecosystem Integration**
- Compatible with GeneForge plugin discovery system
- Standard plugin interface (`run()` method)
- Composable with other GFL tools

## ⚙️ Configuration

### Plugin Initialization

```python
config = {
    # Required: Email for PubMed API (NCBI requirement)
    'email': 'your.email@institution.org',

    # Optional: Vector database path (default: './chroma_db')
    'db_path': '/path/to/vector/database',

    # Optional: Max PubMed results per query (default: 10)
    'max_results': 20
}

plugin = RAGEnginePlugin(config=config)
```

### Runtime Parameters

```python
params = {
    # Number of evidence documents to retrieve (default: 5)
    'top_k_docs': 10,

    # Minimum confidence threshold to include in report (default: 0.0)
    'evidence_threshold': 0.70
}

result = plugin.run(input_gfl, output_report, params)
```

## 📚 API Reference

### `RAGEnginePlugin`

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`
Initialize the plugin with configuration options.

##### `run(input_gfl: str, output_report: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute hypothesis validation pipeline.

**Parameters:**
- `input_gfl`: Path to GFL file with hypothesis blocks
- `output_report`: Path for output JSON report
- `params`: Optional execution parameters

**Returns:**
- Dictionary with execution status and metadata

##### `get_metadata() -> Dict[str, Any]`
Get plugin metadata and capabilities.

## 🧪 Testing

The plugin includes a comprehensive test suite with 42 tests covering all functionality.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=gfl_plugin_rag_engine --cov-report=html

# Run specific test file
pytest tests/test_plugin_interface.py

# Use the convenient test runner script
bash run_tests.sh --verbose --coverage
```

### Test Coverage

- **Plugin Interface**: 12 tests (100% coverage)
- **GFL Parser Integration**: 10 tests (100% coverage)
- **PubMed Retrieval**: 11 tests (95% coverage)
- **Reasoning & Scoring**: 9 tests (100% coverage)
- **Total**: 42 tests (~98% coverage)

All tests use mocking to avoid external dependencies, ensuring fast and reliable execution (~2 seconds for full suite).

## 🔮 Future Enhancements

- **LLM Integration**: Natural language evidence summaries
- **Multi-Source Retrieval**: ClinVar, GeneCards, DrugBank
- **Advanced Reasoning**: Multi-hop inference across gene networks
- **Interactive UI**: Web interface for hypothesis exploration
- **Caching**: Intelligent caching of PubMed queries

## 📖 Examples

See the `examples/` directory for complete workflows:

- `example_workflow.gfl`: Basic validation workflow
- `guided_discovery_with_rag.gfl`: Integration with guided discovery
- `batch_validation.gfl`: Batch processing of multiple hypothesis files

## 🤝 Integration with GeneForge

This plugin integrates seamlessly with:

- **GFL Parser**: Uses official parser for hypothesis extraction
- **GeneForge WebApp**: Can be invoked from web workflows
- **Multi-Omic Platform**: Enriches genomic data with literature context
- **Guided Discovery**: Validates hypotheses before wet-lab experiments

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Authors

**GeneForge Development Team**
- Email: geneforge@research.org
- GitHub: [Fundacion-de-Neurociencias/GeneForgeLang](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)

## 🙏 Acknowledgments

- NCBI for PubMed/Entrez API access
- ChromaDB team for vector database infrastructure
- GeneForge community for feedback and contributions

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: October 2025
