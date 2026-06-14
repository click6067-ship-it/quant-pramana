# PRAMANA A2 — Profit Vault Module

## 0. 정의

Profit Vault는 A2의 핵심이다.

```text
목적: 평가익을 실제 내 돈으로 잠그기.
```

Vault는 표시용 숫자가 아니다. 실제 active capital에서 빠져야 한다.

---

## 1. 비중

```text
Base: 10%
Range: 5~30%
```

---

## 2. Vault Types

```text
Hard Vault = 절대 재투입 금지
Reload Vault = 조건부 재장전 가능
```

Vault 유입:

```text
70% → Hard Vault
30% → Reload Vault
```

---

## 3. Benchmark Vault Rule

```text
A2_excess = A2_NAV_return - QQQ_return
A2_excess_HWM = max(previous_HWM, A2_excess)
```

작동 조건:

```text
1. 새로운 A2_excess_HWM 발생
2. A2 absolute NAV가 수익 상태
3. 주 1회 제한 통과
4. 월간 이동량 ≤ 전체 NAV의 10%
```

금지:

```text
QQQ보다 덜 잃은 것만으로 Vault 발동 금지
```

---

## 4. Vault Trigger

| 조건 | 행동 |
|---|---|
| excess HWM ≥ +4%p | 신규 초과수익분의 25% Vault |
| excess HWM ≥ +8%p | 신규 초과수익분의 추가 25% Vault |
| excess HWM ≥ +12%p | 신규 초과수익분의 50% Vault |

---

## 5. Source Priority

Vault 이동 source:

```text
1. TQQQ realized profit
2. Attack realized profit
3. Moonshot realized profit
4. QQQ realized profit
```

손실 중인 sleeve에서 Vault 이동 금지.

---

## 6. Vault Ledger Schema

`positions/vault.json`

```json
{
  "hard_vault": 0,
  "reload_vault": 0,
  "last_vault_date": null,
  "month_vault_total": 0,
  "a2_excess_hwm": 0,
  "events": []
}
```

`outputs/a2_live/vault_ledger.csv` columns:

```text
date,event_type,source_sleeve,amount,total_hard,total_reload,reason,a2_excess,a2_nav,qqq_nav
```

---

## 7. Reload Vault Out

Reload 조건:

```text
Leadership GREEN
TQQQ Decay GREEN
Market Stress not RED
QQQ 20일선 회복
A2 drawdown 회복 중
Attack A급 후보 존재
```

사용:

```text
한 번에 Reload Vault의 25%만
월 1회 이하
Hard Vault 사용 금지
```

---

## 8. Moonshot Vault

```text
Moonshot 2배 → 원금 회수
Moonshot 3배 → 절반 Vault
Moonshot thesis 깨짐 → 즉시 종료
```

---

## 9. Dashboard Fields

```text
Hard Vault balance
Reload Vault balance
Vaulted Profit total
Active NAV
Vault-adjusted NAV
A2 excess HWM
Vault trigger status
Weekly vault eligibility
Monthly vault limit usage
Reload eligibility
```

---

## 10. Completion Criteria

```text
Vault 이동 시 active capital 감소
Hard/Reload ledger append-only 기록
Vault-adjusted NAV와 active NAV 분리
주1회/월10% 제한 코드 enforcement
Hard Vault 재투입 불가
```

---

## 11. Implementation Files

```text
engine/a2_profit_vault.py
positions/vault.json
outputs/a2_live/vault_ledger.csv
reports/A2_weekly_vault_review.md
```
