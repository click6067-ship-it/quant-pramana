# PRAMANA A2 — Delta Master Patch v0.1

## 0. 이 문서의 역할

기존 `PRAMANA_A2_Convex_Raider_Book_FINAL_v1.md`의 방향은 유지한다.

기존 핵심:

```text
A2 = QQQ/TQQQ 성장 베타를 의식적으로 증폭하고,
Attack/Moonshot으로 비대칭을 붙이며,
Profit Vault와 Risk Dashboard로 자멸을 줄이는 고위험 convex book.
```

이번 delta는 기존 A2 설계에서 부족했던 다음 네 축을 보강한다.

```text
A. Attack/Moonshot blind/PIT backtest 설계
B. TQ-DH — TQQQ Dip Harvester 추가
C. 벤치마크 체계 확장
D. 동적 매도/Vault timing 알고리즘 추가
```

---

## 1. 최신 기본 비중

Base allocation은 다음으로 고정한다.

| Sleeve | 비중 | 역할 |
|---|---:|---|
| QQQ Core | 35% | 성장 베타 기본 노출 |
| TQQQ Booster | 35% | 상승장 폭발력, 레버 베타 |
| Attack | 10% | 분봉 급등주, momentum, catalyst day trade |
| Moonshot | 10% | 큰 비대칭 thesis bet |
| Vault | 10% | 수익 회수, reload reserve, 생존 |

실질 QQQ beta 근사:

```text
QQQ 35% × 1 = 35%
TQQQ 35% × 3 = 105%
합계 ≈ QQQ beta 140%
```

Attack/Moonshot이 성장주·AI·반도체에 몰리면 실질 성장주 beta는 1.4x보다 커질 수 있다.

---

## 2. 동적 비중 조절

사용자는 각 sleeve 비중을 10%p 내외로 유동화하길 원하지만, 구현은 더 보수적으로 시작한다.

```text
기본 변경 단위: 5%p
일일 최대 변경: 5%p
주간 최대 변경: 10%p
```

허용 범위:

| Sleeve | 범위 |
|---|---:|
| QQQ | 25~45% |
| TQQQ | 15~45% |
| Attack | 0~20% |
| Moonshot | 0~15% |
| Vault | 5~30% |

LLM Council은 숫자를 직접 결정하지 않는다.

```text
LLM 출력 = GREEN / YELLOW / RED / ACCUMULATE / RELOAD_ALLOWED
Rule engine = 실제 비중 변경
```

---

## 3. 기존 폐기 전략의 역할 변경

폐기 전략은 원래 역할 그대로 되살리지 않는다. 역할을 바꿔 A2 부품으로 재활용한다.

| 기존 전략/도구 | 기존 판정 | A2 내 새 역할 |
|---|---|---|
| ORB/VWAP/RVOL | 단독 setup DEAD | Attack confirmation sensor |
| momentum broad | standalone 약함 | 단기 strength confirmation |
| quality broad | standalone 실패 | 품질 하한선/지뢰 제거 필터 |
| event positive 8-K | 매수 OOS 실패 | catalyst radar |
| NEG filing | 회피 신호 일관 | hard/soft veto |
| trend/risk score | core timing 실패 | TQQQ/Attack/Moonshot permission input |
| LETF convex | 알파 아님 | TQQQ booster 관리 참고 |

---

## 4. 이번 delta에서 새로 추가되는 핵심

### 4.1 Blind/PIT Simulation

Attack/Moonshot은 과거 시뮬레이션 시 반드시 “그 시점에 알 수 있었던 정보만” 사용한다.

```text
decision_time = 전략이 결정을 내리는 시각
available_at <= decision_time 인 데이터만 사용
```

### 4.2 TQ-DH — TQQQ Dip Harvester

단순히 “떨어지면 TQQQ 추가매수”가 아니라 dip을 네 종류로 분류한다.

```text
A. Liquidity Air Pocket
B. Growth Reset
C. Structural Break
D. Capitulation + Repair
```

### 4.3 Dynamic Sell / Vault Timing

Vault는 단순 고정 규칙이 아니라 수익회수 alpha-timing engine이다.

```text
Vault In = 이겼고 위험이 커질 때 수익 회수
Vault Out = 위험이 줄고 기회가 확인될 때 Reload Vault 일부 사용
```

### 4.4 벤치마크 확장

A2는 QQQ만 이기면 안 된다. 다음도 같이 비교한다.

```text
QQQ buy-and-hold
SPY buy-and-hold
TQQQ buy-and-hold
naive QQQ/TQQQ beta book
A2-Q
A2-T
TQQQ monthly DCA
TQQQ drawdown DCA
TQ-DH
V7 survival core
```

---

## 5. 수정 후 절대 금지

```text
look-ahead contaminated data 사용
LLM이 직접 비중 숫자 결정
Hard Vault 재투입
TQQQ를 alpha라고 부르기
Attack/Moonshot을 thesis 없이 진입
분봉 proxy 결과를 실전 검증으로 포장
Vault를 표시용으로만 두기
backtest와 live ledger를 혼동
```

---

## 6. 구현 목표

이번 delta 구현 완료 후 A2는 다음 상태가 되어야 한다.

```text
1. A2 35/35/10/10/10 설정 반영.
2. Attack/Moonshot backtest는 blind/PIT path만 허용.
3. TQ-DH 모듈이 Reload Vault 사용 여부를 결정.
4. Vault In/Out이 실제 ledger로 작동.
5. A2 결과가 확장 벤치마크들과 비교됨.
6. LLM Council은 상태만 판정하고 mapping engine이 비중 변경.
```
