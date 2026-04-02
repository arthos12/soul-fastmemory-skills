#!/usr/bin/env bash
set -euo pipefail

# Create an MVC (model card + script stub + test stub) for a 1-line requirement.
# Usage: scripts/mvc_create.sh <id> <name-slug>
# Example: scripts/mvc_create.sh L2 ack-no-silence

ID="${1:?need id (e.g. L2)}"
NAME="${2:?need name slug (e.g. ack-no-silence)}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODEL_PATH="skills/soul-booster/references/models/${ID}_${NAME}.md"
SCRIPT_PATH="scripts/${NAME}.sh"
TEST_PATH="docs/mvc_tests/${NAME}.md"

mkdir -p "$(dirname "$MODEL_PATH")" "$(dirname "$TEST_PATH")"

if [[ ! -f "$MODEL_PATH" ]]; then
cat > "$MODEL_PATH" <<EOF
# ${ID} ${NAME}

## 一句话定义

## 适用场景

## 禁用/高风险场景

## 输入

## 输出格式（强制）

## 验收指标

## 最小测试
- 运行：bash ${SCRIPT_PATH}
EOF
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
cat > "$SCRIPT_PATH" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "TODO: implement"
EOF
chmod +x "$SCRIPT_PATH"
fi

if [[ ! -f "$TEST_PATH" ]]; then
cat > "$TEST_PATH" <<EOF
# MVC Test: ${ID} ${NAME}

## Goal

## Steps
1) Run: 
   - \
   	bash ${SCRIPT_PATH}

## Pass/Fail
- Pass if:
- Fail if:
EOF
fi

echo "Created/ensured:" \
  && echo "- $MODEL_PATH" \
  && echo "- $SCRIPT_PATH" \
  && echo "- $TEST_PATH"
