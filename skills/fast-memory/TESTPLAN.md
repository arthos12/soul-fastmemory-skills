# fast-memory test plan

## Goal
Verify that after installation, the skill is in a directly usable default-on state.

## Checks
1. skill package validates
2. skill exists in active skills directory
3. metadata files exist (`_meta.json`, `BOOTSTRAP.md`)
4. SKILL.md states default-on behavior
5. install docs state install-immediately-active behavior
6. OpenClaw can see the skill directory
7. packaged artifact exists

## Note
This verifies packaging + installation + default-on skill readiness.
It does not prove that the OpenClaw runtime automatically executes background maintenance hooks unless the runtime itself supports such hooks.
