#!/usr/bin/env python3
"""Generate a prediction batch JSONL from a markets JSONL source.

This is intentionally a *minimal* v0: it creates a structured record with a placeholder
prediction using base-rate + time-window heuristics.

Goal: enforce the output format so we can iterate (improve model) without losing structure.

Usage:
  python3 scripts/polymarket_predict.py \
    --in data/polymarket/markets_batch2_source.jsonl \
    --out data/polymarket/predictions_YYYY-MM-DD_batch2.jsonl \
    --limit 12
"""

import argparse, datetime, json, os, math


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def base_rate_two_outcome(question: str):
    q = (question or "").lower()

    # legal / court outcomes
    if any(k in q for k in ["convicted", "sentenced", "indicted", "guilty"]):
        return 0.25

    # geopolitical tail events
    if any(k in q for k in ["invade", "war", "attack", "return before gta vi"]):
        return 0.05

    # celebrity / product / album / release timing events
    if any(k in q for k in ["album", "launch", "released", "release", "before gta vi"]):
        return 0.2

    # extreme crypto price targets in short windows
    if "bitcoin" in q and "$1m" in q:
        return 0.03

    # price threshold questions are not all 50/50; keep only generic price cases mild-neutral
    if any(k in q for k in ["above", "below", "hit", "price"]):
        return 0.35

    # sports championship outrights are long-tail by construction
    if any(k in q for k in ["stanley cup", "world cup", "championship", "qualify"]):
        return 0.12

    # religion / miracle style claims should be extremely low unless strong evidence exists
    if any(k in q for k in ["jesus christ return", "second coming"]):
        return 0.001

    return 0.2


def adjust_time_window(p, end_date: str):
    # Shorter window should make rare events rarer, not drag everything toward 0.5.
    try:
        end = datetime.datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        now = datetime.datetime.utcnow().replace(tzinfo=end.tzinfo)
        days = max((end - now).days, 0)
        if days < 30:
            return clamp(p * 0.4)
        if days < 60:
            return clamp(p * 0.6)
        if days < 120:
            return clamp(p * 0.8)
        if days < 240:
            return clamp(p * 0.9)
    except Exception:
        pass
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.outp), exist_ok=True)

    created = datetime.datetime.utcnow().isoformat() + "Z"
    n = 0
    with open(args.inp, "r", encoding="utf-8") as f_in, open(args.outp, "w", encoding="utf-8") as f_out:
        for line in f_in:
            if n >= args.limit:
                break
            line = line.strip()
            if not line:
                continue
            m = json.loads(line)
            outcomes = m.get("outcomes") or []
            prices = m.get("outcomePrices") or []
            # only handle simple yes/no
            if outcomes != ["Yes", "No"] or len(prices) < 1:
                continue
            p_mkt = float(prices[0])

            p0 = base_rate_two_outcome(m.get("question"))
            p = adjust_time_window(p0, m.get("endDate") or "")

            # Edge guard: if our prior is massively far from market on sparse-template questions,
            # shrink toward market instead of pretending certainty.
            if abs(p - p_mkt) > 0.25:
                p = 0.65 * p + 0.35 * p_mkt

            p = clamp(p)

            q = (m.get("question") or "").lower()

            # Minimal, templated triggers/invalidation (v1) to remove placeholders
            trigger = []
            invalidation = []
            if any(k in q for k in ["convicted", "sentenced", "indicted", "guilty"]):
                trigger = ["credible court update: indictment/plea/trial date/conviction report"]
                invalidation = ["charges dropped OR case stalled beyond meaningful window"]
            elif any(k in q for k in ["released", "launch", "album"]):
                trigger = ["official announcement: release date + preorder/presave"]
                invalidation = ["no official release signals by mid-window OR delay announcement"]
            elif any(k in q for k in ["ceasefire", "peace", "truce"]):
                trigger = ["signed ceasefire framework + verification/enforcement mechanism"]
                invalidation = ["renewed escalation OR negotiations collapse"]
            elif any(k in q for k in ["bitcoin", "eth", "sol", "xrp", "price", "above", "below", "$", "hit"]):
                trigger = ["price momentum + sustained inflows consistent with target within window"]
                invalidation = ["macro tightening / weak inflows / time window shrinking"]
            elif any(k in q for k in ["invade", "war", "attack"]):
                trigger = ["mobilization + logistics indicators + sustained escalation beyond exercises"]
                invalidation = ["de-escalation signals / diplomacy restart / posture reduction"]
            else:
                trigger = ["new credible evidence that shifts base rate"]
                invalidation = ["evidence contradicts thesis OR no progress as time elapses"]

            rec = {
                "createdAt": created,
                "marketId": m.get("id"),
                "question": m.get("question"),
                "endDate": m.get("endDate"),
                "p_yes_me": round(p, 4),
                "p_yes_mkt": round(p_mkt, 4),
                "modelsUsed": ["base_rate", "time_window", "trigger_template_v1"],
                "trigger": trigger,
                "invalidation": invalidation,
                "url": m.get("url"),
            }
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1

    print(args.outp)


if __name__ == "__main__":
    main()
