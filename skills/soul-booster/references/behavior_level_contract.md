# Behavior Level Contract

## Purpose
Capability levels must map to observable behavior, not vague self-description.

## Levels

### L0 — Installed only
- skill files exist
- behavior not yet meaningfully affected
- mostly old habits

### L1 — Rule summary only
- can restate rules
- often sounds aligned
- real tasks still mostly template-driven
- understanding failures are frequent

### L2 — Partial adoption
- some rules affect default behavior
- can produce structured replies and simple execution
- compound-question handling is unstable
- frequently follows keywords instead of real intent
- prioritization is weak

### L3 — Minimal execution loop passes
- can do: short state/plan -> action -> verification -> save
- can finish simple real tasks
- still unstable on real understanding, prioritization, and repeated-task consistency
- may still over-report completion

### L4 — Real-task understanding and judgment
- reliably identifies the main question in real tasks
- splits compound questions correctly
- answers current-state questions directly first
- provides one sensible next action when the goal is clear
- strict self-evaluation is present
- does not casually report "failed checks: none"

### L5 — Stable cross-task reliability
- L4 behavior holds across repeated tasks and session recovery
- understanding remains stable even with ambiguous phrasing
- can recover from drift quickly
- low need for human correction

## Rules
- use only L0-L5 as the main capability label
- do not invent labels like "medium mode" for grading
- choose the highest level only when all lower-level behaviors are already stable
- when uncertain between two levels, choose the lower one
