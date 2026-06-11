# v2.0 — True PEAD / Announcement-Window Drift — Protocol v0.1 (PRE-REGISTERED)
**Date:** 2026-06-11 · **Status:** 결과 보기 *전* 사전등록 · **v1 CLOSED 이후 첫 새 edge source(1개만).** · **Scope:** US-only (KR/새시장 금지).
**한 줄:** 공시/실적 발표 *직후 가격반응* 이후에 **비용 후 drift가 남는가**를 1회 검증. 팩터 또 만들기 아님 — 더 구체적인 edge source.

## edge hypothesis
공개 *레벨/펀더 surprise proxy*는 죽었지만(v1), **announcement 직후 가격반응(시장의 즉각 반영)이 그 방향으로 *지연 drift*를 남기면**(under-reaction = PEAD) 거래 가능할 수 있다. v1에서 event/surprise가 *decay 안 한* 점이 이 방향을 가리킴.

## 사용 데이터 (캐시만, 신규 pull 0)
- `broad_SEP.csv` (closeadj 일별, top-1500 union) — 가격반응·drift.
- `broad_SF1.csv` (datekey = SEC 공시일, PIT) — 이벤트 앵커.
- `DAILY_all.csv` (marketcap) — 비용 tier·유동성 버킷.
- `broad_universe_top1500.csv` — PIT 멤버십(universe 재조정 금지, 기존 그대로).

## 이벤트 정의 (고정 — 정의 사냥 금지, 처음엔 하나만)
- **Event** = SF1 `datekey` (공시/실적 발표일, PIT).
- **Announcement reaction (signal)** = `[-1, +1]` 거래일 수익률 = `closeadj[t0+1]/closeadj[t0-1] − 1` (t0 = 발표일).
- **Forward drift (outcome/holding)** = `[+2, +21]` 거래일 = `closeadj[t0+21]/closeadj[t0+2] − 1`.
- **No look-ahead:** 반응은 +1에 확정 → 포지션은 **+2에 진입**, +21 청산. (반응 관측 후 진입.)

## universe (재조정 금지)
- top-1500 PIT (기존 broad). 이벤트의 ticker가 발표 월 멤버십에 있어야 포함. price≥$5 경량 필터.

## cost model (동결 tier 재사용)
- marketcap tier **5/10/15bp** one-way (cost.py). PEAD는 진입(+2)+청산(+21) = **round-trip → 2× one-way**.
- base / 2x cost 스트레스.

## benchmark (둘)
- **announcer EW(1/N)** = 같은 달 발표 종목 전체의 평균 drift(="발표한 거 다 들고있기" 기준선).
- **cap-weight** = 같은 달 발표 종목 marketcap 가중 drift.

## 측정
월별(발표월) cross-sectional: reaction 5분위 → Q5(강한 +반응)/Q1 drift · Rank IC(reaction vs drift)·IC-IR·IC>0% · gross/net Q5-Q1 · **long-only Q5 vs 벤치** · subperiod 2016-20/2021-26 · 유동성(marketcap) 버킷별.

## ★ PRE-REGISTERED KILL CONDITIONS (결과 전 확정 — 변경 금지)
1. **net active return(long-only vs 벤치) ≤ 0** → FAIL
2. **2021–2026에서 사망** (recent net ≤ 0 또는 recent IC-IR < 0.10) → FAIL
3. **IC-IR < 0.20** → FAIL
4. **2x cost(round-trip)에서 사망** (net ≤ 0) → FAIL
5. **유동성 하위 버킷에만 존재** (저유동성만 +, 고유동성 ≤ 0) → FAIL
6. **long-only로 안 됨** (long-short만 +, long-only net ≤ 0) → FAIL

## 판정
- **6개 전부 통과** → v3 quarantine 심화 후보(즉시 paper/live 아님).
- **≥1 kill** → True PEAD(이 정의) = US 다음 후보로 종료/보류.
- no tuning to rescue · no live/paper 자동승격 · goalpost 불변.

## 금지사항 (LOCKED)
KR/새시장 착수 금지 · XGBoost/LLM-alpha/TSFM/deep 금지 · 기존 factor(value/quality/momentum/lowvol/event) 튜닝 금지 · universe 재조정 금지 · 여러 edge 동시 테스트 금지(PEAD 하나만) · kill 결과 전 박기.

## 실행
event-time(일별·발표앵커)이라 run.py의 *월 캘린더 cross-sectional* config에 안 맞음 → **단일 스크립트 `phase1a/pead_true_v1.py`**(engine.data·cost 재사용). 산출 `reports/V2_pead_true_result.md`·`outputs/pead_true_result.csv`.
