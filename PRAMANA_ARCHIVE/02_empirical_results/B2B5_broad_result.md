# B2~B5 Broad Cost-Aware Retest — Result (top-1500 PIT)
**Date:** 2026-06-11 · **Universe:** top-1500 by marketcap PIT (union 2973, ~$1.2B floor=중대형) · 2016~2026 · 126월
**Data:** broad_SEP(closeadj)·broad_DAILY_pb·broad_SF1(gp/assets)·DAILY_all(marketcap) — 캐시·hash. **팩터 정의 S&P500 run과 동일(튜닝 0).**
**Protocol:** Broad_Universe_Factor_Retest_Protocol_v0.1 (kill조건 사전등록)

| Sleeve | Rank IC | IC-IR | gross Q5-Q1/yr | net/yr | turnover/yr | size(하위/상위) | 판정 |
|---|---|---|---|---|---|---|---|
| B2 value 1/pb | +0.0015 | +0.011 | −1.56% | −1.77% | 116% | — | **DEAD** (net≤0;IC-IR<0.2) |
| B3 quality gp/assets | +0.0207 | **+0.220** | +4.62% | **+4.41%** | 99% | +0.020/+0.019 | **SURVIVE** |
| B4 momentum 12-1 | +0.0140 | +0.098 | +8.24% | +7.63% | 301% | +0.018/+0.009 | **DEAD** (IC-IR<0.2) |
| B5 low-vol | +0.0226 | +0.117 | −4.78% | −5.11% | 142% | +0.029/+0.007 | **DEAD** (net≤0;IC-IR<0.2;소형집중) |

## 판정: 3/4 DEAD · B3 quality만 사전등록 screen 통과
- **value/momentum/low-vol = 비용 후 DEAD.** momentum은 net +7.6%이나 IC-IR 0.10(노이즈)+turnover 301% → 사전규칙대로 DEAD(goalpost 불변).
- **B3 quality = SURVIVE(채택 아님).** IC-IR 0.22(임계 간신히)·net +4.4%/yr·대형/소형 일관·Novy-Marx 이론과 정합 → *quarantine 후보*.

## quality 추가검증 필요 (Phase 1B 입력 前) — 채택 아님
1. **다중검정 보정**: 4팩터 중 1개 통과 → DSR/PBO/N-조정. 보정 후도 살아남나?
2. **subperiod 안정성**: 연도별·전후반 IC 부호 일관성.
3. **cost stress 2x/3x**: 비용 2배에도 net>0?
4. **long-only 버전**: Q5-Q1 long-short 아닌 long-only 벤치-상대 active return.
5. **정의 강건성**: gp/assets vs grossmargin vs roe (단, *과적합 주의* — 정의 사냥 금지).

## 결론
- **단순 single-factor family: value/momentum/lowvol 종료.** quality 1개만 약하게 생존 → 보수적 추가검증으로.
- 다음: quality quarantine 검증 → 통과 시 Phase 1B(저-DoF challenger: penalized regression·constrained ranker·simple blend)에서 quality를 baseline 신호로. *XGBoost/LLM/TSFM 여전히 금지.*
- 정직: IC-IR 0.22는 약함. "엣지 발견"이 아니라 "유일하게 안 죽은 후보". broad에서도 대부분 죽음 = 단순팩터로 쉬운 알파 없음 재확인.
