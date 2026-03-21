#!/usr/bin/env bash
set -euo pipefail
OUTDIR="data/system_guard"
mkdir -p "$OUTDIR"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# snapshot
scripts/system_protection_check.sh >/dev/null 2>&1 || true

# metrics
read -r total used free shared buff available < <(free -m | awk 'NR==2{print $2,$3,$4,$5,$6,$7}')
read -r swap_total swap_used swap_free < <(free -m | awk 'NR==3{print $2,$3,$4}')
read -r load1 load5 load15 rest < /proc/loadavg
nproc=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)

avail_mb=${available:-0}
swap_used_mb=${swap_used:-0}
load1_val=${load1:-0}

# thresholds (relaxed for 2G box)
mem_crit=$((avail_mb < 200))
swap_crit=$((swap_used_mb > 1024))
# compare load1 > 2*nproc using awk
load_crit=$(awk -v l="$load1_val" -v n="$nproc" 'BEGIN{print (l > (2*n))?1:0}')

if [[ $mem_crit -eq 1 || $swap_crit -eq 1 || $load_crit -eq 1 ]]; then
  alert=$(printf '{"ts":"%s","available_mb":%s,"swap_used_mb":%s,"load1":%s,"nproc":%s,"mem_crit":%s,"swap_crit":%s,"load_crit":%s}' "$TS" "$avail_mb" "$swap_used_mb" "$load1_val" "$nproc" "$mem_crit" "$swap_crit" "$load_crit")
  echo "$alert" >> "$OUTDIR/alerts.jsonl"
  echo "$alert" > "$OUTDIR/guard.flag"
fi

# recovery check: clear guard.flag if recovered
if [[ -f "$OUTDIR/guard.flag" ]]; then
  mem_ok=$((avail_mb >= 400))
  swap_ok=$((swap_used_mb <= 512))
  load_ok=$(awk -v l="$load1_val" -v n="$nproc" 'BEGIN{print (l <= (1.2*n))?1:0}')
  if [[ $mem_ok -eq 1 && $swap_ok -eq 1 && $load_ok -eq 1 ]]; then
    rm -f "$OUTDIR/guard.flag"
  fi
fi
