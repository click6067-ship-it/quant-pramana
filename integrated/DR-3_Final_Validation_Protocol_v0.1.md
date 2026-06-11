# DR-3 Final Validation Protocol v0.1
## GPT DR-3 Primary + Claude DR-3 Red-team 병합본

**Date:** 2026-06-08  
**Project:** Pramana systematic equity research / validation / trading operating system  
**Scope:** Validation protocol before any layer-by-layer model candidate research.  
**Non-scope:** alpha model selection, TSFM/LLM model adoption, company benchmarking, final strategy selection.

---

## 0. Final Verdict

| 항목 | 최종 판정 |
|---|---|
| DR-3 상태 | **PATCHED-LOCK** |
| Validation framework | **LOCK** |
| Numeric thresholds | **PROVISIONAL / calibrated house rules** |
| Model candidate map 진입 | **GO after this protocol is accepted** |
| Actual model promotion | **NO-GO until validation artifacts and gates pass** |
| US-core | Primary validation pilot |
| KR-addon | Later adapter; validation protocol reused with KR-specific cost/data gates |

### 한 문장 결론

검증 프레임은 잠근다.  
다만 `DSR 95%`, `PBO < 0.20`, `family-level t-stat > 3`, `8주 paper + 8주 shadow`, `5%/10% ADV` 같은 숫자 임계값은 출처 기반 hard rule이 아니라 **calibrated house rule**로 둔다.

---

## 1. Locked Validation Principles

| Principle | Status | Meaning |
|---|---:|---|
| Data gate before model gate | LOCK | 데이터/PIT/benchmark/cost 검증 전 모델 리서치 금지 |
| PIT safety | LOCK | 미래 구성종목·미래 재무정보·미래 공시 사용 금지 |
| Survivorship safety | LOCK | inactive/delisted securities 또는 이에 준하는 처리 필수 |
| Corporate-action safety | LOCK | splits, dividends, distributions, mergers, spin-offs reconciliation 필수 |
| Benchmark sanity | LOCK | self-built cap-weight TR sanity와 external benchmark drift 설명 필수 |
| OOS validation | LOCK | time-ordered out-of-sample 검증 필수 |
| Walk-forward / rolling evaluation | LOCK | expanding/rolling 재추정 프로토콜 필요 |
| Cost honesty | LOCK | after-cost 평가, cost stress, turnover/capacity check 필수 |
| Multiple-testing control | LOCK | trial/hypothesis/feature/model registry 필요 |
| Promotion lifecycle | LOCK | idea → hypothesis → data-ready → OOS → paper/shadow → production 후보 단계화 |
| Paper / shadow gate | LOCK as concept | 기간과 수치는 provisional |
| Human approval | LOCK | production 후보 승격에는 human approval 필요 |
| LLM role | LOCK | off-path advisory/critic only; validation authority 없음 |

---

## 2. What Claude Changed

Claude DR-3 Red-team이 GPT DR-3에서 조정해야 한다고 본 핵심 사항:

| 항목 | GPT Primary 처리 | Claude 감사 | 최종 병합 |
|---|---|---|---|
| family-level t-stat > 3 | hard-ish gate 후보 | Harvey-Liu-Zhu 계열 근거는 맞지만 flat constant 아님 | **method lock / value provisional** |
| DSR 95% | 통과 기준 후보 | trial count N, Sharpe dispersion, skew/kurtosis 없으면 계산 불가 | **method lock / threshold calibrated** |
| PBO < 0.20 | house gate 후보 | 원 논문 cutoff는 0.05, 0.20은 더 완화된 house rule | **diagnostic/house rule** |
| CPCV | 중요 검증 수단 | overlapping labels 있을 때 중요, non-overlap 월간 전략엔 과설계 가능 | **conditional / optional** |
| purging / embargo | 포함 | horizon overlap과 label leakage에 따라 필요 | **conditional lock** |
| paper/shadow 8주+8주 | 운영 게이트 후보 | 고정기간 근거 약함 | **provisional house rule** |
| ADV 5% / 10% cap | capacity 후보 | 전략/유동성별 calibration 필요 | **provisional house rule** |

---

## 3. DR-3 Lock Decision Table

| Item | Final Status | Notes |
|---|---:|---|
| Data acceptance gate | LOCK | 모델 리서치 전 필수 |
| PIT membership test | LOCK | US/KR 모두 적용 |
| No-future-fundamentals test | LOCK | filing timestamp 기준 |
| Delisting / inactive handling test | LOCK | US는 delisting imputation, KR은 casebook/prototype 필요 |
| Corporate-action reconciliation | LOCK | 가격·배당·조정계수 정합성 |
| Self-built benchmark sanity | LOCK | actual universe 기준 내부 benchmark |
| Train / validation / test split | LOCK | chronological split |
| Walk-forward protocol | LOCK | rolling/expanding 둘 다 설계 가능 |
| Purged / embargoed validation | CONDITIONAL LOCK | overlapping labels / horizon leakage 있을 때 필수 |
| CPCV | PROVISIONAL / optional | model-family comparison이나 overlap 심한 경우 사용 |
| Final untouched holdout | LOCK | 최종 1회성 검증 세트 |
| Benchmark-relative metrics | LOCK | after-cost excess return, tracking error, IR 등 |
| Cost stress | LOCK | base + stress scenario 필수 |
| 2x / 3x cost multipliers | PROVISIONAL | house rule; market/strategy별 calibration 필요 |
| Turnover / capacity check | LOCK | ADV participation, liquidity, turnover |
| ADV 5% median / 10% max | PROVISIONAL | house rule |
| DSR | METHOD LOCK | threshold requires N and trial distribution |
| PBO | METHOD LOCK | 0.20 is not primary-source hard cutoff |
| Deflated Sharpe | METHOD LOCK | multiplicity-adjusted diagnostic |
| family-level t-stat hurdle | METHOD LOCK | value depends on number of tests and error-control target |
| Model registry | LOCK | all trials logged |
| Feature registry | LOCK | feature provenance and timestamping |
| Hypothesis registry | LOCK | preregister research rationale |
| Paper / shadow trading gate | LOCK as concept | duration provisional |
| Promotion / quarantine / reject rules | LOCK | lifecycle mandatory |

---

## 4. Data Acceptance Gate

No model may enter alpha backtesting until the relevant market sleeve passes the data gate.

| Test ID | Test | Applies to | Pass condition | Failure action |
|---|---|---|---|---|
| D-01 | PIT membership replay | US/KR | as-of-date universe table has no future constituents | block alpha |
| D-02 | No future fundamentals | US/KR | feature timestamp >= filing/availability timestamp | block alpha |
| D-03 | Filing lag integrity | US/KR | filings only available after accepted date/time | block alpha |
| D-04 | Delisting / inactive inclusion | US/KR | inactive/delisted names handled or explicit imputation policy exists | block alpha |
| D-05 | Corporate action reconciliation | US/KR | split/dividend/distribution adjustments reconcile to raw data | block alpha |
| D-06 | Dividend/distribution reconciliation | US/KR | cash distributions correctly included/excluded by return definition | block alpha |
| D-07 | Benchmark replication sanity | US/KR | self-built benchmark drift explained and bounded | block alpha |
| D-08 | Missing OHLCV check | US/KR | missingness policy documented and tested | quarantine data |
| D-09 | Abnormal return / split detection | US/KR | abnormal jumps reconciled to CA or flagged | quarantine data |
| D-10 | Identifier mapping integrity | US/KR | stable security identifiers and link history validated | block alpha |
| D-11 | Data version lineage | US/KR | raw source ID, release, vendor version, transformation hash logged | block alpha |
| D-12 | License lineage | US/KR | research/paper/production usage rights known | block production |

---

## 5. OOS / Walk-forward Protocol

### Required structure

1. **Chronological split only**  
   Random split is prohibited for time-series and cross-sectional market data.

2. **Train / validation / test separation**  
   Validation is for tuning; test is not touched until final evaluation.

3. **Walk-forward evaluation**  
   Use rolling or expanding windows. The choice is a protocol parameter, not a model-specific convenience.

4. **Final untouched holdout**  
   Final holdout is used once after model-family and hyperparameter decisions.

5. **Regime coverage check**  
   OOS window must cover at least distinct volatility/rate/market regimes where feasible.

6. **No test-set tuning**  
   Any post-test modification restarts the evidence clock.

### Conditional purging / embargo

| Condition | Treatment |
|---|---|
| Overlapping labels / holding periods | Purging and embargo required |
| Multi-day forward returns with overlapping observations | Purging strongly recommended |
| Monthly non-overlapping cross-sectional rebalance | Full CPCV may be overkill; simpler walk-forward + final holdout may suffice |
| Model-family comparison across many trials | CPCV/PBO or equivalent diagnostic recommended |

---

## 6. Multiple Testing / Overfitting Control

### Locked controls

| Risk | Control |
|---|---|
| Too many unlogged trials | hypothesis registry |
| Feature mining | feature registry |
| Hyperparameter search | search log |
| Model-family shopping | model registry |
| Data snooping | untouched holdout + multiple-testing diagnostic |
| Lucky Sharpe | deflated Sharpe / DSR |
| Backtest overfitting | PBO / CSCV-style analysis where appropriate |
| Researcher degrees of freedom | preregistered analysis plan and failure log |

### Threshold treatment

| Metric | Final treatment |
|---|---|
| DSR | method locked; threshold calibrated by trial count and Sharpe distribution |
| PBO | method locked; cutoff provisional; 0.05 is primary-source strict reference, 0.20 is house diagnostic only |
| t-stat hurdle | method locked; value depends on test count and error-control target |
| Sharpe / IR | diagnostic + soft gate unless calibrated |
| p-value | diagnostic only unless multiple-testing adjusted |

---

## 7. Cost / Slippage / Capacity Protocol

### Locked requirements

1. Every backtest must be reported **pre-cost and after-cost**.
2. Cost must be decomposed into commission, tax/fees, FX, spread, slippage, market impact.
3. Turnover must be reported.
4. Capacity must be estimated using ADV participation or equivalent liquidity constraint.
5. Strategy must survive at least one conservative cost-stress scenario.
6. KR and US cost adapters must remain separate.
7. KR later must support KRX-only vs SOR-enabled execution regimes.

### Provisional house rules

| Rule | Status |
|---|---|
| 2x cost stress | Provisional baseline |
| 3x cost stress | Provisional adverse case |
| 5% ADV median participation | Provisional |
| 10% ADV max participation | Provisional |
| Fixed slippage bps | Not sufficient alone |
| Market impact model | Provisional until empirical calibration |

---

## 8. Metrics Policy

| Metric | Treatment |
|---|---|
| Annualized after-cost excess return | Required |
| Information ratio | Required |
| Tracking error | Required |
| Sharpe / Sortino | Diagnostic |
| Max drawdown | Required |
| Drawdown duration | Diagnostic |
| Turnover | Required |
| Capacity / ADV usage | Required |
| Rank IC mean | Required for cross-sectional signal diagnostics |
| Rank IC stability | Required |
| Quantile portfolio returns | Required |
| Hit rate | Optional / diagnostic |
| Tail risk | Required diagnostic |
| DSR / deflated Sharpe | Required diagnostic before promotion |
| PBO | Required where many trials/model families are compared |
| t-stat | Diagnostic unless adjusted for multiple testing |

---

## 9. Paper / Shadow Trading Gate

### Locked concept

No model goes directly from backtest to production. It must pass paper/shadow validation.

### Provisional operational rule

| Gate | Status |
|---|---|
| Paper trading | Required, duration provisional |
| Shadow trading | Required before live production, duration provisional |
| 8-week paper + 8-week shadow | House rule candidate, not hard evidence-based lock |
| Broker reconciliation | Required |
| Daily audit report | Required |
| Signal freshness check | Required |
| Missing data handling test | Required |
| Kill switch test | Required |
| Rollback procedure | Required |

### Paper/shadow logs

- expected vs observed signal
- expected vs observed weights
- simulated orders
- broker/paper fills
- slippage drift
- missing data
- rejected orders
- risk veto events
- benchmark drift
- daily PnL attribution
- manual overrides

---

## 10. Promotion / Quarantine / Reject Lifecycle

| State | Entry requirement | Exit requirement |
|---|---|---|
| Idea | research hypothesis | registered hypothesis |
| Registered hypothesis | hypothesis log | data availability confirmed |
| Data-ready | data acceptance gate passed | initial backtest |
| Backtest candidate | backtest config/version logged | OOS candidate |
| OOS candidate | walk-forward / holdout evidence | paper candidate or quarantine |
| Paper candidate | after-cost OOS survives | shadow candidate |
| Shadow candidate | paper/live reconciliation stable | production candidate |
| Production candidate | human approval + risk sign-off | production or reject |
| Production | active monitoring | continue / quarantine / retire |
| Quarantine | failed gate or instability | patch or retire |
| Retired | persistent failure | archived |

---

## 11. Validation Artifacts

Every future model candidate must produce:

1. Research memo
2. Hypothesis registry entry
3. Data snapshot ID
4. Universe config
5. Benchmark config
6. Feature snapshot ID
7. Model config
8. Cost config
9. Backtest config
10. OOS report
11. Multiple-testing report
12. Cost-stress report
13. Capacity report
14. Paper/shadow report
15. Approval log
16. Failure log
17. Postmortem template

---

## 12. Final Recommendation

| Question | Decision |
|---|---|
| Proceed to layer-by-layer model candidate map? | **YES, after accepting this DR-3 Final Protocol** |
| Proceed directly to model implementation? | **NO** |
| Proceed directly to production/paper trading? | **NO** |
| Need more Deep Research before model map? | **No, not for validation protocol** |
| Next task | **DR-4 Layer-by-layer Model Candidate Map** |

---

## 13. DR-4 Handoff

DR-4 may begin only under these constraints:

1. DR-4 is a **model candidate map**, not final model selection.
2. Every model family must be mapped to:
   - candidate layer
   - required data
   - failure mode
   - validation gate
   - cost/capacity risk
   - small-team feasibility
3. No model is adopted in DR-4.
4. Model families must be classified as:
   - baseline candidate
   - challenger candidate
   - exploratory / quarantine
   - reject for Phase 1
5. DR-4 must preserve:
   - data gate first
   - validation gate before promotion
   - US-core first, KR-addon later
   - LLM off-path
   - signal ≠ order
   - alpha ≠ position
