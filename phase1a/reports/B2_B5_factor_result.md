# B2~B5 Factor Sleeve Baselines — Result (PIT S&P500, DIAGNOSTIC)
**Date:** 2026-06-11 · **Universe:** PIT S&P500 (712 ever-members, ~500/월) · 2016~2026 · 월리밸런스(실제 마지막 거래일)
**Data:** SEP closeadj(mom/lowvol) · DAILY pb(value) · SF1 ARQ gp/assets PIT-by-datekey(quality) — 모두 캐시
**지표:** Rank IC(Spearman: factor vs 다음달 수익) + Q5-Q1 분위 spread

| Sleeve | factor | Rank IC mean | IC-IR | IC>0 | Q5-Q1(연) | n월 |
|---|---|---|---|---|---|---|
| B2 value | 1/pb | −0.0051 | −0.029 | 50% | −0.58%p | 125 |
| B3 quality | gp/assets | +0.0032 | +0.022 | 48% | +0.34%p | 122 |
| B4 momentum | 12-1 | +0.0094 | +0.045 | 51% | +4.18%p | 113 |
| B5 low-vol | −trailing126d vol | −0.0064 | −0.026 | 50% | −7.06%p | 119 |

## 결론 (정직)
- **4개 단순 팩터 전부 S&P500 대형주에서 Rank IC ≈ 0** (|IC|<0.01, IC-IR<0.05). 비용·다중검정 보정 전인데도 신호 없음.
- 모멘텀이 그나마 덜 약함(+4.2% spread)이나 tradeable 기준(IC-IR>0.3) 한참 미달 = 노이즈.
- **이는 정상·예상된 결과**: 대형주 팩터 프리미엄은 차익거래로 희석. 팩터는 소형주 포함 broad universe에서 더 강함(차후).
- **Phase 1A 관점 성공**: 신호가 *재현·측정* 가능(파이프라인 작동) + 가짜 알파를 만들지 않음(정직). 채택 아님(원래 Phase 1A는 채택 단계 아님).

## 버그 수정 기록
- 리밸런스일을 달력 월말→**실제 마지막 거래일**로 수정(이전엔 거래일 겹친 ~40%달만 계산되어 momentum n=11 등 편향). 수정 후 113~125월 전체 계산.

## Phase 1A baseline 시퀀스 완료
B0(cap-weight corr0.998) · B1(1/N) · B2~B5(팩터 IC). 데이터/벤치/팩터 측정 기계 검증 완료. 다음=broad-universe 팩터 or Phase 1B는 별도(재구독 시).
