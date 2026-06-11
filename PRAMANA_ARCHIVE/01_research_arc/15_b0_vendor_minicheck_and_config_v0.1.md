# 15 · B0 Vendor Mini-Check + Config Fill v0.1
## Sharadar vs Norgate 확정 → B0 config 채움 → P0-02/P0-03

**Date:** 2026-06-10
**Scope:** Vendor_License_Confirmation_Mini-Check 실행 결과 — 메일 없이 공식 공개문서로 확정.
**Non-scope:** 구현 코드·백테스트·알파·종목·수익예측.

> **메일 0통.** Mini-Check의 필드/스키마/EULA 질문은 전부 공식 공개문서로 답했다(§6 evidence rule = "Official documentation URL = preferred"). 공개 미상세 2건(derived-storage 세부·lapse 거동)은 B0 sandbox엔 무관 → P0-03 기본값(unknown=sandbox fail-closed)으로 처리.

---

## 1. Sharadar가 무엇이고, 왜 결정 대상이었나

- **Sharadar** = 미국 주식 **유료 데이터 공급업체**(Nasdaq Data Link / 옛 Quandl 통해 판매). 상장폐지 종목 포함(survivorship-free) 미국 주가·시가총액·배당·기업행동을 **REST API**로 제공.
- 코드가 아니라 **B0가 벤치마크를 재구성할 때 먹이는 "원재료 데이터"**. B0 = "깨끗한(PIT·survivorship-aware) 데이터로 cap-weight TR 벤치를 재구성할 수 있나" 테스트 → 그 *깨끗한 데이터*를 어디서 살지가 이 결정.
- **구독료:** 정확한 현재가 Unknown(로그인/비공개). 공개정보상 Core US Equities Bundle 개인구독 ≈ 월 수십~백수십 달러대, SEP(가격만)는 더 저렴. → **확인 항목: data.nasdaq.com/databases/SFA/pricing**.

---

## 2. Mini-Check Decision Sheet (공식 공개문서로 채움)

| Question | Sharadar | Norgate | Decision impact |
|---|---|---|---|
| adjusted + unadjusted prices | ✅ SEP `closeadj`/`closeunadj` [S1] | ⚠️ 명시 불확실 [N1] | required |
| active + delisted coverage | ✅ survivorship-free, 1998~ [S2] | ✅ delisted(Platinum/Diamond) [N2] | required |
| corporate actions (splits 등) | ✅ ACTIONS [S3] | ✅ Capital Event [N3] | required |
| dividends/distributions | ✅ SEP `dividends`+ACTIONS [S3] | ✅ Dividend 지표 [N3] | required |
| **historical shares / market cap** | ✅ **DAILY `marketcap` 일별 series** [S4] | ❌ **current-only(NOT historical)** [N4] | **critical** |
| identifier history | ✅ TICKERS `permaticker`(불변)+`isdelisted` [S5] | ⚠️ 불확실 | required |
| universe / PIT membership | ✅ SP500 constituents 1957~ [S6] | ✅ PIT idx(Platinum/Diamond) [N2] | useful |
| research/sandbox license | ✅ 내부연구 허용(구독약관) | ✅ 개인연구 허용(EULA) | critical |
| derived storage | ◐ 내부용 일반 허용·세부 공개X | ❌ 재배포금지·파생공개 불가 | critical |
| redistribution | ❌ 금지(표준) | ❌ 금지(EULA) | risk |
| subscription lapse | ◐ 공개 미상세 | ◐ 공개 미상세 | risk |
| implementation friction | ✅ **REST·크로스플랫폼(WSL OK)** | ❌ **Windows NDU·로컬DB** | decision factor |

**Sharadar Pass/Fail = PASS** (core 필드 + research/sandbox license 충족). **Norgate = cap-weight 부적합**(historical shares/market cap 부재) + Windows 마찰 + 상업금지.

### Evidence (공개문서 링크)
| ID | 내용 | 출처 |
|---|---|---|
| [S1] | SEP에 unadjusted/adjusted 종가(closeadj/closeunadj) | data.nasdaq.com SHARADAR / quantrocket.com/sharadar |
| [S2] | active+delisted, "nearly completely free from survivorship bias", 1998~ | sharadar.com / quantrocket.com/sharadar |
| [S3] | ACTIONS = dividends·splits·corporate actions (20,000+종, 1998~) | data.nasdaq.com/publishers/SHARADAR |
| [S4] | DAILY = ev/evebit/evebitda/**marketcap**/pb/pe/ps 일별 | data.nasdaq.com SHARADAR/DAILY |
| [S5] | TICKERS `permaticker`(불변 고유 식별자)·`isdelisted`(Y/N) | data.nasdaq.com SHARADAR/TICKERS |
| [S6] | S&P 500 constituents history since 1957 | quantrocket.com/sharadar |
| [N1] | 가격 제공(adj/unadj 명시 불확실) | norgatedata.com/data-content-tables.php |
| [N2] | delisted·PIT 지수 구성종목 = Platinum/Diamond tier | norgatedata.com/data-content-tables.php |
| [N3] | Dividend 지표·Capital Event(splits/reverse/bonus/reorg) | norgatedata.com/data-content-tables.php |
| [N4] | **SharesOutstanding/SharesFloat/mktcap = current values only, NOT historical** | norgatedata.com/data-content-tables.php |
| [N5] | EULA 개인용만·상업 전면금지·재배포 금지 | norgatedata.com/subscribe/eula.php |

---

## 3. 선택 (Decision Tree A)

> **선택 = Sharadar + EDGAR.**
> Sharadar가 core 필드 + research/sandbox license 충족(Tree A). Norgate는 **historical cap input 부재**로 cap-weight B0 부적합(Tree C 탈락사유)이고, Windows·상업금지 제약까지 있어 백업으로도 열위.
> CRSP/WRDS = production-grade이나 이중구독·institution-gated → DEFER(변경 없음).

---

## 4. B0 Config Fill (Sharadar + EDGAR 기준)

### 4.1 data_snapshot_config (DS-US-YYYYMMDD-v1)
```yaml
data_snapshot_id: DS-US-YYYYMMDD-v1
status: draft   # 구독 결제 후 extraction_date·hash 확정
market: US
timezone: America/New_York
calendar_version: US-NYSE-v1
raw_sources:
  price_return_universe:
    name: Sharadar (Nasdaq Data Link, Core US Equities Bundle)
    tables: [SEP, DAILY, ACTIONS, TICKERS, SP500]
    role: price / returns / market_cap / corporate_actions / identifiers / index_membership
    field_map:
      price_unadjusted: SEP.closeunadj          # [S1]
      price_adjusted:   SEP.closeadj            # [S1]
      volume:           SEP.volume
      dividends:        SEP.dividends + ACTIONS  # [S3]
      splits/CA:        ACTIONS                  # [S3]
      market_cap:       DAILY.marketcap          # [S4] historical 일별
      delisting_flag:   TICKERS.isdelisted       # [S5]
      permanent_id:     TICKERS.permaticker      # [S5]
      index_membership: SP500 (1957~)            # [S6]
    license_state: research_sandbox_allowed; production=DEFER; redistribution=prohibited
    confirmation_state: public_docs_confirmed_fields; price/lapse=Unknown
  filing_floor:
    name: SEC EDGAR (data.sec.gov)
    role: filing/fundamentals floor (B2+ 용, B0엔 placeholder)
    license_state: public
point_in_time_rule: no_data_before_availability_timestamp
corporate_action_policy: reconcile_splits_dividends_distributions (ACTIONS 기준)
delisting_inactive_policy: retain delisted (TICKERS.isdelisted); terminal/imputation 정책은 B0에선 보존+플래그, 수익보정 수치는 Provisional
identifier_link_snapshot_id: permaticker 기반 (IDMAP-US-YYYYMMDD-v1)
missing_data_policy: documented; fail_on_unexplained_critical_missingness: true
lineage:
  data_hash: TODO   # 추출 시 생성 (필수)
license:
  data_license_state: research_sandbox_allowed   # 세부(derived/lapse)=Unknown→fail_closed_outside_sandbox
  fail_closed_if_unknown: true
```

### 4.2 universe_config (UNI-US-v1)
```yaml
universe_config_id: UNI-US-v1
market: US
calendar_version: US-NYSE-v1
inclusion_rule: common_stock_eligible        # Sharadar TICKERS.category로 필터
exclusion_rule: [ETF, ADR, preferred, units, closed_end_fund, fund, rights, warrants]
share_code_whitelist_version: Sharadar-category-v1 (TICKERS.category 기반)  # Provisional
exchange_rule: NYSE/NASDAQ/NYSE American (TICKERS.exchange)                 # Provisional
primary_listing_rule: TODO   # Do not lock yet
IPO_seasoning_rule: TODO     # Do not lock yet
liquidity_filter: {enabled: false}  # Do not lock yet (B0는 신호 아님)
survivorship_policy: retain_inactive_and_delisted (isdelisted 포함)   # Lock
as_of_date_handling: no_future_membership   # Lock
reconstitution_frequency: monthly_provisional
```

### 4.3 benchmark_config (BMK-US-selfTR-v1)
```yaml
benchmark_config_id: BMK-US-selfTR-v1
benchmark_type: internal_self_built
market: US
calendar_version: US-NYSE-v1
universe_config_id: UNI-US-v1
data_snapshot_id: DS-US-YYYYMMDD-v1
construction:
  weight_basis: full_cap (DAILY.marketcap 사용)   # float-adjusted는 미제공 → full-cap + 플래그. Provisional
  total_return_policy: include_dividends_and_distributions (SEP.dividends/ACTIONS)
  rebalancing_rule: monthly_provisional
  as_of_date_rule: month_end_as_of
  trade_date_rule: next_session_after_signal
  delisting_handling: retain through delisting; terminal return 정책 플래그
drift_policy:
  internal_reconstruction_error: {classification: hard_gate, threshold: TODO_provisional}
  external_comparator_difference: {classification: diagnostic, external_comparator_id: SP500(Sharadar) or 외부, action: explain_not_auto_fail}
outputs:
  benchmark_series_path: outputs/benchmark_series/BMK-US-selfTR-v1.csv
  benchmark_drift_report_link: reports/B0_benchmark_drift_report.md
```

---

## 5. Pre-Implementation Gate 상태

| Gate | 상태 | 근거 |
|---|---|---|
| **P0-02 Data Source Track Chosen** | ✅ **PASS** | Sharadar+EDGAR 확정; 모든 필수 컴포넌트 public-docs confirmed |
| **P0-03 License State Recorded** | ◐ **CONDITIONAL PASS** | research/sandbox=allowed; **production/derived/lapse=Unknown→sandbox fail-closed**(B0 sandbox엔 충분). production 전 메일/약관 확정 필요 |
| 미해결(비차단) | 구독료(Unknown→네가 결제 전 확인) · 구독 후 extraction_date/data_hash 생성 | — |

---

## 6. 내 판단 (네가 부탁한 것)

**"꼭 필요한가 / 지금 결제해야 하나"에 대한 판단:**

1. **데이터 자체는 필요하다** — B0의 정의가 "survivorship-aware·PIT 데이터로 벤치 재구성"이라, 무료 소스(Yahoo/stooq 등)는 survivorship-biased라 B0를 *진짜로* 통과시킬 수 없다. 깨끗한 데이터 중 **가장 싼 게 Sharadar**(CRSP/WRDS는 기관전용·고가). 그래서 "진짜 B0"를 돌릴 땐 Sharadar가 맞다.
2. **단, 지금 당장 결제할 필요는 없다.** 이유: (a) 너는 방금 "Sharadar가 뭐냐"고 물었을 만큼 *셋업/학습 단계*고, 파이프라인이 아직 없다 — 데이터부터 사는 건 순서가 거꾸로. (b) B0의 진짜 목적은 **파이프라인(데이터 게이트→벤치 재구성→재현성)이 작동하는지** 증명이라, 그 기계는 데이터 없이도(또는 무료 샘플로) 만들어두고, **결제는 "진짜 B0 돌릴 준비가 됐을 때"** 하면 된다.
3. **그래서 지금은 안 막힌다.** config·게이트·decision은 다 채워뒀으니(이 문서), Sharadar 구독만 하면 즉시 B0 실행 가능한 상태다. 결제 타이밍은 네 선택.
4. **선택지 정리:**
   - **(권장) 지금: 무료로 셋업 완료(이 문서) → 파이프라인 코드 만들 준비 → "진짜 B0" 직전에 Sharadar 구독(월 수십~백수십\$).** 데이터정직 원칙은 "무료 데이터 숫자를 *신뢰하지 않는다*"로 지킨다.
   - (연습용) 정 결제 전에 손에 익히고 싶으면, 무료 데이터로 **버려도 되는 dry-run**(machinery만)해보되 — *벤치마크 숫자는 절대 신뢰 금지*, survivorship-biased라 명시.
   - (대안) 대학/기관 CRSP/WRDS 접근이 있으면 그게 gold standard(무료일 수 있음) — 접근경로 있는지만 확인.

> **한 줄:** Sharadar는 "꼭 필요한 깨끗한 데이터의 가장 싼 선택"이 맞지만, **지금 결제는 불필요** — 파이프라인부터 만들고, 진짜 B0 돌리기 직전에 사면 된다. 지금 셋업은 이 문서로 끝.

---

## 7. Next

```text
[완료] vendor 확정(Sharadar+EDGAR)·Mini-Check·B0 config·P0-02 PASS·P0-03 conditional (이 문서)
   │
   ▼ (결제 타이밍은 너의 선택)
[옵션 A] Sharadar 구독 → extraction_date/data_hash 생성 → B0 실행
[옵션 B] 무료 dry-run으로 파이프라인 코드 먼저 검증(숫자 불신) → 이후 Sharadar로 진짜 B0
   │
   ▼
B0 구현: data gate G-01/04/05/06/07/08/09/11/12/14 + self-built cap-weight TR 재구성
```

> 미해결 = Sharadar 구독료(확인) · 구독 후 snapshot hash · production용 license 세부(production 갈 때). B0 sandbox 진행엔 비차단.
