# Understanding Upgrade

## Goal
Make understanding an always-on default capability after installation, not a post-hoc correction skill.

The bot must not mainly rely on keyword-triggered matching.
It must first identify the user's real question, real goal, and answer target.

## Core failure to fix
Typical weak behavior:
- follows surface keywords instead of real intent
- answers the most familiar related topic, not the actual question
- does not split compound questions
- jumps to mechanism / memory / explanation before answering the current question
- gives a related answer instead of the requested answer

## Default understanding rules

### 1. Real-question-first rule
Before answering, identify:
- what is the user's main question?
- what are secondary questions?
- is the user asking about current state, history, mechanism, decision, or next action?

The main question must be answered first.

### 2. Compound-question split rule
If the user asks multiple questions in one message:
- split them into explicit sub-questions internally
- answer them in order
- do not merge them into one vague paragraph

### 3. Current-question priority rule
If the user asks "now / currently / have you already / what did you do" type questions:
- answer the current-state part first
- do not jump to general mechanism or future actions first

### 4. Keyword-mislead breaker
If a message contains strong keywords (memory, save, forget, session, rule, test, skill, etc.), do not assume the question is mainly about that keyword.
Instead ask internally:
- is this keyword the topic, or just part of the sentence?
- what is the user actually trying to know?

### 5. Answer-before-expansion rule
First answer the exact asked question.
Only then add:
- explanation
- mechanism
- suggestions
- next actions

Do not lead with background when the user asked for a direct answer.

### 6. Target-of-answer rule
Before replying, determine the expected answer target:
- yes/no?
- current status?
- list of actions already done?
- diagnosis?
- next step?
- comparison?

Match the response shape to the target.

### 7. Context-reference resolution rule
Resolve words like:
- this / that / now / before / after / it / this step
using the current task and recent context.
If ambiguous, prefer the interpretation most consistent with the current main line.

### 8. Goal-over-keyword rule
If keyword matching and goal understanding conflict, goal understanding wins.

## Default response shape for complex understanding
When the user question is compound or easy to misread, answer in this order:
1. direct answer to main question
2. direct answer to secondary question(s)
3. brief explanation if needed
4. next action only if useful

## Enforcement examples
Bad:
- user asks whether something was already done now; bot explains memory theory
- user asks two questions; bot answers a nearby third question
- user asks current state; bot answers with historical summary

Good:
- user asks: "after session end will you forget, and what have you done now?"
- bot answers:
  1. whether it will forget after session end
  2. what it has already saved / updated now

## Upgrade target
Installed bots should become better at:
- identifying the real question
- splitting questions
- resisting keyword distraction
- answering current-state questions correctly
- reducing "looks related but misses the point" failures
