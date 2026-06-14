# PRAMANA A2 — Ledger, Accounting, and Benchmarks

## 0. 핵심

A2의 수치는 회계가 맞아야 의미가 있다. Codex STOP이 잡은 가장 큰 문제는 live/backtest 혼동과 Vault 미회계였다.

---

## 1. Live vs Backtest

### Live ledger

```text
outputs/a2_live/nav_log.csv
outputs/a2_live/allocation_log.csv
outputs/a2_live/vault_ledger.csv
```

live는 inception 이후만.

### Backtest panel

```text
outputs/a2_backtest/backtest_panel.csv
outputs/a2_backtest/multi_anchor.csv
```

backtest는 historical simulation.

Dashboard에서 두 섹션을 분리한다.

---

## 2. NAV Accounting

```text
TOTAL_NAV = QQQ_value + TQQQ_value + Attack_value + Moonshot_value + Cash + Hard_Vault + Reload_Vault
```

```text
ACTIVE_NAV = QQQ_value + TQQQ_value + Attack_value + Moonshot_value + Cash + eligible_Reload_Vault
```

Hard Vault는 active capital 아님.

---

## 3. Empty Sleeve Accounting

Attack/Moonshot이 비어 있으면 해당 금액은 cash로 계산한다.

```text
Attack empty → Attack_cash
Moonshot empty → Moonshot_cash
```

대시보드에 표시:

```text
A2 is currently beta-only if Attack/Moonshot empty
```

---

## 4. Benchmarks

필수 비교:

```text
QQQ 100%
SPY 100%
TQQQ 100% (reference only)
A2-Q
A2-T
naive beta book
synthetic QQQ 1.4x proxy
V7 survival core
```

### naive beta book

```text
QQQ 35
TQQQ 35
Cash 30
```

목적:

```text
A2가 단순 QQQ/TQQQ 고정 book보다 나은지 확인
```

---

## 5. Attribution

```text
QQQ contribution
TQQQ contribution
Attack contribution
Moonshot contribution
Vaulted profit
Dynamic allocator contribution
Naive beta gap
```

A2가 QQQ를 이겼더라도 naive beta book을 못 이기면 동적 조절 가치는 미확정.

---

## 6. Look-ahead Guard

```text
All daily states must be shifted by 1 trading day before applying returns.
```

예:

```python
weights_t = target_weights.shift(1)
book_return_t = weights_t * returns_t
```

금지:

```python
weights_t = f(close_t)
book_return_t = weights_t * returns_t
```

---

## 7. Multi-anchor Dashboard

기간:

```text
3년
12개월
6개월
3개월
live inception
```

표시:

```text
계좌금액
누적수익
MDD
excess vs QQQ
Vaulted Profit
active NAV
vault-adjusted NAV
```

---

## 8. Completion Criteria

```text
live NAV and backtest NAV separated
Vault reflected in NAV/accounting
Attack/Moonshot empty cash counted
Naive benchmark generated
next-bar applied
attribution sums to total return within tolerance
```
