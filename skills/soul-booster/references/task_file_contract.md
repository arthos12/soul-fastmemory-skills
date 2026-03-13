# Task File Contract

## Purpose
Tasks and goals must not live only inside the current session.
Each meaningful mainline task should have a file-based carrier so progress can survive session changes and idle/autonomous execution.

## Required rule
When a meaningful task or goal is established, create or update a task file.
The task file is the durable operational source, not just the conversation.

## Minimum required sections
1. Goal
- what the task is trying to achieve

2. Key facts / key requirements
- critical constraints
- critical decisions
- important user requirements
- acceptance standards

3. Current progress
- what is already done
- current stage
- next actionable step

4. Unresolved items
- open issues
- blockers
- what still needs verification
- what needs user cooperation

## Update rule
The task file must be updated when:
- requirements are clarified
- constraints change
- progress advances
- blockers appear or disappear
- goals become outdated, replaced, or complete

## Anti-loss rule
Do not rely on memory of the session alone.
If a requirement matters for future execution, put it into the task file or another durable file layer.

## Goal
Make task continuity depend on files, not fragile conversational state.
