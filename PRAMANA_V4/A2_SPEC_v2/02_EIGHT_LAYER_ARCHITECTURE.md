# 02 — A2 8-Layer Architecture

A2는 기존 PRAMANA 8레이어를 유지하되, 각 레이어에 QQQ/TQQQ/Attack/Moonshot/Vault 모듈을 명확히 배치한다.

## Layer 1 — Data & Integrity

역할:

```text
Sharadar EOD/PIT/fundamental backbone
EDGAR filing timestamp
minute provider interface
yfinance proxy
LLM input snapshots
look-ahead 방지
```

필수:

```text
available_at <= decision_time
signal_time < execution_time
all risk states shift(1)
```

## Layer 2 — Signal / State Factory

생성하는 상태:

```text
Leadership Risk
Market Stress
TQQQ Decay Meter
TQQQ Booster Rent
LLM Narrative State
NEG Filing Flags
Attack Candidates
Moonshot Draft Candidates
TQ-DH Dip Type
```

## Layer 3 — Sleeve Engines

```text
QQQ Module
TQQQ Booster Module
Attack Module
Moonshot Module
Vault Module
```

각 모듈은 독립 ledger를 가진다.

## Layer 4 — Dynamic Allocator / Mapping Engine

LLM이 비중을 정하지 않는다.

```text
LLM state → GREEN/YELLOW/RED
Mapping engine → target weight
Risk limits → clamp
next-bar 적용
```

## Layer 5 — Risk Engine

```text
Leadership RED
Decay Zone
Market Stress RED
Beta Governor
Drawdown ladder
Attack token lockout
Moonshot thesis invalidation
NEG Gate
```

Risk Engine은 우선 **신규진입/증액 금지** 역할을 한다. 기존 QQQ/TQQQ 자동매도는 극단 조건에서만 후보로 표시한다.

## Layer 6 — Execution / Paper Ledger

현재는 paper only.

```text
EOD rebalance for QQQ/TQQQ/Vault
Intraday paper signal for Attack
Manual/paper entry for Moonshot
Vault transfer ledger
```

실제 주문 API가 붙더라도 기본은 paper.

## Layer 7 — Attribution / Monitoring

대시보드 필수:

```text
A2 active NAV
Vault-adjusted NAV
QQQ/SPY/TQQQ/naive benchmarks
TQQQ contribution
Attack contribution
Moonshot contribution
Vaulted Profit
Dynamic allocator contribution
TQ-DH contribution
```

## Layer 8 — Governance / Human Gate

```text
실자본 금지
Hard Vault 재투입 금지
Moonshot thesis 승인 필요
LLM 직접매매 금지
Codex STOP checklist 통과 필요
```

## 레이어별 구현 산출물

| Layer | 주요 파일 |
|---|---|
| L1 | `engine/a2_data_contract.py`, providers |
| L2 | `engine/a2_risk_dashboard.py`, `a2_daily_war_plan.py` |
| L3 | `a2_book.py`, `a2_attack_ledger.py`, `a2_moonshot_ledger.py`, `a2_profit_vault.py` |
| L4 | `a2_dynamic_allocator.py`, `config/a2_state_mapping.yaml` |
| L5 | `a2_neg_gate.py`, `a2_tq_dh.py`, `a2_drawdown_rules.py` |
| L6 | `a2_live_runner.py`, `a2_attack_executor_paper.py` |
| L7 | `a2_dashboard.py`, reports |
| L8 | checklist, decision logs |
