#!/usr/bin/env bash
# FILE: scripts/setup.sh
# DESCRIPTION: One-command local development environment setup for AXIONIK

set -euo pipefail

RESET="\033[0m"
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

echo -e "${BOLD}"
echo "╔══════════════════════════════════════╗"
echo "║        AXIONIK  LOCAL  SETUP         ║"
echo "╚══════════════════════════════════════╝"
echo -e "${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ============================================================
# BACKEND SETUP
# ============================================================
info "Setting up backend (Python FastAPI)..."

BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  success "Virtual environment created at backend/.venv"
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
success "Python dependencies installed"

if [ ! -f "firebase-key.json" ]; then
  if [ -f "firebase-key.json.example" ]; then
    cp firebase-key.json.example firebase-key.json
    warn "Copied firebase-key.json.example → firebase-key.json. Fill in real credentials!"
  else
    warn "firebase-key.json missing. Backend will run in memory-only fallback mode."
  fi
fi

deactivate

# ============================================================
# FRONTEND SETUP
# ============================================================
info "Setting up frontend (Flutter)..."

FRONTEND_DIR="$PROJECT_ROOT/frontend"
cd "$FRONTEND_DIR"

if command -v flutter &>/dev/null; then
  flutter pub get
  success "Flutter packages installed"
else
  warn "Flutter not found in PATH. Install Flutter SDK and re-run this script."
fi

# ============================================================
# DONE
# ============================================================
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${GREEN}║          SETUP COMPLETE!             ║${RESET}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}Backend:${RESET}  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo -e "  ${BOLD}Frontend:${RESET} cd frontend && flutter run"
echo -e "  ${BOLD}Dashboard:${RESET} http://localhost:8000/dashboard-ui"
echo ""
