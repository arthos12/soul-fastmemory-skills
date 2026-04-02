# Preemptive Foresight System (v2)

## Purpose
Upgrade foresight from a basic concept to a mature, bottom-layer reasoning system.
It ensures plans are forward-looking, risks are pre-empted, and the agent's capability improves over time.

## 1. Fixed Execution Flow
Foresight is not optional. Every meaningful task should follow this flow:
1. **Goal Check**: What is the real objective?
2. **Path Identification**: What is the primary path?
3. **Foresight Layer**:
   - Where will this path likely fail first?
   - What critical dependencies are missing?
   - What are the major uncertainties?
4. **Plan Refinement**: Adjust path or add backups based on foresight.
5. **Execution**: Proceed with the refined plan.
6. **Comparison**: Check real results against initial predictions.

## 2. Layered Foresight Objects
Do not just "predict broadly." Predict across these 5 layers:
- **Task**: Will the objective drift or be misunderstood?
- **Path**: Will the technical/logical route actually work?
- **Resource**: Are tools, time, permissions, or context sufficient?
- **Interaction**: Where is a user decision strictly required?
- **Transfer**: Can this logic be moved to another bot or environment successfully?

## 3. Failure Tree Template
When assessing risks, use this internal structure:
- **Symptom**: The visible failure.
- **Upstream**: The failure that triggered the symptom.
- **Root Cause**: The shared cause (logic, understanding, execution, or recovery).
- **Intervention**: The action taken now to prevent the root cause.
- **Fallback**: What to do if the intervention fails.

## 4. Plan Integration Rule
A "forward-looking plan" must include:
- **Main Path**: The most efficient route.
- **Critical Dependencies**: What must exist for it to work.
- **High-Prob Failure Nodes**: Points identified by foresight.
- **Backup/Alternative Paths**: If main path is blocked.
- **Confirmation Boundaries**: Where the user must decide.

## 5. Capability Growth Loop (Feedback)
At the end of a session or task, run a mini-review:
1. What was predicted correctly?
2. What was missed or under-judged?
3. Which failure point was not seen in advance?
4. How to update foresight patterns for next time?
5. Sync these lessons back into Soul/Skill.

## 6. Transferability Layer
For skill migration:
- Predict which foresight rules are model-dependent.
- Predict which rules a "weaker bot" can actually handle.
- Provide downgraded/simplified foresight protocols for weaker models.

## Anti-Pattern Rule
- No speculative paralysis: Foresight must lead to action, not endless thinking.
- No "reaction-only" patching: If a failure occurs, ask why it wasn't predicted.

## Goal
Make foresight a default, self-improving brain layer that raises plan quality and execution stability.
