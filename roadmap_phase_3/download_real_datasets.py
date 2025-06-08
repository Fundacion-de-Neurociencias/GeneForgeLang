import os
import requests

ATAC_DIR = './roadmap_phase_3/datasets/ATAC_seq'
CHIP_DIR = './roadmap_phase_3/datasets/ChIP_seq'

os.makedirs(ATAC_DIR, exist_ok=True)
os.makedirs(CHIP_DIR, exist_ok=True)

def download_file(url, folder):
    local_filename = os.path.join(folder, url.split('/')[-1].split('?')[0])
    print(f"Downloading {url} to {local_filename}")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except requests.HTTPError as e:
        print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    atac_url = 'https://www.encodeproject.org/files/ENCFF000ATG/@@download/ENCFF000ATG.bam'
    chip_url = 'https://www.encodeproject.org/files/ENCFF001UJU/@@download/ENCFF001UJU.bed.gz'

    download_file(atac_url, ATAC_DIR)
    download_file(chip_url, CHIP_DIR)
