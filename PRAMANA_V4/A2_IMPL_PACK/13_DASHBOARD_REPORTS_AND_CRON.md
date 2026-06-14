# PRAMANA A2 — Dashboard, Reports, and MiniPC Operation

## 0. 목적

A2는 미니PC에서 24h monitoring과 regular-session paper trading을 수행한다.

---

## 1. 24시간 운영 정의

미국 주식 전종목을 24시간 체결한다는 뜻이 아니다.

```text
24h monitoring
premarket scan
regular session intraday attack
after-hours filing/news scan
overnight risk planning
```

---

## 2. Daily Routine

미국 동부 기준 예시.

```text
05:30 data update
06:00 risk dashboard
06:30 LLM war plan
07:00 premarket scanner
09:30-16:00 intraday scanner / paper execution
16:15 EOD reconcile
17:00 vault review
18:00 dashboard publish
```

한국/미니PC cron은 현지 시간으로 변환한다.

---

## 3. Dashboard 필수 항목

```text
A2 active NAV
A2 vault-adjusted NAV
QQQ benchmark
SPY benchmark
TQQQ reference
naive beta benchmark
A2-Q vs A2-T
actual weights
target weights
mode
LLM states
Leadership Risk
TQQQ Decay Meter
Market Stress
TQQQ Booster Rent
Attack tokens
Attack candidates
Moonshot draft board
Moonshot open theses
Hard Vault
Reload Vault
Vault trigger status
Theme concentration
NEG filing flags
```

---

## 4. Reports

### Daily War Plan

```text
reports/A2_daily_war_plan.md
```

내용:

```text
Market state
Leadership state
TQQQ permission
Attack permission
Moonshot permission
Vault state
Top candidates
Forbidden actions
Human review items
```

### Weekly Vault Review

```text
reports/A2_weekly_vault_review.md
```

내용:

```text
A2 vs QQQ excess
HWM
Vault trigger
Hard/Reload balances
Reload eligibility
```

### Codex Check

```text
reports/A2_codex_check.md
```

내용:

```text
look-ahead check
live/backtest separation
vault accounting
invariant check
secrets check
```

---

## 5. MiniPC Requirements

```text
sleep off
auto reboot recovery
cron or systemd timer
.env secrets only
Tailscale or remote access
daily health log
disk backup
timezone explicitly set
```

---

## 6. Suggested Runners

```text
engine/a2_daily_data_update.py
engine/a2_risk_dashboard.py
engine/a2_daily_war_plan.py
engine/a2_premarket_scanner.py
engine/a2_intraday_scanner.py
engine/a2_attack_executor_paper.py
engine/a2_eod_reconcile.py
engine/a2_profit_vault.py
engine/a2_dashboard.py
```

---

## 7. Fail-closed Conditions

```text
data stale
provider missing
ledger invariant broken
Vault accounting mismatch
unexpected negative cash
signals not shifted
API key missing
```

---

## 8. Completion Criteria

```text
Dashboard opens locally
Daily War Plan generated
NAV ledger append-only
Vault ledger append-only
cron/systemd status visible
health report written
```
