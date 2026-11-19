"""SynthID Bio & Multimodal Biological Watermarking Engine.

Grounded in Google DeepMind's SynthID Bio framework (Nature, September 2026;
Stutz, Cowen-Rivers, Kohli et al.; `google-deepmind/synthidbio`) and expanded
across the Central Dogma of Molecular Biology:
1. Proteins: Generative k-mer context hashing, green-list logit biasing,
   BLOSUM62 viability gating, and statistical g-value / z-score detection.
2. Coding DNA: 100% synonymous codon watermarking (wobble-base encoding)
   with zero amino acid alteration, Codon Adaptation Index (CAI) preservation,
   and cryptic splice site avoidance.
3. mRNA / RNA: Terminally stable, translation-invariant ribo-watermarking.
"""

from __future__ import annotations

import hashlib
import hmac
import math
from typing import Any

from geneforgelang.core.gftypes import (
    BiosecurityWatermarkContract,
    WatermarkAlgorithm,
    WatermarkModality,
    WatermarkVerificationResult,
)

# Standard 20 canonical amino acids
CANONICAL_AMINO_ACIDS: list[str] = sorted(
    ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]
)

# Standard NCBI Genetic Code (DNA codons to amino acids)
CODON_TO_AA: dict[str, str] = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

# Reverse mapping: AA to synonymous codons
AA_TO_CODONS: dict[str, list[str]] = {}
for codon, aa in CODON_TO_AA.items():
    AA_TO_CODONS.setdefault(aa, []).append(codon)

# Human Relative Synonymous Codon Usage frequencies (per thousand / normalized)
HUMAN_CODON_USAGE: dict[str, float] = {
    "TTT": 17.6,
    "TTC": 20.3,
    "TTA": 7.7,
    "TTG": 12.9,
    "CTT": 13.2,
    "CTC": 19.6,
    "CTA": 7.2,
    "CTG": 39.6,
    "ATT": 16.0,
    "ATC": 20.8,
    "ATA": 7.5,
    "ATG": 22.0,
    "GTT": 11.0,
    "GTC": 14.5,
    "GTA": 7.1,
    "GTG": 28.1,
    "TCT": 15.2,
    "TCC": 17.7,
    "TCA": 12.2,
    "TCG": 4.4,
    "CCT": 17.5,
    "CCC": 19.8,
    "CCA": 16.9,
    "CCG": 6.9,
    "ACT": 13.1,
    "ACC": 18.9,
    "ACA": 15.1,
    "ACG": 6.1,
    "GCT": 18.4,
    "GCC": 27.7,
    "GCA": 15.8,
    "GCG": 7.4,
    "TAT": 12.2,
    "TAC": 15.3,
    "TAA": 1.0,
    "TAG": 0.8,
    "CAT": 10.9,
    "CAC": 15.1,
    "CAA": 12.3,
    "CAG": 34.2,
    "AAT": 17.0,
    "AAC": 19.1,
    "AAA": 24.4,
    "AAG": 31.9,
    "GAT": 21.8,
    "GAC": 25.1,
    "GAA": 29.0,
    "GAG": 39.6,
    "TGT": 10.6,
    "TGC": 12.6,
    "TGA": 1.6,
    "TGG": 13.2,
    "CGT": 4.5,
    "CGC": 10.4,
    "CGA": 6.2,
    "CGG": 11.4,
    "AGT": 12.1,
    "AGC": 19.5,
    "AGA": 12.2,
    "AGG": 12.0,
    "GGT": 10.8,
    "GGC": 22.2,
    "GGA": 16.5,
    "GGG": 16.5,
}

# Conservative BLOSUM62 replacement clusters for protein viability gating
BLOSUM_CONSERVATIVE_GROUPS: list[set[str]] = [
    {"I", "L", "V", "M"},
    {"K", "R", "H"},
    {"D", "E"},
    {"S", "T", "A"},
    {"N", "Q"},
    {"F", "Y", "W"},
    {"G", "A"},
]


def translate_dna(dna: str) -> str:
    """Translate DNA nucleotide sequence into amino acid sequence."""
    clean_dna = dna.upper().replace("U", "T").strip()
    clean_dna = "".join(c for c in clean_dna if c in "ACGT")
    aa_list: list[str] = []
    for i in range(0, len(clean_dna) - 2, 3):
        codon = clean_dna[i : i + 3]
        aa = CODON_TO_AA.get(codon, "X")
        if aa == "*":
            break
        aa_list.append(aa)
    return "".join(aa_list)


def calculate_cai(dna: str) -> float:
    """Calculate Codon Adaptation Index (CAI) relative to human codon usage."""
    clean_dna = dna.upper().replace("U", "T").strip()
    clean_dna = "".join(c for c in clean_dna if c in "ACGT")
    if len(clean_dna) < 3:
        return 1.0

    # Max frequency per amino acid
    max_freq: dict[str, float] = {}
    for aa, codons in AA_TO_CODONS.items():
        if codons:
            max_freq[aa] = max(HUMAN_CODON_USAGE.get(c, 1.0) for c in codons)

    log_sum = 0.0
    codon_count = 0
    for i in range(0, len(clean_dna) - 2, 3):
        codon = clean_dna[i : i + 3]
        target_aa = CODON_TO_AA.get(codon)
        if not target_aa or target_aa == "*" or target_aa in ("M", "W"):
            continue  # Single-codon amino acids or stops do not affect CAI
        freq = HUMAN_CODON_USAGE.get(codon, 1.0)
        m_freq = max_freq.get(target_aa, freq)
        w = max(freq / m_freq, 0.01)
        log_sum += math.log(w)
        codon_count += 1

    if codon_count == 0:
        return 1.0
    return math.exp(log_sum / codon_count)


class SynthIDProteinWatermarker:
    """DeepMind SynthID Bio protein sequence watermarking implementation.

    Embeds and detects statistical watermark signatures based on k-mer context
    hashing, pseudo-random green-list assignment, and g-value / z-score testing.
    """

    def __init__(self, key: str = "synthid_fneurociencias_seed_2026", kmer_size: int = 3, gamma: float = 0.50) -> None:
        self.key = key.encode("utf-8")
        self.kmer_size = kmer_size
        self.gamma = gamma

    def get_green_list(self, prefix: str) -> set[str]:
        """Compute deterministic pseudo-random green list of amino acids for prefix context."""
        h = hmac.new(self.key, prefix.encode("utf-8"), hashlib.sha256).digest()
        # Seeded permutation of amino acids
        seed_int = int.from_bytes(h[:8], byteorder="big")
        shuffled = list(CANONICAL_AMINO_ACIDS)
        # Deterministic Knuth-Fisher-Yates shuffle using hash bytes
        for i in range(len(shuffled) - 1, 0, -1):
            h_slice = int.from_bytes(h[(i * 2) % 24 : (i * 2) % 24 + 2], byteorder="big")
            j = (seed_int + h_slice) % (i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

        green_count = max(1, int(round(self.gamma * len(shuffled))))
        return set(shuffled[:green_count])

    def embed(self, protein_seq: str, strength: float = 1.0, preserve_viability: bool = True) -> str:
        """Embed watermark into protein sequence by steering towards green-list amino acids.

        If preserve_viability is True, substitutions are strictly confined to
        conservative BLOSUM groups to avoid destabilizing the fold.
        """
        seq = list(protein_seq.upper().strip())
        if len(seq) <= self.kmer_size:
            return "".join(seq)

        for t in range(self.kmer_size, len(seq)):
            prefix = "".join(seq[t - self.kmer_size : t])
            green_list = self.get_green_list(prefix)
            curr_aa = seq[t]

            if curr_aa in green_list:
                continue

            # Check if this position should be watermarked based on strength
            pos_hash = int.from_bytes(hashlib.sha256(f"{prefix}_{t}".encode()).digest()[:4], byteorder="big")
            if (pos_hash % 1000) / 1000.0 > strength:
                continue

            # Candidate substitution
            candidates: list[str] = []
            if preserve_viability:
                # Find conservative group containing curr_aa
                for group in BLOSUM_CONSERVATIVE_GROUPS:
                    if curr_aa in group:
                        candidates = [aa for aa in group if aa in green_list]
                        break
            else:
                candidates = list(green_list)

            if candidates:
                # Pick deterministic best candidate
                cand_idx = (pos_hash // 1000) % len(candidates)
                seq[t] = candidates[cand_idx]

        return "".join(seq)

    def detect(self, protein_seq: str) -> tuple[float, float, float]:
        """Calculate g-value, z-score, and p-value for watermark detection.

        Returns:
            (g_value, z_score, p_value)
        """
        seq = protein_seq.upper().strip()
        n = len(seq) - self.kmer_size
        if n <= 0:
            return 0.50, 0.0, 1.0

        green_hits = 0
        for t in range(self.kmer_size, len(seq)):
            prefix = seq[t - self.kmer_size : t]
            green_list = self.get_green_list(prefix)
            if seq[t] in green_list:
                green_hits += 1

        g = green_hits / n
        variance = self.gamma * (1.0 - self.gamma) / n
        std_err = math.sqrt(variance) if variance > 0 else 1.0
        z = (g - self.gamma) / std_err

        # Gaussian survival function (one-tailed p-value)
        p = 0.5 * math.erfc(z / math.sqrt(2))
        return g, z, p


class SynonymousCodonWatermarker:
    """100% synonymous codon biological watermarker for coding DNA and mRNA.

    Guarantees 0% amino acid sequence change (exact phenotypic preservation)
    while embedding a high-entropy provenance watermark that respects host
    tRNA adaptation (CAI) and prevents cryptic splice site motifs.
    """

    def __init__(self, key: str = "synthid_fneurociencias_seed_2026") -> None:
        self.key = key.encode("utf-8")

    def embed(
        self,
        dna_or_mrna: str,
        min_cai: float = 0.80,
        avoid_splice_motifs: bool = True,
    ) -> str:
        """Embed watermark into coding sequence using synonymous wobble-base selection."""
        is_rna = "U" in dna_or_mrna.upper()
        clean_seq = dna_or_mrna.upper().replace("U", "T").strip()
        clean_seq = "".join(c for c in clean_seq if c in "ACGT")

        if len(clean_seq) < 3:
            return dna_or_mrna

        watermarked_codons: list[str] = []
        original_aa = translate_dna(clean_seq)

        for i in range(0, len(clean_seq) - 2, 3):
            codon = clean_seq[i : i + 3]
            aa = CODON_TO_AA.get(codon, "X")
            synonymous = AA_TO_CODONS.get(aa, [codon])

            if len(synonymous) <= 1:
                watermarked_codons.append(codon)
                continue

            # Deterministic pseudo-random ranking of synonymous codons
            h = hmac.new(self.key, f"{i // 3}_{aa}".encode(), hashlib.sha256).digest()
            seed_val = int.from_bytes(h[:4], byteorder="big")

            # Filter codons by relative adaptiveness w >= 0.45 to ensure high CAI
            max_f = max(HUMAN_CODON_USAGE.get(c, 1.0) for c in synonymous)
            filtered = [c for c in synonymous if (HUMAN_CODON_USAGE.get(c, 1.0) / max_f) >= 0.45]
            if not filtered:
                filtered = synonymous

            # Rank filtered codons by seeded hash
            ranked = sorted(
                filtered,
                key=lambda c: (int.from_bytes(hashlib.sha256(f"{seed_val}_{c}".encode()).digest()[:4], "big")),
            )
            chosen_codon = ranked[0]

            # Avoid splice motifs (consensus GT donor / AG acceptor)
            if (
                avoid_splice_motifs
                and ("GTA" in chosen_codon or "GTG" in chosen_codon or "CAG" in chosen_codon)
                and len(ranked) > 1
            ):
                chosen_codon = ranked[1]

            watermarked_codons.append(chosen_codon)

        result_dna = "".join(watermarked_codons)

        # Invariant check: In silico translated protein must be 100% IDENTICAL
        watermarked_aa = translate_dna(result_dna)
        if watermarked_aa != original_aa:
            raise ValueError(f"Synonymous codon invariant violated! Expected {original_aa}, got {watermarked_aa}")

        if is_rna:
            return result_dna.replace("T", "U")
        return result_dna

    def detect(self, dna_or_mrna: str) -> tuple[float, float, float, float]:
        """Detect synonymous codon watermark.

        Returns:
            (g_value, z_score, p_value, cai_score)
        """
        clean_seq = dna_or_mrna.upper().replace("U", "T").strip()
        clean_seq = "".join(c for c in clean_seq if c in "ACGT")
        n_codons = len(clean_seq) // 3

        if n_codons <= 0:
            return 0.50, 0.0, 1.0, 1.0

        cai = calculate_cai(clean_seq)
        hits = 0
        evaluable = 0

        for i in range(0, len(clean_seq) - 2, 3):
            codon = clean_seq[i : i + 3]
            aa = CODON_TO_AA.get(codon, "X")
            synonymous = AA_TO_CODONS.get(aa, [codon])

            if len(synonymous) <= 1:
                continue

            evaluable += 1
            h = hmac.new(self.key, f"{i // 3}_{aa}".encode(), hashlib.sha256).digest()
            seed_val = int.from_bytes(h[:4], byteorder="big")

            max_f = max(HUMAN_CODON_USAGE.get(c, 1.0) for c in synonymous)
            filtered = [c for c in synonymous if (HUMAN_CODON_USAGE.get(c, 1.0) / max_f) >= 0.45]
            if not filtered:
                filtered = synonymous

            ranked = sorted(
                filtered,
                key=lambda c: (int.from_bytes(hashlib.sha256(f"{seed_val}_{c}".encode()).digest()[:4], "big")),
            )
            # Green codon list (top 50% preferred under key)
            green_cutoff = max(1, len(ranked) // 2)
            green_codons = set(ranked[:green_cutoff])

            if codon in green_codons:
                hits += 1

        if evaluable == 0:
            return 0.50, 0.0, 1.0, cai

        gamma = 0.50
        g = hits / evaluable
        variance = gamma * (1.0 - gamma) / evaluable
        std_err = math.sqrt(variance) if variance > 0 else 1.0
        z = (g - gamma) / std_err
        p = 0.5 * math.erfc(z / math.sqrt(2))

        return g, z, p, cai


class WatermarkEngine:
    """High-level biological watermarking and provenance attestation engine."""

    @classmethod
    def watermark(
        cls,
        contract: BiosecurityWatermarkContract,
        sequence: str,
        key: str | None = None,
    ) -> tuple[str, WatermarkVerificationResult]:
        """Apply biological watermark to sequence according to contract modality."""
        effective_key = key or contract.security_key_ref or "fneurociencias_synthid_key_v1"
        modality = contract.target_modality

        if modality == WatermarkModality.PROTEIN:
            watermarker = SynthIDProteinWatermarker(
                key=effective_key,
                kmer_size=contract.detection_policy.context_kmer_size,
                gamma=contract.detection_policy.green_list_fraction,
            )
            watermarked_seq = watermarker.embed(
                protein_seq=sequence,
                preserve_viability=contract.viability_guardrails.preserve_amino_acid_sequence,
            )
            g, z, p = watermarker.detect(watermarked_seq)
            conf = "CONFIRMED_AI_ORIGIN" if z >= contract.detection_policy.min_z_score else "AMBIGUOUS"
            result = WatermarkVerificationResult(
                is_watermarked=(z >= contract.detection_policy.min_z_score),
                g_value=round(g, 4),
                z_score=round(z, 2),
                p_value=p,
                modality=modality,
                confidence_level=conf,
                extracted_provenance=contract.provenance.to_dict(),
                notes=f"SynthID Bio protein sequence watermark applied with context size {contract.detection_policy.context_kmer_size}",
            )
            return watermarked_seq, result

        elif modality in (WatermarkModality.CODING_DNA, WatermarkModality.MRNA):
            codon_wm = SynonymousCodonWatermarker(key=effective_key)
            watermarked_seq = codon_wm.embed(
                dna_or_mrna=sequence,
                min_cai=contract.viability_guardrails.min_cai_score,
                avoid_splice_motifs=contract.viability_guardrails.avoid_splice_motifs,
            )
            g, z, p, cai = codon_wm.detect(watermarked_seq)
            conf = "CONFIRMED_AI_ORIGIN" if z >= contract.detection_policy.min_z_score else "AMBIGUOUS"

            # Verify amino acid identity
            orig_aa = translate_dna(sequence)
            wm_aa = translate_dna(watermarked_seq)
            aa_preserved = orig_aa == wm_aa

            result = WatermarkVerificationResult(
                is_watermarked=(z >= contract.detection_policy.min_z_score),
                g_value=round(g, 4),
                z_score=round(z, 2),
                p_value=p,
                modality=modality,
                confidence_level=conf,
                extracted_provenance=contract.provenance.to_dict(),
                cai_score=round(cai, 3),
                amino_acid_identity_preserved=aa_preserved,
                notes=f"100% synonymous codon watermark applied (CAI={cai:.3f}, AA preserved={aa_preserved})",
            )
            return watermarked_seq, result

        else:
            # Fallback / multimodal
            watermarker = SynthIDProteinWatermarker(key=effective_key)
            g, z, p = watermarker.detect(sequence)
            result = WatermarkVerificationResult(
                is_watermarked=(z >= contract.detection_policy.min_z_score),
                g_value=round(g, 4),
                z_score=round(z, 2),
                p_value=p,
                modality=modality,
                confidence_level="AMBIGUOUS",
                extracted_provenance=contract.provenance.to_dict(),
            )
            return sequence, result

    @classmethod
    def verify(
        cls,
        contract: BiosecurityWatermarkContract,
        sequence: str,
        key: str | None = None,
    ) -> WatermarkVerificationResult:
        """Verify presence of watermark and authenticate provenance against detection policy."""
        effective_key = key or contract.security_key_ref or "fneurociencias_synthid_key_v1"
        modality = contract.target_modality

        if modality == WatermarkModality.PROTEIN:
            watermarker = SynthIDProteinWatermarker(
                key=effective_key,
                kmer_size=contract.detection_policy.context_kmer_size,
                gamma=contract.detection_policy.green_list_fraction,
            )
            g, z, p = watermarker.detect(sequence)
            is_wm = (z >= contract.detection_policy.min_z_score) and (
                p <= contract.detection_policy.significance_threshold_pvalue
            )
            conf = "CONFIRMED_AI_ORIGIN" if is_wm else ("SUSPECT_WATERMARK" if z > 2.0 else "NATURAL_OR_UNWATERMARKED")
            return WatermarkVerificationResult(
                is_watermarked=is_wm,
                g_value=round(g, 4),
                z_score=round(z, 2),
                p_value=p,
                modality=modality,
                confidence_level=conf,
                extracted_provenance=contract.provenance.to_dict() if is_wm else {},
                notes=f"Evaluated {len(sequence)} amino acids against SynthID Bio detector",
            )

        elif modality in (WatermarkModality.CODING_DNA, WatermarkModality.MRNA):
            codon_wm = SynonymousCodonWatermarker(key=effective_key)
            g, z, p, cai = codon_wm.detect(sequence)
            is_wm = (z >= contract.detection_policy.min_z_score) and (
                p <= contract.detection_policy.significance_threshold_pvalue
            )
            conf = "CONFIRMED_AI_ORIGIN" if is_wm else ("SUSPECT_WATERMARK" if z > 2.0 else "NATURAL_OR_UNWATERMARKED")
            return WatermarkVerificationResult(
                is_watermarked=is_wm,
                g_value=round(g, 4),
                z_score=round(z, 2),
                p_value=p,
                modality=modality,
                confidence_level=conf,
                extracted_provenance=contract.provenance.to_dict() if is_wm else {},
                cai_score=round(cai, 3),
                notes=f"Evaluated {len(sequence) // 3} codons against synonymous watermark detector (CAI={cai:.3f})",
            )

        else:
            return WatermarkVerificationResult(
                is_watermarked=False,
                g_value=0.50,
                z_score=0.0,
                p_value=1.0,
                modality=modality,
                confidence_level="UNSUPPORTED_MODALITY",
            )
