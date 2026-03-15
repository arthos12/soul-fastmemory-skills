#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
python3 scripts/check_core_brain_library_boundaries.py
