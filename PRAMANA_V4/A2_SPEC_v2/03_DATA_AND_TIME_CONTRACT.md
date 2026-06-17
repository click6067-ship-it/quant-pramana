# 03 — Data, API, PIT, Blind Backtest Contract

## 1. 데이터 원칙

A2에서 가장 중요한 것은 “그 시점에 실제로 알 수 있었던 정보만 사용”하는 것이다.

필수 시간 필드:

```text
event_time      = 사건이 실제 발생한 시각
available_at    = 데이터가 우리에게 사용 가능해진 시각
decision_time   = 전략이 판단을 내리는 시각
signal_time     = 신호가 확정된 시각
execution_time  = 진입/청산이 가능한 첫 시각
```

규칙:

```text
available_at <= decision_time < execution_time
signal t → execution t+1
same close 신호로 same close return 적용 금지
```

## 2. Sharadar

역할:

```text
EOD 가격
PIT universe
fundamentals
corporate actions
liquidity filter
daily momentum/quality/event context
QQQ/TQQQ EOD book
Attack/Moonshot 일봉 필터
```

한계:

```text
분봉/VWAP/ORB/RVOL 실전 데이터 아님
뉴스/실적콜 텍스트 데이터 아님
진짜 analyst revision 데이터 아님
```

## 3. EDGAR

역할:

```text
8-K / 10-Q / 10-K
NEG Filing Gate
catalyst input
Moonshot filing risk
PIT timestamp
```

사용 기준:

```text
acceptance timestamp 기준
acceptance_time 이후 다음 가능한 거래시점부터만 사용
filing content hash 저장
```

## 4. yfinance

역할:

```text
무료 intraday proxy
5m/15m forward signal 축적
QA/prototype
```

라벨:

```text
DATA_QUALITY = PROXY
```

금지:

```text
yfinance proxy 결과를 execution-grade 검증이라고 부르기 금지
```

## 5. Minute Provider

interface:

```python
def get_intraday_bars(ticker, start, end, interval): ...
def get_premarket_bars(ticker, date): ...
def get_latest_quote(ticker): ...
```

adapter 후보:

```text
yfinance_provider.py       # proxy
polygon_provider.py        # paid minute/fuller data
alpaca_provider.py         # paper broker + optional SIP, IEX는 주의
databento_provider.py      # professional market data
```

## 6. Alpaca

역할:

```text
paper execution
positions sync
orders
broker API
```

주의:

```text
무료 IEX 데이터는 full-market VWAP/RVOL 검증용이 아님
브로커 API와 데이터 검증 소스를 분리할 것
```

## 7. LLM Input Snapshot

LLM에 넣는 모든 입력은 저장해야 한다.

```text
input_json_path
input_hash
llm_model
prompt_hash
output_json
output_hash
```

금지:

```text
미래 뉴스 사용 금지
결과 수익률을 LLM에게 보여준 뒤 과거 라벨링 금지
LLM이 확률/매수/비중 결정 금지
```

## 8. Blind Backtest Contract

Attack/Moonshot 과거실험은 반드시 아래를 만족해야 한다.

```text
1. 후보 생성 시점에서 사용 가능한 데이터만 사용
2. ticker universe는 그 시점 기준
3. EDGAR filing은 acceptance_time 이후만 사용
4. Sharadar fundamental은 datekey/filing date 기준
5. minute data 없으면 daily approximation으로만 라벨
6. proxy 데이터는 proxy라고 표시
7. strategy outcome을 보고 후보를 재분류하지 않음
```
