import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("./results/long_peaks_summary.tsv", sep="\t")
plt.figure(figsize=(12, 5))
plt.bar(df["chrom"], df["n_peaks_gt_2000bp"])
plt.xlabel("Chromosome")
plt.ylabel("Number of peaks >2000 bp")
plt.title("Number of long ChIP-seq peaks per chromosome")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("./results/long_peaks_histogram.png")
plt.show()
print("Histograma guardado en ./results/long_peaks_histogram.png")
