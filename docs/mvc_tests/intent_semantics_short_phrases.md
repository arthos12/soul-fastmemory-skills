# MVC Test: intent_semantics_short_phrases

## Goal
Reduce drift on short user phrases by forcing correct intent classification + human-first reply.

## How to use
Jim provides 5 short phrases he often uses.
For each phrase, assistant must output:
1) Reference binding: Prev1 / Prev5 / New (and which it points to)
2) What Jim wants (1 sentence)
3) Correct response (1-3 sentences)

## Pass
- No multiple-choice when Jim wants a direct answer
- No concept-dumping when Jim says "说人话/没懂"
- When Jim says "现在做", assistant moves to plan+execute
