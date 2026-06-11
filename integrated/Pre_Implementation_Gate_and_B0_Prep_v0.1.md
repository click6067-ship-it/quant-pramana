# Pre-Implementation Gate & B0 Implementation Prep v0.1
## Phase 1A Boring Baseline — 구현 직전 체크리스트 + B0 준비 문서

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-10  
**Status:** Implementation-prep document  
**Scope:** Pre-Implementation Gate + B0 data-only benchmark sanity experiment  
**Non-scope:** model implementation, alpha backtest, stock recommendation, live trading, performance forecast

---

## 0. 한 줄 결론

Phase 1A 구현은 바로 전체 B0–B11로 들어가면 안 된다.

먼저 아래 순서로 간다.

```text
1. Pre-Implementation Gate 통과
2. B0 data-only benchmark sanity experiment만 구현 준비
3. B0 실행
4. Data gate + benchmark sanity review
5. B0 통과 후에만 B1 이후로 이동
```

B0는 알파 실험이 아니다.  
B0는 **데이터·유니버스·기업행동·상장폐지·벤치마크 재구성이 정직하게 작동하는지 확인하는 실험**이다.

---

## 1. 지금 단계의 목적

이 문서는 실제 백테스트 구현 전에 확인할 **운영 준비 문서**다.

| 구분 | 목적 |
|---|---|
| Pre-Implementation Gate | 구현 전에 필요한 데이터·라이선스·레지스트리·템플릿·승인체계가 준비됐는지 확인 |
| B0 준비 | 첫 실험인 data-only benchmark sanity experiment를 실행 가능한 단위로 쪼개기 |
| 구현 제한 | B0 외의 factor, ML, optimizer, LLM-alpha 실험을 막기 |
| 산출물 | 체크리스트, 파일 구조, config skeleton, B0 input/output, pass/fail rule |

---

## 2. Pre-Implementation Gate Overview

Implementation may not begin until every blocking item is resolved.

| Gate ID | Gate | Blocking? | Owner | Output |
|---|---|---:|---|---|
| P0-01 | Source file version lock | Yes | Research owner | source manifest |
| P0-02 | Data source track chosen | Yes | Data owner | data source decision |
| P0-03 | License state recorded | Yes | Legal/data owner | license register |
| P0-04 | Trading calendar fixed | Yes | Data owner | calendar config |
| P0-05 | Code/environment tracking ready | Yes | Engineering owner | version/hash policy |
| P0-06 | Experiment registry ready | Yes | Research owner | registry schema |
| P0-07 | Config schemas ready | Yes | Research/data owner | config folder |
| P0-08 | Data gate G-01~G-14 ready | Yes | Data owner | data gate checklist |
| P0-09 | Benchmark drift report template ready | Yes | Research owner | benchmark report template |
| P0-10 | Cost stress report template ready | Yes for B1+, optional for B0 | Research owner | cost report template |
| P0-11 | Failure log ready | Yes | Research owner | failure log template |
| P0-12 | Approval log ready | Yes for promotion | Research owner | approval log template |
| P0-13 | Phase 1A denylist lint ready | Yes | Research/engineering owner | denylist rule |
| P0-14 | B0 experiment card registered | Yes | Research owner | B0 registry entry |

---

## 3. Pre-Implementation Gate Checklist

### P0-01. Source File Version Lock

| Check | Required state | Status |
|---|---|---|
| Integrated Lock Sheet available | exact version path recorded | TODO |
| DR-3 Final Validation Protocol available | exact version path recorded | TODO |
| DR-4 Final Model Candidate Map available | exact version path recorded | TODO |
| Phase 1 Final Experiment Design available | exact version path recorded | TODO |
| All source files hash-recorded | SHA256 or equivalent | TODO |

**Pass condition:** all source documents have fixed paths, version labels, and hashes.  
**Fail action:** block implementation.

---

### P0-02. Data Source Track Chosen

For Phase 1A U.S.-core pilot, choose one data track.

| Component | Minimum acceptable state | Candidate / decision |
|---|---|---|
| Filing/fundamental floor | EDGAR or equivalent official as-filed floor | TODO |
| Price/return history | survivorship-aware source | TODO |
| Universe membership | PIT or survivorship-aware membership source | TODO |
| Delisting/inactive handling | source or imputation policy | TODO |
| Corporate actions | split/dividend/distribution source | TODO |
| Identifier mapping | stable security identifier and link history | TODO |

**Pass condition:** data source track is chosen and every component is either `confirmed`, `sandbox-only`, or `blocked`.  
**Fail action:** if any required component is `unknown`, B0 cannot begin.

---

### P0-03. License State Recorded

| License item | Required label | Status |
|---|---|---|
| Research use | confirmed / unknown / prohibited | TODO |
| Paper-trading use | confirmed / unknown / prohibited | TODO |
| Production use | confirmed / unknown / prohibited | TODO |
| Redistribution | allowed / prohibited / unknown | TODO |
| Derived data storage | allowed / restricted / unknown | TODO |
| Commercial use | allowed / restricted / unknown | TODO |

**Rule:** unknown license state is fail-closed outside a sandbox.  
**Pass condition:** Phase 1A B0 use is legally allowed or explicitly sandbox-only.

---

### P0-04. Trading Calendar Fixed

| Field | Required |
|---|---|
| calendar_id | e.g., `US-NYSE-v1` |
| timezone | e.g., `America/New_York` |
| holiday source | source/version |
| trading day definition | open trading days only |
| month-end signal rule | defined |
| next-session trade rule | defined |
| rebalance calendar | defined |

**Pass condition:** all time-series alignment uses this calendar.  
**Fail action:** block B0 because benchmark reconstruction depends on calendar consistency.

---

### P0-05. Code / Environment Tracking Ready

| Item | Required |
|---|---|
| code_version | git commit or equivalent |
| environment_hash | container/env hash |
| package manifest | locked dependency versions |
| random_seed_policy | deterministic / fixed / NA |
| run_id format | defined |
| output hash policy | defined |

**Pass condition:** a run can be reproduced from `code_version + environment_hash + config ids + data hash`.

---

### P0-06. Experiment Registry Ready

Minimum fields must be implemented before B0:

```yaml
experiment_id:
phase_lock:
hypothesis_id:
market_sleeve:
data_snapshot_id:
data_hash:
data_license_state:
universe_config_id:
benchmark_config_id:
validation_config_id:
trial_family_id:
trial_number:
code_version:
environment_hash:
calendar_version:
data_gate_report_link:
benchmark_drift_report_link:
failure_log_id:
status:
decision:
reviewer_id:
```

**Pass condition:** B0 can be registered before any code is run.  
**Fail action:** running B0 without registry invalidates the experiment.

---

### P0-07. Config Schemas Ready

Required config files:

```text
configs/
  data_snapshot/
  universe/
  benchmark/
  validation/
  execution_support/
  monitoring/
  registry/
```

For B0, the minimum configs are:

| Config | Required for B0? |
|---|---:|
| data snapshot config | Yes |
| universe config | Yes |
| benchmark config | Yes |
| validation config | Yes |
| feature config | No |
| alpha config | No |
| portfolio config | No |
| risk config | No |
| cost config | Optional / placeholder |
| execution support config | Placeholder |
| monitoring config | Placeholder |

---

### P0-08. Data Gate G-01~G-14 Ready

| Gate | Required for B0? | Note |
|---|---:|---|
| G-01 PIT universe replay | Yes | core |
| G-02 No future fundamentals | Not directly / placeholder | needed for B2+ |
| G-03 Filing timestamp lag | Not directly / placeholder | needed for B2+ |
| G-04 Delisting/inactive inclusion | Yes | core |
| G-05 Corporate-action reconciliation | Yes | core |
| G-06 Dividend/distribution reconciliation | Yes | core |
| G-07 Missing OHLCV policy | Yes | core |
| G-08 Abnormal return/split detection | Yes | core |
| G-09 Benchmark internal reconstruction | Yes | B0 primary objective |
| G-10 Cost data sanity | Placeholder | B1+ |
| G-11 Identifier mapping integrity | Yes | core |
| G-12 Data lineage/hash check | Yes | core |
| G-13 Restatement leakage | Placeholder | B2+ |
| G-14 License lineage | Yes | core |

**Pass condition:** required B0 gates are executable or manually auditable.  
**Fail action:** block B0.

---

### P0-09. Benchmark Drift Report Template Ready

Required sections:

```text
1. Benchmark config
2. Universe config
3. Weight construction
4. Corporate action handling
5. Dividend/distribution handling
6. Rebalance dates
7. Internal reconstruction error
8. External comparator difference
9. Known drift sources
10. Decision: pass / quarantine / fail
```

---

### P0-10. Failure Log Ready

Minimum fields:

```yaml
failure_id:
experiment_id:
trial_family_id:
date_detected:
failure_type:
affected_layer:
severity:
description:
root_cause:
detection_method:
immediate_action:
downstream_invalidation_scope:
rerun_eligibility:
prevention_patch:
owner:
status:
closure_reviewer:
resolution_timestamp:
```

---

### P0-11. Approval Log Ready

Approval events required for:

| Event | Approval required? |
|---|---:|
| data-gate-passed | reviewer sign-off |
| OOS-evaluated | reviewer sign-off |
| quarantine release | approver sign-off |
| promoted-to-Phase-1B-review | human approval |

For B0, at minimum:

```yaml
approval_event: data_gate_passed
reviewer_id:
review_timestamp:
review_decision:
review_notes:
```

---

### P0-12. Phase 1A Denylist Lint Ready

B0 and all Phase 1A configs must reject these terms/classes:

```text
penalized regression
ridge/lasso/elastic net
tree ensemble
XGBoost
LightGBM
CatBoost
NLP/event ML
LLM-derived alpha
TSFM
financial foundation model
deep sequence
HRP
robust optimizer
constrained MVO
raw MVO
alternative data
RL
black-box allocator
autonomous retraining
free-form LLM trading
```

**Pass condition:** config lint fails if any forbidden model family appears.

---

## 4. B0 Data-only Benchmark Sanity Experiment

### 4.1 B0 Purpose

B0 answers only one question:

> Can we reconstruct a clean, PIT-safe, survivorship-aware internal benchmark for the actual research universe?

B0 does not test alpha.

B0 does not use factor features.

B0 does not form a predictive portfolio.

B0 does not compare models.

---

### 4.2 B0 Hypothesis

```text
H-B0:
Given a fixed data snapshot, universe config, corporate-action policy,
delisting/inactive policy, and benchmark construction rule,
the system can reconstruct the internal self-built total-return benchmark
for the actual research universe with explainable drift and reproducible outputs.
```

---

### 4.3 B0 Required Inputs

| Input | Required? | Description |
|---|---:|---|
| data_snapshot_config | Yes | fixed data source, release, hash, license |
| universe_config | Yes | eligible securities, as-of membership |
| benchmark_config | Yes | self-built TR benchmark rule |
| calendar_config | Yes | trading day and rebalance calendar |
| corporate_action_policy | Yes | splits, dividends, distributions |
| delisting_inactive_policy | Yes | inactive/delisted treatment |
| identifier_mapping_snapshot | Yes | stable identifier links |
| validation_config | Yes | date range and benchmark sanity procedure |
| external comparator benchmark | Optional | reporting comparison only |
| cost_config | No | B0 does not trade |

---

### 4.4 B0 Required Outputs

| Output | Required? |
|---|---:|
| B0 experiment registry entry | Yes |
| data gate report | Yes |
| universe reconstruction report | Yes |
| corporate action reconciliation report | Yes |
| dividend/distribution reconciliation report | Yes |
| delisting/inactive inclusion report | Yes |
| identifier mapping report | Yes |
| self-built benchmark return series | Yes |
| benchmark drift report | Yes |
| reproducibility manifest | Yes |
| failure log entries, if any | Yes |
| approval log entry | Yes |

---

## 5. B0 Implementation Checklist

### Step 1. Register B0

| Item | Value |
|---|---|
| experiment_id | `P1A-B0-YYYYMMDD-01` |
| phase_lock | `Phase1A` |
| family_type | `data_benchmark_sanity` |
| trial_family_id | `TF-B0-benchmark-sanity` |
| hypothesis_id | `H-B0` |
| model_family | `none` |
| feature_config_id | `NA` |
| alpha_config_id | `NA` |
| portfolio_config_id | `NA` |
| cost_config_id | `NA` or placeholder |
| decision | `pending` |

---

### Step 2. Freeze data snapshot

Required manifest:

```yaml
data_snapshot_id:
raw_source:
vendor_source_version:
source_release_timestamp:
extraction_date:
timezone:
calendar_version:
point_in_time_rule:
corporate_action_policy:
delisting_inactive_policy:
identifier_link_snapshot_id:
data_hash:
data_license_state:
```

Pass condition:

```text
data_hash exists and all required source/version fields are non-empty.
```

---

### Step 3. Freeze universe config

Required manifest:

```yaml
universe_config_id:
market: US
inclusion_rule:
share_code_whitelist_version:
exclusion_rule:
exchange_rule:
primary_listing_rule:
IPO_seasoning_rule:
halted_no_price_handling:
liquidity_filter:
survivorship_policy:
reconstitution_frequency:
as_of_date_handling:
```

Pass condition:

```text
Universe can be reconstructed for every as-of date without future membership.
```

---

### Step 4. Run B0 data gates

B0 mandatory gates:

```text
G-01 PIT universe replay
G-04 Delisting/inactive inclusion
G-05 Corporate-action reconciliation
G-06 Dividend/distribution reconciliation
G-07 Missing OHLCV policy
G-08 Abnormal return/split detection
G-09 Benchmark internal reconstruction
G-11 Identifier mapping integrity
G-12 Data lineage/hash check
G-14 License lineage
```

B0 placeholder gates:

```text
G-02 No future fundamentals
G-03 Filing timestamp lag
G-10 Cost data sanity
G-13 Restatement leakage
```

Placeholder gates must be marked `not applicable to B0 / required for B2+`.

---

### Step 5. Construct internal benchmark

Benchmark construction rule:

```text
Internal benchmark = cap-weighted total-return benchmark of actual research universe.
```

Required choices:

| Field | Decision |
|---|---|
| weight basis | full market cap or float-adjusted market cap |
| rebalance frequency | monthly default unless changed |
| as-of date | defined by calendar |
| trade date | next-session or configured date |
| total return | dividends/distributions included |
| missing price handling | fail / carry / exclude rule |
| delisted name handling | retained through delisting event with policy |
| external comparator | optional reporting only |

---

### Step 6. Produce benchmark drift report

Separate two drift types:

| Drift type | Meaning | Action |
|---|---|---|
| internal reconstruction error | error inside self-built benchmark | hard gate |
| external comparator difference | difference vs external index | diagnostic |

Do not fail B0 merely because the self-built benchmark differs from an external benchmark, unless the difference is unexplained or caused by reconstruction error.

---

### Step 7. Reproducibility check

B0 must rerun to identical or acceptably equivalent outputs from:

```text
data_hash
config ids
code_version
environment_hash
calendar_version
```

Required output:

```text
reproducibility_manifest.json or .md
```

---

### Step 8. Reviewer sign-off

Reviewer must check:

| Check | Pass? |
|---|---|
| B0 registered before run | TODO |
| data hash fixed | TODO |
| universe config fixed | TODO |
| benchmark config fixed | TODO |
| G-01/G-04/G-05/G-06/G-07/G-08/G-09/G-11/G-12/G-14 reviewed | TODO |
| benchmark drift explained | TODO |
| failure log complete | TODO |
| approval log updated | TODO |

---

## 6. B0 Pass / Quarantine / Fail Rules

| Outcome | Condition |
|---|---|
| PASS | all critical gates pass, benchmark reconstruction error explainable, reproducibility passes |
| QUARANTINE | non-critical data issues exist but are isolated and documented |
| FAIL | any critical gate fails, benchmark cannot be reconstructed, lineage/hash mismatch, license unknown outside sandbox |

Critical fail examples:

```text
future constituents detected
inactive/delisted securities missing without policy
corporate-action mismatch unexplained
dividend/distribution treatment inconsistent
identifier mapping broken
data hash mismatch
license state unknown for non-sandbox use
benchmark internal reconstruction error unexplained
```

---

## 7. B0 File/Folder Structure Recommendation

```text
phase1a/
  README.md
  source_manifest.md

  registry/
    experiment_registry.csv
    trial_family_registry.csv
    approval_log.md
    failure_log.md

  configs/
    data_snapshot/DS-US-YYYYMMDD-v1.yml
    universe/UNI-US-v1.yml
    benchmark/BMK-US-selfTR-v1.yml
    validation/VAL-B0-v1.yml
    execution_support/EXEC-placeholder-v1.yml
    monitoring/MON-placeholder-v1.yml

  gates/
    G01_pit_universe_replay.md
    G04_delisting_inactive.md
    G05_corporate_actions.md
    G06_dividends_distributions.md
    G07_missing_ohlcv.md
    G08_abnormal_returns.md
    G09_benchmark_reconstruction.md
    G11_identifier_mapping.md
    G12_lineage_hash.md
    G14_license_lineage.md

  reports/
    B0_data_gate_report.md
    B0_universe_report.md
    B0_corporate_action_report.md
    B0_benchmark_drift_report.md
    B0_reproducibility_manifest.md
    B0_final_decision.md

  outputs/
    benchmark_series/
    diagnostics/
    hashes/
```

---

## 8. B0 Minimal Config Skeletons

### data snapshot config

```yaml
data_snapshot_id: DS-US-YYYYMMDD-v1
raw_source: UNKNOWN
vendor_source_version: UNKNOWN
source_release_timestamp: UNKNOWN
extraction_date: YYYY-MM-DD
timezone: America/New_York
calendar_version: US-NYSE-v1
point_in_time_rule: no data before availability timestamp
restatement_mode: as_filed_or_snapshot_required
corporate_action_policy: reconcile_splits_dividends_distributions
delisting_inactive_policy: include_or_impute
identifier_link_snapshot_id: IDMAP-US-YYYYMMDD-v1
data_hash: TODO
data_license_state: unknown
```

### universe config

```yaml
universe_config_id: UNI-US-v1
market: US
inclusion_rule: common_stock_eligible
share_code_whitelist_version: TODO
exclusion_rule:
  - ETF
  - ADR
  - preferred
  - units
  - closed_end_fund
exchange_rule: TODO
primary_listing_rule: TODO
IPO_seasoning_rule: TODO
halted_no_price_handling: TODO
liquidity_filter: TODO
survivorship_policy: retain_inactive_and_delisted
reconstitution_frequency: monthly_provisional
as_of_date_handling: no_future_membership
```

### benchmark config

```yaml
benchmark_config_id: BMK-US-selfTR-v1
internal_self_built_benchmark: actual_universe_cap_weight_total_return
weight_basis: TODO_full_cap_or_float_adjusted
total_return_policy: include_dividends_and_distributions
rebalancing_rule: monthly_provisional
benchmark_calendar: US-NYSE-v1
internal_reconstruction_error_policy: hard_gate
external_comparator: TODO_optional
external_comparator_difference_policy: diagnostic_only
benchmark_drift_report_link: reports/B0_benchmark_drift_report.md
```

### validation config

```yaml
validation_config_id: VAL-B0-v1
purpose: data_and_benchmark_sanity
chronological_only: true
random_split_allowed: false
train_window: not_applicable_for_B0
OOS_window: benchmark_reconstruction_period
primary_walk_forward_scheme: not_applicable_or_calendar_replay
final_holdout_rule: not_applicable_for_B0
label_overlap_flag: false
embargo_rule: not_applicable
no_test_set_tuning: true
```

---

## 9. Deep Research 사용 기준

### 지금은 Deep Research가 필요 없는 단계

아래 작업은 내부 설계·구현 준비이므로 일반 작업으로 충분하다.

| 작업 | Deep Research 필요? |
|---|---:|
| Pre-Implementation Gate 체크리스트 작성 | No |
| B0 구현 준비 문서 작성 | No |
| registry/config template 작성 | No |
| folder structure 설계 | No |
| failure log/report template 작성 | No |
| Phase 1A denylist/lint rule 작성 | No |

### Deep Research를 써야 하는 단계

Deep Research는 **외부 사실 확인·소스 비교·벤더/데이터 선택·방법론 감사**에 쓴다.

| 상황 | Deep Research 사용 |
|---|---|
| 데이터 벤더 선택: CRSP vs Norgate vs Sharadar 등 | Yes |
| EDGAR/XBRL/Compustat PIT 처리 방식 비교 | Yes |
| delisting imputation 정책의 근거 확인 | Yes |
| cost/slippage/market impact 공식·문헌 근거 조사 | Yes |
| benchmark methodology / universe source 비교 | Yes |
| Phase 1B/1C로 넘어가기 전 red-team audit | Yes |
| 새 모델군을 Phase 1B/1C 후보로 열지 판단 | Yes |
| 외부 문헌 기반 임계값 calibration | Yes |

### 간단한 기준

```text
내부 문서/양식/구조를 만드는 일 = 일반 작업
외부 근거를 새로 찾아야 하는 일 = Deep Research
결정을 잠그기 전 적대 검증 = Deep Research 또는 Claude red-team
구현/코드 작성 = Deep Research 아님
```

---

## 10. Next Step Recommendation

Recommended next request:

```text
B0 implementation scaffold를 만들어줘.
실제 코드는 아직 말고, config 파일 템플릿과 registry row 예시,
data gate report template, benchmark drift report template만 Markdown/YAML 형태로 만들어줘.
```

Implementation should not start until:

```text
1. Data source track chosen
2. License state recorded
3. Calendar/version fixed
4. Registry/config templates created
5. B0 registered
6. Data gate checklist ready
```
