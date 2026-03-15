# MVC Test: two_lane_generator

Manual test:
- Ask: "两条线怎么提效".
- Must output:
  - lane1: input/action/output/verify
  - lane2: input/action/output/verify
  - interface + failure loop

Also test parallel validation tool:
```bash
python3 scripts/parallel_validate.py \
  --cmd "python3 scripts/req_latest.py" \
  --cmd "python3 scripts/delivery_ratio_report_v2.py"
```
