# 01 — A2 Master Specification v2.0

## 1. 정체성

**PRAMANA A2 — Convex Raider Book v2**는 안정적인 검증 알파 시스템이 아니다.

A2는 다음 전제를 받아들인다.

```text
1. 공개 정량 데이터로 검증된 반복 알파는 거의 발견되지 않았다.
2. QQQ/SPY를 안정적으로 위험조정 초과하는 쉬운 알파는 없다.
3. 수익을 극대화하려면 위험을 회피하는 게 아니라 의식적으로 사야 한다.
4. 다만 위험을 산 뒤, 수익이 나면 Vault로 빼서 계좌 밖에 잠가야 한다.
5. A2는 PAPER only이며 실자본 권한은 없다.
```

## 2. 최신 기본 비중

| Sleeve | 기본 비중 | 허용 범위 | 역할 |
|---|---:|---:|---|
| QQQ Core | 35% | 25~45% | 성장 베타 기본 노출 |
| TQQQ Booster | 35% | 15~45% | 상승장 폭발력·레버 베타 |
| Attack | 10% | 0~20% | 급등주·모멘텀·분봉 day trade |
| Moonshot | 10% | 0~15% | 큰 비대칭 thesis bet |
| Vault/Cash | 10% | 5~30% | 수익 회수·재장전·생존 |

기본 실질 QQQ beta 근사:

```text
QQQ 35% × 1 = 35%
TQQQ 35% × 3 = 105%
합계 ≈ QQQ beta 140%
```

Attack/Moonshot이 AI·반도체·성장주에 몰리면 실제 growth beta는 1.4x보다 커질 수 있다.

## 3. A2의 5대 모듈

| 모듈 | 역할 |
|---|---|
| QQQ Core | 기본 성장 베타 |
| TQQQ Booster | 레버 베타·convex growth engine |
| Attack | 당일/초단기 급등주·모멘텀 공격 |
| Moonshot | thesis 기반 비대칭 베팅 |
| Vault | 수익 회수·Reload 대기·생존 장치 |

## 4. A2의 성공 정의

A2는 Sharpe 우선 book이 아니다. 성공은 아래 3개를 동시에 본다.

```text
A2 total NAV > QQQ
Vaulted Profit > 0
큰 손실 후에도 게임 지속 가능
```

추가 확인:

```text
A2 > naive QQQ/TQQQ beta book?
A2-T > A2-Q?
Attack/Moonshot contribution > 0?
TQQQ contribution이 전부인가?
Vault-adjusted NAV가 QQQ보다 나은가?
```

## 5. 절대 금지

```text
TQQQ를 Core라고 부르기 금지
TQQQ를 Alpha라고 부르기 금지
A2를 검증된 알파 전략이라고 부르기 금지
LLM이 매수/매도 결정 금지
LLM이 비중 숫자 직접 결정 금지
LLM이 성공확률 확정 금지
same-day signal로 same-day return 적용 금지
backtest와 live ledger 혼동 금지
Vault를 표시용으로만 두기 금지
Hard Vault 재투입 금지
손실 중 물타기 금지
Moonshot thesis 없이 진입 금지
판정일 없는 Moonshot 금지
NEG filing 무시 금지
```

## 6. 중요한 라벨

```text
A2-Beta = QQQ/TQQQ/Vault 중심, Attack/Moonshot 없음 또는 비어 있음
A2-Full = A2-Beta + Attack + Moonshot 실제 ledger 포함
A2-Q = TQQQ 없는 QQQ 중심 공격형 book
A2-T = TQQQ 포함 공격형 book
Naive Beta = QQQ35/TQQQ35/Cash30 고정 book
TQ-DH = Reload Vault를 이용한 TQQQ dip harvesting module
```

## 7. 구현 핵심

Claude는 새 백테스트를 계속 만들지 말고, 먼저 **회계 가능한 book**을 만들어야 한다.

최소 구현 조건:

```text
1. 모든 sleeve는 ledger에 명확히 존재한다.
2. Vault는 active capital에서 실제 차감된다.
3. LLM은 상태만 판정한다.
4. 비중 변경은 mapping engine만 수행한다.
5. Attack/Moonshot은 별도 ledger와 closed trade 기록을 가진다.
6. A2 결과는 QQQ뿐 아니라 naive beta book과 비교한다.
```
