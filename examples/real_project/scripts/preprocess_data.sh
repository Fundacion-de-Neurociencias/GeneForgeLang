#!/bin/bash
set -e
DATA_DIR="databases"
GENOME_FASTA="GRCh38.primary_assembly.genome.fa"
BLAST_DB_NAME="GRCh38_blast_db"

echo "--- Iniciando el preprocesamiento de datos para GFL Genesis ---"

# Verificar que el genoma existe
if [ ! -f "$DATA_DIR/$GENOME_FASTA" ]; then
    echo "Error: No se encontró el fichero del genoma $DATA_DIR/$GENOME_FASTA"
    echo "Por favor, ejecute primero el script fetch_data.sh"
    exit 1
fi

# Crear base de datos BLAST
echo "-> Creando base de datos BLAST a partir del genoma..."
makeblastdb -in "$DATA_DIR/$GENOME_FASTA" -dbtype nucl -out "$DATA_DIR/$BLAST_DB_NAME" -title "GRCh38_BLAST_DB"

echo "✅ Base de datos BLAST creada en $DATA_DIR/$BLAST_DB_NAME"
