# Prediction Case Library Spec

## Goal
Maintain a structured library of prediction cases so they can be monitored, checked, scored, and used to improve prediction ability.

## Minimum fields
- caseId
- sourcePlatform
- sourceType (self prediction / external prediction / market)
- targetType (price / range / event / probability)
- symbolOrEvent
- claim
- directionOrRange
- timeWindow
- createdAt
- checkAt
- actualResult
- status (open / checked / invalid / stale)
- confidence
- probability
- tradeCandidate (yes/no)
- sourceUrl
- sourceAuthor
- notes

## Monitoring states
1. open: waiting for result
2. due: result time arrived, should be checked now
3. checked: result already written
4. stale: missed check, needs repair
5. invalid: malformed or not checkable

## Core rule
Prediction without later checking is incomplete.

## Primary case buckets
- self crypto short-horizon predictions
- self crypto medium-horizon predictions
- self range/grid predictions
- Polymarket event predictions
- X/Twitter prediction cases
- later: other platform prediction cases
