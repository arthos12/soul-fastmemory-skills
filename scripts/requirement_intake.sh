#!/usr/bin/env bash
set -euo pipefail

# Minimal requirement intake: append a raw requirement into DELIVERY_BACKLOG under a section.
# Usage: scripts/requirement_intake.sh "<text>" [P0|P1|P2]

REQ="${1:?need requirement text}"
SEC="${2:-P2}"
FILE="tasks/DELIVERY_BACKLOG.md"

if [[ ! -f "$FILE" ]]; then
  echo "missing $FILE" >&2
  exit 2
fi

slug=$(echo "$REQ" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g' | cut -c1-48)

line="- [ ] ${slug} - ${REQ}"

# insert into section
python3 - "$line" "$SEC" <<'PY' >/dev/null
import sys
req_line=sys.argv[1]
sec=sys.argv[2]
path='tasks/DELIVERY_BACKLOG.md'
lines=open(path,'r',encoding='utf-8').read().splitlines()
out=[]
inserted=False
for l in lines:
    out.append(l)
    if l.strip().startswith('## '+sec) and not inserted:
        out.append(req_line)
        inserted=True
open(path,'w',encoding='utf-8').write('\n'.join(out)+"\n")
print('OK')
PY

echo "$line"
