# Understanding Behavior Tests

## Purpose
Test whether the installed bot improved real understanding, not just formatting.

## Test 1: Compound question split
Prompt pattern:
- ask two questions in one sentence
Pass:
- bot answers both clearly and separately
Fail:
- bot merges them or answers only one

## Test 2: Current-state priority
Prompt pattern:
- ask what is true now and what has already been done
Pass:
- current state answered first
Fail:
- bot jumps to theory, memory design, or future plan first

## Test 3: Keyword distraction resistance
Prompt pattern:
- include strong words like save / memory / session / rule but the actual question is different
Pass:
- bot answers the real question
Fail:
- bot follows the keywords instead of intent

## Test 4: Main-question detection
Prompt pattern:
- user asks a broad sentence with one real point hidden inside
Pass:
- bot identifies the main point and answers it first
Fail:
- bot answers a nearby but less important point

## Test 5: Direct-answer-first discipline
Prompt pattern:
- ask a yes/no or current-status question
Pass:
- bot gives direct answer first, explanation second
Fail:
- bot starts with long background

## Evaluation note
A bot does not pass understanding just because it sounds structured.
It passes only if it reliably answers the actual intended question.
