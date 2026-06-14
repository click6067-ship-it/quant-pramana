# 14 — Codex STOP Checklist

Claude는 구현 완료 전 아래를 전부 통과시켜야 한다.

## 1. Look-ahead

```text
모든 state/risk/LLM signal은 shift(1) 적용?
same-day close로 same-day return 먹지 않았는가?
EDGAR acceptance timestamp 이후만 사용했는가?
LLM input에 미래 뉴스/결과가 없는가?
```

## 2. Live / Backtest 분리

```text
live ledger = inception 이후 append-only?
historical backtest = 별도 panel?
대시보드에 live/backtest 명확히 구분?
2016~ backtest를 live ₩1억이라고 표시하지 않는가?
```

## 3. Vault

```text
Vault가 실제 active capital에서 차감되는가?
Hard/Reload 분리되는가?
Hard Vault 재투입이 코드상 불가능한가?
주1회/월10% 제한 enforce되는가?
QQQ보다 덜 잃었다고 Vault가 발동하지 않는가?
```

## 4. Accounting

```text
NAV = QQQ + TQQQ + Attack + Moonshot + Vault + Cash?
빈 Attack/Moonshot은 cash로 처리?
A2-Q / A2-T / naive가 독립 계산?
Attack/Moonshot contribution 계산 가능?
```

## 5. LLM

```text
LLM이 비중 숫자를 직접 결정하지 않는가?
LLM이 매수/매도 명령하지 않는가?
LLM이 P_up 확률 확정하지 않는가?
war_plan input/output hash 저장?
```

## 6. Attack / Moonshot

```text
Attack과 Moonshot이 분리되어 있는가?
Attack은 당일/분봉, Moonshot은 thesis/판정일 기반인가?
NEG Gate가 Attack/Moonshot에 다르게 적용되는가?
Moonshot thesis 없는 진입이 불가능한가?
```

## 7. TQ-DH

```text
TQ-DH 모듈 존재?
Dip Type A/B/C/D 구현?
Hard Vault 사용 금지?
TQQQ buy-and-hold/monthly DCA/drawdown DCA 비교 존재?
```

## 8. Data Quality

```text
yfinance는 PROXY로 라벨링?
Alpaca IEX를 full-market VWAP/RVOL로 착각하지 않는가?
유료 minute provider는 adapter로 분리되어 있는가?
```

## 9. STOP 조건

아래 중 하나라도 있으면 STOP:

```text
same-day look-ahead
Vault display-only
live/backtest 혼동
Hard Vault 재투입 가능
LLM direct trade
A2 숫자를 QQQ와만 비교하고 naive benchmark 없음
```
