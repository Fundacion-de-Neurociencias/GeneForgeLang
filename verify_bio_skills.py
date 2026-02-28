import requests
import json
import time

def test_bio_skills():
    base_url = "http://127.0.0.1:8000"
    
    print("--- 1. Listando Bio-Skills disponibles ---")
    try:
        response = requests.get(f"{base_url}/api/v2/skills")
        if response.status_code == 200:
            skills = response.json().get("skills", [])
            print(f"Skills registradas: {[s['name'] for s in skills]}")
        else:
            print(f"Error al listar skills: {response.status_code}")
            return
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    # TEST PHARMGX
    print("\n--- 2. Ejecutando Neuro-PharmGx (Paciente Pobre en CYP2D6) ---")
    payload = {
        "skill_name": "neuro_pharmgx",
        "inputs": {
            "patient_id": "PAT-NEURO-001",
            "diplotypes": {"CYP2D6": "*4/*4"},
            "drugs": ["fluoxetina"]
        }
    }
    r = requests.post(f"{base_url}/api/v2/skills/execute", json=payload).json()
    print(f"Summary: {r['data']['summary']}")

    # TEST GERIATRIC RISK
    print("\n--- 3. Ejecutando Neuro-Geriatric Risk (Paciente APOE E4/E4) ---")
    payload = {
        "skill_name": "neuro_geriatric_risk",
        "inputs": {
            "patient_id": "PAT-GER-001",
            "genotypes": {"APOE": "E4/E4"}
        }
    }
    r = requests.post(f"{base_url}/api/v2/skills/execute", json=payload).json()
    print(f"Risk Score: {r['data']['overall_risk_score']}/10")
    print(f"Findings: {r['data']['findings']}")

    # TEST NUTRIGX
    print("\n--- 4. Ejecutando Neuro-NutriGx (MTHFR TT) ---")
    payload = {
        "skill_name": "neuro_nutrigx",
        "inputs": {
            "patient_id": "PAT-NUT-001",
            "genotypes": {"MTHFR": "TT", "FADS1": "TT"}
        }
    }
    r = requests.post(f"{base_url}/api/v2/skills/execute", json=payload).json()
    print(f"Summary: {r['data']['summary']}")
    print(f"Recs: {r['data']['core_recommendations']}")

if __name__ == "__main__":
    test_bio_skills()
