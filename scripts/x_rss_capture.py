#!/usr/bin/env python3
import argparse, os, json, datetime, urllib.request, xml.etree.ElementTree as ET
BASE='https://nitter.net/{}/rss'

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def text(x):
    return (x or '').strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--accounts', required=True)
    ap.add_argument('--limit', type=int, default=10)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.accounts,'r',encoding='utf-8') as f:
        accounts=[line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    now=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
    rows=[]
    for acct in accounts:
        url=BASE.format(acct)
        try:
            raw=fetch(url)
            root=ET.fromstring(raw)
            items=root.findall('./channel/item')[:args.limit]
            for it in items:
                title=text(it.findtext('title'))
                link=text(it.findtext('link'))
                pub=text(it.findtext('pubDate'))
                desc=text(it.findtext('description'))
                rows.append({
                    'capturedAt': now,
                    'platform': 'X',
                    'captureMethod': 'nitter-rss',
                    'author': acct,
                    'title': title,
                    'url': link,
                    'publishedAt': pub,
                    'text': desc,
                    'checkableCandidate': any(k in (title+' '+desc).lower() for k in ['will ',' by ', 'before ', 'today', 'tomorrow', 'this week', '24h', 'hours', 'break', 'above', 'below']),
                })
        except Exception as e:
            rows.append({'capturedAt': now, 'platform':'X', 'captureMethod':'nitter-rss', 'author':acct, 'error':repr(e)})
    with open(args.out,'w',encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')
    print(json.dumps({'accounts': len(accounts), 'rows': len(rows), 'out': args.out}, ensure_ascii=False))

if __name__=='__main__':
    main()
