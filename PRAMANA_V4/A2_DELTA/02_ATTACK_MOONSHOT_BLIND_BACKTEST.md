# PRAMANA A2 — Attack/Moonshot Blind Backtest 설계 v0.1

## 0. 목적

Attack/Moonshot을 과거데이터로 테스트할 때 가장 큰 위험은 look-ahead다.

특히 다음은 전부 금지다.

```text
그날 마감 후 거래량을 장초 진입에 사용
나중에 나온 뉴스/분석을 과거 의사결정에 사용
수정된 공시/뉴스를 원래 시점의 정보처럼 사용
월 평균가/미래 평균가로 시작 NAV 계산
LLM에게 미래 결과를 암시하는 정보 제공
```

목표는 “그 시점에 실제로 알 수 있었던 정보만”으로 후보를 만들고 진입·청산을 계산하는 것이다.

---

## 1. 핵심 개념

### 1.1 decision_time

전략이 실제 결정을 내리는 시각.

예:

```text
Premarket scan: 09:20 ET
ORB entry: 09:45 ET
EOD entry: 16:10 ET
Moonshot review: filing acceptance timestamp 이후 첫 regular session close
```

### 1.2 available_at

각 데이터가 실제로 공개/사용 가능해진 시각.

규칙:

```text
feature 사용 가능 조건 = available_at <= decision_time
```

### 1.3 signal_time / execution_time

```text
signal_time = 신호 계산 시각
execution_time = 실제 체결 가정 시각
```

원칙:

```text
execution_time > signal_time
same-bar 내부 체결 금지
same-close 금지
```

---

## 2. Sharadar로 가능한 것

Sharadar는 daily/PIT backbone으로 사용한다.

가능:

```text
EOD price
corporate actions
fundamentals
PIT universe
liquidity filter
daily momentum / quality / event context
```

Sharadar 기반으로 가능한 blind backtest:

```text
EOD Attack 후보 필터
Moonshot daily candidate filter
NEG filing 이후 daily drift
fundamental quality floor
daily momentum confirmation
```

주의:

```text
Sharadar는 분봉/VWAP/ORB용 데이터가 아니다.
Sharadar만으로 historical intraday ORB/VWAP/RVOL backtest는 불가능하다.
```

---

## 3. EDGAR로 가능한 것

EDGAR는 공시 timestamp가 있어서 PIT에 강하다.

사용:

```text
8-K
10-Q
10-K
S-3
424B
DEF 14A
Form 4 등
```

필수 필드:

```text
ticker
CIK
form_type
item_code
acceptance_datetime
filing_url
text_snapshot
```

규칙:

```text
acceptance_datetime 이후에만 해당 공시 사용 가능.
장중 공시라면, 공시 시각 이후 첫 사용 가능 bar부터 사용.
장마감 후 공시라면, 다음 거래일 premarket/regular open 이후 사용.
```

---

## 4. 무료 데이터로 가능한 분봉 backtest 수준

### 4.1 yfinance

사용 가능:

```text
최근 60일 5m/15m proxy
최근 짧은 1m proxy
forward paper signal 축적
```

라벨:

```text
DATA_QUALITY = PROXY
```

제한:

```text
오래된 과거 분봉 불가
full-market volume 아님 가능성
premarket/after-hours 일관성 제한
실제 체결/quote 검증 불가
```

따라서 yfinance 분봉 결과는 다음 목적만 허용한다.

```text
scanner QA
signal logging
recent replay
paper-forward observation
```

금지:

```text
yfinance 5m 결과를 production-grade alpha proof로 사용
```

### 4.2 Alpaca 무료 IEX

용도:

```text
paper order plumbing
position sync
basic quote sanity
```

금지:

```text
full-market VWAP/RVOL 검증용으로 사용 금지
```

---

## 5. 유료 분봉 데이터가 필요한 경우

필요 조건:

```text
Attack v0/v1 paper signal이 최소한 positive hint를 보임
체결/스프레드/bid-ask가 실제 병목으로 확인됨
ORB/VWAP/RVOL confirmation을 정확히 검증해야 함
```

후보:

```text
Polygon
Databento
Alpaca SIP/Algo Trader Plus
```

지금 기본 원칙:

```text
과거 구현은 무료로 최대한 한다.
유료는 provider interface만 먼저 설계한다.
성과 가능성이 보일 때 1개월 파일럿.
```

---

## 6. Blind Backtest 구현 구조

### 6.1 Feature Store

파일:

```text
outputs/a2_features/feature_store.parquet
```

필수 컬럼:

```text
ticker
feature_name
feature_value
asof_time
available_at
source
quality_label
```

사용 규칙:

```python
usable = features[features.available_at <= decision_time]
```

### 6.2 Event Store

파일:

```text
outputs/a2_events/event_store.parquet
```

필수 컬럼:

```text
ticker
event_type
event_time
available_at
form_type
item_code
source_url
raw_text_hash
llm_label
```

### 6.3 Decision Log

파일:

```text
outputs/a2_decisions/decision_log.csv
```

필수 컬럼:

```text
decision_id
decision_time
ticker
strategy_type
features_used_hash
events_used_hash
llm_snapshot_hash
decision
planned_execution_time
```

### 6.4 Fill Simulation

```text
EOD strategy:
- signal on day t after close
- enter on day t+1 open or VWAP proxy

Intraday strategy:
- signal after bar close
- enter next bar open/close
- same bar execution 금지
```

---

## 7. Attack blind backtest

Attack은 과거 full intraday가 없으면 두 단계로 나눈다.

### Stage A — Daily proxy backtest

목적:

```text
catalyst + daily momentum + NEG filter가 후보를 좁히는지 확인
```

입력:

```text
Sharadar daily
EDGAR events
EOD gap/momentum
volume spike daily proxy
```

출력:

```text
candidate quality
next 1/3/5/10 day return
SPY/QQQ excess
```

라벨:

```text
ATTACK_DAILY_PROXY
```

### Stage B — Intraday recent replay / forward

목적:

```text
ORB/VWAP/RVOL confirmation이 실제로 작동하는지 최근 데이터/forward로 확인
```

입력:

```text
yfinance 5m/15m 또는 provider minute bars
```

라벨:

```text
ATTACK_INTRADAY_PROXY or ATTACK_INTRADAY_PROVIDER
```

---

## 8. Moonshot blind backtest

Moonshot은 백테스트보다 thesis ledger가 핵심이다.

과거 시뮬레이션 시 가능한 것:

```text
EDGAR event-based moonshot proxy
clinical/FDA/merger/legal events with known event_time
post-event payoff distribution
```

주의:

```text
과거 대박종목을 사후 선택하면 무효.
후보 universe를 decision_time에 만들 수 있어야 함.
```

Moonshot backtest 최소 요구:

```text
candidate 생성 규칙이 event 발생 전/당시에 정의되어 있어야 함
판정일이 있어야 함
성공/실패 조건이 데이터로 평가 가능해야 함
```

---

## 9. LLM blind 처리

LLM은 과거 결과를 보지 않아야 한다.

금지:

```text
미래 주가 결과 포함
나중에 작성된 기사/분석 포함
현재 위키/현재 뉴스로 과거 판단
```

허용:

```text
EDGAR filing text at acceptance time
company press release captured with timestamp
news item with timestamp and archival source
```

LLM snapshot 기록:

```text
prompt_template_hash
input_text_hash
model_name
run_time
llm_output_hash
```

---

## 10. 구현 체크리스트

```text
[ ] every feature has available_at
[ ] every event has acceptance_time or timestamp
[ ] decision_time saved
[ ] execution_time > decision_time
[ ] same-bar execution prohibited
[ ] yfinance data labeled PROXY
[ ] Sharadar used only for daily/PIT
[ ] LLM input excludes future information
[ ] decision log append-only
```
