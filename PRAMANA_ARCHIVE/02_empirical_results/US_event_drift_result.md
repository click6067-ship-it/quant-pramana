# US Event / Earnings Drift — 결과 (사전등록 1회 kill-test)

**날짜:** 2026-06-11 · **데이터:** broad top-1500 PIT, 2016–2026, 110개월 · **프로토콜:** `integrated/US_Event_Earnings_Drift_Experiment_Protocol_v0.1.md` (결과 전 박음) · **튜닝 0.**
**이벤트:** SF1 `datekey`(PIT 공시일) · **신호:** *레벨* 아닌 *변화/서프라이즈 proxy* (gp/assets YoY·revenue YoY·eps YoY·grossmargin YoY) + filing freshness. 진짜 PEAD(가격반응)·analyst surprise 아님(정직 한계).

## 한 줄 결론
**FAIL → US event(이 신호군) 종료.** 단 — **level 팩터와 달리 decay하지 않았다**(최근 절반이 오히려 강함). 그래도 **cap-weight 벤치를 long-only로 못 이긴다**(또 그 벽).

## 결과

| 신호 | Rank IC | IC-IR | 2021–26 IC-IR |
|---|---|---|---|
| S1 gp/assets YoY | +0.0031 | +0.043 | **+0.215** |
| S2 revenue YoY | +0.0011 | +0.010 | −0.123 |
| S3 eps YoY | +0.0054 | +0.078 | **+0.226** |
| S4 gross-margin Δ | +0.0077 | +0.128 | +0.185 |
| **EVENT composite** | +0.0050 | +0.069 (t≈0.72) | **+0.219** |

EVENT composite 포트폴리오:
- net active vs CW: **1x −0.90%/yr · 2x −1.17%/yr** (음수)
- gross vs CW −0.64% / **vs 1/N EW +2.46%**
- subperiod net vs CW: 2016–20 **−2.92%** / 2021–26 **+0.49%** (IC-IR +0.219)
- sector-neutral net vs CW: **−1.49%** · turnover 265%/yr
- freshness(≤63일 PEAD-lite 창) composite IC-IR +0.080, 최근 절반 +0.170

## 판정 (사전등록 규칙 — goalpost 불변)
**KILLS 4개 발동:** net active vs CW≤0 · 2x cost net≤0 · long-only vs CW 음수 · sector중립화후 net≤0.
→ **US event 신호군 종료.** no tuning to rescue, no live/paper.

## ★ 메타 패턴 (3개 신호군 공통 — 중요)
| 신호군 | vs 1/N EW | vs cap-weight (실측정선) |
|---|---|---|
| Phase 1A level (quality) | +1.79% | **−1.15%** |
| Phase 1B 결합 | +1.13~2.86% | **−0.7~−3.6%** |
| Event/surprise | **+2.46%** | **−0.90%** |

**모든 신호군이 1/N은 이기지만 cap-weight long-only는 못 이긴다.** 일관된 killer = **cap-weight 벤치 = 2016–2026 메가캡 지배 레짐**. 즉 cross-sectional EW 틸트는 *신호와 무관하게* 이 10년 cap-weight 인덱스에 구조적으로 진다(이기려면 이미 지배적인 메가캡을 더 담아야 함 = 틸트의 반대).

추가로 — **event/surprise 신호는 level과 달리 decay하지 않음**(최근 절반 IC-IR +0.219 > 전체 +0.069). 정보 방향은 맞으나 *cap-weight 벽*과 *비용*이 먹어버림.

## 다음
사전등록대로 A 종료 → B(US 소형 cost-first) → C(KR feasibility). **단 메타 패턴 때문에 기계적 B 진행 전 전략 재검토 권고**(아래 대화). 벤치/레짐/접근(EW 틸트 vs cap-weight) 자체가 진짜 제약일 수 있음.
