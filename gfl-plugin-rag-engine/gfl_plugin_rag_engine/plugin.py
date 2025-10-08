"""
Neuro-Symbolic RAG Engine Plugin for GeneForge
===============================================

This plugin provides hypothesis validation capabilities by combining:
- Symbolic reasoning from GFL AST
- Neural embeddings for semantic search
- Retrieval from PubMed scientific literature
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# GFL parser integration
try:
    from gfl.parser import parse as gfl_parse
except ImportError:
    gfl_parse = None
    logging.warning("GFL parser not available. Install with: pip install -e /path/to/GeneForgeLang")

# Vector database
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

# PubMed integration
try:
    from Bio import Entrez
except ImportError:
    Entrez = None
    logging.warning("Biopython not available. Install with: pip install biopython")

logger = logging.getLogger(__name__)


class RAGEnginePlugin:
    """
    Neuro-Symbolic RAG Engine Plugin for hypothesis validation.

    This plugin validates GFL hypotheses against scientific literature,
    combining symbolic constraints with neural retrieval to provide
    evidence-based confidence scores.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the RAG Engine plugin.

        Args:
            config: Optional configuration dictionary with keys:
                - email: Email for PubMed API (required by NCBI)
                - db_path: Path for ChromaDB vector database
                - max_results: Maximum PubMed results per query
        """
        self.config = config or {}
        self.name = "gfl-plugin-rag-engine"
        self.version = "1.0.0"

        # Configuration
        self.email = self.config.get("email", "geneforge@research.org")
        self.db_path = self.config.get("db_path", "./chroma_db")
        self.max_results = self.config.get("max_results", 10)

        # Verify dependencies
        if not all([gfl_parse, chromadb, Entrez]):
            raise RuntimeError(
                "Missing required dependencies. Please install: " "gfl, chromadb, biopython"
            )

        # Initialize Entrez
        Entrez.email = self.email

        # Initialize vector database
        self.chroma_client = chromadb.Client(
            Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.db_path)
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="biomedical_literature",
            metadata={"description": "PubMed abstracts for hypothesis validation"},
        )

        logger.info(f"Plugin '{self.name}' v{self.version} initialized")
        logger.info(f"Vector DB: {self.db_path} ({self.collection.count()} documents)")

    def validate_input(self, input_gfl: str) -> bool:
        """
        Validate that the input GFL file exists and is readable.

        Args:
            input_gfl: Path to GFL file

        Returns:
            True if valid, False otherwise
        """
        if not input_gfl:
            logger.error("Input GFL path is empty")
            return False

        gfl_path = Path(input_gfl)
        if not gfl_path.exists():
            logger.error(f"GFL file not found: {input_gfl}")
            return False

        if not gfl_path.is_file():
            logger.error(f"Path is not a file: {input_gfl}")
            return False

        return True

    def run(
        self, input_gfl: str, output_report: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the RAG engine on a GFL file with hypotheses.

        Args:
            input_gfl: Path to input GFL file containing hypothesis blocks
            output_report: Path where the JSON report will be saved
            params: Optional parameters:
                - top_k_docs: Number of evidence documents to retrieve (default: 5)
                - evidence_threshold: Minimum confidence threshold (default: 0.0)

        Returns:
            Dictionary with execution results and metadata
        """
        logger.info(f"Running RAG Engine plugin on: {input_gfl}")

        # Validate input
        if not self.validate_input(input_gfl):
            return {"status": "error", "message": "Invalid input file", "plugin": self.name}

        # Extract parameters
        params = params or {}
        top_k = params.get("top_k_docs", 5)
        threshold = params.get("evidence_threshold", 0.0)

        try:
            # Parse GFL hypotheses
            hypotheses = self._parse_gfl_hypotheses(input_gfl)

            if not hypotheses:
                return {
                    "status": "warning",
                    "message": "No hypotheses found in GFL file",
                    "hypotheses_validated": 0,
                    "plugin": self.name,
                }

            # Validate each hypothesis
            results = []
            for hypothesis in hypotheses:
                result = self._validate_hypothesis(hypothesis, top_k)

                # Apply threshold filter
                if result["confidence"] >= threshold:
                    results.append(result)
                else:
                    logger.info(
                        f"Hypothesis {hypothesis['id']} below threshold: "
                        f"{result['confidence']:.2%} < {threshold:.2%}"
                    )

            # Prepare report
            report = {
                "plugin": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "input_file": str(input_gfl),
                "hypotheses_total": len(hypotheses),
                "hypotheses_validated": len(results),
                "evidence_threshold": threshold,
                "results": results,
            }

            # Save report
            self._save_report(report, output_report)

            logger.info(
                f"RAG Engine completed: {len(results)}/{len(hypotheses)} " f"hypotheses validated"
            )

            return {
                "status": "success",
                "hypotheses_total": len(hypotheses),
                "hypotheses_validated": len(results),
                "output_report": str(output_report),
                "plugin": self.name,
                "version": self.version,
            }

        except Exception as e:
            logger.error(f"RAG Engine failed: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e), "plugin": self.name}

    def _parse_gfl_hypotheses(self, gfl_path: str) -> List[Dict[str, Any]]:
        """
        Parse GFL file and extract hypothesis blocks.

        Args:
            gfl_path: Path to GFL file

        Returns:
            List of hypothesis dictionaries
        """
        logger.info(f"Parsing GFL file: {gfl_path}")

        with open(gfl_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Parse with official GFL parser
        ast = gfl_parse(source)

        # Extract hypotheses
        hyp_nodes = ast.get("hypothesis", [])
        if not isinstance(hyp_nodes, list):
            hyp_nodes = [hyp_nodes] if hyp_nodes else []

        hypotheses = []
        for hyp_node in hyp_nodes:
            if not hyp_node:
                continue

            hypothesis_data = self._extract_hypothesis_data(hyp_node)
            if hypothesis_data:
                hypotheses.append(hypothesis_data)

        logger.info(f"Extracted {len(hypotheses)} hypotheses")
        return hypotheses

    def _extract_hypothesis_data(self, hyp_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract gene/disease data from hypothesis node."""
        gene = None
        disease = None
        hypothesis_id = hyp_node.get("id", "unknown")
        description = hyp_node.get("description", "")

        # Extract from 'if' conditions
        if_conditions = hyp_node.get("if", [])
        if not isinstance(if_conditions, list):
            if_conditions = [if_conditions] if if_conditions else []

        for condition in if_conditions:
            if isinstance(condition, dict):
                # Handle entity_is predicates
                if "entity_is" in condition:
                    entity = condition["entity_is"]
                    if isinstance(entity, dict):
                        if "gene" in entity:
                            gene = entity["gene"]
                        if "disease" in entity:
                            disease = entity["disease"]
                # Handle direct keys
                if "gene" in condition:
                    gene = condition.get("gene")
                if "disease" in condition:
                    disease = condition.get("disease")

        if gene or disease:
            return {
                "id": hypothesis_id,
                "gene": gene,
                "disease": disease,
                "description": description,
                "raw_node": hyp_node,
            }

        return None

    def _validate_hypothesis(self, hypothesis: Dict[str, Any], top_k: int) -> Dict[str, Any]:
        """
        Validate a single hypothesis against literature.

        Args:
            hypothesis: Hypothesis data
            top_k: Number of evidence documents to retrieve

        Returns:
            Validation result with evidence and confidence
        """
        logger.info(f"Validating hypothesis: {hypothesis['id']}")

        # Fetch PubMed literature
        abstracts = self._fetch_pubmed_abstracts(hypothesis["gene"], hypothesis["disease"])

        # Index documents
        if abstracts:
            self._index_documents(abstracts)

        # Query for evidence
        query = f"Association between {hypothesis['gene']} gene and " f"{hypothesis['disease']}"
        evidence = self._query_knowledge_base(query, top_k)

        # Compute confidence
        confidence = self._compute_confidence(evidence)

        return {
            "hypothesis_id": hypothesis["id"],
            "gene": hypothesis["gene"],
            "disease": hypothesis["disease"],
            "description": hypothesis["description"],
            "evidence_count": len(abstracts),
            "top_evidence": evidence[:3],
            "confidence": confidence,
            "validated_at": datetime.now().isoformat(),
        }

    def _fetch_pubmed_abstracts(self, gene: str, disease: str) -> List[Dict[str, str]]:
        """Fetch PubMed abstracts for gene-disease pair."""
        query = f"({gene}[Gene]) AND ({disease}[Disease/Title/Abstract])"
        logger.debug(f"PubMed query: {query}")

        try:
            # Search
            handle = Entrez.esearch(db="pubmed", term=query, retmax=self.max_results)
            record = Entrez.read(handle)
            handle.close()

            id_list = record.get("IdList", [])
            if not id_list:
                logger.warning(f"No PubMed results for {gene} + {disease}")
                return []

            # Fetch abstracts
            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="xml")
            records = Entrez.read(handle)
            handle.close()

            abstracts = []
            for article in records.get("PubmedArticle", []):
                try:
                    medline = article["MedlineCitation"]
                    pmid = str(medline["PMID"])
                    article_data = medline["Article"]

                    title = article_data.get("ArticleTitle", "")
                    abstract_parts = article_data.get("Abstract", {}).get("AbstractText", [])
                    abstract = " ".join([str(part) for part in abstract_parts])

                    if abstract:
                        abstracts.append(
                            {
                                "pmid": pmid,
                                "title": title,
                                "abstract": abstract,
                                "gene": gene,
                                "disease": disease,
                            }
                        )
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue

            logger.debug(f"Retrieved {len(abstracts)} abstracts")
            return abstracts

        except Exception as e:
            logger.error(f"PubMed query failed: {e}")
            return []

    def _index_documents(self, abstracts: List[Dict[str, str]]):
        """Index abstracts into vector database."""
        if not abstracts:
            return

        documents = []
        metadatas = []
        ids = []

        for abstract in abstracts:
            doc_text = f"{abstract['title']} {abstract['abstract']}"
            documents.append(doc_text)
            metadatas.append(
                {
                    "pmid": abstract["pmid"],
                    "gene": abstract["gene"],
                    "disease": abstract["disease"],
                    "title": abstract["title"],
                }
            )
            ids.append(f"pmid_{abstract['pmid']}")

        try:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logger.debug(f"Indexed {len(documents)} documents")
        except Exception as e:
            logger.warning(f"Indexing warning: {e}")

    def _query_knowledge_base(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Query vector database for relevant evidence."""
        results = self.collection.query(
            query_texts=[query], n_results=min(n_results, max(1, self.collection.count()))
        )

        retrieved_docs = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None

                retrieved_docs.append({"document": doc, "metadata": metadata, "distance": distance})

        return retrieved_docs

    def _compute_confidence(self, evidence: List[Dict[str, Any]]) -> float:
        """Compute confidence score from evidence quality."""
        if not evidence:
            return 0.0

        distances = [doc["distance"] for doc in evidence if doc["distance"] is not None]

        if not distances:
            return 0.5

        avg_distance = sum(distances) / len(distances)
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))

        return confidence

    def _save_report(self, report: Dict[str, Any], output_path: str):
        """Save validation report to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {output_path}")

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Neuro-Symbolic RAG Engine for hypothesis validation",
            "author": "GeneForge Team",
            "capabilities": [
                "hypothesis_validation",
                "literature_retrieval",
                "semantic_search",
                "evidence_ranking",
            ],
            "input_format": "GFL file with hypothesis blocks",
            "output_format": "JSON report with validation results",
        }
