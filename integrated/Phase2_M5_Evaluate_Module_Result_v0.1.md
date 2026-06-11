# Phase 2 M5 — Evaluate Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M5 DONE(PASS) · **Scope:** `phase1a/engine/evaluate.py` — 메트릭 일원화 *만* (순수 L 패널 소비자). universe/feature/cost-tier 정의 0.

## 한 줄
**evaluate.py가 5개 실험의 핵심수치를 재현 — b2b5_broad 20개 수치 머신정밀도(Δ~1e-17), quality/phase1b/event/small-mid 전부 일치.** 키 숨기고 = API-free. Phase 2 숫자재현의 실질 클라이맥스 통과.

## 무엇을 했나
복붙된 evaluate()/stats()(b2b5_broad·quality_quarantine·phase1b·us_event_drift·b_smallmid)를 1모듈로:
- `evaluate_panel(L, scorecol, dropna_cols, cost_tier)` → per-rebal R(ic·q5lo·spread·bench cw/ew·turnover·cost·size-bucket ic).
- `summarize(R, recent_start, cost_mult)` → ic·**IC-IR**·IC>0%·gross/net Q5-Q1·long-only vs CW/1N·turnover·recent(subperiod)·size-bucket.
- `subperiod_icir(R,a,b)`. 입력 L=멤버-월 패널(asof,ticker,score,fwd,mc[,adv]). cost는 cost.py(M4) 호출.

## 검증 (저장 CSV/리포트 대조, .ndl_key 숨기고)
| 실험 | 재현 결과 |
|---|---|
| **b2b5_broad** value/quality/momentum/lowvol | ic·ic_ir·gross·net·turnover **20/20 Δ~1e-17** (사실상 동일 코드경로) |
| **quality quarantine** | IC-IR 0.220 · 2016-20 0.424 / 2021-26 0.046 · long-only vs CW −1.15% · vs 1/N +1.79% ✅ |
| **phase1b A_simple_blend** | icir 0.200 · rec_icir 0.306 · net_cw −2.44% ✅ |
| **event composite** | ic 0.005 · icir 0.069 · rec_icir 0.219 · net_cw −0.90% ✅ |
| **small/mid** quality·event·blend | ic·icir·net_cw 9/9 ✅ (Δ=CSV 2자리 반올림) |

## Acceptance
- 앵커 2~3개(b2b5_broad·quality_quarantine·small/mid) **+ phase1b·event 추가**까지 핵심수치 재현 ✅.
- IC/IC-IR/Q5-Q1(gross·net)/long-only(vs CW·1N)/subperiod/size-bucket/turnover 메트릭 일원화 ✅.
- API-free smoke ✅(키 숨기고).
- b2b5 20수치 머신정밀도 = evaluate.py가 기존과 *동일 코드경로*임을 증명.

## M5에서 안 한 것 (범위 규율)
universe/feature 재정의 0 · cost-tier 정의 0(cost.py 호출) · 새 메트릭 0 · 임계값/kill 판정 0(M6) · API 0.

## 산출물
`phase1a/engine/evaluate.py` · `engine/_smoke_evaluate.py` · 본 문서.

## 다음 (M6)
`kills.py` — 사전등록 kill 조건을 dict 템플릿 + verdict 적용기로(quarantine·phase1b·event·smallmid·broad retest의 kill 세트). evaluate summary를 받아 verdict 재현. 이후 M7 report(표준 md/csv), M8 run.py(config-driven, 회귀 게이트).
