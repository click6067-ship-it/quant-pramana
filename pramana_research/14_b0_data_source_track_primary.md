# 14 · B0 Data Source Track Decision v0.1 (PRIMARY)
## Phase 1A B0 (data-only benchmark sanity) — US 데이터 소스 트랙 선택

**Date:** 2026-06-10
**Project:** Pramana systematic equity research / validation / trading operating system
**Role:** Primary Data Source Track Decision Researcher. **B0(data-only benchmark sanity) 데이터 트랙 선택**에만 한정. 코드·백테스트·알파·종목추천·수익예측·Phase 1B/1C 제외.
**Constraints (input only):** Phase_1_Final_Experiment_Design_v0.1 · Pre_Implementation_Gate_and_B0_Prep_v0.1 (특히 **P0-02 Data Source Track Chosen** = blocking) · B0_Implementation_Scaffold_v0.1 (config placeholder) · Integrated_Lock_Sheet_DR1_to_DR2B_v0.1.
**Method:** full-power deep-research(104 agents·25주장 3표검증·**22 confirmed/3 killed**, runId `wf_a6bcc852-a31`)로 공식 벤더문서에 대고 검증. *주: synthesize 단계가 막판 소켓끊김으로 실패 → salvage로 22개 raw confirmed claim 반환, 종합은 본 문서에서 수행.* DR-2B 락을 컨텍스트로 상속.

> 표기: **Lock now** / **Provisional** / **Do not lock yet** / **Requires confirmation**(vendor/legal). 공식 미공개 = **Unknown / Requires legal confirmation**(추측 금지). 인용 `[n]` = 아래 §2 Source Register의 claim 번호.

---

## 1. Executive Decision Summary

- **B0 진행 판정 = `PATCH-BEFORE-B0`.** 트랙 *방향*은 잠글 수 있으나, B0 시작 전 추천 트랙의 Requires-confirmation 항목(아래)이 해소돼야 한다.
- **추천 prototype 트랙 = Sharadar (via Nasdaq Data Link) + EDGAR.** survivorship-aware(active+delisted) [4]·REST API 크로스플랫폼(WSL/Linux 친화)·저가. — **Prototype track.**
- **백업 prototype 트랙 = Norgate Data + EDGAR.** survivorship-free(delisted 보존, 25,222종 1950~) [1] + **PIT 지수 구성종목 history**(S&P500 1957·Russell 1990) [2]·CA 완비 [3]. 단 **Windows 데스크탑앱 의존**·**시총/주식수 필드 불확실**·**EULA 상업금지** [21][22]. — **Backup prototype track (제약 있음).**
- **Production/research-grade 트랙 = CRSP + Compustat/CCM via WRDS.** PERMNO 영구·never-reassigned [18]·delisting 코드·메타데이터 [17][19]·cap-weight TR 필드 완비 [9][20]·S&P500 universe 지수 [12]·wrds 클라이언트 크로스플랫폼 [8]. 단 **CRSP+Compustat 이중구독·institution-gated** [6][7]. — **Production track, DEFER**(솔로 접근성 미확정).
- **Reject for B0 = EDGAR-only + 무료 가격소스.** EDGAR는 filing/fundamentals **floor**지 survivorship-aware price/return/benchmark 패널이 아님(DR-2B 락); 무료 가격소스는 survivorship-biased → 깨끗한 benchmark 재구성 불가. EDGAR는 B2+ fundamentals floor로만 유지.
- **Lock now:** B0 트랙 *방향*(prototype=Sharadar 우선/Norgate 백업, production=CRSP DEFER, EDGAR=floor only, EDGAR-only=reject) · CRSP delisting 코드/-55% imputation 정책 [13–17] · 식별자 안정성 기준 = PERMNO류 영구식별자 [18].
- **Provisional:** Sharadar vs Norgate 최종 택1 · 외부 comparator(S&P500/CRSP index) · 벤치 weight_basis(full-cap vs float).
- **Do not lock yet:** 최종 universe 모집단(CRSP-style broad vs Russell-1000-like) · liquidity filter 값.
- **Requires confirmation:** ① **Sharadar의 정확한 dataset/field roster**(특히 shares outstanding / market cap = cap-weight 벤치 입력)와 **license**(research/paper/derived storage) — 본 연구서 roster claim이 refuted됨 → 공식 Nasdaq Data Link/Sharadar 문서로 재확인. ② **Norgate의 시총/주식수 필드 존재 여부**(claim refuted, 1-2) ③ Norgate **commercial-use 금지**가 향후 production을 막음 [21] — prototype엔 OK, production엔 부적합 명시.
- **이건 데이터 트랙 *선택*이지 구현이 아니다.** B0 구현은 P0-02 PASS + license 확정 후.

---

## 2. Source Register (검증된 22 claim의 출처)

| # | Source | Type | What it supports | Vendor | Reliability | Notes |
|---|---|---|---|---|---|---|
| [1] | norgatedata.com/data-content-tables.php | 공식벤더 | Norgate delisted 보존(survivorship-free), Platinum/Diamond tier, 25,222종 1950~Sep2022 | Norgate | High | tier-gated |
| [2] | 〃 | 공식벤더 | PIT 지수 구성종목: S&P500 1957·Russell 1990·Nasdaq100 1993·DJIA 1950 (Platinum/Diamond) | Norgate | High | tier-gated |
| [3] | 〃 | 공식벤더 | CA: split·reverse·bonus·stock div·복합 reorg, Capital Event 지표 | Norgate | High | ex-date 전일 종가 기준 |
| [4] | sharadar.com | 공식벤더 | active+delisted, "nearly completely free from survivorship bias" | Sharadar | High | 마케팅 문구지만 공식 |
| [5][11] | wrds .../using-crspcompustat-merged-database; CRSP-Data-on-WRDS.pdf | 공식 | CCM이 PERMNO/PERMCO↔GVKEY many-to-many over time 연결(CRSP Link) | CRSP/WRDS | High | |
| [6] | 〃 | 공식 | CCM = CRSP+Compustat **이중 구독 필요**(institution-gated) | CRSP/WRDS | High | |
| [7][8] | pypi.org/project/wrds | 공식 | wrds 클라이언트는 WRDS 계정 필요·**Linux/macOS/Windows·Py3.8+**(크로스플랫폼) | WRDS | High | Norgate Windows앱과 대비 |
| [9] | crsp.org cap-based-portfolio-index-overview.pdf | 공식 | CRSP cap-based = value-weighted, 가중=shares×전월종가 → cap-weight 입력 보유 | CRSP | High | |
| [10] | wrds CRSP-Data-on-WRDS.pdf | 공식 | NYSE/AMEX/NASDAQ price/return/volume + PERMNO/PERMCO | CRSP | High | |
| [12] | 〃 | 공식 | CRSP 역사 지수 DB(Stock File Indices·Cap-Based·S&P500 Universe) | CRSP | High | 외부 comparator 후보 |
| [13][16] | Wiley 0022-1082.00192 (Shumway-Warther 1999) | 학술 | CRSP Nasdaq delisting 수익 누락·large negative | academic | High | |
| [14][15] | SSRN 11150 (Shumway 1997) | 학술 | 성과사유 Nasdaq delisting imputation = **-55%** | academic | High | |
| [17] | crsp.org US Stock & Indexes Data Descriptions Guide | 공식 | delisting return **missing 코드**(-55.0/-66.0/-88.0/-99.0) | CRSP | High | missing-by-design 공식 확인 |
| [18] | 〃 | 공식 | **PERMNO 영구·never reassigned** → 식별자 안정·survivorship 추적 | CRSP | High | 식별자 gold standard |
| [19] | 〃 | 공식 | delisted 보존: Delisting Date never missing·사유 코드·worthless=-1 | CRSP | High | |
| [20] | 〃 | 공식 | Cap(종가×shares)·Holding Period TR(배당재투자)·Index TR → 벤치 재구성 메커니즘 | CRSP | High | |
| [21] | norgatedata.com/subscribe/eula.php | 공식 EULA | **개인용만 허용·모든 상업적 사용 금지**(3중 bar, 경쟁적 사용 포함) | Norgate | High | production blocker |
| [22] | 〃 | 공식 EULA | **재배포 금지**(express-permission 제한 발췌만) → 파생 데이터 공개 불가 | Norgate | High | derived-storage 제약 |

**Refuted (적대검증 탈락 — 정직 표기):**
- Norgate가 SharesOutstanding/SharesFloat/mktcap 필드를 노출한다 (vote **1-2**) → **cap-weight 벤치 입력 필드 미확인 = Requires confirmation.**
- Sharadar dataset roster(SF1/SFB/SF3/SF2…) 명세 (vote **0-3**) → **정확한 dataset/field 이름 미확정 = Requires confirmation.**
- "CRSP Cap-Based Portfolio 방법론이 delisted 종목 final delisting return을 명시 연구" (vote **0-3**) → delisting-return 처리 근거는 cap-based overview가 아니라 Stock DB guide [17][19]에 있음(결론 불변).

---

## 3. Candidate Track Matrix (B0)

| Track | B0 적합성 | Price/return | Active/inactive | Delisted | CA | Div/dist | 식별자 history | Universe/PIT | 벤치 재구성 | Fund/filing floor | API/export | License risk | Cost/access risk | Solo feasibility | Final treatment |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CRSP+Compustat/WRDS** | 최상(과잉) | ✅[10] | ✅[19] | ✅[17][19] | ✅ | ✅[20] | ✅PERMNO[18] | ✅S&P500 idx[12] | ✅full[9][20] | ✅(Compustat) | wrds API 크로스플랫폼[7][8] | 학술/상업 구분·이중구독[6] | **institution-gated, 비쌈** | ❌솔로 접근난 | **Production / DEFER** |
| **Sharadar+EDGAR** | ✅양호 | ✅ | ✅[4] | ✅[4] | Req conf(roster refuted) | Req conf | Req conf | Req conf(S&P/Russell) | ⚠️shares/cap 필드 Req conf | EDGAR floor | ✅REST 크로스플랫폼 | Req legal conf | 저가(추정) | ✅높음 | **Primary prototype** |
| **Norgate+EDGAR** | ✅조건부 | ✅ | ✅[1] | ✅[1] 25,222종 | ✅[3] | ✅[3] | Req conf | ✅PIT idx[2] | ⚠️시총/주식수 **refuted** | EDGAR floor | ❌**Windows 데스크탑앱**·로컬DB | ❌**상업금지·재배포금지**[21][22] | 저가(소비자) | ⚠️WSL 마찰·prototype-ceiling | **Backup prototype(제약)** |
| **EDGAR-only+무료가격** | ❌부적합 | 무료(survivorship-biased) | ❌ | ❌ | ❌ | 부분 | ❌ | ❌ | ❌깨끗한 재구성 불가 | ✅EDGAR | ✅무료 | 무료 | 무료 | — | **Reject for B0**(EDGAR는 floor로만) |
| **기타(EODHD/Polygon/Intrinio/Tiingo)** | 미확정 | 일부 | 일부 | 벤더별 | 벤더별 | 벤더별 | 벤더별 | 대개 ❌PIT | 벤더별 | — | REST | Req conf | 저가 | — | **Provisional alt(Sharadar보다 우월 근거 없음)** |

> CRSP가 모든 B0 요구를 충족하나 솔로엔 과잉·접근난 → DR-2B 락(free/cheap prototype 먼저)대로 **prototype은 Sharadar/Norgate, CRSP는 production DEFER**.

---

## 4. B0 Data Requirement Fit

| B0 요구 | Best source | Alternative | Gap | Lock status | Required confirmation |
|---|---|---|---|---|---|
| price history | Sharadar | Norgate / CRSP | — | Provisional(택1) | Sharadar field |
| adjusted price | Sharadar/Norgate(조정/CA) | CRSP | both adj+unadj 동시 제공 확인 | Provisional | adj+unadj 둘 다 |
| unadjusted price | Norgate(unadjusted 제공) / CRSP | Sharadar | — | Provisional | Sharadar unadj |
| volume | Sharadar/Norgate/CRSP[10] | — | — | Lock(존재) | — |
| shares out / market cap | **CRSP[9][20]** | Sharadar(Req conf) | **Norgate refuted·Sharadar 미확정** | **Requires confirmation** | prototype 벤더의 shares/cap 필드 |
| dividends | Sharadar/Norgate[3]/CRSP[20] | — | — | Provisional | — |
| distributions(special) | CRSP[20]/Norgate[3] | Sharadar | special 분배 완전성 | Provisional | — |
| splits | Norgate[3]/CRSP/Sharadar | — | — | Lock(존재) | — |
| corporate actions | Norgate[3]/CRSP | Sharadar | 복합 reorg 완전성 | Provisional | — |
| inactive/delisted names | Sharadar[4]/Norgate[1]/CRSP[19] | — | — | **Lock(요구)** | 벤더 보존 확인 |
| delisting/terminal return | **CRSP(코드+impute)[17][19]** | imputation 정책(-55%/-30%)[14] | Sharadar/Norgate terminal 처리 | Provisional(정책 Lock·소스 conf) | prototype 벤더 terminal 처리 |
| identifier history | **CRSP PERMNO[18]** | Sharadar/Norgate vendor id | ticker-reuse 처리 | Provisional | prototype 벤더 link history |
| universe membership(PIT) | **Norgate PIT idx[2]** | CRSP S&P500 idx[12] | Sharadar PIT 미확정 | Provisional | — |
| benchmark constituent history | Norgate[2]/CRSP[12] | — | 외부 comparator 선택 | Do not lock yet | — |
| trading calendar | NYSE 공식(US-NYSE-v1) | 벤더 calendar | — | Lock(rule) | calendar 소스 |
| data hash/versioning | 자체 생성(snapshot hash) | — | — | **Lock(필수)** | — |
| license state | 벤더 EULA | — | Sharadar 미확정·Norgate 상업금지[21] | **Requires legal confirmation** | Sharadar license |

---

## 5. License / Legal Risk Audit

| Source | research | paper | production | commercial | redistribution | derived storage | export limit | lapse 영향 | unknown | B0 전 필요조치 |
|---|---|---|---|---|---|---|---|---|---|---|
| **CRSP/WRDS** | ✅(학술 WRDS) | 기관계약 의존 | 상업 별도라이선스 | 별도 | 금지(기관) | 기관 정책 | 기관 정책 | 구독종료=접근차단 | 솔로 접근경로 | **솔로용 접근/license 확인(Requires confirmation)** |
| **Sharadar** | 추정 허용 | 추정 허용 | **Unknown** | **Unknown** | **Unknown** | **Unknown** | Unknown | Unknown | **license 전반** | **공식 Sharadar/Nasdaq Data Link 약관 확인(Requires legal confirmation)** |
| **Norgate** | ✅개인 investment/trading[21] | ✅(개인) | ❌**금지**[21] | ❌**전면금지**[21] | ❌**금지**[22] | ❌(파생 공개 불가)[22] | 제한발췌만[22] | Unknown(다운로드분 유지여부) | lapse 영향 | **prototype OK·production 부적합 명시; lapse 영향 확인** |
| **EDGAR** | ✅공개 | ✅ | ✅ | ✅ | ✅(공개) | ✅ | 없음 | 없음 | — | floor로만 사용 |
| **무료 가격소스** | 소스별 | 소스별 | 대개 제한 | 제한 | 제한 | 제한 | 소스별 | — | 약관 | B0 미사용 |

> **핵심 법적 결론:** Norgate는 **개인 research/paper에만** 합법, **상업 production·재배포·파생데이터 공개 전면 금지** [21][22] → prototype-only ceiling. Sharadar license는 **공식 미확인 = Requires legal confirmation**(추측 금지). license unknown은 Pre-Impl Gate P0-03대로 **sandbox 밖 fail-closed**.

---

## 6. Implementation Friction Audit

| Source | API 가용 | 로컬 DB 요구 | OS 의존 | Python 호환 | export 한계 | 업데이트 | 통합 난이도 | 재현성 | 버저닝 |
|---|---|---|---|---|---|---|---|---|---|
| **CRSP/WRDS** | wrds API[7] | 아니오(WRDS 클라우드) | **없음(Linux/mac/Win)**[8] | wrds Py3.8+[8] | 기관 정책 | WRDS 갱신 | 중(계정·쿼리) | 높음(PERMNO·릴리스) | CRSP 릴리스 |
| **Sharadar** | **REST(Nasdaq Data Link)** | 아니오 | **없음(크로스플랫폼)** | nasdaqdatalink/pandas | API rate(Req conf) | API pull | **낮음(REST)** | 높음(스냅샷 hash 자체) | 벤더 버전 Req conf |
| **Norgate** | norgatedata Py 패키지 | **예(로컬 DB)** | ❌**Windows 데스크탑 Data Updater**(WSL/Linux 비공식) | norgatedata(Windows updater 가동 전제) | 로컬 | NDU 데몬 | **높음(WSL 환경 마찰)** | 중(로컬 스냅샷) | NDU 버전 |
| **EDGAR** | data.sec.gov REST | 아니오 | 없음 | requests | rate-limit | pull | 낮음 | 높음 | accession |

> **WSL2/Linux 환경 결정타:** Norgate Data Updater는 **Windows 데스크탑 앱 + 로컬 DB** → 이 프로젝트(WSL2/Linux)에선 Windows측 가동·경로 연동 마찰. **Sharadar/CRSP-wrds는 REST/크로스플랫폼**으로 헤드리스·Linux 친화 [8]. → prototype에서 Sharadar가 운영 마찰 최소.

---

## 7. B0 Failure Mode Audit by Source

| Failure mode | CRSP/WRDS | Sharadar | Norgate | EDGAR-only+무료 |
|---|---|---|---|---|
| survivorship bias | 낮음(보존[19]) | 낮음([4]) | 낮음(보존[1], Platinum+) | **높음**(무료가격) |
| missing delisted | 낮음(단 return은 missing-code[17]→impute[14]) | Req conf | tier-gated(Gold면 누락[1]) | **높음** |
| incomplete CA | 낮음 | Req conf | 낮음[3] | **높음** |
| div/dist mismatch | 낮음[20] | Req conf | 낮음[3] | 높음 |
| identifier gaps | 낮음(PERMNO[18]) | Req conf | Req conf | 높음 |
| index membership gaps | 낮음[12] | Req conf(PIT 미확정) | 낮음(PIT[2]) | 높음 |
| restatement/as-filed 혼동 | Compustat 처리 | EDGAR as-filed | NA(가격중심) | EDGAR floor |
| **license 위반** | 기관 약관 | **Unknown→fail-closed** | **상업·재배포시 위반**[21][22] | 낮음 |
| data version drift | 낮음(릴리스) | 벤더 버전 Req conf | NDU 버전 | 소스별 |
| vendor lock-in | 높음(비쌈) | 중(REST 이식 용이) | 중(상업금지로 prototype-only) | 낮음 |
| export/API fragility | 낮음 | rate-limit Req conf | 로컬DB 의존 | rate-limit |
| **cap-weight 입력 부재** | 없음(shares/cap[9][20]) | **Req conf** | **refuted(필드 미확인)** | 높음 |

---

## 8. Recommended B0 Source Track (≤5 bullets)

- **Primary prototype = Sharadar (via Nasdaq Data Link) + EDGAR floor.** survivorship-aware[4]·REST 크로스플랫폼(WSL 친화·운영마찰 최소)·저가. B0에 충분조건에 가장 근접.
- **Backup prototype = Norgate + EDGAR.** survivorship+PIT 멤버십이 강점[1][2][3]이나 **Windows 데스크탑 의존**·**상업/재배포 금지**[21][22]·**시총/주식수 필드 refuted** → cap-weight 벤치 입력이 미확인이고 production 불가.
- **Production/research-grade = CRSP+Compustat/WRDS, DEFER.** 모든 면에서 gold standard[9][12][17][18][19][20]이나 이중구독·institution-gated[6] → 솔로 prototype엔 과잉, production 단계에서 재검토.
- **Reject for B0 = EDGAR-only + 무료가격.** EDGAR는 fundamentals floor지 survivorship price/benchmark 패널 아님; 무료가격=survivorship-biased.
- **단, primary 확정 전 2건 확인 필수:** (1) Sharadar의 **shares outstanding/market cap 필드**(cap-weight 벤치 입력) 존재·**license**(research/paper/derived) — 공식 약관·dataset 문서로; (2) 미확인 시 **차선책 = Norgate(prototype-only, 상업금지 수용) 또는 CRSP 학술접근 가능 여부**.

---

## 9. Config Fill Plan (chosen track 기준 — B0 placeholder 채움)

> 가정 트랙 = **Sharadar+EDGAR(primary), Norgate 백업**. 미확인 값은 Unknown/Requires confirmation 유지(추측 금지).

### A. Data Snapshot Config
| Field | 채움 값 | 근거/상태 |
|---|---|---|
| raw_source | `EDGAR(floor) + Sharadar(price/universe/CA)`; 백업 `Norgate` | [4]; Req conf(field/license) |
| vendor_source_version | **Requires confirmation**(Sharadar dataset 버전) | roster refuted |
| source_release_timestamp | Unknown until 추출 | — |
| calendar_version | `US-NYSE-v1` | Lock(rule) |
| point_in_time_rule | feature ≥ availability ts; 미확보시 next session | Lock(rule) |
| corporate_action_policy | split/div/distribution reconcile; Sharadar CA(Req conf) 또는 Norgate Capital Event[3] | Lock(rule)·소스 conf |
| delisting_inactive_policy | inactive/delisted 보존 + **terminal/imputation 정책**(CRSP 코드[17]·성과사유 -55%/-30%[14] 참조) | Lock(rule); 수치 Provisional |
| identifier_link_snapshot_id | 벤더 식별자 link snapshot; 기준=영구식별자(PERMNO류[18]) | Provisional(prototype 벤더 conf) |
| data_license_state | Sharadar=**unknown→Requires legal confirmation**; Norgate=personal-only·상업금지[21] | **Requires confirmation**(unknown=sandbox fail-closed) |
| data_hash | snapshot 콘텐츠 hash | **Lock(필수)** |

### B. Universe Config
| Field | 채움 값 | 근거/상태 |
|---|---|---|
| inclusion_rule | common stock eligible | Lock(rule) |
| share_code_whitelist_version | 벤더 security-type 코드 기반 whitelist | Provisional(벤더 코드 conf) |
| exclusion_rule | ETF/ADR/preferred/units/CEF/rights/warrants 제외 | Lock(rule) |
| exchange_rule | NYSE/AMEX/NASDAQ(+modern Arca/BZX 검토) | Provisional |
| primary_listing_rule | primary listing only(중복상장 처리) | Provisional |
| IPO_seasoning_rule | seasoning 기간 | Do not lock yet |
| liquidity_filter | min ADV/price | Do not lock yet |
| survivorship_policy | retain inactive+delisted | **Lock(rule)** |

### C. Benchmark Config
| Field | 채움 값 | 근거/상태 |
|---|---|---|
| weight_basis | `full_cap`(float 미확보시) — shares×price[9][20] | **Provisional**(prototype 벤더 shares/cap 필드 Req conf) |
| total_return_policy | 배당/분배 포함 TR | Lock(rule) |
| rebalancing_rule | monthly as-of, calendar 정합 | Provisional |
| internal benchmark source | 선택 prototype 벤더의 price+shares+dist | Provisional |
| external comparator | CRSP S&P500 universe index[12] 또는 외부 지수 (reporting only) | Do not lock yet |
| drift report expectations | internal reconstruction error=hard gate; external diff=diagnostic | Lock(rule) |

> **cap-weight 벤치의 핵심 입력 = shares outstanding/market cap.** CRSP는 보유[9][20]; **Sharadar/Norgate는 미확정/refuted** → B0 전 **반드시 확인**. 미확보 시 cap-weight 벤치 불가 → equal-weight 벤치로 후퇴하거나 CRSP 학술접근 필요.

---

## 10. Final Decision Table

| Item | Status |
|---|---|
| prototype source track | **Provisional** — Sharadar(primary)/Norgate(backup), shares-cap·license 확인 후 Lock |
| production source track | **Do not lock yet** — CRSP+Compustat/WRDS DEFER |
| EDGAR role | **Lock now** — filing/fundamentals floor only (B2+) |
| CRSP/WRDS role | **Do not lock yet / Requires confirmation** — production-grade, 솔로 접근 미확정[6] |
| Norgate role | **Provisional (prototype-only)** — survivorship+PIT 강점[1][2], 상업금지[21]·Windows·시총필드 conf |
| Sharadar role | **Provisional (primary prototype)** — survivorship[4]·REST, dataset/field/license Req conf |
| free price source role | **Reject for B0** |
| B0 universe source | **Provisional** — prototype 벤더 |
| B0 benchmark source | **Provisional** — self-built cap-weight TR(=벤더 shares/cap 필요) |
| corporate action source | **Provisional** — Sharadar(conf)/Norgate[3] |
| delisting/inactive source | **Lock(요구)/Provisional(소스)** — 보존 필수·imputation 정책[14][17] |
| license state | **Requires legal confirmation** — Sharadar unknown·Norgate 상업금지[21] |
| implementation environment | **Lock now** — WSL2/Linux; REST 벤더 선호([8]); Norgate=Windows 마찰 |
| data export method | **Provisional** — REST(Sharadar/wrds) 우선 |
| **B0 GO / NO-GO** | **PATCH-BEFORE-B0** — shares/cap 필드 + license 확인 후 GO |

---

## 11. Recommendation (≤5 bullets)

- **선택: `Patch before B0`.** 트랙 방향(Sharadar primary·Norgate backup·CRSP defer·EDGAR floor·무료 reject)은 잠그되, B0 시작 전 2건 패치.
- **Patch-1:** Sharadar의 **shares outstanding/market cap 필드**(cap-weight 벤치 입력)와 **dataset roster**를 공식 Nasdaq Data Link/Sharadar 문서로 확인(본 연구서 roster refuted).
- **Patch-2:** Sharadar **license**(research/paper/derived storage/redistribution) 공식 확인 — unknown이면 Pre-Impl P0-03대로 **sandbox fail-closed**. Norgate 채택 시 **상업 production 불가**[21] 명시.
- **차선:** shares/cap·license가 막히면 → Norgate(prototype-only, 상업금지 수용) 백업, 또는 CRSP 학술/저가 접근 가능성 타진.
- **그 후:** P0-02/P0-03 PASS → B0 config 확정 → B0 구현(코드는 그 다음).

---

## 12. Next Handoff

```text
[현재] B0 Data Source Track Decision v0.1 (PRIMARY, 이 문서)
   │
   ▼
[다음] (1) Sharadar shares/cap 필드 + dataset roster 공식 확인
       (2) Sharadar/Norgate license state 확정 (unknown=sandbox fail-closed)
   │
   ▼
B0 config 채움: data_snapshot_config · universe_config · benchmark_config (§9)
   │
   ▼
Pre-Implementation Gate P0-02(Data Source) · P0-03(License) PASS
   │
   ▼
(그 다음에야) B0 구현 — data gate G-01/04/05/06/07/08/09/11/12/14 + self-built cap-weight TR 재구성
```

**구현·코드·백테스트는 이 문서 범위가 아니며, 데이터 소스 트랙 + license 확정(P0-02/P0-03) 전에는 시작하지 않는다.**

---

> **불확실성 표기:** Sharadar dataset/field roster·license = **Requires legal confirmation**(roster claim refuted); Norgate 시총/주식수 필드 = **refuted/미확인**; CRSP 솔로 접근경로 = Unknown; 외부 comparator·universe 모집단·weight_basis = Do not lock yet. 추측하지 않고 규칙·방향만 잠갔다.
> **근거:** 22개 claim 전부 3표 적대검증 confirmed(공식 벤더문서·Shumway), deep-research runId `wf_a6bcc852-a31`. (synthesize는 소켓끊김 실패 → 본 문서가 종합 수행.)
