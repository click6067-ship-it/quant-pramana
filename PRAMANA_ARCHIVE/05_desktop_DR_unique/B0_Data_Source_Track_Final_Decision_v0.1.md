# B0 Data Source Track Final Decision v0.1
## Claude Primary + GPT Red-team 병합본

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-10  
**Scope:** Phase 1A B0 data-only benchmark sanity experiment — U.S. data source track decision  
**Non-scope:** implementation code, backtest, alpha model, stock recommendation, performance forecast

---

## 0. Final Verdict

| Item | Final decision |
|---|---|
| Overall status | **REVISE AND KEEP / PATCH-BEFORE-B0** |
| B0 implementation | **NO-GO until vendor/license confirmations are closed** |
| Prototype track | **Sharadar vs Norgate conditional prototype bake-off** |
| Production/research-grade track | **CRSP + Compustat/CCM via WRDS, deferred** |
| EDGAR role | **Official filing/fundamentals floor only** |
| EDGAR-only + free price | **Reject for B0** |

### One-line decision

> **Do not lock Sharadar yet.**  
> Final decision is **Sharadar vs Norgate conditional prototype bake-off**, with **CRSP/WRDS deferred as production-grade** and **EDGAR-only rejected for B0**.

---

## 1. What Changed After GPT Red-team

| Area | Claude Primary | GPT Red-team correction | Final merge |
|---|---|---|---|
| Sharadar priority | Primary prototype | Official field roster/license not closed | **Conditional primary candidate, not locked** |
| Norgate shares/cap field | Treated as refuted/missing | Official docs indicate shares/float/mktcap-like fields exist, but historical PIT suitability unclear | **Data field existence corrected; historical benchmark suitability requires confirmation** |
| Norgate limitation | Backup due to field uncertainty + Windows/EULA | Main blockers are legal/commercial/redistribution limits and Windows/NDU friction | **Strong backup or co-primary prototype; production blocked** |
| CRSP/WRDS | Production-grade deferred | Correct | **Keep** |
| EDGAR-only | Reject for B0 | Correct | **Keep** |
| B0 status | PATCH-BEFORE-B0 | Correct | **Keep** |

---

## 2. Final Data Source Track Classification

| Track | Final status | Use case | Why |
|---|---|---|---|
| **Sharadar + EDGAR** | **Conditional primary prototype candidate** | First candidate if field roster + license confirm | REST/API and small-team friendliness, but core fields/license unresolved |
| **Norgate + EDGAR** | **Strong backup / possible co-primary prototype candidate** | Candidate if historical cap inputs and personal prototype use are confirmed | Strong survivorship/PIT index/CA coverage; legal and Windows/NDU constraints |
| **CRSP + Compustat/CCM via WRDS** | **Production/research-grade / deferred** | Later production-grade or institutional research track | Gold-standard identifiers, delisting, cap-weight inputs, but access/cost barrier |
| **EDGAR-only + free price** | **Reject for B0** | Not valid for B0 | EDGAR is filing/XBRL floor, not survivorship-aware price/universe/benchmark panel |
| **Other cheap vendors** | **Do not lock yet** | Only if they beat Sharadar/Norgate on B0 requirements | Needs separate source audit |

---

## 3. Corrected Sharadar Position

### Final treatment

```text
Sharadar + EDGAR = Conditional primary prototype candidate
Status = Provisional / Requires vendor and legal confirmation
```

### Must confirm before B0

| Requirement | Status | Required evidence |
|---|---|---|
| Adjusted prices | Requires confirmation | official table/field roster or account schema capture |
| Unadjusted prices | Requires confirmation | official field/schema |
| Active + delisted coverage | Partially supported | official coverage statement + schema |
| Delisting/security status fields | Requires confirmation | official field/schema |
| Corporate actions | Requires confirmation | official field/schema |
| Dividends/distributions | Requires confirmation | official field/schema |
| Shares outstanding | Requires confirmation | official field/schema |
| Shares float | Requires confirmation | official field/schema |
| Market cap | Requires confirmation | official field/schema |
| Identifier history | Requires confirmation | official field/schema |
| Universe membership / constituents | Unknown | official field/schema |
| License for research | Requires legal confirmation | official terms |
| License for paper/sandbox | Requires legal confirmation | official terms |
| Derived storage / redistribution | Requires legal confirmation | official terms |

### Decision rule

Sharadar can become the primary prototype only if:

```text
1. field roster confirms price/return/CA/dividend/delisting/share-cap inputs
2. license permits at least research/sandbox B0 use
3. data export/API supports versioned snapshot storage
4. unknown terms are resolved or sandbox-fail-closed
```

---

## 4. Corrected Norgate Position

### Final treatment

```text
Norgate + EDGAR = Strong backup / possible co-primary prototype candidate
Status = Provisional prototype-only
```

### Corrected conclusion

The prior wording “Norgate shares/market-cap fields are missing/refuted” should be removed.

Correct wording:

> Norgate appears to expose shares outstanding / shares float / market-cap-like fields in official or package documentation, but whether these fields are available as historical PIT series suitable for B0 cap-weight benchmark reconstruction remains unconfirmed.

### Strengths

| Strength | Treatment |
|---|---|
| Survivorship-free / delisted coverage | strong |
| Historical index constituents | strong |
| Corporate action / capital event coverage | strong |
| Unadjusted close availability | useful |
| PIT index membership | useful |
| Personal prototype suitability | plausible |

### Blockers

| Blocker | Final treatment |
|---|---|
| Commercial use restriction | production blocker |
| Redistribution restriction | production/reporting blocker |
| Subscription lapse implications | requires confirmation |
| Windows / Norgate Data Updater dependency | implementation friction |
| WSL2/Linux integration | friction / workaround required |
| Historical PIT shares/cap series | requires confirmation |

### Decision rule

Norgate can become the prototype track if:

```text
1. historical shares/cap inputs are confirmed usable for B0
2. B0 use is legally allowed as personal/research/sandbox use
3. Windows/NDU operational friction is acceptable
4. production limitation is explicitly accepted
```

---

## 5. CRSP / WRDS Position

### Final treatment

```text
CRSP + Compustat/CCM via WRDS = Production/research-grade track, deferred
```

### Why deferred

| Reason | Treatment |
|---|---|
| Active/inactive security history | strongest |
| PERMNO/PERMCO identifier stability | strongest |
| Delisting return / missing delisting code handling | strongest |
| Shares outstanding / market cap | strongest |
| Corporate actions / dividends / distributions | strongest |
| CRSP index and universe support | strong |
| WRDS / institutional access | blocker for solo prototype |
| CRSP + Compustat dual subscription | cost/access blocker |

### Decision rule

If affordable legitimate access to CRSP/WRDS becomes available, it may override the prototype track.

Until then:

```text
Use as production-grade reference, not immediate B0 requirement.
```

---

## 6. EDGAR Position

### Final treatment

```text
EDGAR = official filing/fundamentals floor
EDGAR-only + free price = Reject for B0
```

### Why

| EDGAR can provide | EDGAR cannot provide for B0 |
|---|---|
| filings/submissions | survivorship-aware price history |
| XBRL/company facts | active/inactive stock return panel |
| filing timestamps | delisting return panel |
| official public filing floor | corporate-action-adjusted price panel |
| B2+ fundamentals support | self-built benchmark inputs by itself |

### Final role

```text
EDGAR is useful later for B2+ fundamentals and filing timestamp discipline.
It does not solve B0 by itself.
```

---

## 7. Final Requirement Fit Matrix

| B0 requirement | Primary candidate | Backup candidate | Production candidate | Final status |
|---|---|---|---|---|
| Price history | Sharadar | Norgate | CRSP | Requires confirmation |
| Adjusted price | Sharadar | Norgate | CRSP | Requires confirmation |
| Unadjusted price | Sharadar/Norgate | Norgate | CRSP | Requires confirmation |
| Volume | Sharadar/Norgate | Norgate | CRSP | Provisional |
| Shares outstanding / market cap | Sharadar if confirmed | Norgate if historical series confirmed | CRSP | **Critical confirmation** |
| Dividends | Sharadar if confirmed | Norgate | CRSP | Requires confirmation |
| Distributions | Sharadar if confirmed | Norgate | CRSP | Requires confirmation |
| Splits | Sharadar if confirmed | Norgate | CRSP | Requires confirmation |
| Corporate actions | Sharadar if confirmed | Norgate | CRSP | Requires confirmation |
| Inactive/delisted names | Sharadar/Norgate | Norgate | CRSP | Provisional |
| Delisting / terminal return | vendor + policy | vendor + policy | CRSP | Provisional |
| Identifier history | Sharadar if confirmed | Norgate if confirmed | CRSP | Requires confirmation |
| Universe membership through time | Unknown for Sharadar | Norgate strong | CRSP | Provisional |
| Benchmark constituent history | Unknown for Sharadar | Norgate strong | CRSP | Do not lock yet |
| Trading calendar | independent calendar | independent calendar | CRSP/WRDS | Lock rule |
| Data hash/versioning | internal | internal | internal | Lock rule |
| License state | unknown | prototype-only constraints | institutional/legal | Requires confirmation |

---

## 8. Final License / Legal Decision

| Source | Final treatment |
|---|---|
| Sharadar / Nasdaq Data Link | **Requires legal confirmation** before B0 outside sandbox |
| Norgate | **Prototype-only candidate; production blocked by commercial/redistribution restrictions unless license changes** |
| CRSP / WRDS | **Institutional/license-gated; production-grade if access confirmed** |
| EDGAR | **Public official filing floor** |
| Free price sources | **Reject for B0** |

### License rule

```text
Unknown license = fail-closed outside sandbox.
```

B0 can only proceed under one of these conditions:

```text
1. chosen source license explicitly permits research/sandbox B0 use
2. use is restricted to local sandbox with no redistribution and documented terms
3. legal/vendor confirmation is obtained
```

---

## 9. Final Implementation Friction Decision

| Source | Friction | Final implication |
|---|---|---|
| Sharadar | likely REST/API friendly, but schema/license unresolved | best if confirmed |
| Norgate | Windows/NDU/local DB dependency | acceptable only if operational friction is accepted |
| CRSP/WRDS | account/institution access | production-grade but not immediate |
| EDGAR | easy REST | useful floor only |
| Free price sources | easy but biased/incomplete | reject |

### WSL2/Linux preference

Given the project environment, a REST/API cross-platform source is preferred.  
However, data correctness outranks convenience.

Decision hierarchy:

```text
1. Data/legal correctness
2. PIT/survivorship/benchmark completeness
3. Reproducibility
4. Implementation convenience
```

---

## 10. Corrected Config Fill Plan

### 10.1 Data Snapshot Config

```yaml
data_snapshot_id: DS-US-YYYYMMDD-v1
raw_source:
  filing_floor: EDGAR
  price_return_universe: TODO_SHARADAR_OR_NORGATE
  corporate_actions: TODO_SHARADAR_OR_NORGATE
  identifier_mapping: TODO_SHARADAR_OR_NORGATE
vendor_source_version: REQUIRES_CONFIRMATION
source_release_timestamp: UNKNOWN_UNTIL_EXTRACTION
calendar_version: US-NYSE-v1
point_in_time_rule: no_data_before_availability_timestamp
corporate_action_policy: reconcile_splits_dividends_distributions
delisting_inactive_policy: retain_inactive_delisted_plus_terminal_policy
identifier_link_snapshot_id: TODO_VENDOR_IDMAP_SNAPSHOT
data_license_state: REQUIRES_LEGAL_CONFIRMATION
data_hash: TODO_AFTER_SNAPSHOT
```

### 10.2 Universe Config

```yaml
universe_config_id: UNI-US-v1
market: US
inclusion_rule: common_stock_eligible
share_code_whitelist_version: TODO_VENDOR_SPECIFIC
exclusion_rule:
  - ETF
  - ADR
  - preferred
  - units
  - closed_end_fund
  - rights
  - warrants
exchange_rule: TODO_VENDOR_SPECIFIC
primary_listing_rule: TODO_VENDOR_SPECIFIC
IPO_seasoning_rule: DO_NOT_LOCK_YET
liquidity_filter: DO_NOT_LOCK_YET
survivorship_policy: retain_inactive_and_delisted
as_of_date_handling: no_future_membership
```

### 10.3 Benchmark Config

```yaml
benchmark_config_id: BMK-US-selfTR-v1
benchmark_type: internal_self_built
weight_basis: TODO_FULL_CAP_OR_FLOAT_ADJUSTED
weight_input_requirement:
  requires: shares_outstanding_or_market_cap_history
  status: CRITICAL_CONFIRMATION_REQUIRED
total_return_policy: include_dividends_and_distributions
rebalancing_rule: monthly_provisional
internal_benchmark_source: TODO_CHOSEN_VENDOR
external_comparator: DO_NOT_LOCK_YET
drift_policy:
  internal_reconstruction_error: hard_gate
  external_comparator_difference: diagnostic_only
```

---

## 11. Final Decision Table

| Item | Final decision |
|---|---|
| Prototype source track | **Do not lock yet — Sharadar vs Norgate conditional bake-off** |
| Production source track | **CRSP + Compustat/CCM via WRDS — deferred** |
| EDGAR role | **Lock now — filing/fundamentals floor only** |
| CRSP/WRDS role | **Production-grade reference / deferred** |
| Norgate role | **Strong backup or co-primary prototype, prototype-only constraint** |
| Sharadar role | **Conditional primary candidate, requires field/license confirmation** |
| Free price source role | **Reject for B0** |
| B0 universe source | **Requires vendor confirmation** |
| B0 benchmark source | **Requires cap-weight input confirmation** |
| Corporate action source | **Requires vendor confirmation** |
| Delisting/inactive source | **Requires vendor confirmation** |
| License state | **Requires legal confirmation** |
| Implementation environment | **Prefer cross-platform REST, but correctness first** |
| Data export method | **Requires vendor confirmation** |
| B0 GO / NO-GO | **NO-GO until confirmations close** |

---

## 12. Required Patches Before B0

1. Obtain Sharadar official field/schema confirmation for adjusted price, unadjusted price, active/delisted status, corporate actions, dividends/distributions, shares outstanding, market cap, and identifiers.
2. Obtain Sharadar license confirmation for research, sandbox/paper use, derived storage, export, and redistribution.
3. Obtain Norgate confirmation on whether shares outstanding / market cap / shares float are available as historical PIT series suitable for cap-weight benchmark reconstruction.
4. Confirm Norgate personal research/sandbox B0 use is allowed under the actual use case.
5. Confirm Norgate subscription lapse consequences for stored local research snapshots.
6. Decide whether Windows/NDU operational friction is acceptable.
7. Keep CRSP/WRDS as production-grade deferred track unless legitimate access becomes available.
8. Reject EDGAR-only + free price for B0 in the source decision table.
9. Select one prototype source after the Sharadar/Norgate confirmation mini-check.
10. Fill B0 data_snapshot_config, universe_config, and benchmark_config only after the source is selected.
11. Keep all unresolved items as Unknown / Requires confirmation.
12. Do not implement B0 before P0-02 and P0-03 pass.

---

## 13. Next Handoff

```text
B0 Data Source Track Final Decision v0.1
    ↓
Vendor / license confirmation mini-check
    ↓
Sharadar vs Norgate final prototype source choice
    ↓
B0 config fill
    ↓
Pre-Implementation Gate P0-02 / P0-03 pass
    ↓
B0 implementation only
```

---

## 14. Short Mental Model

```text
CRSP is the gold standard but hard to access.
EDGAR is official but not enough.
Sharadar is convenient but needs schema/license proof.
Norgate is data-rich but legally/operationally constrained.

So the next step is not implementation.
The next step is a small vendor/license confirmation check.
```
