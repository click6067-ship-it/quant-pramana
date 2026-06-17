# 06 — TQQQ Booster Module

## 1. 역할

TQQQ는 Core가 아니다. Booster다.

```text
TQQQ = QQQ 일일수익률 3배를 목표로 하는 레버 베타 도구.
TQQQ = 알파가 아님.
TQQQ = 강세장 폭발력 + 하락/횡보장 파괴 리스크.
```

## 2. 기본 비중

```text
Base: 35%
Range: 15~45%
Absolute experimental max: 50%
```

## 3. 증액 허용 조건

```text
Leadership Risk GREEN
TQQQ Decay Meter GREEN
Market Stress GREEN/YELLOW
LLM Narrative GREEN/YELLOW
QQQ 20일선 위
QQQ 50일선 위
A2 drawdown -15% 이내
Effective Beta RED 아님
NEG cluster 없음
```

## 4. 증액 금지 조건

```text
Leadership RED
TQQQ Decay Zone
Market Stress RED
A2 MDD -20% 초과
QQQ 20/50일선 동시 이탈
VIX/VXN 급등
big leaders high-volume down day 다수
LLM Narrative RED
```

## 5. 축소 후보 조건

기본은 자동매도 금지. 단 아래는 파산 방지 후보.

```text
A2 전체 MDD -30%
TQQQ sleeve MDD -35%
Leadership RED 10거래일 지속
TQQQ Decay Zone 20거래일 지속
QQQ 200일선 하회 + VXN 급등 + leaders breakdown
```

축소 제한:

```text
1회 -5%p
하루 최대 -10%p
```

## 6. TQQQ Decay Meter

Decay Zone 조건:

```text
QQQ 20일 수익률이 -3%~+3%
AND QQQ realized vol 상승
AND 20일 high-low range 확대
```

행동:

```text
TQQQ 증액 금지
Berserker 금지
Profit Vault 우선
Attack size 축소
```

## 7. Booster Rent Metric

TQQQ가 돈값을 못 하는지 본다.

```text
최근 20거래일:
TQQQ 수익률 < 2.3 × QQQ 수익률
AND QQQ 수익률 -3%~+3%
AND realized vol 높음
```

판정:

```text
Booster inefficiency flag
```

행동:

```text
증액 금지
Berserker 금지
Vault 우선
Attack 축소
```

## 8. 대시보드 표시

```text
TQQQ target/actual weight
TQQQ contribution
TQQQ sleeve MDD
Decay status
Booster Rent status
TQQQ vs QQQ realized multiple
TQQQ add permission
TQQQ trim candidate flag
```
