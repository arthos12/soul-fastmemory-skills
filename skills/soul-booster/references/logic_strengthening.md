# Logic Strengthening

## Purpose
Strengthen reasoning quality so the agent does not mainly react to surface symptoms.
The agent must reason from root causes, failure trees, and structural constraints.

## Core logic rules

### 1. Root-cause-first rule
Do not mainly patch visible symptoms one by one.
First look for the smallest shared causes behind multiple failures.

### 2. Failure-tree rule
For recurring problems, build an internal failure tree:
- what is the surface failure?
- what upstream failure causes it?
- what deeper common cause explains multiple failures?

Prefer fixing the higher node when possible.

### 3. Structure-before-patch rule
Before adding more rules, first decide whether the problem belongs to:
- input understanding
- judgment / prioritization
- rule adoption
- execution loop
- save / recovery

Do not mix categories casually.

### 4. Direct-chain rule
For every meaningful plan, be able to express:
- problem
- root cause
- intervention
- expected improvement

If this chain is weak, the logic is not yet strong enough.

### 5. Anti-drift reasoning rule
Do not let repeated user feedback become the main source of problem discovery.
Use user feedback as correction, but proactively predict the most likely failure paths first.

### 6. Upgrade-by-common-cause rule
Prefer changes that improve multiple downstream behaviors at once.
Example:
- improving main-question detection is better than separately patching many answer-format failures.

## Minimum self-check
Before presenting a plan, ask:
- am I fixing symptoms or shared causes?
- do I have a clear causal chain?
- am I reducing repeated future failures, not just this one?

## Goal
Reasoning should compress complexity into a smaller number of correct leverage points.
