#!/usr/bin/env bash
set -euo pipefail

# Deliver next backlog item as an MVC skeleton (model card + script + test).
# Marks the backlog checkbox as done.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKLOG="tasks/DELIVERY_BACKLOG.md"

# find first unchecked item
line=$(grep -nE '^\- \[ \] ' "$BACKLOG" | head -n 1 || true)
if [[ -z "$line" ]]; then
  echo "NO_PENDING"
  exit 0
fi

lnum=${line%%:*}
item=${line#*] }
slug=$(echo "$item" | awk '{print $1}')
# sanitize slug
slug=$(echo "$slug" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_\-]+/_/g; s/^_+|_+$//g')

# use mvc creator
bash scripts/mvc_create.sh Lx "$slug" >/dev/null

# mark as done (replace checkbox and append done_at once)
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
tmp=$(mktemp)
awk -v n="$lnum" -v now="$now" 'NR==n{sub("\\[ \\\]","[m]"); print $0 "  # mvc_at=" now; next} {print}' "$BACKLOG" > "$tmp"
cat "$tmp" > "$BACKLOG"
rm -f "$tmp"

echo "DONE_MVC $slug"
