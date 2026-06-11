# Phase 2 M7+M8 — Report·Run Module 결과 v0.1 (Phase 2 COMPLETE)
**Date:** 2026-06-11 · **Status:** M7·M8 DONE(PASS) · **Phase 2 Engine Hardening = COMPLETE.** · **Scope:** `engine/report.py`(표준 출력) + `engine/run.py`(config-driven 러너 + 회귀 게이트).

## 한 줄
**config 하나로 과거 7실험을 M1~M7 엔진으로 재실행 → 동결 숫자·verdict 재현 + 표준 리포트 출력**, 키 숨기고 = API-free. **Phase 2 acceptance(회귀 게이트) 통과 = 엔진 하드닝 완료.**

## M7 report.py
표준 md/csv 생성기 — `summary_row`/`write_csv`/`render_md`/`write_md`. 메트릭/kill 계산 0(포맷만).

## M8 run.py (config-driven)
`run_experiment(cfg)` = M1(data)→M2(universe)→M3(features)→M4(cost)→M5(evaluate)→M6(kills)→M7(report) 오케스트레이션. config: `bundle·rank·score(raw|composite|composite_event)·dropna·cost_tier·kill_set·filters·composite_predropna·min_names`.

## ★ 회귀 게이트 (config→동결 재현, .ndl_key 숨기고)
| config | 재현 | verdict |
|---|---|---|
| B2_value | net_ann/ic_ir/turnover **머신정밀도** | DEAD ✅ |
| B3_quality | net_ann 0.0441·ic_ir 0.220·turnover 0.99 **머신정밀도** | **SURVIVE** ✅ |
| B4_momentum | 머신정밀도 | DEAD ✅ |
| B5_lowvol | 머신정밀도 | DEAD ✅ |
| sm_quality | net_cw +0.66·icir 0.157 | FAIL{icir,recent_dead,lowest_liq} ✅ |
| sm_event | net_cw +1.85·icir 0.164 | FAIL{icir,turnover_weak} ✅ |
| sm_blend | net_cw +2.20·icir 0.335 | FAIL{lowest_liq} ✅ |

→ 7/7 동결 숫자·verdict·fired-kill 재현. 표준 리포트 `outputs/engine/regression_report.{csv,md}` 생성.

## 회귀 게이트가 잡은 실제 차이 (가치 증명)
broad 합성신호(phase1b/event)는 **합성 전 컴포넌트 dropna**를 하지만 **b_smallmid는 안 함**(price/adv 필터만, NaN 컴포넌트 허용·z는 skipna). 처음 균일 처리 시 sm_event/blend 불일치(net +2.09 vs +1.85) → `composite_predropna` 플래그로 분리 → 정확 재현. **회귀 게이트가 미세 로직 차이를 강제로 드러냄 = 게이트가 작동.**

## Acceptance (Phase 2 전체)
- M8 회귀: config 하나로 과거 실험 재실행 → 동결 숫자 재현 ✅ (앵커 7개).
- 숫자 바뀌면 실패 = 리팩터 무효 → 7/7 재현이므로 리팩터 유효.
- 전 모듈 API-free(snapshot+TICKERS 동결) ✅.

## engine/ 최종 (8 모듈)
`data·universe·features·cost·evaluate·kills·report·run` + smoke 6개. 입력 전부 캐시(`outputs/raw/` + `manifest.json` + `TICKERS.csv`). 원본 실험 스크립트는 미접촉(legacy 증거 보존).

## 산출물
`engine/report.py·run.py` · `engine/_smoke_run.py` · `outputs/engine/regression_report.{csv,md}` · 본 문서.

## Phase 2 = COMPLETE
검증 엔진(data→universe→features→cost→evaluate→kills→report→run)이 **config-driven으로 동결·재현**됨.

## 다음 (handoff — US-only 고정, 2026-06-11 재정렬)
**프로젝트 scope = US-only 고정.** KR-B0를 next-immediate에서 제거 → **US-Only Completion Roadmap**으로 전환: P3.1 engine final packaging · P3.2 config/run/report workflow 정리 · P3.3 US next-edge protocol **또는** paper-ready simulator(택1, 사전등록) · P3.4 subscription/key housekeeping. 정본 = `US_Only_Completion_Roadmap_v0.1.md`.
**KR = Future Market Adapter (Deferred)** — 엔진 모듈화로 나중에 새 `data` 어댑터+config로 붙일 수 있음. US 완성 전엔 착수 안 함.
