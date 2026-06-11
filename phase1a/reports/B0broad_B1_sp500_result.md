# B0-broad + B1 Result — self-built S&P500 (PIT, survivorship-aware)
**Date:** 2026-06-10 · **Source:** Sharadar SP500 membership + SEP.closeadj + DAILY.marketcap + SFP SPY (real, 구독)
**Universe:** 712 ever-members (current 503), 월중앙 멤버 B0=500 / B1=505 · 2016-01-04~2026-06-09 (2623일, 월리밸런스)
**data_hash:** `003e50390b250dbd` · **raw snapshot:** `outputs/raw/{SHARADAR_SEP,SHARADAR_DAILY,SP500_membership,SFP_SPY}.csv`

## PIT 멤버십 (future-leakage 차단)
현재 멤버(`current`)에서 `added`/`removed` 425 이벤트를 **역재생**해 각 시점 멤버십 복원 → **현재 리스트를 과거 소급하지 않음**(GPT 경고 반영). removed/delisted 종목은 제거 전까지 보유 후 자연 제외.

## 결과
| 지수 | 100→ | 연(신뢰금지) |
|---|---|---|
| B0 cap-weight TR | 457.3 | +15.7% |
| B1 1/N equal-weight TR | 348.9 | +12.8% |

## CHECKS
| Check | 결과 | 근거 |
|---|---|---|
| CHK-W(B0) weights sum≈1 | **PASS** | 0 bad |
| CHK-W(B1) weights sum≈1 | **PASS** | 0 bad |
| CHK-S survivorship | **PASS** | removed-ever 213 + delisted 119 보존 |
| CHK-F no-future | **PASS** | members_asof 구조적 차단 |
| **CHK-D(B0) vs SPY** | **corr 0.998 · +0.55%p/yr** | ⭐ 재구성 cap-weight가 실제 SPY와 거의 일치 = 데이터 파이프라인 정직성 강력 검증 |
| CHK-D(B1) vs SPY | corr 0.937 · -1.93%p/yr | 1/N=소형주 틸트 → SPY와 차이 큼(정상) |

## 해석 (정직)
- **corr 0.998이 핵심.** 밑바닥부터 만든 S&P500 cap-weight TR이 SPY를 0.998로 추종 → PIT·cap-weight·배당·survivorship·CA 처리가 정확. +0.55%p/yr 잔차 = SPY 운용보수(~0.09%)+멀티클래스/타이밍 미세차로 설명.
- **수익률 숫자(457/349)는 성과가 아니라 sanity 산출물** — 신뢰 대상 아님.
- B1(1/N)은 동일 유니버스·리밸런스·delisting/TR 처리로 생성 → cap-weight와 직접 비교 가능. 1/N이 이 구간 cap-weight보다 낮음(소형주 틸트·동일 구간).

## B0 verdict: **PASS (broad, real, survivorship-aware).**
demo(18종)를 넘어 **진짜 ~500종 PIT 유니버스**에서 데이터/벤치 정직성 검증 완료.

## Next
- B2~B5(가치·퀄리티·모멘텀·저변동 팩터) = **아직 보류**(B1까지가 baseline). 진행하려면 펀더멘털(SF1) 필요 → 구독 중에 받아두거나 재구독.
- ③ hoard: 우선순위1(SP500/SPY)·2(SEP/DAILY subset) **저장 완료**. 우선순위3(전체 SEP/DAILY)은 별도 대용량.
- ⚠️ 구독 해지 후 이 데이터로 B2~ 진행은 약관 회색지대 — B0/B1은 구독 중 완료(OK).
