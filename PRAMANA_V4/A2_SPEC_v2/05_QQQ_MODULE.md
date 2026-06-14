# 05 — QQQ Core Module

## 1. 역할

QQQ는 A2의 기본 성장 베타다.

```text
SPY는 A2에서 퇴출.
QQQ는 벤치마크이자 기본 엔진.
```

## 2. 기본 비중

```text
Base: 35%
Range: 25~45%
```

## 3. QQQ Module 입력

```text
QQQ EOD close/high/low/volume
20/50/200일선
20일 realized vol
drawdown
gap-up/gap-down
relative strength vs SPY
```

## 4. QQQ 증감 원칙

QQQ는 TQQQ보다 안정적인 성장 노출이다.

```text
TQQQ Decay RED인데 성장 노출을 유지하고 싶으면 TQQQ 대신 QQQ.
TQ-DH Type B/Growth Reset에서는 먼저 QQQ reload 후 TQQQ 확인.
```

## 5. QQQ는 매도타이밍 엔진이 아니다

QQQ는 코어 노출이며, Risk Dashboard가 RED라고 자동으로 전부 팔지 않는다.

축소 후보:

```text
A2 Crash Lockout
전체 MDD -30%
QQQ 200일선 하회 + Leadership RED 장기화
사용자 manual review
```

## 6. 대시보드 표시

```text
QQQ weight actual/target
QQQ contribution
QQQ 20/50/200 state
QQQ drawdown
QQQ vs SPY relative strength
QQQ vs A2 excess
```
