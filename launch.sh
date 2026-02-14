#!/bin/bash
# ====================================================================================
#  Habit Tracker - Professional Launcher
# ====================================================================================

# Strict mode
set -e

# Cleanup trap
cleanup() {
    echo ""
    echo "[INFO] Shutting down..."
    # Kill background jobs if any
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo " ================================================================"
echo "  Habit Tracker - Automatic Launcher"
echo " ================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check for Python 3.10+
PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "[ERROR] Python 3 not found."
    exit 1
fi

# Verify version
$PYTHON -c "import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)"
if [ $? -ne 0 ]; then
    echo "[ERROR] Python 3.10+ is required."
    exit 1
fi
echo "[OK] Using $($PYTHON --version)"

# 2. Check for .env
if [ -f ".env" ]; then
    echo "[OK] .env file detected."
else
    echo "[INFO] No .env file found. Using default development settings."
fi

# 3. Check Global Dependencies
if $PYTHON -c "import flask" &>/dev/null; then
    echo "[OK] Dependencies found globally. Using global Python."
else
    # 4. Virtual Environment (Fallback)
    echo "[INFO] Dependencies not found globally. Using virtual environment..."
    
    if [ ! -d "venv" ]; then
        echo "[INFO] Creating virtual environment..."
        $PYTHON -m venv venv
    fi

    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate

    # 5. Install Dependencies
    echo "[INFO] Installing/Checking dependencies in venv..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    echo "[OK] Dependencies installed."
fi

# 6. Launch
echo ""
echo "[INFO] Starting Habit Tracker..."
echo "       Press Ctrl+C to stop."
echo ""
python run.py
