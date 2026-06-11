# US Public-Data Cross-Sectional Chapter — Final Lock v0.1
**Date:** 2026-06-11 · **Status:** CHAPTER CLOSED(종료선) · **Scope:** US, Sharadar+EDGAR 공개데이터, cross-sectional, long-only, 2016–2026
**한 줄:** **US 공개데이터·cross-sectional·long-only로 거래 가능한 standalone edge 없음.** 단 방향 신호 2개가 KR small/mid+event를 향함. 검증 시스템은 의도대로 작동(가짜 알파를 네 단계에서 죽임). 추가 알파 실험 금지.

## 1. B0/B1 — 데이터·벤치마크 machinery = PASS
자작 S&P500 cap-weight TR이 실제 SPY와 **corr 0.998·연차 +0.55%p**. PIT 멤버십(future-leakage 차단)·survivorship(제거+폐지 보존)·배당/TR·재현성(동결 hash) 검증. 1/N(B1) 동일 유니버스. → 파이프라인은 신뢰 가능. `reports/B0broad_B1_sp500_result.md`.

## 2. S&P500 단순팩터 = FAIL
value/quality/momentum/lowvol 대형주 Rank IC ≈ 0 (|IC|<0.01, IC-IR<0.05). 비용·다중검정 *전*인데 무신호. `reports/B2_B5_factor_result.md`.

## 3. Broad top-1500 단순팩터 = FAIL
비용 후 3/4 DEAD(value/momentum/lowvol). quality만 1차 스크린 생존(IC-IR 0.22, net +4.4%) → quarantine으로. `reports/B2B5_broad_result.md`.

## 4. Quality quarantine = standalone FAIL
decay(2016–20 IC-IR 0.42 → 2021–26 0.046, 25/26 음수) + **long-only vs cap-weight −1.15%/yr**. long-short spread(+4.4%)은 공매도 전제(솔로 불가), long-leg vs 1/N +1.79%(noise는 아님). `reports/B3_quality_quarantine_result.md`.

## 5. Low-DoF 결합 = FAIL
simple blend / constrained rank / ridge OOS 전부 net vs CW 음수(−2.4/−3.6/−0.7%). **OOS ridge IC-IR 0.014**(정직 fit 시 edge無, 2016–20 +10.5%→2021–26 −4.8% 반전). 결합이 long-leg 희석. `reports/Phase1B_lowdof_result.md`.

## 6. Event / earnings drift = FAIL
SF1 datekey(PIT) 기반 fundamental-surprise proxy(gp/rev/eps/gm YoY). **level과 달리 decay 안 함**(2021–26 IC-IR +0.219). 그러나 large-cap cap-weight 벽 → long-only vs CW −0.90%/2x −1.17%. `reports/US_event_drift_result.md`.

## 7. Small/mid cost-first = FAIL
rank 1001–3000, 보수비용. **메타패턴 확증**: 셋 다 base서 cap-weight 이김(+0.66~+2.2%)·value 부활(IC-IR 0.224). 그러나 edge가 **최저유동성 버킷에 집중**(고유동성서 quality −4.9%·blend −3.0%)·IC-IR<0.20 바·turnover·3x cost. event만 잔여(2021–26 IC-IR +0.30·고유동성 +1.7%)나 바 미달 FAIL(goalpost 불변). `reports/US_smallmid_costfirst_result.md`.

## 8. 최종 결론
**US public-data cross-sectional long-only standalone edge 없음.** 4 arena(level·결합·event·small/mid) 전부 종료. 공개 데이터로 잡을 수 있는 단순·결합·event·소형 cross-sectional 신호는 비용/유동성/벤치 벽을 넘지 못함.

## 9. 살아남은 관찰 (carry-forward 가설)
- **event/surprise는 decay가 덜하다** (level은 2021–26 소멸, event는 IC-IR +0.2~+0.3 유지).
- **신호는 small/mid에서 강해진다** (메가캡 cap-weight 벽은 large 현상; small/mid서 value 부활·blend t=3.75).
- **그러나 US에선 비용·유동성·메가캡 벤치 벽에 막힘.** → 이 두 관찰은 **KR small/mid + 공시이벤트** 가설(v2)을 향한다.

## 10. 다음 (2026-06-11 업데이트: US-only 고정)
- **Phase 2 research engine 고도화 = COMPLETE** (`Phase2_M7_M8_Report_Run_Result_v0.1.md`).
- **프로젝트 scope = US-only 고정.** 다음 = **US-Only Completion Roadmap** (`US_Only_Completion_Roadmap_v0.1.md`): packaging → workflow → next-edge/simulator → housekeeping.
- **KR = Future Market Adapter (Deferred)** — US 완성 전엔 착수 안 함. next-immediate 아님.

## ★ 종료선 (여기서 더 하면 안 되는 것 — LOCKED)
quality 재정의 · event composite 수정 · cost bar 낮추기 · small/mid universe 재조정 · rank 1001–3000 → 다른 범위 변경 · XGBoost/LLM-alpha 열기 · KR 즉시 점프. **이 중 어느 것도 안 한다.** 지금은 추가 실험이 아니라 종료선을 긋고 엔진을 성숙시킬 때.

## Artifacts (locked)
| 항목 | 경로 |
|---|---|
| Final Locks | `integrated/Phase1A_Final_Empirical_Lock_v0.1.md` · 본 파일 |
| Protocols(사전등록) | `integrated/{Broad_Universe_Factor_Retest,Phase1B_LowDoF_Challenger,Arena_Selection_Gate,US_Event_Earnings_Drift_Experiment,US_SmallMid_CostFirst}_*.md` |
| Reports | `phase1a/reports/` (B0broad·B2_B5·B2B5_broad·B3_quality_quarantine·Phase1B_lowdof·US_event_drift·US_smallmid_costfirst) |
| Code | `phase1a/*.py` (b0b1_sp500·b2b5_broad·quality_quarantine·phase1b_lowdof·us_event_drift·build_smallmid_universe·b_smallmid 등) |
| Data snapshot | `phase1a/outputs/raw/` + `HASHES.txt` (구독 윈도우 내 캐시; 해지 후 추가연구 회색지대) |
| Milestones | `phase1a/registry/phase1a_milestones.csv` |
