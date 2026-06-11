# Pramana Systematic Equity Research Project — Integrated Context Summary v0.1
## 전체 진행상황·의도·잠금 결정·다음 단계 통합 요약

**Date:** 2026-06-10  
**Project:** Pramana systematic equity research / validation / trading operating system  
**Purpose of this file:** 이 파일 하나만 보고 지금까지의 전체 맥락, 의사결정, 왜 이 순서로 진행했는지, 현재 무엇이 잠겼고 무엇이 아직 아닌지 이해할 수 있도록 만든 통합 요약본.  
**Current phase:** Phase 1A / B0 구현 직전 준비 단계  
**Current immediate focus:** Sharadar + EDGAR 데이터 접근·schema 확인 후 B0 data-only benchmark sanity experiment 준비  
**Important warning:** 이 문서는 투자자문, 종목추천, 성과예측, 실거래 전략 문서가 아니다.

---

## 0. Executive Brief

이 프로젝트의 목표는 “좋은 종목을 찍는 AI”를 만드는 것이 아니다.  
목표는 **소규모/솔로+AI가 운영 가능한 systematic equity research / validation / trading operating system**을 만드는 것이다.

핵심 원칙은 다음이다.

```text
데이터가 먼저 정직해야 한다.
비용이 먼저 정직해야 한다.
검증이 먼저 통과돼야 한다.
그 다음에야 모델을 비교한다.
```

현재까지 한 일은 크게 네 가지다.

1. **시스템 철학과 구조 잠금**
   - signal ≠ order
   - alpha ≠ position
   - optimizer가 forecast를 weight로 변환
   - deterministic risk engine이 production 최종 veto
   - LLM은 off-path advisory / critic only

2. **시장·데이터·검증 순서 잠금**
   - U.S.-core first
   - KR-addon later
   - Phase 1A는 boring baseline만
   - B0는 alpha 실험이 아니라 data/benchmark sanity 실험

3. **모델 후보 지도 잠금**
   - Phase 1A: simple factor, cross-sectional rank, 1/N, monotone rank-to-weight
   - Phase 1B: low-DoF challenger
   - Phase 1C: controlled ML challenger
   - Phase 1D: quarantine research
   - 최종 모델 채택은 아직 금지

4. **B0 데이터 소스 방향 설정**
   - Prototype selected direction: Sharadar + EDGAR
   - Production-grade future track: CRSP + Compustat/CCM via WRDS
   - EDGAR-only + free price: rejected for B0
   - Norgate: backup/learned from audit, but not selected due to historical cap input and legal/operational constraints

---

## 1. 가장 중요한 현재 판단

### 1.1 모델이 전부 결정됐는가?

**아니다.**

결정된 것은 “최종 모델”이 아니라 **모델 후보의 실험 순서와 허용 범위**다.

| 질문 | 답 |
|---|---|
| 최종 사용할 모델이 결정됐는가? | **아니오** |
| Phase 1A에서 쓸 baseline 후보는 정해졌는가? | **예** |
| XGBoost/LightGBM 같은 ML을 바로 쓸 수 있는가? | **아니오, Phase 1C 이후** |
| LLM-derived alpha를 바로 쓸 수 있는가? | **아니오, quarantine** |
| raw MVO를 쓸 수 있는가? | **아니오, Phase 1 reject** |
| 지금 해야 할 일은 모델 고도화인가? | **아니오, B0 데이터/벤치마크 sanity 확인** |

정확한 상태:

```text
모델 최종 채택 = NO-GO
모델 후보 분류 = DONE
Phase 1A 허용 모델군 = LOCK
Phase 1B/1C 후보군 = QUEUED
성과 기반 모델 선택 = 아직 시작 전
```

---

### 1.2 데이터 결제가 모델 설계보다 먼저인가?

**정확히는 “최종 모델 설계보다 데이터 결제부터”가 아니다.**

이미 우리가 한 것은 다음과 같다.

```text
1. 시스템 원칙 잠금
2. 데이터/벤치마크/비용 요구사항 잠금
3. 검증 프로토콜 잠금
4. 모델 후보 지도 잠금
5. Phase 1A 실험 설계 잠금
6. B0 구현 준비 문서 작성
```

즉, **모델 후보 지도와 실험 설계는 이미 충분히 선행했다.**  
지금 데이터 접근이 필요한 이유는 모델을 고르기 위해서가 아니라, **B0가 데이터 자체를 검증하는 실험이기 때문**이다.

현재 순서가 맞는 이유:

| 단계 | 왜 필요한가 |
|---|---|
| 모델 후보 지도 | 어떤 모델군을 어느 단계에서 볼지 결정 |
| Phase 1A 설계 | 첫 boring baseline 실험을 어떻게 기록·검증할지 결정 |
| B0 준비 | 데이터/벤치마크 sanity를 먼저 확인 |
| 데이터 접근 | B0를 실제로 실행하려면 필요 |
| 모델 비교 | B0와 Phase 1A가 통과된 뒤 가능 |

따라서 지금 결론은:

```text
고가 production data를 바로 결제하자는 뜻은 아니다.
Sharadar + EDGAR로 B0 sandbox/prototype을 위한 최소 접근을 준비하는 단계다.
```

---

### 1.3 유료 데이터는 Sharadar가 최적인가?

**B0 prototype 기준으로는 Sharadar + EDGAR가 현재 선택된 트랙이다.**  
하지만 “모든 면에서 최적” 또는 “production-grade 최종 데이터”라는 뜻은 아니다.

| 목적 | 현재 판단 |
|---|---|
| B0 prototype / 소규모 시작 / REST API / WSL 친화 | **Sharadar + EDGAR** |
| production-grade / 학술·기관급 정석 | **CRSP + Compustat/CCM via WRDS** |
| 데이터는 강하지만 법무·운영 제약 큼 | **Norgate** |
| 무료 filing/fundamentals floor | **EDGAR** |
| B0 단독 데이터 소스 | **EDGAR-only rejected** |

현재 표현:

```text
Sharadar + EDGAR = B0 prototype track
단, production / redistribution / subscription-lapse use는 아직 미확정
```

---

## 2. 프로젝트 목적과 의도

### 2.1 원래 의도

사용자의 목표는 단순히 “퀀트 모델 추천”이 아니었다.  
목표는 **소규모 팀 또는 개인이 AI를 활용해 운영 가능한 주식형 systematic research system**을 구축하는 것이다.

구체적 목표:

```text
대상 시장: 미국 주식 먼저, 한국 주식 나중
목표 성과: benchmark-relative, after-cost excess return
거래 주기: daily swing / mid-long, mostly cross-sectional
운영 형태: solo/small-team + AI
중요 원칙: data honesty, cost honesty, validation discipline
```

### 2.2 왜 이렇게 오래 설계했는가?

이 프로젝트는 “좋은 모델을 먼저 고르는 방식”이 위험하다고 봤다.

위험한 순서:

```text
모델 먼저 고름 → 백테스트 좋게 나옴 → 비용·데이터 누수 뒤늦게 발견 → 결과 무효
```

우리가 택한 순서:

```text
시장/벤치마크/데이터/비용 잠금
→ 검증 프로토콜 잠금
→ 모델 후보 지도 잠금
→ Phase 1A boring baseline 설계
→ B0 데이터/벤치마크 sanity
→ 그 다음 모델 실험
```

이 순서의 목적은 **과최적화, 미래정보 누수, survivorship bias, 비용 과소추정, LLM 과신**을 막기 위함이다.

---

## 3. 절대 보호 원칙

아래 원칙은 이후 모든 단계에서 유지한다.

| 원칙 | 상태 |
|---|---|
| Signal is not order | **LOCK** |
| Alpha is not position | **LOCK** |
| Forecast는 optimizer를 거쳐 weight로 변환 | **LOCK** |
| Deterministic risk engine이 production 최종 veto | **LOCK** |
| LLM은 off-path advisory / critic only | **LOCK** |
| Free-form LLM output은 주문·사이징·거부권·레짐 전환 불가 | **LOCK** |
| Data gate before model gate | **LOCK** |
| Validation gate before promotion | **LOCK** |
| Firm income / public track record / user-replicable strategy return 분리 | **LOCK** |
| 외부 회사 성과를 사용자 재현 가능 수익으로 import 금지 | **LOCK** |

---

## 4. 지금까지의 단계별 진행 요약

## 4.1 Stage 0A / 0B — 시스템 철학과 운영 구조

### 목적
최신 퀀트/자동화매매 시스템을 참고하되, 알파 복제가 아니라 **운영 구조와 검증 규율**만 추상화하기 위한 단계.

### 핵심 결론

```text
복제할 것은 회사의 수익률이 아니라 구조와 검증 규율이다.
```

잠긴 구조:

```text
data layer
→ feature layer
→ alpha layer
→ portfolio construction / optimizer
→ risk engine
→ cost / execution
→ monitoring
→ governance
```

LLM 위치:

```text
research assistant
adversarial critic
parser / summarizer
hypothesis generator
post-trade explanation

절대 금지:
direct order
direct sizing
direct risk veto
direct regime switch
```

---

## 4.2 DR-1 / DR-1A — Benchmark / Universe / Cost / Data Feasibility

### 목적
시장별 benchmark, universe, cost/tax/slippage, PIT 데이터 가능성을 잠그는 단계.

### 핵심 결론

| 항목 | 결정 |
|---|---|
| benchmark와 trading universe | 분리 |
| internal benchmark | actual universe의 self-built cap-weight TR |
| external benchmark | reporting comparator |
| cost model | commission / tax / FX / spread / slippage / impact 분리 |
| PIT 데이터 | 필수 |
| survivorship/delisting/CA | 필수 |
| KR | 가능하지만 PIT/free-float/NXT/SOR/license 확인 필요 |
| US | 데이터 생태계가 더 성숙 |

---

## 4.3 DR-2A — KR Data / PIT Architecture

### 목적
한국 시장 데이터 구조를 공식/무료 소스로 어디까지 만들 수 있는지 확인.

### 결론

| 항목 | 상태 |
|---|---|
| KR free-official prototype | GO |
| KR alpha research | NO-GO |
| KR PIT membership | Provisional |
| Free-float PIT history | Requires vendor |
| NXT/SOR | separate execution regime |
| KR production-grade | vendor/legal/broker confirmation 필요 |

KR은 버린 게 아니라 **addon/later sleeve**로 밀렸다.

---

## 4.4 DR-2B — US Data / PIT Architecture

### 목적
미국 시장 데이터 구조를 EDGAR, CRSP, Compustat/WRDS, Norgate/Sharadar 등으로 평가.

### 결론

| 항목 | 상태 |
|---|---|
| US data prototype | GO |
| US alpha research | NO-GO until validation gates |
| EDGAR | official filing/fundamentals floor |
| CRSP/Compustat/WRDS | production-grade candidate |
| Norgate/Sharadar | cheap prototype candidates |
| CRSP delisting return | useful but missing-code/imputation policy 필요 |

---

## 4.5 Market Architecture Decision

### 최종 시장 방향

```text
US-core first
KR-addon later
```

이유:

| 이유 | 설명 |
|---|---|
| US 데이터 생태계 성숙 | EDGAR + commercial vendors + CRSP/WRDS |
| KR self-build 부담 | PIT membership, CA/dividend, delisting, NXT/SOR |
| 혼합 패널 위험 | US/KR을 처음부터 섞으면 검증 복잡도 급증 |
| 구조 재사용 가능 | shared research OS + market-specific adapters |

---

## 4.6 DR-3 — Validation Protocol

### 목적
모든 미래 모델이 통과해야 하는 검증 규칙을 잠그는 단계.

### 핵심 결론

| 항목 | 상태 |
|---|---|
| data acceptance gate | LOCK |
| PIT/no-lookahead tests | LOCK |
| OOS / walk-forward | LOCK |
| final untouched holdout | LOCK |
| cost stress | LOCK |
| trial registry | LOCK |
| promotion/quarantine/reject lifecycle | LOCK |
| paper/shadow gate | LOCK as concept |
| DSR/PBO/t-stat thresholds | method lock, numeric threshold provisional |

중요한 조정:

```text
DSR 95%, PBO < 0.20, t-stat > 3 같은 숫자는 universal hard rule이 아니다.
trial count, search budget, Sharpe dispersion에 따라 calibration해야 한다.
```

---

## 4.7 DR-4 — Layer-by-layer Model Candidate Map

### 목적
어떤 모델군을 어느 레이어에 배치할지 정리하되, 최종 모델 채택은 금지.

### 최종 모델 후보 분류

| 분류 | 대표 후보 | 상태 |
|---|---|---|
| Baseline candidate | simple factor, cross-sectional rank, equal-weight blend, 1/N, monotone rank-to-weight | Phase 1A |
| Low-DoF challenger | penalized regression, deterministic calendar feature | Phase 1B |
| Challenger candidate | tree ensemble, constrained optimizer, HRP/robust optimizer, nonlinear cost model | Phase 1C |
| Exploratory / quarantine | alternative data, LLM weak signal, regime model | Phase 1D |
| Reject for Phase 1 | raw MVO, free-form LLM trading, RL trading agent, autonomous retraining | Reject |

가장 중요한 패치:

```text
boring baseline을 더 지루하게 낮춤.
penalized regression과 optimizer 고도화는 baseline이 아니라 challenger.
tree ensemble은 challenger지만 heavy DSR/PBO gate 필요.
deep/TSFM/foundation은 Phase 1 core alpha로 reject.
```

---

## 4.8 Phase 1 Final Experiment Design

### 목적
Phase 1A boring baseline 실험을 어떻게 기록하고, 검증하고, 판정할지 설계.

### 산출물

```text
experiment registry schema
config schema set
data acceptance gate G-01~G-14
OOS / walk-forward rules
B0–B11 experiment matrix
metrics policy
cost stress configuration
trial budget policy
lifecycle
report template
failure log template
Phase 1B / 1C gate
```

### 핵심 결론

```text
Phase 1A final design = LOCKED
Implementation = NO-GO until Pre-Implementation Gate passes
First implementation target = B0 only
```

---

## 4.9 Pre-Implementation Gate & B0 Prep

### 목적
구현 전에 필요한 체크리스트와 B0 준비사항을 정리.

### B0 정의

```text
B0 = data-only benchmark sanity experiment
```

B0는 알파 실험이 아니다.  
B0의 목적은 self-built internal benchmark를 정직하게 재구성할 수 있는지 확인하는 것이다.

B0에서 확인할 것:

```text
PIT universe replay
inactive/delisted inclusion
corporate action reconciliation
dividend/distribution reconciliation
missing OHLCV policy
identifier mapping
benchmark reconstruction
data lineage/hash
license lineage
```

---

## 4.10 B0 Implementation Scaffold

### 목적
B0 실행 전 파일 구조, config template, registry row, data gate report, benchmark drift report 등을 정의.

### 산출물

```text
folder structure
source_manifest.md
experiment_registry.csv
trial_family_registry.csv
approval_log.md
failure_log.md
data_snapshot_config.yml
universe_config.yml
benchmark_config.yml
validation_config.yml
data gate report template
benchmark drift report template
B0 final decision template
```

---

## 4.11 B0 Data Source Track Decision

### 목적
B0를 어떤 데이터 소스로 실행할지 결정.

### Primary + Red-team 병합 후 결론

| 트랙 | 최종 상태 |
|---|---|
| Sharadar + EDGAR | B0 prototype track |
| Norgate + EDGAR | backup / not selected |
| CRSP + Compustat/CCM via WRDS | production-grade deferred |
| EDGAR-only + free price | reject |

중요한 판단:

```text
Sharadar 확정 이유:
- SEP: adjusted/unadjusted price
- DAILY: daily marketcap
- TICKERS: permaticker, isdelisted
- ACTIONS: dividends/splits
- S&P500 구성종목 이력 가능
- REST/API, WSL 친화

주의:
production/redistribution/subscription-lapse use는 아직 미확정
```

---

## 5. 현재 Lock / 확정 상태

## 5.1 시스템 원칙

| 항목 | 상태 |
|---|---|
| signal ≠ order | **LOCK** |
| alpha ≠ position | **LOCK** |
| risk engine 최종 veto | **LOCK** |
| LLM off-path | **LOCK** |
| data gate before model gate | **LOCK** |
| validation before promotion | **LOCK** |

## 5.2 시장

| 항목 | 상태 |
|---|---|
| U.S.-core first | **LOCK** |
| KR-addon later | **LOCK** |
| US Phase 1A | 진행 중 |
| KR alpha research | 아직 NO-GO |

## 5.3 데이터

| 항목 | 상태 |
|---|---|
| B0 prototype data source | **Sharadar + EDGAR** |
| EDGAR role | filing/fundamentals floor |
| Sharadar role | price/return/universe/CA/marketcap |
| Norgate role | backup, not selected |
| CRSP/WRDS role | production-grade deferred |
| EDGAR-only + free price | reject |
| production license | Unknown |
| redistribution | Unknown/prohibited |
| subscription-lapse data use | Unknown |

## 5.4 모델

| 항목 | 상태 |
|---|---|
| Phase 1A boring baseline only | **LOCK** |
| Simple factor / rank / 1/N | **LOCK for Phase 1A** |
| Penalized regression | Phase 1B |
| Tree ensemble | Phase 1C |
| TSFM/deep/foundation | no Phase 1 core alpha |
| LLM-derived alpha | quarantine only |
| Raw MVO | reject |
| final model selection | **NOT YET** |

## 5.5 실험

| 항목 | 상태 |
|---|---|
| B0 first | **LOCK** |
| B0 alpha-free | **LOCK** |
| B1+ only after B0 | **LOCK** |
| B0 failure blocks alpha | **LOCK** |

---

## 6. 현재 작업 위치

현재 위치:

```text
Phase 1A / B0 구현 직전
```

정확히는:

```text
Sharadar + EDGAR track selected
→ API/schema/license evidence capture 필요
→ config TODO 채우기 필요
→ data snapshot export/hash 필요
→ 그 다음 B0 구현 가능
```

현재는 코드 구현 전 단계다.

---

## 7. 지금 바로 해야 할 일

### 7.1 Sharadar API / schema 확인

해야 할 것:

```text
1. Nasdaq Data Link / Sharadar 접근 준비
2. API key 확보
3. SF0 또는 sample API 호출
4. SEP schema 확인
5. DAILY schema 확인
6. TICKERS schema 확인
7. ACTIONS schema 확인
8. 가능하면 S&P500 constituents schema 확인
9. license/terms 페이지 저장
10. bulk export 가능 여부 확인
```

### 7.2 B0 config TODO 채우기

채울 파일:

```text
data_snapshot_config
universe_config
benchmark_config
validation_config
source_manifest
experiment_registry row
```

### 7.3 snapshot/hash 준비

필요한 것:

```text
raw export path
data hash
schema capture evidence
license evidence
calendar version
code_version
environment_hash
```

---

## 8. 아직 하면 안 되는 것

아직 금지:

```text
XGBoost 구현
LightGBM 구현
CatBoost 구현
NLP/event alpha
LLM alpha
optimizer 고도화
HRP/robust optimizer
raw MVO
실거래
종목 추천
성과 예측
Phase 1B/1C 이동
```

왜냐하면 B0가 아직 끝나지 않았기 때문이다.

---

## 9. Deep Research 사용 기준

### 지금 단계에서 Deep Research가 필요한 경우

| 상황 | Deep Research 필요 |
|---|---|
| 데이터 벤더 최종 비교를 다시 해야 할 때 | Yes |
| Sharadar 약관/라이선스가 모호해서 공식 비교 필요 | Yes |
| delisting imputation 정책을 새로 잠그려 할 때 | Yes |
| cost/slippage 모델을 외부 문헌으로 정해야 할 때 | Yes |
| Phase 1B/1C 후보를 열기 전 red-team | Yes |

### 지금 단계에서 Deep Research가 필요 없는 경우

| 작업 | Deep Research 필요 |
|---|---|
| API key 확인 | No |
| sample API 호출 | No |
| schema capture | No |
| config TODO 채우기 | No |
| B0 registry row 작성 | No |
| folder/template 생성 | No |
| 구현 코드 작성 | No |

간단한 기준:

```text
외부 지식을 새로 검증해야 하면 Deep Research.
이미 잠긴 설계를 실행 파일/양식/config로 바꾸는 건 일반 작업.
코드 구현은 Deep Research가 아니라 구현 작업.
```

---

## 10. 다음 단계 로드맵

## Immediate Next

```text
Sharadar/Nasdaq Data Link API 연결 확인
→ schema capture
→ license/terms evidence 저장
→ B0 config TODO 채우기
```

## Then

```text
B0 implementation
→ data gates G-01/G-04/G-05/G-06/G-07/G-08/G-09/G-11/G-12/G-14
→ self-built cap-weight TR benchmark reconstruction
→ benchmark drift report
→ reproducibility manifest
→ reviewer sign-off
```

## If B0 passes

```text
B1 = 1/N universe baseline
```

## If B0 fails

```text
Stop alpha path.
Return to data source / universe / benchmark design.
```

## If Phase 1A passes

```text
Phase 1B low-DoF challenger planning
```

---

## 11. Artifact Index

현재까지 생성된 핵심 문서:

| File | Purpose |
|---|---|
| Integrated_Lock_Sheet_DR1_to_DR2B_v0.1.md | DR-1~DR-2B 통합 잠금 |
| DR-3_Final_Validation_Protocol_v0.1.md | 검증 프로토콜 |
| DR-4_Final_Model_Candidate_Map_v0.1.md | 모델 후보 지도 |
| Phase_1_Final_Experiment_Design_v0.1.md | Phase 1A 실험 설계 |
| Pre_Implementation_Gate_and_B0_Prep_v0.1.md | 구현 전 체크리스트 |
| B0_Implementation_Scaffold_v0.1.md | B0 scaffold |
| B0_Data_Source_Track_Final_Decision_v0.1.md | 데이터 소스 최종 결정 |
| Vendor_License_Confirmation_Mini_Check_v0.1.md | 벤더/라이선스 확인표 |
| B0_Sharadar_EDGAR_Config_Fill_v0.1.md | Sharadar+EDGAR config 적용 |
| Sharadar_API_Schema_Checklist_and_Config_TODO_v0.1.md | Sharadar API/schema 확인용 TODO |

---

## 12. Short Mental Model

```text
우리는 아직 모델을 고르는 단계가 아니다.
우리는 모델을 검증할 수 있는 실험장을 짓는 중이다.

그 실험장의 첫 삽이 B0다.
B0는 alpha가 아니라 data/benchmark sanity다.

B0가 성공하면 B1부터 boring baseline을 본다.
Boring baseline이 통과하면 그때 Phase 1B/1C 모델을 연다.
```

---

## 13. If Another Person Reads This

이 프로젝트를 처음 보는 사람은 이렇게 이해하면 된다.

```text
이 프로젝트는 개인/소규모 팀이 AI를 활용해
미국 주식 중심 systematic equity research system을 만들기 위한 장기 설계다.

현재까지 모델을 고른 것이 아니라,
데이터·비용·검증·실험 기록 체계를 먼저 잠갔다.

미국 시장을 먼저 하고, 한국 시장은 나중에 adapter로 붙인다.

현재는 Phase 1A의 첫 실험인 B0를 준비 중이다.
B0는 데이터를 검증하는 실험이고, alpha 모델은 없다.

B0를 위해 Sharadar + EDGAR를 prototype 데이터 트랙으로 선택했다.
다음은 Sharadar API/schema를 실제로 확인하고 config를 채워 B0를 실행하는 것이다.
```
