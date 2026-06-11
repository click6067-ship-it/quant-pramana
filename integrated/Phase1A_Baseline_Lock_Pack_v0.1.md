# Phase 1A Baseline Lock Pack v0.1
**Date:** 2026-06-11 · **Status:** Phase 1A baseline sequence COMPLETE (locked) · **Scope:** US-core, S&P500 PIT, real Sharadar data

## Final Decision (박음)
1. **B0/B1 — data & benchmark machinery = PASS.** self-built S&P500 cap-weight TR이 실제 SPY와 **corr 0.998·연차 +0.55%p**. PIT 멤버십(future-leakage 차단)·survivorship(제거213+폐지119 보존)·배당/TR·재현성(동결 hash) 전부 검증. 1/N(B1)도 동일 유니버스 생성.
2. **B2~B5 — simple S&P500 large-cap factors show NO robust signal.** Rank IC ≈ 0 (|IC|<0.01, IC-IR<0.05; value −0.005 / quality +0.003 / momentum +0.009 / lowvol −0.006). **이는 비용·다중검정 *전* 수치** → 보정하면 더 나빠질 뿐. momentum이 그나마 덜 약하나 노이즈.
3. **Decision: simple factor sleeves = DO NOT PROMOTE.** 튜닝·비틀기 금지(=overfit 경로). 
4. **No tuning / no overfit.** B2~B5를 더 만지지 않는다.
5. **Next recommended = broad-universe retest BEFORE Phase 1B** — 단 *비용 포함* + *사전 kill 조건* 필수(아래).

## Artifacts (locked)
| 항목 | 경로 |
|---|---|
| B0/B1 결과 | `phase1a/reports/B0broad_B1_sp500_result.md` (data_hash 003e5039) |
| B2~B5 결과 | `phase1a/reports/B2_B5_factor_result.md` · `outputs/b2b5_factor_ic.csv` |
| Milestones | `phase1a/registry/phase1a_milestones.csv` (B0/B1 PASS · B2~B5 MEASURED) |
| Raw snapshot (S&P500 subset) | `phase1a/outputs/raw/` SEP·DAILY·SF1_ARQ·SP500_membership·SFP_SPY + `HASHES.txt`(sha256) |
| Code/config | `phase1a/b0b1_sp500.py · b2b5_factors.py · b0_benchmark_sanity.py` |
| 지수 series | `phase1a/outputs/b0_sp500_capweight.csv · b1_sp500_equalweight.csv` |

## Known limitations (정직)
- **유니버스 = S&P500 대형주 only**(2016~2026, 1구간). 대형주 팩터 프리미엄은 차익거래로 희석 — 팩터 약한 게 예상됨.
- **B2~B5는 비용 미반영 순수 Rank IC** (신호 존재 여부만; tradeable 평가 아님).
- 멀티클래스 종목 일부 DAILY 결측(예: GOOG/NWS) → cap-weight서 자연 제외.
- 데이터 license = 구독 중 사용. 해지 후 이 snapshot으로 추가 연구는 약관 회색지대.

## Next round (재구독 시) — kill 조건 미리 박기
- **broad-universe retest**: US top 1000~3000 by marketcap + 유동성필터, **same B2~B5 + 비용·turnover 포함**.
- **kill 조건(사전):** 비용 차감 후 어떤 sleeve도 IC-IR이 의미수준(예: 다중검정 보정 후 유의) 못 넘기면 → 단순팩터 경로 종료, Phase 1B(저-DoF challenger)로. *무한 탐색·튜닝 금지.*
- 정직한 사전확률: 비용 후 robust 엣지 없을 가능성 높음. broad retest는 *한 번의 깨끗한 검정*이지 알파 사냥 아님.

## Cancellation readiness
- 백업 검증 완료(2026-06-11): raw 5파일 + HASHES.txt + 리포트/outputs/코드 전부 존재. → **구독 해지 안전.**
- 해지 후: API key revoke/regenerate(traceback 노출) → `.ndl_key` 교체/삭제.
