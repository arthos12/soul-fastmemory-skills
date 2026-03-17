import json, os, time, requests
import datetime as dt

GAMMA = "https://gamma-api.polymarket.com/markets"
UA = {"User-Agent": "openclaw/pm-test"}

def fetch_5min_btc_markets():
    params = {"limit": 10, "active": "true", "closed": "false", "query": "Bitcoin Price"}
    r = requests.get(GAMMA, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    # Filter for markets with Yes/No and prices
    valid = []
    for m in r.json():
        outcomes = m.get("outcomes")
        prices = m.get("outcomePrices")
        if outcomes and prices and len(outcomes) == 2:
            valid.append(m)
    return valid

def run_dual_side_test():
    print("Starting Dual-Side Verification Test...")
    markets = fetch_5min_btc_markets()
    if not markets:
        print("No suitable 5min BTC markets found.")
        return

    m = markets[0]
    mid = m['id']
    outcomes = m['outcomes']
    prices = m['outcomePrices']
    print(f"Testing Market: {m['question']} (ID: {mid})")
    
    orders = []
    now_ts = int(time.time())
    for i, oc in enumerate(outcomes):
        orders.append({
            "ts": now_ts,
            "marketId": mid,
            "title": m['question'],
            "outcome": oc,
            "limitPrice": float(prices[i]),
            "sizeUSD": 50,
            "tag": "dual_test"
        })
    
    order_path = f"data/polymarket/verification_dual_orders_{mid}.jsonl"
    with open(order_path, "w") as f:
        for o in orders:
            f.write(json.dumps(o) + "\n")
    print(f"Orders written to {order_path}")
    print("Waiting 10 minutes for resolution...")

if __name__ == "__main__":
    os.makedirs("data/polymarket", exist_ok=True)
    run_dual_side_test()
