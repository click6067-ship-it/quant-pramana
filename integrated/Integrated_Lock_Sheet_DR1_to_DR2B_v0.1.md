# Integrated Lock Sheet v0.1
## DR-1 → DR-2A → DR-2B Consolidated Decisions

**Date:** 2026-06-08  
**Project:** Pramana systematic equity research / validation / trading operating system  
**Scope:** Locked decisions from DR-1, DR-1A, DR-2A, DR-2B, and Market Architecture Decision.  
**Non-scope:** alpha model selection, TSFM/LLM model research, quant firm ranking, final optimizer design.

---

## 0. Executive Summary

| Area | Final Decision |
|---|---|
| Market direction | **US-core first, KR-addon later** |
| U.S. data prototype | **GO** |
| Korean data prototype | **GO, but lower priority / pending prototype tests** |
| U.S. alpha research | **NO-GO until DR-3 validation gates pass** |
| Korean alpha research | **NO-GO until DR-2A prototype tests pass** |
| Next Deep Research | **DR-3 Validation Protocol** |
| Model candidate map | **Blocked until DR-3 is locked** |

---

## 1. Global Locked Principles

These principles are carried forward into every future research unit.

| Principle | Status |
|---|---|
| Signal is not order | LOCK |
| Alpha model is not position | LOCK |
| Portfolio optimizer converts forecast into weights | LOCK |
| Deterministic risk engine has final production veto | LOCK |
| LLM is off-path advisory / critic only | LOCK |
| Free-form LLM output cannot trigger order, veto, sizing, or regime switch | LOCK |
| Firm income, public track record, and user-replicable strategy return must remain separate | LOCK |
| Company references are evidence sources, not direct strategy templates | LOCK |
| Data honesty and cost honesty come before model sophistication | LOCK |

---

## 2. DR-1 Benchmark / Universe / Cost / Data Locks

| Item | Final Status | Notes |
|---|---|---|
| Benchmark and trading universe must be separated | LOCK | External benchmark is not automatically the tradable universe. |
| Internal benchmark | LOCK | Use self-built cap-weight total-return benchmark for the actual chosen universe where feasible. |
| External benchmark | PROVISIONAL | Use for reporting/comparison; exact candidate depends on market sleeve. |
| KOSPI100 | REJECT for Phase 1 cross-sectional universe | Too narrow. |
| S&P 500 | Reporting comparator | Too narrow as only broad cross-sectional research universe. |
| Cost model decomposition | LOCK | Commission, tax/levy, FX, dividend withholding, spread, slippage, market impact must be separated. |
| PIT / survivorship / delisting / CA requirements | LOCK | No alpha research before these are handled. |
| NXT/SOR as KR execution regime | LOCK | Must not be hidden inside generic slippage. |

---

## 3. DR-1A KR Official Source Gap Locks

| Item | Final Status | Notes |
|---|---|---|
| KRX300 | Conditional benchmark candidate | KRX source path and methodology must remain attached. |
| KRX300 TR | Conditional benchmark candidate | Existence/usefulness upgraded by Claude; still verify exact source/history path before final use. |
| KOSPI200 + KOSDAQ150 + liquidity filter | KR Phase 1 candidate universe | Candidate only; not final production universe. |
| KR transaction tax | Conditional Lock | Model as time-varying market/year rule; verify legal source and broker statement treatment. |
| NXT/SOR mechanism | LOCK | Separate KRX-only vs SOR-enabled execution regimes. |
| NXT/KRX customer fee pass-through | Requires broker confirmation | Do not infer from venue fee schedules alone. |
| KR PIT constituents | Provisional | Requires end-to-end reconstruction test. |
| KR corporate actions / dividends | Provisional | Official building blocks exist; normalization workflow must be tested. |
| KR delisting / survivorship | Provisional | Event availability is not equivalent to clean delisting-return handling. |
| OpenDART fundamentals floor | Provisional / floor | Useful free official floor, not clean research-grade PIT panel. |

---

## 4. DR-2A KR Data / PIT / Feature Architecture Locks

**Overall status:** PATCHED-LOCK  
**KR free-official prototype:** GO  
**KR alpha research:** NO-GO until prototype tests pass

| Item | Final Status |
|---|---|
| KR raw price/basic data architecture | LOCK |
| Raw / normalized / derived / feature-ready layer separation | LOCK |
| OpenDART fundamentals floor | LOCK as free floor |
| Filing date floor | LOCK as day-level |
| KOSPI200 PIT membership reconstruction | Provisional |
| KOSDAQ150 PIT membership reconstruction | Provisional |
| KRX300 PIT membership reconstruction | Provisional |
| KOSPI200 + KOSDAQ150 combined universe | Architecture Lock / Data Provisional |
| Custom liquidity-filtered universe | Provisional |
| Adjusted / unadjusted price layer | Provisional |
| Dividends | Provisional |
| Corporate actions | Provisional |
| Delisting / survivorship handling | Provisional |
| Research-grade normalized PIT fundamentals panel | Provisional |
| Earnings announcement dates | Provisional |
| PIT sector / industry history | Do not lock yet |
| Free-float PIT history | Do not lock yet / Requires vendor |
| NXT-eligible universe through time | Requires confirmation |
| Venue-level fill data | Requires broker confirmation |
| Broker routing metadata | Requires broker confirmation |
| Production/live data license | Requires legal/vendor confirmation |

### DR-2A Prototype Tests Required Before KR Alpha Research

1. PIT membership replay for KOSPI200 / KOSDAQ150 / KRX300  
2. Interim/ad-hoc constituent-change completeness test  
3. Free-float availability test  
4. OpenDART fundamentals completeness and restatement-leakage test  
5. Earnings event file test  
6. Corporate action and dividend reconciliation  
7. Delisting casebook and survivorship-safe panel test  
8. NXT/SOR venue-field test  
9. Benchmark / self-built TR sanity check  
10. Data license lineage test  

---

## 5. DR-2B US Data / PIT / Feature Architecture Locks

**Overall status:** PATCHED-LOCK  
**U.S. data prototype:** GO  
**U.S. alpha research:** NO-GO until DR-3 validation gates pass

| Item | Final Status |
|---|---|
| US-core first | LOCK |
| EDGAR as free official filing/fundamentals floor | LOCK as floor |
| U.S. prototype can start before CRSP/WRDS | LOCK |
| Paid-vendor production track required | LOCK |
| CRSP/Compustat/WRDS or equivalent production stack | Provisional production candidate |
| Norgate / Sharadar-class survivorship-aware vendor prototype | Provisional / strong candidate |
| S&P 500 PIT membership | Provisional |
| Russell 1000 PIT membership | Provisional |
| Russell 3000 PIT membership | Provisional |
| CRSP-style broad common-stock universe | Provisional |
| Russell-1000-like liquid universe | Provisional |
| CRSP price / return data | Provisional production candidate |
| CRSP delisting returns | Provisional with mandatory imputation |
| Inactive securities inclusion | LOCK as requirement; data source provisional |
| Share-code / exchange-code filters | LOCK as requirement; implementation provisional |
| Compustat fundamentals | Provisional production candidate |
| SEC EDGAR filing timestamps | LOCK as free official floor |
| Earnings announcement dates / RDQ | Provisional |
| CIK / GVKEY / PERMNO linking | Provisional |
| Sector / industry history | Do not lock yet / requires license or alternate floor |
| Self-built cap-weight TR benchmark inputs | Provisional |
| Research / paper / production data license | Requires vendor/legal confirmation |

### DR-2B Tests Required Before U.S. Alpha Research

1. PIT universe construction test  
2. Norgate / Sharadar / CRSP comparison test  
3. CRSP delisting imputation policy test  
4. Common-stock whitelist test  
5. Inactive securities inclusion test  
6. Identifier mapping and CCM link-validity test  
7. EDGAR filing lag test  
8. 8-K Item 2.02 earnings event test  
9. Corporate action and distribution reconciliation  
10. Self-built cap-weight TR sanity check  
11. Vendor/license lineage test  

---

## 6. Market Architecture Decision

| Area | Decision |
|---|---|
| Core market | U.S. first / U.S. core |
| Secondary market | Korea later / KR addon |
| Shared architecture | Research OS, PIT data contract, acceptance tests, validation protocol, feature timestamping, versioning |
| Market-specific adapters | Data source adapter, cost/tax adapter, execution adapter |
| Immediate priority | DR-3 Validation Protocol using US-core as primary pilot |
| KR handling | Keep KR prototype backlog; add as market adapter after DR-2A prototype tests pass |

---

## 7. What Is Still Blocked

| Area | Blocker |
|---|---|
| Model candidate map | Blocked until DR-3 validation protocol is locked |
| Alpha baseline | Blocked until data acceptance gates and validation gates are defined |
| KR alpha research | Blocked until DR-2A prototype tests pass |
| U.S. alpha research | Blocked until DR-3 defines acceptance and validation gates |
| Final optimizer / risk architecture | Blocked until model validation protocol is locked |
| Live / paper deployment | Blocked until execution, broker, and data-license checks |

---

## 8. Handoff to DR-3 Validation Protocol

DR-3 must define the validation gates that all future models must pass.

Required DR-3 topics:

1. Data acceptance gate  
2. PIT universe validation  
3. No-future-membership test  
4. No-future-fundamentals test  
5. Delisting imputation policy  
6. Corporate action / distribution reconciliation  
7. Self-built benchmark sanity check  
8. Cost / slippage / market-impact stress  
9. Train / validation / test split  
10. Walk-forward / rolling OOS  
11. Multiple-testing controls  
12. Deflated Sharpe / PBO / DSR  
13. Paper / shadow trading gate  
14. Promotion / quarantine / reject rules  

---

## 9. Final Status

**Integrated lock status:** COMPLETE THROUGH DR-2B  
**Next step:** DR-3 ChatGPT Deep Research Primary  
**Do not proceed to:** layer-by-layer model candidate map until DR-3 is complete.
