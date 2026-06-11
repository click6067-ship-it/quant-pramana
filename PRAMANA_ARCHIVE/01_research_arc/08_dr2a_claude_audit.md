# 08 · DR-2A Claude Red-Team Audit (KR Data / PIT / Feature Architecture)

> **적대 레드팀 대상:** ChatGPT DR-2A (한국 Phase-1 PIT 데이터 아키텍처 설계).
> **방법:** deep-research 하니스 (fan-out 검색 → 소스 fetch → 3-vote 적대 검증 → 종합).
> **생성:** 2026-06-07. runId `wf_c5ba285e-03d` — 최초 실행이 Verify 도중 abort(튕김) → 동일 runId journal 캐시로 resume하여 완주.
> **규모:** 102 agent calls · sources fetched 20 · claims extracted 83 · verified 25 · confirmed 20 · killed 5 · findings 9.

---

## VERDICT — PATCH-BEFORE-LOCK

VERDICT on ChatGPT DR-2A: PATCH-BEFORE-LOCK. The audit confirms three categories of error. (1) Genuine SEARCH FALSE-NEGATIVES where ChatGPT said "do not lock / requires vendor" but a free official source demonstrably exists: earnings-announcement dates are retrievable free as discrete, individually-addressable, day-dated Fair-Disclosure events on KIND/DART (영업(잠정)실적/영업실적 전망, 공정공시 category I002); and a free FSC-published listed-securities master (data.go.kr/15094775) with an unrestricted commercial license exists, undercutting reliance on the non-commercial KRX Open API for the security-master layer. (2) Genuine OVERCONFIDENT LOCKS: PIT membership "Lock now" is premature — the free KRX constituent endpoint (MDCSTAT00601/trdDd via pykrx) does serve as-of-date per-name snapshots with MKTCAP (enabling replay cross-validation), but it is hard-floored at 2014-05-01 (cannot reconstruct pre-2014 constituents), returns NO free-float field, and the notice-board completeness for interim/ad-hoc (수시) changes could not be confirmed — so it remains a feasibility floor, not a validated Lock. Free-float PIT history is absent from the free endpoint, which hardens both index-replay and self-built float-adjusted TR from "Provisional" toward "do-not-lock/requires-vendor." (3) ChatGPT correctly identified real production blockers but soft-pedaled severity: the KRX Open API terms genuinely impose both non-commercial-use and no-redistribution restrictions (binding, enforceable), which block a live/commercial system on that free channel — though the separate paid KRX Market Data license only bars redistribution-for-profit, not all commercial use. OpenDART structured fundamentals are confirmed solid (2015+ floor, all 5 statements via sj_div, CFS/OFS, quarterly+annual) but filing timestamps are day-granular only (no intraday), and 기업개황 industry code is current-snapshot only (no PIT industry history from that endpoint).

---

## Findings (적대 검증 통과)

### [1] PIT membership 'Lock now' is OVERCONFIDENT — the free KRX constituent endpoint serves as-of-date per-name snapshots (enabling replay cross-validation) but is hard-floored at 2014-05-01, lacks any free-float field, and interim/ad-hoc (수시) notice completeness is unverified. Revised status: Provisional / feasibility-floor, NOT Lock.
**confidence:** high · **vote:** 3-0 (composite of claims 0,1,2,3,4,5)

KRX endpoint MDCSTAT00601 (지수구성종목) accepts trdDd=date and returns per-name ISU_SRT_CD/ISU_ABBRV/TDD_CLSPRC/MKTCAP for the as-of date (claims 0,1 — primary code, 3-0), enabling a dated snapshot for replay cross-validation, NOT just a current name list. BUT: (a) hard depth floor — get_index_portfolio_deposit_file returns [] for any target_date <= 20140501 ('KRX web server does NOT provide data prior to 2014/05/01'), so pre-May-2014 constituents are unreconstructable via the free channel (claim 3, 3-0); (b) NO free-float / 유동주식 ratio column exists in the returned fields (claim 1, 3-0); (c) the official 주가지수 공지 board exists with proper structure (claim 4, 2-0) but its actual notice rows are JS-rendered and could NOT be statically confirmed to publish ALL interim/ad-hoc 편입/편출 changes or historical as-of snapshots (claim 5, 3-0). Therefore the failure mode ChatGPT itself listed ('수시변경 omission risk') is unresolved while it rated membership 'Lock now' — internally inconsistent. A feasibility floor cannot be Locked without a validated replay prototype reconciling regular+interim changes against dated snapshots.

**Sources:**
- https://github.com/sharebook-kr/pykrx/blob/master/pykrx/website/krx/market/core.py
- https://github.com/sharebook-kr/pykrx/blob/master/pykrx/stock/stock_api.py
- https://data.krx.co.kr/contents/MDC/COMS/board/MDCCOMS010_S1.cmd?boardId=MDCINFO005


### [2] EARNINGS-ANNOUNCEMENT DATES are a ChatGPT FALSE-NEGATIVE — a free official, individually-addressable, day-dated earnings-event channel demonstrably exists on KIND/DART (Fair-Disclosure 공정공시, category I002), distinct from the periodic-report filing date. ChatGPT's 'do not lock / requires vendor' on earnings dates is wrong.
**confidence:** high · **vote:** 3-0 / 2-1 (claims 12,13,14)

OpenDART list API exposes searchable disclosure category I=거래소공시 with detail subtype I002=공정공시 (Fair Disclosure) and I001=수시공시 as REQUEST/FILTER parameters (pblntf_ty/pblntf_detail_ty), so fair-disclosure events are retrievable free by category (claim 12, 3-0, primary). Concrete real instances confirm the discrete event type: '영업실적 등에 대한 전망(공정공시)' (forward earnings forecast, acptno 20251029000126, 한세예스24홀딩스, 2025.10.29) and the parallel realized-results type '연결재무제표기준 영업(잠정)실적(공정공시)' exist on KIND as standalone disclosures separate from periodic reports, statutorily distinguished per easylaw.go.kr (claim 13, 2-1). Each event carries a unique acptno (YYYYMMDD + 6-digit serial), is individually addressable on the free KIND viewer without auth/paywall (claim 14, 3-0). PRECISION CAVEAT: granularity is DAY-level (공시일자) plus an intraday receipt-order serial, NOT an HH:MM timestamp — sufficient for PIT trading-day event-dating but not sub-day. Revised status for earnings dates: Provisional / Lockable as a free-official floor, NOT 'requires vendor'.

**Sources:**
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001
- https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=20251029000126&docno=&viewerhost=


### [3] A FREE FSC listed-securities master exists with an UNRESTRICTED commercial license — undercutting ChatGPT's reliance on the non-commercial-restricted KRX Open API for the security-master / instrument-identifier layer (false-negative).
**confidence:** high · **vote:** 3-0 (claim 8); note one refuted over-broad variant

data.go.kr/15094775 (금융위원회_KRX상장종목정보, published by the FSC on Korea's official public-data portal) furnishes 기준일자, 단축코드, ISIN코드, 시장구분, 종목명, 법인등록번호, 법인명 — free (무료), REST/JSON+XML, daily T+1 update (claim 8, 3-0, primary). The detail/license page lists 이용허락범위 = '제한 없음' (no usage-rights restriction), i.e., commercial use permitted, providing an official free security-master source not subject to the KRX Open API's non-commercial bar. CAVEAT: a related broader claim ('this source carries NO non-commercial/redistribution restriction at all, license 제한 없음') was REFUTED at 1-2 — treat the unrestricted-license assertion as supported for the master-data field set but do not over-extend it as a blanket finding; verify the exact license text before relying on it for redistribution. Underlying data is KRX-origin re-published by FSC.

**Sources:**
- https://www.data.go.kr/data/15094775/openapi.do
- https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15094775


### [4] The KRX Open API non-commercial-use AND no-redistribution restrictions are REAL and BINDING production blockers that ChatGPT soft-pedaled — they block a live/commercial trading system on that free channel (not an overstatement).
**confidence:** high · **vote:** 3-0 (claims 6,7)

KRX Open API Terms Article 6(2): 'API Users may only use the API Service for non-commercial purposes and may not charge third parties any consideration for the results' (verbatim KR: 'API 이용자는 API 서비스를 비상업적인 목적으로만 이용할 수 있으며...') (claim 6, 3-0, primary, both languages). Article 11(2): 'The API User may not provide the data provided by the KRX to any third parties' (no redistribution) (claim 7, 3-0). Bindingness confirmed by Art 11(4)/(5): KRX may withdraw authorization, suspend service, and claim damages. Terms effective 2025-12-26, current. This is a genuine blocker for any live/commercial KR system pulling via the free Open API channel — ChatGPT's vague 'non-commercial use restriction in the API FAQ' under-stated its severity and channel-specificity.

**Sources:**
- https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO005.jsp
- https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO002.jsp


### [5] The SEPARATE paid KRX Market Data license bars only redistribution-FOR-PROFIT (Art 9 Clause 5), not all commercial use — so the two KRX channels (free Open API vs paid Market Data) have DIFFERENT terms and must be tracked separately; ChatGPT conflated them.
**confidence:** medium · **vote:** 2-1 (claim 9); related carve-out variant refuted

KRX Market Data Terms Art 9(5): '이용자는 마켓데이터의 단순 복제, 게시, 표출 및 재분배 등의 행위를 통하여 수익을 창출할 수 없다' — restricts revenue-from-simple-redistribution, NOT a blanket 상업적 이용 금지 (claim 9, 2-1, primary). This is the paid Marketplace data license, structurally distinct from the stricter free Open API (Art 6 non-commercial-only). For DR-2A this distinction is load-bearing: a licensed Market Data buyer is barred only from redistribution-for-profit, whereas the free Open API channel is non-commercial-only. CAVEAT: the variant claim that derived/processed 'original works' and indirect-revenue web posting are explicitly permitted was REFUTED at 1-2 — do NOT rely on the carve-out interpretation; the split vote and refuted variant mean the precise scope of permitted derived/commercial use needs direct legal confirmation before production. Hence 'medium' confidence.

**Sources:**
- https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO002.cmd


### [6] OpenDART structured fundamentals are SOLID and largely Lockable: 2015+ business-year floor, all five statements (BS/IS/CIS/CF/SCE) via sj_div, consolidated vs separate via fs_div (CFS/OFS), and both quarterly + annual via reprt_code. ChatGPT's 'Lock now' on OpenDART fundamentals is supported on coverage — but pre-2015 fundamentals are NOT available via the structured API.
**confidence:** high · **vote:** 3-0 (claims 17,18,19)

fnlttSinglAcntAll (단일회사 전체 재무제표): bsns_year note '사업연도(4자리) ※ 2015년 이후 부터 정보제공' — structured data from FY2015 only; pre-2015 not served by this API (claim 17, 3-0, primary). sj_div distinguishes exactly five statements: BS=재무상태표, IS=손익계산서, CIS=포괄손익계산서, CF=현금흐름표, SCE=자본변동표 (claim 18, 3-0, KR+EN primary). fs_div REQUIRED with CFS=연결/OFS=개별; reprt_code 11013=Q1, 11012=half-year, 11014=Q3, 11011=annual (claim 19, 3-0, primary + EN portal + 3 client libs). SCOPE CAVEAT for acceptance testing: these claims establish SCHEMA coverage only, NOT per-company/per-period data COMPLETENESS — documented real omissions exist (GitHub OpenDartReader #23), so a fundamentals completeness/restatement-leakage test is still warranted beyond schema coverage.

**Sources:**
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
- https://engopendart.fss.or.kr


### [7] Filing timestamps are DAY-granular only — OpenDART list API rcept_dt is YYYYMMDD with NO intraday time-of-day field. ChatGPT's reliance on a filing-timestamp floor is correct only at day granularity; intraday leakage control needs a separate mechanism.
**confidence:** high · **vote:** 3-0 (claim 11)

The OpenDART 공시검색(list) API documents rcept_dt as '공시 접수일자(YYYYMMDD)' — 8-char date only; the full field set (status...corp_code, stock_code, report_nm, rcept_no, flr_nm, rcept_dt, rm) contains NO rcept_tm or time-of-day field (claim 11, 3-0, primary). So the free list API delivers a day-level filing-date floor, not an intraday timestamp. CAVEAT (non-refuting): rcept_no's leading 8 digits = YYYYMMDD and the DART web frontend surfaces a submission time in some views, so intraday time may be obtainable elsewhere, but NOT via this free field. Implication for DR-2A: same-day point-in-time alignment (filing before vs after market) cannot be done from rcept_dt alone — needs the receipt-serial ordering or the web-view submission time, and an acceptance test for same-day look-ahead.

**Sources:**
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001


### [8] PIT SECTOR/INDUSTRY HISTORY is a PARTIAL false-negative: the industry code (induty_code, KSIC) IS freely available — but only as a CURRENT snapshot from 기업개황, with NO as-of-date parameter, so the free OpenDART endpoint does NOT provide point-in-time historical industry classification. ChatGPT's 'requires vendor' is too strong for current data but a genuine gap remains for PIT history via this endpoint.
**confidence:** high · **vote:** 3-0 (claims 15,16)

OpenDART 기업개황 (company-overview) API exposes induty_code (업종코드, KSIC minor/3-digit), keyed by corp_code with a free key (claim 15, 3-0, primary; e.g., Samsung corp_code 00126380 returns induty_code '264'). BUT its only inputs are crtfc_key + corp_code — NO date/year/as-of parameter — so it returns the CURRENT registered profile, not historical PIT records (claim 16, 3-0, primary; dart-fss docs corroborate 'no mechanism to query data as of specific historical dates'). SCOPE: this proves only THIS endpoint lacks PIT industry history; it does NOT establish that KR sector history is unobtainable free overall (KRX 업종분류 board / per-filing KSIC reconstruction were not tested). Revised: current industry = free/Lockable floor; PIT industry HISTORY = do-not-lock-yet / needs a reconstruction prototype or vendor, but 'requires vendor' is not fully exhausted.

**Sources:**
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002


### [9] Disambiguation guard (prevents a false-positive in the audit): the 'S&P/KRX Exchanges Index' is an S&P-DJI-owned GLOBAL index of financial-exchange COMPANIES (GICS 40203040), NOT the KOSPI200/KOSDAQ150/KRX300 domestic equity indices the DR-2A audit concerns.
**confidence:** high · **vote:** 3-0 (claim 10)

S&P DJI methodology: index 'comprised of leading publicly traded financial exchanges... classified as part of the GICS Financial Exchanges & Data Sub-Industry (code: 40203040)... owned, calculated, maintained and distributed by S&P Dow Jones Indices' (claim 10, 3-0, primary). This is a thematic global-sector index, structurally distinct from KRX's domestic broad-market indices. Relevance: a search for 'KRX index' must not pull this S&P-owned product into the PIT-membership work; the claim scopes it OUT and protects the audit from a false-positive. Does not bear on any Lock decision directly.

**Sources:**
- https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-krx-exchanges.pdf


---

## Caveats / 시간민감성

SCOPE OF VERIFICATION: This synthesis is bounded by the 20 confirmed claims; it did NOT independently re-run KRX/OpenDART/KIND endpoints. Several load-bearing red-team questions are confirmed only at the DATA-ACCESS-FEASIBILITY level (via pykrx primary code + official portals), NOT as validated end-to-end replays — exactly the DR-1A 'feasibility floor' caveat the project established. SOURCE-QUALITY NOTES: pykrx (open-source) is used only as data-access feasibility evidence, clearly labeled, never as authority for index methodology; the substantive authorities are KRX, OpenDART/FSS, KIND, FSC/data.go.kr, S&P DJI. SPLIT-VOTE / REFUTED CAUTIONS: (1) the KRX Market Data 'commercial use allowed except redistribution-for-profit' reading is 2-1 with a related carve-out variant REFUTED 1-2 — do not rely on derived-work/indirect-revenue carve-outs without direct legal confirmation. (2) The FSC master-data 'license 제한 없음 = no restriction at all' broad variant was REFUTED 1-2; the field-set free availability is solid but verify the exact license text before assuming unrestricted redistribution. (3) The pykrx documented example call demonstrating a 2021-01-25 historical query was REFUTED 1-2, and direct anonymous programmatic access to the data.krx.co.kr loader screen returned 'LOGOUT'/login-required in some attempts (refuted as a blanket claim 1-2) — so live programmatic retrieval may require session handling; the as-of-date CAPABILITY is confirmed at the API-parameter level but the practical free-access path needs a working prototype to confirm. TIME-SENSITIVITY: KRX Open API terms are dated 2025-12-26 and could change; the 2014-05-01 free-constituent floor is a current limit of the scraped web endpoint (paid KRX marketplace 'past index constituents' product may extend depth at cost). GRANULARITY: all confirmed 'timestamp' findings (filing dates, earnings events) are DAY-level (+ intraday receipt serial), NOT sub-day HH:MM — intraday same-day look-ahead control needs a separate mechanism. NO DR-1 Final Lock Sheet was available to cross-check against, as stated in the brief.

---

## Open Questions (이번 라운드 미해결)

- Does the KRX 주가지수 공지 board (or the MDCSTAT00601 historical snapshots) reliably capture ALL interim/ad-hoc (수시변경) constituent changes from delistings/M&A/transfers — not just semi-annual regular rebalances? This was unverifiable from static HTML (JS-rendered) and is the decisive gate for upgrading PIT membership from feasibility-floor to Lock. A working replay-reconciliation prototype is required.
- Is point-in-time FREE-FLOAT (유동주식비율) ratio history obtainable from any FREE official KRX channel (the data.krx.co.kr loader screens or a paid-only marketplace product), given the free constituent endpoint returns no free-float field? Without it, both the index-selection replay (10% min free-float criterion) and the self-built float-adjusted cap-weight TR benchmark are blocked — likely a do-not-lock/requires-vendor, harder than ChatGPT's 'Provisional'.
- Can KR POST-DELISTING return path / final tradable price + delisting reason be captured free (KIND + KRX daily), or is post-delisting return genuinely unobtainable free (forcing a sensitivity-band approach)? This DR-2A target (item 6) was not covered by any confirmed claim and needs direct verification against KIND 상장폐지/정리매매 data and Korean involuntary-delisting academic findings.
- What is the exact, legally-precise scope of (a) the free FSC master-data license and (b) the paid KRX Market Data redistribution-for-profit clause for a live/commercial derived-signal trading system — given the split votes and refuted carve-out variants, does a compliant free-or-licensed path to LIVE commercial operation actually exist, or does production require a paid vendor (FnGuide/Bloomberg) track as ChatGPT's split-track recommendation implies?

---

## Refuted claims (적대 검증서 탈락 — 투명성)

- "The documented example call (지수구성종목().fetch("20210125", "001", "1")) demonstrates retrieval of constituents for a specific historical date (2021-01-25), confirming the date-parameterized historical query works in practice via the documented bld endpoint." — vote 1-2 · https://github.com/sharebook-kr/pykrx/blob/master/pykrx/website/krx/market/core.py
- "The KRX 정보데이터시스템 index-constituent statistics loader page at menuId=MDC0201010106 is not anonymously accessible: requesting it returns an HTML page that immediately alerts 'login or signup required' and force-redirects to the KRX login page, so its substantive content (constituent fields, any as-of-date picker, free-float columns) cannot be read without an account." — vote 1-2 · https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201010106
- "The underlying data API call for this screen (getJsonData.cmd with bld=dbms/MDC/STAT/standard/MDCSTAT00601, the 지수구성종목 / index-constituent dataset, parameterized by trdDd as-of-date and indIdx index family) returns only the string 'LOGOUT' (6 bytes) and no JSON when invoked without an authenticated session, indicating server-side session/auth gating on programmatic retrieval from this environment." — vote 1-2 · https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201010106
- "The FSC KRX listed-securities open API is distributed under '이용허락범위 제한 없음' (no usage-rights restriction) and is free of charge ('비용부과유무: 무료'), meaning this official government source for KR listed-securities master data carries NO non-commercial / redistribution restriction that would block a live-capable trading system." — vote 1-2 · https://www.data.go.kr/data/15094775/openapi.do
- "KRX Terms explicitly permit revenue-generating use when the purchased data is processed into an 'original/creative work' (독창성 있는 저작물), and permit posting on a web page where indirect revenue arises from third-party visits/signups — meaning a derived signal/trading system that does not simply redistribute the raw data is not barred by the redistribution clause." — vote 1-2 · https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO002.cmd

---

## Sources (20)

- https://github.com/sharebook-kr/pykrx/blob/master/pykrx/website/krx/market/core.py — primary · Index membership PIT (primary) · 5 claims
- https://github.com/sharebook-kr/pykrx/blob/master/pykrx/stock/stock_api.py — primary · Index membership PIT (primary) · 4 claims
- https://data.krx.co.kr/contents/MDC/COMS/board/MDCCOMS010_S1.cmd?boardId=MDCINFO005 — primary · Index membership PIT (primary) · 5 claims
- https://www.kfenews.co.kr/news/articleView.html?idxno=649362 — secondary · Index membership PIT (primary) · 4 claims
- https://namu.wiki/w/KOSPI200 — unreliable · Index membership PIT (primary) · 4 claims
- https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201010106 — primary · Index membership PIT (primary) · 3 claims
- https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO005.jsp — primary · KRX free-float & data licensing · 5 claims
- https://openapi.krx.co.kr/ — unreliable · KRX free-float & data licensing · 0 claims
- https://www.data.go.kr/data/15094775/openapi.do — primary · KRX free-float & data licensing · 5 claims
- https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020203 — unreliable · KRX free-float & data licensing · 0 claims
- https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO002.cmd — primary · KRX free-float & data licensing · 5 claims
- https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-krx-exchanges.pdf — primary · KRX free-float & data licensing · 4 claims
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001 — primary · DART earnings dates & sector history (false-negative hunt) · 5 claims
- https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=20251029000126&docno=&viewerhost= — primary · DART earnings dates & sector history (false-negative hunt) · 5 claims
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002 — primary · DART earnings dates & sector history (false-negative hunt) · 5 claims
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020 — primary · OpenDART fundamentals integrity (technical) · 5 claims
- https://github.com/FinanceData/OpenDartReader/blob/master/dart_finstate.py — primary · OpenDART fundamentals integrity (technical) · 5 claims
- https://www.sciencedirect.com/science/article/abs/pii/S0927538X14000857 — primary · KR delisting returns (academic + official) · 4 claims
- https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain&disclosureType=02&disTypevalue=0311 — primary · KR delisting returns (academic + official) · 5 claims
- https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1701&ccfNo=1&cciNo=2&cnpClsNo=2 — primary · KR delisting returns (academic + official) · 5 claims

---

## Stats

```json
{
  "angles": 5,
  "sourcesFetched": 20,
  "claimsExtracted": 83,
  "claimsVerified": 25,
  "confirmed": 20,
  "killed": 5,
  "afterSynthesis": 9,
  "urlDupes": 1,
  "budgetDropped": 9,
  "agentCalls": 102
}
```