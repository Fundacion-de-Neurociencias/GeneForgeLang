"""
gfl_plugin_causal_evidence — GFL Causal Evidence & Equity Plugin
===================================================================
ADR-0003 compliant GFL GeneratorPlugin providing:
  - Causal Instrument Verification (F >= 10)
  - Horizontal Pleiotropy Invalidation (Egger intercept test)
  - Equity-Aware Population Matching
"""

from .causal_triangulation import CausalEvidencePlugin, CausalTriangulationResult

__all__ = ["CausalEvidencePlugin", "CausalTriangulationResult"]
