# 11 — TQ-DH: TQQQ Dip Harvester

## 1. 목적

TQ-DH는 “떨어지면 무조건 TQQQ 추가매수”를 대체한다.

```text
모든 dip을 사지 않는다.
Dip의 종류를 분류한다.
Reload Vault만 사용한다.
Hard Vault는 절대 사용하지 않는다.
구조적 붕괴에서는 TQQQ 매수를 금지한다.
회복 확인 시 QQQ → TQQQ 순서로 진입한다.
```

## 2. 이겨야 할 대상

TQ-DH는 아래보다 나아야 의미 있다.

```text
TQQQ buy-and-hold
TQQQ monthly DCA
TQQQ drawdown DCA
QQQ buy-and-hold
A2 base
```

평가:

```text
최종 NAV
MDD
회복기간
Vaulted Profit
TQQQ sleeve 손실
Reload Vault 사용 효율
```

## 3. Dip Type A — Liquidity Air Pocket

특징:

```text
QQQ drawdown -5% ~ -8%
VIX/VXN 단기 spike 후 둔화
Leadership basket 절반 이상 50일선 위
주도주 earnings/narrative 훼손 없음
credit stress 없음
```

행동:

```text
Reload Vault 25% → TQQQ
3거래일 후 recovery 확인 시 추가 Reload 25% 가능
```

## 4. Dip Type B — Growth Reset

특징:

```text
QQQ drawdown -10% ~ -15%
리더 일부 20/50일선 이탈
AI/빅테크 narrative 유지
VXN 높지만 안정화 시작
QQQ 5일 고점 회복 시도
```

행동:

```text
1차 Reload Vault 25% → QQQ
QQQ 10일 고점 회복 + Leadership YELLOW 이상 → TQQQ 25% reload
```

## 5. Dip Type C — Structural Break

특징:

```text
QQQ drawdown -20% 이상
QQQ 200일선 하회
Leadership RED
AI/반도체/빅테크 narrative RED
credit stress 확대
VIX/VXN 고공 유지
earnings guidance deterioration
```

행동:

```text
TQQQ 매수 금지
Reload Vault 사용 금지
Attack/Moonshot 신규 금지
Risk report만 생성
```

## 6. Dip Type D — Capitulation + Repair

특징:

```text
QQQ drawdown -20% 이상 이후
VIX/VXN peak 후 하락
QQQ 10일 고점 돌파
리더 5개 중 3개가 20일선 회복
breadth 회복
LLM narrative RED → YELLOW
```

행동:

```text
Reload Vault 25% → QQQ
3~5거래일 follow-through 확인
Reload Vault 25% → TQQQ
Hard Vault 사용 금지
```

## 7. 입력 데이터

```text
QQQ close/high/low/volume
TQQQ close/high/low/volume
QQQ 20/50/200일선
QQQ drawdown
VIX/VXN
QQQ realized volatility
Leadership basket 상태
Credit stress: HYG/IEF or HYG/SHY
AI/semiconductor narrative
Earnings guidance risk
LLM Narrative Risk
```

## 8. Reload 규칙

```text
Reload Vault만 사용
Hard Vault 사용 금지
1회 reload = Reload Vault 25%
연속 reload 간격 최소 3거래일
Reload 후 TQQQ sleeve MDD -15% 이상이면 추가 reload 금지
```

## 9. 단순 TQQQ 추가매수와의 차이

단순 DCA:

```text
떨어지면 산다
```

TQ-DH:

```text
왜 떨어졌는지 분류한다
일시적 dip이면 TQQQ
성장주 조정이면 QQQ 먼저
구조적 붕괴면 금지
복구 확인 후 단계적 reload
```

## 10. 구현 파일

```text
engine/a2_tq_dh.py
outputs/a2_live/tq_dh_signals.csv
reports/A2_tq_dh_report.md
```
