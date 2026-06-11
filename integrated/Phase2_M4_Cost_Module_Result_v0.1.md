# Phase 2 M4 — Cost Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M4 DONE(PASS) · **Scope:** `phase1a/engine/cost.py` — 동결 비용 tier + turnover *만*. universe/feature/portfolio/evaluate 0.

## 한 줄
**cost.py가 기존 net/turnover/cost-stress를 머신 정밀도로 재현**(broad quality Δ=9e-17, smallmid 1x/2x/3x CSV 일치), 키 숨기고 = API-free. tier·turnover 정의 0 변경.

## 무엇을 했나
복붙된 비용 로직(b2b5_broad.cost_bps · quality_quarantine.ctier · b_smallmid.cost_oneway)을 1모듈로 동결:
- `tier_marketcap_bps`: marketcap tercile **5/10/15bp** one-way (broad).
- `tier_adv_bps`: ADV tercile **25/45/75bp** one-way (small/mid, 보수적).
- `turnover_oneway`: |cur △ prev|/(2·max(|cur|,1)), 최초=1.0.
- `longshort_cost`/`longonly_cost`: per-rebal 비용항(1x/2x/3x = × mult).

## 검증 (저장 CSV 대조, .ndl_key 숨기고)
| 항목 | 재현 | 기존 | Δ |
|---|---|---|---|
| tier 동치 (mc·adv·turnover) | ✅ | inline | exact |
| **broad B3 quality net_ann (1x)** | +0.04410 | +0.04410 | **9e-17** |
| **broad B3 quality turnover_ann** | +0.99230 | +0.99230 | **0** |
| quality cost-stress 1x/2x/3x | +4.41/+4.19/+3.98% | 리포트 동일 | <6e-4 |
| small/mid quality net_cw 1x/2x | +0.66/+0.00% | CSV +0.66/+0.00 | 반올림(2자리) |
| small/mid event net_cw 1x/2x | +1.85/+0.31% | CSV +1.85/+0.31 | 반올림 |
| small/mid blend net_cw 1x/2x | +2.20/+0.74% | CSV +2.20/+0.74 | 반올림 |
| small/mid 3x net_cw | quality −0.65·event −1.24·blend −0.73% | 리포트 동일 | exact |

(small/mid Δ~5e-3%는 저장 CSV가 소수 2자리 반올림이라 생긴 표시오차 — 실제 계산 경로는 동일.)

## Acceptance 대조 (5/5)
| # | 조건 | 결과 |
|---|---|---|
| 1 | B2B5_broad net/turnover 재현 | ✅ Δ=9e-17 / 0 |
| 2 | quality quarantine 1x/2x/3x stress 재현 | ✅ +4.41/+4.19/+3.98 |
| 3 | small/mid B 1x/2x/3x net 재현 | ✅ 3신호 일치 |
| 4 | API-free smoke 통과 | ✅ 키 숨기고 PASS |
| 5 | 결과 문서 | ✅ 본 문서 |

## M4에서 안 한 것 (범위 규율)
새 비용모델 0 · spread/impact 새 추정 0 · tier 변경 0 · universe/feature/portfolio/evaluate 0 · API 0.

## 산출물
`phase1a/engine/cost.py`(+`REGISTRY`) · `engine/_smoke_cost.py` · 본 문서.

## 다음 (M5)
`evaluate.py` — IC·IC-IR·IC>0% · Q5-Q1(gross/net) · long-only vs CW/1N · subperiod(2016-20/2021-26) · size/liquidity 버킷 · turnover. **여기가 메트릭 일원화 + 7 리포트 핵심수치 재현의 핵심 구간**(M3 feature + M4 cost를 조립). 이후 M6 kills · M7 report · M8 run.py(config-driven).
