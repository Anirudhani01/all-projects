#!/usr/bin/env bash
set -euo pipefail
if [ -f ".venv/bin/activate" ]; then source .venv/bin/activate; fi
export $(grep -v '^#' .env 2>/dev/null | xargs -I {} echo {}) >/dev/null 2>&1 || true
uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-8000}
