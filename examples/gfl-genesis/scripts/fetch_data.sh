#!/bin/bash
set -e
DATA_DIR="databases"
GENOME_FASTA="GRCh38.primary_assembly.genome.fa"
ANNOTATION_GTF="gencode.v44.primary_assembly.annotation.gtf"

echo "--- Iniciando la descarga de datos para GFL Genesis ---"
mkdir -p $DATA_DIR

# Descargar Genoma (ejemplo con un enlace de GENCODE)
if [ ! -f "$DATA_DIR/$GENOME_FASTA" ]; then
    echo "-> Descargando genoma GRCh38..."
    wget -q -O "$DATA_DIR/${GENOME_FASTA}.gz" "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz"
    gunzip "$DATA_DIR/${GENOME_FASTA}.gz"
else
    echo "-> El fichero del genoma ya existe."
fi

# Descargar Anotaciones (ejemplo con un enlace de GENCODE)
if [ ! -f "$DATA_DIR/$ANNOTATION_GTF" ]; then
    echo "-> Descargando anotaciones GENCODE..."
    wget -q -O "$DATA_DIR/${ANNOTATION_GTF}.gz" "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz"
    gunzip "$DATA_DIR/${ANNOTATION_GTF}.gz"
else
    echo "-> El fichero de anotaciones ya existe."
fi

echo "✅ Datos descargados y listos en $DATA_DIR/"