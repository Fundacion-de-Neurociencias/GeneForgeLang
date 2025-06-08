import collections

bed_file = "./datasets/ChIP_seq/merged_peaks.bed"
chrom_counts = collections.Counter()
sizes = []

with open(bed_file) as f:
    for line in f:
        if line.strip():
            fields = line.strip().split()
            if len(fields) >= 3:
                chrom, start, end = fields[:3]
                chrom_counts[chrom] += 1
                sizes.append(int(end) - int(start))

print(f"Total peaks: {len(sizes)}")
print("Peaks per chromosome:")
for chrom, count in chrom_counts.most_common():
    print(f"  {chrom}: {count}")
if sizes:
    print(f"Peak size (bp): mean={sum(sizes)//len(sizes)}, min={min(sizes)}, max={max(sizes)}")
else:
    print("No peaks found!")
