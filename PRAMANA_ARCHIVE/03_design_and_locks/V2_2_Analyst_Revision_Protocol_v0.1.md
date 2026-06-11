# v2.2 — Analyst Estimate Revision — Full Validation Protocol v0.1 (PRE-REGISTERED · CONTINGENT)
**Date:** 2026-06-11 · **Status:** **사전등록(kill 먼저)** · **CONTINGENT — 미실행.** 실행 조건 ① V2.1 2018 부호 스크린 PASS ② Zacks 전체 history 구독(가격 감당) 확정. · **Scope:** US-only.
**한 줄:** v1이 못 가진 *진짜 consensus revision*(obs_date PIT)으로 estimate-revision momentum이 **비용 후·최근 절반에도 남는가** 1회 검증. 데이터축 전환의 첫 full kill-test.

## edge hypothesis
애널리스트 컨센서스 *상향/하향 revision*은 정보가 점진 반영(under-reaction) → revision↑ 종목이 이후 초과수익. 문헌상 가장 견고한 공개 anomaly 중 하나. v1 event/surprise *proxy*는 죽었으나, 이건 *진짜 revision 타임라인*(obs_date)이라 다른 데이터.

## 사용 데이터 (Zacks 구독 전제 — 미보유)
- `ZACKS/EEH` (Earnings Estimates History) — **obs_date(PIT)**·eps_cnt_est·eps_cnt_est_rev_up/down·eps_mean_est. 전체 2016–2026.
- `ZACKS/FC` (보고 EPS, actual) — SUE 보조(2차).
- 기존 캐시: `broad_SEP`(가격)·`DAILY_all`(marketcap·비용/유동성)·`broad_universe_top1500`(PIT, 재조정 금지).

## 신호 정의 (고정 — V2.1 스크린과 동일, 사냥/튜닝 0)
- **primary** = `(eps_cnt_est_rev_up − eps_cnt_est_rev_down) / max(eps_cnt_est, 1)`, **front quarter**(per_type='Q', per_end_date ≥ obs_date 중 최근), **PIT as-of obs_date**.
- 월말 리밸런스 시점의 *최신 obs_date* 신호 사용(no look-ahead). raw rev_up−rev_down·dispersion·SUE는 *참고/2차*만(primary 1개로 판정).

## universe / cost / benchmark (엔진 동결 재사용)
- universe: top-1500 PIT(기존, 재조정 금지). cost: marketcap tier 5/10/15bp round-trip(cost.py). benchmark: cap-weight + 1/N. price≥$5.

## 측정 (engine evaluate)
Rank IC·IC-IR·IC>0% · gross/net Q5-Q1 · long-only Q5 vs CW·1/N · **subperiod 2016-20/2021-26** · 유동성(marketcap) 버킷 · turnover.

## ★ PRE-REGISTERED KILL CONDITIONS (결과 전 확정 — 변경 금지)
1. net active(long-only vs 벤치) ≤ 0 → FAIL
2. 2021–2026 사망(recent net ≤ 0 또는 recent IC-IR < 0.10) → FAIL
3. IC-IR < 0.20 → FAIL
4. 2x cost(round-trip)에서 사망 → FAIL
5. 유동성 하위 버킷에만 존재 → FAIL
6. long-only로 안 됨(long-short만 +) → FAIL

## 판정
6개 전부 통과 → v3 quarantine 심화 후보(즉시 paper/live 아님). ≥1 kill → revision 축 종료/보류. no tuning to rescue · no live/paper.

## 금지 (LOCKED)
파라미터/window 튜닝 0 · 신호 재정의 0 · universe 재조정 0 · KR/새시장 0 · XGBoost/LLM/TSFM 0 · 여러 신호 동시 0(primary 1개).

## 실행 (엔진 config — 새 스크립트 남발 금지)
revision은 *느린 cross-sectional*(PEAD의 event-time 아님) → **run.py 월-캘린더 config에 맞음.** 추가물: ① `engine/features.py`에 동결 `revision` feature(EEH obs_date as-of) ② `engine/configs.py`에 `revision_ts` named config(bundle=broad·rank(1,1500)·score raw revision·cost marketcap·kill_set=event류 6-kill) ③ ZACKS 로더는 `engine/data.py`에 어댑터. → `reports/V2_2_revision_result.md`.

## 선행(실행 전 필수)
1. V2.1 2018 부호 스크린 = PASS (`reports/V2_1_zacks_2018_rapid_screen.md`).
2. Zacks EEH+FC 구독 가격 확인 → 감당 가능 → 구독.
둘 중 하나라도 NO → 이 프로토콜 미실행(축 HOLD/CLOSE).
