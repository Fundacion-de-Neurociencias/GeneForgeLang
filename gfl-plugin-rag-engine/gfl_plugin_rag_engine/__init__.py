"""
GFL Plugin: Neuro-Symbolic RAG Engine
======================================

A GeneForgeLang plugin that validates biological hypotheses using a
Neuro-Symbolic Retrieval-Augmented Generation (RAG) engine.

This plugin bridges symbolic GFL hypotheses with unstructured scientific
literature from PubMed, providing evidence-based confidence scores.
"""

from .plugin import RAGEnginePlugin

__version__ = "1.0.0"
__all__ = ["RAGEnginePlugin"]
