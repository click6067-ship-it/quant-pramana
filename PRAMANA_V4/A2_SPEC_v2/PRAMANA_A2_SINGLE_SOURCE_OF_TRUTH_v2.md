# PRAMANA A2 — Single Source of Truth v2.0

**통합 MD 파일.** 이 문서가 최신 A2 구현 기준이다. 이전 문서와 충돌하면 이 문서가 우선한다.



---


# PRAMANA A2 — Claude 구현용 최종 통합 스펙 v2.0

**상태:** PAPER only · NO LIVE · 자본권한 0  
**이 문서팩의 목적:** Claude가 더 이상 이전 문서/구현을 임의 해석하지 않고, 이 문서만 보고 A2를 A→Z로 구현하도록 하는 단일 source of truth.

## 이 문서가 이전 문서보다 우선한다

충돌 시 우선순위:

1. `PRAMANA_A2_SINGLE_SOURCE_OF_TRUTH_v2.md` / 이 모듈팩
2. `pramana_a2_delta_patch_pack`
3. `pramana_a2_implementation_pack`
4. `PRAMANA_A2_Convex_Raider_Book_FINAL_v1.md`
5. 과거 A1/V7 문서

이전 A2 v1의 `QQQ30/TQQQ40/Attack12/Moon8/Vault10`은 **legacy**다.  
최신 A2 v2 기본 비중은 **QQQ35/TQQQ35/Attack10/Moonshot10/Vault10**이다.

## 구현 순서

Claude는 반드시 아래 순서대로만 구현한다.

1. **Phase 0 — 무결성 패치**  
   next-bar, live/backtest 분리, 회계 통일, Vault display-only 제거.
2. **Phase A — Vault 진짜 ledger**  
   Hard/Reload Vault, NAV 차감, Vault In/Out, weekly/monthly limit.
3. **Phase B — 모듈별 book 회계**  
   QQQ, TQQQ, Attack, Moonshot, Vault sleeve를 독립 ledger로 구현.
4. **Phase C — Attack/Moonshot 연료**  
   Attack scanner, Moonshot thesis board, NEG Gate, Token/Draft/Decay.
5. **Phase D — LLM Council + Mapping Engine**  
   LLM은 상태만 판정, 비중 변경은 사전정의 mapping.
6. **Phase E — TQ-DH**  
   TQQQ Dip Harvester, Reload Vault 기반 dip 분류/재투입.
7. **Phase F — 대시보드/운영**  
   3년/12/6/3/live comparison, mini PC cron, health check.

## 파일 목록

| 파일 | 역할 |
|---|---|
| `01_A2_MASTER_SPEC.md` | A2 v2 전체 목적·원칙·금지사항 |
| `02_EIGHT_LAYER_ARCHITECTURE.md` | 기존 8레이어에 A2 모듈 매핑 |
| `03_DATA_AND_TIME_CONTRACT.md` | 데이터/API·PIT·blind backtest·분봉 데이터 계약 |
| `04_ALLOCATION_AND_MAPPING.md` | 35/35/10/10/10·동적 비중·LLM state mapping |
| `05_QQQ_MODULE.md` | QQQ Core 구현 |
| `06_TQQQ_MODULE.md` | TQQQ Booster·Decay·Booster Rent |
| `07_ATTACK_MODULE.md` | 급등주·ORB/VWAP/RVOL·Bollinger·day trade |
| `08_MOONSHOT_MODULE.md` | Moonshot thesis·EV·Draft Board |
| `09_VAULT_MODULE.md` | Profit Vault 진짜 ledger·Vault In/Out |
| `10_RISK_LLM_COUNCIL.md` | Risk Dashboard·LLM Council 역할 |
| `11_TQ_DH_DIP_HARVESTER.md` | TQQQ Dip Harvester |
| `12_BENCHMARKS_AND_DASHBOARD.md` | QQQ/SPY/TQQQ/naive/A2-Q/A2-T/TQ-DH 비교 |
| `13_IMPLEMENTATION_SEQUENCE.md` | 구현 단계·파일·완료조건 |
| `14_CODEX_STOP_CHECKLIST.md` | Codex STOP 방지 체크리스트 |
| `15_CLAUDE_EXECUTION_PROMPT.md` | Claude에게 그대로 넣을 실행 프롬프트 |

## Claude에게 전달 방법

1. 압축을 풀어 repo의 `PRAMANA_V4/A2_SPEC_v2/`에 넣는다.
2. Claude에게 먼저 `15_CLAUDE_EXECUTION_PROMPT.md`를 붙여넣는다.
3. Claude가 구현 전 `00_INDEX.md → 01 → 02 → 03 → 04 → 모듈별 문서 → 13 → 14` 순서로 읽었는지 확인한다.
4. Claude가 구현 완료를 말하면 `14_CODEX_STOP_CHECKLIST.md` 기준으로 자체검사 결과를 보고하게 한다.

## 한 줄 요약

A2는 알파가 검증된 전략이 아니다. **QQQ/TQQQ 성장 베타를 사고, Attack/Moonshot으로 비대칭을 붙이고, Profit Vault로 번 돈을 잠그며, Risk/LLM Dashboard로 자멸을 줄이는 고위험 paper book**이다.


---


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


---


# 02 — A2 8-Layer Architecture

A2는 기존 PRAMANA 8레이어를 유지하되, 각 레이어에 QQQ/TQQQ/Attack/Moonshot/Vault 모듈을 명확히 배치한다.

## Layer 1 — Data & Integrity

역할:

```text
Sharadar EOD/PIT/fundamental backbone
EDGAR filing timestamp
minute provider interface
yfinance proxy
LLM input snapshots
look-ahead 방지
```

필수:

```text
available_at <= decision_time
signal_time < execution_time
all risk states shift(1)
```

## Layer 2 — Signal / State Factory

생성하는 상태:

```text
Leadership Risk
Market Stress
TQQQ Decay Meter
TQQQ Booster Rent
LLM Narrative State
NEG Filing Flags
Attack Candidates
Moonshot Draft Candidates
TQ-DH Dip Type
```

## Layer 3 — Sleeve Engines

```text
QQQ Module
TQQQ Booster Module
Attack Module
Moonshot Module
Vault Module
```

각 모듈은 독립 ledger를 가진다.

## Layer 4 — Dynamic Allocator / Mapping Engine

LLM이 비중을 정하지 않는다.

```text
LLM state → GREEN/YELLOW/RED
Mapping engine → target weight
Risk limits → clamp
next-bar 적용
```

## Layer 5 — Risk Engine

```text
Leadership RED
Decay Zone
Market Stress RED
Beta Governor
Drawdown ladder
Attack token lockout
Moonshot thesis invalidation
NEG Gate
```

Risk Engine은 우선 **신규진입/증액 금지** 역할을 한다. 기존 QQQ/TQQQ 자동매도는 극단 조건에서만 후보로 표시한다.

## Layer 6 — Execution / Paper Ledger

현재는 paper only.

```text
EOD rebalance for QQQ/TQQQ/Vault
Intraday paper signal for Attack
Manual/paper entry for Moonshot
Vault transfer ledger
```

실제 주문 API가 붙더라도 기본은 paper.

## Layer 7 — Attribution / Monitoring

대시보드 필수:

```text
A2 active NAV
Vault-adjusted NAV
QQQ/SPY/TQQQ/naive benchmarks
TQQQ contribution
Attack contribution
Moonshot contribution
Vaulted Profit
Dynamic allocator contribution
TQ-DH contribution
```

## Layer 8 — Governance / Human Gate

```text
실자본 금지
Hard Vault 재투입 금지
Moonshot thesis 승인 필요
LLM 직접매매 금지
Codex STOP checklist 통과 필요
```

## 레이어별 구현 산출물

| Layer | 주요 파일 |
|---|---|
| L1 | `engine/a2_data_contract.py`, providers |
| L2 | `engine/a2_risk_dashboard.py`, `a2_daily_war_plan.py` |
| L3 | `a2_book.py`, `a2_attack_ledger.py`, `a2_moonshot_ledger.py`, `a2_profit_vault.py` |
| L4 | `a2_dynamic_allocator.py`, `config/a2_state_mapping.yaml` |
| L5 | `a2_neg_gate.py`, `a2_tq_dh.py`, `a2_drawdown_rules.py` |
| L6 | `a2_live_runner.py`, `a2_attack_executor_paper.py` |
| L7 | `a2_dashboard.py`, reports |
| L8 | checklist, decision logs |


---


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


---


# 04 — Allocation & Dynamic Mapping Engine

## 1. 기본 비중

```yaml
base_allocation:
  QQQ: 0.35
  TQQQ: 0.35
  Attack: 0.10
  Moonshot: 0.10
  Vault: 0.10
```

## 2. 허용 범위

```yaml
ranges:
  QQQ: [0.25, 0.45]
  TQQQ: [0.15, 0.45]
  Attack: [0.00, 0.20]
  Moonshot: [0.00, 0.15]
  Vault: [0.05, 0.30]
```

## 3. 변경 단위

```yaml
change_unit: 0.05
max_daily_change: 0.05
max_weekly_change: 0.10
```

## 4. LLM Council 역할

LLM은 상태만 판정한다.

```text
GREEN / YELLOW / RED
ACCUMULATE / HOLD / RELOAD_ALLOWED
OPEN / HOLD_ONLY / LOCKED
```

LLM은 아래를 하지 않는다.

```text
비중 숫자 직접 결정
매수/매도 명령
성공확률 확정
포지션 사이징 확정
```

## 5. Mapping Engine

상태를 target weight로 바꾸는 것은 code/config가 한다.

### TQQQ state

```text
GREEN  → TQQQ +5%p 가능
YELLOW → 유지
RED    → 증액 금지 또는 -5%p 후보
```

### Attack state

```text
GREEN  → Attack +5%p 가능
YELLOW → 유지 또는 half size
RED    → 신규진입 금지
```

### Moonshot state

```text
OPEN      → thesis 있는 후보만 가능
HOLD_ONLY → 기존만 유지, 신규 금지
LOCKED    → 신규 금지, 기존 thesis 재검토
```

### Vault state

```text
ACCUMULATE     → Vault +5%p 후보
HOLD           → 유지
RELOAD_ALLOWED → Reload Vault 일부 사용 가능
```

## 6. Mode Labels

```text
Base Mode
Berserker Mode
Red King Mode
Attack Lockout / Booster Add Ban
Crash Lockout
```

Risk-Off라는 이름은 사용하지 않는다. 마켓타이밍 자동매도로 오해되기 때문이다.

## 7. Attack Lockout / Booster Add Ban

의미:

```text
기존 QQQ/TQQQ 자동매도 아님
TQQQ 신규 증액 금지
Attack 신규진입 금지
Moonshot 신규진입 금지
Reload Vault 사용 금지
Profit Vault 우선 검토
```

## 8. Crash Lockout

조건:

```text
A2 전체 MDD -30%
TQQQ sleeve MDD -35%
Leadership RED 10거래일 지속
TQQQ Decay Zone 20거래일 지속
QQQ 200일선 하회 + VXN 급등 + leaders breakdown
```

행동:

```text
TQQQ 신규매수 0
Attack/Moonshot 신규 0
사람 리뷰 필요
자동매도는 manual decision flag로만 표시
```

## 9. next-bar 적용

모든 상태 판정은 t일 계산, t+1일 적용.

```python
state_today = compute_state(data_until_t)
target_weight_tomorrow = mapping(state_today)
```

same-day return에 same-day state를 적용하지 않는다.


---


# 05 — QQQ Core Module

## 1. 역할

QQQ는 A2의 기본 성장 베타다.

```text
SPY는 A2에서 퇴출.
QQQ는 벤치마크이자 기본 엔진.
```

## 2. 기본 비중

```text
Base: 35%
Range: 25~45%
```

## 3. QQQ Module 입력

```text
QQQ EOD close/high/low/volume
20/50/200일선
20일 realized vol
drawdown
gap-up/gap-down
relative strength vs SPY
```

## 4. QQQ 증감 원칙

QQQ는 TQQQ보다 안정적인 성장 노출이다.

```text
TQQQ Decay RED인데 성장 노출을 유지하고 싶으면 TQQQ 대신 QQQ.
TQ-DH Type B/Growth Reset에서는 먼저 QQQ reload 후 TQQQ 확인.
```

## 5. QQQ는 매도타이밍 엔진이 아니다

QQQ는 코어 노출이며, Risk Dashboard가 RED라고 자동으로 전부 팔지 않는다.

축소 후보:

```text
A2 Crash Lockout
전체 MDD -30%
QQQ 200일선 하회 + Leadership RED 장기화
사용자 manual review
```

## 6. 대시보드 표시

```text
QQQ weight actual/target
QQQ contribution
QQQ 20/50/200 state
QQQ drawdown
QQQ vs SPY relative strength
QQQ vs A2 excess
```


---


# 06 — TQQQ Booster Module

## 1. 역할

TQQQ는 Core가 아니다. Booster다.

```text
TQQQ = QQQ 일일수익률 3배를 목표로 하는 레버 베타 도구.
TQQQ = 알파가 아님.
TQQQ = 강세장 폭발력 + 하락/횡보장 파괴 리스크.
```

## 2. 기본 비중

```text
Base: 35%
Range: 15~45%
Absolute experimental max: 50%
```

## 3. 증액 허용 조건

```text
Leadership Risk GREEN
TQQQ Decay Meter GREEN
Market Stress GREEN/YELLOW
LLM Narrative GREEN/YELLOW
QQQ 20일선 위
QQQ 50일선 위
A2 drawdown -15% 이내
Effective Beta RED 아님
NEG cluster 없음
```

## 4. 증액 금지 조건

```text
Leadership RED
TQQQ Decay Zone
Market Stress RED
A2 MDD -20% 초과
QQQ 20/50일선 동시 이탈
VIX/VXN 급등
big leaders high-volume down day 다수
LLM Narrative RED
```

## 5. 축소 후보 조건

기본은 자동매도 금지. 단 아래는 파산 방지 후보.

```text
A2 전체 MDD -30%
TQQQ sleeve MDD -35%
Leadership RED 10거래일 지속
TQQQ Decay Zone 20거래일 지속
QQQ 200일선 하회 + VXN 급등 + leaders breakdown
```

축소 제한:

```text
1회 -5%p
하루 최대 -10%p
```

## 6. TQQQ Decay Meter

Decay Zone 조건:

```text
QQQ 20일 수익률이 -3%~+3%
AND QQQ realized vol 상승
AND 20일 high-low range 확대
```

행동:

```text
TQQQ 증액 금지
Berserker 금지
Profit Vault 우선
Attack size 축소
```

## 7. Booster Rent Metric

TQQQ가 돈값을 못 하는지 본다.

```text
최근 20거래일:
TQQQ 수익률 < 2.3 × QQQ 수익률
AND QQQ 수익률 -3%~+3%
AND realized vol 높음
```

판정:

```text
Booster inefficiency flag
```

행동:

```text
증액 금지
Berserker 금지
Vault 우선
Attack 축소
```

## 8. 대시보드 표시

```text
TQQQ target/actual weight
TQQQ contribution
TQQQ sleeve MDD
Decay status
Booster Rent status
TQQQ vs QQQ realized multiple
TQQQ add permission
TQQQ trim candidate flag
```


---


# 07 — Attack Module

## 1. 역할

Attack은 **당일/초단기 급등주·모멘텀 공격 sleeve**다.

```text
기본 비중: 10%
허용 범위: 0~20%
보유 기간: 기본 당일, 강한 경우 1~3일
목표: 작은 손실로 빠르게 진입하고, 수익은 Vault/익절로 회수
```

## 2. Attack 후보 유형

```text
A. Catalyst Confirmed Momentum
B. Delayed Recognition
C. Leadership Rotation
D. Bollinger Squeeze Breakout
E. Gap + RVOL + ORB + VWAP day trade
```

## 3. 데이터

```text
Sharadar: 일봉 필터/유동성/PIT/fundamental
EDGAR: NEG/Catalyst
yfinance 5m/15m: PROXY 분봉
Polygon/Databento/Alpaca SIP: 실전급 분봉 option
LLM: catalyst/narrative 요약
```

## 4. 진입 조건

A/B catalyst 또는 강한 momentum trigger 중 하나 필요.

그리고 아래 확인:

```text
RVOL entry-time 통과
VWAP 위
ORB15 돌파 또는 전일 고점 돌파
Bollinger squeeze breakout 또는 upper band expansion
Leadership RED 아님
Market Stress RED 아님
Attack token 있음
```

## 5. Bollinger 전략

Bollinger는 단독 매수 신호가 아니다.

사용:

```text
volatility squeeze 후 상단 확장
급등주 모멘텀 confirmation
ORB/VWAP/RVOL과 결합
```

금지:

```text
Bollinger 상단 터치만 보고 매수
횡보장에서 반복 매수
```

## 6. NEG 처리

Attack은 Moonshot과 다르게 Hard NEG를 완전 금지로만 쓰지 않는다.

```text
Hard NEG + 급등주:
- paper-only 또는 0.25R~0.5R
- overnight 금지
- VWAP 이탈 즉시 청산
- 물타기 금지
- high-risk flag 표시
```

하지만 아래는 매우 주의:

```text
상폐 위험
재무제표 신뢰 불가
회계 문제
반복 유증
```

이 경우 실전 승격 금지, paper-only.

## 7. Attack 등급

| 등급 | 조건 | 사이즈 |
|---|---|---|
| A | strong catalyst + clean filing + RVOL/VWAP/ORB | 1R |
| B | catalyst 있음 + 일부 confirmation | 0.5R |
| C | momentum only | paper watch |
| D | reject | 금지 |

## 8. Attack Token

```text
매주 3 token
A급 attack = 1 token
B급 attack = 0.5 token
손실 trade = 다음 주 token -1
+2R 이상 승리 = 다음 주 token +1
Leadership RED = token 0
```

## 9. 청산

```text
-1R 손절
+1R → stop breakeven
+2R → 1/3 익절
+3R → 1/3 Vault
VWAP 이탈
ORB low 이탈
time stop
장마감 전 청산 기본
```

## 10. Overnight

기본 금지.

허용 조건:

```text
A급 catalyst
종가 VWAP 위
strong close
Market not RED
NEG 없음
```

## 11. blind/PIT backtest

분봉 과거 데이터가 없는 경우:

```text
daily approximation만 사용
DATA_QUALITY=DAILY_PROXY
```

분봉 결과는 유료 provider 전까지 실전 검증으로 부르지 않는다.


---


# 08 — Moonshot Module

## 1. 역할

Moonshot은 **큰 비대칭 thesis 베팅**이다.

```text
기본 비중: 10%
허용 범위: 0~15%
목표: 2x~5x 이상 가능성이 있는 event/thesis를 작은 손실 한도로 포착
```

Moonshot은 분봉매매가 아니다. Moonshot은 thesis와 판정일이 핵심이다.

## 2. 후보 유형

```text
FDA/임상 결과
소송 판결
M&A 가능성
규제 승인
대형 계약
파산 회생
구조조정
숏스퀴즈
AI/전력/반도체/바이오 핵심 테마
복잡한 8-K/10-Q/10-K mispricing
```

## 3. 필수 thesis 필드

```text
Ticker:
Thesis:
Catalyst:
판정일:
왜 시장이 틀렸는가:
성공 조건:
실패 조건:
무효화 조건:
최대손실:
Reward/Risk:
P_up_human:
LLM bull case:
LLM bear case:
Tail risk:
Exit plan:
```

## 4. 진입 조건

```text
thesis 명확
판정일 있음
Reward/Risk ≥ 3:1
EV > +0.5R
최대손실 사전확정
Hard NEG 없음
LLM bull/bear case 작성
Moonshot Draft Board 상위 후보
```

## 5. 금지

```text
판정일 없는 Moonshot
Hard NEG 있는 Moonshot
그냥 꿈
P_up 근거 없는 진입
Reward/Risk < 3:1
최대손실 불명확
손실 중 물타기
```

## 6. 사이징

```text
기본 = 1R
강한 thesis = 2R
최대 = 3R
1R = A2 NAV의 0.5% 손실
공격모드 1R = A2 NAV의 1.0% 손실
Moonshot sleeve 전체를 한 번에 사용 금지
```

## 7. P_up 과대평가 방지

```text
LLM은 P_up 확률을 결정하지 않음
LLM은 bull/bear case만 작성
사람의 P_up 입력 기본 상한 40%
P_up 60% 이상은 특별 사유 없으면 금지
```

## 8. Moonshot Draft Board

점수:

```text
Catalyst clarity
Time to catalyst
Reward/Risk
NEG filing risk
Dilution risk
Liquidity
Narrative strength
LLM bear case severity
Theme concentration
Tail risk
```

상위 1~2개만 실제 진입 가능.

## 9. Optionality Queue

```text
Queue 1: 판정일 30일 이내
Queue 2: 판정일 90일 이내
Queue 3: 장기 thesis
```

가장 가까운 catalyst부터 배정.

## 10. Moonshot Vault

```text
2배 → 원금 회수
3배 → 절반 Vault
thesis 깨짐 → 즉시 종료
판정일 경과 → 강제 리뷰
```

## 11. Thesis Decay Timer

```text
판정일 경과 후 업데이트 없음 → 강제 리뷰
catalyst 지연 → thesis decay
negative filing 발생 → 즉시 재평가
```


---


# 09 — Profit Vault Module

## 1. 목적

Vault는 평가익을 실제로 잠그는 회계 장치다.

```text
A2가 QQQ를 이겼을 때 수익 일부를 전장에서 빼낸다.
Vault는 표시용이 아니다.
Vault 이동 시 active capital에서 실제 차감된다.
```

## 2. 핵심 ledger

파일:

```text
positions/vault.json
outputs/a2_live/vault_ledger.csv
reports/A2_weekly_vault_review.md
```

스키마:

```json
{
  "hard_vault": 0,
  "reload_vault": 0,
  "last_vault_date": null,
  "month_vault_total": 0,
  "a2_excess_hwm": 0,
  "vault_events": []
}
```

## 3. Vault In 조건

```text
A2_excess = A2_total_return - QQQ_total_return
A2_excess_HWM = max(previous_HWM, A2_excess)
```

발동 조건:

```text
1. 새로운 excess HWM 갱신
2. A2 absolute NAV가 수익 상태
3. QQQ보다 덜 잃은 것만으로는 발동 금지
4. 주 1회 제한 통과
5. 월간 Vault 이동 ≤ 전체 NAV 10%
```

## 4. Vault In 비율

```text
A2 excess HWM ≥ +4%p  → 신규 초과수익분 25% Vault
A2 excess HWM ≥ +8%p  → 신규 초과수익분 추가 25% Vault
A2 excess HWM ≥ +12%p → 신규 초과수익분 50% Vault
```

## 5. Vault source

수익 난 sleeve에서만 이동.

우선순위:

```text
1. TQQQ realized profit
2. Attack realized profit
3. Moonshot realized profit
4. QQQ profit
```

손실 중 sleeve에서 Vault 이동 금지.

## 6. Hard / Reload Vault

```text
Vault inflow 70% → Hard Vault
Vault inflow 30% → Reload Vault
```

Hard Vault:

```text
절대 재투입 금지
공격자금에서 제외
가능하면 별도 계좌/별도 ETF/별도 브로커
```

Reload Vault:

```text
조건부 재투입 가능
한 번에 Reload Vault 25%만 사용
월 1회 이하
```

## 7. Vault Out 조건

Reload Vault만 사용 가능.

```text
Leadership GREEN
TQQQ Decay GREEN
Market Stress not RED
QQQ 20일선 회복
A2 drawdown 회복 중
Attack A급 후보 존재
```

Hard Vault 사용 금지.

## 8. Dynamic Sell / Vault Timing

Vault In은 단순 수익률만이 아니라 위험 신호도 본다.

Vault In 강화 조건:

```text
A2 excess HWM 갱신
AND Leadership YELLOW/RED
OR TQQQ Decay YELLOW/RED
OR LLM Narrative YELLOW/RED
```

즉, 이겼고 위험이 커질 때 더 강하게 잠근다.

Vault Out은 위험이 줄고 기회가 확인될 때만.

## 9. Moonshot Vault

```text
Moonshot 2배 → 원금 회수
Moonshot 3배 → 절반 Vault
Moonshot thesis 깨짐 → 즉시 종료
```

## 10. 완료 기준

```text
Vault 이동이 active NAV에서 실제 차감됨
Hard/Reload balance가 dashboard에 표시됨
Vault-adjusted NAV와 active NAV가 분리됨
주1회/월10% 제한이 코드로 enforce됨
Vaulted Profit이 성공지표로 사용 가능
```


---


# 10 — Risk Dashboard & LLM Council

## 1. 원칙

LLM은 정보참모다. 매수/매도 결정자가 아니다.

```text
LLM = 상태 판정, narrative 요약, bull/bear case
Rule engine = 비중 변경
Ledger = 실제 회계
Human = 최종 override
```

## 2. LLM 입력

```text
QQQ/TQQQ 상태
Leadership basket 상태
VIX/VXN
realized volatility
QQQ drawdown
EDGAR filings
NEG Gate candidates
뉴스/공시/실적/테마 narrative
Attack/Moonshot open positions
Vault trigger status
TQ-DH dip classification candidates
```

## 3. LLM 출력

```json
{
  "market_state": "GREEN|YELLOW|RED",
  "leadership_state": "GREEN|YELLOW|RED",
  "tqqq_state": "GREEN|YELLOW|RED",
  "attack_state": "GREEN|YELLOW|RED",
  "moonshot_state": "OPEN|HOLD_ONLY|LOCKED",
  "vault_state": "ACCUMULATE|HOLD|RELOAD_ALLOWED",
  "narrative_state": "GREEN|YELLOW|RED",
  "top_risks": [],
  "top_attack_candidates": [],
  "top_moonshot_candidates": [],
  "forbidden_actions_today": [],
  "human_review_required": []
}
```

## 4. 금지

```text
LLM이 TQQQ 45% 같은 비중 숫자 제안 금지
LLM이 NVDA 매수 같은 주문 결정 금지
LLM이 성공확률 확정 금지
LLM 점수로 자동 진입 금지
```

## 5. Leadership Risk

감시 대상:

```text
NVDA, MSFT, AAPL, AMZN, GOOGL, META, AVGO, TSLA, AMD, NFLX/COST
```

종목별 1점:

```text
20일선 이탈
50일선 이탈
high-volume down day
earnings gap-down
VWAP 아래 마감
QQQ 대비 상대약세
negative filing/news
```

해석:

```text
0~10 = GREEN
11~25 = YELLOW
26+ = RED
```

## 6. Market Stress

체크:

```text
QQQ 20/50/200일선
VIX/VXN
20일 realized vol
QQQ drawdown
gap-down 연속
HYG/IEF credit stress
Treasury yield shock
```

## 7. TQQQ Decay

체크:

```text
QQQ 20일 수익률 ±3% 이내
realized vol 상승
20일 high-low range 확대
TQQQ realized multiple < 2.3 × QQQ
```

## 8. Narrative Risk

LLM이 판정:

```text
AI/반도체 narrative 약화
빅테크 capex 우려
금리/인플레 narrative 악화
규제/반독점 리스크
earnings call tone 악화
```

출력:

```text
GREEN/YELLOW/RED
근거 3~5줄
어떤 sleeve에 영향 있는지
```

## 9. Daily War Plan

매일 장 시작 전 생성:

```text
reports/A2_daily_war_plan.md
outputs/a2_live/war_plan.json
```

내용:

```text
1. 오늘의 market state
2. leadership state
3. tqqq permission
4. attack permission
5. moonshot permission
6. vault state
7. top risks
8. top candidates
9. forbidden actions
10. human review items
```


---


# 11 — TQ-DH: TQQQ Dip Harvester

## 1. 목적

TQ-DH는 “떨어지면 무조건 TQQQ 추가매수”를 대체한다.

```text
모든 dip을 사지 않는다.
Dip의 종류를 분류한다.
Reload Vault만 사용한다.
Hard Vault는 절대 사용하지 않는다.
구조적 붕괴에서는 TQQQ 매수를 금지한다.
회복 확인 시 QQQ → TQQQ 순서로 진입한다.
```

## 2. 이겨야 할 대상

TQ-DH는 아래보다 나아야 의미 있다.

```text
TQQQ buy-and-hold
TQQQ monthly DCA
TQQQ drawdown DCA
QQQ buy-and-hold
A2 base
```

평가:

```text
최종 NAV
MDD
회복기간
Vaulted Profit
TQQQ sleeve 손실
Reload Vault 사용 효율
```

## 3. Dip Type A — Liquidity Air Pocket

특징:

```text
QQQ drawdown -5% ~ -8%
VIX/VXN 단기 spike 후 둔화
Leadership basket 절반 이상 50일선 위
주도주 earnings/narrative 훼손 없음
credit stress 없음
```

행동:

```text
Reload Vault 25% → TQQQ
3거래일 후 recovery 확인 시 추가 Reload 25% 가능
```

## 4. Dip Type B — Growth Reset

특징:

```text
QQQ drawdown -10% ~ -15%
리더 일부 20/50일선 이탈
AI/빅테크 narrative 유지
VXN 높지만 안정화 시작
QQQ 5일 고점 회복 시도
```

행동:

```text
1차 Reload Vault 25% → QQQ
QQQ 10일 고점 회복 + Leadership YELLOW 이상 → TQQQ 25% reload
```

## 5. Dip Type C — Structural Break

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

## 6. Dip Type D — Capitulation + Repair

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

## 7. 입력 데이터

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

## 8. Reload 규칙

```text
Reload Vault만 사용
Hard Vault 사용 금지
1회 reload = Reload Vault 25%
연속 reload 간격 최소 3거래일
Reload 후 TQQQ sleeve MDD -15% 이상이면 추가 reload 금지
```

## 9. 단순 TQQQ 추가매수와의 차이

단순 DCA:

```text
떨어지면 산다
```

TQ-DH:

```text
왜 떨어졌는지 분류한다
일시적 dip이면 TQQQ
성장주 조정이면 QQQ 먼저
구조적 붕괴면 금지
복구 확인 후 단계적 reload
```

## 10. 구현 파일

```text
engine/a2_tq_dh.py
outputs/a2_live/tq_dh_signals.csv
reports/A2_tq_dh_report.md
```


---


# 12 — Benchmarks, Metrics, Dashboard

## 1. 필수 벤치마크

A2는 QQQ만 이기면 부족하다.

필수 비교:

```text
QQQ buy-and-hold
SPY buy-and-hold
TQQQ buy-and-hold
V7 survival core
A2-Q
A2-T
naive QQQ35/TQQQ35/Cash30
synthetic QQQ 1.4x
TQQQ monthly DCA
TQQQ drawdown DCA
TQ-DH
```

## 2. 구간

```text
3년
12개월
6개월
3개월
live-only since inception
```

## 3. 지표

```text
Total NAV
Total return
MDD
Recovery time
A2 vs QQQ excess
A2 vs naive excess
Vaulted Profit
Vault-adjusted NAV
Hard Vault
Reload Vault
Attack contribution
Moonshot contribution
TQQQ contribution
Dynamic allocator contribution
TQ-DH contribution
```

## 4. Dashboard 필수 항목

```text
A2 active NAV
A2 vault-adjusted NAV
QQQ NAV
SPY NAV
TQQQ NAV
V7 NAV
naive beta NAV
A2-Q vs A2-T
A2 vs QQQ excess
Excess HWM
Vault trigger status
Hard Vault balance
Reload Vault balance
Effective QQQ beta
TQQQ Decay Meter
Booster Rent
Leadership Risk
Market Stress
LLM Narrative State
Attack tokens
Attack candidates
Moonshot draft board
NEG filing flags
Theme concentration
TQ-DH dip type
TQ-DH reload recommendation
```

## 5. 성공 정의

```text
A2 total NAV > QQQ
A2 vault-adjusted NAV > QQQ
Vaulted Profit > 0
A2 > naive beta book
게임 지속 가능
```

## 6. 주의

A2가 QQQ를 이겼지만 naive를 못 이기면:

```text
TQQQ 덕분이지, A2 운영규칙의 부가가치는 미확정.
```

A2가 TQQQ를 못 이기는 것은 당연할 수 있음. A2는 TQQQ보다 안정성과 Vault를 추구한다.

## 7. 대시보드 경고 문구

대시보드 상단에 항상 표시:

```text
A2 is not verified alpha.
A2 is a high-risk QQQ/TQQQ convex book with paper-only Attack/Moonshot optionality.
```


---


# 13 — Implementation Sequence

## Phase 0 — Codex STOP 무결성 패치

목적: 수치 신뢰성 회복.

해야 할 일:

```text
0.1 allocator next-bar 적용
0.2 live ledger와 historical backtest 분리
0.3 to_won 기준 s.iloc[0] 또는 inception NAV로 수정
0.4 QQQ/TQQQ/Attack/Moonshot/Vault/Cash capital accounting 통일
0.5 naive beta benchmark 추가
0.6 old contaminated A2 숫자는 deprecated 처리
```

완료 기준:

```text
same-day look-ahead 없음
live/backtest 라벨 분리
NAV = QQQ + TQQQ + Attack + Moonshot + Vault + Cash
```

## Phase A — Vault 진짜 ledger

파일:

```text
engine/a2_profit_vault.py
positions/vault.json
outputs/a2_live/vault_ledger.csv
reports/A2_weekly_vault_review.md
```

완료 기준:

```text
Vault가 active capital에서 실제 차감
Hard/Reload 분리
주1회/월10% 제한
Vault-adjusted NAV 표시
```

## Phase B — 모듈별 book 회계

파일:

```text
engine/a2_book.py
engine/a2_q_module.py
engine/a2_tqqq_module.py
engine/a2_attack_ledger.py
engine/a2_moonshot_ledger.py
```

완료 기준:

```text
각 sleeve가 별도 ledger 보유
빈 Attack/Moonshot은 cash로 회계
Attack/Moonshot contribution 계산 가능
```

## Phase C — Attack/Moonshot 연료

파일:

```text
engine/a2_attack_scanner.py
engine/a2_attack_tokens.py
engine/a2_moonshot_draft.py
engine/a2_neg_gate.py
reports/moonshot_thesis/*.md
```

완료 기준:

```text
Attack 후보 발생
Attack token 소모/회복
Moonshot draft board 표시
NEG Gate 적용
```

## Phase D — LLM War Plan + Mapping

파일:

```text
engine/a2_daily_war_plan.py
engine/a2_dynamic_allocator.py
config/a2_state_mapping.yaml
outputs/a2_live/war_plan.json
```

완료 기준:

```text
LLM은 state만 출력
mapping engine이 target_weights 생성
5%p 변경 제한 적용
next-bar 적용
```

## Phase E — TQ-DH

파일:

```text
engine/a2_tq_dh.py
outputs/a2_live/tq_dh_signals.csv
reports/A2_tq_dh_report.md
```

완료 기준:

```text
dip type A/B/C/D 분류
Reload Vault만 사용
TQQQ DCA 벤치마크와 비교
```

## Phase F — 분봉 provider

파일:

```text
engine/a2_intraday_provider.py
engine/providers/yfinance_provider.py
engine/providers/polygon_provider.py
engine/providers/alpaca_provider.py
```

완료 기준:

```text
yfinance PROXY 작동
provider interface 통일
DATA_QUALITY 표시
자동집행 전 paper signal만
```

## Phase G — Dashboard/cron

파일:

```text
engine/a2_dashboard.py
outputs/a2_live_dashboard.html
reports/A2_daily_dashboard.md
reports/A2_weekly_review.md
```

완료 기준:

```text
A2 vs QQQ/SPY/TQQQ/naive/V7/A2-Q/A2-T/TQ-DH 표시
Vault 실제 표시
Attack/Moonshot 표시
mini PC cron/systemd 문서화
```


---


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


---


# 15 — Claude Execution Prompt

아래 지시를 그대로 실행하라.

```text
너는 PRAMANA A2 구현 담당 Claude다.
과거 구현에서 look-ahead, live/backtest 혼동, Vault display-only, TQ-DH 누락, Attack/Moonshot 미회계 문제가 반복되었다.
이번에는 이 문서팩만 source of truth로 사용한다.

읽을 순서:
00_INDEX.md
01_A2_MASTER_SPEC.md
02_EIGHT_LAYER_ARCHITECTURE.md
03_DATA_AND_TIME_CONTRACT.md
04_ALLOCATION_AND_MAPPING.md
05~11 모듈 문서
12_BENCHMARKS_AND_DASHBOARD.md
13_IMPLEMENTATION_SEQUENCE.md
14_CODEX_STOP_CHECKLIST.md

우선 구현 순서:
1. Phase 0 Codex STOP 무결성 패치
2. Phase A Vault 진짜 ledger
3. Phase B 모듈별 book 회계
4. Phase C Attack/Moonshot 연료
5. Phase D LLM War Plan + Mapping
6. Phase E TQ-DH
7. Phase F 분봉 provider
8. Phase G Dashboard/cron

핵심 설정:
QQQ 35
TQQQ 35
Attack 10
Moonshot 10
Vault 10

절대 조건:
- LLM은 상태만 판정한다.
- 비중 변경은 mapping engine만 한다.
- 1회 변경 단위 5%p.
- same-day 신호로 same-day 수익 먹지 않는다.
- Vault는 반드시 active capital에서 실제 차감한다.
- Hard Vault는 재투입 금지다.
- TQ-DH는 반드시 구현한다.
- Attack과 Moonshot은 반드시 별도 ledger다.
- A2는 QQQ뿐 아니라 naive beta book과 비교한다.

구현 후 보고:
1. 변경 파일 목록
2. 구현 완료 phase
3. 남은 미구현
4. Codex STOP checklist 자체검사 결과
5. 현재 live/backtest 분리 상태
6. Vault가 진짜 ledger인지 증명
7. A2-Q/A2-T/naive 비교표
8. TQ-DH 모듈 존재 확인
9. Attack/Moonshot ledger 상태
10. 다음 필요한 사용자 입력
```
