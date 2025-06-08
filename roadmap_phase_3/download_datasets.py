import os
import requests

DATA_DIR = './roadmap_phase_3/datasets'
ATAC_DIR = os.path.join(DATA_DIR, 'ATAC_seq')
CHIP_DIR = os.path.join(DATA_DIR, 'ChIP_seq')

os.makedirs(ATAC_DIR, exist_ok=True)
os.makedirs(CHIP_DIR, exist_ok=True)

# URLs ejemplo de datasets públicos (debes ajustar con links reales)
atac_urls = [
    'https://example.org/dataset/atac_sample1.bam',
    'https://example.org/dataset/atac_sample2.bam',
]

chip_urls = [
    'https://example.org/dataset/chip_sample1.bam',
    'https://example.org/dataset/chip_sample2.bam',
]

def download_file(url, dest_folder):
    local_filename = os.path.join(dest_folder, url.split('/')[-1])
    if not os.path.exists(local_filename):
        print(f'Downloading {url} to {local_filename}')
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    else:
        print(f'File {local_filename} already exists, skipping.')
    return local_filename

for url in atac_urls:
    download_file(url, ATAC_DIR)

for url in chip_urls:
    download_file(url, CHIP_DIR)

print('Datasets download completed.')
