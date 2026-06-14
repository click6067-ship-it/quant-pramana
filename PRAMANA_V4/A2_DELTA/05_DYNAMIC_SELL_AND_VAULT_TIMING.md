# PRAMANA A2 — Dynamic Sell & Vault Timing v0.1

## 0. 목적

Vault는 단순히 “QQQ보다 +4%p 먹으면 일부 빼기”가 아니다.

A2에서 Vault는 다음 역할을 한다.

```text
1. 평가익을 실제 내 돈으로 잠근다.
2. TQQQ/Attack/Moonshot 수익을 전부 토해내지 않게 한다.
3. Reload Vault를 통해 좋은 dip에서 제한적으로 재투입한다.
4. 매도 타이밍을 시장 예측이 아니라 수익/위험 상태 기반으로 만든다.
```

---

## 1. Vault In — 빼는 알고리즘

Vault In은 다음 세 조건 중 최소 2개 이상이 충족될 때 작동한다.

### 조건 A — QQQ 대비 초과수익

```text
A2_excess_HWM ≥ +4%p
A2_excess_HWM ≥ +8%p
A2_excess_HWM ≥ +12%p
```

### 조건 B — 절대 수익 상태

```text
A2 NAV가 inception 대비 수익 상태
또는 A2 NAV가 최근 active HWM 근처
```

### 조건 C — 위험 신호 악화

```text
Leadership YELLOW/RED
TQQQ Decay Zone
Market Stress YELLOW/RED
LLM Narrative YELLOW/RED
TQQQ Booster Rent flag
```

핵심:

```text
A2가 QQQ보다 덜 잃었다고 Vault 작동 금지.
실제로 이긴 돈이 있을 때만 빼기.
```

---

## 2. Vault In 강도

기본 규칙:

| 상황 | Vault 이동률 |
|---|---:|
| excess +4%p, 위험 GREEN | 신규 초과수익분의 10~25% |
| excess +4%p, 위험 YELLOW | 신규 초과수익분의 25% |
| excess +8%p, 위험 YELLOW/RED | 신규 초과수익분의 25~50% |
| excess +12%p 이상, 위험 RED | 신규 초과수익분의 50% |
| TQQQ sleeve +50% 이상, Decay YELLOW/RED | TQQQ 수익분의 25~33% |
| Moonshot 2배 | 원금 회수 |
| Moonshot 3배 | 절반 Vault |

---

## 3. Vault source 우선순위

```text
1. TQQQ realized profit
2. Attack realized profit
3. Moonshot realized profit
4. QQQ profit
```

손실 중인 sleeve에서 Vault 이동 금지.

---

## 4. Hard Vault / Reload Vault

Vault 유입 분리:

```text
Hard Vault = 70%
Reload Vault = 30%
```

Hard Vault:

```text
절대 재투입 금지
A2 공격자금에서 제외
가능하면 별도 계좌/별도 ETF/별도 브로커
```

Reload Vault:

```text
TQ-DH와 Attack A급 후보에만 사용 가능
한 번에 Reload Vault의 25% 이하
월 1회 이하 기본
```

---

## 5. Vault Out — 꺼내 쓰는 알고리즘

Reload Vault만 사용 가능.

Vault Out 조건:

```text
Leadership GREEN
TQQQ Decay GREEN
Market Stress not RED
LLM Narrative GREEN/YELLOW
QQQ 20일선 회복
A2 drawdown 회복 중
A급 Attack 후보 또는 TQ-DH Type A/D 발생
```

Reload 방식:

```text
Type A Liquidity Air Pocket → Reload 25% to TQQQ
Type B Growth Reset → Reload 25% to QQQ first, then TQQQ on confirmation
Type C Structural Break → Reload 금지
Type D Capitulation + Repair → QQQ 먼저, follow-through 후 TQQQ
```

---

## 6. Dynamic Sell Timing — 5%p 단위

Vault In과 별도로, A2는 sleeve 자체를 5%p 단위로 줄일 수 있다.

### TQQQ Trim 후보

```text
Leadership RED
TQQQ Decay Zone 10거래일 이상
QQQ 20/50일선 동시 하회
TQQQ Booster Rent flag
A2 MDD -20% 초과
```

행동:

```text
TQQQ -5%p
Vault +5%p 또는 QQQ +5%p
```

### Attack Trim 후보

```text
Attack 연속 손실 3회
Leadership RED
Market Stress RED
NEG cluster 발생
```

행동:

```text
Attack -5%p
Vault +5%p
```

### Moonshot Trim 후보

```text
Moonshot thesis decay
판정일 경과
Hard NEG 발생
A2 regret budget breach
```

행동:

```text
Moonshot -5%p
Vault +5%p
```

---

## 7. Dynamic Add Timing — 5%p 단위

### TQQQ Add 후보

```text
Leadership GREEN
Decay GREEN
QQQ 20/50일선 위
Narrative GREEN/YELLOW
A2 MDD -15% 이내
TQ-DH Type A 또는 D
```

행동:

```text
TQQQ +5%p
Vault/QQQ -5%p
```

### Attack Add 후보

```text
Attack 최근 5개 중 3개 성공
A급 catalyst 다수
Leadership GREEN/YELLOW
Market Stress not RED
```

행동:

```text
Attack +5%p
Vault -5%p 또는 QQQ -5%p
```

### Moonshot Add 후보

```text
M1 thesis 존재
Reward/Risk ≥ 3:1
판정일 명확
Hard NEG 없음
Moonshot drawdown 없음
```

행동:

```text
Moonshot +5%p
Vault/QQQ -5%p
```

---

## 8. 매도와 Vault의 차이

매도:

```text
sleeve 비중을 줄인다.
위험노출을 낮춘다.
```

Vault:

```text
이미 번 돈을 공격자금에서 제거한다.
Hard/Reload로 분리한다.
```

둘을 혼동하지 않는다.

---

## 9. 구현 체크리스트

```text
[ ] Vault In은 실제 ledger에 기록
[ ] Vault Out은 Reload Vault에서만
[ ] Hard Vault는 코드상 재투입 불가
[ ] 5%p trim/add는 target weights에 반영
[ ] LLM은 상태만 제공
[ ] mapping engine이 실제 변경
[ ] 매도/trim과 Vault 이동은 별도 이벤트로 기록
[ ] 대시보드에 Vault In/Out/Trim/Add 구분 표시
```

---

## 10. 구현 파일

```text
engine/a2_dynamic_sell.py
engine/a2_profit_vault.py
config/a2_vault_rules.yaml
outputs/a2_live/vault_events.csv
outputs/a2_live/sleeve_adjustments.csv
reports/A2_weekly_vault_review.md
```
