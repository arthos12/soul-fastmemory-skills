import json

index = {
    "created_at": "2026-03-21T04:07:00Z",
    "source": "Polymarket Leaderboard",
    "traders": [
        {
            "rank": 0,
            "name": "BoneReader",
            "address": "0xd84c2b6d65dc596f49c7b6aadd6d74ca91e407b9",
            "username": "BoneReader",
            "monthly_pnl": 452686,
            "volume": 82800000,
            "data_dir": "br",
            "notes": "参考标杆 - Crypto 5分钟短线"
        },
        {
            "rank": 1,
            "name": "HorizonSplendidView",
            "address": "0x02227b8f5a9636e895607edd3185ed6ee5598ff7",
            "monthly_pnl": 4016107,
            "volume": 12394130,
            "data_file": "horizon_user.html",
            "notes": "月度盈利$400万 - 体育预测"
        },
        {
            "rank": 2,
            "name": "reachingthesky",
            "address": "0xefbc5fec8d7b0acdc8911bdd9a98d6964308f9a2",
            "monthly_pnl": 3742635,
            "volume": 13750267,
            "data_file": "reaching_user.html",
            "notes": "月度盈利$370万"
        },
        {
            "rank": 3,
            "name": "majorexploiter",
            "address": "0x019782cab5d844f02bafb71f512758be78579f3c",
            "monthly_pnl": 2416975,
            "volume": 6949025,
            "data_file": "major_user.html",
            "notes": "名字暗示套利模式"
        }
    ]
}

with open('data/polymarket/top_traders/index.json', 'w') as f:
    json