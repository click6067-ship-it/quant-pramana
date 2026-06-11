# V2.1 — Analyst Estimate / Revision Data Rapid Gate
**Date:** 2026-06-11 · **목표:** 알파 아님 — **PIT analyst estimate/revision history를 싸게·코드로 받을 수 있나** 1회 판정. 결제 0 · 새 실험 0.
**한 줄 판정:** **GO(구조) / HOLD(가격).** 정확히 필요한 PIT revision 데이터가 **Nasdaq Data Link Zacks `ZACKS/EEH`**에 존재 — *내 기존 .ndl_key로 접근됨* — 단 **무료는 2018 샘플 1년뿐**, 전체 history는 별도 Zacks 구독(가격 미확인·결제금지).

## 후보 3개 probe 결과
| 벤더 | 코드로 샘플 | revision/obs date | 5년+ history | 판정 |
|---|---|---|---|---|
| **NDL Zacks `ZACKS/EEH`** | ✅ **기존 키로 됨** | ✅ **`obs_date`(PIT 관측일)** | ⚠️ **무료=2018만**, 전체는 유료 | **GO 구조 / HOLD 가격** |
| FMP | ❌ free key 필요(가입) | ? (doc상 estimates/ratings 있으나 PIT revision 불확실) | ? | HOLD(가입 후 재확인) |
| Finnhub | ❌ free key 필요(가입) | ? (EPS estimate/surprise 있으나 PIT 불확실) | ? | HOLD(가입 후 재확인) |

## ★ Zacks `ZACKS/EEH` (Earnings Estimates History) — 필드 (필요한 것 다 있음)
- `obs_date` = **관측일(시장이 그날 알던 consensus) = PIT revision 타임스탬프** ✓✓ (가장 중요한 필드, FAIL 회피 조건)
- `eps_mean_est·eps_median_est·eps_high_est·eps_low_est·eps_std_dev_est` = 컨센서스 값 + dispersion ✓
- `eps_cnt_est` = 애널리스트 수 ✓ · **`eps_cnt_est_rev_up`·`eps_cnt_est_rev_down`** = 상/하향 revision 수(= revision-momentum 신호 자체) ✓✓
- `per_end_date·per_type·per_fisc_year/qtr·per_cal_year/qtr` = estimate/fiscal 기간 ✓ · `ticker` = 매핑 ✓ (AAPL 533·MSFT 447·JPM 420·XOM 528행)
- actual(보고 EPS, SUE용) = **`ZACKS/FC`**(eps_basic_consol 등) 별도 테이블에 존재 ✓

## 캡 확인 (왜 HOLD인가)
`obs_date gte 2019` / `2016–17` / `2022` 요청 → **전부 0행.** 무료 = **2018 한 해 publisher 샘플.** 2016–2026(5년+) 검증용 전체 history = **별도 Zacks 구독 필요**(가격 미확인 — 결제 금지라 직접 확인 안 함).

## 판정 (사전 기준 대조)
| GO 기준 | 결과 |
|---|---|
| PIT revision/update date 있음 | ✅ `obs_date` |
| 5년+ history | ⚠️ 무료=2018만 / 유료=가능(미확인) |
| API batch 가능 | ✅ NDL get_table(Sharadar와 동일) |
| top-1500 매핑 | ✅ ticker(대형주 확인) |
| 가격 감당 | ❓ **미확인(결제금지)** |

→ **이번이 데이터축 후보 중 처음으로 구조·PIT 바를 깨끗이 통과.** v1의 정확한 공백(진짜 consensus revision)을 메우는 데이터가 *친숙한 플랫폼(NDL)·동일 키 방식*으로 존재. 막힌 건 *가격 한 줄*뿐.

## 다음 (권고, 결제 전 — 속도/저위험)
1. **(무료·즉시) 2018 샘플로 rapid IC 스크린** — `rev_up − rev_down`(또는 eps_mean_est 변화) → forward return 부호만 1회. 1년·1레짐이라 결론 아님이지만, **부호도 안 맞으면 유료 history 살 필요 없음**(결제 전 zero-cost 디리스크).
2. 부호가 말이 되면 → **Zacks EEH+FC 구독 가격 확인**(NDL Zacks 데이터 페이지) → 감당되면 full 사전등록 kill-test.
3. 부호 안 맞거나 가격 과함 → 이 축 HOLD/CLOSE, FMP/Finnhub는 가입 후에야 재확인 가치.

**규율:** 데이터 접근 안 됨→실험 안 함 · PIT 불명확→실험 안 함 · 결제 전 rapid screen 먼저.
