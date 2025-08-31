import collections
import os

bed_file = "./datasets/ChIP_seq/merged_peaks.bed"
output_file = "./results/long_peaks_summary.tsv"
peak_cutoff = 2000  # longitud mínima de pico (bp)

chr_peaks = collections.defaultdict(list)
with open(bed_file) as f:
    for line in f:
        if line.strip():
            chrom, start, end = line.strip().split()[:3]
            peak_size = int(end) - int(start)
            if peak_size > peak_cutoff:
                chr_peaks[chrom].append((int(start), int(end), peak_size))

os.makedirs("./results", exist_ok=True)

with open(output_file, "w") as out:
    out.write(
        "chrom\tn_peaks_gt_2000bp\ttop1_start\ttop1_end\ttop1_length\ttop2_start\ttop2_end\ttop2_length\ttop3_start\ttop3_end\ttop3_length\n"
    )
    for chrom in sorted(chr_peaks):
        peaks = sorted(chr_peaks[chrom], key=lambda x: x[2], reverse=True)
        n = len(peaks)
        tops = peaks[:3] + [("", "", "")] * (3 - len(peaks))
        tops_flat = [str(x) for peak in tops for x in peak]
        out.write(f"{chrom}\t{n}\t" + "\t".join(tops_flat) + "\n")

print(f"Informe generado: {output_file}")
