# In-Task Correction

## Purpose
Do not wait until the end of the task to discover misunderstanding.
Correction must happen before and during the response, not only after.

## 3-stage correction loop

### 1. Before answering: question framing
Internally identify:
- main question
- sub-questions
- question type: current state / history / mechanism / next action / judgment
- expected answer shape

### 2. During answering: drift check
Before finalizing the answer, quickly check:
- am I answering the main question?
- did I miss any sub-question?
- did I get pulled by keywords instead of intent?
- am I giving background before the direct answer?
- if this is a current-state question, did I answer the current state first?

### 3. After answering: strict acceptance
Check:
- did the reply directly answer the user's actual question?
- was the answer shape matched to the request?
- did I add unnecessary mechanism discussion too early?
- should this failure/success be recorded for future correction?

## Rule
A beautiful format does not compensate for missing the point.
If the answer does not match the user's real question, treat the turn as failed understanding even if the structure looks good.
