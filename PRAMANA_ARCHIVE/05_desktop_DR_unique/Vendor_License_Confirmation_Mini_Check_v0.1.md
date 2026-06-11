# Vendor / License Confirmation Mini-Check v0.1
## B0 Data Source Track Final Decision 이후 실행 문서

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-10  
**Scope:** Sharadar vs Norgate prototype source confirmation before B0  
**Non-scope:** implementation code, backtest, alpha model, stock recommendation, performance forecast

---

## 0. 지금 해야 하는 일

현재 B0 구현은 아직 시작하면 안 된다.

먼저 아래 2개 벤더 후보에 대해 **필드 + 라이선스 확인**을 끝내야 한다.

```text
1. Sharadar / Nasdaq Data Link
2. Norgate Data
```

결정 목표는 하나다.

```text
B0 prototype data source를 Sharadar로 할지, Norgate로 할지, 아니면 둘 다 보류하고 CRSP/WRDS 접근성을 확인할지 결정한다.
```

---

## 1. 현재 상태 요약

| 항목 | 상태 |
|---|---|
| B0 Data Source Track | **Sharadar vs Norgate conditional bake-off** |
| Sharadar | conditional primary candidate |
| Norgate | strong backup / possible co-primary prototype |
| CRSP/WRDS | production-grade / deferred |
| EDGAR | filing/fundamentals floor only |
| EDGAR-only + free price | reject |
| B0 implementation | **NO-GO until confirmations close** |

---

## 2. 왜 이 확인이 필요한가

B0는 data-only benchmark sanity experiment다.

B0의 핵심은 아래다.

```text
actual research universe의 self-built cap-weight total-return benchmark를
PIT-safe, survivorship-aware, reproducible하게 재구성할 수 있는가?
```

따라서 데이터 소스에는 최소한 아래가 필요하다.

| 필수 항목 | 이유 |
|---|---|
| adjusted / unadjusted price | 수익률·조정 검증 |
| active + delisted coverage | survivorship bias 방지 |
| corporate actions | split/dividend/distribution 정합성 |
| dividends / distributions | total-return benchmark 필수 |
| shares outstanding or market cap history | cap-weight benchmark 필수 |
| identifier history | ticker reuse / corporate action 추적 |
| universe membership / status through time | no-future-membership |
| license permission | sandbox/research/paper use 합법성 |
| export/snapshot permission | reproducible data snapshot 저장 |

---

## 3. Decision Tree

```text
A. Sharadar field roster + license가 모두 확인됨
   → Sharadar + EDGAR 선택
   → B0 config fill 진행

B. Sharadar가 불충분하지만 Norgate historical cap inputs + personal/sandbox use가 확인됨
   → Norgate + EDGAR 선택
   → Windows/NDU 운영 제약 수용 후 B0 config fill 진행

C. Sharadar와 Norgate 모두 cap-weight benchmark 입력이 불충분
   → B0 HOLD
   → CRSP/WRDS 접근성 또는 다른 survivorship-aware 벤더 확인

D. CRSP/WRDS 접근 가능
   → CRSP/WRDS로 B0 진행 가능
   → 비용/라이선스 확인 후 config fill
```

---

## 4. Sharadar Confirmation Checklist

### 4.1 Field / Schema Questions

Sharadar 또는 Nasdaq Data Link에 확인할 질문:

| ID | Question | Required answer | Status |
|---|---|---|---|
| S-F01 | Does the current Sharadar package provide both adjusted and unadjusted daily prices? | yes / no / field names | TODO |
| S-F02 | Does it include active and delisted U.S. securities? | yes / no / coverage notes | TODO |
| S-F03 | Does it include a delisted/security status field? | yes / no / field name | TODO |
| S-F04 | Does it include splits and split adjustment factors? | yes / no / field names | TODO |
| S-F05 | Does it include dividends and cash distributions? | yes / no / field names | TODO |
| S-F06 | Does it include shares outstanding? | yes / no / field name | TODO |
| S-F07 | Does it include shares float? | yes / no / field name | TODO |
| S-F08 | Does it include market cap, or can market cap be reconstructed from price × shares? | yes / no / method | TODO |
| S-F09 | Are shares outstanding / market cap available historically through time, not only current values? | yes / no / frequency | TODO |
| S-F10 | Does it provide stable identifiers beyond ticker, including mapping through ticker changes? | yes / no / identifier fields | TODO |
| S-F11 | Does it provide universe membership or security status through time? | yes / no / fields | TODO |
| S-F12 | Can the data be exported and snapshotted for reproducible research? | yes / no / terms | TODO |
| S-F13 | Is there an official field list / schema document for the relevant tables? | yes / no / link or attachment | TODO |

### 4.2 License Questions

| ID | Question | Required answer | Status |
|---|---|---|---|
| S-L01 | Is local research use allowed? | yes / no / terms | TODO |
| S-L02 | Is paper/sandbox backtesting allowed? | yes / no / terms | TODO |
| S-L03 | Is derived data storage allowed for internal reproducibility? | yes / no / limits | TODO |
| S-L04 | Is redistribution prohibited or allowed in limited form? | yes / no / terms | TODO |
| S-L05 | Is commercial/production use allowed under the subscription? | yes / no / requires upgrade | TODO |
| S-L06 | What happens to stored local snapshots after subscription lapse? | retain / delete / unknown | TODO |
| S-L07 | Are API/bulk download exports allowed for research pipelines? | yes / no / limits | TODO |
| S-L08 | Are there any restrictions on publishing aggregate research reports derived from the data? | yes / no / terms | TODO |

### 4.3 Sharadar Pass / Fail

| Result | Decision |
|---|---|
| All core fields + research/sandbox license confirmed | Sharadar selected |
| Core fields confirmed but license unclear | Hold / legal confirmation required |
| License confirmed but shares/mcap historical unavailable | Cannot use for cap-weight B0 unless equal-weight fallback approved |
| Field schema unavailable | Hold |
| Derived storage prohibited | Hold / reject for reproducible B0 |

---

## 5. Norgate Confirmation Checklist

### 5.1 Field / Schema Questions

| ID | Question | Required answer | Status |
|---|---|---|---|
| N-F01 | Does Norgate provide adjusted and unadjusted daily prices? | yes / no / field names | TODO |
| N-F02 | Does the subscription tier include active and delisted U.S. securities? | yes / no / tier | TODO |
| N-F03 | Does it include historical index constituents through time? | yes / no / tier | TODO |
| N-F04 | Does it include corporate actions / capital events? | yes / no / fields | TODO |
| N-F05 | Does it include dividends / distributions? | yes / no / fields | TODO |
| N-F06 | Does it include shares outstanding? | yes / no / field name | TODO |
| N-F07 | Does it include shares float? | yes / no / field name | TODO |
| N-F08 | Does it include market cap? | yes / no / field name | TODO |
| N-F09 | Are shares outstanding / float / market cap historical PIT time series or current-only fundamentals? | historical / current-only / unknown | TODO |
| N-F10 | Can those fields be used to reconstruct historical cap-weight benchmarks? | yes / no / caveat | TODO |
| N-F11 | Does it support stable identifiers through ticker changes / delistings? | yes / no / method | TODO |
| N-F12 | Can a fixed local snapshot be hashed and preserved for reproducibility? | yes / no / terms | TODO |

### 5.2 License / EULA Questions

| ID | Question | Required answer | Status |
|---|---|---|---|
| N-L01 | Is personal research/backtesting allowed? | yes / no / terms | TODO |
| N-L02 | Is local sandbox B0 benchmark reconstruction allowed? | yes / no / terms | TODO |
| N-L03 | Is commercial use prohibited? | yes / no / exact terms | TODO |
| N-L04 | Is redistribution prohibited? | yes / no / exact terms | TODO |
| N-L05 | Can internal derived metrics be stored locally? | yes / no / limits | TODO |
| N-L06 | What happens to local downloaded data after subscription lapse? | retain / delete / inaccessible / unknown | TODO |
| N-L07 | Can aggregate non-security-level research reports be kept after lapse? | yes / no / terms | TODO |

### 5.3 Implementation Questions

| ID | Question | Required answer | Status |
|---|---|---|---|
| N-I01 | Does Norgate require Windows Data Updater? | yes / no | TODO |
| N-I02 | Can WSL2/Linux workflows access the local database reliably? | yes / no / workaround | TODO |
| N-I03 | Can Python scripts export fixed snapshots? | yes / no | TODO |
| N-I04 | Can snapshot version and updater version be recorded? | yes / no | TODO |
| N-I05 | What tier is required for U.S. delisted securities and historical index constituents? | tier name | TODO |

### 5.4 Norgate Pass / Fail

| Result | Decision |
|---|---|
| Historical cap inputs + personal/sandbox use + acceptable Windows/NDU workflow confirmed | Norgate can be selected |
| Historical cap inputs unavailable | cannot support cap-weight B0 unless equal-weight fallback approved |
| License forbids local B0 research use | reject |
| Commercial restriction confirmed | still possible for prototype only, not production |
| Subscription lapse requires deletion/inaccessibility | document as major operational risk |

---

## 6. Evidence Capture Rules

For every answer, save evidence.

| Evidence type | Acceptable? | Notes |
|---|---:|---|
| Official documentation URL | yes | preferred |
| Vendor email reply | yes | save as PDF/text |
| Account schema screenshot/export | yes | acceptable if dated |
| Terms of service / EULA excerpt | yes | required for license |
| Sales chat without written follow-up | no | ask for written confirmation |
| Forum/blog answer | no | not sufficient |
| Model guess | no | not evidence |

Evidence file naming:

```text
evidence/
  sharadar/
    S-F06_shares_outstanding_YYYYMMDD.pdf
    S-L03_derived_storage_YYYYMMDD.pdf
  norgate/
    N-F09_historical_shares_YYYYMMDD.pdf
    N-L06_subscription_lapse_YYYYMMDD.pdf
```

---

## 7. Vendor Inquiry Template — Sharadar / Nasdaq Data Link

```text
Subject: Confirmation request for Sharadar/Nasdaq Data Link fields and license for internal benchmark research

Hello,

I am evaluating Sharadar/Nasdaq Data Link for an internal systematic equity research prototype.

The first use case is a data-only benchmark sanity test. It is not live trading and not redistribution. I need to reconstruct an internal, self-built, cap-weighted total-return benchmark for a U.S. equity research universe using historical, survivorship-aware data.

Could you confirm the following?

1. Does the current Sharadar package provide both adjusted and unadjusted daily prices?
2. Does it include active and delisted U.S. securities?
3. Does it include delisted/security status fields?
4. Does it include splits, dividends, and other distributions?
5. Does it include historical shares outstanding, shares float, or market cap through time?
6. Are these fields available historically, not only as current values?
7. Does it provide stable identifiers or mapping through ticker changes and delistings?
8. Does it include any historical universe membership or security-status history?
9. Is there an official schema/field list for the relevant tables?
10. Can the data be exported and stored as a local, versioned research snapshot for reproducibility?
11. Does the license allow internal research and sandbox/paper backtesting?
12. Does the license allow derived internal research artifacts to be stored?
13. What redistribution or publication restrictions apply?
14. What happens to locally stored data or derived datasets if the subscription lapses?

A written confirmation or official documentation link would be very helpful.

Thank you.
```

---

## 8. Vendor Inquiry Template — Norgate

```text
Subject: Confirmation request for Norgate historical fields, PIT suitability, and license for internal benchmark research

Hello,

I am evaluating Norgate Data for an internal systematic equity research prototype.

The first use case is a data-only benchmark sanity test. It is not live trading and not redistribution. I need to reconstruct an internal, self-built, cap-weighted total-return benchmark for a U.S. equity research universe using historical, survivorship-aware data.

Could you confirm the following?

1. Which U.S. subscription tier is required for active and delisted securities?
2. Which tier is required for historical S&P 500 / Russell 1000 / Russell 3000 constituents?
3. Does Norgate provide adjusted and unadjusted daily prices?
4. Does it include splits, dividends, distributions, and capital events?
5. Does it provide shares outstanding, shares float, or market cap?
6. Are shares outstanding, shares float, and market cap available as historical point-in-time time series, or only as current fundamentals?
7. Can those fields be used to reconstruct historical cap-weighted benchmarks?
8. Does Norgate provide stable identifiers or mapping through ticker changes and delistings?
9. Can Python scripts export fixed local snapshots for reproducible research?
10. Does this require the Windows Norgate Data Updater to be running?
11. Can the local database be used from WSL2/Linux workflows?
12. Does the EULA allow personal/internal research and sandbox backtesting?
13. Does the EULA prohibit commercial use and redistribution?
14. What happens to locally downloaded data and derived research artifacts after subscription lapse?

A written confirmation or official documentation link would be very helpful.

Thank you.
```

---

## 9. Mini-Check Decision Sheet

| Question | Sharadar answer | Norgate answer | Decision impact |
|---|---|---|---|
| adjusted + unadjusted prices | TODO | TODO | required |
| active + delisted coverage | TODO | TODO | required |
| corporate actions | TODO | TODO | required |
| dividends/distributions | TODO | TODO | required |
| historical shares / market cap | TODO | TODO | critical |
| identifier history | TODO | TODO | required |
| universe / PIT membership | TODO | TODO | useful |
| research/sandbox license | TODO | TODO | critical |
| derived storage allowed | TODO | TODO | critical |
| redistribution restrictions | TODO | TODO | risk |
| subscription lapse rules | TODO | TODO | risk |
| implementation friction | TODO | TODO | decision factor |

---

## 10. Final Selection Rule

After receiving evidence, decide:

```text
IF Sharadar confirms core fields + license
THEN choose Sharadar + EDGAR.

ELSE IF Norgate confirms historical cap inputs + personal/sandbox use + acceptable Windows workflow
THEN choose Norgate + EDGAR.

ELSE IF CRSP/WRDS access is available
THEN choose CRSP/WRDS.

ELSE
HOLD B0 and do not implement.
```

---

## 11. After Source Selection

Once the source is chosen, update:

```text
1. data_snapshot_config
2. universe_config
3. benchmark_config
4. source_manifest
5. experiment_registry row
6. evidence folder
7. license register
```

Then run:

```text
P0-02 Data Source Track Chosen
P0-03 License State Recorded
```

Only after both pass:

```text
Proceed to B0 implementation.
```

---

## 12. Current Next Step

The next action is manual/vendor confirmation, not code.

```text
1. Send Sharadar inquiry
2. Send Norgate inquiry
3. Save written evidence
4. Fill Mini-Check Decision Sheet
5. Choose source
6. Fill B0 config
```
