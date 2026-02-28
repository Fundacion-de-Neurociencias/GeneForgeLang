"""
GeneForge Neuro-PharmGx Skill
==============================
Farmacogenómica Neurológica — Análisis local de respuesta a fármacos
neuropsiquiátricos basado en polimorfismos CYP450.

Sin nubes. Sin alucinaciones. Sin datos que abandonen el hospital.

Autor: GeneForge / Fundación de Neurociencias — EBRAINS Lab
Versión: 0.1.0

Referencia clínica:
  - CPIC Guidelines: https://cpicpgx.org/guidelines/
  - PharmGKB: https://www.pharmgkb.org/
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from gfl.plugins.plugin_registry import GeneForgeSkill


# ---------------------------------------------------------------------------
# Knowledge Base local (simulada — en producción, se cargaría de un archivo
# CPIC actualizado o base de datos SQLite local)
# ---------------------------------------------------------------------------

# Tabla de fenotipos CYP2D6 según diplotipos (simplificada)
CYP2D6_PHENOTYPE_MAP: Dict[str, str] = {
    "*1/*1":  "Metabolizador Extenso (Normal)",
    "*1/*2":  "Metabolizador Extenso (Normal)",
    "*1/*3":  "Metabolizador Intermedio",
    "*1/*4":  "Metabolizador Intermedio",
    "*1/*5":  "Metabolizador Intermedio",
    "*3/*4":  "Metabolizador Pobre",
    "*4/*4":  "Metabolizador Pobre",
    "*1/*1xN": "Metabolizador Ultra-Rápido (riesgo de toxicidad reducida / ineficacia)",
    "*1/*2xN": "Metabolizador Ultra-Rápido (riesgo de toxicidad reducida / ineficacia)",
}

CYP2C19_PHENOTYPE_MAP: Dict[str, str] = {
    "*1/*1": "Metabolizador Extenso (Normal)",
    "*1/*2": "Metabolizador Intermedio",
    "*2/*2": "Metabolizador Pobre",
    "*17/*1": "Metabolizador Ultra-Rápido",
    "*17/*17": "Metabolizador Ultra-Rápido",
}

# Recomendaciones clínicas CPIC simplificadas por fármaco y fenotipo
CPIC_RECOMMENDATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "fluoxetina": {
        "enzyme": "CYP2D6",
        "phenotypes": {
            "Metabolizador Pobre": {
                "recommendation": "⚠️  REDUCIR DOSIS. Riesgo de acumulación plasmática y toxicidad serotoninérgica.",
                "cpic_level": "A",
                "alternative": "Considerar escitalopram (metabolismo CYP2C19, no CYP2D6).",
            },
            "Metabolizador Ultra-Rápido (riesgo de toxicidad reducida / ineficacia)": {
                "recommendation": "⚠️  POSIBLE INEFICACIA. Metabolismo acelerado puede reducir niveles plasmáticos.",
                "cpic_level": "A",
                "alternative": "Considerar citalopram o escitalopram.",
            },
            "default": {
                "recommendation": "✅ Dosis estándar. No se requiere ajuste farmacogenético.",
                "cpic_level": "A",
                "alternative": None,
            },
        },
    },
    "amitriptilina": {
        "enzyme": "CYP2D6",
        "phenotypes": {
            "Metabolizador Pobre": {
                "recommendation": "⚠️  CONTRAINDICADA o dosis muy reducida. Alto riesgo de efectos adversos cardíacos.",
                "cpic_level": "A",
                "alternative": "Considerar antidepresivos SSRI con perfil CYP más favorable.",
            },
            "default": {
                "recommendation": "✅ Dosis estándar con monitorización de niveles plasmáticos.",
                "cpic_level": "B",
                "alternative": None,
            },
        },
    },
    "clopidogrel": {
        "enzyme": "CYP2C19",
        "phenotypes": {
            "Metabolizador Pobre": {
                "recommendation": "⚠️  ALTA RESISTENCIA. El fármaco no se activa correctamente. Riesgo de eventos cardiovasculares.",
                "cpic_level": "A",
                "alternative": "Prasugrel o ticagrelor (no dependientes de CYP2C19).",
            },
            "Metabolizador Intermedio": {
                "recommendation": "⚠️  RESISTENCIA PARCIAL. Considerar dosis alternativa o monitorizar.",
                "cpic_level": "A",
                "alternative": "Evaluar prasugrel individualizado.",
            },
            "default": {
                "recommendation": "✅ Dosis estándar. No se requiere ajuste.",
                "cpic_level": "A",
                "alternative": None,
            },
        },
    },
    "risperidona": {
        "enzyme": "CYP2D6",
        "phenotypes": {
            "Metabolizador Pobre": {
                "recommendation": "⚠️  REDUCIR DOSIS 50%. Riesgo elevado de efectos extrapiramidales.",
                "cpic_level": "B",
                "alternative": "Quetiapina (metabolismo CYP3A4, más independiente).",
            },
            "default": {
                "recommendation": "✅ Dosis estándar. Monitorizar efectos secundarios.",
                "cpic_level": "B",
                "alternative": None,
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Clase principal de la Skill
# ---------------------------------------------------------------------------

class NeuroPharmGxSkill(GeneForgeSkill):
    """
    Bio-Skill: Neuro-PharmGx

    Analiza el perfil farmacogenómico de un paciente para fármacos
    neurológicos y psiquiátricos. Cruza polimorfismos CYP450 con las
    guías CPIC y genera recomendaciones clínicas estructuradas.

    Entradas esperadas (dict):
        patient_id    : Identificador anonimizado del paciente (str)
        diplotypes    : Dict con enzimas y sus diplotipos. Ej:
                        {"CYP2D6": "*1/*4", "CYP2C19": "*1/*1"}
        drugs         : Lista de fármacos a analizar. Ej:
                        ["fluoxetina", "risperidona"]

    Salida (data dict):
        patient_id    : str
        analyses      : Lista de análisis por fármaco con fenotipo y recomendación
        summary       : Resumen textual de alto nivel
    """

    @property
    def name(self) -> str:
        return "neuro_pharmgx"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def author(self) -> str:
        return "GeneForge / Fundación de Neurociencias — EBRAINS Lab"

    @property
    def description(self) -> str:
        return (
            "Farmacogenómica Neurológica local: analiza polimorfismos CYP450 "
            "y genera recomendaciones CPIC para fármacos neuropsiquiátricos."
        )

    @property
    def skill_type(self) -> str:
        return "Neuro-PharmGx"

    # ------------------------------------------------------------------
    # Implementación del análisis
    # ------------------------------------------------------------------

    def _analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis farmacogenómico neurológico basado en CPIC.
        Todo se ejecuta localmente — los datos nunca abandonan el entorno.
        """
        patient_id: str = inputs.get("patient_id", "ANON-001")
        diplotypes: Dict[str, str] = inputs.get("diplotypes", {})
        drugs: List[str] = inputs.get("drugs", [])

        if not diplotypes:
            raise ValueError("Se requiere al menos un diplotipo de enzima CYP450.")
        if not drugs:
            raise ValueError("Se requiere al menos un fármaco a analizar.")

        # Calcular fenotipos a partir de los diplotipos
        phenotype_profile = self._calculate_phenotypes(diplotypes)

        # Generar análisis por fármaco
        analyses = []
        alerts: List[str] = []

        for drug in drugs:
            drug_lower = drug.lower()
            analysis = self._analyze_drug(drug_lower, phenotype_profile)
            analyses.append(analysis)
            if analysis.get("alert"):
                alerts.append(f"{drug}: {analysis['alert']}")

        summary = self._generate_summary(patient_id, phenotype_profile, alerts)

        return {
            "patient_id": patient_id,
            "phenotype_profile": phenotype_profile,
            "analyses": analyses,
            "total_alerts": len(alerts),
            "summary": summary,
        }

    def _calculate_phenotypes(self, diplotypes: Dict[str, str]) -> Dict[str, str]:
        """Traduce diplotipos a fenotipos clínicos."""
        phenotypes: Dict[str, str] = {}
        enzyme_maps = {
            "CYP2D6": CYP2D6_PHENOTYPE_MAP,
            "CYP2C19": CYP2C19_PHENOTYPE_MAP,
        }
        for enzyme, diplotype in diplotypes.items():
            enzyme_map = enzyme_maps.get(enzyme.upper())
            if enzyme_map:
                phenotypes[enzyme.upper()] = enzyme_map.get(
                    diplotype, f"Fenotipo desconocido para {diplotype}"
                )
            else:
                phenotypes[enzyme.upper()] = f"Enzima {enzyme} no incluida en la base CPIC local."
        return phenotypes

    def _analyze_drug(self, drug: str, phenotype_profile: Dict[str, str]) -> Dict[str, Any]:
        """Genera la recomendación clínica para un fármaco dado el perfil enzimático."""
        if drug not in CPIC_RECOMMENDATIONS:
            return {
                "drug": drug,
                "status": "SIN_DATOS",
                "recommendation": "Fármaco no incluido en la base local CPIC. Consultar PharmGKB.",
                "cpic_level": "N/A",
                "alternative": None,
                "alert": None,
            }

        drug_data = CPIC_RECOMMENDATIONS[drug]
        enzyme = drug_data["enzyme"]
        patient_phenotype = phenotype_profile.get(enzyme, "")

        # Buscar la recomendación específica o usar el default
        phenotype_recs = drug_data["phenotypes"]
        rec = phenotype_recs.get(patient_phenotype) or phenotype_recs.get("default", {})

        is_alert = "⚠️" in rec.get("recommendation", "")

        return {
            "drug": drug,
            "enzyme_evaluated": enzyme,
            "patient_phenotype": patient_phenotype,
            "status": "ALERTA" if is_alert else "OK",
            "recommendation": rec.get("recommendation", "Sin recomendación disponible."),
            "cpic_level": rec.get("cpic_level", "N/A"),
            "alternative": rec.get("alternative"),
            "alert": rec.get("recommendation") if is_alert else None,
        }

    def _generate_summary(
        self,
        patient_id: str,
        phenotype_profile: Dict[str, str],
        alerts: List[str],
    ) -> str:
        """Genera resumen clínico de alto nivel."""
        phenotype_str = "; ".join(
            f"{enz}: {pheno}" for enz, pheno in phenotype_profile.items()
        )
        if not alerts:
            return (
                f"Paciente {patient_id} — Perfil: {phenotype_str}. "
                "✅ No se detectaron interacciones farmacogenéticas de alto riesgo."
            )
        alert_str = " | ".join(alerts)
        return (
            f"Paciente {patient_id} — Perfil: {phenotype_str}. "
            f"⚠️  {len(alerts)} ALERTA(S) DETECTADA(S): {alert_str}"
        )
