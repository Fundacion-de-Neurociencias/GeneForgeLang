import csv
import sys
import logging
import requests
import time
import os
import argparse
import pandas as pd
import dotenv

# Load AlphaGenome Client (Empirical API, no simulation)
try:
    from alphagenome.models import dna_client
    from alphagenome.models import variant_scorers
    from alphagenome.data import genome
    HAS_ALPHAGENOME = True
except ImportError:
    HAS_ALPHAGENOME = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_alphagenome_score(dna_model, chrom, pos, ref, alt):
    """
    Fetch the empirical regulatory impact quantile score from DeepMind AlphaGenome API.
    """
    if not dna_model:
        return 0.0
        
    try:
        # 1MB sequence length for context
        SEQ_LENGTH = 2**20
        pos = int(pos)
        interval = genome.Interval(chrom, pos - SEQ_LENGTH // 2, pos + SEQ_LENGTH // 2)
        variant = genome.Variant(chrom, pos, ref, alt)
        
        scorers = [
            variant_scorers.RECOMMENDED_VARIANT_SCORERS[m]
            for m in variant_scorers.RECOMMENDED_VARIANT_SCORERS
            if "ACTIVE" not in m and "CAGE" not in m and "PROCAP" not in m
        ]
        
        scores_list = dna_model.score_variant(interval=interval, variant=variant, variant_scorers=scorers)
        
        # Aggregate the maximum absolute quantile score across tissues
        max_quantile = 0.0
        for score_adata in scores_list:
            df = variant_scorers.tidy_scores([score_adata], match_gene_strand=True)
            if df is not None and not df.empty:
                max_q = df['quantile_score'].abs().max()
                if max_q > max_quantile:
                    max_quantile = max_q
                    
        return max_quantile
    except Exception as e:
        logging.error(f"AlphaGenome API Error for {chrom}:{pos}: {e}")
        return 0.0

def fetch_gnomad_af_native(chrom, pos, ref, alt):
    """
    Fetch allele frequency from gnomAD GraphQL API.
    """
    variant_id = f"{chrom.replace('chr', '')}-{pos}-{ref}-{alt}"
    query = """
    query VariantFrequency($variantId: String!, $datasetId: DatasetId!) {
      variant(variantId: $variantId, dataset: $datasetId) {
        genome {
          ac
          an
          af
        }
        exome {
          ac
          an
          af
        }
      }
    }
    """
    variables = {
        "variantId": variant_id,
        "datasetId": "gnomad_r4"
    }
    
    try:
        response = requests.post(
            "https://gnomad.broadinstitute.org/api/",
            json={"query": query, "variables": variables},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json().get("data", {}).get("variant", {})
            if not data:
                return 0.0
                
            # Aggregate genome and exome stats safely
            g = data.get("genome") or {"ac": 0, "an": 0}
            e = data.get("exome") or {"ac": 0, "an": 0}
            
            total_ac = g.get("ac", 0) + e.get("ac", 0)
            total_an = g.get("an", 0) + e.get("an", 0)
            
            if total_an > 0:
                return total_ac / total_an
            return 0.0
        return 0.0
    except Exception as e:
        logging.error(f"gnomAD API Error for {variant_id}: {e}")
        return 0.0

def get_3d_topology_contacts(chrom, pos):
    """
    Query the local FastAPI microservice (which uses Cooler + fsspec on 4D Nucleome).
    """
    url = "http://localhost:8000/api/v1/topology/neighborhood"
    req_data = {
        "source": "Neurodiagnoses_Screening",
        "region": f"{chrom}:{pos}",
        "radius_bins": 5
    }
    
    try:
        res = requests.post(url, json=req_data, timeout=30)
        if res.status_code == 200:
            data = res.json()
            return data.get("neighborhood", [])
        else:
            logging.error(f"Topology API returned {res.status_code}")
            return []
    except Exception as e:
        logging.error(f"Topology API Connection Error: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Batch screening engine (Empirical).")
    parser.add_argument("--input", type=str, default="variants_screening.csv", help="Input CSV with variants")
    parser.add_argument("--output", type=str, default="resultados_screening.csv", help="Output CSV with scores")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logging.error(f"Input file not found: {args.input}")
        sys.exit(1)
        
    # Setup AlphaGenome API
    dna_model = None
    if HAS_ALPHAGENOME:
        dotenv.load_dotenv(os.path.expanduser('~/.env'))
        api_key = os.environ.get('ALPHAGENOME_API_KEY')
        if api_key:
            logging.info("Initializing AlphaGenome DNA Client...")
            dna_model = dna_client.create(api_key=api_key, address='dns:///gdmscience.googleapis.com:443')
        else:
            logging.warning("ALPHAGENOME_API_KEY not found in ~/.env. Skipping epigenetic scoring.")
    else:
        logging.warning("alphagenome module not found. Skipping epigenetic scoring.")
        
    logging.info(f"Reading {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        variants = list(reader)
        
    results = []
    
    for i, var in enumerate(variants):
        gene = var.get("gene", "Unknown")
        chrom = var.get("chr")
        pos = var.get("pos")
        ref = var.get("ref", "").strip() or "N"
        alt = var.get("alt", "").strip() or "N"
        vid = var.get("variant_id", f"{chrom}:{pos}")
        
        logging.info(f"[{i+1}/{len(variants)}] Procesando variante {vid} ({gene})...")
        
        # 1. gnomAD AF
        af = 0.0
        if ref != "N" and alt != "N":
            af = fetch_gnomad_af_native(chrom, pos, ref, alt)
            logging.info(f"  -> gnomAD AF: {af:.6e}")
            
        # 2. 3D Topology
        contacts = get_3d_topology_contacts(chrom, pos)
        num_contacts = len(contacts)
        logging.info(f"  -> Lazos 3D descubiertos (4D Nucleome): {num_contacts}")
        
        # 3. AlphaGenome Epigenetics
        alpha_score = 0.0
        if dna_model and ref != "N" and alt != "N":
            alpha_score = get_alphagenome_score(dna_model, chrom, pos, ref, alt)
            logging.info(f"  -> AlphaGenome Quantile Max: {alpha_score:.4f}")
            
        # 4. Regla del Orquestador (Axis 1)
        weight_tier = "DOCUMENTED"
        if num_contacts > 0 and alpha_score > 0.95:
            weight_tier = "ABSOLUTE_RISK"
        elif num_contacts > 0 or alpha_score > 0.95:
            weight_tier = "HIGH_RISK"
            
        logging.info(f"  => Reclasificación Neurodiagnoses: {weight_tier}")
        
        var["gnomad_af"] = af
        var["3d_contacts"] = num_contacts
        var["alphagenome_quantile"] = round(alpha_score, 4)
        var["neurodiagnoses_tier"] = weight_tier
        results.append(var)
        
        # Rate limiting to avoid bans
        time.sleep(2)
        
    # Guardar resultados
    if results:
        keys = results[0].keys()
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        logging.info(f"Screening finalizado. Resultados empíricos guardados en {args.output}")

if __name__ == "__main__":
    main()
