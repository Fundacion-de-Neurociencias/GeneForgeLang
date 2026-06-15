"""Corpus ingestion tool: fetches PubMed papers and generates GFL fixtures for Auditoría B."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

# Configuracion
QUERY = "lewy body dementia OR creutzfeldt-jakob OR alzheimer"
RETMAX = 50
OUTPUT_DIR = Path("tests/fixtures/real_world_corpus")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_pmids() -> list[str]:
    url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={urllib.parse.quote(QUERY)}&retmode=json&retmax={RETMAX}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "GeneForgeLang/1.0"})
    try:
        with urllib.request.urlopen(req) as response:  # noqa: S310
            data: dict[str, object] = json.loads(response.read().decode())
            result = data.get("esearchresult", {})
            if isinstance(result, dict):
                ids = result.get("idlist", [])
                if isinstance(ids, list):
                    return [str(i) for i in ids]
    except Exception as exc:
        print(f"Error fetching PMIDs: {exc}")
    return []


def fetch_summaries(pmids: list[str]) -> dict[str, dict[str, object]]:
    if not pmids:
        return {}
    ids_str = ",".join(pmids)
    url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={ids_str}&retmode=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "GeneForgeLang/1.0"})
    try:
        with urllib.request.urlopen(req) as response:  # noqa: S310
            data: dict[str, object] = json.loads(response.read().decode())
            result = data.get("result", {})
            if isinstance(result, dict):
                return {k: v for k, v in result.items() if isinstance(v, dict)}
    except Exception as exc:
        print(f"Error fetching summaries: {exc}")
    return {}


def generate_gfl(pmid: str, summary: dict[str, object]) -> Optional[str]:
    raw_title = summary.get("title", "")
    title = str(raw_title).replace('"', "'") if raw_title else ""
    if not title:
        return None

    return f"""observation:
  id: "PMID_{pmid}"
  type: clinical_report
  description: "{title}"
  disease_entity: LEWY_BODY_DEMENTIA
  criteria:
    - criterion_id: CRITERIA_CLINICAL_PHENOTYPE
      criterion_description: "Evaluated in study: {title}"
      weight_tier: HIGH
  epistemic_state:
    truth_support: SUPPORTED
    temporal_stability: STABLE
    observational_resolution: HIGH_RESOLUTION
    ecological_scope: RESTRICTED
    contradiction_load: NONE
  source_citation: "PMID: {pmid}"
"""


def main() -> None:
    print("Fetching PMIDs from PubMed...")
    pmids = fetch_pmids()
    print(f"Found {len(pmids)} papers. Fetching summaries...")
    summaries = fetch_summaries(pmids)

    count = 0
    for pmid in pmids:
        summary = summaries.get(pmid)
        if summary:
            gfl = generate_gfl(pmid, summary)
            if gfl:
                out_path = OUTPUT_DIR / f"pmid_{pmid}.gfl"
                out_path.write_text(gfl, encoding="utf-8")
                count += 1

    print("Generating synthetic variants for structural stress testing...")
    for i in range(1, 151):
        gfl_content = f"""observation:
  id: "SYNTH_{i}"
  type: simulated_record
  disease_entity: CJD_SPORADIC
  criteria:
    - criterion_id: CRITERIA_SYNTH_{i}
      weight_tier: MEDIUM
  epistemic_state:
    truth_support: UNSUPPORTED
    temporal_stability: UNSTABLE
    observational_resolution: LOW_RESOLUTION
    ecological_scope: ISOLATED
    contradiction_load: CONTESTED
  parse_trace: "noise_{i}"
"""
        out_path = OUTPUT_DIR / f"synth_{i}.gfl"
        out_path.write_text(gfl_content, encoding="utf-8")
        count += 1

    print(f"Successfully generated {count} GFL files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
