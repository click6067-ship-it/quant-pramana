# B0 Implementation Scaffold v0.1
## Phase 1A — Data-only Benchmark Sanity Experiment

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-10  
**Scope:** B0 implementation scaffold only  
**Non-scope:** executable code, alpha backtest, model implementation, stock recommendation, performance forecast

---

## 0. Purpose

B0 is the first implementation target after the Pre-Implementation Gate.

B0 does **not** test alpha.  
B0 does **not** build a trading strategy.  
B0 does **not** test factor signals.  
B0 does **not** select stocks.

B0 only answers:

> Can the system reconstruct a clean, PIT-safe, survivorship-aware internal benchmark for the actual research universe from versioned data and configs?

---

## 1. Recommended Scaffold File Tree

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
    data_snapshot/
      DS-US-YYYYMMDD-v1.yml
    universe/
      UNI-US-v1.yml
    benchmark/
      BMK-US-selfTR-v1.yml
    validation/
      VAL-B0-v1.yml
    execution_support/
      EXEC-placeholder-v1.yml
    monitoring/
      MON-placeholder-v1.yml

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

## 2. Source Manifest Template

**File:** `phase1a/source_manifest.md`

```markdown
# Source Manifest — Phase 1A / B0

## Locked design sources

| Document | Version | Path | Hash | Status |
|---|---|---|---|---|
| Integrated Lock Sheet DR1→DR2B | v0.1 | TODO | TODO | required |
| DR-3 Final Validation Protocol | v0.1 | TODO | TODO | required |
| DR-4 Final Model Candidate Map | v0.1 | TODO | TODO | required |
| Phase 1 Final Experiment Design | v0.1 | TODO | TODO | required |
| Pre-Implementation Gate and B0 Prep | v0.1 | TODO | TODO | required |

## Data sources

| Source | Role | Version / release | License state | Confirmation state |
|---|---|---|---|---|
| EDGAR or official filing floor | filing / fundamentals floor | TODO | TODO | TODO |
| Survivorship-aware price/universe source | price / returns / universe | TODO | TODO | TODO |
| Corporate action source | splits / dividends / distributions | TODO | TODO | TODO |
| Identifier mapping source | security id history | TODO | TODO | TODO |

## Decision

- Source lock status: TODO PASS / FAIL
- Notes:
```

---

## 3. Experiment Registry Row Example

**File:** `phase1a/registry/experiment_registry.csv`

CSV header:

```csv
experiment_id,experiment_name,experiment_owner,creation_date,phase_lock,hypothesis_id,hypothesis_text,market_sleeve,universe_config_id,benchmark_config_id,data_snapshot_id,data_hash,data_license_state,data_vendor_bundle,vendor_confirmation_state,broker_confirmation_state,legal_confirmation_state,feature_config_id,alpha_config_id,portfolio_config_id,risk_config_id,cost_config_id,execution_support_config_id,monitoring_config_id,validation_config_id,trial_group_id,trial_family_id,family_type,trial_number,parent_trial_id,variant_of,degrees_of_freedom_count,search_budget_used,budget_cap_rule,effective_N_method,code_version,environment_hash,random_seed_policy,calendar_version,rebalance_calendar,OOS_window,walk_forward_scheme,final_holdout_freeze_id,data_gate_report_link,benchmark_drift_report_link,cost_stress_report_link,approval_log_link,failure_log_id,abandoned_flag,abandoned_reason,budget_counted_flag,status,decision,decision_date,decision_reason,reviewer_id,approval_stage,approval_timestamp,notes
```

B0 example row:

```csv
P1A-B0-20260610-01,B0 data-only benchmark sanity,TODO_OWNER,2026-06-10,Phase1A,H-B0,"Given a fixed data snapshot, universe config, corporate-action policy, delisting/inactive policy, and benchmark construction rule, the system can reconstruct the internal self-built total-return benchmark for the actual research universe with explainable drift and reproducible outputs.",US,UNI-US-v1,BMK-US-selfTR-v1,DS-US-YYYYMMDD-v1,TODO_HASH,unknown,TODO_VENDOR_BUNDLE,unknown,NA,unknown,NA,NA,NA,NA,NA,EXEC-placeholder-v1,MON-placeholder-v1,VAL-B0-v1,TG-B0,TF-B0-benchmark-sanity,data_benchmark_sanity,1,,,0,1,phase1a-low-dof-v1,exact_count,TODO_CODE_VERSION,TODO_ENV_HASH,NA,US-NYSE-v1,"month-end signal / next-session trade",benchmark_reconstruction_period,not_applicable_or_calendar_replay,NA,reports/B0_data_gate_report.md,reports/B0_benchmark_drift_report.md,NA,registry/approval_log.md,,false,NA,true,registered,pending,,,,"none",,B0 registered before implementation
```

---

## 4. Trial Family Registry Template

**File:** `phase1a/registry/trial_family_registry.csv`

```csv
trial_family_id,family_name,phase_lock,family_type,parent_objective,allowed_variants,blocked_variants,effective_N_method,budget_cap_rule,DSR_PBO_trigger_rule,status,notes
TF-B0-benchmark-sanity,B0 benchmark sanity,Phase1A,data_benchmark_sanity,"Data-only benchmark reconstruction sanity","data source snapshot rerun only","alpha features; factor sleeves; portfolio optimization; ML; LLM alpha",exact_count,phase1a-b0-budget-v1,"not applicable unless variants expand beyond predefined rerun checks",active,B0 has no alpha search
```

---

## 5. Approval Log Template

**File:** `phase1a/registry/approval_log.md`

```markdown
# Approval Log — Phase 1A / B0

| approval_id | experiment_id | event | reviewer_id | timestamp | decision | notes |
|---|---|---|---|---|---|---|
| A-B0-001 | P1A-B0-YYYYMMDD-01 | data-gate-passed | TODO | TODO | pending | TODO |
| A-B0-002 | P1A-B0-YYYYMMDD-01 | benchmark-sanity-reviewed | TODO | TODO | pending | TODO |
| A-B0-003 | P1A-B0-YYYYMMDD-01 | final-decision | TODO | TODO | pending | TODO |
```

---

## 6. Failure Log Template

**File:** `phase1a/registry/failure_log.md`

```markdown
# Failure Log — Phase 1A / B0

## Failure Record Template

- failure_id:
- experiment_id:
- trial_family_id:
- date_detected:
- failure_type:
- affected_layer:
- affected_artifacts:
- severity: Critical / High / Medium / Low
- description:
- root_cause:
- detection_method:
- immediate_action: block / quarantine / patch / reject
- downstream_invalidation_scope:
- rerun_eligibility:
- prevention_patch:
- long_term_fix:
- owner:
- status: open / mitigated / closed
- closure_reviewer:
- resolution_timestamp:
- linked_artifacts:

## Failure Type Enum

- future_constituent_detected
- missing_inactive_or_delisted
- corporate_action_mismatch
- dividend_distribution_mismatch
- missing_ohlcv_policy_failure
- abnormal_return_unexplained
- benchmark_reconstruction_error
- identifier_mapping_error
- data_hash_mismatch
- license_lineage_failure
- source_version_mismatch
- calendar_mismatch
- reproducibility_failure
- unknown
```

---

# 7. Config Templates

## 7.1 Data Snapshot Config

**File:** `phase1a/configs/data_snapshot/DS-US-YYYYMMDD-v1.yml`

```yaml
data_snapshot_id: DS-US-YYYYMMDD-v1
status: draft

market: US
timezone: America/New_York
calendar_version: US-NYSE-v1

raw_sources:
  filing_floor:
    name: TODO_EDGAR_OR_EQUIVALENT
    role: filing_and_fundamental_floor
    source_release_timestamp: UNKNOWN
    vendor_source_version: UNKNOWN
    license_state: unknown
    confirmation_state: unknown

  price_return_universe:
    name: TODO_SURVIVORSHIP_AWARE_SOURCE
    role: price_return_universe_membership
    source_release_timestamp: UNKNOWN
    vendor_source_version: UNKNOWN
    license_state: unknown
    confirmation_state: unknown

  corporate_actions:
    name: TODO_CA_SOURCE
    role: splits_dividends_distributions
    source_release_timestamp: UNKNOWN
    vendor_source_version: UNKNOWN
    license_state: unknown
    confirmation_state: unknown

  identifier_mapping:
    name: TODO_ID_MAPPING_SOURCE
    role: security_identifier_history
    source_release_timestamp: UNKNOWN
    vendor_source_version: UNKNOWN
    license_state: unknown
    confirmation_state: unknown

extraction:
  extraction_date: YYYY-MM-DD
  extraction_timestamp: UNKNOWN
  extraction_timezone: America/New_York
  extracted_by: TODO_OWNER

point_in_time_rule:
  rule: no_data_before_availability_timestamp
  enforcement: block_on_violation
  notes: "For B0, filing/fundamental fields are placeholders. Required for B2+."

restatement_mode:
  mode: not_applicable_to_B0_or_as_filed_required_for_later
  enforcement: placeholder_for_B2_plus

corporate_action_policy:
  split_adjustment: required
  dividend_distribution_handling: required
  total_return_compatible: true
  reconciliation_required: true

delisting_inactive_policy:
  inactive_securities_retained: true
  delisted_securities_retained: true
  imputation_policy_id: TODO_OR_NA
  fail_if_missing_without_policy: true

missing_data_policy:
  missing_ohlcv_allowed: false_unless_documented
  severity_weighted_missingness: true
  fail_on_unexplained_critical_missingness: true

identifier_mapping:
  identifier_link_snapshot_id: IDMAP-US-YYYYMMDD-v1
  effective_date_ranges_required: true
  fail_on_unmapped_security: true

lineage:
  data_hash: TODO_SHA256
  transform_hash: TODO_SHA256_OR_NA
  raw_archive_path: TODO
  derived_archive_path: TODO

license:
  data_license_state: unknown
  allowed_use:
    research: unknown
    paper_trading: unknown
    production: unknown
    redistribution: unknown
    derived_storage: unknown
  fail_closed_if_unknown: true
```

---

## 7.2 Universe Config

**File:** `phase1a/configs/universe/UNI-US-v1.yml`

```yaml
universe_config_id: UNI-US-v1
status: draft

market: US
calendar_version: US-NYSE-v1

inclusion_rule:
  description: common_stock_eligible_universe
  share_code_whitelist_version: TODO
  exchange_rule: TODO
  primary_listing_rule: TODO
  IPO_seasoning_rule: TODO

exclusion_rule:
  exclude:
    - ETF
    - ADR
    - preferred
    - units
    - closed_end_fund
    - rights
    - warrants
    - funds
  notes: "Exact security type codes depend on chosen data vendor."

tradeability:
  halted_no_price_handling: TODO
  missing_price_handling: TODO
  illiquid_name_drop_rule: TODO
  liquidity_filter:
    enabled: false
    rule: TODO_FOR_LATER
    status: provisional

survivorship_policy:
  retain_inactive: true
  retain_delisted: true
  no_future_membership: true
  as_of_date_handling: strict_as_of

reconstitution:
  frequency: monthly_provisional
  signal_date_rule: month_end_as_of
  trade_date_rule: next_session_after_signal
  alternative_frequency_requires_new_trial_family: true

validation:
  required_gate_tests:
    - G-01
    - G-04
    - G-07
    - G-11
```

---

## 7.3 Benchmark Config

**File:** `phase1a/configs/benchmark/BMK-US-selfTR-v1.yml`

```yaml
benchmark_config_id: BMK-US-selfTR-v1
status: draft

benchmark_type: internal_self_built
purpose: actual_universe_total_return_sanity

market: US
calendar_version: US-NYSE-v1
universe_config_id: UNI-US-v1
data_snapshot_id: DS-US-YYYYMMDD-v1

construction:
  weight_basis: TODO_FULL_CAP_OR_FLOAT_ADJUSTED
  total_return_policy: include_dividends_and_distributions
  rebalancing_rule: monthly_provisional
  as_of_date_rule: month_end_as_of
  trade_date_rule: next_session_after_signal
  corporate_action_policy_id: DS-US-YYYYMMDD-v1.corporate_action_policy
  delisting_inactive_policy_id: DS-US-YYYYMMDD-v1.delisting_inactive_policy

drift_policy:
  internal_reconstruction_error:
    classification: hard_gate
    threshold: TODO_PROVISIONAL
    action_on_fail: block_B0
  external_comparator_difference:
    classification: diagnostic
    external_comparator_id: TODO_OPTIONAL
    action_on_difference: explain_not_auto_fail

outputs:
  benchmark_series_path: outputs/benchmark_series/BMK-US-selfTR-v1.csv
  benchmark_drift_report_link: reports/B0_benchmark_drift_report.md

validation:
  required_gate_tests:
    - G-05
    - G-06
    - G-09
    - G-12
```

---

## 7.4 Validation Config

**File:** `phase1a/configs/validation/VAL-B0-v1.yml`

```yaml
validation_config_id: VAL-B0-v1
status: draft

experiment_id: P1A-B0-YYYYMMDD-01
purpose: data_and_benchmark_sanity

split_design:
  chronological_only: true
  random_split_allowed: false
  train_window: not_applicable_for_B0
  validation_window: not_applicable_for_B0
  OOS_window: benchmark_reconstruction_period
  primary_walk_forward_scheme: not_applicable_or_calendar_replay
  alternative_walk_forward_scheme_requires_new_trial_family: true
  final_holdout_rule: not_applicable_for_B0
  final_holdout_freeze_id: NA

leakage_controls:
  no_test_set_tuning: true
  label_overlap_flag: false
  embargo_rule: not_applicable
  purging_rule: not_applicable

required_reports:
  data_gate_report: reports/B0_data_gate_report.md
  benchmark_drift_report: reports/B0_benchmark_drift_report.md
  reproducibility_manifest: reports/B0_reproducibility_manifest.md
  final_decision: reports/B0_final_decision.md

decision_policy:
  pass_if:
    - all_critical_B0_gates_pass
    - benchmark_internal_reconstruction_error_explained
    - reproducibility_manifest_complete
  quarantine_if:
    - noncritical_data_issues_are_isolated_and_documented
  fail_if:
    - any_critical_gate_fails
    - benchmark_cannot_be_reconstructed
    - lineage_hash_mismatch
    - license_unknown_outside_sandbox
```

---

## 7.5 Execution Support Placeholder Config

**File:** `phase1a/configs/execution_support/EXEC-placeholder-v1.yml`

```yaml
execution_support_config_id: EXEC-placeholder-v1
status: placeholder

purpose: B0_has_no_trading
order_handoff_mode: none
execution_algo_assumption: none
participation_cap: not_applicable
no_trade_buffer: not_applicable
broker_dependency: not_applicable

notes: "B0 reconstructs a benchmark and does not create orders. This placeholder exists to keep registry schema stable."
```

---

## 7.6 Monitoring Placeholder Config

**File:** `phase1a/configs/monitoring/MON-placeholder-v1.yml`

```yaml
monitoring_config_id: MON-placeholder-v1
status: placeholder

purpose: B0_monitoring_placeholder
paper_shadow_plan_id: NA_for_B0
daily_audit_fields:
  - data_gate_status
  - benchmark_drift_status
  - reproducibility_status
data_QA_alarm: enabled
benchmark_drift_alarm: enabled
cost_drift_alarm: not_applicable
signal_freshness_check: not_applicable

notes: "B0 has no alpha signal or portfolio order. Monitoring focuses on data QA and benchmark reconstruction."
```

---

# 8. Data Gate Report Template

**File:** `phase1a/reports/B0_data_gate_report.md`

```markdown
# B0 Data Gate Report

- experiment_id:
- data_snapshot_id:
- universe_config_id:
- benchmark_config_id:
- calendar_version:
- reviewer_id:
- review_date:
- decision: PASS / QUARANTINE / FAIL

## 1. Summary

| Gate | Status | Severity | Notes |
|---|---|---|---|
| G-01 PIT universe replay | TODO | Critical | TODO |
| G-04 Delisting/inactive inclusion | TODO | Critical | TODO |
| G-05 Corporate-action reconciliation | TODO | Critical | TODO |
| G-06 Dividend/distribution reconciliation | TODO | High | TODO |
| G-07 Missing OHLCV policy | TODO | High | TODO |
| G-08 Abnormal return/split detection | TODO | Medium | TODO |
| G-09 Benchmark internal reconstruction | TODO | High | TODO |
| G-11 Identifier mapping integrity | TODO | High | TODO |
| G-12 Data lineage/hash check | TODO | Critical | TODO |
| G-14 License lineage | TODO | Critical | TODO |

## 2. Placeholder Gates Not Applicable to B0

| Gate | Reason | Required later |
|---|---|---|
| G-02 No future fundamentals | B0 has no fundamental features | B2+ |
| G-03 Filing timestamp lag | B0 has no fundamental/filing features | B2+ |
| G-10 Cost data sanity | B0 has no trading cost | B1+ |
| G-13 Restatement leakage | B0 has no fundamental features | B2+ |

## 3. Gate Details

### G-01 PIT Universe Replay

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-04 Delisting / Inactive Inclusion

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-05 Corporate Action Reconciliation

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-06 Dividend / Distribution Reconciliation

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-07 Missing OHLCV Policy

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-08 Abnormal Return / Split Detection

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-09 Benchmark Internal Reconstruction

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-11 Identifier Mapping Integrity

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-12 Data Lineage / Hash Check

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

### G-14 License Lineage

- Input:
- Method:
- Pass condition:
- Result:
- Evidence path:
- Decision:

## 4. Failures

| failure_id | gate | severity | action | linked log |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |

## 5. Final Decision

- Data gate decision:
- Reviewer:
- Approval log id:
- Next action:
```

---

# 9. Benchmark Drift Report Template

**File:** `phase1a/reports/B0_benchmark_drift_report.md`

```markdown
# B0 Benchmark Drift Report

- experiment_id:
- benchmark_config_id:
- universe_config_id:
- data_snapshot_id:
- calendar_version:
- reviewer_id:
- review_date:
- decision: PASS / QUARANTINE / FAIL

## 1. Benchmark Definition

| Item | Value |
|---|---|
| internal benchmark | actual universe cap-weight total return |
| weight basis | TODO |
| total return policy | include dividends/distributions |
| rebalance rule | TODO |
| as-of date rule | TODO |
| trade date rule | TODO |
| universe source | TODO |
| corporate action source | TODO |
| dividend/distribution source | TODO |
| delisting/inactive policy | TODO |

## 2. Internal Reconstruction Error

This is a hard QA gate.

| Check | Result | Notes |
|---|---|---|
| benchmark series produced | TODO | TODO |
| all dates covered | TODO | TODO |
| all securities mapped | TODO | TODO |
| corporate actions reconciled | TODO | TODO |
| dividends/distributions reconciled | TODO | TODO |
| delisted/inactive handled | TODO | TODO |
| weight sums valid | TODO | TODO |
| unexplained drift exists | TODO | TODO |

## 3. External Comparator Difference

This is diagnostic only.

| Item | Value |
|---|---|
| external comparator id | TODO or NA |
| external comparator role | reporting only |
| difference summary | TODO |
| explained difference sources | TODO |
| unexplained difference sources | TODO |
| decision impact | diagnostic only |

## 4. Known Drift Sources

| Drift source | Internal reconstruction error? | External comparator difference? | Explanation |
|---|---:|---:|---|
| different universe | No / Yes | Yes | TODO |
| float-adjusted vs full-cap weights | TODO | TODO | TODO |
| dividend timing | TODO | TODO | TODO |
| delisting return treatment | TODO | TODO | TODO |
| corporate action timing | TODO | TODO | TODO |
| missing securities | TODO | TODO | TODO |
| calendar mismatch | TODO | TODO | TODO |

## 5. Reproducibility

| Item | Value |
|---|---|
| data_hash | TODO |
| code_version | TODO |
| environment_hash | TODO |
| config ids | TODO |
| rerun result identical? | TODO |
| output hash | TODO |

## 6. Decision

| Decision | Condition |
|---|---|
| PASS | internal reconstruction error is explainable and no critical data gates fail |
| QUARANTINE | non-critical drift exists but is isolated and documented |
| FAIL | unexplained internal reconstruction error or critical gate failure |

## 7. Final Notes

- Reviewer:
- Approval log id:
- Linked failure ids:
- Next action:
```

---

# 10. Reproducibility Manifest Template

**File:** `phase1a/reports/B0_reproducibility_manifest.md`

```markdown
# B0 Reproducibility Manifest

| Item | Value |
|---|---|
| experiment_id | TODO |
| run_id | TODO |
| data_snapshot_id | TODO |
| data_hash | TODO |
| universe_config_id | TODO |
| benchmark_config_id | TODO |
| validation_config_id | TODO |
| code_version | TODO |
| environment_hash | TODO |
| calendar_version | TODO |
| output_benchmark_hash | TODO |
| rerun_count | TODO |
| rerun_status | TODO |

## Reproduction Command / Procedure

No executable code in this document.  
Record the eventual command or procedure here after implementation.

```text
TODO
```

## Decision

- reproducibility_status: PASS / QUARANTINE / FAIL
- reviewer:
- notes:
```

---

# 11. B0 Final Decision Template

**File:** `phase1a/reports/B0_final_decision.md`

```markdown
# B0 Final Decision

- experiment_id:
- decision_date:
- reviewer_id:
- approval_log_id:
- final_decision: PASS / QUARANTINE / FAIL

## 1. Required Reports

| Report | Status | Link |
|---|---|---|
| data gate report | TODO | TODO |
| benchmark drift report | TODO | TODO |
| reproducibility manifest | TODO | TODO |
| failure log | TODO | TODO |
| approval log | TODO | TODO |

## 2. Decision Criteria

| Criterion | Status | Notes |
|---|---|---|
| all critical B0 gates passed | TODO | TODO |
| internal benchmark reconstructed | TODO | TODO |
| drift explained | TODO | TODO |
| data hash stable | TODO | TODO |
| license state acceptable | TODO | TODO |
| reproducibility manifest complete | TODO | TODO |
| failures resolved or quarantined | TODO | TODO |

## 3. Decision

- PASS:
- QUARANTINE:
- FAIL:

## 4. Next Action

If PASS:
- proceed to B1 1/N universe baseline preparation

If QUARANTINE:
- patch specific data/config issue
- rerun B0 under same or new trial family as required

If FAIL:
- stop Phase 1A implementation
- return to data source / universe / benchmark design
```

---

## 12. B0 Launch Checklist

Before running B0, every item below must be checked.

| Checklist item | Status |
|---|---|
| B0 registry row created | TODO |
| trial family registered | TODO |
| data snapshot config created | TODO |
| universe config created | TODO |
| benchmark config created | TODO |
| validation config created | TODO |
| execution placeholder created | TODO |
| monitoring placeholder created | TODO |
| source manifest updated | TODO |
| data license state recorded | TODO |
| calendar version fixed | TODO |
| code_version policy ready | TODO |
| environment_hash policy ready | TODO |
| data gate report template ready | TODO |
| benchmark drift report template ready | TODO |
| failure log ready | TODO |
| approval log ready | TODO |
| denylist lint ready | TODO |
| reviewer assigned | TODO |

---

## 13. What Comes After B0

If B0 passes:

```text
B1 = 1/N universe baseline
```

If B0 is quarantined:

```text
Patch data/config issue → rerun B0
```

If B0 fails:

```text
Stop Phase 1A implementation → revisit data source / universe / benchmark design
```

B1 must not begin until:

```text
B0 final decision = PASS
critical data gates pass
benchmark reconstruction is accepted
failure log is clean or quarantined
approval log is complete
```
