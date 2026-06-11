# v3 Model-Selection — Council Decision v0.1 (LOCKED)
**Date:** 2026-06-11 · **Mandate:** 용하 "가장 중요한 모델선택은 deep-research + council로 결정." · **결정: 모델공간 CONSTRAIN**(OPEN→제약). research가 판정.

## Council = 3 독립 소스 수렴 (전부 같은 결론)
| 소스 | 결론 |
|---|---|
| **① Codex 적대리뷰** | ML 유죄추정·defer·운영 척추 먼저·정직천장=레버리지된 modest edge. GBM/정규화선형은 도울 수도, deep=Sharadar 일별엔 theater. |
| **② 우리 데이터 empirical bake-off** (walk-forward OOS·비용후) | ridge +0.15·GBM +0.02 net Sharpe — **둘 다 3피처 선형 composite(0.33) 못 넘음.** GBM=theater 확증. |
| **③ deep-research** (105 에이전트·4.3M토큰·literature) | GKX2020 ML OOS R² 0.33-0.40%/월(작음)·헤드라인 Sharpe는 **pre-cost·micro-cap 집중**(EW 2.45→ex-microcap 1.69·턴오버 110-130%/월). 후속(Avramov2023·FAJ2026): ex-microcap/distressed시 ML VW alpha 66-78%↓·deep 전멸. **ML edge는 솔로가 싸게 못 사는 곳에 산다.** 과적합 통제 필수(False Strategy Theorem·Harvey-Liu-Zhu t>3·DSR/PBO/trial ledger). 우리 bake-off를 local 확증으로 인용. |

## 결정 (LOCKED)
1. **모델공간 = CONSTRAINED**(사용자 "OPEN, research결정" → research가 *제약*으로 결정). 
2. **모델 팩토리 = 정규화 선형(ridge/elastic-net) + GBM-as-challenger 까지만.** **deep learning·비제약 ML 금지.** GBM은 *challenger*로만, 통과시켜도 strict gate.
3. **strict trial ledger 필수**: 모든 시도 모델 기록 + Deflated Sharpe Ratio(Bailey-LdP) + PBO/CSCV + Harvey-Liu-Zhu **t>3**(2 아님). 게이트 못 넘으면 채택 0.
4. **진짜 lever는 모델복잡도가 아니다 → 분산(무상관 sleeve 앙상블) + 실행 현실성 + 리스크/레버리지 엔지니어링.** (v3 병렬빌드가 이미 입증: equity MN + ETF trend 결합 = combo Sharpe 0.82, *더 나은 모델이 아니라 분산*에서 옴.)

## 빌드 함의 (effort 재배치)
- **모델 팩토리: 단순 유지** — 현 선형 composite(z-mean) 그대로, GBM은 trial-ledger 게이트 challenger로만 가끔. 모델 정교화에 시간 쓰지 않는다.
- **effort 이동처:** ① **더 많은 무상관 sleeve**(ETF trend 외 — carry/vol/cross-asset, 각 사전등록 kill) ② **execution 현실성**(execution.py 통합·일별 체결·비용) ③ **risk/leverage 엔지니어링**(monitor.py 통합·kill·capacity) ④ **forward paper 검증**(promotion gate).
- LOCKED 갱신: "모델공간 OPEN(research결정)" → **research결정 = CONSTRAINED**(정규화선형+GBM challenger·trial ledger·no deep).

## 산출
deep-research 전문 = `phase1a/reports/V3_model_selection_deepresearch.json` · 본 결정 = LOCK. 다음: master plan v0.2의 "모델 research" 항목을 본 결정으로 대체.
