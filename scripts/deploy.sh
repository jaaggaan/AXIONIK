#!/usr/bin/env bash
# FILE: scripts/deploy.sh
# DESCRIPTION: One-command production deployment for AXIONIK backend

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

DEPLOY_TARGET="${1:-render}"   # Usage: ./scripts/deploy.sh [render|docker]

echo -e "${BOLD}"
echo "╔══════════════════════════════════════╗"
echo "║        AXIONIK  DEPLOYMENT           ║"
echo "╚══════════════════════════════════════╝"
echo -e "${RESET}"
info "Target: ${DEPLOY_TARGET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

case "$DEPLOY_TARGET" in

  render)
    info "Deploying to Render.com via Git push..."
    cd "$PROJECT_ROOT"

    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    info "Current branch: $CURRENT_BRANCH"

    git add -A
    git commit -m "chore: deploy $(date '+%Y-%m-%d %H:%M:%S')" || warn "Nothing new to commit"
    git push origin "$CURRENT_BRANCH"

    success "Pushed to $CURRENT_BRANCH — Render will auto-deploy from render.yaml"
    echo ""
    echo -e "  ${BOLD}Monitor at:${RESET} https://dashboard.render.com"
    ;;

  docker)
    info "Building Docker image..."
    cd "$BACKEND_DIR"

    IMAGE_NAME="axionik-api"
    IMAGE_TAG="${2:-latest}"

    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    success "Image built: ${IMAGE_NAME}:${IMAGE_TAG}"

    info "Running container on port 8000..."
    docker run -d \
      --name axionik-api \
      -p 8000:8000 \
      -e FIREBASE_CREDENTIALS_PATH=/app/firebase-key.json \
      "${IMAGE_NAME}:${IMAGE_TAG}"

    success "Container running at http://localhost:8000"
    echo -e "  ${BOLD}Dashboard:${RESET} http://localhost:8000/dashboard-ui"
    echo -e "  ${BOLD}Health:${RESET}    http://localhost:8000/health"
    echo ""
    echo "  To stop:  docker stop axionik-api && docker rm axionik-api"
    ;;

  *)
    error "Unknown target '$DEPLOY_TARGET'. Usage: ./scripts/deploy.sh [render|docker]"
    ;;
esac

echo ""
echo -e "${BOLD}${GREEN}Deployment complete!${RESET}"
