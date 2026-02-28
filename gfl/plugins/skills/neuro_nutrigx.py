"""
GeneForge Neuro-NutriGx Skill
=============================
Nutrigenómica local orientada a la salud cerebral y neuroprotección.
Analiza la relación entre variantes genéticas y requerimientos nutricionales.

Autor: GeneForge / Fundación de Neurociencias — EBRAINS Lab
Versión: 0.1.0
"""

from __future__ import annotations
from typing import Any, Dict, List
from gfl.plugins.plugin_registry import GeneForgeSkill

class NeuroNutriGxSkill(GeneForgeSkill):
    """
    Bio-Skill: Neuro-NutriGx

    Evalúa la predisposición genética a deficiencias o necesidades 
    específicas de nutrientes críticos para el cerebro (Folatros, B12, Omegas).
    """

    @property
    def name(self) -> str:
        return "neuro_nutrigx"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def author(self) -> str:
        return "Fundación de Neurociencias — EBRAINS Lab"

    @property
    def description(self) -> str:
        return "Nutrigenómica para neuroprotección: Metilación (B12/Folatols) e inflamación."

    @property
    def skill_type(self) -> str:
        return "Neuro-Nutrition"

    def _analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        patient_id = inputs.get("patient_id", "ANON-NUT-001")
        genotypes = inputs.get("genotypes", {})
        
        results = {}
        recommendations = []

        # 1. Análisis MTHFR (Metilación / Folatos)
        mthfr = genotypes.get("MTHFR")
        if mthfr:
            res = self._analyze_mthfr(mthfr)
            results["methylation_status"] = res
            if res["priority"] == "ALTA":
                recommendations.append(res["advice"])

        # 2. Análisis FADS1 (Omega-3 metabolism)
        fads1 = genotypes.get("FADS1")
        if fads1:
            res = self._analyze_fads1(fads1)
            results["omega3_metabolism"] = res
            recommendations.append(res["advice"])

        return {
            "patient_id": patient_id,
            "nutritional_profile": results,
            "core_recommendations": recommendations,
            "summary": f"Análisis nutrigenómico completado para {len(results)} ejes metabólicos."
        }

    def _analyze_mthfr(self, genotype: str) -> Dict[str, Any]:
        # MTHFR C677T levels
        responses = {
            "CC": {"priority": "BAJA", "status": "Normal", "advice": "Metabolismo de folatos estándar."},
            "CT": {"priority": "MEDIA", "status": "Reducido", "advice": "Monitorizar niveles de homocisteína y asegurar ingesta de folatos."},
            "TT": {"priority": "ALTA", "status": "Significativamente Reducido", "advice": "⚠️ Requiere suplementación con Metilfolato (no ácido fólico sintético) para neuroprotección."},
        }
        return responses.get(genotype, {"priority": "DESCONOCIDA", "status": "N/A", "advice": "Variante no reconocida."})

    def _analyze_fads1(self, genotype: str) -> Dict[str, Any]:
        # FADS1 influences conversion of ALA to EPA/DHA
        responses = {
            "GG": {"status": "Eficiente", "advice": "Conversión óptima de precursores vegetales a EPA/DHA."},
            "GT": {"status": "Reducido", "advice": "Considerar aporte directo de EPA/DHA marino."},
            "TT": {"status": "Muy bajo", "advice": "⚠️ Alta dependencia de fuentes directas de DHA (Algas/Pescado) para salud cognitiva."},
        }
        res = responses.get(genotype, {"status": "N/A", "advice": "Variante FADS1 no reconocida."})
        res["priority"] = "MEDIA" # Simplificado
        return res
