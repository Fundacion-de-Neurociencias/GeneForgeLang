#!/usr/bin/env python3
"""
Neuro-Symbolic RAG Engine for GeneForge
========================================

This module implements a Retrieval-Augmented Generation (RAG) system that bridges
symbolic GFL hypotheses with unstructured scientific literature knowledge.

It uses the official GFL parser to extract structured hypotheses and queries
PubMed/biomedical literature to validate or enrich these hypotheses with
evidence from scientific publications.

Author: GeneForge Team
License: MIT
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# GFL official parser integration
try:
    from gfl.parser import parse as gfl_parse
except ImportError:
    print("ERROR: GFL library not found. Please install it with:")
    print("  pip install -e /path/to/GeneForgeLang")
    sys.exit(1)

# Vector database and embeddings
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ERROR: ChromaDB not found. Please install it with:")
    print("  pip install chromadb")
    sys.exit(1)

# PubMed integration
try:
    from Bio import Entrez
except ImportError:
    print("ERROR: Biopython not found. Please install it with:")
    print("  pip install biopython")
    sys.exit(1)


class NeuroSymbolicRAG:
    """
    A neuro-symbolic reasoning engine that combines:
    - Symbolic knowledge from GFL hypotheses
    - Neural embeddings for semantic search
    - Retrieval from scientific literature
    """

    def __init__(self, email: str = "geneforge@example.com", db_path: str = "./chroma_db"):
        """
        Initialize the RAG engine.

        Args:
            email: Email for PubMed API (required by NCBI)
            db_path: Path to store the ChromaDB vector database
        """
        self.email: str = email
        Entrez.email = email

        # Initialize vector database
        self.chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=db_path))

        # Create or get collection for scientific documents
        self.collection = self.chroma_client.get_or_create_collection(
            name="biomedical_literature", metadata={"description": "PubMed abstracts and scientific literature"}
        )

        print("✓ Neuro-Symbolic RAG Engine initialized")
        print(f"✓ Vector database: {db_path}")
        print(f"✓ Collection size: {self.collection.count()} documents")

    def parse_gfl_hypotheses(self, gfl_path: str) -> list[dict[str, Any]]:
        """
        Parse a GFL file using the official parser and extract hypothesis blocks.

        Args:
            gfl_path: Path to the .gfl file

        Returns:
            List of hypothesis dictionaries with extracted gene/disease pairs
        """
        print(f"\n📖 Parsing GFL file: {gfl_path}")

        with open(gfl_path, encoding="utf-8") as f:
            source = f.read()

        try:
            # Use official GFL parser
            ast = gfl_parse(source)
        except Exception as e:
            print(f"ERROR: Failed to parse GFL file: {e}")
            return []

        hypotheses = []

        # Extract hypothesis blocks from AST
        # The AST structure may contain hypothesis as a key or in a list
        hyp_nodes = ast.get("hypothesis", [])

        # Handle both single hypothesis and list of hypotheses
        if not isinstance(hyp_nodes, list):
            hyp_nodes = [hyp_nodes] if hyp_nodes else []

        for hyp_node in hyp_nodes:
            if not hyp_node:
                continue

            hypothesis_data = self._extract_hypothesis_data(hyp_node)
            if hypothesis_data:
                hypotheses.append(hypothesis_data)

        print(f"✓ Extracted {len(hypotheses)} hypotheses from GFL file")
        return hypotheses

    def _extract_hypothesis_data(self, hyp_node: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Extract gene, disease, and other relevant data from a hypothesis node.

        Args:
            hyp_node: A hypothesis node from the GFL AST

        Returns:
            Dictionary with extracted hypothesis data or None if invalid
        """
        gene = None
        disease = None
        hypothesis_id = hyp_node.get("id", "unknown")
        description = hyp_node.get("description", "")

        # Extract entities from 'if' conditions
        if_conditions = hyp_node.get("if", [])
        if not isinstance(if_conditions, list):
            if_conditions = [if_conditions] if if_conditions else []

        for condition in if_conditions:
            # Handle entity_is predicates
            if isinstance(condition, dict):
                if "entity_is" in condition:
                    entity = condition["entity_is"]
                    if isinstance(entity, dict):
                        if "gene" in entity:
                            gene = entity["gene"]
                        if "disease" in entity:
                            disease = entity["disease"]
                # Also handle direct gene/disease keys
                if "gene" in condition:
                    gene = condition.get("gene")
                if "disease" in condition:
                    disease = condition.get("disease")

        # Only return if we found at least a gene or disease
        if gene or disease:
            return {
                "id": hypothesis_id,
                "gene": gene,
                "disease": disease,
                "description": description,
                "raw_node": hyp_node,
            }

        return None

    def fetch_pubmed_abstracts(self, gene: str, disease: str, max_results: int = 10) -> list[dict[str, str]]:
        """
        Query PubMed for abstracts related to a gene-disease association.

        Args:
            gene: Gene symbol (e.g., "TP53")
            disease: Disease name (e.g., "Lung Cancer")
            max_results: Maximum number of abstracts to retrieve

        Returns:
            List of dictionaries containing PubMed abstracts
        """
        query = f"({gene}[Gene]) AND ({disease}[Disease/Title/Abstract])"
        print(f"🔍 Querying PubMed: {query}")

        try:
            # Search PubMed
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()

            id_list = record.get("IdList", [])

            if not id_list:
                print(f"  ⚠ No results found for {gene} + {disease}")
                return []

            print(f"  ✓ Found {len(id_list)} PubMed articles")

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
                            {"pmid": pmid, "title": title, "abstract": abstract, "gene": gene, "disease": disease}
                        )
                except Exception as e:
                    print(f"  ⚠ Error parsing article: {e}")
                    continue

            print(f"  ✓ Successfully retrieved {len(abstracts)} abstracts")
            return abstracts

        except Exception as e:
            print(f"  ✗ PubMed query failed: {e}")
            return []

    def index_documents(self, abstracts: list[dict[str, str]]):
        """
        Add abstracts to the vector database for semantic search.

        Args:
            abstracts: List of abstract dictionaries from PubMed
        """
        if not abstracts:
            return

        print(f"📚 Indexing {len(abstracts)} documents into vector database...")

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
            print(f"✓ Successfully indexed {len(documents)} documents")
        except Exception as e:
            print(f"⚠ Warning during indexing: {e}")

    def query_knowledge_base(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """
        Perform semantic search over the indexed literature.

        Args:
            query: Natural language query
            n_results: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        print(f"🔎 Semantic search: '{query}'")

        results = self.collection.query(query_texts=[query], n_results=min(n_results, self.collection.count()))

        retrieved_docs = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None

                retrieved_docs.append({"document": doc, "metadata": metadata, "distance": distance})

        print(f"✓ Retrieved {len(retrieved_docs)} relevant documents")
        return retrieved_docs

    def reason_about_hypothesis(self, hypothesis: dict[str, Any]) -> dict[str, Any]:
        """
        Perform neuro-symbolic reasoning on a hypothesis by combining
        symbolic constraints with neural retrieval.

        Args:
            hypothesis: Hypothesis data extracted from GFL

        Returns:
            Reasoning results with evidence and confidence
        """
        print(f"\n🧠 Reasoning about hypothesis: {hypothesis['id']}")
        print(f"   Gene: {hypothesis['gene']}")
        print(f"   Disease: {hypothesis['disease']}")
        print(f"   Description: {hypothesis['description']}")

        # Fetch literature evidence
        abstracts = self.fetch_pubmed_abstracts(hypothesis["gene"], hypothesis["disease"], max_results=10)

        # Index new evidence
        self.index_documents(abstracts)

        # Query for supporting evidence
        query = f"Association between {hypothesis['gene']} gene and {hypothesis['disease']}"
        evidence = self.query_knowledge_base(query, n_results=5)

        # Compute confidence based on evidence strength
        confidence = self._compute_confidence(evidence)

        result = {
            "hypothesis_id": hypothesis["id"],
            "gene": hypothesis["gene"],
            "disease": hypothesis["disease"],
            "evidence_count": len(abstracts),
            "top_evidence": evidence[:3],
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

        print(f"✓ Reasoning complete. Confidence: {confidence:.2%}")
        print(f"✓ Evidence: {len(abstracts)} PubMed articles found")

        return result

    def _compute_confidence(self, evidence: list[dict[str, Any]]) -> float:
        """
        Compute confidence score based on retrieved evidence quality.

        Args:
            evidence: List of retrieved documents

        Returns:
            Confidence score between 0 and 1
        """
        if not evidence:
            return 0.0

        # Simple heuristic: inverse of average distance
        distances = [doc["distance"] for doc in evidence if doc["distance"] is not None]

        if not distances:
            return 0.5

        avg_distance = sum(distances) / len(distances)
        # Convert distance to confidence (lower distance = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))

        return confidence

    def process_gfl_file(self, gfl_path: str, output_path: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Complete pipeline: parse GFL, reason about hypotheses, generate report.

        Args:
            gfl_path: Path to input GFL file
            output_path: Optional path to save JSON results

        Returns:
            List of reasoning results for each hypothesis
        """
        print("=" * 80)
        print("🧬 NEURO-SYMBOLIC RAG ENGINE FOR GENEFORGE")
        print("=" * 80)

        # Parse GFL hypotheses
        hypotheses = self.parse_gfl_hypotheses(gfl_path)

        if not hypotheses:
            print("⚠ No hypotheses found in GFL file")
            return []

        # Reason about each hypothesis
        results = []
        for hypothesis in hypotheses:
            result = self.reason_about_hypothesis(hypothesis)
            results.append(result)

        # Save results if output path provided
        if output_path:
            self._save_results(results, output_path)

        # Print summary
        self._print_summary(results)

        return results

    def _save_results(self, results: list[dict[str, Any]], output_path: str):
        """Save reasoning results to JSON file."""
        print(f"\n💾 Saving results to: {output_path}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("✓ Results saved successfully")

    def _print_summary(self, results: list[dict[str, Any]]):
        """Print a summary of reasoning results."""
        print("\n" + "=" * 80)
        print("📊 REASONING SUMMARY")
        print("=" * 80)

        for result in results:
            print(f"\nHypothesis: {result['hypothesis_id']}")
            print(f"  Gene-Disease: {result['gene']} ↔ {result['disease']}")
            print(f"  Evidence: {result['evidence_count']} articles")
            print(f"  Confidence: {result['confidence']:.2%}")

            if result["top_evidence"]:
                print("  Top Evidence:")
                for i, evidence in enumerate(result["top_evidence"][:2], 1):
                    pmid = evidence["metadata"].get("pmid", "N/A")
                    title = evidence["metadata"].get("title", "No title")[:60]
                    print(f"    {i}. PMID:{pmid} - {title}...")

        print("\n" + "=" * 80)


def main():
    """Main entry point for the RAG engine."""
    if len(sys.argv) < 2:
        print("Usage: python neuro_symbolic_rag.py <gfl_file> [output_json]")
        sys.exit(1)

    gfl_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rag_results.json"

    # Initialize RAG engine
    rag = NeuroSymbolicRAG(email="geneforge@research.org", db_path="./chroma_db")

    # Process GFL file
    rag.process_gfl_file(gfl_file, output_file)


if __name__ == "__main__":
    main()
