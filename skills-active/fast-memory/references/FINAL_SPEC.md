# Fast Memory Final Spec

This file is the compact final spec for the installable skill.

## Defaults
- full-session hot buffer: 3
- constrained mode: 1
- hot window: 3 days
- structured restore first
- full-session fallback second

## Save flow
1. classify content
2. assign importance
3. save with matching completeness
4. place in the correct layer

## Restore flow
1. load recent structured memory
2. identify important and recently important content
3. reconstruct topic, logic, step, goal
4. expand key details
5. use full-session fallback if needed

## Lifecycle
1. recent full preservation
2. extracted transfer after 3 days
3. second-pass compression for cold oversized content
4. safe removal of old raw sessions after transfer
