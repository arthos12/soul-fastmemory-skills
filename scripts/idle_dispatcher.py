#!/usr/bin/env python3
"""Idle dispatcher (queue-driven + bounded concurrency).

- Reads tasks/IDLE_QUEUE.json
- Runs enabled lanes with maxParallel (default 2)
- Appends evidence to data/brain_evolution/idle_cycle_reports.log

Design goals:
- Higher throughput without relying on live conversation
- Bounded concurrency to avoid rate-limit / API storms
- Evidence-first logging
"""

import json, os, subprocess, time, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_PATH = os.path.join(ROOT, "tasks", "IDLE_QUEUE.json")
LOG_DIR = os.path.join(ROOT, "data", "brain_evolution")
LOG_PATH = os.path.join(LOG_DIR, "idle_cycle_reports.log")


def now_utc():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run_one(lane):
    start = time.time()
    cmd = lane["command"]
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out, _ = p.communicate(timeout=110)
    end = time.time()
    tail = "\n".join(out.strip().splitlines()[-20:])
    return {
        "ts": now_utc(),
        "lane": lane.get("id"),
        "desc": lane.get("desc"),
        "cmd": cmd,
        "exitCode": p.returncode,
        "secs": round(end - start, 3),
        "outputTail": tail,
    }


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        q = json.load(f)

    max_parallel = int(q.get("maxParallel", 2))
    cycles = int(q.get("cyclesPerWake", 2))
    max_secs = float(q.get("maxSecsPerWake", 0))
    lanes = [l for l in q.get("lanes", []) if l.get("enabled")]

    if not lanes:
        return

    # If REQUIREMENTS_FOCUS.json exists, only run lanes listed in allowedLanes.
    focus_path = os.path.join(ROOT, 'tasks', 'REQUIREMENTS_FOCUS.json')
    if os.path.exists(focus_path):
        try:
            with open(focus_path, 'r', encoding='utf-8') as ff:
                focus = json.load(ff)
            allowed = set(focus.get('allowedLanes', []))
            if allowed:
                lanes = [l for l in lanes if l.get('id') in allowed]
        except Exception:
            pass

    # Delivery-first: if backlog has unchecked items, prioritize P0 delivery lane and skip others
    priority_mode = q.get("priorityMode", "")
    backlog_path = os.path.join(ROOT, "tasks", "DELIVERY_BACKLOG.md")
    backlog_pending = False
    if priority_mode == "delivery_first" and os.path.exists(backlog_path):
        try:
            with open(backlog_path, 'r', encoding='utf-8') as bf:
                for ln in bf:
                    if ln.startswith('- [ ] '):
                        backlog_pending = True
                        break
        except Exception:
            backlog_pending = False

    # backlog counts (for self-check)
    backlog_pending_count = 0
    backlog_mvc_count = 0
    backlog_done_count = 0
    if os.path.exists(backlog_path):
        try:
            with open(backlog_path, 'r', encoding='utf-8') as bf:
                for ln in bf:
                    if ln.startswith('- [ ] '):
                        backlog_pending_count += 1
                    elif ln.startswith('- [m] '):
                        backlog_mvc_count += 1
                    elif ln.startswith('- [x] '):
                        backlog_done_count += 1
        except Exception:
            pass

    if backlog_pending:
        lanes = [l for l in lanes if l.get('id') == 'P0_brain']

    all_results = []

    start_all = time.time()
    for _ in range(max(1, cycles)):
        # stop early if we hit time budget
        if max_secs and (time.time() - start_all) >= max_secs:
            break
        # bounded concurrency (simple batch): run up to max_parallel, then next
        results = []
        i = 0
        while i < len(lanes):
            batch = lanes[i:i+max_parallel]
            procs = []
            for lane in batch:
                cmd = lane["command"]
                start = time.time()
                p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                procs.append((lane, p, start))
            for lane, p, start in procs:
                try:
                    out, _ = p.communicate(timeout=110)
                except subprocess.TimeoutExpired:
                    p.kill()
                    out = "TIMEOUT"
                end = time.time()
                tail = "\n".join(str(out).strip().splitlines()[-20:])
                results.append({
                    "ts": now_utc(),
                    "lane": lane.get("id"),
                    "desc": lane.get("desc"),
                    "cmd": lane.get("command"),
                    "exitCode": getattr(p, "returncode", None),
                    "secs": round(end - start, 3),
                    "outputTail": tail,
                })
            i += max_parallel

        all_results.extend(results)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("===== " + now_utc() + " =====\n")
        f.write(json.dumps({"queue": os.path.relpath(QUEUE_PATH, ROOT), "maxParallel": max_parallel, "cyclesPerWake": cycles, "lanes": [l.get('id') for l in lanes]}, ensure_ascii=False) + "\n")
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.write("\n")

    # Efficiency metrics (evidence for throughput)
    ok = sum(1 for r in all_results if r.get('exitCode') == 0)
    fail = sum(1 for r in all_results if r.get('exitCode') not in (0, None))
    total_secs = round(sum(float(r.get('secs') or 0) for r in all_results), 3)

    # Effective output proxy (upgraded): count meaningful outputs in last 2 minutes
    def sh(cmd):
        return subprocess.check_output(["bash", "-lc", cmd], cwd=ROOT, text=True)

    # all recent files
    recent_files = [p.strip().lstrip('./') for p in sh("find . -path './.git' -prune -o -type f -mmin -2 -print").splitlines() if p.strip()]

    # mvc created proxy: new mvc_tests in last 10 minutes (create time is hard; use mtime)
    mvc_created = len([p for p in sh("find docs/mvc_tests -type f -mmin -10 -name '*.md' -print 2>/dev/null || true").splitlines() if p.strip()])

    # scripts changed proxy
    scripts_changed = len([p for p in sh("find scripts -type f -mmin -10 -print 2>/dev/null || true").splitlines() if p.strip()])

    # prediction lines proxy: total lines of predictions modified in last 10 minutes
    pred_files = [p.strip() for p in sh("find data/polymarket -type f -mmin -10 -name 'predictions_*' -print 2>/dev/null || true").splitlines() if p.strip()]
    pred_lines = 0
    for pf in pred_files:
        try:
            pred_lines += int(sh(f"wc -l < '{pf}'").strip() or "0")
        except Exception:
            pass

    metric = {
        "ts": now_utc(),
        "lanes": [l.get('id') for l in lanes],
        "maxParallel": max_parallel,
        "cyclesPerWake": cycles,
        "ok": ok,
        "fail": fail,
        "totalSecs": total_secs,
        "recentFiles2m": len(recent_files),
        "mvcCreated10m": mvc_created,
        "scriptsChanged10m": scripts_changed,
        "predictionLines10m": pred_lines,
        "backlogPending": backlog_pending_count,
        "backlogMVC": backlog_mvc_count,
        "backlogDone": backlog_done_count,
    }

    # add deltas vs previous record (true progress signal)
    try:
        mdir = os.path.join(ROOT, 'data', 'efficiency')
        mpath = os.path.join(mdir, 'metrics.jsonl')
        prev = None
        if os.path.exists(mpath):
            with open(mpath, 'r', encoding='utf-8') as pf:
                for ln in pf:
                    if ln.strip():
                        prev = ln
        if prev:
            pr = json.loads(prev)
            metric['deltaBacklogDone'] = metric['backlogDone'] - int(pr.get('backlogDone', 0))
            metric['deltaBacklogMVC'] = metric['backlogMVC'] - int(pr.get('backlogMVC', 0))
            metric['deltaBacklogPending'] = metric['backlogPending'] - int(pr.get('backlogPending', 0))
            # conversion signal: done / (done+mvc)
            denom = max(1, metric['backlogDone'] + metric['backlogMVC'])
            metric['mvcToDoneRatio'] = round(metric['backlogDone'] / denom, 4)
    except Exception:
        pass
    mdir = os.path.join(ROOT, 'data', 'efficiency')
    os.makedirs(mdir, exist_ok=True)
    mpath = os.path.join(mdir, 'metrics.jsonl')
    with open(mpath, 'a', encoding='utf-8') as mf:
        mf.write(json.dumps(metric, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
