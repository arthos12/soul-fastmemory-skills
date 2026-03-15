#!/usr/bin/env python3
import os, re, sys
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace')
BASE = ROOT / 'skills' / 'soul-booster' / 'references'
MODELS = BASE / 'models'

errors = []

# 1) required constitution file
if not (BASE / 'core_brain_library_constitution.md').exists():
    errors.append('missing core_brain_library_constitution.md')

# 2) U* should be understanding only, not logic/prediction/rules
for p in sorted(MODELS.glob('U*.md')):
    txt = p.read_text(encoding='utf-8', errors='ignore')
    bad = []
    if re.search(r'演绎|归纳|辩证|溯因|系统论', txt):
        bad.append('contains logic terms')
    if re.search(r'预测|预判|路径推演|反转预警', txt):
        bad.append('contains prediction terms')
    if re.search(r'先审后做|人话输出|焦点控制|验证规则|防 stub', txt):
        bad.append('contains runtime rules')
    if bad:
        errors.append(f'{p.name}: ' + ', '.join(bad))

# 3) L0 logic index should not contain understanding or runtime wording as primary definition
l0 = MODELS / 'L0_logic_library_index.md'
if l0.exists():
    txt = l0.read_text(encoding='utf-8', errors='ignore')
    if '语义理解' in txt or '意图识别' in txt:
        errors.append('L0_logic_library_index.md mixes understanding terms')

# 4) constitution referenced in key files
for p in [BASE/'model_library_index.md', BASE/'core_runtime_rules.md', ROOT/'skills'/'soul-booster'/'SKILL.md']:
    if p.exists():
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if 'core_brain_library_constitution.md' not in txt:
            errors.append(f'{p.name}: missing constitution reference')

# 5) constitution must contain strict-review gate wording
const = (BASE / 'core_brain_library_constitution.md').read_text(encoding='utf-8', errors='ignore') if (BASE / 'core_brain_library_constitution.md').exists() else ''
for needle in ['最严格审核', 'Jim 主动提出修改时', '默认否决原则']:
    if needle not in const:
        errors.append(f'constitution missing required clause: {needle}')

if errors:
    print('BOUNDARY_CHECK_FAIL')
    for e in errors:
        print('-', e)
    sys.exit(1)

print('BOUNDARY_CHECK_OK')
