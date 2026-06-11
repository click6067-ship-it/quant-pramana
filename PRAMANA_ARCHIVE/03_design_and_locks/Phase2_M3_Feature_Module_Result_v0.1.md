# Phase 2 M3 — Feature Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M3 DONE(PASS) · **Scope:** `phase1a/engine/features.py` — 동결 6 feature 정의 *만*. universe/cost/portfolio/evaluate 0.

## 한 줄
**6개 feature(value·quality·momentum·lowvol·event·blend)가 기존 inline 정의와 byte-perfect 1:1 동치**(broad+small/mid, max|Δ|=0.00e+00), 키 숨기고 실행 = API-free. 정의·튜닝 0 변경.

## 무엇을 했나
복붙된 feature 계산(b2b5_broad·quality_quarantine·us_event_drift·phase1b·b_smallmid)을 1모듈로 동결:
- **raw 매트릭스(universe-독립)**: `value`=1/pb · `quality`=gp/assets PIT(datekey≤asof,last) · `momentum`=12-1 · `lowvol`=-126d vol.
- **event sub-signals**: gp/assets·revenue·eps·grossmargin YoY(shift4, ffill PIT).
- **composite(per-rebal 멤버 z-mean)**: `event`=4 YoY z-mean · `blend`=4 raw z-mean. `zscore`=winsor±3(동결 z()).
- `REGISTRY` = frozen definitions table.

## 검증 (verbatim-inline과 동치, .ndl_key 숨기고)
| 대상 | broad | small/mid |
|---|---|---|
| value/quality/momentum/lowvol 매트릭스 | ✅ 동일 (126×2973) | ✅ 동일 (126×4504) |
| event 4 YoY 서브시그널 | ✅ 동일 | ✅ 동일 |
| event composite 멤버레벨 | ✅ **154,332 멤버-월 · max\|Δ\|=0** | (함수 동일) |
| blend composite 멤버레벨 | ✅ **162,169 멤버-월 · max\|Δ\|=0** | (함수 동일) |

coverage(첫 12개월 워밍업 제외): broad value 70.0%·quality 87.2%·momentum 67.4%·lowvol 68.6% / small/mid value 62.2%·quality 84.2%·momentum 59.3%·lowvol 60.7%.

## Acceptance 대조 (6/6)
| # | 조건 | 결과 |
|---|---|---|
| 1 | B2~B5 broad feature table 동일 재현 | ✅ raw 매트릭스 1:1 |
| 2 | quality quarantine input 재현 | ✅ quality 매트릭스 1:1 |
| 3 | event drift input 재현 | ✅ event subs + composite 1:1(max\|Δ\|=0) |
| 4 | small/mid B input 재현 | ✅ small/mid 매트릭스 1:1 |
| 5 | coverage/missing rate 동일 | ✅ 보고됨 |
| 6 | API-free smoke 통과 | ✅ 키 숨기고 PASS |

## M3에서 안 한 것 (범위 규율)
새 feature 0 · 정의/부호/PIT 로직 변경 0 · 튜닝 0 · universe/cost/portfolio/evaluate 0 · API 0.

## 산출물
`phase1a/engine/features.py`(+`REGISTRY`) · `engine/_smoke_features.py` · 본 문서.

## 다음 (M4)
`cost.py` — 동결 tier 비용 모델(broad 5/10/15bp by mktcap · small/mid 25/45/75bp by ADV) + base/2x/3x. quality_quarantine·b2b5_broad·b_smallmid의 cost_oneway/ctier 통합, 동결 tier 재현.
