# PRAMANA A2 — TQ-DH: TQQQ Dip Harvester v0.1

## 0. 목적

단순한 TQQQ 낙폭매수는 강세장에서는 강하지만, 긴 하락장·횡보 고변동장에서는 계좌를 크게 훼손할 수 있다.

TQ-DH의 목표는 다음이다.

```text
떨어지면 무조건 TQQQ를 사지 않는다.
Dip의 종류를 분류한다.
Reload Vault만 사용한다.
Hard Vault는 절대 사용하지 않는다.
구조적 붕괴에서는 TQQQ 매수를 금지한다.
회복 확인 시 QQQ → TQQQ 순서로 진입한다.
```

---

## 1. TQ-DH는 무엇을 이겨야 하나

TQ-DH는 다음보다 나아야 의미가 있다.

```text
1. TQQQ buy-and-hold
2. TQQQ monthly DCA
3. TQQQ drawdown DCA
4. QQQ buy-and-hold
5. A2 base
```

최종 NAV만 보면 TQQQ buy-and-hold가 이길 수 있다.

따라서 평가 기준은 다음을 모두 본다.

```text
최종 NAV
MDD
회복기간
Vaulted Profit
TQQQ sleeve 손실
Reload Vault 사용 효율
```

---

## 2. Dip 분류 체계

### Type A — Liquidity Air Pocket

일시적 유동성 충격.

특징:

```text
QQQ drawdown -5% ~ -8%
VIX/VXN 단기 spike 후 둔화
Leadership basket의 절반 이상은 50일선 위
주도주 earnings/narrative 훼손 없음
credit stress 없음
```

행동:

```text
Reload Vault 25% → TQQQ
3거래일 후 recovery 확인 시 추가 Reload 25% 가능
```

---

### Type B — Growth Reset

성장주 조정.

특징:

```text
QQQ drawdown -10% ~ -15%
리더 일부 20/50일선 이탈
AI/빅테크 narrative는 유지
VXN 높지만 안정화 시작
QQQ가 5일 고점 회복 시도
```

행동:

```text
1차 Reload Vault 25% → QQQ
QQQ가 10일 고점 회복 + Leadership YELLOW 이상 → TQQQ 25% reload
```

---

### Type C — Structural Break

진짜 위험한 하락.

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

---

### Type D — Capitulation + Repair

폭락 후 복구 시작.

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

---

## 3. TQ-DH 입력 데이터

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

---

## 4. Reload 사용 규칙

```text
Reload Vault만 사용.
Hard Vault 사용 금지.
1회 reload = Reload Vault의 25%.
연속 reload 간격 최소 3거래일.
Reload 후 TQQQ sleeve MDD -15% 이상이면 추가 reload 금지.
```

---

## 5. TQ-DH와 기존 TQQQ 추가매수의 차이

단순 TQQQ 추가매수:

```text
떨어지면 산다.
```

TQ-DH:

```text
왜 떨어졌는지 분류한다.
일시적 충격이면 TQQQ.
성장주 조정이면 QQQ 먼저, 확인 후 TQQQ.
구조적 붕괴면 아무것도 안 산다.
복구 확인 후 단계적으로 Reload.
```

---

## 6. TQ-DH 의사결정 테이블

| Dip Type | QQQ | TQQQ | Attack | Moonshot | Vault |
|---|---:|---:|---:|---:|---|
| Type A | 유지 | Reload 25% 가능 | 제한 허용 | 신규 금지 | Reload 일부 사용 |
| Type B | Reload 25% | 확인 후 Reload 25% | 축소 | 신규 금지 | Reload 일부 사용 |
| Type C | 유지/축소 검토 | 매수 금지 | 금지 | 금지 | Hard/Reload 보존 |
| Type D | Reload 25% | follow-through 후 25% | 재개 후보 | thesis only | Reload 일부 사용 |

---

## 7. TQ-DH 벤치마크

반드시 같이 실행한다.

```text
QQQ buy-and-hold
TQQQ buy-and-hold
TQQQ monthly DCA
TQQQ drawdown DCA
A2 base 35/35/10/10/10
A2 without TQ-DH
A2 with TQ-DH
```

---

## 8. 성공 조건

```text
A2 with TQ-DH가 A2 without TQ-DH보다
- final NAV가 같거나 높고
- MDD가 낮고
- 회복기간이 짧고
- Vaulted Profit이 높아야 함.
```

TQQQ buy-and-hold보다 최종 NAV가 낮아도 괜찮다.  
대신 MDD와 Vaulted Profit에서 보상이 있어야 한다.

---

## 9. 실패 조건

```text
TQ-DH가 TQQQ drawdown DCA보다 final NAV/MDD 모두 열위
Reload가 대부분 Type C에서 발생
Hard Vault를 사용해야만 성과가 나옴
Reload 후 손실이 반복됨
A2가 QQQ 대비 큰 언더퍼폼을 확대
```

---

## 10. 구현 파일

```text
engine/a2_tq_dh.py
config/a2_tq_dh.yaml
outputs/a2_live/tq_dh_decisions.csv
reports/A2_tq_dh_weekly_review.md
```

필수 컬럼:

```text
date
qqq_drawdown
vix_vxn_state
leadership_state
narrative_state
dip_type
action
reload_amount
asset_used
post_reload_return_5d
post_reload_return_20d
```
