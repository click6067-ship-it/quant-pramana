# PRAMANA A2 — Benchmarks & Metrics v0.1

## 0. 목적

A2는 QQQ만 이기면 충분하지 않다.

A2는 QQQ/TQQQ 성장 베타를 의식적으로 산 book이므로, 단순 QQQ보다 성과가 좋아도 그게 전략의 부가가치인지 알 수 없다.

따라서 다음 벤치마크를 반드시 같이 실행한다.

---

## 1. 벤치마크 목록

### 1.1 기본 시장 벤치마크

```text
SPY buy-and-hold
QQQ buy-and-hold
TQQQ buy-and-hold
```

### 1.2 A2 내부 벤치마크

```text
A2-Q: TQQQ 없이 QQQ 중심
A2-T: TQQQ 포함
A2 base fixed: QQQ35/TQQQ35/Attack10/Moon10/Vault10 고정
A2 dynamic: LLM state + mapping engine
```

### 1.3 Naive beta benchmark

```text
Naive Beta Book = QQQ35 + TQQQ35 + Cash30
```

목적:

```text
A2가 단순 QQQ/TQQQ 혼합보다 나은지 확인.
```

### 1.4 Synthetic beta benchmark

```text
Synthetic QQQ 1.4x proxy
```

계산:

```text
QQQ_daily_return × 1.4 - financing_cost_proxy
```

목적:

```text
A2의 실질 beta 1.4x와 비교.
```

### 1.5 TQQQ DCA 벤치마크

```text
TQQQ monthly DCA
TQQQ drawdown DCA
TQQQ fixed allocation
```

목적:

```text
TQ-DH가 단순 낙폭매수보다 나은지 확인.
```

### 1.6 Survival benchmark

```text
V7 4-sleeve survival core
```

목적:

```text
A2가 깨질 때 V7과 얼마나 다른지 확인.
```

---

## 2. 결과표 기간

모든 대시보드에서 아래 기간을 표시한다.

```text
3년
12개월
6개월
3개월
inception-to-date
live-only
```

주의:

```text
backtest와 live ledger는 분리한다.
2016~ historical panel을 live ₩1억 성과처럼 표시 금지.
```

---

## 3. 성과 지표

### 3.1 수익 지표

```text
final NAV
total return
annualized return
A2 vs QQQ excess
A2 vs naive excess
A2 vs synthetic beta excess
Vault-adjusted return
```

### 3.2 위험 지표

```text
MDD
rolling drawdown
recovery days
worst month
worst week
A2 max underperformance vs QQQ
A2 max underperformance vs naive
```

### 3.3 Convex 지표

```text
upside participation
downside participation
up/down asymmetry
big winner contribution
TQQQ contribution
Attack/Moonshot contribution
Vaulted Profit
```

### 3.4 운용 지표

```text
number of Attack trades
Attack win rate
Attack median trade return
Moonshot payoff ratio
Moonshot thesis success/fail
Vault trigger count
Reload usage count
TQ-DH action count
LLM state distribution
```

---

## 4. 성공 정의

A2는 다음을 모두 만족할 때 성공으로 본다.

```text
A2 total NAV > QQQ
A2 total NAV > naive beta book
Vaulted Profit > 0
A2가 큰 낙폭 후에도 게임을 계속할 수 있음
```

부분 성공:

```text
A2 > QQQ but A2 < naive
→ TQQQ beta는 효과 있었지만 A2 운영규칙 부가가치 미확정
```

실패:

```text
A2 < QQQ
A2 < naive
Vaulted Profit = 0
Attack/Moonshot contribution <= 0
MDD가 QQQ보다 크고 회복도 느림
```

---

## 5. TQ-DH 평가 기준

TQ-DH는 다음과 비교한다.

```text
TQQQ buy-and-hold
TQQQ monthly DCA
TQQQ drawdown DCA
A2 base without TQ-DH
A2 with TQ-DH
```

TQ-DH 성공 조건:

```text
A2 with TQ-DH가 without TQ-DH보다
- MDD 낮음
- 회복기간 짧음
- Vaulted Profit 높음
- final NAV 같거나 높음
```

---

## 6. 대시보드 필수 표

```text
A2 / QQQ / SPY / TQQQ / naive / synthetic beta / V7
```

표 컬럼:

```text
period
return
MDD
Sharpe or simple risk ratio
Vaulted Profit
recovery days
max underperformance vs QQQ
```

---

## 7. 구현 파일

```text
engine/a2_benchmarks.py
outputs/a2_live/benchmark_panel.csv
outputs/a2_live/a2_benchmark_dashboard.html
reports/A2_monthly_benchmark_review.md
```
