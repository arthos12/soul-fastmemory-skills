# Weak Bot Bootstrap

## Purpose
Some bots are too weak to benefit from long skill documents immediately.
For those bots, start with a compressed bootstrap layer.

## Bootstrap principle
Do not assume the bot can absorb the whole skill at once.
Instead, force a small number of default behaviors first.

## Required default behaviors
1. identify the main question before answering
2. split compound questions
3. answer current-state questions directly first
4. do not let keywords override intent
5. if the goal is clear, provide one next action
6. if understanding is materially uncertain, ask one short clarification

## Adoption rule
A bot does not count as improved just because it can quote the skill.
It counts as improved only when these behaviors appear in real turns.

## Compression rule
For weaker bots:
- prioritize short hard rules over long explanations
- prioritize behavior examples over abstract prose
- prioritize one-step corrections over large conceptual frameworks

## Upgrade path
- first pass: minimum cognitive protocol
- second pass: in-task correction
- third pass: strict grading and self-training
- fourth pass: larger soul runtime logic

## Goal
Make low-capability bots gain usable improvements quickly instead of drowning in documentation.
