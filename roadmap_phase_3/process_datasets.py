import os

import pybedtools
import pysam

# Procesar archivo BAM de ATAC-seq
bam_path = "./datasets/ATAC_seq/ENCFF000ATG.bam"
if os.path.exists(bam_path):
    bamfile = pysam.AlignmentFile(bam_path, "rb")
    total_reads = bamfile.count()
    print(f"Total reads processed: {total_reads}")
    bamfile.close()
else:
    print(f"BAM file not found: {bam_path}")

# Procesar archivo BED de ChIP-seq
bed_path = "./datasets/ChIP_seq/ENCFF001UJU.bed.gz"
out_path = "./datasets/ChIP_seq/merged_peaks.bed"
if os.path.exists(bed_path):
    bed = pybedtools.BedTool(bed_path)
    merged = bed.sort().merge()
    merged.saveas(out_path)
    print(f"Number of merged peaks: {len(merged)}")
    print("Merged peaks saved.")
else:
    print(f"ChIP-seq BED file not found: {bed_path}")
