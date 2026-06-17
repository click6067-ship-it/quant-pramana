# PRAMANA A2 — 8 Layer Architecture

A2는 기존 PRAMANA 8레이어 구조 위에서 구현한다.

```text
L1 Data & Integrity
→ L2 Signal / Feature / LLM State
→ L3 Sleeve Modules
→ L4 Dynamic Allocator / Mapping
→ L5 Risk Gates / Governance
→ L6 Execution / Paper Ledger
→ L7 Attribution / Dashboard / Monitoring
→ L8 Human Governance / Review
```

---

## L1. Data & Integrity Layer

### 역할

모든 데이터의 출처·timestamp·사용 가능 시점을 관리한다.

### 입력

```text
Sharadar: EOD price, PIT universe, fundamentals, corporate actions
EDGAR: 8-K, 10-Q, 10-K acceptance timestamp
Minute provider: yfinance proxy / Polygon / Databento / Alpaca SIP
Market data: QQQ, TQQQ, SPY, VIX/VXN, HYG/IEF 등
LLM input corpus: filings, news summaries, narrative sources
```

### 불변 규칙

```text
모든 신호는 next-bar.
당일 종가로 계산한 신호는 당일 수익에 적용 금지.
EDGAR는 acceptance timestamp 기준.
yfinance minute는 PROXY 라벨.
Alpaca 무료 IEX는 full-market VWAP/RVOL 검증용 아님.
live ledger와 historical backtest는 저장 위치와 dashboard 섹션을 분리.
```

---

## L2. Signal / Feature / LLM State Layer

### 역할

가격·분봉·공시·LLM narrative를 feature와 state로 바꾼다.

### 산출물

```text
leadership_state: GREEN/YELLOW/RED
tqqq_decay_state: GREEN/YELLOW/RED
market_stress_state: GREEN/YELLOW/RED
llm_narrative_state: GREEN/YELLOW/RED
attack_permission_state: FULL/HALF/LOCKED
moonshot_permission_state: OPEN/HOLD_ONLY/LOCKED
vault_state: ACCUMULATE/HOLD/RELOAD_ALLOWED
```

### 금지

```text
L2는 매수/매도 명령을 내리지 않는다.
L2는 비중 숫자를 직접 결정하지 않는다.
L2는 상태와 근거만 낸다.
```

---

## L3. Sleeve Modules Layer

### 5개 sleeve

```text
QQQ Core
TQQQ Booster
Attack
Moonshot
Vault/Cash
```

각 sleeve는 독립 state, target weight, actual weight, P&L, ledger를 가진다.

---

## L4. Dynamic Allocator / Mapping Layer

### 역할

L2 state를 받아 사전 정의된 mapping으로 target weights를 계산한다.

### 규칙

```text
기본 비중 = 35/35/10/10/10
한 번 변경 단위 = 5%p
하루 최대 변경 = 5%p
주간 최대 변경 = 10%p
Hard Vault는 target allocation 대상 아님
```

LLM이 “TQQQ 45%”라고 말해도 무시한다. Mapping 파일만 유효하다.

---

## L5. Risk Gates / Governance Layer

### 역할

진입 허용·증액 금지·Moonshot 금지·Vault 우선 등 권한을 제어한다.

### Gate 종류

```text
Leadership Risk Gate
TQQQ Decay Gate
Market Stress Gate
LLM Narrative Gate
NEG Filing Gate
Attack Token Gate
Moonshot Thesis Gate
Vault Reload Gate
Human Lockout Gate
```

---

## L6. Execution / Paper Ledger Layer

### 역할

실제 주문이 아니라 paper ledger를 업데이트한다.

### 산출물

```text
outputs/a2_live/nav_log.csv
outputs/a2_live/trades_attack.csv
outputs/a2_live/trades_moonshot.csv
outputs/a2_live/vault_ledger.csv
positions/attack.json
positions/moonshot.json
positions/vault.json
```

### 원칙

```text
execution is paper-only
same-bar execution 금지
bar-close signal이면 다음 bar 또는 다음 session 적용
extended hours는 별도 flag
```

---

## L7. Attribution / Dashboard / Monitoring Layer

### 역할

성과를 분해하고 눈속임을 막는다.

### 반드시 표시

```text
A2-T vs A2-Q
A2 vs QQQ/SPY/TQQQ/naive
QQQ contribution
TQQQ contribution
Attack contribution
Moonshot contribution
Vaulted Profit
Vault-adjusted NAV
active NAV
effective beta
dynamic allocator contribution
TQQQ decay drag
```

---

## L8. Human Governance / Review Layer

### 역할

사람 승인과 정지 규칙.

### 사람 리뷰 필요

```text
A2 MDD -30%
TQQQ sleeve MDD -35%
Moonshot thesis 무효화
Hard NEG filing in open Moonshot
LLM Narrative RED + Leadership RED 동시
API/data integrity failure
Codex STOP
```

---

## 구현 순서와 레이어 관계

```text
Phase 0: L1/L6/L7 무결성
Phase A: L6/L7 Vault ledger
Phase B: L3/L5 Attack/Moonshot
Phase C: L2/L4 LLM State + Mapping
Phase D: L7/L8 dashboard + runbook
```
