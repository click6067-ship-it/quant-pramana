# 04 — Allocation & Dynamic Mapping Engine

## 1. 기본 비중

```yaml
base_allocation:
  QQQ: 0.35
  TQQQ: 0.35
  Attack: 0.10
  Moonshot: 0.10
  Vault: 0.10
```

## 2. 허용 범위

```yaml
ranges:
  QQQ: [0.25, 0.45]
  TQQQ: [0.15, 0.45]
  Attack: [0.00, 0.20]
  Moonshot: [0.00, 0.15]
  Vault: [0.05, 0.30]
```

## 3. 변경 단위

```yaml
change_unit: 0.05
max_daily_change: 0.05
max_weekly_change: 0.10
```

## 4. LLM Council 역할

LLM은 상태만 판정한다.

```text
GREEN / YELLOW / RED
ACCUMULATE / HOLD / RELOAD_ALLOWED
OPEN / HOLD_ONLY / LOCKED
```

LLM은 아래를 하지 않는다.

```text
비중 숫자 직접 결정
매수/매도 명령
성공확률 확정
포지션 사이징 확정
```

## 5. Mapping Engine

상태를 target weight로 바꾸는 것은 code/config가 한다.

### TQQQ state

```text
GREEN  → TQQQ +5%p 가능
YELLOW → 유지
RED    → 증액 금지 또는 -5%p 후보
```

### Attack state

```text
GREEN  → Attack +5%p 가능
YELLOW → 유지 또는 half size
RED    → 신규진입 금지
```

### Moonshot state

```text
OPEN      → thesis 있는 후보만 가능
HOLD_ONLY → 기존만 유지, 신규 금지
LOCKED    → 신규 금지, 기존 thesis 재검토
```

### Vault state

```text
ACCUMULATE     → Vault +5%p 후보
HOLD           → 유지
RELOAD_ALLOWED → Reload Vault 일부 사용 가능
```

## 6. Mode Labels

```text
Base Mode
Berserker Mode
Red King Mode
Attack Lockout / Booster Add Ban
Crash Lockout
```

Risk-Off라는 이름은 사용하지 않는다. 마켓타이밍 자동매도로 오해되기 때문이다.

## 7. Attack Lockout / Booster Add Ban

의미:

```text
기존 QQQ/TQQQ 자동매도 아님
TQQQ 신규 증액 금지
Attack 신규진입 금지
Moonshot 신규진입 금지
Reload Vault 사용 금지
Profit Vault 우선 검토
```

## 8. Crash Lockout

조건:

```text
A2 전체 MDD -30%
TQQQ sleeve MDD -35%
Leadership RED 10거래일 지속
TQQQ Decay Zone 20거래일 지속
QQQ 200일선 하회 + VXN 급등 + leaders breakdown
```

행동:

```text
TQQQ 신규매수 0
Attack/Moonshot 신규 0
사람 리뷰 필요
자동매도는 manual decision flag로만 표시
```

## 9. next-bar 적용

모든 상태 판정은 t일 계산, t+1일 적용.

```python
state_today = compute_state(data_until_t)
target_weight_tomorrow = mapping(state_today)
```

same-day return에 same-day state를 적용하지 않는다.
