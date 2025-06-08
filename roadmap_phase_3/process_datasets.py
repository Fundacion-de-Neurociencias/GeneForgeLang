import os
import pysam
import pybedtools

ATAC_BAM = './datasets/ATAC_seq/ENCFF000ATG.bam'
CHIP_BED = './datasets/ChIP_seq/ENCFF001UJU.bed.gz'

def process_atac_seq(bam_file):
    print(f'Processing ATAC-seq BAM file: {bam_file}')
    bam = pysam.AlignmentFile(bam_file, 'rb')
    count = 0
    for read in bam.fetch():
        count += 1
        if count % 100000 == 0:
            print(f'Processed {count} reads...')
    bam.close()
    print(f'Total reads processed: {count}')

def process_chip_seq(bed_file):
    print(f'Processing ChIP-seq BED file: {bed_file}')
    bed = pybedtools.BedTool(bed_file)
    peaks = bed.merge()
    print(f'Number of merged peaks: {len(peaks)}')
    return peaks

if __name__ == '__main__':
    if not os.path.exists(ATAC_BAM):
        print('ATAC BAM file not found.')
    else:
        process_atac_seq(ATAC_BAM)

    if not os.path.exists(CHIP_BED):
        print('ChIP BED file not found.')
    else:
        peaks = process_chip_seq(CHIP_BED)
        peaks.saveas('./datasets/ChIP_seq/merged_peaks.bed')
        print('Merged peaks saved.')
