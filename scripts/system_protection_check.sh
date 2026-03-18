#!/usr/bin/env bash
set -euo pipefail
OUTDIR="data/system_guard"
mkdir -p "$OUTDIR"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MEM=$(free -m | awk 'NR==2{printf "{\"total_mb\":%s,\"used_mb\":%s,\"free_mb\":%s,\"available_mb\":%s}",$2,$3,$4,$7}')
SWAP=$(free -m | awk 'NR==3{printf "{\"total_mb\":%s,\"used_mb\":%s,\"free_mb\":%s}",$2,$3,$4}')
LOAD=$(cat /proc/loadavg | awk '{printf "{\"load1\":%s,\"load5\":%s,\"load15\":%s}",$1,$2,$3}')
TOP=$(ps -eo pid=,pcpu=,pmem=,rss=,comm= --no-headers --sort=-rss | head -n 5 | awk 'BEGIN{print "["} {pid=$1; cpu=$2; mem=$3; rss=$4; $1=$2=$3=$4=""; sub(/^ +/ ,"",$0); cmd=$0; printf "%s{\"pid\":%s,\"cmd\":\"%s\",\"cpu\":%s,\"mem\":%s,\"rss_kb\":%s}",(NR==1?"":" ,"),pid,cmd,cpu,mem,rss} END{print "]"}')
JSON="{\"ts\":\"$TS\",\"mem\":$MEM,\"swap\":$SWAP,\"load\":$LOAD,\"top\":$TOP}"
echo "$JSON" > "$OUTDIR/last.json"
echo "$JSON" >> "$OUTDIR/history.jsonl"
