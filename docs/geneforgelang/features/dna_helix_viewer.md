# Multi-Dimensional Dynamic DNA Helix Explorer (`GF-HelixView`)

## Overview

The **GeneForge Multi-Dimensional Dynamic DNA Helix Explorer (`GF-HelixView`)** introduces a state-of-the-art interactive visualization instrument that brings physical bio-computing to life. Inspired by the dynamic B-DNA viewer by Muhammad Sohaib Hassan (*DMD* 20,000 bp prototype), `GF-HelixView` transforms flat nucleotide sequences into an active, multi-dimensional genomic canvas.

It pairs canonical right-handed **B-DNA double helix physics** (antiparallel 5'&rarr;3' and 3'&rarr;5' strands, outer sugar-phosphate winding backbones, 2 vs. 3 hydrogen bond energetics, and major/minor groove geometry) with the full multi-omic dimensions of GeneForgeLang (GFL):
- **Exon/Intron Splicing Boundaries**: Canonical donor (`GT`) and acceptor (`AG`) splice sites, phase transitions, and exon skipping hotspots.
- **Reading Frames & Dynamic Translation**: 3-frame codon triplet translation, amino acid assignment, stop codon detection, and real-time **frameshift alerts** if deletions or insertions disrupt the open reading frame.
- **ClinVar Pathogenic Variant Overlays**: Pathogenic, likely pathogenic, and VUS variant pins mapped to exact coordinates with ACMG classifications and disease phenotypes.
- **Epigenetic Marks (5mC / 5hmC)**: Cytosine methylation profiling at single-base CpG resolution.
- **CRISPR-Cas PAM Scanner**: Protospacer adjacent motif recognition (`NGG`, `TTTV`), 20-nt guide RNA target windows, and double-strand break cut site markers.

---

## 1. Biophysical & Helical Architecture

Canonical Watson-Crick B-DNA geometry is modeled using empirical constants:
- **Helical Pitch ($p$)**: $3.4\text{ nm}$ per complete $360^\circ$ turn.
- **Rise per Base Pair ($h$)**: $0.34\text{ nm}$ per step.
- **Base Pairs per Turn ($n$)**: $10.0$ to $10.5\text{ bp}$.
- **Helix Diameter ($d$)**: $2.0\text{ nm}$ outer perimeter, $1.1\text{ nm}$ base pair span.
- **Grooves**: Major groove ($2.2\text{ nm}$, wide gap) and Minor groove ($1.2\text{ nm}$, narrow gap).
- **Hydrogen Bonding Thermodynamics**:
  - Adenine (A) &ndash; Thymine (T): 2 hydrogen bonds ($\approx 2\text{--}3\text{ kcal/mol}$).
  - Guanine (G) &ndash; Cytosine (C): 3 hydrogen bonds ($\approx 5\text{--}7\text{ kcal/mol}$).
- **Purines vs. Pyrimidines**:
  - Purines (**A**, **G**): Two fused heterocyclic rings (longer base block).
  - Pyrimidines (**T**, **C**): Single heterocyclic ring (shorter base block).

---

## 2. Declarative GFL Specification (`dna_viewer`)

```gfl
# DMD Exons 44-51 Multi-Omic DNA Helix Explorer
dna_viewer DMD_Helix_Scanner:
  viewer_id: "dmd_exons44_51_scanner"
  target_gene: "DMD"
  genomic_range: "chrX:31119222-31139222"
  reference_build: "GRCh38"
  helix_type: "b_dna"
  active_coordinate: 161
  raw_sequence: "ATGCTTTGGTGGGAAGAAGTAGAGGACTGTTATGAAAGAGAAGATGTT..."
  tracks:
    - "exons"
    - "reading_frames"
    - "clinvar_variants"
    - "epigenetics_5hmc"
    - "crispr_pam_sites"
  exons:
    - exon_number: 44
      start_coord: 1
      end_coord: 148
      phase: 0
      splice_donor: "GT"
      splice_acceptor: "AG"
    - exon_number: 45
      start_coord: 149
      end_coord: 324
      phase: 1
      splice_donor: "GT"
      splice_acceptor: "AG"
  variants:
    - coordinate: 161
      ref_allele: "T"
      alt_allele: "A"
      variant_id: "VCV000098451"
      pathogenicity: "pathogenic"
      molecular_consequence: "nonsense (p.Arg54Ter)"
      condition: "Duchenne Muscular Dystrophy"
  epigenetic_marks:
    - coordinate: 105
      modification_type: "5hmC"
      modification_probability: 0.94
  crispr_sites:
    - pam_sequence: "TGG"
      start_coord: 155
      strand: "+"
      target_grna_20nt: "TCAGTGACCTACAGGATGGG"
      cleavage_offset: -3
  interactive: true
  export_format: "html"
```

---

## 3. Python API & Command-Line Usage

### Command-Line Interface (CLI)
```bash
# Visualize a FASTA sequence directly
gfl view dna --fasta path/to/sequence.fasta --gene DMD --coord 161 --output dmd_helix.html

# Visualize directly from a GFL protocol file
gfl view dna examples/dmd_gene_helix_viewer.gfl --output visualizations/dmd_viewer.html

# Launch and automatically open in default web browser
gfl view dna --gene DMD --open
```

### Programmatic Python Usage
```python
from geneforgelang.core.gftypes import DNAViewerContract, HelixConformation, ViewerTrackType
from geneforgelang.visualization.dna_helix_viewer import render_dna_helix_viewer

contract = DNAViewerContract(
    viewer_id="my_dmd_viewer",
    target_gene="DMD",
    helix_type=HelixConformation.B_DNA,
    active_coordinate=161,
    tracks=[ViewerTrackType.EXONS, ViewerTrackType.READING_FRAMES, ViewerTrackType.CLINVAR_VARIANTS],
)

# Render self-contained HTML5 string or write to disk
html = render_dna_helix_viewer(contract, output_path="visualizations/my_dmd_viewer.html")
```

---

## 4. Generative UI & Sidecar Compatibility

The output produced by `GF-HelixView` is **100% self-contained**:
- **Zero NPM / Node dependencies**.
- **Zero external CDN script or stylesheet fetches** (fully operable in offline air-gapped clinical environments).
- Directly embeddable as an Antigravity Generative UI widget, inside sidecar viewer panels, or exported to standalone files for scientific presentations and peer review supplements.
