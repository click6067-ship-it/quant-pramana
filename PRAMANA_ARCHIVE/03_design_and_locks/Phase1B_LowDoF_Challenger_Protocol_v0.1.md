# Phase 1B — Low-DoF Challenger Protocol v0.1 (PRE-REGISTERED)
**Date:** 2026-06-11 · **Status:** 결과 보기 *전* 사전등록(overfit 방지) · **구독 윈도우 내 1회 실행** · **Scope:** US, broad top-1500 PIT, 2016–2026
**목적:** 단순 single-factor가 안 되는 건 확인됨(Phase 1A). 이제 **"단순 결합 / 제약 선형 모델도 안 되는지"**를 확인. **알파 사냥 아님 — 결합 가설을 *죽이기 위한* 1회 확정 테스트.** kill 조건을 먼저 박는다.

## 0. 불변 규칙 (LOCKED)
- **feature 정의 신규 사냥 금지.** Phase 1A에서 쓴 4개 그대로:
  | feature | 정의(고정) | 부호 |
  |---|---|---|
  | quality | gp/assets (SF1 ARQ, datekey PIT) | 높을수록 good |
  | momentum | 12-1 (t-12→t-1) | 높을수록 good |
  | value | 1/pb (DAILY pb) | 높을수록 good |
  | low-vol | −trailing 126d daily-ret vol | 높을수록(=저변동) good |
- size / liquidity = **control(중립화 대상)**, alpha feature 아님. sector neutralization = on/off 옵션.
- **튜닝·하이퍼파라미터 탐색 금지.** 각 모델은 *기본·정직값 1세트*만. 여러 설정 돌려 best 고르기 = overfit = 금지.
- **금지 모델: XGBoost / LightGBM / CatBoost / 모든 tree-ensemble / LLM-alpha / TSFM / deep model.** (DR-4 결정.)

## 1. 허용 후보 (low-DoF only, 각 1세트)
1. **Simple blend (boring baseline)** — 4 feature를 매월 cross-sectional z-score(winsorize ±3σ)로 표준화 → 동일가중 평균 = composite. **추정 파라미터 0개.**
2. **Constrained linear ranker** — 부호 제약(전부 +)·동일/고정 가중의 선형 결합 랭커. 데이터로 가중 최적화 안 함(=DoF 최소).
3. **Penalized regression** — 다음달 cross-sectional 수익률을 4 z-score feature에 ridge(강한 penalty)로 회귀. **expanding-window chronological OOS**(in-sample 적합·예측 분리), 매월 재적합→다음달 랭킹 예측. 정당한 저DoF(DR-4).

## 2. 포트폴리오·측정
- 매월 composite/예측으로 랭킹 → **long-only Q5 EW**(실거래 가능형) 주측정 + 참고로 long-short Q5-Q1.
- 벤치: **cap-weight(주측정선)** + 1/N EW(apples-to-apples). 비용: Phase 1A와 동일 tier(5/10/15bp, turnover×). base/2x 스트레스.
- 지표: net active return vs CW(연), Rank IC·IC-IR(composite/예측), IC>0%, **subperiod 2016–20 vs 2021–26**, turnover(연), size·sector 귀속(편향 점검), long-only/short 분리.

## 3. ★ PRE-REGISTERED KILL CONDITIONS (결과 보기 전 확정 — goalpost 불변)
**아래 중 하나라도 걸리면 해당 모델 FAIL.** (Phase 1A의 quality보다 *느슨하게 풀지 않는다*.)
1. **net active return vs cap-weight ≤ 0** → FAIL (가장 중요; 실거래 가능 long-only 기준).
2. **recent half 2021–2026 에서 IC-IR < 0.10** → FAIL (decay = 과거유물 거부).
3. **turnover 과도** (연 one-way > 250%) 이고 그걸 상쇄할 net edge 없음 → FAIL.
4. **성과가 2016–2020에만 집중** (2021–26 net active ≤ 0) → FAIL.
5. **size/liquidity/sector 편향으로 설명됨** (중립화 후 net active ≤ 0, 또는 단일 size·sector 분위가 성과의 >60% 설명) → FAIL.
6. **long-only가 안 됨** (long-short만 양수, long-only vs CW 음수) → FAIL.

## 4. 판정 규칙 (사전 박음)
- **3개 모델 중 하나라도 위 6개를 *전부* 통과** → 그 모델 = **Phase 1C 검토 후보** (그래도 **즉시 paper/live 아님**; 추가 다중검정·OOS·robustness 후).
- **3개 모두 ≥1개 kill 발동** → **US simple/linear factor family 종료(TERMINATE).** → 그다음 KR arena 또는 다른 edge source 검토.
- 어떤 경우에도: **no tuning to rescue**(kill 걸렸다고 설정 바꿔 재시도 금지), **no live/paper 자동승격.**

## 5. 산출물
`phase1a/phase1b_lowdof.py` · `reports/Phase1B_lowdof_result.md` · `outputs/phase1b_lowdof_result.csv` · milestone 1줄. (이 프로토콜 파일 = 사전등록 기록; 실행 후 수치만 채우고 kill 조건·판정규칙은 **변경 금지**.)
