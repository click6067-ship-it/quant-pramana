# Phase 1 Final Experiment Design v0.1
## Phase 1A Boring Baseline Experiment Design — Final Merge

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-10  
**Status:** **FINAL DESIGN LOCKED / IMPLEMENTATION-GATED**  
**Merged from:** Claude Phase 1A Primary + ChatGPT Red-team Audit  
**Scope:** Phase 1A boring baseline experiment design only  
**Non-scope:** implementation code, live trading, backtest results, stock recommendation, performance forecast, final model adoption

---

## 0. Executive Brief

Phase 1A의 목적은 **돈 버는 모델을 찾는 것**이 아니다.  
목적은 **데이터·벤치마크·비용·검증·기록 체계가 정직하게 작동하는지 증명하는 것**이다.

### One-line Decision

> **Phase 1A는 boring baseline만 설계한다.**
>  
> B0 데이터/벤치마크 sanity → B1 1/N baseline → B2–B5 simple factor sleeves → B6 attribution diagnostic → B7/B8 rank/composite sanity → B9/B10 construction/risk sensitivity → B11 cost-stress suite 순서로 진행한다.

### Final Gate

| Area | Decision |
|---|---|
| Phase 1A final design | **LOCKED** |
| Immediate implementation | **NO-GO until Pre-Implementation Gate passes** |
| First implementation target | **B0 data-only benchmark sanity** |
| ML / tree / NLP / LLM-alpha | **Blocked until later phases** |
| Phase 1B | Only after Phase 1A gates pass |
| Phase 1C | Only after Phase 1B and multiple-testing machinery pass |

---

## 1. Provenance and Merge Decision

| Input | Role | Final use |
|---|---|---|
| Integrated Lock Sheet DR1→DR2B | Upper-level market/data/cost lock | US-core first, KR-addon later, data/cost honesty |
| DR-3 Final Validation Protocol | Validation lock | data gate, OOS/WF, cost stress, trial registry, lifecycle |
| DR-4 Final Model Candidate Map | Model candidate lock | Phase 1A boring baseline only |
| Claude Phase 1A Primary | Primary experiment design | Base structure |
| ChatGPT Phase 1A Red-team | Adversarial audit | Required patches |

### Red-team patches incorporated

1. Added reproducibility fields to registry: `code_version`, `environment_hash`, `calendar_version`, `rebalance_calendar`, `random_seed_policy`.
2. Added legal/data fields: `data_license_state`, `vendor_confirmation_state`, `broker_confirmation_state`, `legal_confirmation_state`.
3. Added trial-control fields: `trial_family_id`, `family_type`, `effective_N_method`, `budget_cap_rule`.
4. Added report links: `data_gate_report_link`, `benchmark_drift_report_link`, `cost_stress_report_link`, `approval_log_link`.
5. Added `G-13 Restatement Leakage Gate`.
6. Added `G-14 License Lineage Gate`.
7. Split benchmark drift into internal reconstruction error vs external comparator difference.
8. Made one primary walk-forward scheme mandatory; alternatives become new trial family.
9. Reclassified B6 as attribution diagnostic, not promotion experiment.
10. Reclassified B8 as merge/invariance diagnostic.
11. Split B9 and B10 into pre-registered sensitivity families.
12. Reclassified B11 as mandatory cost-stress suite, not standalone alpha experiment.
13. Removed automatic promote/reject based on provisional thresholds.
14. Added execution support and paper/shadow artifacts.
15. Added reviewer sign-off to data-gate-passed, OOS-evaluated, quarantine release, and Phase 1B promotion.

---

## 2. Phase 1A Scope Lock

### Included

| Included item | Layer | Treatment |
|---|---|---|
| PIT core characteristics | L3 | baseline substrate |
| Simple factor sleeves | L3/L4 | baseline signal |
| Cross-sectional rank composite | L4 | baseline alpha |
| Equal-weight alpha blend | L5 | baseline ensemble |
| 1/N portfolio | L6 | primary boring portfolio baseline |
| Equal-weight top-N | L6 | baseline variant |
| Monotone rank-to-weight | L6 | baseline variant |
| Basic hard risk cap | L7 | deterministic risk control |
| Simple cost haircut | L8 | base cost realism |
| Basic execution support | L9 | operational baseline |
| Paper/shadow monitoring | L11 | operational validation |

### Excluded from Phase 1A

| Excluded item | Reason |
|---|---|
| Penalized regression | Phase 1B low-DoF challenger |
| Learned blending | Phase 1B/1C, not baseline |
| Tree ensemble / XGBoost / LightGBM / CatBoost | Phase 1C controlled ML challenger |
| NLP/event ML | later conditional challenger or quarantine |
| Robust optimizer / HRP / constrained MVO | later challenger |
| Raw MVO | rejected for Phase 1 |
| Nonlinear market-impact model | later challenger |
| Regime model | exploratory/quarantine |
| Alternative data | exploratory/quarantine |
| TSFM / financial foundation / deep sequence | reject as Phase 1 core alpha; quarantine overlay only |
| LLM-derived alpha | quarantine only if schema-locked |
| RL / black-box meta-allocator | reject for Phase 1 |
| Autonomous online retraining | reject for Phase 1 |
| Free-form LLM trading control | forbidden |

---

## 3. Phase 1A Objective

Phase 1A tests whether the research system can produce a **reproducible, PIT-safe, after-cost, benchmark-relative boring baseline**.

It must prove:

| Objective | Meaning |
|---|---|
| Data integrity | no future data, no survivorship bias, correct corporate actions, correct delisting handling |
| Benchmark sanity | self-built internal benchmark is reconstructable and explainable |
| Cost realism | base/adverse costs are applied and stress-tested |
| Baseline reproducibility | same configs + same snapshot reproduce same results |
| OOS/WF machinery | chronological split, walk-forward, final holdout work correctly |
| Trial discipline | every trial, abandoned trial, and variant is logged |
| Failure logging | failures are classified and traceable |
| Promotion discipline | no automatic promotion from provisional thresholds |
| Operational readiness | execution support and paper/shadow artifacts exist before moving forward |

---

## 4. Pre-Implementation Gate

Implementation may not begin until this gate passes.

| Gate | Pass condition | Failure action |
|---|---|---|
| P0-01 Source files | Final design, DR-3, DR-4, Lock Sheet available and versioned | block implementation |
| P0-02 Data source chosen | U.S. data source track selected: EDGAR floor + survivorship-aware price/universe source | block B0 |
| P0-03 License state | research/paper/production rights marked; unknown = fail-closed or sandbox-only | block non-sandbox |
| P0-04 Calendar | trading calendar version fixed | block B0 |
| P0-05 Code/environment tracking | code_version and environment_hash mechanism defined | block B0 |
| P0-06 Registry ready | required registry fields implemented | block all experiments |
| P0-07 Data gate runner | G-01 to G-14 checklist executable or manually auditable | block all experiments |
| P0-08 Benchmark drift report | template exists | block B0 |
| P0-09 Cost stress report | template exists | block B1+ |
| P0-10 Failure log | template exists | block all experiments |
| P0-11 Approval log | reviewer/approver fields exist | block promotion |
| P0-12 Denylist lint | Phase 1A excluded models cannot enter configs | block all experiments |

---

## 5. Final Experiment Registry Schema

| Field | Type | Required | Example | Purpose |
|---|---:|---:|---|---|
| experiment_id | string | Y | P1A-B02-20260610-01 | immutable experiment key |
| experiment_name | string | Y | value sleeve baseline | human-readable name |
| experiment_owner | string | Y | owner_id | responsibility |
| creation_date | date | Y | 2026-06-10 | time trace |
| phase_lock | enum | Y | Phase1A | prevent phase drift |
| hypothesis_id | string | Y | H-001 | preregistered hypothesis |
| hypothesis_text | text | Y | value rank has positive diagnostic IC | prevents post-hoc story |
| market_sleeve | enum | Y | US | US-core first |
| universe_config_id | string | Y | UNI-US-v1 | universe contract |
| benchmark_config_id | string | Y | BMK-US-selfTR-v1 | benchmark contract |
| data_snapshot_id | string | Y | DS-US-20260610-a3f8 | data version |
| data_hash | string | Y | sha256:... | reproducibility |
| data_license_state | enum | Y | licensed_research | legal/data lineage |
| data_vendor_bundle | string | Y | EDGAR+VendorX-v1 | source bundle |
| vendor_confirmation_state | enum | Y | confirmed/unknown | confirmation |
| broker_confirmation_state | enum | Y | confirmed/unknown/NA | broker dependency |
| legal_confirmation_state | enum | Y | confirmed/unknown | legal dependency |
| feature_config_id | string | Y | FEAT-value-v1 | feature contract |
| alpha_config_id | string | Y | ALPHA-rank-v1 | alpha contract |
| portfolio_config_id | string | Y | PORT-1N-v1 | portfolio contract |
| risk_config_id | string | Y | RISK-hardcap-v1 | risk contract |
| cost_config_id | string | Y | COST-US-base-v1 | cost contract |
| execution_support_config_id | string | Y | EXEC-basic-v1 | L9 baseline |
| monitoring_config_id | string | Y | MON-shadow-v1 | L11 baseline |
| validation_config_id | string | Y | VAL-WF-v1 | validation contract |
| trial_group_id | string | Y | TG-B02 | broad grouping |
| trial_family_id | string | Y | TF-B02-value | multiple-testing family |
| family_type | enum | Y | baseline/sensitivity/diagnostic | trial classification |
| trial_number | int | Y | 1 | trial count |
| parent_trial_id | string | N | P1A-B02... | variant relationship |
| variant_of | string | N | top_N_variant | variant trace |
| degrees_of_freedom_count | int | Y | 0 | DoF tracking |
| search_budget_used | int | Y | 1 | search discipline |
| budget_cap_rule | string | Y | low-DoF baseline budget v1 | budget reference |
| effective_N_method | string | Y | exact count / clustered estimate | DSR/PBO input |
| code_version | string | Y | git:abc123 | code reproducibility |
| environment_hash | string | Y | docker_sha256:... | runtime reproducibility |
| random_seed_policy | enum | Y | deterministic/NA/fixed | stochastic control |
| calendar_version | string | Y | NYSE-cal-v1 | trading calendar |
| rebalance_calendar | string | Y | month-end signal, next-session trade | rebalance rule |
| OOS_window | string | Y | rule-based | OOS trace |
| walk_forward_scheme | enum | Y | primary_expanding_v1 | WF scheme |
| final_holdout_freeze_id | string | Y | HOLDOUT-v1 | freeze evidence |
| data_gate_report_link | uri | Y | reports/gate.md | data gate evidence |
| benchmark_drift_report_link | uri | Y | reports/benchmark.md | benchmark evidence |
| cost_stress_report_link | uri | Y | reports/cost.md | cost evidence |
| approval_log_link | uri | Y | approvals/log.md | governance evidence |
| failure_log_id | string | N | F-001 | failure trace |
| abandoned_flag | bool | Y | false | file-drawer prevention |
| abandoned_reason | string | N | NA | abandonment trace |
| budget_counted_flag | bool | Y | true | search budget discipline |
| status | enum | Y | registered | lifecycle |
| decision | enum | Y | pending/promote/quarantine/reject | final decision |
| decision_date | date | N | 2026-06-15 | decision trace |
| decision_reason | text | N | failed data gate | audit trace |
| reviewer_id | string | N | reviewer_1 | review trace |
| approval_stage | enum | Y | none/data_gate/oos/promotion | governance |
| approval_timestamp | datetime | N | 2026-06-15T09:00Z | approval trace |
| notes | text | N | — | context |

---

## 6. Final Config Schema Set

### 6.1 Data Snapshot Config

| Field | Status | Rule |
|---|---|---|
| raw_source | Requires confirmation | EDGAR floor + chosen survivorship-aware price/universe source |
| source_release_timestamp | Requires confirmation | source release time stored |
| vendor_source_version | Requires confirmation | vendor release/version stored |
| extraction_date | Lock now | ISO date |
| timezone | Lock now | timezone explicitly stored |
| point_in_time_rule | Lock now | feature availability cannot precede filing/market availability |
| restatement_mode | Lock now | as-filed / restated / snapshot explicitly selected |
| corporate_action_policy | Lock now | splits/dividends/distributions reconciled |
| delisting_inactive_policy | Lock now | inactive/delisted handled |
| filing_timestamp_policy | Lock now | acceptance timestamp or next-session fallback |
| missing_data_policy | Lock now | missingness policy documented |
| identifier_link_snapshot_id | Lock now | identifier history version stored |
| calendar_version | Lock now | trading calendar version stored |
| data_hash | Lock now | immutable snapshot hash |
| data_license_state | Requires confirmation | unknown blocks non-sandbox use |

### 6.2 Universe Config

| Field | Status | Rule |
|---|---|---|
| market | Lock now | US for Phase 1A |
| inclusion_rule | Provisional | common stock eligible universe |
| share_code_whitelist_version | Provisional | machine-readable whitelist |
| exclusion_rule | Lock now | ETF/ADR/preferred/units etc excluded unless explicitly allowed |
| exchange_rule | Provisional | exchange eligibility |
| primary_listing_rule | Provisional | primary listing logic |
| IPO_seasoning_rule | Provisional | seasoning period |
| halted_no_price_handling | Lock now | no-price/halt treatment documented |
| liquidity_filter | Provisional | values not locked yet |
| survivorship_policy | Lock now | inactive/delisted retained |
| reconstitution_frequency | Provisional | default monthly; change = new trial family |
| as_of_date_handling | Lock now | no future membership |

### 6.3 Benchmark Config

| Field | Status | Rule |
|---|---|---|
| internal_self_built_benchmark | Lock now | actual universe cap-weight TR benchmark |
| reporting_benchmark | Do not lock yet | external comparator only |
| benchmark_source_version | Provisional | required when chosen |
| total_return_policy | Lock now | TR includes distributions |
| weight_construction | Provisional | full-cap or float-cap mode explicit |
| rebalancing_rule | Provisional | must match calendar |
| benchmark_calendar | Lock now | same calendar/version |
| internal_reconstruction_error | Lock now | QA metric |
| external_comparator_difference | Diagnostic | reporting difference, not automatic failure |
| benchmark_drift_report_link | Lock now | required artifact |

### 6.4 Feature Config

| Field | Status | Rule |
|---|---|---|
| factor_list | Lock now | value, quality/profitability, momentum, low-vol, size/liquidity control |
| factor_definition_id | Provisional | exact formula version |
| winsorization | Provisional | value not locked |
| standardization | Lock now | rank/z-score documented |
| sector_taxonomy_version | Provisional | required if used |
| sector_adjustment | Provisional | raw vs adjusted comparison; variant counted |
| beta_adjustment | Provisional | raw vs adjusted comparison; variant counted |
| stale_age_cap | Provisional | stale features flagged |
| lag_rule | Lock now | availability-time safe |
| missing_value_rule | Provisional | explicit per factor |
| ADV_window | Provisional | size/liquidity definition |

### 6.5 Alpha Config

| Field | Status | Rule |
|---|---|---|
| alpha_family_id | Lock now | family mapped to B-id |
| allowed_family_enum | Lock now | Phase 1A only |
| sign_convention_id | Lock now | factor direction preregistered |
| factor_sleeve_definition | Lock now | single sleeve rank |
| rank_construction | Lock now | cross-sectional rank |
| composite_score | Lock now | equal-weight rank blend only |
| tie_handling | Lock now | average rank |
| neutralization_option | Provisional | off/sector/beta; variant counted |
| refresh_frequency | Provisional | default monthly |
| long_only_mode | Lock now | Phase 1A long-only baseline |
| denylist_lint | Lock now | learned ML/optimizer/LLM-alpha forbidden |

### 6.6 Portfolio Config

| Field | Status | Rule |
|---|---|---|
| construction_method | Lock now | 1/N, equal-weight top-N, monotone rank-to-weight |
| top_N | Provisional | value not locked |
| weight_function_id | Provisional | monotone function version |
| max_name_weight | Provisional | house rule |
| max_sector_weight | Provisional | house rule |
| cash_handling | Provisional | fully invested unless constraints force residual |
| residual_cash_rule | Provisional | residual handling documented |
| signal_to_trade_lag | Lock now | next-session or configured lag |
| lot_rounding_rule | Provisional | rounding documented |
| no_trade_buffer | Provisional | allowed only as basic execution support |
| rebalance_frequency | Provisional | default monthly |
| illiquid_name_drop_rule | Provisional | fail-closed or conservative |

### 6.7 Risk Config

| Field | Status | Rule |
|---|---|---|
| hard_caps | Lock now | deterministic caps only |
| liquidity_cap | Provisional | ADV cap house rule |
| turnover_cap | Do not lock yet | values unknown |
| beta_sector_exposure_check | Lock now | report/watch |
| benchmark_relative_exposure_band | Provisional | diagnostic |
| breach_handling_path | Lock now | breach => block/quarantine |
| watch_to_veto_escalation | Provisional | escalation documented |
| drawdown_watch | Provisional | soft diagnostic |
| risk_veto_rule | Lock now | deterministic hard cap veto |

### 6.8 Cost Config

| Field | Status | Rule |
|---|---|---|
| jurisdiction_mode | Lock now | US first, KR later separate |
| commission | Requires broker confirmation | unknown = conservative fallback |
| fees | Requires confirmation | separate from commission |
| tax_levy | Requires confirmation | separate by jurisdiction |
| spread_model_version | Provisional | proxy version |
| slippage_model_version | Provisional | fixed bps alone not enough |
| turnover_cost | Lock now | turnover linked |
| ADV_cap_link | Provisional | capacity linkage |
| missing_cost_fallback | Lock now | fail-closed or conservative |
| base_cost | Provisional | scenario |
| cost_2x | Provisional | house stress |
| cost_3x | Provisional | separate scenario |
| adverse_cost | Provisional | separate adverse scenario |
| broker_fee_schedule_id | Requires confirmation | broker dependency |

### 6.9 Execution Support Config

| Field | Status | Rule |
|---|---|---|
| execution_support_config_id | Lock now | required registry field |
| no_trade_buffer | Provisional | basic buffer only |
| participation_cap | Provisional | ADV cap |
| order_handoff_mode | Lock now | simulated/paper only in Phase 1A |
| execution_algo_assumption | Lock now | VWAP/TWAP handoff only, not execution alpha |
| broker_dependency | Requires broker confirmation | unknown kept separate |
| slippage_feedback_log | Provisional | for paper/shadow later |

### 6.10 Monitoring / Paper-Shadow Config

| Field | Status | Rule |
|---|---|---|
| monitoring_config_id | Lock now | required |
| paper_shadow_plan_id | Lock now | required before Phase 1B review |
| daily_audit_fields | Lock now | PnL, exposures, turnover, costs, errors |
| data_QA_alarm | Lock now | data gate failures |
| benchmark_drift_alarm | Lock now | drift report |
| cost_drift_alarm | Provisional | cost deviations |
| signal_freshness_check | Lock now | stale signal detection |
| human_review_cadence | Provisional | cadence unknown |

### 6.11 Validation Config

| Field | Status | Rule |
|---|---|---|
| train_window | Provisional | rule locked, dates unknown |
| validation_window | Provisional | rule locked, dates unknown |
| OOS_window | Lock now | chronological OOS |
| primary_walk_forward_scheme | Lock now | one primary scheme required |
| alternative_walk_forward_scheme | Provisional | alternative = new trial family |
| final_holdout_rule | Lock now | untouched, one-time |
| final_holdout_freeze_id | Lock now | required |
| no_random_split | Lock now | mandatory |
| no_test_set_tuning | Lock now | mandatory |
| label_overlap_flag | Lock now | determines purging |
| embargo_rule | Conditional | required only if label overlap/event leakage |
| regime_coverage_report | Lock now | report artifact |
| DSR_PBO_trigger_rule | Provisional | rule required, thresholds provisional |
| metric_list | Lock now | see Section 10 |
| reporting_template | Lock now | see Section 14 |

---

## 7. Data Acceptance Gate

| ID | Test | Purpose | Pass condition | Failure action | Severity |
|---|---|---|---|---|---|
| G-01 PIT universe replay | no future constituents | membership as-of date valid | block | Critical |
| G-02 No future fundamentals | prevent look-ahead | feature_ts >= filing/availability_ts | block | Critical |
| G-03 Filing timestamp lag | prevent filing leakage | accepted/available before use | block | Critical |
| G-04 Delisting/inactive inclusion | prevent survivorship bias | inactive/delisted retained or imputed | block | Critical |
| G-05 Corporate-action reconciliation | price integrity | split/dividend/distribution reconcile | block | Critical |
| G-06 Dividend/distribution reconciliation | TR integrity | cash distributions handled correctly | block | High |
| G-07 Missing OHLCV policy | missingness control | severity-weighted policy passes | quarantine/block | High |
| G-08 Abnormal return/split detection | outlier control | jump explained by CA or flagged | quarantine | Medium |
| G-09 Benchmark internal reconstruction | benchmark QA | self-built TR reconstructable | block | High |
| G-10 Cost data sanity | cost realism | components present or conservative fallback | quarantine/block | High |
| G-11 Identifier mapping integrity | security history | id link snapshot validates | block | High |
| G-12 Data lineage/hash check | reproducibility | data hash/version match | block | Critical |
| G-13 Restatement leakage | prevent restated look-ahead | as-filed/restated mode safe and explicit | block | Critical |
| G-14 License lineage | legal/data lineage | license state known or sandbox fail-closed | block non-sandbox | Critical |

---

## 8. OOS / Walk-forward Split Design

| Rule | Final treatment |
|---|---|
| Chronological split only | LOCK |
| Random split | FORBIDDEN |
| Train/validation/OOS separation | LOCK |
| Final untouched holdout | LOCK |
| Test-set tuning | FORBIDDEN |
| One primary WF scheme | LOCK |
| Alternative WF scheme | new trial family |
| Rolling vs expanding | primary scheme must be chosen in config |
| Regime coverage | report required |
| Label overlap flag | required |
| Purging/embargo | mandatory only if overlapping labels or event leakage |
| Monthly non-overlap baseline | purging/embargo usually Not Applicable, documented |
| New trial definition | config/split/universe/benchmark/cost/feature/portfolio/risk change = new trial |
| Evidence clock reset | any post-test modification resets evidence clock |

---

## 9. Final Phase 1A Experiment Matrix

### B0 — Data-only Benchmark Sanity

| Item | Design |
|---|---|
| Purpose | validate data, corporate actions, universe, self-built benchmark |
| Hypothesis | self-built internal TR benchmark is reconstructable and explainable |
| Portfolio | none / benchmark reconstruction |
| Promotion | data/benchmark sanity passes |
| Failure | unexplained drift, CA mismatch, missing lineage |

### B1 — 1/N Universe Baseline

| Item | Design |
|---|---|
| Purpose | establish boring no-skill portfolio baseline |
| Portfolio | 1/N or equal-weight eligible universe |
| Cost | base + scenario reporting |
| Promotion | reproducible after-cost reporting, no data/cost errors |
| Failure | cost/reporting/reproducibility failure |

### B2–B5 — Simple Factor Sleeve Baselines

| ID | Sleeve | Special rule |
|---|---|---|
| B2 | value | PIT fundamentals and lag discipline |
| B3 | quality/profitability | PIT fundamentals and restatement gate |
| B4 | momentum | turnover shock mandatory |
| B5 | low-volatility | raw vs beta-neutral diagnostic |

For B2–B5:

| Item | Design |
|---|---|
| Portfolio | monotone rank-to-weight or top-N, preregistered |
| Promotion | soft/conditional; no auto-promotion from thresholds |
| Quarantine | unstable OOS, cost/capacity issue |
| Reject | data gate or reproducibility failure |

### B6 — Size / Liquidity Attribution Diagnostic

| Item | Design |
|---|---|
| Purpose | determine whether baseline effect is hidden size/liquidity exposure |
| Treatment | diagnostic, not standalone promotion target |
| Output | attribution report |
| Failure | if all signal disappears after control, candidate is quarantined for interpretation |

### B7 — Cross-sectional Rank Composite

| Item | Design |
|---|---|
| Purpose | equal-weight rank composite across approved sleeves |
| Allowed | simple equal-weight rank blend only |
| Forbidden | learned weights |
| Promotion | only if B2–B6 diagnostics are clean and OOS/cost reporting survives |

### B8 — Invariance / Composite Consistency Check

| Item | Design |
|---|---|
| Purpose | verify B7 is not fragile to equivalent representation |
| Treatment | optional if budget tight; merge with B7 if necessary |
| Classification | diagnostic/invariance check |
| Trial treatment | counts toward family budget |

### B9 — Portfolio Construction Sensitivity Family

B9 is **not one broad experiment**. It is a pre-registered sensitivity family.

| Sub-ID | Variant |
|---|---|
| B9a | 1/N |
| B9b | equal-weight top-N |
| B9c | monotone rank-to-weight |

| Rule | Treatment |
|---|---|
| Purpose | compare construction sensitivity |
| Promotion | no automatic winner; informs Phase 1A final baseline |
| Trial counting | each variant counts as trial |
| Failure | construction causes turnover/capacity/cost breach |

### B10 — Risk Cap Sensitivity Family

B10 is **not alpha**. It is a risk-control sensitivity family.

| Sub-ID | Variant |
|---|---|
| B10a | name cap |
| B10b | sector cap |
| B10c | liquidity/ADV cap |
| B10d | turnover watch/cap |

| Rule | Treatment |
|---|---|
| Purpose | measure impact of deterministic hard caps |
| Promotion | informs default risk config only |
| Failure | cap hides infeasible portfolio or erases all signal |

### B11 — Mandatory Cost-stress Suite

B11 is **not standalone alpha experiment**. It attaches to any B1–B10 candidate considered for promotion.

| Scenario | Treatment |
|---|---|
| base cost | mandatory |
| 2x cost | mandatory house stress |
| 3x cost | mandatory separate scenario |
| calibrated adverse | optional/separate, not substitute for 3x unless justified |
| spread widening | mandatory where spread data available |
| turnover shock | mandatory for B4/B9 |
| ADV participation stress | mandatory |
| missing-cost fallback | mandatory |

---

## 10. Metrics Policy

| Metric | Final classification | Notes |
|---|---|---|
| data error count | hard gate | severity-weighted; critical errors block |
| benchmark internal reconstruction error | hard gate | benchmark QA |
| external comparator difference | diagnostic | not automatic failure |
| after-cost excess return | soft/conditional gate | no auto-promotion |
| information ratio | soft gate | threshold provisional |
| Rank IC mean | diagnostic / conditional for signal sleeves | not for B0/B1/B9/B10/B11 |
| Rank IC stability | diagnostic / soft | threshold provisional |
| turnover | conditional hard | linked to cost/capacity |
| ADV participation | conditional hard | house bands provisional |
| max drawdown | soft gate | benchmark-relative context |
| drawdown duration | diagnostic |
| hit rate | diagnostic |
| quantile spread | diagnostic |
| factor/sector/beta exposure | diagnostic |
| cost drag | report only |
| DSR / PBO | conditional hard once trigger reached | trigger rule required |
| t-stat | report only / diagnostic | no flat t-stat gate |

---

## 11. Cost Stress Configuration

| Scenario | Applies to | Purpose | Failure action |
|---|---|---|---|
| base cost | all B1+ | realistic baseline cost | report/quarantine if negative |
| 2x cost | all B1+ | cost underestimation check | soft/conditional gate |
| 3x cost | all B1+ | severe simple stress | diagnostic/soft gate |
| calibrated adverse | where data permits | adverse market state | separate scenario family |
| spread widening | liquidity-sensitive | stress indirect costs | quarantine if infeasible |
| turnover shock | momentum/construction variants | test cost blow-up | quarantine/reject |
| ADV participation stress | all trading variants | capacity realism | block if hard cap breached |
| missing-cost fallback | missing costs | prevent zero-cost bias | fail-closed or conservative |

---

## 12. Trial Budget Policy

| Rule | Final treatment |
|---|---|
| Every config evaluation is a trial | LOCK |
| Any changed data/universe/benchmark/feature/alpha/portfolio/risk/cost/validation config creates a new trial | LOCK |
| Alternative WF scheme = new trial family | LOCK |
| Abandoned trials count toward budget | LOCK |
| Failed trials are logged with same rigor as successful trials | LOCK |
| Unlogged trial invalidates family evidence | LOCK |
| `trial_family_id` required | LOCK |
| `effective_N_method` required | LOCK |
| DSR/PBO trigger | PROVISIONAL; must be encoded before Phase 1C and if Phase 1A family search expands |
| Search budget numeric cap | PROVISIONAL; must be low for Phase 1A |

---

## 13. Lifecycle

| State | Entry | Exit | Human control |
|---|---|---|---|
| draft | initial idea | registered | no |
| registered | hypothesis and configs complete | data-gate-pending | optional completeness review |
| data-gate-pending | data gate queued | data-gate-passed / rejected | no |
| data-gate-passed | G-01..G-14 pass | backtest-running | reviewer sign-off required |
| backtest-running | immutable run context ready | OOS-evaluated | no |
| OOS-evaluated | OOS/WF result available | quarantine/reject/Phase1B-review | reviewer sign-off required |
| quarantined | gate borderline/failure | patched/rejected/archived | release approver required |
| rejected | hard fail | archived | reviewer sign-off required |
| promoted-to-Phase-1B-review | Phase 1A package complete | Phase 1B planning | human approval required |
| archived | terminal state | none | no |

---

## 14. Required Artifact Templates

Phase 1A implementation requires these artifacts.

| Artifact | Required before |
|---|---|
| experiment registry | any experiment |
| data snapshot config | B0 |
| universe config | B0 |
| benchmark config | B0 |
| feature config | B2+ |
| alpha config | B2+ |
| portfolio config | B1+ |
| risk config | B1+ |
| cost config | B1+ |
| execution support config | B1+ |
| monitoring / paper-shadow config | Phase 1B review |
| data gate report | B0 |
| benchmark drift report | B0 |
| cost stress report | B1+ and all promotion candidates |
| capacity report | B4/B9/B10+ |
| multiple-testing report | if trigger reached; required before Phase 1C |
| approval log | all promotions/quarantine releases |
| failure log | all failures and abandoned trials |
| postmortem template | repeated failures |
| paper/shadow report | before Phase 1B review |

---

## 15. Phase 1A Experiment Report Template

```markdown
# Phase 1A Experiment Report — {experiment_id}

## 1. Experiment Summary
- experiment_id:
- phase_lock:
- owner:
- status:
- decision:

## 2. Hypothesis
- hypothesis_id:
- hypothesis_text:
- trial_family_id:
- effective_N_method:

## 3. Data Snapshot
- data_snapshot_id:
- data_hash:
- data_license_state:
- source_release_timestamp:
- restatement_mode:
- identifier_link_snapshot_id:

## 4. Universe
- universe_config_id:
- inclusion/exclusion:
- as-of handling:
- survivorship policy:

## 5. Benchmark
- benchmark_config_id:
- internal reconstruction error:
- external comparator difference:
- benchmark_drift_report_link:

## 6. Feature / Alpha
- feature_config_id:
- alpha_config_id:
- factor definitions:
- lag policy:
- raw vs neutralized variant:

## 7. Portfolio / Risk
- portfolio_config_id:
- risk_config_id:
- weight rule:
- hard caps:
- breach events:

## 8. Cost / Execution
- cost_config_id:
- execution_support_config_id:
- base/2x/3x/adverse scenarios:
- ADV participation:

## 9. Validation Split
- validation_config_id:
- primary_walk_forward_scheme:
- final_holdout_freeze_id:
- no test-set tuning confirmation:

## 10. Results Summary
- no performance prediction; report observed backtest result only

## 11. Metrics Table
- hard / soft / diagnostic / report-only metrics

## 12. Cost Stress Table
- base / 2x / 3x / adverse / spread / turnover / ADV

## 13. Trial Family Summary
- trial_number:
- search_budget_used:
- abandoned trials:
- failed trials:
- DSR/PBO trigger status:

## 14. Failure Analysis
- failure_log_id:
- failure type:
- downstream invalidation scope:

## 15. Approval Chain
- reviewer_id:
- approval_stage:
- approval_timestamp:

## 16. Decision
- promote / quarantine / reject / pending
- decision_reason:
- next action:
```

---

## 16. Failure Log Template

```markdown
# Failure Log — {failure_id}

- failure_id:
- experiment_id:
- trial_family_id:
- date_detected:
- failure_type:
- affected_layer:
- affected_artifacts:
- severity:
- description:
- root_cause:
- detection_method:
- immediate_action:
- downstream_invalidation_scope:
- rerun_eligibility:
- prevention_patch:
- long_term_fix:
- owner:
- status:
- closure_reviewer:
- resolution_timestamp:
- linked_artifacts:
```

---

## 17. Phase 1B / Phase 1C Gates

### Phase 1B may begin only after:

| Condition | Required |
|---|---|
| Data gate stable | yes |
| B0 benchmark sanity passes | yes |
| B1 1/N baseline reproducible | yes |
| B2–B5 factor sleeves completed or explicitly rejected | yes |
| B6 attribution diagnostic completed | yes |
| B7/B8 composite sanity completed | yes |
| B9/B10 sensitivity families documented | yes |
| B11 cost-stress suite attached to candidates | yes |
| Registry and failure log functioning | yes |
| Cost stress report functioning | yes |
| Approval log functioning | yes |
| Paper/shadow plan drafted | yes |

### Phase 1C may begin only after:

| Condition | Required |
|---|---|
| Phase 1B review completed | yes |
| Feature/model registry functioning | yes |
| Trial-family search budget enforced | yes |
| DSR/PBO trigger operational | yes |
| Independent holdout protected | yes |
| High-DoF gates ready | yes |
| Tree/ML denylist reopened by explicit approval | yes |

---

## 18. Final Lock Decision Table

| Item | Final status |
|---|---|
| experiment registry schema | **Lock structure / Provisional field values** |
| data snapshot config | **Requires data/vendor/legal confirmation** |
| universe config | **Provisional** |
| benchmark config | **Provisional; internal self-built benchmark required** |
| feature config | **Provisional** |
| alpha config | **Lock Phase 1A allow/deny / Provisional definitions** |
| portfolio config | **Provisional** |
| risk config | **Provisional** |
| cost config | **Requires data/vendor/broker/legal confirmation** |
| execution support config | **Lock structure / Provisional params** |
| monitoring/paper-shadow config | **Lock structure / Provisional params** |
| validation config | **Lock rules / Provisional windows** |
| data acceptance gate | **Lock tests G-01..G-14** |
| OOS / walk-forward split | **Lock rules / dates unknown** |
| B0–B11 matrix | **Lock structure / Provisional thresholds** |
| metrics policy | **Provisional thresholds; no auto-promotion** |
| cost stress | **Provisional values; mandatory structure** |
| trial budget policy | **Lock rule / Provisional numeric caps** |
| report template | **Lock now** |
| failure log template | **Lock now** |
| lifecycle | **Lock now** |
| Phase 1B gate | **Lock now** |
| Phase 1C gate | **Lock now** |
| implementation | **NO-GO until Pre-Implementation Gate passes** |

---

## 19. Next Handoff

```text
Phase 1 Final Experiment Design v0.1
    ↓
Pre-Implementation Gate
    ↓
Data/vendor/license confirmation
    ↓
Registry/config/artifact setup
    ↓
B0 implementation only
    ↓
Data + benchmark sanity review
    ↓
B1–B11 Phase 1A sequence
    ↓
Phase 1A review package
    ↓
Phase 1B planning only if gates pass
```

---

## 20. Short Mental Model

```text
DR-4 decided what kinds of models are allowed.
Phase 1 Final Experiment Design decides how the first boring baseline experiments must be recorded and judged.

Next:
Do not build XGBoost.
Do not build LLM alpha.
Do not optimize portfolio yet.
First prove the data, benchmark, cost, and registry work.
```
