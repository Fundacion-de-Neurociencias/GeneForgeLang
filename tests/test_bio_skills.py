"""
Tests for GeneForge Bio-Skills Ecosystem
========================================
Verification of the base contract (reproducibility) and clinical logic 
for the neuro-diagnostic skill library.
"""

import pytest
import time
from gfl.plugins.skills.neuro_pharmgx import NeuroPharmGxSkill
from gfl.plugins.skills.neuro_geriatric_risk import NeuroGeriatricRiskSkill
from gfl.plugins.skills.neuro_nutrigx import NeuroNutriGxSkill
from gfl.plugins.plugin_registry import GeneForgeSkill

class TestBioSkillsCore:
    """Tests for the base GeneForgeSkill functionality."""
    
    def test_reproducibility_package_format(self):
        """Verify the reproducibility package contains all required scientific fields."""
        skill = NeuroPharmGxSkill()
        payload = {
            "patient_id": "TEST-001",
            "diplotypes": {"CYP2D6": "*1/*1"},
            "drugs": ["fluoxetina"]
        }
        result = skill.execute(payload)
        
        assert result["success"] is True
        pkg = result["reproducibility_package"]
        
        # Check mandatory fields for scientific audit
        assert "timestamp" in pkg
        assert "execution_time_ms" in pkg
        assert "skill_name" in pkg
        assert "skill_version" in pkg
        assert "input_hash_sha256" in pkg
        assert pkg["local_execution"] is True
        assert pkg["status"] == "SUCCESS"

    def test_input_hashing_consistency(self):
        """Ensure the same input produces the same hash for audit trails."""
        skill = NeuroPharmGxSkill()
        payload = {"patient_id": "SAME", "data": [1, 2, 3]}
        
        # We need to call _analyze or just mock the hash internal
        res1 = skill.execute(payload)
        res2 = skill.execute(payload)
        
        assert res1["reproducibility_package"]["input_hash_sha256"] == \
               res2["reproducibility_package"]["input_hash_sha256"]

class TestNeuroPharmGx:
    """Clinical validation for Pharmacogenomics skill."""
    
    @pytest.fixture
    def skill(self):
        return NeuroPharmGxSkill()

    def test_cyp2d6_poor_metabolizer_alert(self, skill):
        """Verify recommendation for a CYP2D6 Poor Metabolizer (Fluoxetine)."""
        payload = {
            "patient_id": "PAT-POOR",
            "diplotypes": {"CYP2D6": "*4/*4"},
            "drugs": ["fluoxetina"]
        }
        result = skill.execute(payload)
        data = result["data"]
        
        # Check phenotype calculation
        assert data["phenotype_profile"]["CYP2D6"] == "Metabolizador Pobre"
        
        # Check clinical recommendation logic
        analysis = data["analyses"][0]
        assert analysis["drug"] == "fluoxetina"
        assert analysis["status"] == "ALERTA"
        assert "REDUCIR DOSIS" in analysis["recommendation"]
        assert "escitalopram" in analysis["alternative"].lower()

    def test_normal_metabolizer_success(self, skill):
        """Verify standard recommendation for Normal Metabolizer."""
        payload = {
            "patient_id": "PAT-NORMAL",
            "diplotypes": {"CYP2D6": "*1/*1"},
            "drugs": ["fluoxetina"]
        }
        result = skill.execute(payload)
        analysis = result["data"]["analyses"][0]
        
        assert analysis["status"] == "OK"
        assert "Dosis estándar" in analysis["recommendation"]

class TestNeuroGeriatricRisk:
    """Clinical validation for Geriatric Risk skill."""
    
    @pytest.fixture
    def skill(self):
        return NeuroGeriatricRiskSkill()

    def test_apoe4_high_risk(self, skill):
        """Verify risk score for APOE E4/E4 genotype."""
        payload = {
            "genotypes": {"APOE": "E4/E4"}
        }
        result = skill.execute(payload)
        data = result["data"]
        
        assert data["overall_risk_score"] >= 8
        assert "ALTO" in data["detailed_analysis"]["apoe_analysis"]["risk_level"]

    def test_apoe2_protection(self, skill):
        """Verify protective score for APOE E2/E2 genotype."""
        payload = {
            "genotypes": {"APOE": "E2/E2"}
        }
        result = skill.execute(payload)
        data = result["data"]
        
        # Negative points for protection, score at 0
        assert data["overall_risk_score"] == 0
        assert "PROTECTOR" in data["detailed_analysis"]["apoe_analysis"]["risk_level"]

class TestNeuroNutriGx:
    """Clinical validation for Nutrigenomics skill."""
    
    @pytest.fixture
    def skill(self):
        return NeuroNutriGxSkill()

    def test_mthfr_tt_advice(self, skill):
        """Verify advice for MTHFR TT genotype (Methylation)."""
        payload = {
            "genotypes": {"MTHFR": "TT"}
        }
        result = skill.execute(payload)
        data = result["data"]
        
        # Check if Methylfolate is specifically recommended
        found_methyl = False
        for rec in data["core_recommendations"]:
            if "Metilfolato" in rec:
                found_methyl = True
        
        assert found_methyl is True
        assert data["nutritional_profile"]["methylation_status"]["priority"] == "ALTA"
