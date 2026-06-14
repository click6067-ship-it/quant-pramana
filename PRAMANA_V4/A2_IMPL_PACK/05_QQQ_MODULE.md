# PRAMANA A2 — QQQ Core Module

## 0. 정의

QQQ Core는 A2의 기본 성장 베타다. SPY는 A2 포트폴리오에서 퇴출하고, benchmark로만 유지한다.

---

## 1. 역할

```text
성장주/기술주/메가캡/AI/소프트웨어/네트워크효과 베타 노출
A2의 기준 엔진
TQQQ와 Attack/Moonshot의 위험 기준점
```

---

## 2. 기본 비중

```text
Base: 35%
Range: 25~45%
```

QQQ는 TQQQ보다 안정적인 성장 베타로 간주한다.

---

## 3. SPY 처리

```text
A2 portfolio에서는 SPY weight = 0
SPY는 secondary benchmark로 유지
```

SPY를 제거하는 이유:

```text
A2의 목적은 안정적 시장대표가 아니라 QQQ를 초과하는 공격형 성장 베타
SPY는 완충은 되지만 목표수익을 낮춘다
```

---

## 4. QQQ State Features

```text
QQQ close
QQQ 20/50/200 moving average
QQQ 20d return
QQQ 20d realized volatility
QQQ drawdown
QQQ gap-up/gap-down
QQQ high-volume down day
QQQ relative to SPY
```

---

## 5. QQQ 권한

QQQ는 core growth exposure이므로 TQQQ보다 덜 자주 줄인다.

```text
GREEN: 35~45%
YELLOW: 30~40%
RED: 25~35%
```

단, QQQ도 Crash Lockout에서는 축소 후보가 될 수 있다.

---

## 6. A2-Q Book

A2-Q는 TQQQ를 쓰지 않는 비교 book이다.

예시 구조:

```text
QQQ 55%
Attack 15%
Moonshot 15%
Vault 15%
```

목적:

```text
TQQQ를 쓴 A2-T가 정말로 A2-Q보다 나은지 비교
횡보장 TQQQ decay가 기대수익보다 큰지 확인
```

A2-Q는 반드시 대시보드에 표시한다.

---

## 7. Implementation Files

```text
engine/a2_qqq_module.py
config/a2_convex_raider.yaml
```

---

## 8. Output

```text
qqq_value
qqq_weight_actual
qqq_weight_target
qqq_return_contribution
qqq_state_features
```
