#!/bin/bash
################################################################################
# Neuro-Symbolic RAG Setup and Execution Script
################################################################################
# This script sets up the environment and runs the neuro-symbolic RAG engine
# that bridges symbolic GFL hypotheses with unstructured scientific knowledge.
#
# Author: GeneForge Team
# License: MIT
################################################################################

set -e  # Exit on error

echo "=========================================================================="
echo "🧬 GeneForge Neuro-Symbolic RAG - Setup & Execution"
echo "=========================================================================="

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GFL_REPO_PATH="${SCRIPT_DIR}/../.."  # Adjust if needed
VENV_DIR="${SCRIPT_DIR}/venv_rag"
EXAMPLE_HYPOTHESES="${SCRIPT_DIR}/example_hypotheses.gfl"
OUTPUT_FILE="${SCRIPT_DIR}/rag_results.json"

echo ""
echo "📁 Working directory: ${SCRIPT_DIR}"
echo "📁 GFL repository: ${GFL_REPO_PATH}"
echo ""

# Step 1: Create virtual environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Creating Python virtual environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "${VENV_DIR}" ]; then
    echo "✓ Virtual environment already exists: ${VENV_DIR}"
else
    echo "Creating new virtual environment..."
    python3 -m venv "${VENV_DIR}"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate" 2>/dev/null || source "${VENV_DIR}/Scripts/activate"
echo "✓ Virtual environment activated"

# Step 2: Install dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Installing dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Installing core dependencies..."
pip install --upgrade pip >/dev/null 2>&1

# Install required packages
echo "  • Installing ChromaDB (vector database)..."
pip install chromadb >/dev/null 2>&1

echo "  • Installing Biopython (PubMed access)..."
pip install biopython >/dev/null 2>&1

echo "  • Installing PyYAML..."
pip install pyyaml >/dev/null 2>&1

# Install GFL library in editable mode
echo "  • Installing GFL library (official parser)..."
if [ -d "${GFL_REPO_PATH}" ]; then
    pip install -e "${GFL_REPO_PATH}" >/dev/null 2>&1
    echo "✓ GFL library installed from: ${GFL_REPO_PATH}"
else
    echo "⚠ WARNING: GFL repository not found at ${GFL_REPO_PATH}"
    echo "Please adjust GFL_REPO_PATH variable in this script"
    exit 1
fi

echo "✓ All dependencies installed"

# Step 3: Create example hypotheses file
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Creating example GFL hypotheses file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > "${EXAMPLE_HYPOTHESES}" << 'EOF'
# GFL Hypotheses for Neuro-Symbolic RAG Validation
# =================================================
# This file contains formal hypotheses about gene-disease associations
# that will be validated against scientific literature using RAG.

hypothesis:
  id: "H_TP53_LungCancer"
  description: "Test the association between TP53 mutations and Lung Cancer susceptibility."
  if:
    - entity_is:
        gene: "TP53"
    - entity_is:
        disease: "Lung Cancer"
  then:
    - relationship_is: "association"

hypothesis:
  id: "H_MYOD1_MuscleAtrophy"
  description: "Evaluate the role of MYOD1 in Muscle Atrophy pathogenesis."
  if:
    - entity_is:
        gene: "MYOD1"
    - entity_is:
        disease: "Muscle Atrophy"
  then:
    - relationship_is: "association"

hypothesis:
  id: "H_BRCA1_BreastCancer"
  description: "Investigate BRCA1 mutations as a risk factor for Breast Cancer."
  if:
    - entity_is:
        gene: "BRCA1"
    - entity_is:
        disease: "Breast Cancer"
  then:
    - relationship_is: "causal"

hypothesis:
  id: "H_CFTR_CysticFibrosis"
  description: "Analyze the relationship between CFTR gene variants and Cystic Fibrosis."
  if:
    - entity_is:
        gene: "CFTR"
    - entity_is:
        disease: "Cystic Fibrosis"
  then:
    - relationship_is: "causal"
EOF

echo "✓ Example hypotheses file created: ${EXAMPLE_HYPOTHESES}"

# Step 4: Run the RAG engine
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Executing Neuro-Symbolic RAG Engine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python "${SCRIPT_DIR}/neuro_symbolic_rag.py" "${EXAMPLE_HYPOTHESES}" "${OUTPUT_FILE}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ RAG Execution Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Results saved to: ${OUTPUT_FILE}"
echo "📚 Vector database stored in: ${SCRIPT_DIR}/chroma_db"
echo ""
echo "To run again with a different GFL file:"
echo "  source ${VENV_DIR}/bin/activate"
echo "  python neuro_symbolic_rag.py <your_file.gfl> [output.json]"
echo ""
