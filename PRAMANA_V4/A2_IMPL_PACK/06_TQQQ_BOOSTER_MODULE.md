# PRAMANA A2 — TQQQ Booster Module

## 0. 정의

TQQQ는 Core가 아니다. Booster다.

```text
TQQQ = QQQ의 일일 3배 레버 베타
TQQQ = 알파 아님
TQQQ = 상승장 폭발력과 회복불능 손실 가능성을 동시에 가진 위험 엔진
```

---

## 1. 기본 비중

```text
Base: 35%
Range: 15~45%
Absolute max: 45% unless manual override
```

---

## 2. TQQQ 증액 허용 조건

모두 충족하거나 mapping score가 GREEN일 때만.

```text
Leadership Risk GREEN
TQQQ Decay GREEN
Market Stress GREEN/YELLOW
LLM Narrative GREEN/YELLOW
QQQ 20일선 위
QQQ 50일선 위
QQQ 20일 수익률 양수
A2 drawdown -15% 이내
Effective Beta RED 아님
```

---

## 3. TQQQ 증액 금지 조건

하나라도 강하게 발생하면 증액 금지.

```text
Leadership RED
TQQQ Decay Zone
Market Stress RED
QQQ 20/50일선 동시 하회
A2 MDD -20% 초과
VIX/VXN 급등
LLM Narrative RED
AI/빅테크 narrative 훼손
```

---

## 4. TQQQ 축소 후보 조건

기본은 자동매도 금지. 아래는 파산 방지용 축소 후보.

```text
A2 전체 MDD -30%
TQQQ sleeve MDD -35%
Leadership RED 10거래일 지속
TQQQ Decay Zone 20거래일 지속
QQQ 200일선 하회 + VXN 급등 + 리더십 붕괴
```

축소 방식:

```text
1회 -5%p
하루 최대 -10%p
주간 최대 -15%p
```

---

## 5. TQQQ Decay Meter

목적: TQQQ가 돈값을 못 하는 횡보 고변동 구간을 감지한다.

### Inputs

```text
QQQ 20d return
QQQ 20d realized volatility
QQQ 20d high-low range
TQQQ 20d return
realized_multiple = TQQQ_20d_return / QQQ_20d_return, if QQQ return nonzero
VXN / implied vol proxy
```

### Decay Zone

```text
QQQ 20d return between -3% and +3%
AND QQQ realized vol elevated
AND high-low range elevated
```

### Booster Rent

```text
TQQQ 20d return < 2.3 × QQQ 20d return
AND QQQ 20d return between -3% and +3%
AND realized vol elevated
```

### Actions

```text
TQQQ 증액 금지
Berserker 금지
Vault 우선
Attack size 축소
```

---

## 6. Dynamic Mapping

```text
TQQQ state GREEN → target +5%p 가능
TQQQ state YELLOW → 유지
TQQQ state RED → target -5%p 후보 또는 증액 금지
```

LLM은 GREEN/YELLOW/RED만 제공. 숫자는 mapping engine이 결정.

---

## 7. Output

```text
tqqq_value
tqqq_target_weight
tqqq_actual_weight
tqqq_contribution
tqqq_decay_state
booster_rent_flag
tqqq_add_permission
```

---

## 8. Implementation Files

```text
engine/a2_tqqq_module.py
engine/a2_tqqq_decay.py
engine/a2_dynamic_allocator.py
```
