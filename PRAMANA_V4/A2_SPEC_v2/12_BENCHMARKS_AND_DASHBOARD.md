# 12 — Benchmarks, Metrics, Dashboard

## 1. 필수 벤치마크

A2는 QQQ만 이기면 부족하다.

필수 비교:

```text
QQQ buy-and-hold
SPY buy-and-hold
TQQQ buy-and-hold
V7 survival core
A2-Q
A2-T
naive QQQ35/TQQQ35/Cash30
synthetic QQQ 1.4x
TQQQ monthly DCA
TQQQ drawdown DCA
TQ-DH
```

## 2. 구간

```text
3년
12개월
6개월
3개월
live-only since inception
```

## 3. 지표

```text
Total NAV
Total return
MDD
Recovery time
A2 vs QQQ excess
A2 vs naive excess
Vaulted Profit
Vault-adjusted NAV
Hard Vault
Reload Vault
Attack contribution
Moonshot contribution
TQQQ contribution
Dynamic allocator contribution
TQ-DH contribution
```

## 4. Dashboard 필수 항목

```text
A2 active NAV
A2 vault-adjusted NAV
QQQ NAV
SPY NAV
TQQQ NAV
V7 NAV
naive beta NAV
A2-Q vs A2-T
A2 vs QQQ excess
Excess HWM
Vault trigger status
Hard Vault balance
Reload Vault balance
Effective QQQ beta
TQQQ Decay Meter
Booster Rent
Leadership Risk
Market Stress
LLM Narrative State
Attack tokens
Attack candidates
Moonshot draft board
NEG filing flags
Theme concentration
TQ-DH dip type
TQ-DH reload recommendation
```

## 5. 성공 정의

```text
A2 total NAV > QQQ
A2 vault-adjusted NAV > QQQ
Vaulted Profit > 0
A2 > naive beta book
게임 지속 가능
```

## 6. 주의

A2가 QQQ를 이겼지만 naive를 못 이기면:

```text
TQQQ 덕분이지, A2 운영규칙의 부가가치는 미확정.
```

A2가 TQQQ를 못 이기는 것은 당연할 수 있음. A2는 TQQQ보다 안정성과 Vault를 추구한다.

## 7. 대시보드 경고 문구

대시보드 상단에 항상 표시:

```text
A2 is not verified alpha.
A2 is a high-risk QQQ/TQQQ convex book with paper-only Attack/Moonshot optionality.
```
