# Prediction Platform Library

## Goal
Identify which platforms are worth monitoring for prediction cases, what kind of information each platform can provide, and how useful/checkable those signals are.

## Evaluation dimensions
For each platform, evaluate:
1. signal density
2. checkable outcome availability
3. time-window clarity
4. data accessibility
5. noise level
6. suitability for high-frequency case generation
7. suitability for event prediction
8. suitability for price/range prediction support

## Platform candidates
### 1. X / Twitter
- strengths:
  - high-frequency prediction opinions
  - short-window crypto/event calls
  - many explicit targets and time windows
- weaknesses:
  - high noise
  - source quality uneven
  - collection and validation require filtering
- best use:
  - crypto short-window cases
  - public prediction case mining
  - event-case discovery

### 2. Polymarket
- strengths:
  - explicit market structure
  - built-in probability / price
  - later checkable resolution
- weaknesses:
  - many long-cycle markets
  - some noisy or narrative-heavy markets
- best use:
  - event prediction training
  - market-implied probability reference
  - settlement-based later validation

### 3. Binance / exchange market data
- strengths:
  - structured, stable, high-frequency price data
  - easy result checking
  - good for 4h / 24h / grid / range prediction
- weaknesses:
  - price-only is not enough for some event-driven moves
- best use:
  - large-scale fast-feedback prediction cases
  - short-horizon and range/grid training

### 4. News / announcement sources
- strengths:
  - clearer event facts
  - better for cause-driven event prediction
- weaknesses:
  - lower frequency than social platforms
- best use:
  - event verification
  - catalyst tracking

### 5. Other social / community platforms
- candidates:
  - Telegram channels
  - Discord communities
  - Reddit
  - Farcaster
- current status:
  - not priority until X + exchange + Polymarket loop is stable
- best use:
  - secondary source expansion after core pipeline works

## Current priority order
1. Binance / exchange market data
2. X / Twitter
3. Polymarket
4. News / announcement sources
5. Other social/community platforms

## Rule
Do not collect platforms just because they are available. Collect only where the platform can generate checkable prediction cases or improve profitable prediction ability.
