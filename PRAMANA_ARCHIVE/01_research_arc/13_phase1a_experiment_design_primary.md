# 13 · Phase 1A Experiment Design v0.1 (PRIMARY)
## 소규모 팀 systematic equity 시스템 — Phase 1A "boring baseline" 실험 설계 (Primary)

**Date:** 2026-06-10
**Project:** Pramana systematic equity research / validation / trading operating system
**Role of this doc:** Primary Phase 1 Experiment Design — *Phase 1A boring baseline only*. 실험 *설계*이지 구현·백테스트·모델선택·종목추천·수익예측이 아니다.
**Method:** Claude가 PRIMARY 설계자. 방법론 근거는 full-power deep-research(104 agents·25주장 3표검증·**25 confirmed/0 killed·6 findings 전부 high**, runId `wf_9939c3da-44b`)로 Tier-1 원전에 대고 검증했고, DR-3 Final Validation Protocol·DR-4 Final Model Candidate Map·Integrated Lock Sheet(DR1–DR2B)의 락 결정을 그대로 상속한다.
**Next handoff:** Claude Phase 1 Experiment Design **Red-team Audit** → Phase 1 Final Experiment Design → 그 *다음에야* 구현/프로토타입/백테스트.

> 표기 규약: **Lock now** / **Provisional** / **Do not lock yet** / **Requires confirmation**(data/vendor/broker/legal). 수치 임계값 중 출처 기반 hard rule이 아닌 것은 전부 **house rule (Provisional)**로 명시. 모르는 값은 추정하지 않고 **Unknown**으로 둔다.

---

## 1. Executive Decision Summary

- **Phase 1A Experiment Design 판정 = `PATCH-BEFORE-IMPLEMENTATION`.** 설계 *프레임*은 지금 잠글 수 있으나, 구현 전 (a) Claude red-team, (b) 데이터 스냅샷 소스/벤더 확정, (c) house-rule 임계값 calibration이 선행돼야 한다.
- 이 문서는 **실험 설계**다. 코드·백테스트·수익·모델채택은 일절 포함하지 않는다. (DR-4 handoff 준수)
- **Lock now (구조):** experiment registry schema, 9개 config schema의 *필드 구조*, 데이터 수용 게이트 *테스트 목록*, chronological-only OOS 원칙, B0–B11 실험 매트릭스 *골격*, promotion/quarantine/reject lifecycle, report·failure-log 템플릿. (방법론 근거: [AHM2019][LdP2018][DGU2009] — §2)
- **Provisional (house rule, 값 보정 필요):** 모든 수치 임계값 — 벤치 drift 허용치, holdout 길이, IR/Rank-IC 컷, 70%/65% 일관성, 2x/3x cost stress, ADV 5%/10%, trial budget 상한. (DR-3가 "calibrated house rule"로 잠근 그대로)
- **Do not lock yet:** 최종 universe 모집단·외부 reporting 벤치마크 후보·factor sleeve의 *정확한* 정의(winsorize 컷 등)·turnover 컷 수치 — 데이터 프로토타입 후 보정.
- **Requires confirmation:** 데이터 스냅샷 raw source/vendor(EDGAR floor + Norgate/Sharadar/CRSP 중 택)·data license(research/paper/production)·broker 비용/체결 파라미터. (Integrated Lock Sheet §5 미해결 항목 상속)
- **시장:** US-core가 Phase 1A pilot. KR은 동일 프레임 재사용하되 **별도 cost/data adapter로 재검증**(KR alpha는 DR-2A 프로토타입 테스트 통과까지 NO-GO).
- **핵심 원칙(상속·LOCK):** signal≠order · alpha≠position · 데이터 게이트가 모델 게이트보다 먼저 · 검증 게이트가 승격보다 먼저 · LLM off-path. (Integrated Lock Sheet §1)
- **Phase 1A의 목적은 수익 최대화가 아니다.** 데이터 정합·벤치 sanity·비용 현실성·baseline 재현성·OOS/walk-forward 기계·registry·failure log·promotion 규칙이 *작동하는지*를 증명하는 것이다.
- **결론 한 줄:** "지루한 자(yardstick)를 먼저, 재현 가능하게, 누수·과최적화·비용기만·trial 난립 없이 세운다."

---

## 2. Source Register

> 방법론 근거는 deep-research(runId `wf_9939c3da-44b`)에서 3표 적대검증으로 confirmed된 6 findings의 1차 인용. 내부 정본(DR-3/DR-4/Lock Sheet)은 프로젝트 lock 문서.

| Source | Type | What it supports | Section | Market | Reliability | Notes |
|---|---|---|---|---|---|---|
| Arnott, Harvey & Markowitz (2019), "A Backtesting Protocol in the Era of ML", *J. Financial Data Science* 1(1) [AHM2019] | 학술/1차 | 표본 사전고정·재튜닝=과적합·only-live-is-OOS·비용 in+OOS·trial 추적·t=2.0 무의미 | §4,7,8,10,12 | general | High | duke.edu/SSRN 3275654 |
| López de Prado (2018), *Advances in Financial ML*, Wiley [LdP2018] | 서적/1차 | k-fold 실패·walk-forward 기준·purging/embargo/CPCV는 label overlap 조건부·DSR | §6,8,12 | general | High | Ch.4/7/12; ETH ToC 검증 |
| DeMiguel, Garlappi & Uppal (2009), "Optimal vs Naive Diversification", *RFS* 22(5) [DGU2009] | 학술/1차 | **1/N이 OOS에서 hard-to-beat** (14모델×7데이터 중 일관초과 0); 추정오차가 분산이득 상쇄 | §3,9 | general | High | RFS DOI 10.1093/rfs/hhm075 |
| Novy-Marx & Velikov (2016), "A Taxonomy of Anomalies and Their Trading Costs", *RFS* 29(1) [NMV2016] | 학술/1차 | 비용이 anomaly 유의성 잠식; net 생존은 turnover 조건부 | §10,11 | US | High | NBER w20721 |
| Patton & Weller (2020), "What you see is not what you get", *JFE* 137(2) [PW2020] | 학술/1차 | paper↔live 실현수익 괴리 | §10,11 | US | High | implementation shortfall |
| Grinold (1994) "Alpha=Vol×IC×Score"; Clarke-de Silva-Thorley (2002) Fundamental Law; CFA Institute Technical Appendix [Grinold/CFA] | 학술/1차 | score→weight 매핑·**Rank IC를 cross-sectional 진단으로** (IR=TC·IC·√BR) | §6(D/E),10 | general | High | CFA 기술부록 eq. A4/A12 |
| Shumway (1997) "The Delisting Bias in CRSP Data" [Shumway1997] | 학술/1차 | 상장폐지 수익 누락→상향편향; imputation 필요 | §7 | US | High | DR-2B에서 검증 |
| SEC EDGAR docs (data.sec.gov, submissions/XBRL, filing acceptance) [SEC-EDGAR] | 공식/1차 | 무료 filing-timestamp + as-reported XBRL floor; 8-K Item 2.02 실적일 | §6(A),7 | US | High | DR-2B 검증 |
| CRSP / Norgate / Sharadar docs [Vendor] | 공식/벤더 | survivorship-aware 가격·수익·구성종목·상폐 | §6(A/B),7 | US | Med | feasibility 근거; 최종선택 Requires confirmation |
| Kenneth R. French Data Library [KFrench] | 공식/1차 | 팩터 구성·중립화 방법 참조 | §6(D),9 | US | High | factor methodology |
| **DR-3 Final Validation Protocol v0.1** [DR-3] | 내부 정본 | 검증 프레임 LOCK·임계값 house rule·conditional purging·lifecycle | 전반 | general | Internal-lock | PATCHED-LOCK |
| **DR-4 Final Model Candidate Map v0.1** [DR-4] | 내부 정본 | Phase 1A 허용/제외·1/N baseline·MVO reject·gate-by-treatment | §3,5,16 | general | Internal-lock | PATCHED-LOCK |
| **Integrated Lock Sheet DR1→DR2B v0.1** [LockSheet] | 내부 정본 | benchmark≠universe·cost 분해·PIT/survivorship·US-core first | §3,6,7 | US/KR | Internal-lock | COMPLETE thru DR-2B |

*보조 요약(Kritzman 2010; Kirby-Ostdiek 2012)는 "1/N은 hard-to-beat지 절대 불패 아님" qualifier로만 사용(증거강도 한 단계 하향).*

---

## 3. Phase 1A Scope Lock

### Included (Phase 1A core — DR-4 §7 상속)
| # | 항목 | Layer | 근거 |
|---|---|---|---|
| 1 | PIT core characteristics | L3 | DR-4 baseline |
| 2 | simple factor sleeves (value / quality·profitability / momentum / low-vol / size·liquidity 통제) | L3/L4 | DR-4 baseline; [KFrench] |
| 3 | cross-sectional rank composite | L4 | DR-4 baseline |
| 4 | equal-weight alpha blend | L5 | DR-4 baseline |
| 5 | 1/N portfolio | L6 | **[DGU2009] boring baseline** |
| 6 | equal-weight top-N | L6 | DR-4 baseline |
| 7 | monotone rank-to-weight | L6 | [Grinold/CFA] score→weight |
| 8 | basic hard risk cap | L7 | 결정론 risk engine |
| 9 | simple cost haircut | L8 | [AHM2019][NMV2016] |
| 10 | basic execution support (no-trade buffer·participation cap·VWAP/TWAP handoff) | L9 | DR-4 baseline |
| 11 | paper/shadow monitoring | L11 | DR-3 §9 |

### Excluded (Phase 1A에서 *연구·실험하지 않음* — 명시적 out-of-scope)
penalized regression · learned blending · tree ensemble (XGBoost/LightGBM/CatBoost) · NLP/event ML · LLM-derived alpha · TSFM / financial foundation / deep sequence · robust optimizer / HRP / constrained MVO · **raw MVO (reject)** · 비선형 market-impact 모델 · regime model · alternative data · RL · black-box meta-allocator · autonomous online retraining · live execution automation · free-form LLM trading control.

> 제외 사유는 DR-4 분류 그대로: penalized reg/tree/optimizer 고도화 = Phase 1B/1C challenger; TSFM/deep = reject-for-alpha(overlay만); raw MVO = estimation-error maximizer reject [DGU2009]. **제외 항목은 "지금 자원을 쓰지 않는다"이지 "영구 불가"가 아니다.**

---

## 4. Phase 1A Experiment Objective (plain language)

**목적은 수익 최대화가 아니다.** Phase 1A는 *시스템의 뼈대가 정직하게 작동하는지*를 증명하는 단계다. 구체적으로 다음을 테스트한다:

| 테스트 대상 | 합격의 의미 | 근거 |
|---|---|---|
| **데이터 정합(data integrity)** | PIT·생존편향·CA·delisting이 게이트를 통과 | [LockSheet §2][Shumway1997] |
| **벤치마크 sanity** | self-built cap-weight TR이 외부 비교지수와 설명 가능한 drift 내 | [DR-3 D-07] |
| **비용 현실성(cost realism)** | after-cost로 평가, fixed-bps 단독 아님, stress 견딤 | [AHM2019][NMV2016][PW2020] |
| **baseline 신호 재현성** | versioned config에서 동일 결과 재생산 | [AHM2019] reproducibility |
| **OOS / walk-forward 기계** | chronological split·최종 holdout 1회성이 작동 | [LdP2018][AHM2019] |
| **experiment registry** | 모든 trial이 기록됨(미기록 trial = 실험 무효) | [AHM2019] trial count N |
| **failure logging** | 실패가 분류·기록·재발방지됨 | [DR-3 §11] |
| **promotion/quarantine/reject 규칙** | 상태 전이가 규칙대로 작동 | [DR-3 §10][DR-4 §6] |

> 즉 Phase 1A의 "성공"은 *높은 평균성과*가 아니라 **오류를 잡아내는 구조적 건전성**이다. baseline이 벤치를 못 이겨도, 파이프라인이 정직하게 그것을 보여주면 Phase 1A는 성공이다.

---

## 5. Experiment Registry Schema

> 한 experiment = 하나의 사전등록된 가설 + 고정된 config 묶음. 변형(variant)·trial 정의는 §12. **미기록 trial은 실험 전체를 무효화**한다 [AHM2019].

| Field | Type | Req | Allowed / format | Example | Why it matters |
|---|---|---|---|---|---|
| experiment_id | string (slug) | Y | `P1A-Bxx-YYYYMMDD-nn` | `P1A-B07-20260610-01` | 불변 식별자; 모든 artifact 링크 키 |
| experiment_name | string | Y | free | "cross-sectional rank composite" | 사람 가독 |
| experiment_owner | string | Y | free | "yongha" | 책임 소재 |
| creation_date | date | Y | ISO-8601 | 2026-06-10 | 시점 추적 |
| hypothesis_id | string | Y | FK→hypothesis registry | `H-0012` | 사전등록 가설 연결 [AHM2019] |
| hypothesis_text | string | Y | free, 사전작성 | "value rank가 EW universe 대비 양의 after-cost active return" | 사후 합리화 방지 |
| market_sleeve | enum | Y | `US` / `KR` | US | US-core first [LockSheet] |
| universe_config_id | string | Y | FK→§6B | `UNI-US-broadcommon-v1` | 모집단 고정 |
| benchmark_config_id | string | Y | FK→§6C | `BMK-US-selfTR-v1` | 벤치 고정 |
| data_snapshot_id | string | Y | FK→§6A (hash 포함) | `DS-US-20260610-a3f8` | 재현성 핵심 |
| feature_config_id | string | Y | FK→§6D | `FEAT-value-v1` | 피처 정의 고정 |
| alpha_config_id | string | Y | FK→§6E | `ALPHA-rankcomposite-v1` | 신호 정의 고정 |
| portfolio_config_id | string | Y | FK→§6F | `PORT-1N-v1` | 가중 규칙 고정 |
| risk_config_id | string | Y | FK→§6G | `RISK-hardcap-v1` | 리스크 규칙 고정 |
| cost_config_id | string | Y | FK→§6H | `COST-US-base-v1` | 비용 가정 고정 |
| validation_config_id | string | Y | FK→§6I | `VAL-WF-v1` | OOS 규칙 고정 |
| trial_group_id | string | Y | 묶음 키 | `TG-B07` | 같은 가설의 trial 군집 |
| trial_number | int | Y | ≥1 | 1 | 군집 내 trial 일련 |
| degrees_of_freedom_count | int | Y | ≥0, 사전 선언 | 0 | DoF 추적(MTC 패널티 입력) [AHM2019] |
| search_budget_used | int | Y | ≤ budget(§12) | 1 | 누적 trial 소비량 |
| OOS_window | string | Y | rule 또는 date-range | "rolling 12m, step 1m" | OOS 정의 |
| walk_forward_scheme | enum | Y | `rolling` / `expanding` | rolling | §8 |
| status | enum | Y | §13 states | `OOS-evaluated` | lifecycle 상태 |
| decision | enum | Y | `promote`/`quarantine`/`reject`/`pending` | quarantine | 판정 |
| decision_date | date | N | ISO-8601 | 2026-06-12 | 판정 시점 |
| decision_reason | string | Y if decided | free | "after-cost IR < provisional cut" | 감사 추적 |
| links_to_reports | list[uri] | Y | §14 report 경로 | `[reports/P1A-B07.md]` | 산출물 |
| failure_log_id | string | N | FK→§15 | `F-0007` | 실패 연결 |
| approval_required | bool | Y | true/false | false | Phase 1A core는 보통 false; 승격은 true [DR-3] |
| notes | string | N | free | — | 기타 |

**Lock now:** 필드 *구조*. **Provisional:** allowed-values 세부(상태명 등은 §13과 동기화).

---

## 6. Config Schema Set

> 모든 config는 **버전 + 불변(immutable once referenced)**. 변경 시 새 버전 id. 모든 backtest는 raw config id들로 재현 가능해야 함 [AHM2019].

### A. Data Snapshot Config
| Field | Type | Allowed / rule | Status |
|---|---|---|---|
| raw_source | enum | `EDGAR` / `CRSP` / `Norgate` / `Sharadar` / ... | **Requires confirmation** (택1+floor) |
| vendor_source_version | string | 벤더 릴리스/버전 | Requires confirmation |
| extraction_date | date | 추출 시점 | Lock now (rule) |
| point_in_time_rule | string | feature timestamp ≥ filing/availability time; 미확보시 next session [DR-3 D-02/03] | **Lock now (rule)** |
| corporate_action_policy | string | split/div/distribution 조정계수 reconcile [DR-3 D-05] | Lock now (rule) |
| delisting_inactive_policy | string | inactive 포함 + **mandatory imputation**(US: CRSP 누락→Shumway식 -30%/-55% 등) [Shumway1997][LockSheet §5] | Lock now (rule); 수치 Provisional |
| filing_timestamp_policy | string | EDGAR acceptance datetime; day-level만이면 next-session 보수 [SEC-EDGAR][DR-3] | Lock now (rule) |
| missing_data_policy | string | OHLCV 결측 규칙 문서화·테스트 [DR-3 D-08] | Lock now (rule) |
| data_hash | string | snapshot 콘텐츠 해시 | **Lock now (필수)** — 재현성 |
| data_version_lineage | string | raw id·release·transform hash [DR-3 D-11] | Lock now |

### B. Universe Config
| Field | rule | Status |
|---|---|---|
| market | US (Phase 1A) | Lock now |
| inclusion_rule | common stock only (share-code whitelist) [LockSheet §5] | Lock now (rule); 코드집합 Provisional |
| exclusion_rule | ETF/ADR/REIT/CEF/preferred/units 제외 | Lock now (rule) |
| liquidity_filter | min ADV / price floor (값 미정) | **Do not lock yet** |
| survivorship_policy | inactive/delisted 포함(as-of) [DR-3 D-04] | Lock now (rule) |
| reconstitution_freq | as-of monthly (rebalance와 정합) | Provisional |
| as_of_date_handling | no future constituents [DR-3 D-01] | **Lock now (rule)** |

> 모집단 후보: CRSP-style broad common-stock 또는 Russell-1000-like liquid — 둘 다 Integrated Lock Sheet에서 **Provisional**. Phase 1A는 *하나*를 고정해 실험, 비교는 Phase 1B 이후.

### C. Benchmark Config
| Field | rule | Status |
|---|---|---|
| reporting_benchmark | 외부 비교용(예: broad US index) — reporting only, tradable universe 아님 [LockSheet §2] | **Do not lock yet** (후보 미정) |
| internal_self_built_benchmark | **actual universe의 cap-weight TR 재구성** [DR-3 D-07][DGU/Daniel] | **Lock now (필수)** |
| total_return_policy | 배당 재투자 포함 TR | Lock now (rule) |
| weight_construction | float-adjusted cap-weight (free-float 미확보시 full-cap + 플래그) | Provisional |
| rebalancing_rule | monthly as-of | Provisional |
| benchmark_drift_tolerance | self-built vs 외부 비교지수 drift 한도 | **Provisional (house rule)** — 값 calibration 필요 |

### D. Feature Config
| Field | rule | Status |
|---|---|---|
| factor_list | value / quality·profitability / momentum / low-vol / size·liquidity (sleeve별 분리) | Lock now (목록); 정의 Provisional |
| winsorization | cross-sectional 양측 컷(예: 1%/99%) | Provisional (값) |
| standardization | cross-sectional z-score 또는 rank-normalize | Lock now (rule) |
| sector_adjustment | sector-neutral 옵션 — **raw vs neutralized 둘 다 리포트**(중립화가 alpha 지울 수 있음) [KFrench] | Lock now (비교 의무) |
| beta_adjustment | beta-neutral 옵션(동일하게 raw vs adj 비교) | Lock now (비교 의무) |
| lag_rule | feature는 가용시점 이후만 — look-ahead 금지 [AHM2019][DR-3 D-02] | **Lock now (rule)** |
| missing_value_rule | sleeve별 결측 처리(제외/중앙값 등) 문서화 | Provisional |

### E. Alpha Config
| Field | rule | Status |
|---|---|---|
| factor_sleeve_definition | sleeve = 단일 특성 rank | Lock now |
| rank_construction | cross-sectional rank (asc/desc 방향 사전고정) | Lock now (rule) |
| composite_score | equal-weight rank 평균 (학습 가중 금지=Phase 1A) | Lock now (rule) |
| tie_handling | average rank | Lock now (rule) |
| neutralization_option | off / sector / beta (D와 동기) | Provisional |
| refresh_frequency | monthly | Provisional |

> score→weight 매핑·IC 진단의 이론 근거: Grinold α=Vol×IC×Score, Fundamental Law IR=TC·IC·√BR [Grinold/CFA].

### F. Portfolio Config
| Field | rule | Status |
|---|---|---|
| construction_method | `1/N` / `equal-weight top-N` / `monotone rank-to-weight` (택1, 사전고정) | Lock now |
| top_N | top-N의 N (값 미정) | Provisional |
| max_name_weight | 종목당 상한(하드캡) | Provisional (house rule) |
| max_sector_weight | 섹터 상한 | Provisional (house rule) |
| cash_handling | fully invested 가정(현금 0 또는 명시) | Lock now (rule) |
| rebalance_frequency | monthly (non-overlapping → purging 최소 [LdP2018]) | Lock now (rule) |

### G. Risk Config (결정론, 학습 없음)
| Field | rule | Status |
|---|---|---|
| hard_caps | name/sector 하드캡(=F와 정합) | Lock now (rule) |
| liquidity_cap | per-name ADV 참여 상한 | Provisional (house rule, §11) |
| turnover_cap | 회전율 상한(값 미정) | **Do not lock yet** |
| beta_sector_exposure_check | 노출 모니터(veto 아닌 watch부터) | Lock now (rule) |
| drawdown_watch | 누적/MDD 격차 watch | Provisional (값) |
| risk_veto_rule | 하드캡 위반시 결정론적 거부(=production veto의 Phase 1A 버전) | Lock now (rule) |

### H. Cost Config
| Field | rule | Status |
|---|---|---|
| commission | bps (브로커) | Requires confirmation |
| fees | 거래소/규제 수수료 | Requires confirmation |
| tax_levy | 세금/levy (US/KR 분리) | Lock now (분리); 값 Requires confirmation |
| spread_proxy | bid-ask spread proxy | Provisional |
| slippage_proxy | **fixed-bps 단독 불충분** [AHM2019] | Lock now (rule); 값 Provisional |
| turnover_cost | turnover×cost | Lock now (rule) |
| base_cost | 위 합산 base 시나리오 | Lock now (rule) |
| cost_2x | base×2 stress | **Provisional (house rule)** [DR-3] |
| cost_3x_or_adverse | base×3 또는 calibrated adverse | **Provisional (house rule)** |

### I. Validation Config
| Field | rule | Status |
|---|---|---|
| train_window | chronological, 사전고정 [AHM2019] | Lock now (rule); 길이 Provisional |
| validation_window | 튜닝용(test와 분리) | Lock now (rule) |
| OOS_window | time-ordered OOS | **Lock now (rule)** |
| walk_forward_schedule | rolling 또는 expanding + step | Lock now (rule); param Provisional |
| final_holdout_rule | **1회성, 재튜닝 금지** [AHM2019][LdP2018] | **Lock now (rule)** |
| metric_list | §10 | Lock now |
| pass_fail_criteria | §10 hard/soft gate | Provisional (값) |
| reporting_template | §14 | Lock now |

---

## 7. Data Acceptance Gate

> **데이터 게이트를 통과하지 못하면 어떤 Phase 1A 실험도 유효하지 않다** [LockSheet §1][DR-3 §4]. (DR-3 D-01~D-12 상속·Phase 1A 적용)

| Test ID | Test name | Purpose | Input | Pass condition | Failure action | Severity |
|---|---|---|---|---|---|---|
| G-01 | PIT universe replay | no future constituents | as-of universe table | as-of date에 미래 구성종목 0 | block alpha | Critical |
| G-02 | No future fundamentals | look-ahead 방지 | feature ts vs filing ts | feature_ts ≥ filing/availability_ts | block alpha | Critical |
| G-03 | Filing timestamp lag | 공시 가용성 | EDGAR acceptance datetime | accepted 이후에만 사용; day-level이면 next session | block alpha | Critical |
| G-04 | Delisting/inactive inclusion | survivorship | inactive/delisted set | 포함 + imputation 정책 존재 [Shumway1997] | block alpha | Critical |
| G-05 | Corporate-action reconciliation | 조정 정합 | raw vs adjusted | split/div/distribution 조정계수 reconcile | block alpha | Critical |
| G-06 | Dividend/distribution reconciliation | TR 정확성 | cash distribution | 수익정의에 맞게 포함/제외 | block alpha | High |
| G-07 | Missing OHLCV policy | 결측 통제 | OHLCV gaps | 정책 문서화+테스트 통과 | quarantine data | High |
| G-08 | Abnormal return / split detection | 이상치 | return jumps | CA로 설명 or 플래그 | quarantine data | Medium |
| G-09 | Benchmark replication sanity | 벤치 오염 | self-built TR vs 비교지수 | drift 설명·한도 내 [DR-3 D-07] | block alpha | High |
| G-10 | Cost data sanity | 비용 현실성 | cost inputs | 분해 항목 존재·범위 합리 | quarantine | High |
| G-11 | Identifier mapping integrity | 시계열 연속성 | id link history | 안정 식별자·링크 검증 | block alpha | High |
| G-12 | Data lineage / hash check | 재현성 | snapshot hash·version | raw id·release·transform hash 기록 | block alpha | Critical |

**Lock now:** 테스트 *목록·pass 조건 규칙*. **Provisional:** drift 한도·imputation 수치.

---

## 8. OOS / Walk-forward Split Design

> 원칙: **chronological split만** (random/k-fold 금지 — 비-IID·시계열 상관) [LdP2018 Ch.7][AHM2019]. test는 모델·하이퍼 결정 후 **1회만**; 사후 수정 시 evidence clock 리셋.

| Split component | Purpose | Rule | Provisional param | Failure mode |
|---|---|---|---|---|
| Chronological split | 누수 방지 | 시간순만, random 금지 | — | 랜덤분할 시 미래누수 |
| Train / Validation / Test | 튜닝과 심사 분리 | validation=튜닝, test=불가침 | window 길이 Unknown | test로 튜닝하면 in-sample化 |
| Walk-forward | 연구-배치 흐름 모사 | rolling 또는 expanding + step | window/step Unknown | 단일 경로 의존 |
| Final untouched holdout | 종단 심사 | **1회성, 재튜닝 금지** [AHM2019] | 길이=max(252d, 12 rebal, 4 earnings) (house) | 짧으면 잡음↑ |
| Regime coverage | 일반화 | 가능한 한 상이한 vol/rate 국면 포함 | 정의 Unknown | 단일 국면 과적합 |
| Re-estimation cadence | 시점 정직 | rebalance 주기와 정합(monthly) | — | 미래 파라미터 누수 |
| Purging / embargo | label overlap 누수 | **monthly non-overlap → 최소/불요**; 다일 보유·overlap시 필수 [LdP2018 Ch.7] | embargo h≈0.01T (overlap시) | overlap 무시시 누수 |
| "새 trial" 정의 | trial 난립 통제 | config 변경·튜닝 1회 = 1 trial(§12) | — | 미기록 trial=실험 무효 |

> **purging/CPCV 판정(DR-3 conditional-lock 재확인):** Phase 1A는 월간 non-overlapping cross-sectional → **단순 walk-forward + 최종 holdout으로 충분**, 전면 CPCV는 과설계. 다일 overlapping 보유로 가면 purging+embargo 필수.
> **날짜는 발명하지 않는다** — 데이터 lock 파일이 날짜를 주지 않으므로 위는 *규칙*만; 실제 train/test 경계 날짜는 data snapshot 확정 후 기입(**Unknown**).

---

## 9. Phase 1A Baseline Experiment Matrix (B0–B11)

> 각 실험은 §5 registry + §6 config로 등록. 모든 행은 §7 게이트 통과 후에만 유효. promotion/quarantine/reject 임계값은 **Provisional house rule**(§10/§13).

| ID | Hypothesis(사전) | 필요 데이터 | Feature config | Portfolio | Risk | Cost | Validation | Expected failure mode | Promote 조건 | Quarantine | Reject |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **B0** | 데이터·벤치 파이프라인이 self-built TR을 외부 비교지수와 설명가능 drift 내로 재구성한다 (신호 없음) | OHLCV·CA·div·universe·벤치 | none | self-built cap-weight TR | none | none | benchmark sanity only | drift 과다·CA 누락 | 벤치 sanity 통과·재현 | drift 경계 | drift 설명불가 |
| **B1** | equal-weight universe(1/N)가 깨끗하게 재현·after-cost 측정된다 | B0 + cost | none | **1/N** | hardcap | base | WF+holdout | turnover/비용 누락 | 재현·after-cost 산출 | 비용 이상 | 파이프라인 실패 |
| **B2** | value rank가 EW 대비 양의 after-cost active return(가설검정, 수익예측 아님) | + value 특성 | value sleeve | monotone rank-to-weight | hardcap | base | WF+holdout+RankIC | 신호 없음/노출 위장 | after-cost active>0(provisional)·RankIC>0 | 경계 | 음수·불안정 |
| **B3** | quality/profitability rank 동일 | + quality | quality sleeve | 〃 | hardcap | base | 〃 | low-vol tilt 위장 | 〃 | 〃 | 〃 |
| **B4** | momentum rank 동일 | + momentum | momentum sleeve | 〃 | hardcap | base | 〃 | turnover 폭증 | 〃 + turnover 한도 | turnover 경계 | turnover 폭증 |
| **B5** | low-volatility rank 동일 | + vol | low-vol sleeve | 〃 | hardcap | base | 〃 | 단순 beta 노출 | 〃 (raw vs beta-neutral 비교) | 〃 | 〃 |
| **B6** | size/liquidity **통제**가 신호를 설명/제거하는가 | + size/liq | size/liq control | 〃 | hardcap | base | 〃 | 소형주 비유동 alpha | 통제 후 잔존 alpha | 부분 잔존 | 통제시 소멸 |
| **B7** | cross-sectional rank composite(EW blend)가 단일 sleeve 대비 안정적 | B2–B6 특성 | composite(EW rank) | 〃 | hardcap | base | WF+holdout+RankIC stability | sleeve 상관 과다 | 안정성↑·after-cost active>0 | 경계 | 불안정 |
| **B8** | equal-weight factor sleeve blend(L5) = composite와 정합 | 〃 | EW alpha blend | 〃 | hardcap | base | 〃 | 메타 과적합(학습 가중 금지 확인) | 정합·재현 | 경계 | 불일치 |
| **B9** | monotone rank-to-weight vs 1/N vs top-N 포트 구성차 진단 | B7 score | composite | 1/N · top-N · rank-to-weight 비교 | hardcap | base | WF+holdout | 구성법별 turnover 차 | 구성차 설명 가능 | — | 진단 실패 |
| **B10** | hard risk cap 변형(name/sector cap)이 신호·turnover에 미치는 영향 | B7 | composite | rank-to-weight | **cap 변형** | base | 〃 | cap이 alpha 제거 | 영향 정량화 | — | — |
| **B11** | cost stress(2x/3x)에서 baseline의 부호·유의성 | B7 | composite | rank-to-weight | hardcap | **base/2x/3x** | WF+holdout+cost stress | 2x에서 음수 전환 | 2x에서 active≥0(provisional) | 2x 경계 | 2x 음수 |

> **B0(데이터-only)가 첫 실험**인 이유: DR-4 kill 조건 = "지루한 baseline조차 깨끗이 재현 못 하면 alpha 빌드 중단". 가장 싸고·고확신·저-DoF 작업부터 front-load.

---

## 10. Metrics and Reporting Policy

> 분류: **hard gate**(미달=승격불가) / **soft gate**(미달=quarantine 검토) / **diagnostic**(해석용) / **report only**(기록). 수치 컷은 출처기반 hard가 아니면 **Provisional house rule** [DR-3].

| Metric | 분류 | Threshold 처리 | 근거 |
|---|---|---|---|
| after-cost excess (active) return | **hard gate** | >0 (provisional) | [AHM2019][NMV2016] |
| information ratio (IR) | soft gate | IR>0.25 (provisional house) — 단기 holdout서 표본오차 큼, CI 병기 | [DR-3 provisional] |
| tracking error | report only | — | — |
| turnover | **hard gate**(비용 연동) | 과도 회전 시 net 소멸; 1-side monthly <50% 생존 경향 | [NMV2016] |
| ADV participation / capacity | soft gate | median<5%·max<10% (provisional house) | [DR-3 provisional] |
| max drawdown | soft gate | benchmark-relative gap watch | [DR-3] |
| drawdown duration | diagnostic | — | — |
| hit rate | diagnostic | — | optional |
| **Rank IC mean** | **hard gate**(cross-sectional) | median Rank IC>0 (provisional) | **[Grinold/CFA]** |
| Rank IC stability (IR-of-IC) | soft gate | 부호 유지 ≥65% 창 (provisional) | [Grinold/CFA] |
| quantile return spread | diagnostic | 단조성 점검 | [Grinold/CFA] |
| factor exposure | diagnostic | — | — |
| sector exposure | diagnostic | — | — |
| beta exposure | diagnostic | raw vs neutral 비교 | [KFrench] |
| cost drag | report only | base/2x/3x 분해 | [NMV2016] |
| benchmark drift | **hard gate** | self-built vs 비교지수 한도 내 | [DR-3 D-07] |
| data error count | **hard gate** | 게이트 위반 0 (Critical) | [DR-3 §4] |
| DSR / deflated Sharpe | diagnostic (Phase 1A) | 값=trial count N 의존 → **로깅 의무, escalate later** | [LdP2018][AHM2019] |
| PBO | diagnostic (Phase 1A) | 다수 trial/family 비교시 필요(Phase 1C↑) | [DR-3] |
| t-stat | diagnostic only | 다중검정 보정 전 무의미(t=2.0 ≈1/20 우연) | **[AHM2019]** |

> **수치 임계값을 발명하지 않는다.** house rule은 전부 Provisional로 표시; calibration은 data snapshot + trial 분포 확정 후.

---

## 11. Cost Stress Configuration

> after-cost가 in-sample·OOS **양쪽** 필수; fixed-bps 단독 불충분 [AHM2019]. US 먼저, KR 별도 adapter.

| Cost stress scenario | Applies to | Purpose | Config fields | Failure action |
|---|---|---|---|---|
| base cost | 모든 trading 경로 | 현실 비용 기준선 | commission/fees/tax/spread/slippage/turnover_cost | 음수면 승격불가 |
| 2x cost | 〃 | 비용 과소추정 내구성 | base×2 | 2x active<0 → 승격불가(provisional) |
| 3x / calibrated adverse | 〃 | 악조건 | base×3 또는 보정 adverse | 다수 창 부호전환 → reject(provisional) |
| turnover shock | high-turnover sleeve(B4 등) | 회전 비용 폭증 | turnover×k | net 소멸 시 quarantine [NMV2016] |
| spread widening | 비유동 종목 | 스프레드 확대 | spread×k | capacity fail |
| ADV participation stress | 전체 | 유동성 제약 | median/max ADV cap | 초과시 capacity fail (provisional) |
| missing-cost-data fallback | 비용 결측 | 보수 대체 | 보수값 + 플래그 | quarantine |
| **US treatment** | US-core | 1차 pilot | US adapter | — |
| **KR treatment** | KR-addon(later) | 별도 재보정 | KRX-only vs SOR-enabled 분리; 시각불명 공시=next session [LockSheet §3][DR-3 §7] | KR은 US보다 한 단계 보수 |

---

## 12. Trial Budget Policy

> **미기록 trial = 실험 무효** [AHM2019]. trial 수 *와* 상관을 추적해야 DSR/PBO/FWER/FDR 계산 가능.

| 정의 | 규칙 |
|---|---|
| **trial** | config 1회 평가(같은 가설·다른 파라미터 1세트) = 1 trial. degrees_of_freedom_count·search_budget_used 증가 |
| **variant** | 동일 가설 내 단일 파라미터 변경(예: top-N의 N) = 새 trial(같은 trial_group_id) |
| **새 experiment_id 필요** | 가설/universe/benchmark/data_snapshot 변경 = 새 experiment |
| **failed trial 기록** | status·decision=reject + decision_reason 필수(삭제 금지) |
| **abandoned trial 기록** | status=archived + 사유; budget에 계상 |
| **Phase 1A search budget** | 의도적으로 **낮게**(low-DoF baseline). 상한값=**Provisional house rule**(절대수 발명 금지 — calibration 후) |
| **Phase 1A에서 DSR/PBO 보정 요구** | trial이 누적되거나 sleeve/composite를 다수 비교할 때(B7/B9) 시작 — 단 Phase 1A는 주로 **로깅 의무**, 본격 보정은 Phase 1C [DR-3] |
| **미기록 trial의 효과** | 사후 trial count N 복원 불가 → 모든 다중검정 통계 무효 → 실험 전체 무효 [AHM2019][LdP2018] |

---

## 13. Promotion / Quarantine / Reject Lifecycle

| State | Entry condition | Exit condition | Failure condition | Required artifact | Human approval |
|---|---|---|---|---|---|
| draft | experiment 초안 | hypothesis 등록 | — | hypothesis_text | N |
| registered | hypothesis_id 등록 | data-gate 진입 | 가설 미작성 | registry entry(§5) | N |
| data-gate-pending | config 고정 | 게이트 평가 | — | config ids(§6) | N |
| data-gate-passed | §7 전 Critical 통과 | backtest 진입 | Critical 실패→reject/quarantine | gate report | N |
| backtest-running | config·version 로깅 | OOS 평가 | 재현 실패 | backtest config/hash | N |
| OOS-evaluated | WF+holdout 증거 | promote/quarantine/reject | holdout 재튜닝 | OOS report(§14) | N |
| quarantined | gate 경계/불안정 | patch 후 재평가 or retire | 반복 실패 | failure log(§15) | N |
| rejected | hard gate 미달 | archived | — | decision_reason | N |
| promoted-to-Phase-1B-review | baseline 재현·sanity·cost stress·registry·failure-log 작동 | Phase 1B 게이트(§16) | — | 전 artifact 묶음 | **Y** |
| archived | 종결 | — | — | 최종 기록 | N |

> Phase 1A core 실험 자체는 human approval 불필요(저위험·off-path). **다음 Phase로의 승격(promoted-to-Phase-1B-review)에는 human approval 필수** [DR-3 §10].

---

## 14. Report Template (per experiment, Markdown)

```markdown
# Phase 1A Experiment Report — {experiment_id}
## 1. Experiment summary
- experiment_id / name / owner / date / status / decision
## 2. Hypothesis
- hypothesis_id, hypothesis_text (사전등록), market_sleeve
## 3. Data snapshot
- data_snapshot_id, raw_source, vendor_version, extraction_date, data_hash
- PIT rule / CA policy / delisting-imputation policy
## 4. Universe
- universe_config_id, inclusion/exclusion, liquidity filter, survivorship, as-of handling
## 5. Benchmark
- benchmark_config_id, self-built TR 구성, 외부 비교지수, drift
## 6. Feature config
- factor_list, winsor/standardize, sector/beta neutralization (raw vs neutral)
## 7. Portfolio config
- construction_method, caps, rebalance freq
## 8. Risk config
- hard caps, liquidity cap, turnover, exposure checks, veto events
## 9. Cost config
- 분해(commission/fees/tax/spread/slippage), base/2x/3x
## 10. Validation split
- train/val/OOS windows, walk_forward_scheme, final holdout 사용 여부
## 11. Results summary (서술 — 수익예측 아님)
## 12. Metrics table  (§10 분류별 — hard/soft/diagnostic/report)
## 13. Cost stress table  (base/2x/3x·turnover/ADV)
## 14. Failure analysis  (failure_log_id 링크)
## 15. Decision  (promote/quarantine/reject + decision_reason)
## 16. Next action
- trial count N·search budget used·reproducibility hash
```

---

## 15. Failure Log Template

```markdown
# Failure Log — {failure_id}
- failure_id:
- experiment_id:
- date_detected:
- failure_type: {look-ahead | survivorship | delisting-omission | CA-error | stale-fundamentals |
                 benchmark-mismatch | cost-underestimation | turnover-explosion |
                 reproducibility | trial-unlogged | data-missing | other}
- affected_layer: {L0..L12}
- severity: {Critical | High | Medium | Low}
- description:
- root_cause:
- detection_method: {gate test id | metric | manual}
- immediate_action: {block | quarantine | reject | patch}
- long_term_fix:
- status: {open | mitigated | closed}
- owner:
- linked_artifacts: [report, config ids, data hash]
```
*failure_type 목록은 DR-4 §10 failure-mode register와 정합.*

---

## 16. Phase 1B / Phase 1C Gate

### Phase 1B(저-DoF challenger: penalized regression·constrained linear·deterministic event feature)는 다음 *전부* 충족 전 시작 불가:
| 조건 | 근거 |
|---|---|
| 데이터 게이트가 **안정적**(반복 통과) | [DR-3 §4] |
| benchmark sanity 통과(B0) | [DR-3 D-07] |
| baseline 실험(B1–B11)이 **재현 가능**(versioned config) | [AHM2019] |
| cost stress 리포팅 작동 | [NMV2016] |
| failure log 작동 | [DR-4 §10] |
| trial registry 작동(trial count N 추적) | [AHM2019] |

### Phase 1C(통제 ML challenger: shallow tree ensemble 등)는 추가로:
| 조건 | 근거 |
|---|---|
| Phase 1B 통과 | [DR-4 §7] |
| **multiple-testing 통제 가동**(DSR/PBO, N 추적) | [LdP2018][DR-3] |
| feature/model registry 가동 | [DR-3] |
| search budget 정책 강제 | [AHM2019] |
| high-DoF 모델 게이트(독립 holdout·heavier DSR/PBO) 준비 | [DR-4 §6] |

> Phase 1D(quarantine 탐색: TSFM/deep/alt-data/LLM weak signal)는 **production 경로 영구 차단**, 별도 거버넌스·재현·데이터권리·장기 paper/shadow 필요 [DR-4 §7].

---

## 17. Final Lock Decision Table

| Item | Status | Note |
|---|---|---|
| experiment registry schema | **Lock now** | 필드 구조 §5 |
| data snapshot config | **Provisional** | raw_source/vendor = Requires confirmation |
| universe config | **Provisional** | 모집단 후보 미확정 |
| benchmark config | **Provisional** | self-built TR=Lock(필수); 외부 비교지수=Do not lock yet |
| feature config | **Provisional** | 목록 Lock; winsor/정의 값 미정 |
| alpha config | **Lock now** | EW rank composite 규칙(학습가중 금지) |
| portfolio config | **Lock now** | 1/N·top-N·rank-to-weight 규칙; N·cap Provisional |
| risk config | **Provisional** | 하드캡 규칙 Lock; turnover 컷 Do not lock yet |
| cost config | **Provisional** | 분해 규칙 Lock; 값 Requires confirmation |
| validation config | **Lock now** | chronological·holdout 1회성 규칙; window param Provisional |
| data acceptance gate | **Lock now** | 테스트 목록·규칙 §7 |
| OOS / walk-forward split | **Lock now** | 규칙; 날짜·param Unknown until snapshot |
| cost stress | **Provisional** | 2x/3x house rule |
| trial budget policy | **Provisional** | 규칙 Lock; 절대 상한 house rule |
| report template | **Lock now** | §14 |
| failure log template | **Lock now** | §15 |
| promotion/quarantine/reject rule | **Lock now** | §13 lifecycle |
| Phase 1B gate | **Lock now** | §16 조건 |
| Phase 1C gate | **Lock now** | §16 조건 |

---

## 18. Recommendation

**선택: `Patch before implementation`.**

- 설계 *프레임*(registry·config 구조·게이트·OOS 규칙·lifecycle·템플릿)은 Tier-1 근거와 DR-3/DR-4 락으로 **지금 잠글 수 있다**.
- 그러나 구현 전 **Claude red-team**(이 문서의 다음 핸드오프)으로 schema 누락·게이트 구멍·house-rule 오용을 적대 검증해야 한다.
- **데이터 스냅샷 소스/벤더(EDGAR floor + CRSP/Norgate/Sharadar 택)와 data license**가 미확정(Requires confirmation) — 이게 풀려야 universe/benchmark/cost config 값이 채워진다.
- 모든 수치 임계값은 **house rule(Provisional)** — data snapshot + trial 분포 확정 후 calibration 전에는 잠그지 않는다.
- 따라서 권고: **(1) red-team → (2) data/vendor/license 확정 → (3) house-rule calibration → 그 다음 구현/B0부터.**

---

## 19. Next Handoff

```text
[현재] Phase 1A Experiment Design v0.1 (PRIMARY, 이 문서)
   │
   ▼
[다음] Claude Phase 1 Experiment Design RED-TEAM AUDIT
   - schema 누락·게이트 우회·house-rule 오용·DR-3/DR-4 정합성·scale 적합성 적대 검증
   │
   ▼
Phase 1 FINAL Experiment Design (primary+red-team 병합)
   │
   ▼
(그 다음에야) 구현 / 프로토타입 / 백테스트
   - B0(데이터·벤치 sanity) 먼저
   - data acceptance gate 통과 후에만 B1–B11
```

**구현·백테스트·모델선택·종목추천·수익예측은 이 문서 범위가 아니며, red-team과 데이터/벤더 확정 전에는 시작하지 않는다.**

---

> **불확실성 표기:** train/test 경계 날짜, 최종 universe·외부 벤치마크, 데이터 raw source/vendor, 모든 house-rule 수치 = **Unknown / Requires confirmation** — 추정하지 않고 규칙만 잠갔다.
> **근거:** 방법론 6 findings 전부 3표 적대검증 confirmed (deep-research runId `wf_9939c3da-44b`); 내부 락 = DR-3/DR-4/Integrated Lock Sheet.
