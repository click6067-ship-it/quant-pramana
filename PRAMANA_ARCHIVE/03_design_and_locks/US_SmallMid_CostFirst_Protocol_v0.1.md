# US Small/Mid Cost-First — Protocol v0.1 (PRE-REGISTERED)
**Date:** 2026-06-11 · **Status:** 결과 전 사전등록(overfit·goalpost 방지) · **마지막 US kill-test** · **Scope:** US domestic common, marketcap rank 1001–3000 PIT, 2016–2026
**질문:** 메가캡 cap-weight 벽이 약한 small/mid arena에서도 **비용 후** cross-sectional 신호가 살아남는가? **알파 사냥 아님 — US public-data cross-sectional arena를 닫거나 quarantine하는 kill-test.**
**근거(Arena A 메타패턴):** level·결합·event 신호 전부 vs 1/N 양수·vs cap-weight 음수 → killer = 2016–26 메가캡 cap-weight 레짐. 그 벽이 *약한* arena가 small/mid. 대신 **비용**이 새 killer.

## 0. 불변 규칙 (LOCKED)
- **신호 신규 사냥 금지.** 이미 검증된 것만: **quality(gp/assets)** · **event composite**(gp/rev/eps/gm YoY) · **simple blend**(4팩터 z 동일가중, 1회). value/momentum/lowvol는 *비교용*만(이미 DEAD). **결론 후보 = quality / event 중심.**
- 정의·튜닝·윈도우 변경 금지. **금지 모델: XGBoost/tree/LLM/TSFM/deep.**
- **소형주 비용을 낮게 잡지 않는다**(가장 중요). 정확한 비용모델보다 *보수성*.

## 1. Universe (PIT, survivorship-aware)
- 모집단: US **Domestic Common Stock** (TICKERS category).
- 각 월말(실제 거래일): marketcap **rank 1001–3000** (top-1000 제외, 다음 2000). *너무 micro로 안 감* — 먼저 중소형 전체 보고 **size bucket(예: 1001–1500 / 1501–2250 / 2251–3000)으로 나눠 어디서 죽는지** 본다.
- 필터(사전): **price ≥ $5** · **dollar-volume(ADV) 하위 극단 제거**(예: arena 내 DV 하위 10% 컷) · marketcap floor · 결측 과다 종목 제거 · **상장폐지 포함**(survivorship) · firstpricedate 이전 편입 금지.
- 현재 리스트 소급 금지(PIT marketcap 랭킹).

## 2. Signals (검증된 것만)
| ID | 정의(고정) |
|---|---|
| quality | gp/assets (SF1 ARQ, datekey PIT) |
| event | (gp/assets·revenue·eps·grossmargin YoY) z 동일가중 |
| blend | (value 1/pb · quality · momentum 12-1 · lowvol) z 동일가중 |
| (참고) value/momentum/lowvol | 단독, 비교용만 |

## 3. ★ Cost model (보수적, 사전고정)
- **one-way cost = liquidity(dollar-volume) tier 기반** (소형주 spread를 *높게*):
  - arena 내 ADV(=close×volume, 20일 평균) 분위로 3-tier: **상위 25bp / 중위 45bp / 하위 75bp** one-way(provisional house, 보수적).
  - + 선택적 impact 근사(거래대금/ADV) — capacity proxy로.
- net = gross − Σ(|Δw| × one-way cost). **base / 2x / 3x cost** 스트레스.
- **liquidity bucket별 net** 분리 보고(저유동성에만 몰리면 kill).

## 4. Benchmark (둘 다)
- **small/mid cap-weight** (arena 내부) + **small/mid 1/N**. ← 질문은 "SPY 이기냐"가 아니라 *arena 내부에서 비용 후 정보가 있냐*. 둘 다 본다.

## 5. ★ PRE-REGISTERED KILL CONDITIONS (결과 전 확정 — 변경 금지)
**하나라도 걸리면 해당 신호 FAIL.**
1. net active vs appropriate benchmark ≤ 0 → FAIL
2. net Q5-Q1 ≤ 0 → FAIL
3. IC-IR < 0.20 → FAIL
4. 2021–2026에서 사망(recent net ≤ 0 또는 recent IC-IR < 0.10) → FAIL
5. 2x cost에서 사망(net ≤ 0) → FAIL
6. 성과가 최저유동성 bucket에만 존재 → FAIL
7. turnover > 300%/yr 이고 net 약함 → FAIL
8. short leg 없이는 안 됨(long-only net ≤ 0, long-short만 양수) → FAIL

## 6. 판정 규칙 (사전 박음)
- **quality 또는 event가 8개 전부 통과** → **승격 금지**, **한 번 더 quarantine**(capacity·2x/3x·subperiod·liquidity attribution·long-only·sector/industry) 후에만 다음 단계.
- **전부 ≥1 kill** → **US public-data cross-sectional arena 종료** → **KR feasibility로 이동**(명분 강해짐).
- no tuning to rescue · no live/paper 자동승격 · goalpost 불변.

## 7. 산출물
`phase1a/build_smallmid_universe.py`(diag 먼저) · `pull_smallmid_data.py` · `b_smallmid.py` · `reports/US_smallmid_costfirst_result.md` · `outputs/us_smallmid_result.csv` · milestone. 데이터: rank1001–3000 union의 SEP(closeadj+**volume**)·DAILY(pb)·SF1(gp/assets)·SF1_ext(rev/eps/gm) pull(resumable).
