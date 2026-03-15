# MVC Test: conv_req_capture

## Goal
A multi-point message is captured into requirements inbox and triaged immediately.

## Steps
```bash
python3 scripts/conv_req_capture.py --text "效率=速度*时间利用率；要汇报并发、时间利用率、空闲多久、最终完成数量占比；纠错/审核也要修" --source test --priority P0
python3 scripts/req_latest.py >/dev/null
python3 scripts/delivery_ratio_report_v2.py | head -n 5
```

## Pass
- command prints JSON with count>=2
- inbox/triaged files have new lines
