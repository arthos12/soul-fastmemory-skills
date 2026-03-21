#!/usr/bin/env python3
"""Scan -> filter -> paper trade loop (integrated)."""
import json, os, time, subprocess
from datetime import datetime

WORKDIR = "/root/.openclaw/workspace"
STATUS_DIR = f"{WORKDIR}/data/polymarket/runtime"
LOG_FILE = f"{STATUS_DIR}/pm_scan_trade_loop.log"

STRATS = [
    "strategies/br_tail_v1.json",
    "strategies/test1_br_copy.json",
    "strategies/test2_follow_br.json",
    "strategies/test3_combined.json",
]

INTERVAL = int(os.environ.get("PM_LOOP_INTERVAL", "60"))
SCAN_PAGES = int(os.environ.get("PM_SCAN_PAGES", "120"))
CACHE_AGE = int(os.environ.get("PM_CACHE_AGE", "60"))

os.makedirs(STATUS_DIR, exist_ok=True)


def log(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat()}Z] {msg}\n")


def run_once(strategy_path: str):
    base = os.path.basename(strategy_path).replace(".json", "")
    tag = f"{base}_{datetime.utcnow().strftime('%H%M%S')}"
    cmd = [
        "python3",
        f"{WORKDIR}/scripts/pm_paper_loop.py",
        "--strategy",
        strategy_path,
        "--tag",
        tag,
        "--scan-pages",
        str(SCAN_PAGES),
        "--cache-age-sec",
        str(CACHE_AGE),
    ]
    log(f"RUN strategy={base} interval={INTERVAL}s")
    try:
        out = subprocess.check_output(cmd, cwd=WORKDIR, timeout=120).decode("utf-8", errors="ignore")
    except Exception as e:
        log(f"ERROR strategy={base} err={e}")
        return
    status_path = f"{STATUS_DIR}/{base}_status.json"
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(out)
    try:
        j = json.loads(out)
        orders = j.get("orders_generated", 0)
        results = j.get("results_backfilled", 0)
        sel = j.get("selection_reasons", {}) or {}
        top = sorted(sel.items(), key=lambda kv: -kv[1])[:3]
        reasons = " ".join([f"{k}:{v}" for k, v in top])
        log(f"OK strategy={base} orders={orders} results={results} reasons={reasons}")
    except Exception:
        log(f"OK strategy={base} (parse_failed)")


if __name__ == "__main__":
    log(f"START interval={INTERVAL}s scan_pages={SCAN_PAGES} cache_age={CACHE_AGE}")
    while True:
        # guard
        try:
            subprocess.run(["bash", f"{WORKDIR}/scripts/system_protection_guard.sh"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        if os.path.exists(f"{WORKDIR}/data/system_guard/guard.flag"):
            log("PAUSED guard")
            time.sleep(INTERVAL)
            continue

        for strat in STRATS:
            run_once(strat)
            time.sleep(1)

        time.sleep(INTERVAL)
