# Phase 2 M6 — Kills Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M6 DONE(PASS) · **Scope:** `phase1a/engine/kills.py` — 사전등록 kill 조건 템플릿 + verdict 적용기 *만*. 메트릭 계산 0(evaluate 결과 소비).

## 한 줄
**5개 kill-set이 11개 실험 verdict + fired-kill 집합을 정확히 재현**(broad 4슬리브·quarantine·phase1b·event·smallmid 3신호), 키 숨기고 = API-free. 임계값·kill 정의 0 변경.

## 무엇을 했나
복붙된 kill 로직(b2b5_broad·quality_quarantine·phase1b·us_event_drift·b_smallmid)을 1모듈로 동결:
- `KILL_SETS` = 5개 사전등록 세트(broad_retest 4 · quality_quarantine 6 · phase1b 6 · event 6 · smallmid 8). 각 kill=(key, label, predicate(m)).
- `apply(name, m)` → (fired_keys, labels, verdict_word, passed). m=evaluate summary(+실험별 extra: sn_net_cw·net2·lo/hi_liq·s1/s2·sector_max).

## 검증 (verdict+fired 집합 대조, .ndl_key 숨기고)
| 실험 | verdict | fired kills | 일치 |
|---|---|---|---|
| broad value | DEAD | net_le0·icir_lt20 | ✅ |
| broad **quality** | **SURVIVE** | (없음) | ✅ |
| broad momentum | DEAD | icir_lt20 | ✅ |
| broad lowvol | DEAD | net_le0·icir_lt20·small_concentration | ✅ |
| quality quarantine | FAIL | longonly_cw_le0 | ✅ |
| phase1b A_simple_blend | FAIL | net_cw·concentrated_early·sector_neutral·longonly | ✅ |
| event composite | FAIL | net_cw·cost2x·longonly·sector_neutral | ✅ |
| small/mid quality | FAIL | icir·recent_dead·lowest_liq | ✅ |
| small/mid event | FAIL | icir·turnover_weak | ✅ |
| small/mid blend | FAIL | lowest_liq | ✅ |

11/11 verdict+집합 일치.

## Acceptance
- 각 protocol의 kill 세트 그대로 적용 → verdict 재현 ✅. (goalpost 불변: predicate가 원본 boolean 로직과 1:1.)
- API-free smoke ✅.

## M6에서 안 한 것 (범위 규율)
새 kill 0 · 임계값 변경 0 · 메트릭 계산 0(evaluate.py 호출) · API 0.

## 산출물
`phase1a/engine/kills.py` · `engine/_smoke_kills.py` · 본 문서.

## 다음 (M7)
`report.py` — 표준 md/csv 생성기(기존 리포트 포맷 호환). 이후 M8 `run.py`(config-driven 러너) + 회귀 게이트(config 하나로 과거 실험 재실행 → 동결 숫자 재현). M1~M6이 전부 재현 PASS라 M7/M8은 조립·출력 단계.
