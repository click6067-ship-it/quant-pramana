# Phase 2 M2 — Universe Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M2 DONE(PASS) · **Scope:** `phase1a/engine/universe.py` — PIT universe 생성 *만*. feature/signal/portfolio/cost 0.

## 한 줄
**3개 앵커 universe(SP500 PIT · top-1500 · small/mid 1001–3000) 전부 기존과 byte-identical 재현, 키 숨긴 채 실행 = API-free 확정.** 복붙 3곳(build_broad_universe·build_smallmid_universe·b0b1_sp500 멤버십)을 1모듈로 통합.

## 무엇을 했나 (consolidation, 범위 좁게)
`engine/universe.py`: `sp500_pit`(added/removed 역재생, b0b1과 동일 로직) · `rank_universe(lo,hi)`(월말 marketcap rank PIT — top-1500=1..1500, small/mid=1001..3000 공통화) · `ticker_flags`(common/delisted, 동결 TICKERS). 입력 전부 캐시(SP500_membership·DAILY_all·TICKERS) → **ndl import 0**.

## 검증 (TICKERS·DAILY 캐시만, .ndl_key 숨기고 실행)
| 앵커 | 재현 결과 |
|---|---|
| **A. SP500 PIT** | ever-members **712 ✅**(target 712) · 월별 median **505**(≈500) · survivorship removed 213·delisted 119 보존 |
| **B. top-1500** | union **2973 ✅** · (asof,ticker) 집합 일치 Δ0 · **hash new==ref `8fd7ae879a9b937b`** |
| **C. small/mid 1001–3000** | union **4504 ✅** · 집합 일치 Δ0 · **hash new==ref `d9227d28d76bf34a`** |

→ 3개 모두 기존 universe와 *멤버십 집합 완전 일치*. 숫자 안 바뀜.

## Acceptance 대조 (8/8)
| # | 조건 | 결과 |
|---|---|---|
| 1 | SP500 PIT 월별 종목수 일치 | ✅ median 505 |
| 2 | 712 ever-members 재현 | ✅ |
| 3 | top-1500 union 재현 | ✅ 2973 |
| 4 | small/mid 1001–3000 월별 종목수 재현 | ✅ 2000/월·union 4504 |
| 5 | delisted/removed 보존 재현 | ✅ removed 213·delisted 119 |
| 6 | 현재리스트 과거 소급 없음 | ✅ members_asof 구조적·PIT marketcap rank |
| 7 | API key 없이 실행 | ✅ .ndl_key 숨기고 PASS |
| 8 | universe output hash 생성 | ✅ new==ref |

## M2에서 안 한 것 (범위 규율)
feature/signal/portfolio/cost 계산 0 · 새 실험 0 · KR 추상화 0 · 범용 플랫폼화 0. **딱 universe 생성 로직 복붙 제거 + 같은 universe 재현.**

## 산출물
- `phase1a/engine/universe.py`
- `phase1a/outputs/engine/{sp500_pit,broad_top1500,smallmid_1001_3000}.csv` (재현본; 기존 원본은 미접촉)
- 본 문서

## 다음 (M3)
`features.py` — 동결 feature registry(value 1/pb · quality gp/assets · momentum 12-1 · lowvol · event YoY composite · blend). **정의·부호·PIT 로직 잠금**, 각 feature 단위테스트(정의 1:1). 여기서부터 숫자 재현이 본격 테스트되는 구간(M3/M5).
