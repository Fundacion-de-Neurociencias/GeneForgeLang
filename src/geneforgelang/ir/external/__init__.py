"""External knowledge connectors for GFL IR.

This module provides connectors to external knowledge sources:
- OpenMed: Biomedical embeddings, NER, and privacy filtering
- HuggingScience: Scientific reasoning models
"""

from geneforgelang.ir.external.openmed_connector import OpenMedConnector
from geneforgelang.ir.external.huggingscience_connector import HuggingScienceConnector
from geneforgelang.ir.external.retrieval_service import RetrievalService, RetrievedEvidence

__all__ = [
    "OpenMedConnector",
    "HuggingScienceConnector", 
    "RetrievalService",
    "RetrievedEvidence",
]
