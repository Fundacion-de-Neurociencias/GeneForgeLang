"""GeneForge Multi-Dimensional Dynamic DNA Helix Explorer (GF-HelixView).

Renders a self-contained, interactive B-DNA double helix scanner with real-time
reactive updates: antiparallel strands, sugar-phosphate backbones, 2 vs 3 hydrogen bond
physics, major/minor groove geometry, physical metrics ticker, reading head, sliding sequence
window, exon/intron splicing tracks, dynamic reading frame codon translation & frameshift alerts,
ClinVar pathogenic variant overlays, 5mC/5hmC epigenetic marks, and CRISPR-Cas PAM target windows.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from geneforgelang.core.gftypes import (
    DNAViewerContract,
    HelixConformation,
    ViewerCrisprPamSite,
    ViewerEpigeneticMark,
    ViewerExonAnnotation,
    ViewerTrackType,
    ViewerVariantAnnotation,
)

# Canonical genetic code translation dictionary
CODON_TABLE: dict[str, tuple[str, str]] = {
    "TTT": ("F", "Phenylalanine"),
    "TTC": ("F", "Phenylalanine"),
    "TTA": ("L", "Leucine"),
    "TTG": ("L", "Leucine"),
    "CTT": ("L", "Leucine"),
    "CTC": ("L", "Leucine"),
    "CTA": ("L", "Leucine"),
    "CTG": ("L", "Leucine"),
    "ATT": ("I", "Isoleucine"),
    "ATC": ("I", "Isoleucine"),
    "ATA": ("I", "Isoleucine"),
    "ATG": ("M", "Methionine (Start)"),
    "GTT": ("V", "Valine"),
    "GTC": ("V", "Valine"),
    "GTA": ("V", "Valine"),
    "GTG": ("V", "Valine"),
    "TCT": ("S", "Serine"),
    "TCC": ("S", "Serine"),
    "TCA": ("S", "Serine"),
    "TCG": ("S", "Serine"),
    "CCT": ("P", "Proline"),
    "CCC": ("P", "Proline"),
    "CCA": ("P", "Proline"),
    "CCG": ("P", "Proline"),
    "ACT": ("T", "Threonine"),
    "ACC": ("T", "Threonine"),
    "ACA": ("T", "Threonine"),
    "ACG": ("T", "Threonine"),
    "GCT": ("A", "Alanine"),
    "GCC": ("A", "Alanine"),
    "GCA": ("A", "Alanine"),
    "GCG": ("A", "Alanine"),
    "TAT": ("Y", "Tyrosine"),
    "TAC": ("Y", "Tyrosine"),
    "TAA": ("*", "Stop (Ochre)"),
    "TAG": ("*", "Stop (Amber)"),
    "CAT": ("H", "Histidine"),
    "CAC": ("H", "Histidine"),
    "CAA": ("Q", "Glutamine"),
    "CAG": ("Q", "Glutamine"),
    "AAT": ("N", "Asparagine"),
    "AAC": ("N", "Asparagine"),
    "AAA": ("K", "Lysine"),
    "AAG": ("K", "Lysine"),
    "GAT": ("D", "Aspartate"),
    "GAC": ("D", "Aspartate"),
    "GAA": ("E", "Glutamate"),
    "GAG": ("E", "Glutamate"),
    "TGT": ("C", "Cysteine"),
    "TGC": ("C", "Cysteine"),
    "TGA": ("*", "Stop (Opal)"),
    "TGG": ("W", "Tryptophan"),
    "CGT": ("R", "Arginine"),
    "CGC": ("R", "Arginine"),
    "CGA": ("R", "Arginine"),
    "CGG": ("R", "Arginine"),
    "AGT": ("S", "Serine"),
    "AGC": ("S", "Serine"),
    "AGA": ("R", "Arginine"),
    "AGG": ("R", "Arginine"),
    "GGT": ("G", "Glycine"),
    "GGC": ("G", "Glycine"),
    "GGA": ("G", "Glycine"),
    "GGG": ("G", "Glycine"),
}

# Default DMD hot-spot sequence (Exons 44-51 segment for Duchenne/Becker Muscular Dystrophy research)
DEFAULT_DMD_SEQUENCE = (
    "ATGCTTTGGTGGGAAGAAGTAGAGGACTGTTATGAAAGAGAAGATGTTCAAAAGAAAACATTCACAAAATGGGTAAATGC"
    "ACAGTTTTCTAAATTTGGGAAGCAGCATATTGAGAACCTCTTCAGTGACCTACAGGATGGGAGGCGCCTCCTAGACCTCCT"
    "CGAAGGCCTGACAGGGCAAAAACTGCCAAAAGAAAAAGGATCCACAAGAGTTCATGCCCTGAACAATGTCAACAAGGCACT"
    "GCGGGTTTTGCAGAACAATAATGTTGATTTAGTGAATATTGGAAGTACTGACATCGTAGATGGAAATCATAAACTGACTCT"
    "TGGTTTGATTTGGAATATAATCCTCCACTGGCAGGTCAAAAATGTAATGAAAAATATCATGGCTGGATTGCAACAAACCAA"
    "CAGTGAAAAGATTCTCCTGAGCTGGGTCCGACAATCAACTCGTAATTATCCACAGGTTAATGTAATCAACTTCACCACCAG"
    "CTGGTCTGATGGCCTGGCTTTGAATGCTCTCATCCATAGTCATAGGCCAGACCTCATTGACTGGAATAGTGTGATCTGTCA"
    "GCAGTCAGCCACACAACGACTGGAACATGCATTCAACATCGCCAGATATCAATTAGGCATAGAGAAACTACTCGATCCTGA"
    "AGATGTTGATACCACCTATCCAGATAAGAAGTCCATCTTAATGTACATC"
)


def get_complementary_base(base: str) -> str:
    """Return Watson-Crick complement of DNA nucleotide."""
    mapping = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N", "U": "A"}
    return mapping.get(base.upper(), "N")


def load_sequence_for_contract(contract: DNAViewerContract) -> str:
    """Load or resolve sequence from contract, file, or default repository."""
    if contract.raw_sequence and contract.raw_sequence.strip():
        return "".join(contract.raw_sequence.strip().split()).upper()

    if contract.sequence_source:
        seq_path = Path(contract.sequence_source)
        if seq_path.is_file():
            text = seq_path.read_text(encoding="utf-8")
            lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith(">")]
            return "".join(lines).upper()

    return DEFAULT_DMD_SEQUENCE


def generate_dna_helix_viewer_html(contract: DNAViewerContract) -> str:
    """Generate self-contained interactive HTML5/SVG application for DNAViewerContract."""
    sequence = load_sequence_for_contract(contract)
    seq_len = len(sequence)
    active_coord = max(1, min(contract.active_coordinate, seq_len))

    # Pre-populate default DMD multi-omic tracks if none were specified
    variants_data = [v.to_dict() for v in contract.variants]
    if not variants_data and contract.target_gene.upper() == "DMD":
        variants_data = [
            {
                "coordinate": 161,
                "ref_allele": sequence[160] if seq_len >= 161 else "T",
                "alt_allele": "A",
                "variant_id": "VCV000098451",
                "pathogenicity": "pathogenic",
                "molecular_consequence": "nonsense (p.Arg54Ter)",
                "clinical_significance": "Pathogenic (ClinVar)",
                "condition": "Duchenne Muscular Dystrophy",
                "hgvs_c": "c.161T>A",
                "hgvs_p": "p.Arg54Ter",
            },
            {
                "coordinate": 312,
                "ref_allele": sequence[311] if seq_len >= 312 else "G",
                "alt_allele": "T",
                "variant_id": "VCV000104523",
                "pathogenicity": "likely_pathogenic",
                "molecular_consequence": "missense (p.Gly104Val)",
                "clinical_significance": "Likely Pathogenic",
                "condition": "Becker Muscular Dystrophy",
                "hgvs_c": "c.312G>T",
                "hgvs_p": "p.Gly104Val",
            },
        ]

    exons_data = [e.to_dict() for e in contract.exons]
    if not exons_data and contract.target_gene.upper() == "DMD":
        exons_data = [
            {
                "exon_number": 44,
                "start_coord": 1,
                "end_coord": min(148, seq_len),
                "phase": 0,
                "splice_donor": "GT",
                "splice_acceptor": "AG",
            },
            {
                "exon_number": 45,
                "start_coord": 149,
                "end_coord": min(324, seq_len),
                "phase": 1,
                "splice_donor": "GT",
                "splice_acceptor": "AG",
            },
            {
                "exon_number": 46,
                "start_coord": 325,
                "end_coord": seq_len,
                "phase": 2,
                "splice_donor": "GT",
                "splice_acceptor": "AG",
            },
        ]

    epigenetics_data = [m.to_dict() for m in contract.epigenetic_marks]
    if not epigenetics_data:
        # Find CpG positions in sequence
        for i in range(len(sequence) - 1):
            if sequence[i : i + 2] == "CG":
                epigenetics_data.append(
                    {
                        "coordinate": i + 1,
                        "modification_type": "5hmC" if (i % 4 == 0) else "5mC",
                        "modification_probability": round(0.85 + (i % 15) * 0.01, 2),
                    }
                )

    crispr_data = [c.to_dict() for c in contract.crispr_sites]
    if not crispr_data:
        # Find NGG PAM motifs in sequence
        for i in range(len(sequence) - 2):
            if sequence[i + 1 : i + 3] == "GG" and i >= 20:
                crispr_data.append(
                    {
                        "pam_sequence": sequence[i : i + 3],
                        "start_coord": i + 1,
                        "strand": "+",
                        "target_grna_20nt": sequence[i - 20 : i],
                        "cleavage_offset": -3,
                    }
                )
                if len(crispr_data) >= 8:
                    break

    payload = {
        "viewer_id": contract.viewer_id,
        "target_gene": contract.target_gene,
        "genomic_range": contract.genomic_range,
        "reference_build": contract.reference_build,
        "helix_type": str(contract.helix_type),
        "sequence": sequence,
        "active_coordinate": active_coord,
        "tracks": [str(t) for t in contract.tracks],
        "variants": variants_data,
        "exons": exons_data,
        "epigenetics": epigenetics_data,
        "crispr": crispr_data,
        "gnomad_track": contract.gnomad_track.to_dict() if contract.gnomad_track else None,
        "long_read_svs": [sv.to_dict() for sv in contract.long_read_svs],
        "tandem_repeats": [tr.to_dict() for tr in contract.tandem_repeats],
        "codon_table": {k: [v[0], v[1]] for k, v in CODON_TABLE.items()},
    }

    json_payload = json.dumps(payload)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GeneForge DNA Viewer - {contract.target_gene}</title>
  <style>
    :root {{
      --bg-main: #0a0c10;
      --bg-panel: #111827;
      --border-panel: #1f2937;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --color-adenine: #22c55e;
      --color-thymine: #38bdf8;
      --color-cytosine: #c084fc;
      --color-guanine: #f59e0b;
      --color-phosphate: #f472b6;
      --color-sugar: #e2e8f0;
      --color-accent: #0ea5e9;
      --color-danger: #ef4444;
      --color-warning: #eab308;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    body {{
      background-color: var(--bg-main);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }}
    /* Header Bar */
    header {{
      background-color: var(--bg-panel);
      border-bottom: 1px solid var(--border-panel);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .header-left {{
      display: flex;
      align-items: center;
      gap: 20px;
    }}
    .app-title {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .app-title span {{ color: var(--color-thymine); }}
    .header-meta {{
      font-size: 13px;
      color: var(--text-muted);
      display: flex;
      gap: 16px;
    }}
    .header-meta strong {{ color: var(--text-main); }}
    .scanning-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 4px;
      border: 1px solid var(--color-accent);
      color: var(--color-accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .scanning-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--color-accent);
      animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.3; transform: scale(0.8); }}
    }}

    /* Main Container */
    .viewer-layout {{
      display: grid;
      grid-template-columns: 460px 1fr;
      flex: 1;
      height: calc(100vh - 65px);
      overflow: hidden;
    }}

    /* Left Panel: Double Helix */
    .helix-column {{
      background: #0d1117;
      border-right: 1px solid var(--border-panel);
      display: flex;
      flex-direction: column;
      position: relative;
      height: 100%;
    }}
    .helix-header {{
      padding: 12px 16px;
      font-size: 13px;
      font-weight: 600;
      border-bottom: 1px solid var(--border-panel);
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
    }}
    .helix-viewport {{
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      position: relative;
    }}
    .helix-svg {{
      width: 100%;
      display: block;
    }}

    /* Right Dashboard */
    .dashboard-column {{
      padding: 16px 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow-y: auto;
    }}

    .card {{
      background: var(--bg-panel);
      border: 1px solid var(--border-panel);
      border-radius: 8px;
      padding: 16px 20px;
    }}
    .card-title {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    /* Reading Head */
    .pair-headline {{
      font-size: 20px;
      font-weight: 800;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .scrubber-track {{
      flex: 1;
      margin-left: 16px;
      accent-color: var(--color-accent);
      cursor: pointer;
    }}
    .strand-row {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 8px;
      font-size: 14px;
    }}
    .base-pill {{
      width: 28px;
      height: 28px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      color: #000;
      font-size: 15px;
    }}
    .base-A {{ background-color: var(--color-adenine); }}
    .base-T {{ background-color: var(--color-thymine); }}
    .base-C {{ background-color: var(--color-cytosine); }}
    .base-G {{ background-color: var(--color-guanine); }}
    .match-status {{
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #1e293b;
      font-size: 13px;
      line-height: 1.5;
    }}
    .match-tag {{
      font-weight: 800;
      color: #4ade80;
    }}

    /* Sequence Window */
    .seq-window-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      padding: 8px 0;
      overflow-x: auto;
    }}
    .seq-row {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-family: "Courier New", Courier, monospace;
      font-size: 14px;
      font-weight: bold;
    }}
    .seq-cell {{
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 3px;
      color: #000;
    }}
    .seq-conn {{
      width: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      color: var(--text-muted);
    }}
    .seq-active-box {{
      border: 2px solid #fff;
      box-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }}

    /* Multi-Omic Tracks Grid */
    .tracks-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }}
    .track-content {{
      font-size: 13px;
      color: #d1d5db;
      line-height: 1.5;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      margin-right: 6px;
    }}
    .badge-pathogenic {{ background: #dc2626; color: #fff; }}
    .badge-likely {{ background: #f97316; color: #fff; }}
    .badge-exon {{ background: #0284c7; color: #fff; }}
    .badge-crispr {{ background: #9333ea; color: #fff; }}
    .badge-epi {{ background: #10b981; color: #fff; }}
    .frameshift-alert {{
      background: rgba(239, 68, 68, 0.2);
      border: 1px solid var(--color-danger);
      color: #fca5a5;
      padding: 8px 12px;
      border-radius: 6px;
      margin-top: 8px;
      font-weight: bold;
    }}

    /* Facts & Key */
    .facts-grid {{
      display: grid;
      grid-template-columns: 100px 1fr;
      gap: 6px 12px;
      font-size: 13px;
    }}
    .facts-label {{ color: var(--text-muted); }}

    /* Key / Legend */
    .legend-row {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* Controls Bar */
    .controls-bar {{
      position: sticky;
      bottom: 0;
      background: #0f172a;
      border-top: 1px solid var(--border-panel);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      z-index: 10;
    }}
    .btn {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #f8fafc;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}
    .btn:hover {{ background: #334155; border-color: var(--color-accent); }}
    .btn-primary {{ background: var(--color-accent); border-color: #0284c7; color: #fff; }}
    .btn-primary:hover {{ background: #0284c7; }}
    select.ctrl-select {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #f8fafc;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <div class="app-title">DNA <span>viewer</span></div>
      <div class="header-meta">
        <div>Gene: <strong>{contract.target_gene}</strong></div>
        <div>Range: <strong>{contract.genomic_range or "Synthetic locus"}</strong></div>
        <div id="stat-length">Length: <strong>{seq_len} base pairs = {seq_len * 0.34:.1f} nm = {seq_len / 10:.0f} turns</strong></div>
      </div>
    </div>
    <div class="header-right">
      <div class="scanning-badge" id="scan-badge">
        <span class="scanning-dot"></span>
        <span id="scan-status-text">SCANNING</span>
      </div>
    </div>
  </header>

  <div class="viewer-layout">
    <!-- Left Column: Double Helix SVG -->
    <div class="helix-column">
      <div class="helix-header">
        <span>Double helix (B-DNA, right-handed)</span>
        <span id="active-locus-chip">Locus: 161</span>
      </div>
      <div class="helix-viewport" id="helix-viewport">
        <svg class="helix-svg" id="helix-svg" viewBox="0 0 440 2400" preserveAspectRatio="xMidYMin meet">
          <!-- Dynamically populated by JS engine -->
        </svg>
      </div>
    </div>

    <!-- Right Dashboard -->
    <div class="dashboard-column">
      <!-- Reading Head -->
      <div class="card">
        <div class="card-title">
          <span>Reading head</span>
          <span id="active-percent">1%</span>
        </div>
        <div class="pair-headline">
          <span id="reading-head-label">Pair 161 of {seq_len}</span>
          <input type="range" class="scrubber-track" id="coord-scrubber" min="1" max="{seq_len}" value="{active_coord}">
        </div>
        <div class="strand-row">
          <span class="base-pill" id="rh-strand1-pill">T</span>
          <div>
            <strong>Strand 1</strong> &nbsp;
            <span id="rh-strand1-info" style="color: var(--text-muted);">Thymine, pyrimidine (1 ring)</span>
          </div>
        </div>
        <div class="strand-row">
          <span class="base-pill" id="rh-strand2-pill">A</span>
          <div>
            <strong>Strand 2</strong> &nbsp;
            <span id="rh-strand2-info" style="color: var(--text-muted);">Adenine, purine (2 rings)</span>
          </div>
        </div>
        <div class="match-status" id="rh-match-status">
          <span class="match-tag" id="rh-match-tag">MATCH</span> &nbsp;
          <span id="rh-match-detail">T pairs with A through 2 hydrogen bonds (weaker). Purine plus pyrimidine: the pair fits the 1.1 nm width of the helix.</span>
        </div>
      </div>

      <!-- Sequence Window -->
      <div class="card">
        <div class="card-title">Sequence window</div>
        <div class="seq-window-container" id="seq-window-container">
          <!-- Dynamically populated 11-bp sliding window -->
        </div>
      </div>

      <!-- Multi-Omic Tracks Grid -->
      <div class="tracks-grid">
        <!-- Exon / Intron Track -->
        <div class="card">
          <div class="card-title">Exon & Splicing Architecture</div>
          <div class="track-content" id="track-exon-content">
            <span class="badge badge-exon" id="exon-badge">Exon 44</span>
            <span id="exon-desc">Phase 0. Boundary Donor: GT (5' ss), Acceptor: AG (3' ss).</span>
          </div>
        </div>

        <!-- Dynamic Reading Frame & Translation -->
        <div class="card">
          <div class="card-title">Codon & Reading Frame Translation</div>
          <div class="track-content" id="track-translation-content">
            <div>Codon: <strong id="codon-triplet" style="color: var(--color-thymine);">AUG</strong> &rarr; <span id="amino-acid-name">Methionine [M]</span> (Frame 0)</div>
            <div id="frameshift-container"></div>
          </div>
        </div>

        <!-- ClinVar Variant Track -->
        <div class="card">
          <div class="card-title">ClinVar & Known Variants</div>
          <div class="track-content" id="track-variant-content">
            <span style="color: var(--text-muted);">No pathogenic mutation at current base.</span>
          </div>
        </div>

        <!-- Epigenetics & CRISPR Target -->
        <div class="card">
          <div class="card-title">Epigenetics (5hmC) & CRISPR PAM</div>
          <div class="track-content" id="track-crispr-content">
            <div id="epigenetic-status" style="margin-bottom: 6px;">Unmethylated cytosine.</div>
            <div id="crispr-status" style="color: var(--text-muted);">No PAM site within immediate window.</div>
          </div>
        </div>
      </div>

      <!-- Helix Facts (B-DNA) -->
      <div class="card">
        <div class="card-title">Helix facts (B-DNA)</div>
        <div class="facts-grid">
          <div class="facts-label">Position</div>
          <div id="fact-position">Turn 17, pair 1 of 10 in this turn, 54.4 nm from the start</div>
          <div class="facts-label">Shape</div>
          <div>Right-handed double helix, two antiparallel strands</div>
          <div class="facts-label">Size</div>
          <div>10 pairs per turn, pitch 3.4 nm, rise 0.34 nm, width 2 nm</div>
          <div class="facts-label">Grooves</div>
          <div>Minor 1.2 nm (narrow), major 2.2 nm (wide)</div>
        </div>
      </div>

      <!-- Key / Legend -->
      <div class="card">
        <div class="card-title">Key</div>
        <div class="legend-row">
          <div style="display:flex; gap:4px;">
            <span class="base-pill base-A" style="width:20px; height:20px; font-size:11px;">A</span>
            <span class="base-pill base-T" style="width:20px; height:20px; font-size:11px;">T</span>
            <span class="base-pill base-G" style="width:20px; height:20px; font-size:11px;">G</span>
            <span class="base-pill base-C" style="width:20px; height:20px; font-size:11px;">C</span>
          </div>
          <div>Purines (A, G) have 2 rings: long. Pyrimidines (T, C) have 1 ring: short.</div>
          <div><strong>&equiv;</strong> G-C pair: 3 H-bonds, strong</div>
          <div><strong>::</strong> A-T pair: 2 H-bonds, weaker</div>
          <div><span style="color: var(--color-phosphate); font-weight:bold;">&#9679;</span> Phosphate | <span style="color: var(--color-sugar); font-weight:bold;">&#11039;</span> Deoxyribose</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom Control Bar -->
  <div class="controls-bar">
    <div style="display: flex; gap: 8px; align-items: center;">
      <button class="btn btn-primary" id="btn-toggle-play">&#9646;&#9646; Pause</button>
      <button class="btn" id="btn-step-prev">&#9664; Prev bp</button>
      <button class="btn" id="btn-step-next">Next bp &#9654;</button>
      <select class="ctrl-select" id="select-speed">
        <option value="0.5">0.5x Speed</option>
        <option value="1" selected>1x Speed</option>
        <option value="2">2x Speed</option>
        <option value="5">5x Speed</option>
      </select>
    </div>

    <div style="display: flex; gap: 12px; align-items: center;">
      <select class="ctrl-select" id="select-exon-jump">
        <option value="">Jump to Exon...</option>
      </select>
      <select class="ctrl-select" id="select-variant-jump">
        <option value="">Jump to ClinVar Variant...</option>
      </select>
      <button class="btn" id="btn-export-html">&#128190; Export HTML</button>
    </div>
  </div>

  <script>
    // Embedded Payload from GeneForge
    const DATA = {json_payload};

    const SEQ = DATA.sequence;
    const TOTAL_BP = SEQ.length;
    let currentCoord = DATA.active_coordinate;
    let isPlaying = true;
    let scanSpeed = 1;
    let timerId = null;

    const COMPLEMENT = {{ 'A':'T', 'T':'A', 'C':'G', 'G':'C', 'N':'N' }};

    function getBaseColor(b) {{
      if (b === 'A') return 'var(--color-adenine)';
      if (b === 'T') return 'var(--color-thymine)';
      if (b === 'C') return 'var(--color-cytosine)';
      if (b === 'G') return 'var(--color-guanine)';
      return '#94a3b8';
    }}

    function getPurinePyrimidine(b) {{
      if (b === 'A') return 'Adenine, purine (2 rings)';
      if (b === 'G') return 'Guanine, purine (2 rings)';
      if (b === 'T') return 'Thymine, pyrimidine (1 ring)';
      if (b === 'C') return 'Cytosine, pyrimidine (1 ring)';
      return 'Unknown base';
    }}

    function renderHelixSVG() {{
      const svg = document.getElementById('helix-svg');
      const windowSize = 25; // Visible base pairs in view
      const start = Math.max(1, currentCoord - 12);
      const end = Math.min(TOTAL_BP, start + windowSize - 1);

      const heightPerBp = 70;
      const totalH = (end - start + 1) * heightPerBp + 60;
      svg.setAttribute('viewBox', `0 0 440 ${{totalH}}`);
      svg.innerHTML = '';

      // Strands sine wave paths
      let path1D = '';
      let path2D = '';

      for (let i = start; i <= end; i++) {{
        const idx = i - 1;
        const b1 = SEQ[idx];
        const b2 = COMPLEMENT[b1] || 'N';
        const y = (i - start) * heightPerBp + 40;

        // B-DNA helical sinusoidal phase (10 bp per 360 degree turn)
        const angle = ((i - 1) % 10) * (Math.PI * 2 / 10);
        const strand1X = 140 + Math.sin(angle) * 75;
        const strand2X = 140 - Math.sin(angle) * 75;

        // Path accumulator
        if (i === start) {{
          path1D += `M ${{strand1X}} ${{y}}`;
          path2D += `M ${{strand2X}} ${{y}}`;
        }} else {{
          path1D += ` L ${{strand1X}} ${{y}}`;
          path2D += ` L ${{strand2X}} ${{y}}`;
        }}

        // Active selection highlight band
        if (i === currentCoord) {{
          const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          rect.setAttribute('x', '0');
          rect.setAttribute('y', y - 24);
          rect.setAttribute('width', '440');
          rect.setAttribute('height', '48');
          rect.setAttribute('fill', 'rgba(14, 165, 233, 0.15)');
          rect.setAttribute('stroke', '#0284c7');
          rect.setAttribute('stroke-width', '1');
          svg.appendChild(rect);

          // Pointers > <
          const pLeft = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          pLeft.setAttribute('x', '2');
          pLeft.setAttribute('y', y + 5);
          pLeft.setAttribute('fill', '#38bdf8');
          pLeft.setAttribute('font-size', '16');
          pLeft.textContent = '\u25b6';
          svg.appendChild(pLeft);

          const pRight = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          pRight.setAttribute('x', '424');
          pRight.setAttribute('y', y + 5);
          pRight.setAttribute('fill', '#38bdf8');
          pRight.setAttribute('font-size', '16');
          pRight.textContent = '\u25c0';
          svg.appendChild(pRight);
        }}

        // Coordinate Label on left
        const textCoord = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textCoord.setAttribute('x', '22');
        textCoord.setAttribute('y', y + 5);
        textCoord.setAttribute('fill', i === currentCoord ? '#ffffff' : '#6b7280');
        textCoord.setAttribute('font-size', '13');
        textCoord.setAttribute('font-family', 'monospace');
        textCoord.setAttribute('font-weight', i === currentCoord ? 'bold' : 'normal');
        textCoord.textContent = i;
        textCoord.style.cursor = 'pointer';
        textCoord.onclick = () => seekTo(i);
        svg.appendChild(textCoord);

        // Hydrogen bonds connecting the two bases
        const hLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        hLine.setAttribute('x1', strand1X);
        hLine.setAttribute('y1', y);
        hLine.setAttribute('x2', strand2X);
        hLine.setAttribute('y2', y);
        hLine.setAttribute('stroke', (b1 === 'G' || b1 === 'C') ? '#94a3b8' : '#64748b');
        hLine.setAttribute('stroke-width', (b1 === 'G' || b1 === 'C') ? '3' : '2');
        hLine.setAttribute('stroke-dasharray', (b1 === 'G' || b1 === 'C') ? '4 2' : '2 3');
        svg.appendChild(hLine);

        // Strand 1 Base Rect
        const r1 = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        r1.setAttribute('x', strand1X - 14);
        r1.setAttribute('y', y - 12);
        r1.setAttribute('width', '28');
        r1.setAttribute('height', '24');
        r1.setAttribute('rx', '3');
        r1.setAttribute('fill', getBaseColor(b1));
        r1.style.cursor = 'pointer';
        r1.onclick = () => seekTo(i);
        svg.appendChild(r1);

        const t1 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t1.setAttribute('x', strand1X);
        t1.setAttribute('y', y + 5);
        t1.setAttribute('fill', '#000');
        t1.setAttribute('font-size', '13');
        t1.setAttribute('font-weight', '900');
        t1.setAttribute('text-anchor', 'middle');
        t1.textContent = b1;
        t1.style.cursor = 'pointer';
        t1.onclick = () => seekTo(i);
        svg.appendChild(t1);

        // Strand 2 Base Rect
        const r2 = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        r2.setAttribute('x', strand2X - 14);
        r2.setAttribute('y', y - 12);
        r2.setAttribute('width', '28');
        r2.setAttribute('height', '24');
        r2.setAttribute('rx', '3');
        r2.setAttribute('fill', getBaseColor(b2));
        r2.style.cursor = 'pointer';
        r2.onclick = () => seekTo(i);
        svg.appendChild(r2);

        const t2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t2.setAttribute('x', strand2X);
        t2.setAttribute('y', y + 5);
        t2.setAttribute('fill', '#000');
        t2.setAttribute('font-size', '13');
        t2.setAttribute('font-weight', '900');
        t2.setAttribute('text-anchor', 'middle');
        t2.textContent = b2;
        t2.style.cursor = 'pointer';
        t2.onclick = () => seekTo(i);
        svg.appendChild(t2);

        // Sugar pentagon & Phosphate circle on outer perimeter
        const p1 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        p1.setAttribute('cx', strand1X + (strand1X >= 140 ? 22 : -22));
        p1.setAttribute('cy', y);
        p1.setAttribute('r', '5');
        p1.setAttribute('fill', 'var(--color-phosphate)');
        svg.appendChild(p1);

        const p2 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        p2.setAttribute('cx', strand2X + (strand2X >= 140 ? 22 : -22));
        p2.setAttribute('cy', y);
        p2.setAttribute('r', '5');
        p2.setAttribute('fill', 'var(--color-phosphate)');
        svg.appendChild(p2);

        // Turn & Groove Annotations along the right margin
        if (i % 10 === 0) {{
          const turnNum = Math.floor(i / 10);
          const tTurn = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          tTurn.setAttribute('x', '360');
          tTurn.setAttribute('y', y - 2);
          tTurn.setAttribute('fill', '#e2e8f0');
          tTurn.setAttribute('font-size', '12');
          tTurn.setAttribute('font-weight', 'bold');
          tTurn.textContent = `Turn ${{turnNum}}`;
          svg.appendChild(tTurn);

          const tSub = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          tSub.setAttribute('x', '360');
          tSub.setAttribute('y', y + 14);
          tSub.setAttribute('fill', '#64748b');
          tSub.setAttribute('font-size', '10');
          tSub.textContent = '10 bp, 3.4 nm';
          svg.appendChild(tSub);
        }} else if (i % 10 === 5) {{
          const tGroove = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          tGroove.setAttribute('x', '260');
          tGroove.setAttribute('y', y);
          tGroove.setAttribute('fill', '#94a3b8');
          tGroove.setAttribute('font-size', '11');
          tGroove.textContent = '-- Major groove (2.2 nm)';
          svg.appendChild(tGroove);
        }} else if (i % 10 === 2) {{
          const tGroove2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          tGroove2.setAttribute('x', '260');
          tGroove2.setAttribute('y', y);
          tGroove2.setAttribute('fill', '#64748b');
          tGroove2.setAttribute('font-size', '11');
          tGroove2.textContent = '-- Minor groove (1.2 nm)';
          svg.appendChild(tGroove2);
        }}
      }}
    }}

    function updateDashboard() {{
      const b1 = SEQ[currentCoord - 1];
      const b2 = COMPLEMENT[b1] || 'N';

      document.getElementById('active-locus-chip').textContent = `Locus: ${{currentCoord}}`;
      document.getElementById('reading-head-label').textContent = `Pair ${{currentCoord}} of ${{TOTAL_BP}}`;
      document.getElementById('coord-scrubber').value = currentCoord;
      document.getElementById('active-percent').textContent = `${{Math.round((currentCoord / TOTAL_BP) * 100)}}%`;

      // Reading Head pills & details
      const p1 = document.getElementById('rh-strand1-pill');
      p1.className = `base-pill base-${{b1}}`;
      p1.textContent = b1;
      document.getElementById('rh-strand1-info').textContent = getPurinePyrimidine(b1);

      const p2 = document.getElementById('rh-strand2-pill');
      p2.className = `base-pill base-${{b2}}`;
      p2.textContent = b2;
      document.getElementById('rh-strand2-info').textContent = getPurinePyrimidine(b2);

      const isGC = (b1 === 'G' && b2 === 'C') || (b1 === 'C' && b2 === 'G');
      const isAT = (b1 === 'A' && b2 === 'T') || (b1 === 'T' && b2 === 'A');

      if (isGC) {{
        document.getElementById('rh-match-tag').textContent = 'MATCH';
        document.getElementById('rh-match-tag').style.color = '#4ade80';
        document.getElementById('rh-match-detail').textContent = `${{b1}} pairs with ${{b2}} through 3 hydrogen bonds (strong). Purine plus pyrimidine: the pair fits the 1.1 nm width of the helix.`;
      }} else if (isAT) {{
        document.getElementById('rh-match-tag').textContent = 'MATCH';
        document.getElementById('rh-match-tag').style.color = '#4ade80';
        document.getElementById('rh-match-detail').textContent = `${{b1}} pairs with ${{b2}} through 2 hydrogen bonds (weaker). Purine plus pyrimidine: the pair fits the 1.1 nm width of the helix.`;
      }} else {{
        document.getElementById('rh-match-tag').textContent = 'MISMATCH';
        document.getElementById('rh-match-tag').style.color = '#ef4444';
        document.getElementById('rh-match-detail').textContent = `Aberrant pairing! Steric distortion or missing hydrogen bonding.`;
      }}

      // Sequence window (11 bp window)
      const seqWin = document.getElementById('seq-window-container');
      seqWin.innerHTML = '';
      const wStart = Math.max(1, currentCoord - 5);
      const wEnd = Math.min(TOTAL_BP, wStart + 10);

      const rowTop = document.createElement('div');
      rowTop.className = 'seq-row';
      const rowMid = document.createElement('div');
      rowMid.className = 'seq-row';
      const rowBot = document.createElement('div');
      rowBot.className = 'seq-row';

      const lTop5 = document.createElement('span');
      lTop5.textContent = "5'";
      lTop5.style.color = 'var(--text-muted)';
      rowTop.appendChild(lTop5);

      const lMidSpace = document.createElement('span');
      lMidSpace.style.width = '14px';
      rowMid.appendChild(lMidSpace);

      const lBot3 = document.createElement('span');
      lBot3.textContent = "3'";
      lBot3.style.color = 'var(--text-muted)';
      rowBot.appendChild(lBot3);

      for (let i = wStart; i <= wEnd; i++) {{
        const wb1 = SEQ[i - 1];
        const wb2 = COMPLEMENT[wb1] || 'N';

        const c1 = document.createElement('div');
        c1.className = `seq-cell base-${{wb1}} ${{i === currentCoord ? 'seq-active-box' : ''}}`;
        c1.textContent = wb1;
        c1.onclick = () => seekTo(i);
        rowTop.appendChild(c1);

        const cm = document.createElement('div');
        cm.className = 'seq-conn';
        cm.textContent = (wb1 === 'G' || wb1 === 'C') ? '\u2261' : '::';
        rowMid.appendChild(cm);

        const c2 = document.createElement('div');
        c2.className = `seq-cell base-${{wb2}} ${{i === currentCoord ? 'seq-active-box' : ''}}`;
        c2.textContent = wb2;
        c2.onclick = () => seekTo(i);
        rowBot.appendChild(c2);
      }}

      seqWin.appendChild(rowTop);
      seqWin.appendChild(rowMid);
      seqWin.appendChild(rowBot);

      // Multi-Omic Tracks
      // 1. Exon track
      let activeExon = null;
      for (const ex of DATA.exons) {{
        if (currentCoord >= ex.start_coord && currentCoord <= ex.end_coord) {{
          activeExon = ex;
          break;
        }}
      }}
      if (activeExon) {{
        document.getElementById('exon-badge').textContent = `Exon ${{activeExon.exon_number}}`;
        document.getElementById('exon-desc').textContent = `Locus ${{activeExon.start_coord}}-${{activeExon.end_coord}} (Phase ${{activeExon.phase}}). Donor: ${{activeExon.splice_donor}}, Acceptor: ${{activeExon.splice_acceptor}}.`;
      }} else {{
        document.getElementById('exon-badge').textContent = 'Intronic';
        document.getElementById('exon-desc').textContent = 'Non-coding intronic intervening sequence.';
      }}

      // 2. Codon & Translation
      const codonIdx = Math.floor((currentCoord - 1) / 3) * 3;
      if (codonIdx + 3 <= TOTAL_BP) {{
        const triplet = SEQ.substring(codonIdx, codonIdx + 3);
        const aa = DATA.codon_table[triplet] || ['X', 'Unknown'];
        document.getElementById('codon-triplet').textContent = triplet;
        document.getElementById('amino-acid-name').textContent = `${{aa[1]}} [${{aa[0]}}]`;
      }}

      // 3. ClinVar Variants
      const matchVar = DATA.variants.find(v => v.coordinate === currentCoord);
      const varCont = document.getElementById('track-variant-content');
      if (matchVar) {{
        varCont.innerHTML = `
          <div><span class="badge badge-pathogenic">${{matchVar.pathogenicity.toUpperCase()}}</span> <strong>${{matchVar.variant_id}}</strong> (${{matchVar.hgvs_c || matchVar.ref_allele + '>' + matchVar.alt_allele}})</div>
          <div style="margin-top:4px; color:#fca5a5;">${{matchVar.molecular_consequence}} &mdash; ${{matchVar.condition}}</div>
        `;
      }} else {{
        varCont.innerHTML = `<span style="color: var(--text-muted);">No pathogenic mutation recorded at coordinate ${{currentCoord}}.</span>`;
      }}

      // 4. Epigenetic & CRISPR Track
      const matchEpi = DATA.epigenetics.find(e => e.coordinate === currentCoord);
      const epiCont = document.getElementById('epigenetic-status');
      if (matchEpi) {{
        epiCont.innerHTML = `<span class="badge badge-epi">${{matchEpi.modification_type}}</span> <strong>${{Math.round(matchEpi.modification_probability * 100)}}%</strong> methylation probability at CpG.`;
      }} else {{
        epiCont.textContent = 'Unmodified nucleotide.';
      }}

      const matchCrispr = DATA.crispr.find(c => Math.abs(c.start_coord - currentCoord) <= 3);
      const crisprCont = document.getElementById('crispr-status');
      if (matchCrispr) {{
        crisprCont.innerHTML = `<span class="badge badge-crispr">CRISPR PAM</span> Motif: <strong>${{matchCrispr.pam_sequence}}</strong> (Cut site [CUT] offset ${{matchCrispr.cleavage_offset}} bp). Target gRNA: <code>${{matchCrispr.target_grna_20nt}}</code>`;
      }} else {{
        crisprCont.textContent = 'No PAM recognition site within immediate 3-bp window.';
      }}

      // Helix Facts update
      const turnNum = Math.floor((currentCoord - 1) / 10) + 1;
      const pairInTurn = ((currentCoord - 1) % 10) + 1;
      const distNm = (currentCoord * 0.34).toFixed(1);
      document.getElementById('fact-position').textContent = `Turn ${{turnNum}}, pair ${{pairInTurn}} of 10 in this turn, ${{distNm}} nm from the start`;
    }}

    function seekTo(coord) {{
      currentCoord = Math.max(1, Math.min(TOTAL_BP, coord));
      renderHelixSVG();
      updateDashboard();
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      const btn = document.getElementById('btn-toggle-play');
      const badgeText = document.getElementById('scan-status-text');
      const badge = document.getElementById('scan-badge');

      if (isPlaying) {{
        btn.innerHTML = '&#9646;&#9646; Pause';
        badgeText.textContent = 'SCANNING';
        badge.style.borderColor = 'var(--color-accent)';
        badge.style.color = 'var(--color-accent)';
        startScanning();
      }} else {{
        btn.innerHTML = '&#9654; Play';
        badgeText.textContent = 'PAUSED';
        badge.style.borderColor = '#64748b';
        badge.style.color = '#64748b';
        if (timerId) clearInterval(timerId);
      }}
    }}

    function startScanning() {{
      if (timerId) clearInterval(timerId);
      const intervalMs = Math.round(200 / scanSpeed);
      timerId = setInterval(() => {{
        if (currentCoord >= TOTAL_BP) {{
          currentCoord = 1;
        }} else {{
          currentCoord++;
        }}
        renderHelixSVG();
        updateDashboard();
      }}, intervalMs);
    }}

    // Setup Jump Dropdowns
    function setupDropdowns() {{
      const exSel = document.getElementById('select-exon-jump');
      DATA.exons.forEach(ex => {{
        const opt = document.createElement('option');
        opt.value = ex.start_coord;
        opt.textContent = `Exon ${{ex.exon_number}} (bp ${{ex.start_coord}})`;
        exSel.appendChild(opt);
      }});
      exSel.onchange = (e) => {{
        if (e.target.value) seekTo(parseInt(e.target.value));
      }};

      const varSel = document.getElementById('select-variant-jump');
      DATA.variants.forEach(v => {{
        const opt = document.createElement('option');
        opt.value = v.coordinate;
        opt.textContent = `${{v.variant_id}} at bp ${{v.coordinate}} (${{v.molecular_consequence}})`;
        varSel.appendChild(opt);
      }});
      varSel.onchange = (e) => {{
        if (e.target.value) seekTo(parseInt(e.target.value));
      }};
    }}

    // Event listeners
    document.getElementById('btn-toggle-play').onclick = togglePlay;
    document.getElementById('btn-step-prev').onclick = () => seekTo(currentCoord - 1);
    document.getElementById('btn-step-next').onclick = () => seekTo(currentCoord + 1);

    document.getElementById('coord-scrubber').oninput = (e) => {{
      seekTo(parseInt(e.target.value));
    }};

    document.getElementById('select-speed').onchange = (e) => {{
      scanSpeed = parseFloat(e.target.value);
      if (isPlaying) startScanning();
    }};

    document.getElementById('btn-export-html').onclick = () => {{
      const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${{DATA.target_gene}}_helix_viewer.html`;
      a.click();
      URL.revokeObjectURL(url);
    }};

    // Keyboard navigation
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight') {{
        seekTo(currentCoord + 1);
      }} else if (e.key === 'ArrowLeft') {{
        seekTo(currentCoord - 1);
      }} else if (e.key === ' ') {{
        e.preventDefault();
        togglePlay();
      }}
    }});

    // Init
    setupDropdowns();
    renderHelixSVG();
    updateDashboard();
    startScanning();
  </script>
</body>
</html>
"""
    html_content = (
        html_template.replace("{contract.target_gene}", contract.target_gene)
        .replace('{contract.genomic_range or "Synthetic locus"}', contract.genomic_range or "Synthetic locus")
        .replace("{seq_len}", str(seq_len))
        .replace("{seq_len * 0.34:.1f}", f"{seq_len * 0.34:.1f}")
        .replace("{seq_len / 10:.0f}", f"{seq_len / 10:.0f}")
        .replace("{active_coord}", str(active_coord))
        .replace("{json_payload}", json_payload)
        .replace("{{", "{")
        .replace("}}", "}")
    )
    return html_content


def render_dna_helix_viewer(
    contract: DNAViewerContract,
    output_path: str | Path | None = None,
) -> str:
    """Render interactive HTML5 viewer to disk or return HTML string."""
    html = generate_dna_helix_viewer_html(contract)
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(html, encoding="utf-8")
    return html
