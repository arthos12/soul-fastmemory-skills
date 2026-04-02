#!/usr/bin/env python3
import argparse, json, os, time
from datetime import datetime, timezone

STATE_PATH = 'data/execution_guard/state.json'
EVENTS_PATH = 'data/execution_guard/events.jsonl'


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def utciso():
    return datetime.now(timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)

    p_start = sp.add_parser('start-mainline')
    p_start.add_argument('--task', required=True)

    p_progress = sp.add_parser('record-progress')
    p_progress.add_argument('--task', required=True)
    p_progress.add_argument('--artifact', default='')
    p_progress.add_argument('--note', default='')

    p_reply = sp.add_parser('check-reply')
    p_reply.add_argument('--task', required=True)
    p_reply.add_argument('--has-artifact', action='store_true')
    p_reply.add_argument('--has-result', action='store_true')
    p_reply.add_argument('--has-blocker', action='store_true')
    p_reply.add_argument('--asked-confirmation', action='store_true')
    p_reply.add_argument('--high-risk', action='store_true')

    p_retro = sp.add_parser('retro-check')
    p_retro.add_argument('--task', required=True)

    args = ap.parse_args()
    state = load_json(STATE_PATH, default={}) or {}
    state.setdefault('mainlines', {})
    state.setdefault('regressions', {'unnecessary_confirmation': 0, 'no_artifact_reply': 0, 'mainline_stall': 0})

    now = int(time.time())
    if args.cmd == 'start-mainline':
        state['mainlines'][args.task] = {
            'active': True,
            'started_at': now,
            'last_progress_at': now,
            'last_artifact_at': None,
            'last_retro_at': None,
            'status': 'active',
            'self_prompt': '继续往下推进，不要停在解释层',
        }
        dump_json(STATE_PATH, state)
        append_jsonl(EVENTS_PATH, {'ts': utciso(), 'type': 'start-mainline', 'task': args.task, 'prompt': '继续往下推进，不要停在解释层'})
        print(json.dumps({'ok': True, 'task': args.task, 'prompt': '继续往下推进，不要停在解释层'}, ensure_ascii=False))
        return

    if args.task not in state['mainlines']:
        state['mainlines'][args.task] = {'active': True, 'started_at': now, 'last_progress_at': now, 'last_artifact_at': None, 'last_retro_at': None, 'status': 'active', 'self_prompt': '继续往下推进，不要停在解释层'}

    m = state['mainlines'][args.task]

    if args.cmd == 'record-progress':
        m['last_progress_at'] = now
        if args.artifact:
            m['last_artifact_at'] = now
        m['status'] = 'active'
        prompt = '已推进一层，继续往下推进下一层，不要停'
        dump_json(STATE_PATH, state)
        append_jsonl(EVENTS_PATH, {'ts': utciso(), 'type': 'record-progress', 'task': args.task, 'artifact': args.artifact, 'note': args.note, 'prompt': prompt})
        print(json.dumps({'ok': True, 'task': args.task, 'prompt': prompt}, ensure_ascii=False))
        return

    if args.cmd == 'check-reply':
        violations = []
        if args.asked_confirmation and not args.high_risk:
            state['regressions']['unnecessary_confirmation'] += 1
            violations.append('unnecessary_confirmation')
        if not (args.has_artifact or args.has_result or args.has_blocker):
            state['regressions']['no_artifact_reply'] += 1
            violations.append('no_artifact_reply')
        m['last_progress_at'] = now if (args.has_artifact or args.has_result or args.has_blocker) else m.get('last_progress_at')
        prompt = '本轮回复后必须继续执行下一步；禁止以纯结论收尾' if violations else '本轮合格，继续往下推进，不要停'
        dump_json(STATE_PATH, state)
        append_jsonl(EVENTS_PATH, {'ts': utciso(), 'type': 'check-reply', 'task': args.task, 'violations': violations, 'prompt': prompt})
        print(json.dumps({'ok': len(violations) == 0, 'violations': violations, 'prompt': prompt, 'regressions': state['regressions']}, ensure_ascii=False))
        return

    if args.cmd == 'retro-check':
        last = m.get('last_progress_at') or m.get('started_at') or now
        stalled = (now - last) > 1800
        if stalled:
            state['regressions']['mainline_stall'] += 1
            m['status'] = 'stalled'
        m['last_retro_at'] = now
        prompt = '主线停滞，立刻切回最小执行动作并继续推进' if stalled else '主线未停，继续推进并顺手做小复盘'
        dump_json(STATE_PATH, state)
        append_jsonl(EVENTS_PATH, {'ts': utciso(), 'type': 'retro-check', 'task': args.task, 'stalled': stalled, 'prompt': prompt})
        print(json.dumps({'ok': True, 'stalled': stalled, 'prompt': prompt, 'regressions': state['regressions']}, ensure_ascii=False))
        return


if __name__ == '__main__':
    main()
