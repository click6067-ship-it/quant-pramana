# PRAMANA A2 — Dynamic Allocator and Mapping Engine

## 0. 핵심

LLM은 상태를 판정한다. 비중은 mapping engine이 변경한다.

---

## 1. Base Allocation

```yaml
base_weights:
  qqq: 0.35
  tqqq: 0.35
  attack: 0.10
  moonshot: 0.10
  vault: 0.10
```

---

## 2. Ranges

```yaml
ranges:
  qqq: [0.25, 0.45]
  tqqq: [0.15, 0.45]
  attack: [0.00, 0.20]
  moonshot: [0.00, 0.15]
  vault: [0.05, 0.30]
```

---

## 3. Change Limits

```yaml
change_limits:
  single_step_pct: 0.05
  max_daily_change_pct: 0.05
  max_weekly_change_pct: 0.10
  crash_lockout_override: true
```

---

## 4. Mode Mapping

### Base

```text
35/35/10/10/10
```

### Berserker

조건:

```text
Leadership GREEN
TQQQ Decay GREEN
Market Stress GREEN/YELLOW
LLM Narrative GREEN
A2 excess vs QQQ positive
Attack 최근 성과 양호
```

목표:

```text
QQQ 30
TQQQ 45
Attack 15
Moonshot 5
Vault 5
```

### Red King

```text
QQQ 40
TQQQ 25
Attack 5
Moonshot 5
Vault 25
```

### Attack Lockout / Booster Add Ban

기존 TQQQ 자동매도 없음.

```text
TQQQ 증액 금지
Attack 신규 금지
Moonshot 신규 금지
Reload 금지
Vault 우선
```

### Crash Lockout

```text
QQQ 45
TQQQ 0~10
Attack 0
Moonshot 0
Vault 45~55
사람 리뷰 필요
```

주의: Crash Lockout만 실제 비중 축소 가능. 그 외에는 신규/증액 금지 중심.

---

## 5. State to Action Example

```text
TQQQ state GREEN → target +5%p 가능
TQQQ state YELLOW → 유지
TQQQ state RED → 증액 금지, 필요 시 -5%p 후보

Attack state GREEN → +5%p 가능
Attack state YELLOW → 유지
Attack state RED → 신규진입 금지

Vault state ACCUMULATE → Vault +5%p
Vault state RELOAD_ALLOWED → Reload Vault 일부 사용 가능
```

---

## 6. Output

`outputs/a2_live/target_weights.json`

```json
{
  "date": "YYYY-MM-DD",
  "mode": "BASE",
  "target_weights": {
    "qqq": 0.35,
    "tqqq": 0.35,
    "attack": 0.10,
    "moonshot": 0.10,
    "vault": 0.10
  },
  "reason": "mapping from states",
  "states": {}
}
```

---

## 7. Implementation Files

```text
config/a2_state_mapping.yaml
engine/a2_dynamic_allocator.py
```

---

## 8. Completion Criteria

```text
LLM output never contains numeric target weights
Mapping engine produces target_weights
Change limits enforced
Hard Vault excluded from target allocation
All changes logged in allocation_log.csv
```
