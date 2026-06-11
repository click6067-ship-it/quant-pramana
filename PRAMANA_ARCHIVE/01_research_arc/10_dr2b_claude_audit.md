# 10 · DR-2B Claude Red-Team Audit (US Data / PIT / Feature Architecture)

> **적대 레드팀 대상:** ChatGPT DR-2B (`09_dr2b_chatgpt_us_data_primary.md.md`) — US-equities Point-in-Time 데이터 아키텍처 설계.
> **방법:** deep-research 하니스 (fan-out 검색 → 소스 fetch → 3-vote 적대 검증 → 종합). 공식/고신뢰 US 소스(CRSP·Compustat/CCM·WRDS·FTSE Russell·S&P DJI·SEC EDGAR·MSCI GICS) 한정.
> **생성:** 2026-06-08. runId `wf_fb786617-774`.
> **규모:** 109 agent calls · sources fetched 26 · claims extracted 115 · verified 25 · confirmed 25 · killed 0 · findings 7.

---

## VERDICT — PATCH-BEFORE-LOCK

The adversarial verification strongly supports a PATCH-BEFORE-LOCK verdict against ChatGPT DR-2B: its two headline positions are both flawed. First, the "Lock CRSP delisting returns now" recommendation is overconfident and contradicted by the primary CRSP guide itself (which defines explicit missing-return codes -55.0/-66.0/-99.0) and by the canonical survivorship literature (Shumway 1997; Shumway-Warther 1999; Beaver-McNichols-Price 2007), which documents that ~99.8% of Nasdaq performance-related delisting returns and ~88% of NYSE/AMEX ones are MISSING, that the omitted returns average roughly -30% (NYSE/AMEX) to -55% (Nasdaq), and that omitting them biases backtests upward so severely the entire Nasdaq size effect vanishes after correction — so this item must be Provisional-with-mandatory-imputation, not Locked. Second, DR-2B's "do not lock / requires confidential subscription-only license" verdict for S&P 500 and Russell PIT membership, and its "Provisional" tag on SEC EDGAR, are SEARCH FALSE-NEGATIVES: Norgate Data provides cheap survivorship-aware PIT index membership (S&P 500 from Mar 1957, Russell 1000/3000 from Jul 1990), and SEC's data.sec.gov RESTful APIs deliver free, keyless, as-reported XBRL fundamentals (2009+), free Financial Statement Data Sets, and free intraday-timestamped 8-K Item 2.02 earnings dates — so EDGAR is a genuine free-official floor, not a passive one. The verification did NOT cover several DR-2B targets directly (GICS licensing, CCM linking internals, share/exchange-code taxonomy, ETF-holdings S&P/Russell proxies, RDQ-vs-8-K look-ahead specifics), so the synthesis confirms the red-team's core thesis on delisting-returns and EDGAR while leaving those audit sections unverified. Net: the correct posture is "prototype on free-official (EDGAR) + cheap survivorship-aware vendor (Norgate/Sharadar-class) data, DEFER the institution-gated CRSP/Compustat/WRDS lock," consistent with the project's free-first/solo ethos.

---

## Findings (적대 검증 통과)

### [1] Cheap, survivorship-aware commercial vendors provide US delisted-inclusive history and PIT index membership, undercutting DR-2B's premise that CRSP is required and that S&P 500 / Russell PIT membership is unobtainable without a confidential subscription-only license. Norgate Data offers a survivorship-bias-free US database of 25,222 delisted securities (1950 to Sep 2022) and PIT constituent membership for S&P 500 (from Mar 1957) and Russell 1000/3000 ($RUI/$RUA, from Jul 1990).
**confidence:** high · **vote:** 3-0 (both underlying claims unanimous)

Norgate's primary technical page states verbatim: 'containing 25222 delisted securities from the start of 1950 to Sep 2022' and that the Delisted DB only includes securities that traded on a major exchange and are no longer tradeable. The same Data Content Tables page confirms S&P 500 ($SPX) constituents start Mar 1957 with delisted stocks replaced immediately, and Russell 1000/3000 ($RUI/$RUA) constituents start Jul 1990. This is a CHEAP commercial subscription (Platinum/Diamond tiers), NOT the institution-gated CRSP/WRDS, so it materially contradicts DR-2B's 'do not lock — unobtainable without confidential subscription-only license' framing for the prototype track. Per the audit's own source discipline, vendor docs are admissible as evidence of data AVAILABILITY/FEASIBILITY (exactly this claim), not as authority on survivorship correctness.

**Sources:**
- https://norgatedata.com/
- https://norgatedata.com/data-content-tables.php


### [2] DR-2B's 'Lock CRSP delisting returns NOW' is OVERCONFIDENT and contradicted by CRSP's own official documentation: delisting returns are missing by design, with explicit missing-return codes (-55.0 = no source to establish post-delisting value or unable to value known distributions; -66.0 = >10 trading periods between last price and first new-exchange price; -99.0 = trades on new exchange but no price source; -88.0 = still active). Issues closed to further research with no criteria met get a missing code; issues pending research get -55.0. Therefore DLRET cannot be treated as fully populated — a mandatory imputation policy is required.
**confidence:** high · **vote:** 3-0 (claims 14 and 15, unanimous)

The official CRSP US Stock & Indexes Database Data Descriptions Guide contains a verbatim 'MISSING DELISTING RETURN CODES' table with -55.0/-66.0/-88.0/-99.0 and their stated reasons, plus methodology text: 'For any issue that is closed to further research and none of the above criteria are met, the delisting return is given a missing return code. For any issue that is pending further research, the delisting return is given a missing return code of -55.0.' Amount After Delisting 'is set to zero if the security is still active, if no price or payment information is available, or if the stock is worthless.' This is primary, issuer-authored evidence that the data-generating process itself produces structural gaps tied to performance-related delistings — directly refuting an unqualified 'Lock now.'

**Sources:**
- https://www.crsp.org/wp-content/uploads/guides/CRSP_US_Stock_&_Indexes_Database_Data_Descriptions_Guide.pdf


### [3] The canonical peer-reviewed survivorship literature documents that CRSP delisting returns are missing for the overwhelming majority of PERFORMANCE-related delistings (codes 500, 520-584), and the omitted returns are large and negative — so omitting them biases backtest returns upward and the raw DLRET field cannot be 'Locked now' without imputation. NYSE/AMEX: only 11.7% of performance-delisted stocks have a delisting return (1962-1993); Nasdaq: ~99.8% missing for performance-related delistings vs <1% for merger/exchange/migration. Over 4,500 performance delisting returns are missing in CRSP.
**confidence:** high · **vote:** 3-0 (claims 2, 3, 6, 16, unanimous)

Shumway (1997, Journal of Finance 52(1):327-340): 'Only 11.7 percent of the NYSE/AMEX stocks delisted for performance reasons have delisting returns, and none of the 3750 performance delisted stocks in the Nasdaq file has a delisting return'; 'Over 4,500 performance delisting returns are missing in the CRSP files. These returns correspond to delists that clearly affect firm value and that are not announced in advance.' Shumway-Warther (1999, JF 54(6):2361-2379): 'virtually all (99.8 percent) returns are missing for performance-related delistings... the missing returns will almost certainly introduce a bias'; abstract: 'the missing returns are large and negative on average.' All numbers verified verbatim against primary PDFs (Table I, Table V). Top-tier peer-reviewed sources, 600+ citations each.

**Sources:**
- https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf
- https://tylergshumway.org/Shumway-DelistingBiasCRSPs-1999.pdf
- https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00192


### [4] Concrete, standard imputation rules exist for missing CRSP delisting returns and can be adopted as hard acceptance-test gates: ~-30% (-29.9% empirical average; -0.3 fill for NQB-missing performance delists; -100% for confirmed-worthless) for NYSE/AMEX per Shumway (1997), and -55% for Nasdaq performance-related delists (~-40% raw price drop plus a liquidity/bid-ask-spread widening) per Shumway-Warther (1999). A finer alternative replaces each missing return with the AVERAGE return of SIMILAR delistings, operationalized in published SAS code by Beaver-McNichols-Price co-author Richard A. Price.
**confidence:** high · **vote:** 3-0 (claims 4, 5, 7, 12, 13, unanimous)

Shumway (1997): 'With 71 percent of the delisting returns accounted for, the average return is -30 percent'; Table V Line 5 average -29.9%; worthless firms -100.0%; Table VII note: 'Stocks that underwent a performance delist but are missing a new delisting return from NQB are given a delisting return of -0.3 in the OTC return column' — applied directly in replicating Fama-French (1992). Shumway-Warther (1999): 'we estimate the average effective return for stocks delisted from Nasdaq for performance reasons to be -55 percent... Researchers can use this estimated return to correct the CRSP database for the delisting bias,' decomposed via Eq.(1) (-40% raw) and Eq.(3) (bid-ask spread widening 0.41->0.82). Richard Price's page hosts _dlret_rv.sas ('macro to calculate replacement values for delisting returns') and delistings.sas, replacing missing returns 'with the average delisting return of similar delistings, rather than a single replacement value.'

**Sources:**
- https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf
- https://tylergshumway.org/Shumway-DelistingBiasCRSPs-1999.pdf
- https://sites.google.com/site/richardaprice3/research/delistings


### [5] Delisting-return treatment is a LIVE survivorship landmine that materially changes measured alpha, not a settled 'lock now' item: omitting missing/large-negative delisting returns biases anomaly returns, and the direction and magnitude of the effect depend on the strategy. After correcting for the Nasdaq delisting bias the entire documented size effect disappears (F-test p=0.0001 -> p=0.930; smallest-portfolio monthly return 3.79% -> 1.97%). Including delisting firm-years increases the extreme-decile spread for earnings/cash-flow/book-to-market strategies but significantly decreases the lowest-accruals-decile return. A large share of delistings is also excluded by common research-design choices independent of data quality.
**confidence:** high · **vote:** 3-0 (claims 8, 9, 10, 11, unanimous)

Shumway-Warther (1999): 'After correcting for the delisting bias, there is no evidence that there ever was a size effect on Nasdaq' (Table V: uncorrected F=3.52 p=0.0001 -> corrected F=0.58 p=0.930; smallest portfolio 3.79% -> 1.97%, a 48% reduction). Beaver-McNichols-Price (2007, J. Accounting & Economics 43:341-368): delisting firm-years 'are most often excluded because the researcher does not correctly incorporate delisting returns, because delisting return data are missing or because other research design choices implicitly exclude them'; 'the difference between average returns in extreme deciles increases when delisting firm-years are included... average returns in the lowest accruals decile decrease significantly'; 'requiring future earnings excludes two-thirds of delisting firm-years... nearly half of all delistings occur outside the date range provided by the CRSP/Compustat merged database.' All verified against publisher abstract and primary PDFs.

**Sources:**
- https://tylergshumway.org/Shumway-DelistingBiasCRSPs-1999.pdf
- https://www.sciencedirect.com/science/article/abs/pii/S0165410106000930


### [6] DR-2B's 'Provisional' tag on SEC EDGAR is a SEARCH FALSE-NEGATIVE: EDGAR is a genuine free-official source of point-in-time fundamentals, not a passive 'floor.' The data.sec.gov RESTful APIs (submissions history, XBRL company-concept, company-facts, frames) require NO authentication or API keys and deliver free as-reported XBRL fundamentals from 2009 onward (10-Q/10-K/8-K/20-F/40-F/6-K and variants) using standard taxonomies (us-gaap, ifrs-full, dei, srt). The SEC Financial Statement Data Sets (Jan 2009 - Mar 2026, quarterly ZIPs) provide the same as-filed (not restated) numeric data for free, and all EDGAR filings are free to access and download.
**confidence:** high · **vote:** 3-0 (claims 18, 19, 20, 22, 23, plus claim 21 at 2-0)

SEC API page verbatim: 'data.sec.gov was created to host RESTful data APIs delivering JSON-formatted data... These APIs do not require any authentication or API keys to access' and lists submissions, companyconcept, companyfacts, and frames endpoints; 'XBRL... was first required by the SEC in 2009' covering '10-Q, 10-K, 8-K, 20-F, 40-F, 6-K, and their variants.' Live reproduction against Apple CIK0000320193 returned 503 us-gaap concepts, earliest fact 2009-07-22, with as-reported fields (start/end/val/accn/fy/fp/form/filed/frame) enabling PIT filtering (filed<=as_of_date). Accessing-edgar-data page: 'Anyone can access and download this information for free.' Financial Statement Data Sets page: 'January 2009 - March 2026... numeric information from the face financials... extracted... using XBRL,' 'presented without change from the as filed financial reports' (as-reported, not restated). Only operational constraint is a 10 req/sec rate limit + descriptive User-Agent — no paywall, no key.

**Sources:**
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets


### [7] A free EDGAR earnings-date channel exists that DR-2B missed in relying on Compustat RDQ: SEC Form 8-K Item 2.02 ('Results of Operations and Financial Condition') is the standard item under which companies announce quarterly and annual results, typically attaching the earnings press release as Exhibit 99.1, and these submissions carry intraday acceptance timestamps. This is a viable free-official floor for earnings-announcement dates parallel to the RDQ look-ahead concern.
**confidence:** high · **vote:** 3-0 (claim 24, unanimous)

SEC investor bulletin 'How to Read an 8-K' states verbatim: 'Item 2.02 - Results of Operations and Financial Condition. Many companies announce their quarterly and annual results simultaneously in a press release and an 8-K (which includes the press release as an exhibit).' Independently corroborated by SEC EDGAR filings titled 'Form 8-K Item 2.02 Results of Operations,' Deloitte DART, and Cooley. Item 2.02 info is 'furnished' (not 'filed') under Reg FD, but remains a public EDGAR submission with an intraday acceptance timestamp — validating that the free EDGAR 8-K Item 2.02 earnings-date channel is real (the premise of the alleged ChatGPT false-negative on RDQ).

**Sources:**
- https://www.sec.gov/investor/pubs/readan8k.pdf


---

## Caveats / 미커버 영역

VERDICT SCOPE: The verified claims decisively support PATCH-BEFORE-LOCK on TWO of DR-2B's central positions — (1) the overconfident 'Lock CRSP delisting returns now' and (2) the false-negative 'Provisional/do-not-lock' tags on SEC EDGAR and on cheap survivorship-aware PIT index membership. They do NOT independently verify several other DR-2B audit targets, so those sections of the requested output remain unestablished by this evidence: GICS hidden-license dependency (Target 7), CCM linking internals / internal-inconsistency of locking Compustat fundamentals while linking is unresolved (Target 8), the CRSP SHRCD/EXCHCD taxonomy precision (Target 9), the SPY/IVV/VOO and iShares IWB/IWV/IWM ETF-holdings proxies for S&P/Russell PIT (Targets 5-6), and a direct head-to-head on RDQ documented errors vs the 8-K channel. SOURCE-QUALITY NOTE: Norgate is a VENDOR availability claim, admissible per the audit's own rules as feasibility evidence but NOT as authority on survivorship correctness relative to CRSP — and Norgate self-admits incompleteness (especially 1950s-early 1960s) and excludes OTC-only commons, preferreds, warrants, rights, convertibles. TIME-SENSITIVITY: The Shumway 1962-1993 / Nasdaq 1972-1995 missingness percentages are scoped to the historical CRSP files; CRSP has since backfilled some delisting returns, so a literal 'X% missing today' reading is stale — but the load-bearing conclusion (performance-delisting returns remain materially incomplete; imputation remains mandatory standard practice) holds, and the CRSP official guide's missing-codes are current. The Norgate page reflects the 2025 Russell methodology change (annual->semi-annual reconstitution), and one claim's loose phrasing ('Russell delisted names replaced immediately / IPOs added quarterly') is slightly imprecise versus current Norgate docs (Russell delisted names replaced only at reconstitution). EDGAR XBRL coverage starts ~2009 (XBRL mandate) and is 'as-filed/uncorrected' — free and PIT-capable, but NOT pre-validated; the SEC disclaimer warns of extraction errors, redundancies, and concept fragmentation (e.g., Revenues vs SalesRevenueNet vs custom extensions) that the consumer must normalize. This verification establishes free ACCESS and the as-reported-vs-restated property, not turnkey data cleanliness.

---

## Open Questions

- Is CRSP GICSHISTORY usable without a separate MSCI/S&P GICS license, and is free SIC (from EDGAR company metadata) or NAICS the correct free-official sector floor? (Target 7 unverified.)
- Do iShares IWB/IWV/IWM and SPY/IVV/VOO ETF daily holdings histories provide a sufficient free/cheap PIT proxy for Russell and S&P 500 membership, and how does their quality compare to Norgate's paid constituent history? (Targets 5-6 partially addressed only via Norgate.)
- What are the precise CCM PIT linking landmines (LinkType code set LC/LU/LX/LD/LN/LS/NR/NU, LinkPrim P/C/J/N, LinkDt<=date<=LinkEndDt filtering, GVKEY-IID secondary issues, ticker/CUSIP reuse), and does locking Compustat fundamentals while linking is unresolved make DR-2B internally inconsistent? (Target 8 unverified.)
- Are Compustat RDQ's documented errors/look-ahead severe enough that an EDGAR 8-K Item 2.02 channel should be the primary earnings-date source rather than a fallback, and does 8-K Item 2.02 cover all reporters with sufficient timestamp granularity for a daily-swing horizon? (Target 4 only partially established.)
- Which specific cheap/free vendor among Norgate, Nasdaq Data Link/Sharadar (SEP/SF1/ACTIONS/TICKERS), Tiingo, EODHD, Polygon, FMP, or OpenBB simultaneously delivers (i) delisted-inclusive history, (ii) split+dividend-adjusted total return, AND (iii) point-in-time fundamentals — only Norgate's delisted/index coverage was verified here.

---

## Sources (26)

- https://www.quantrocket.com/docs/data/fundamental/sharadar/ — secondary · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 4 claims
- https://data.nasdaq.com/databases/SF1 — secondary · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 5 claims
- https://norgatedata.com/ — primary · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 5 claims
- https://eodhd.com/financial-academy/financial-faq/survivorship-bias-free-financial-analysis — blog · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 3 claims
- https://www.tiingo.com/products/fundamental-data-api — unreliable · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 0 claims
- https://concretumgroup.com/historical-constituents-of-an-equity-index-in-python-norgate-data/ — blog · Cheap survivorship-aware vendor alternatives to CRSP (free-first challenge) · 5 claims
- https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 5 claims
- https://tylergshumway.org/Shumway-DelistingBiasCRSPs-1999.pdf — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 5 claims
- https://www.sciencedirect.com/science/article/abs/pii/S0165410106000930 — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 5 claims
- https://sites.google.com/site/richardaprice3/research/delistings — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 4 claims
- https://www.crsp.org/wp-content/uploads/guides/CRSP_US_Stock_&_Indexes_Database_Data_Descriptions_Guide.pdf — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 5 claims
- https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00192 — primary · CRSP delisting-return missingness (overconfident-lock landmine) · 4 claims
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces — primary · SEC EDGAR free intraday timestamps, XBRL APIs, 8-K Item 2.02 earnings dates (false-negative hunt) · 5 claims
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data — primary · SEC EDGAR free intraday timestamps, XBRL APIs, 8-K Item 2.02 earnings dates (false-negative hunt) · 5 claims
- https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets — primary · SEC EDGAR free intraday timestamps, XBRL APIs, 8-K Item 2.02 earnings dates (false-negative hunt) · 5 claims
- https://www.sec.gov/investor/pubs/readan8k.pdf — primary · SEC EDGAR free intraday timestamps, XBRL APIs, 8-K Item 2.02 earnings dates (false-negative hunt) · 5 claims
- https://github.com/talsan/ishares — secondary · Free PIT index membership via ETF holdings & official add/drop (Russell + S&P) · 5 claims
- https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund — primary · Free PIT index membership via ETF holdings & official add/drop (Russell + S&P) · 5 claims
- https://www.prnewswire.com/news/s&p-dow-jones-indices/ — primary · Free PIT index membership via ETF holdings & official add/drop (Russell + S&P) · 4 claims
- https://github.com/fja05680/sp500 — secondary · Free PIT index membership via ETF holdings & official add/drop (Russell + S&P) · 5 claims
- https://www.lseg.com/en/ftse-russell/russell-reconstitution — primary · Free PIT index membership via ETF holdings & official add/drop (Russell + S&P) · 5 claims
- https://www.spglobal.com/spdji/en/documents/methodologies/methodology-gics.pdf — primary · GICS licensing dependency vs free SIC/NAICS sector floor (hidden license) · 5 claims
- https://wrds-www.wharton.upenn.edu/pages/classroom/using-crspcompustat-merged-database/ — primary · GICS licensing dependency vs free SIC/NAICS sector floor (hidden license) · 3 claims
- https://en.wikipedia.org/wiki/Global_Industry_Classification_Standard — secondary · GICS licensing dependency vs free SIC/NAICS sector floor (hidden license) · 5 claims
- https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/linking-crsp-with-compustat/ — primary · CRSP-Compustat (CCM) PIT linking + share/exchange code taxonomy (internal inconsistency) · 3 claims
- https://www.crsp.org/wp-content/uploads/guides/CRSP_Compustat_Merged_Database_Guide.pdf — primary · CRSP-Compustat (CCM) PIT linking + share/exchange code taxonomy (internal inconsistency) · 5 claims

---

## Stats

```json
{
  "angles": 6,
  "sourcesFetched": 26,
  "claimsExtracted": 115,
  "claimsVerified": 25,
  "confirmed": 25,
  "killed": 0,
  "afterSynthesis": 7,
  "urlDupes": 3,
  "budgetDropped": 7,
  "agentCalls": 109
}
```