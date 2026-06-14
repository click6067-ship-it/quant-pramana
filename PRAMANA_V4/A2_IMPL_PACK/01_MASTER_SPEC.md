# PRAMANA A2 — Master Implementation Specification

## 0. 한 줄 정의

**PRAMANA A2 — Convex Raider Book**은 QQQ/TQQQ 성장 베타를 의식적으로 증폭하고, Attack/Moonshot으로 비대칭 수익을 노리며, Profit Vault와 Risk Dashboard로 토해내는 것을 줄이는 고위험 PAPER book이다.

A2는 검증된 안정 알파 시스템이 아니다. A2는 위험을 산다. 단, 위험을 무작정 사는 게 아니라 **위험 × 수익 × 확률**이 충분히 크다고 판단될 때만 실행하고, 수익은 Vault로 빼앗아 온다.

---

## 1. 기본 상태

```yaml
project: PRAMANA A2 Convex Raider
status: PAPER_ONLY
live_trading: false
initial_capital_krw: 100000000
portfolio_currency: KRW_display / USD_market
benchmark_primary: QQQ
benchmark_secondary: SPY
benchmark_beta: naive_QQQ_TQQQ_book
core_asset: QQQ
booster_asset: TQQQ
spy_in_portfolio: false
```

---

## 2. Base Allocation v2

| Sleeve | Base Weight | Range | Role |
|---|---:|---:|---|
| QQQ Core | 35% | 25~45% | 성장 베타 기본 노출 |
| TQQQ Booster | 35% | 15~45% | 상승장 폭발력, 레버 베타 |
| Attack | 10% | 0~20% | 급등주·모멘텀·분봉 당일 전략 |
| Moonshot | 10% | 0~15% | 큰 비대칭 thesis 베팅 |
| Vault/Cash | 10% | 5~30% | 수익 회수·재장전 대기금 |

기본 실질 QQQ beta:

```text
QQQ 35% × 1 = 35%
TQQQ 35% × 3 = 105%
기본 beta ≈ 140%
```

Attack/Moonshot이 성장주·AI·반도체에 몰리면 실질 beta는 더 커질 수 있다.

---

## 3. A2-Q / A2-T 동시 운용

A2는 반드시 두 버전을 동시에 추적한다.

```text
A2-T = QQQ + TQQQ + Attack + Moonshot + Vault
A2-Q = QQQ only + Attack + Moonshot + Vault, TQQQ 없음
```

목적:

```text
TQQQ Booster가 기대수익을 올리는지,
또는 횡보장 decay로 인해 QQQ-only 공격형 book보다 나쁜지 확인.
```

A2-T가 QQQ를 이겨도 A2-Q, naive beta book, TQQQ contribution을 같이 봐야 한다.

---

## 4. 절대 금지어 / 금지 행동

```text
TQQQ를 Core라고 부르기 금지
TQQQ를 알파라고 부르기 금지
A2를 검증된 알파 시스템이라고 부르기 금지
손실 중 물타기 금지
Hard Vault 재투입 금지
LLM이 직접 매수/매도 결정 금지
LLM이 비중 숫자 직접 결정 금지
LLM이 성공확률 확정 금지
NEG filing 무시 금지
Moonshot thesis 없이 진입 금지
판정일 없는 Moonshot 금지
Vault를 표시용으로만 남기기 금지
live ledger와 backtest 섞기 금지
same-day signal로 same-day return 먹이기 금지
```

---

## 5. A2의 성공 정의

A2는 Sharpe 우선 book이 아니다. 성공은 아래 세 조건이다.

```text
1. A2 total NAV > QQQ benchmark
2. Vaulted Profit > 0
3. 큰 손실 후에도 게임을 계속할 수 있음
```

추가 평가:

```text
A2 > naive beta book?
A2-T > A2-Q?
Vault-adjusted NAV > QQQ?
Attack/Moonshot contribution > 0?
TQQQ contribution이 전체 성과 대부분인가?
```

---

## 6. 최종 구현 목표

```text
1. QQQ/TQQQ beta engine을 정확한 회계로 구현
2. Attack/Moonshot이 실제 ledger를 갖도록 구현
3. Vault를 실제 ledger로 구현하여 active capital에서 차감
4. LLM War Plan은 상태 판정만 하고 mapping engine이 비중 조절
5. 분봉 provider는 interface로 추상화하고 yfinance는 PROXY로 라벨
6. 3년/12/6/3개월 기준 A2-T/A2-Q/QQQ/SPY/TQQQ/naive 비교 대시보드
7. Codex STOP 체크를 통과할 만큼 look-ahead와 live/backtest 혼동 제거
```
