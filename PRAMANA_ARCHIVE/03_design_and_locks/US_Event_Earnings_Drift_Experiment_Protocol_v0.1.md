# US Event / Earnings Drift — Minimal Experiment Protocol v0.1 (PRE-REGISTERED)
**Date:** 2026-06-11 · **Status:** 결과 보기 *전* 사전등록(overfit·goalpost 이동 방지) · **구독 윈도우 내 1회** · **Scope:** US, broad top-1500 PIT, 2016–2026
**목적:** 공개 *레벨* 팩터는 죽었다(Phase 1A/1B). **공시 이벤트 주변의 *변화·드리프트*가 거래 가능한 edge인지** 1회 확정 검증. **알파 사냥 아님 — event arena를 열거나 닫는 kill-test.**

## 0. 불변 규칙 (LOCKED)
- universe·benchmark·cost·IC 파이프는 Phase 1A/1B와 **동일 재사용**(검증된 것). 신호만 event 기반으로 교체.
- **레벨 팩터 재사용·재튜닝 금지.** 이건 *변화/타이밍* 신호 — Phase 1A의 gp/assets *레벨*과 다른 가설.
- **금지: XGBoost/LightGBM/tree-ensemble / LLM-alpha / TSFM / deep.** 신호 결합은 저DoF(z 동일가중)만.
- **튜닝·윈도우 탐색 금지.** 각 신호 *기본 정의 1세트*. 여러 설정 중 best 고르기 = overfit = 금지.

## 1. Event anchor (PIT)
- **이벤트 = SF1 `datekey`** (펀더멘털이 SEC에 공개된 날 = 공시일). 모든 신호는 *datekey ≤ asof* 만 사용(no look-ahead). 진짜 earnings *surprise*는 analyst estimate 부재로 **fundamental-acceleration proxy로 대체**(정직한 한계 명시).

## 2. Signals (변화·서프라이즈 proxy·타이밍 — 정의 고정)
| ID | 신호 | 정의(PIT, datekey 기준) | 가설 |
|---|---|---|---|
| S1 | gp acceleration | gp/assets 의 YoY 변화 (최신 datekey vs ~4분기 전) | 막 좋아진 수익성이 드리프트 |
| S2 | revenue growth | revenue YoY 성장률 | 매출 가속 드리프트 |
| S3 | earnings momentum | eps(epsusd) YoY 성장률 | 이익 모멘텀 |
| S4 | gross-margin Δ | grossmargin YoY 변화 | 마진 개선 드리프트 |
| S5 | filing freshness | days-since-datekey (작을수록 최근 공시) | post-filing drift 창(PEAD-lite) |
- **EVENT composite** = S1~S4의 cross-sectional z(winsor ±3σ) 동일가중 평균. (저DoF, 추정파라미터 0.)
- S5(freshness)는 별도 진단 + "최근 공시 종목만" 부분표본 robustness로.

## 3. 포트폴리오·측정
- 매월 리밸런스(top-1500 PIT). EVENT composite 랭킹 → **long-only Q5 EW**(실거래형) 주측정 + long-short Q5-Q1 rank-IC diagnostic.
- 벤치: **cap-weight(주측정선)** + 1/N EW. 비용: Phase 1A 동일 tier(5/10/15bp × turnover), base/2x.
- 지표: net active vs CW(연), Rank IC·IC-IR, IC>0%, **subperiod 2016–20 vs 2021–26**, turnover, size·sector 귀속, long-only/short 분리. 신호별 단독 IC도 보고(어느 게 일하는지).

## 4. ★ PRE-REGISTERED KILL CONDITIONS (결과 전 확정 — 변경 금지)
**하나라도 걸리면 EVENT arena (이 신호군) FAIL.**
1. **net active vs cap-weight ≤ 0** → FAIL (실거래 long-only 기준).
2. **2021–2026 IC-IR < 0.10** → FAIL (최근 절반서 살아있어야).
3. **비용 후 사망** (2x cost net active ≤ 0) → FAIL.
4. **2016–2020에만 집중** (2021–26 net active ≤ 0) → FAIL.
5. **long-only가 안 됨** (long-short만 양수, long-only vs CW 음수) → FAIL.
6. **size/sector 편향으로 설명** (중립화 후 net active ≤ 0) → FAIL.

## 5. 판정 규칙 (사전 박음)
- **6개 전부 통과** → EVENT arena = **유망(deeper event study 후보)**. **즉시 paper/live 아님** — 추가 다중검정·OOS·진짜 PEAD(가격반응) 연구 후.
- **≥1개 kill 발동** → **US event(이 신호군) 종료** → 다음 = B(US 소형 cost-first kill-test), 그 다음 C(KR feasibility).
- **no tuning to rescue** · **no live/paper 자동승격** · goalpost 불변.

## 6. 산출물
`phase1a/us_event_drift.py` · `reports/US_event_drift_result.md` · `outputs/us_event_drift_result.csv` · milestone 1줄. (데이터: 기존 broad_SF1에 revenue·eps·grossmargin·roe 컬럼 추가 pull 필요 → `outputs/raw/broad_SF1_ext.csv`.)
