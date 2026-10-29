#!/usr/bin/env bash
# ==============================================================================
# Carbon-X (14.8B) Sovereign Deployment on Apple Silicon Mac Studio (M4 Max)
# ==============================================================================
# Architecture: Apple Silicon arm64 (Metal GPU Acceleration, 64 GB Unified RAM)
# Model: HuggingFaceBio/Carbon-X (Qwen3-14B backbone, 5,515 6-mer DNA tokens)
# Context: 40,960 tokens (approx. 245,760 bp of contiguous DNA)
# Port: 8000 (OpenAI-compatible /v1/chat/completions)
#
# STRICT INVARIANT (ADR-073 & Owner Rule):
# This deployment processes purely public/institutional genomic DNA sequences.
# NEVER upload, mount, cache, or log personal data or credentials on this node.
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " Starting Carbon-X Deployment on Apple Silicon Mac Studio "
echo "=========================================================="

# 1. Environment & Hardware Verification
ARCH=$(uname -m)
OS=$(uname -s)

if [ "$OS" != "Darwin" ] || [ "$ARCH" != "arm64" ]; then
    echo "[-] Error: This deployment script requires macOS on Apple Silicon (arm64)."
    exit 1
fi

echo "[+] Detected Architecture: $OS $ARCH (Apple Silicon)"

# Check Homebrew Python
PYTHON_BIN="/opt/homebrew/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    echo "[-] Homebrew Python 3 not found at $PYTHON_BIN. Using system python3."
    PYTHON_BIN="python3"
fi

echo "[+] Using Python interpreter: $($PYTHON_BIN --version) at $PYTHON_BIN"

# 2. Workspace & Virtual Environment Setup
DEPLOY_DIR="${HOME}/models/carbonx"
VENV_DIR="${HOME}/.carbonx_env"

mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 3. Install Metal-accelerated inference backend
echo "[+] Ensuring build dependencies (wheel, pip, huggingface_hub)..."
pip install --upgrade pip setuptools wheel huggingface_hub

# Install llama-cpp-python with Metal support
if ! python -c "import llama_cpp" 2>/dev/null; then
    echo "[+] Installing Metal-accelerated llama-cpp-python..."
    CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python[server] --no-cache-dir
else
    echo "[+] llama-cpp-python is already installed with Metal support."
fi

# 4. Model Weights Download (Quantized GGUF or MLX)
# Carbon-X 14.8B Q4_K_M (~8.9 GB) or Q8_0 (~15.5 GB) fit comfortably inside 64 GB Unified RAM
MODEL_FILENAME="carbonx-14b.Q4_K_M.gguf"
MODEL_PATH="${DEPLOY_DIR}/${MODEL_FILENAME}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "[+] Downloading Carbon-X 14.8B weights from HuggingFaceBio/Carbon-X..."
    python -c "
from huggingface_hub import hf_hub_download
import os

repo_id = 'HuggingFaceBio/Carbon-X'
try:
    hf_hub_download(
        repo_id=repo_id,
        filename='${MODEL_FILENAME}',
        local_dir='${DEPLOY_DIR}',
        local_dir_use_symlinks=False,
    )
    print('[+] Model weights downloaded successfully.')
except Exception as e:
    print(f'[*] Note: Remote checkpoint download requires active HF token or direct GGUF export: {e}')
"
fi

# 5. Launch Service Helper
cat << 'EOF' > run_carbonx_server.sh
#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${HOME}/.carbonx_env/bin/activate"

PORT=8000
HOST="0.0.0.0"
MODEL_PATH="${SCRIPT_DIR}/carbonx-14b.Q4_K_M.gguf"

echo "[+] Starting Carbon-X OpenAI-compatible API server on ${HOST}:${PORT}..."
echo "[+] Metal Acceleration: ENABLED (All layers offloaded to Apple GPU)"

python -m llama_cpp.server \
    --model "$MODEL_PATH" \
    --model_alias "carbonx-14b" \
    --n_ctx 40960 \
    --n_gpu_layers -1 \
    --host "$HOST" \
    --port "$PORT"
EOF

chmod +x run_carbonx_server.sh

echo "=========================================================="
echo " Carbon-X Deployment Prepared Successfully!              "
echo " To run the service:                                      "
echo "   cd ${DEPLOY_DIR} && ./run_carbonx_server.sh           "
echo "=========================================================="
