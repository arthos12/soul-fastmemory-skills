#!/usr/bin/env python3
"""Self-check for Polymarket data pipeline."""
import requests, json

GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
CLOB_BOOK = "https://clob.polymarket.com/book"


def main():
    print("[A] events fetch")
    r = requests.get(GAMMA_EVENTS, params={"active":"true","closed":"false","limit":5}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        events = data.get("events") or data.get("results") or data.get("data") or []
    else:
        events = data
    print("events_len", len(events))
    if not events:
        print("FAIL: no events")
        return

    ev = events[0]
    markets = ev.get("markets") or []
    print("[B] first event markets", len(markets))
    if not markets:
        print("FAIL: no markets in first event")
        return

    mk = markets[0]
    clob = mk.get("clobTokenIds")
    if isinstance(clob, str):
        try:
            clob = json.loads(clob)
        except Exception:
            clob = None
    print("clobTokenIds", clob)
    if not clob:
        print("FAIL: no clobTokenIds")
        return

    tid = clob[0]
    print("[C] clob book", tid)
    book = requests.get(CLOB_BOOK, params={"token_id": tid}, timeout=20).json()
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    print("best_bid", bids[0]['price'] if bids else None, "best_ask", asks[0]['price'] if asks else None)

    print("[OK] pipeline reachable")


if __name__ == "__main__":
    main()
