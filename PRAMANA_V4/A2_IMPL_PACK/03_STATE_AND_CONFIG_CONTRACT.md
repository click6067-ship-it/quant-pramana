# PRAMANA A2 — State and Config Contract

Claude 구현 실수를 막기 위한 가장 중요한 문서다. 모든 파일은 이 계약을 따른다.

---

## 1. Directory Contract

```text
config/
  a2_convex_raider.yaml
  a2_state_mapping.yaml
  a2_provider.yaml

positions/
  a2_state.json
  attack.json
  moonshot.json
  vault.json

outputs/a2_live/
  nav_log.csv
  allocation_log.csv
  vault_ledger.csv
  attack_ledger.csv
  moonshot_ledger.csv
  war_plan.json
  dashboard.html

outputs/a2_backtest/
  backtest_panel.csv
  multi_anchor.csv
  charts/

reports/
  A2_daily_war_plan.md
  A2_weekly_vault_review.md
  A2_codex_check.md
```

---

## 2. Single Source of Truth

### Portfolio config

`config/a2_convex_raider.yaml`이 기본 비중, 범위, R sizing, Vault rules, max change rule의 단일 소스다.

### State mapping

`config/a2_state_mapping.yaml`이 LLM/Risk state → target weight mapping의 단일 소스다.

### Position state

`positions/*.json`은 현재 open state의 단일 소스다.

### Ledger

`outputs/a2_live/*.csv`는 append-only다.

---

## 3. Backtest vs Live Contract

```text
backtest 함수는 outputs/a2_backtest/만 쓴다.
live runner는 outputs/a2_live/만 쓴다.
backtest 결과를 live NAV로 표시하지 않는다.
live inception 이전 데이터는 live ledger에 절대 쓰지 않는다.
```

Dashboard는 반드시 두 섹션으로 분리한다.

```text
Historical Backtest Panel
Live Paper Ledger
```

---

## 4. Signal Timing Contract

모든 신호는 아래 규칙을 따른다.

```text
EOD signal at date t → trade/weight at date t+1
Intraday bar signal at bar t close → entry at next bar or later
EDGAR filing accepted at timestamp t → earliest eligible entry after timestamp + data lag rule
Premarket signal → regular session entry only if provider supports timestamp
```

금지:

```text
당일 종가로 계산한 leadership/decay/market state를 당일 수익률에 적용
월평균 첫 가격을 starting value로 사용
당일 전체 거래량으로 entry-time RVOL 계산
```

---

## 5. Capital Accounting Contract

총 NAV는 항상 아래 합과 같아야 한다.

```text
TOTAL_NAV = active_cash + QQQ_value + TQQQ_value + Attack_value + Moonshot_value + Hard_Vault + Reload_Vault
```

Active capital:

```text
ACTIVE_NAV = active_cash + QQQ_value + TQQQ_value + Attack_value + Moonshot_value + Reload_Vault_eligible_amount
```

Hard Vault는 공격자금이 아니다.

---

## 6. Sleeve State Schema

### a2_state.json

```json
{
  "date": "YYYY-MM-DD",
  "mode": "BASE|BERSERKER|RED_KING|ATTACK_LOCKOUT|CRASH_LOCKOUT",
  "target_weights": {
    "qqq": 0.35,
    "tqqq": 0.35,
    "attack": 0.10,
    "moonshot": 0.10,
    "vault": 0.10
  },
  "actual_weights": {},
  "states": {
    "leadership": "GREEN|YELLOW|RED",
    "tqqq_decay": "GREEN|YELLOW|RED",
    "market_stress": "GREEN|YELLOW|RED",
    "llm_narrative": "GREEN|YELLOW|RED"
  },
  "human_review_required": false
}
```

---

## 7. Required Invariants

모든 runner 종료 시 아래를 체크한다.

```text
weights sum to 1.0 ± tolerance
TOTAL_NAV equals sleeve values + cash + vault
Hard Vault never decreases except manual withdrawal flag
No target weight outside configured min/max
No daily weight change > 5%p unless Crash Lockout
No weekly weight change > 10%p unless Crash Lockout
All signals applied with next-bar timing
```

Invariant 실패 시:

```text
runner must fail closed
no ledger append
write error report
```
