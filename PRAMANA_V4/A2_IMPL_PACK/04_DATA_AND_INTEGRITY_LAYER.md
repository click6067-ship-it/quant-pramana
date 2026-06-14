# PRAMANA A2 — Data and Integrity Layer

## 0. 핵심 원칙

데이터 레이어의 목적은 수익이 아니라 **거짓 수익 방지**다.

---

## 1. Data Sources

### Sharadar

사용처:

```text
QQQ/TQQQ/SPY daily price
PIT universe
corporate actions
fundamentals
liquidity filters
quality/momentum/context features
```

Sharadar는 A2 daily backbone이다.

### EDGAR

사용처:

```text
8-K / 10-Q / 10-K acceptance timestamp
NEG Filing Gate
Catalyst radar
Moonshot thesis evidence
```

EDGAR는 timestamp 기반 PIT가 가능하므로 정성 데이터 중 가장 우선이다.

### Minute Provider

용도:

```text
Attack sleeve only
ORB15
VWAP
RVOL entry-time
Bollinger / intraday momentum
```

Provider 단계:

```text
Stage 0: yfinance 5m/15m PROXY
Stage 1: Polygon / Databento / Alpaca SIP
Stage 2: broker paper execution + quote/fill reconciliation
```

### Alpaca

용도:

```text
paper execution / broker API / position sync
```

주의:

```text
Alpaca free IEX data = full-market VWAP/RVOL 검증용 아님
```

---

## 2. Timestamp Rules

### EOD

```text
Feature calculated with close(t) can only affect position(t+1)
```

### Intraday

```text
ORB/VWAP/RVOL calculated at bar close can only enter next bar
```

### EDGAR

```text
Filing accepted before market open → same-day regular session eligible
Filing accepted during market hours → next bar or next session, depending strategy flag
Filing accepted after market close → next trading day eligible
```

---

## 3. RVOL Rule

RVOL must be entry-time only.

```text
RVOL_at_time = cumulative_volume_so_far_today / average_cumulative_volume_by_same_time
```

금지:

```text
full-day volume used before close
```

---

## 4. Data Quality Labels

모든 Attack signal은 data_quality를 가진다.

```text
PROXY = yfinance / delayed / approximate
IEX_ONLY = partial market
SIP = full consolidated
QUOTE_LEVEL = best
```

성과표는 data_quality별로 분리한다.

---

## 5. Integrity Checks

```text
NaN bars → fail closed
stale bars → fail closed
split/corporate action mismatch → warning/fail
volume zero during regular session → suspicious
timezone mismatch → fail
future timestamp → fail
```

---

## 6. Implementation Files

```text
engine/a2_data_loader.py
engine/a2_edgar_loader.py
engine/a2_intraday_provider.py
engine/providers/yfinance_provider.py
engine/providers/polygon_provider.py
engine/providers/alpaca_provider.py
```

---

## 7. Completion Criteria

```text
Daily data loads without future leakage
Intraday provider returns bars with timestamp/session labels
EDGAR filings have acceptance timestamp
RVOL is entry-time only
All data source labels are written to ledgers
```
