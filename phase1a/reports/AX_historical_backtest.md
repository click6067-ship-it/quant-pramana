# AX Historical Backtest — 2026-06-14

> RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 자본권한 0 · 검증된 알파 아님. 사전등록 PRAMANA_V4/AX0_Protocol.md.
> 옵션(S1) = **MODELED_OPTION_BS_IVPROXY**(과거 옵션가 데이터 없음·BS+trailing 실현변동성 IV proxy = 가정·실 체결/IV크러시 아님). S3 = 캐시 일봉 = REAL.
> catalyst = EDGAR POS 8-K 2.02/1.01·available_at→next bar(PIT). 비용 옵션 round-trip 5%·spot 1.0bp. 이벤트 12326건.
> **커버리지(Codex#4): EDGAR 표본 199종**(leadership+attack 빈출·a2_event_store)·**전종목 survivorship 증명 아님**. N = (ticker·expiry-month) **독립 클러스터** 수(Codex#3·상관 반복 제거).

## 사전등록 gate(net>0만으론 통과 X: N≥30·median>0·net LCB>0; S1은 추가로 directional Δ LCB>0 **AND** residual LCB>0·protocol §4)
| sleeve | N(클러스터) | median | net LCB | Δ LCB | resid LCB | VERDICT |
|---|---|---|---|---|---|---|
| **S3 long (spot·REAL·excess vs QQQ)** | 8633 | -0.0264 | 0.0054 | — | — | **DEAD** |
| S3 lev3 (3x spot net) | 8633 | -0.0273 | 0.0744 | — | — | DEAD |
| S3 short (−spot net) | 8633 | 0.009 | -0.0349 | — | — | DEAD |
| **S1 modeled-option (Δ+residual gate)** | 8078 | -0.593 | -0.0584 | 0.0102 | -0.0229 | **DEAD** |

## S1 옵션 P&L attribution 평균 (Greeks 분해·-0.03 net)
Δ(directional) 0.026 · gamma 0.2116 · vega(IV) -0.0094 · theta(decay) -0.1356 · residual -0.0208
→ 옵션 P&L이 directional(Δ)이 아니라 theta/vega(decay·변동성)로 설명되면 = catalyst edge 아님.

## S2 conviction calibration (momentum 방향 예측 vs 실현)
N 9910·hit rate 0.521(≈0.5면 무정보)·Brier 0.3109(낮을수록 좋음·0.25=무정보 기준).
재량(discretionary) calibration은 forward-only(과거 사람판단 없음) → 여기는 *systematic momentum 신호*의 방향 정보량만.

## 결론 (정직)
- S3 directional·S1 modeled-option 모두 DEAD/INSUFFICIENT = 8세대 + A2 Attack DEAD 일관(catalyst-momentum spot edge 없음 → 레버·옵션도 그 위에선 못 살림).
- **S1 정직 caveat:** 모델 옵션은 IV proxy·constant-ish·실 IV 크러시(어닝 후 급락) 미반영 → **실제는 더 나쁨**(이 결과가 오히려 낙관). residual gate가 directional 아닌 vega/theta 아티팩트를 걸러냄.
- family-wise(S1/S3 = registry trial): 한 sleeve 통과해도 global hurdle 전엔 exploratory.
- 다음: GRADUATE면 forward broker-valid 검증 / DEAD면 graveyard·registry 다음 칸. "쉬운 공격 엣지 없음" 수용 조건 = 무한루프 차단.
