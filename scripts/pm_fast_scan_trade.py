#!/usr/bin/env python3
"""Scan -> filter -> paper trade loop (integrated)."""
import json, os, time, subprocess
from datetime import datetime

WORKDIR = "/root/.openclaw/workspace"
DATA_DIR = f"{WORKDIR}/data/polymarket"
STATUS_DIR = f"{DATA_DIR}/runtime"
LOG_FILE = f"{STATUS_DIR}/pm_scan_trade_loop.log"
SCAN_LOG = f"{DATA_DIR}/market_snapshot_latest.jsonl"

# Strategies to run every loop (each strategy may place its own orders)
STRATS = [
    "strategies/tail_confirm_5m_99.json",
    "strategies/tail_confirm_5m_98.json",
    "strategies/tail_confirm_5m_97.json",
    "strategies/tail_confirm_15m_99.json",
    "strategies/tail_confirm_15m_98.json",
    "strategies/tail_confirm_15m_97.json",
    # test data: 0.55/0.45
    "strategies/test_tail_5m_55.json",
    "strategies/test_tail_15m_55.json",
    # plan A non-tail strategies
    "strategies/br_v2_highprob.json",
    "strategies/br_v3_short.json",
    "strategies/test1_br_copy.json",
]

INTERVAL = int(os.environ.get("PM_LOOP_INTERVAL", "60"))
SCAN_PAGES = int(os.environ.get("PM_SCAN_PAGES", "120"))
CACHE_AGE = int(os.environ.get("PM_CACHE_AGE", "60"))

os.makedirs(STATUS_DIR, exist_ok=True)


def log(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat()}Z] {msg}\n")


def run_once(strategy_path: str):
    """
    One loop = scan + filter + paper orders for a single strategy.
    Writes:
      - status json: data/polymarket/runtime/<strategy>_status.json (overwrite)
      - scan snapshot: once per strategy (first capture only)
      - logs: only on orders/results OR minute summary
    """
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
        "--use-events",
    ]
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
        snap = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "strategy": base,
            "scan_pages": SCAN_PAGES,
            "orders": orders,
            "results": results,
            "selection_reasons": sel,
        }
        # market snapshot: write ONCE per strategy
        once_path = f"{STATUS_DIR}/{base}_snapshot_once.json"
        if not os.path.exists(once_path):
            with open(SCAN_LOG, "a", encoding="utf-8") as sf:
                sf.write(json.dumps(snap, ensure_ascii=False) + "\n")
            with open(once_path, "w", encoding="utf-8") as tf:
                json.dump({"ts": int(time.time())}, tf)

        # log ONLY when orders/results > 0
        if orders > 0 or results > 0:
            top = sorted(sel.items(), key=lambda kv: -kv[1])[:3]
            reasons = " ".join([f"{k}:{v}" for k, v in top])
            log(f"HIT strategy={base} orders={orders} results={results} reasons={reasons}")

        # accumulate minute summary
        summary_path = f"{STATUS_DIR}/minute_summary.json"
        summary = {"ts": int(time.time()//60*60)}
        if os.path.exists(summary_path):
            try: summary.update(json.load(open(summary_path)))
            except Exception: pass
        s = summary.setdefault(base, {})
        for k,v in sel.items():
            s[k] = s.get(k,0) + int(v)
        summary["ts"] = int(time.time()//60*60)
        with open(summary_path, "w", encoding="utf-8") as sf:
            json.dump(summary, sf, ensure_ascii=False, indent=2)
    except Exception:
        log(f"OK strategy={base} (parse_failed)")


if __name__ == "__main__":
    log(f"START interval={INTERVAL}s scan_pages={SCAN_PAGES} cache_age={CACHE_AGE}")
    while True:
        # guard: pause loop if system protection is active
        try:
            subprocess.run(["bash", f"{WORKDIR}/scripts/system_protection_guard.sh"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        if os.path.exists(f"{WORKDIR}/data/system_guard/guard.flag"):
            # no per-iteration log spam
            time.sleep(INTERVAL)
            continue

        # Each strategy runs independently; no global de-dup.
        for strat in STRATS:
            run_once(strat)
            time.sleep(1)

        time.sleep(INTERVAL)
