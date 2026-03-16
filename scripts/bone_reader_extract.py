#!/usr/bin/env python3
import json,re,requests,datetime,os,sys
URL='https://polymarket.com/profile/%40BoneReader'
html=requests.get(URL,headers={'User-Agent':'Mozilla/5.0'},timeout=20).text
m=re.search(r'__NEXT_DATA__"[^>]*>(.*?)</script>',html,re.S)
obj=json.loads(m.group(1))
queries=obj['props']['pageProps']['dehydratedState']['queries']
out={'fetchedAt':datetime.datetime.utcnow().isoformat()+'Z','profileUrl':URL,'queryMap':{}}
for q in queries:
    key=q.get('queryKey')
    state=q.get('state',{})
    data=state.get('data')
    out['queryMap'][json.dumps(key,ensure_ascii=False)]=data
os.makedirs('data/polymarket',exist_ok=True)
path='data/polymarket/bone_reader_profile_dump.json'
json.dump(out,open(path,'w'),ensure_ascii=False,indent=2)
print(path)
