import json
import os
import sys

STATE_FILE = "memory/session_state.json"

def save_checkpoint(task, step, metadata=None):
    state = {"task": task, "step": step, "metadata": metadata or {}, "timestamp": os.popen("date +%s").read().strip()}
    os.makedirs("memory", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"Checkpoint saved: {task} @ {step}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: checkpoint.py <task> <step>")
    else:
        save_checkpoint(sys.argv[1], sys.argv[2])
