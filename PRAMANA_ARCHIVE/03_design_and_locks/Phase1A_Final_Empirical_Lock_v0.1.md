# Phase 1A — Final Empirical Lock v0.1
**Date:** 2026-06-11 · **Status:** Phase 1A 실증 종료(LOCKED) · **Scope:** US-core, Sharadar real data, S&P500 PIT + broad top-1500 PIT (2016–2026)

## 한 줄
정보는 조금 있다. **하지만 거래 가능한 standalone edge는 아니다.** — 이게 Phase 1A의 가장 정직한 결론.

## Final Decision (박음)
1. **B0/B1 — data & benchmark machinery = PASS.** 자작 S&P500 cap-weight TR이 실제 SPY와 **corr 0.998·연차 +0.55%p**. PIT 멤버십(future-leakage 차단)·survivorship(제거+폐지 보존)·배당/TR·재현성(동결 hash) 검증. 1/N(B1) 동일 유니버스 생성.
2. **B2~B5 broad cost-aware retest — value / momentum / low-vol = DEAD.** 사전등록 kill 조건대로 종료(momentum net +7.6%나 IC-IR 0.10 + turnover 301% → 규칙대로 DEAD, goalpost 불변).
3. **B3 quality(gp/assets) — quarantine 5-test 결과 standalone FAIL.**
   - decay: 2016–20 IC-IR **0.42** → 2021–26 **0.046**(동전), 2025·2026 IC 음수.
   - long-only vs cap-weight 벤치 **−1.15%/yr (IR −0.16)** = 실제 측정선서 인덱스에 짐.
   - 단 layered: long-SHORT spread는 cost robust(+4.4%, 공매도 전제→솔로 불가), long-leg vs 1/N은 **+1.79%(IR 0.39)** → **noise는 아님**. 다중검정 Bonferroni p≈0.030 표면통과지만 거의 전부 2016–20산.
4. **Simple single-factor family = TERMINATED** (직접 거래 standalone 전략으로서). 4개 모두 정리.
5. **quality = Phase 1B의 weak input feature 후보까지만 허용.** 단독 거래·튜닝·재정의 금지.
6. **No live / no paper trading (전 케이스).** **No tuning / no overfit.** B2~B5 더 만지지 않는다.

## 의미
검증 프로토콜이 의도대로 작동 — **틀린 방향을 자신있게 만들기 전에 죽였다.** factor-decay / Alpha Illusion / post-publication 소멸 prior-art와 정합. 미국 중대형에서 단순 single-factor 직접거래 알파는 안 보인다.

## Next (확정)
**KR arena 전환 *보류*.** 먼저 미국에서 **Phase 1B low-DoF 결합 가설**을 닫는다 — "단순 결합/제약 선형 모델도 안 되는지"를 확인하기 전에 KR로 넘어가면 "결합했으면 됐을 수도"가 남는다. Phase 1B는 *알파 사냥이 아니라 결합 가설을 죽이는 1회 사전등록 테스트*. → `Phase1B_LowDoF_Challenger_Protocol_v0.1.md`.

## Phase 1B 결과 (2026-06-11, 위 테스트 실행 완료)
**3개 저DoF 모델(simple blend / constrained rank / ridge OOS) 전부 FAIL → US simple/linear factor family TERMINATE.** net active vs cap-weight 전부 음수(−2.4 / −3.6 / −0.7%/yr), OOS ridge IC-IR 0.014(2021–26 −0.099)=정직 fit 시 edge無, 최근 절반 전부 음수. 결합이 long-leg를 못 살림(quality 단독 +1.79% → blend +1.13% 희석). **결론: 미국 중대형에서 단순/선형/결합 패러다임 닫힘.** → `reports/Phase1B_lowdof_result.md`. **다음 = KR arena 또는 다른 edge source 검토.**

## Artifacts (locked)
| 항목 | 경로 |
|---|---|
| B0/B1 | `phase1a/reports/B0broad_B1_sp500_result.md` (data_hash 003e5039) |
| B2~B5 broad | `phase1a/reports/B2B5_broad_result.md` · `outputs/b2b5_broad_result.csv` |
| B3 quarantine | `phase1a/reports/B3_quality_quarantine_result.md` |
| Universe(PIT) | `phase1a/outputs/broad_universe_top1500.csv` (diagnostics PASS) |
| Milestones | `phase1a/registry/phase1a_milestones.csv` |
| Raw snapshot | `phase1a/outputs/raw/` (SEP·DAILY·SF1·SP500·SPY + `HASHES.txt` sha256) |
| Code | `phase1a/{b0b1_sp500,b2b5_broad,quality_quarantine,build_broad_universe}.py` |

## Known limitations (정직)
- 1 region(US) · 1 history(2016–2026, GFC·COVID 외 단일 레짐) · top-1500 = 중대형(딥소형 아님; volume 미pull→liquidity는 marketcap proxy).
- 데이터 license = 구독 중 사용. 해지 후 이 snapshot으로 추가 연구는 약관 회색지대 → Phase 1B는 구독 윈도우(잔여 ~29일) 내 완료.
