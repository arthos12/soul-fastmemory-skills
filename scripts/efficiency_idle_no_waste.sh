#!/usr/bin/env bash
set -euo pipefail

# One-shot self-check for "idle time not wasted".
# Runs requirement pipeline and prints S/A delivery ratio v2.

cd /root/.openclaw/workspace

bash scripts/requirement_pipeline.sh
