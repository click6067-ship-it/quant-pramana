# SOURCE_LOCK_OK

## 연구 계획

- 범위는 **정량 주식 시스템(systematic equity) 후보군 맵 작성**으로만 잠그겠습니다. 즉, 연구 목적은 **feature/representation → alpha → ensemble → optimizer → risk → cost/slippage → execution support → monitoring/drift → LLM advisory**의 계층별 후보군 정리이며, **최종 모델 채택·종목 추천·실거래 설계·성과 예측**은 제외합니다. fileciteturn0file0

- 먼저 **최종 레이어 분류(L0~L12)**를 고정하겠습니다. L0 연구목표/벤치마크/유니버스, L1 데이터 소스/계약, L2 데이터 엔지니어링/PIT/버저닝, L3 특징/표현, L4 알파 모델, L5 알파 앙상블, L6 포트폴리오 구성/최적화, L7 리스크 모델/엔진, L8 비용·슬리피지, L9 실행 지원, L10 검증/실험 팩토리, L11 모니터링/드리프트, L12 거버넌스/인간/LLM 자문으로 놓고 각 레이어의 입력·출력·금지사항·필수 게이트를 맵핑하겠습니다. fileciteturn0file0

- 다음으로 **모델 패밀리 그룹화**를 수행하겠습니다. 기준선 후보는 고전 팩터, value/quality/profitability/low-vol, momentum/trend, 단순 reversal, cross-sectional ranking, 선형·패널티 회귀로 두고, challenger는 tree ensemble, regime-aware weighting, event/NLP, robust optimizer, volatility/risk 고도화, cost-aware optimization으로 두며, exploratory/quarantine은 deep sequence, TSFM, financial foundation model, LLM weak signal, alternative data, RL·black-box meta-allocator로 분류하겠습니다. fileciteturn0file0

- 각 모델 패밀리마다 **필수 데이터 요구사항**을 명시하겠습니다. 기본적으로 가격·거래량·기업행위·상장폐지, PIT fundamentals와 restatement 처리, 벤치마크/섹터/리스크 참조데이터가 필요하며, 이벤트/NLP 계열은 공시·실적발표·뉴스·문서 시점 정합성이, 비용/실행 계층은 체결/호가/ADV·스프레드·시장충격 근사 데이터가 필요하다는 식으로 정리하겠습니다. fileciteturn0file0

- **Phase 1 “지루한 기준선”**은 보수적으로 정의하겠습니다. 단순 팩터 묶음, cross-sectional rank, equal-weight 또는 monotone rank-to-weight, 기본 리스크 캡, 단순 turnover/cost haircut, 결정론적 리스크 엔진을 baseline candidate로 두고, 이후 challenger가 이를 넘는지만 검증하는 구조로 두겠습니다. fileciteturn0file0

- 모든 promotable 후보에는 **검증 게이트 매핑**을 붙이겠습니다. 최소한 **data gate → OOS → walk-forward → cost stress → multiple-testing control → paper-shadow gate** 순서를 강제하고, 각 모델 패밀리에 대해 어느 게이트가 필수인지, 실패 시 quarantine 또는 reject로 가는지를 표로 고정하겠습니다. fileciteturn0file0

- 별도로 **과최적화·누수·데이터 실패 레지스터**를 만들겠습니다. look-ahead bias, survivorship bias, delisting omission, stale fundamentals, restatement leakage, benchmark mismatch, cost underestimation, turnover explosion, feature mining, hyperparameter overfitting, regime overfitting, vendor artifact, LLM hallucinated signal을 모델 패밀리별 실패 모드에 연결하겠습니다. fileciteturn0file0

- **소규모 팀 실현 가능성(small-team feasibility)**을 독립 축으로 평가하겠습니다. 각 후보군에 대해 구현 복잡도, 계산량, 데이터 부담, 디버깅 가능성, 모니터링 부담, 유지보수 비용을 low/med/high로 매기고, **U.S.-core first, KR-addon later** 원칙에 따라 미국 1차 실험 적합성과 한국 후속 적합성을 분리해 적겠습니다. 한국 시장으로 옮길 때는 회계 공시 타이밍, 유동성, 비용·체결 구조, 시장 제도 차이를 재검증 대상으로 분리하겠습니다. fileciteturn0file0

- **LLM은 오프패스(off-path) 자문 계층**으로만 다루겠습니다. 허용 범위는 research assistant, filing/news parser, event extraction, 가설 생성, adversarial critic, 사후 설명 수준으로 제한하고, 자유형 출력은 주문·거부권·포지션 사이징·regime switch를 직접 트리거하지 못하도록 명시하겠습니다. LLM-derived weak signal은 있더라도 quarantine 또는 엄격한 schema-locked artifact로만 취급하겠습니다. fileciteturn0file0

- **소스 레지스터는 1차·공식 소스 중심**으로 구성하겠습니다. 기준선 팩터 및 정렬 기준은 Kenneth R. French Data Library 같은 공식 데이터 설명을 우선 보고, tree/tabular challenger는 XGBoost·LightGBM·CatBoost의 공식 문서를 우선 참조하며, 이후 학술 논문과 검증 문헌으로 보강하겠습니다. 최종 산출물은 **후보군 맵과 검증 조건**만 제시하며, **최종 모델 채택 판단은 보류**합니다. citeturn4view0turn5view0turn5view1turn5view2