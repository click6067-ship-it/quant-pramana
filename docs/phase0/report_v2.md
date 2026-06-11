# Phase 0 리서치 보고서 v2 (통합본)

## 최신 퀀트 트레이딩 / 자동화매매 시스템 구조 분석 — 검증된 9개 사례

**대형 systematic 3 + 프론티어 MM/prop 3 + 소규모/개인 3** · 기준일 2026-05-31 · 공개자료 기반 · 한국어 + 핵심 영어 병기

> 이 v2는 (1) 1차 docx, (2) 멀티에이전트 워크플로(54 agents, adversarial verify→macro→modeling→synthesis→critic), (3) Codex 독립조사를 통합하고, **적대적 비평(critic) 결과를 본문에 반영**한 판이다. 핵심 변화: ①firm-income과 strategy-return의 검증성을 분리, ②LLM council을 라이브 주문경로에서 분리(off-path advisory), ③LLM 트레이딩 회의론 실증(StockBench/TradeTrap/Alpha Illusion/FINSABER)을 부록에 추가.


---

## 목차

- 0. Executive Summary
- 1. 문제정의와 조사 범위
- 2. 자료 신뢰도와 선정 기준
- 3. 후보 Longlist와 탈락/참고 처리
- 4. 최종 9개 요약 매트릭스
- 5. 개별 Case Study 9개
- 6. Cross-case Architecture Synthesis
- 7. 최신 모델링·AI·LLM 활용 위치
- 8. Frontier Operating Model (정본 레이어드)
- 9. Scorecard (10차원)
- 10. Phase 0 결론
- 부록 A. 적대적 비평 (Critic) — 본문 보정 근거
- 부록 B. LLM 트레이딩 회의론 실증
- 부록 C. Sources
- 부록 D. Locked Research Brief

---

## 0. Executive Summary

## 0.1 한 문장 결론
최신 자동 퀀트 시스템의 수익 구조는 **"천재 시그널 하나"가 아니라 `다수의 약한 신호(weak signals)를 예측 레이어가 생성 → 비용·리스크를 내재화한 optimizer가 포지션으로 변환 → risk-engine이 최종 게이트로 강제 → 사람은 메타 거버넌스(배포·한도·킬스위치)만`이라는 레이어 분리(layered separation)에 있다.** 9개 타깃 전부가 자산군·규모·빈도가 달라도 이 골격을 공유했다. 우리(solo+AI, ₩10M, KOSPI100→US, swing/mid-long)가 복제할 것은 이 **구조와 검증 규율(discipline)**이지, 그들의 알파 수치·인프라·레버리지가 아니다.

## 0.2 모든 시스템이 공유하는 6개 매크로 패턴 (profit-maximization lens)

**패턴 1 — 신호 ≠ 주문 (Signal is never the order).**
9곳 전부 예측(forecast)과 집행(execution) 사이에 반드시 한 단계 이상의 변환층을 둔다. AQR/Man Numeric은 `forecast → risk model → cost-aware optimizer → 포지션`, Marshall Wace TOPS는 `idea → contributor-scoring → aggregation → risk overlay`, XTX/Jane Street/Flow Traders는 `price forecast → 호가 skew → inventory/risk cap`. **솔로가 가장 흔히 죽는 함정이 "신호=주문" 직결인데, 검증된 시스템은 구조적으로 이를 금지한다.**

**패턴 2 — risk-engine이 최상위, 알파는 그 아래 (risk on top, alpha below).**
어떤 단일 모델·신호도 리스크 한도를 우회하지 못한다. Jane Street의 "risk engine > signal", Man의 독립 Risk team(1987~), Flow Traders의 이사회 레벨 한도, Marshall Wace의 factor-neutral optimizer 제약 — 전부 동일. **이것이 우리 brief의 "LLM은 risk-engine 위가 아니라 review 레이어로 그 옆/아래"라는 설계의 외부 검증이다.**

**패턴 3 — 비용을 처음부터 내재화 (cost internalization, not subtraction).**
AQR 'Implementable Efficient Frontier'의 핵심 = 거래비용을 사후 차감이 아니라 optimizer 목적함수에 넣어 **모델 우열을 net-of-cost로 판정**. Jane Street의 utility/weighted 타깃, Flow Traders의 회전비용 최소 ETF 메커니즘 동일. **₩10M·KR tax 0.20% 환경에서 이것이 north star(after-cost 초과) 달성의 구조적 열쇠다.**

**패턴 4 — 다수 약신호의 분산 결합 (weak-signal ensemble + diversification).**
Man AHL "약한 신호 다수 → 강한 signalling power", AQR Fundamental Law(IR ≈ IC × √breadth), Unger "다수 단순 시스템 portfolio", Parker "무상관 룰 시스템 6개". **단일 강신호 추구는 과적합의 입구. 알파는 breadth × 저상관 분산에서 나온다.**

**패턴 5 — 검증 게이트가 곧 알파 (validation discipline = the real edge).**
walk-forward, out-of-sample, parameter-stability, net-of-cost 평가, economic-prior 통과가 배포 전 강제 게이트. AQR economic-prior-first, Man의 ML 5년 검증 후 라이브, Jane Street types-as-veto, Unger walk-forward+OOS+stability, Parker robustness-first. **백테스트 우수 ≠ 자동 배포. 검증을 통과한 것만 portfolio 입장.**

**패턴 6 — high automation + human-only-at-meta.**
정상 주문은 무승인 자동, 사람은 모델 배포·리스크 한도·예외·킬스위치에만 개입. 9곳 전부 이 거버넌스를 따른다. **우리 brief의 자동화 목표와 거의 1:1.**

## 0.3 학습-가능도(structure-knowability) 스펙트럼

| 그룹 | 타깃 | structure | profit-verify | 우리에게의 본질 |
|---|---|---|---|---|
| A | **AQR** | HIGH (논문 공개) | HIGH | 유일하게 논문으로 복제 가능한 청사진 |
| A | **Man (AHL+Numeric)** | HIGH | **HIGH (상장 audited)** | 레이어 분리 + vol-targeting + black/glass-box |
| A | **Marshall Wace TOPS** | HIGH | MEDIUM | 생성원을 데이터로 보는 alpha-capture 템플릿 |
| B | **XTX** | MEDIUM | HIGH (Companies House) | 학습/실행 분리, 예측=단일 중앙자산 |
| B | **Jane Street** | MEDIUM (HOW공개/WHAT비밀) | MEDIUM | 재현성+types-as-veto 거버넌스 교본 |
| B | **Flow Traders** | MEDIUM | **HIGH (상장 audited)** | risk-engine 우위 + estimate→act 분리 |
| C | **Parker** | HIGH | MEDIUM-HIGH | **솔로 1:1 구조 템플릿** (system stop, equity-curve 스위치) |
| C | **Alpha Architect** | HIGH (책 공개) | MEDIUM (지수 LAG) | **함정 회피 레퍼런스** (공개 factor도 지수 하회) |
| C | **Unger** | MEDIUM | MEDIUM | portfolio-of-systems + 2단 risk cap |

## 0.4 가장 날카로운 적대적 발견 (adversarial findings — 돈 잃지 않기 위해)

1. **"검증된 기록 ≠ 벤치마크 초과."** Alpha Architect QMOM/QVAL는 10년 라이브 audited 기록이 진짜지만 S&P500을 **다년간 하회**(QMOM 10년 ~12.2% vs VOO ~13.9%, MDD −39%/−51%). **공개·규율 있는 단일 factor 시스템조차 지수를 못 이긴다** → 단일 factor 복제만으로는 우리 north star 미달. 이것이 가장 비싼 교훈.

2. **"firm-profit-verified ≠ strategy-replicable."** XTX £1.28B, Jane Street $20.5B, Flow Traders €159.5m는 절대 순이익이 검증됐을 뿐 **strategy-level Sharpe/MDD/수익률은 미공개** → 우리 north star(after-cost 위험조정)와 직접 비교 불가. 그들은 "수익률 벤치마크"가 아니라 "구조 학습 표본"이다.

3. **"대회 수익률 ≠ 지속 CAGR."** Unger +672%/+240%는 small-account high-leverage futures 대회 산물 + survivorship/multiple-entry 결함. 숫자는 버리고 규율만.

4. **"factor는 수 년 죽는다."** AQR quant winter AUM 50%+ 증발, Parker −45% DD(7개월). **드로다운 ≠ 즉시 kill**, 단 사전정의 risk 조건에서만 개입. 25% MDD는 강선호지 hard filter 아님.

## 0.5 solo가 복제 CAN vs CANNOT (요약)

**CAN (이식 가치 HIGH):**
- 레이어 분리 아키텍처 (신호 → optimizer → risk-engine → exec → governance)
- cross-sectional rank 기반 factor (value/momentum/quality) — 공개 가격+재무제표만으로 구성
- 다수 무상관 시스템 portfolio + 동일가중(1/N) baseline
- cost-aware 비중결정 (KR 0.20% + 슬리피지를 목적함수에 내재화)
- 2단 risk cap (per-system + portfolio) + system stop (−10%/−15%) + equity-curve on/off 스위치
- robustness-first 검증 게이트 (walk-forward + OOS + deflated Sharpe + net-of-cost)
- governance 모델 (정상주문 자동, 사람은 메타만)

**CANNOT (버릴 것):**
- 마켓메이킹·초저지연·FPGA·colocation·AP creation/redemption (XTX/JS/Flow)
- 25k GPU·650PB·alt-data 인프라·다자산 cross-asset 규모
- 거대 AUM·기관 LP·멀티에셋 풀스택·고레버리지·풀 long-short market-neutral (AQR/Man)
- futures/forex high-leverage sizing (Unger/Parker)
- 그들의 알파 수치·시그널 내용 (전부 영업비밀 = group A/B 정상)

---


---

## 1. 문제정의와 조사 범위

사용자 목표는 구현 전 **Phase 0 리서치**다. 코드·클라우드 비용·브로커 API·모델 튜닝이 아니라, 최신 자동화 퀀트 시스템의 **거시 작동방식과 시스템 패턴**을 파악한다.

| 항목 | 확정 기준 |
|---|---|
| 최우선 목표 | 수익률 극대화 (profit maximization) |
| 보조 (평가항목) | 솔로/소팀이 클라우드 GPU + 개인 PC로 참고·응용 가능한가 |
| 주요 시장 | 한국 주식, 미국 주식 |
| 참고 시장 | 선물·옵션 (구조 참조, 옵션은 신호로만 / naked selling 제외) |
| 제외 | 크립토·코인, 미검증 개인자료, tail-risk 몰빵 |
| 거래 주기 | 수분 intraday~일중~일봉~중기/장기 systematic (HFT는 구조 참조용) |
| MDD | 25% = hard filter 아닌 strong preference |
| 인간 개입 | 예외·모드전환·전략배포·리스크한도·kill switch (정상주문은 자동) |

> **이 v2의 핵심 전제(critic 반영):** 공개자료로 내부 알파를 복원할 수 없다. 9개 중 누구도 *검증된 after-cost risk-adjusted 초과수익*을 우리에게 직접 제공하지 않는다. 목적은 **전략 복제가 아니라 operating model의 추상화**다.


---

## 2. 자료 신뢰도와 선정 기준

**성과 검증성(profit-verifiability)과 자료 신뢰도(source tier)를 분리**해 평가하고, 카테고리별로 다른 바를 적용한다.

| 구분 | 인정 가능한 성과/자료 |
|---|---|
| 대형 systematic | 펀드 수익률·투자자 서한·규제(13F)·감사(상장 statutory)·재검증된 장기 기록 |
| 프론티어 MM/prop | 회사 순이익·거래량·시장점유율·공식 기술자료·규제/등기 (단 **수익률 검증성 점수는 낮게**) |
| 개인/소형 | 공식 대회·브로커 인증 실계좌·규제 등록·감사 track record·외부검증 장기 실거래 |
| 제외 | 미검증 블로그·유튜브·트위터·출처불명 수익률 캡처·성과인증 없는 백테스트 |

> **critic이 강제한 가장 중요한 보정:** "회사가 돈 벌었다(firm-income, audited)"와 "전략이 OOS after-cost로 돈 번다(strategy-return)"는 **다른 축**이다. 후자 기준으로는 **9개 전부 LOW~NONE**. 따라서 어떤 회사의 수익 숫자도 *우리 목표치로 import 금지*. 매트릭스(§4)와 스코어카드(§9)는 이 두 축을 분리해 읽어야 한다.


---

## 3. 후보 Longlist와 탈락/참고 처리

워크플로가 longlist 28개를 발굴→adversarial verify로 검증했다. 탈락은 *구조 미달*이 아니라 대부분 *그룹별 수익 검증 바 미달*이다.


**탈락/참고 강등 (대표):**

| 후보 | 그룹 | 처리 사유 (요약) |
|---|---|---|
| Jump Trading | B | DROP at shortlist. 브리프의 MM 증거기준(직접 검증 가능한 net-income/volume/market-share/filings) 어느 것도 충족하지 못하고, 확인 가능한 것은 Tier3 제3자 추정치뿐 — Tier1/2 profit proof 부재. 아키텍처는 ultra-low-latency HFT로 secret(브리프 reference-only 존). 우리 solo+AI / ₩10M / KOSPI100… |
| Robert Carver (ex-Man AHL, solo systematic trader, pysystemtrade) | C | Group-C 수익 증거 바 미달: 제3자 감사·broker-verified·공식대회·규제등록 수익 기록 없음. pedigree(AHL global-macro PM)와 live system(pysystemtrade, IB 실거래 since ~2014)은 확인되나, 개인 수익은 self-reported·unaudited뿐이라 profit exemplar로는 탈락. 단 STRUCTURE 레퍼런스(volatility-targe… |
| Andreas Clenow (ACIES Asset Management, Stocks on the Move) | C | Group C 포함 기준(third-party-verified live/audited/competition profit)을 충족하지 못해 '검증된 수익' 케이스로는 FAIL. 수익 증거가 backtest-illustrative이고 외부감사 live track record가 공개되지 않음. 다만 전략 구조의 재현성·적용성이 우리 시스템(cross-sectional KOSPI100/US momentum, swing+mid/l… |
| Nick Radge / The Chartist (solo systematic momentum, ASX and US equities) | C | 탈락 사유 = PROFIT 검증 미달(구조 미달 아님). 그룹C 증거 바(third-party-verifiable live/competition/audited/regulator-filed)를 만족하는 독립 소스 부재. 존재하는 것은 firm-reported newsletter 모델포트폴리오 + 주장만 된(독립 확인 불가) audit으로, 자기보고 단독 → low confidence → FAIL. Wesley Gray(학술… |

> Goldman Sachs = 본문 9개가 아닌 **참고 레퍼런스**(비정형 데이터→신호화). Carver/Clenow/Radge는 수익 검증 바 미달로 *수익 사례*에선 탈락하나 **구조/설계 레퍼런스로는 최상급** — §5·§8·Codex 부록에서 활용.


---

## 4. 최종 9개 요약 매트릭스

| 그룹 | 대상 | 수익검증성(firm) | 전략수익 검증 | 구조 공개 | 우리에게의 본질 |
|---|---|---|---|---|---|
| A | AQR Capital Management | MEDIUM(언론) | LOW~NONE | high | 유일하게 논문으로 복제 가능한 factor 청사진 |
| A | Man (AHL+Numeric) | HIGH(상장audit) | LOW~NONE | high | 레이어 분리 + vol-targeting + black/glass-box 병치 |
| A | Marshall Wace (TOPS) | MEDIUM | LOW~NONE | high | 생성원을 데이터로 보는 alpha-capture(단 표본부족→직접이식 제한) |
| B | XTX Markets | HIGH(Companies House) | LOW~NONE | medium | 학습/실행 분리 패턴 (compute moat는 비이식) |
| B | Flow Traders | HIGH(상장audit) | LOW~NONE | medium | risk-engine 우위 + estimate→act 분리 |
| B | Jane Street | MEDIUM(채권공시) | LOW~NONE | medium | 재현성·types-as-veto 거버넌스 교본 |
| C | Marsten Parker | MEDIUM(저자재구성) | LOW~NONE | high | 솔로 1:1 구조 템플릿(system stop·equity-curve 스위치) |
| C | Wesley Gray / Alpha Architect | MEDIUM(ETF NAV) | LOW~NONE | high | 함정 회피 레퍼런스(공개 factor도 지수 하회) |
| C | Andrea Unger | MEDIUM(대회검증) | LOW~NONE | medium | portfolio-of-systems + 2단 risk cap (수치는 격리) |

> **전략수익 검증 컬럼이 전부 LOW~NONE인 것이 이 표의 핵심 메시지다**(critic). firm이 돈 번 것과 전략이 재현가능한 것은 다르다.


---

## 5. 개별 Case Study 9개

### A1. AQR Capital Management  ·  [대형 systematic 운용]

**선정 이유:** 9개 타깃 중 AQR을 group A에 넣는 결정적 이유 = structure-knowability가 압도적으로 높음. 르네상스/D.E.Shaw 등은 secret-structure(group A에서 비밀은 정상)인 반면, AQR은 Asness 등이 value·momentum·quality·carry 방법론을 SSRN/저널에 동료심사 논문으로 공개 → 대형 quant 중 거의 유일하게 "복제 가능한 청사진"을 준다. 그 팩터 체계가 우리의 KR/US cross-sectional equity swing+mid/long 코어와 1:1 매핑. 또 profit-verifiability도 high: press 재구성 수익률 + 장기 사이클 전구간(정점→quant winter 드로다운→회복) 기록 + SEC 규제등록으로 삼중 검증. 무엇보다 2018-2020 quant winter(AUM 50%+ 증발)는 adversarial 증거로서 가치가 큼 — 우리의 25% MDD 선호와 LLM-council regime-critic 역할에 "factor가 수 년간 죽을 수 있다"는 직접적 regime-risk 교훈. 버릴 것: AQR의 거대 AUM·기관 LP·멀티에셋 풀스택은 ₩10M 솔로엔 과대 → 우리는 팩터 로직·cost-aware optimizer·governance 구조만 차용하고 규모·상품화·레버리지는 버린다.

**검증/성과 근거:** 2024 fund-level returns (복수 Tier2 언론 독립 확인 — Bloomberg/BNN, Hedgeweek, Financial Post, Pensions & Investments):
- Apex (멀티전략): +15.1% (2019 출범 이래 최고의 해, 신규자금 마감)
- Delphi Long-Short Equity: +14.6%
- Helix (macro/멀티에셋): +14.2%
- 최고 수익 펀드(주식 market-neutral 계열로 보도): 약 +71% → brief가 명시한 후보 주장 "15-20%+"보다 오히려 상회
AUM 사이클 (Pensions & Investments + Wikipedia/Institutional Investor):
- 2018 정점 ~$226B → 2020-21 <$100B (quant winter로 ~50%+ 감소, adversarial 드로다운 증거) → 2024 ~$120-128B 회복
규제·등록: SEC EDGAR CIK 0001167557 = AQR CAPITAL MANAGEMENT LLC, 13F-HR 분기 보고 확인(Tier1).
방법론 검증: AQR/SSRN의 Asness 등 동료심사 논문(value/momentum/quality/carry) = methodology-verifiability HIGH(Tier2 academic).
profit-verifiability 종합 = HIGH (press returns + 전 사이클 기록 + 규제등록 삼중).

**무엇인가:** AQR Capital Management LLC (AQR = "Applied Quantitative Research") — 1998년 Cliff Asness, David Kabiller, Robert Krail, John Liew가 설립한 그리니치(코네티컷) 소재 대형 systematic/quantitative 자산운용사. SEC 등록 운용사(EDGAR CIK 0001167557, 13F-HR 분기 보고). 핵심 정체성: factor investing(value, momentum, quality/defensive, carry)을 학술 논문 수준으로 공개하면서 그 동일 팩터를 long-short·cross-sectional·multi-asset로 구현하는 "rules-first systematic" 운용사. AUM은 2018년 정점 ~$226B → quant winter로 2020-21년 <$100B(약 50%+ 급감) → 2024년 ~$120-128B로 회복. 우리 프로젝트 관점에서 AQR이 특별한 이유: 9개 타깃 중 방법론 공개도(structure-knowability)가 가장 높고, 그 팩터 체계가 우리의 KR/US equity cross-sectional swing+mid/long 코어와 거의 1:1로 매핑된다. 즉 "group A 중 유일하게 우리가 베껴 쓸 수 있는 청사진을 논문으로 내놓은 곳".

**거시 아키텍처:**

END-TO-END 레이어드 구조 (AQR 공개 논문·전략 설명에서 재구성, 구체 파라미터는 비공개=FACT/INFERENCE 혼합):

(1) RESEARCH / SIGNAL LAYER — 경제 이론(economic priors)에서 출발한 가설 → SSRN/저널 논문화 가능한 팩터로 정제. 4대 스타일: value(싼 것 매수), momentum(추세 추종), quality/defensive(우량·저위험), carry(보유수익). 데이터: 가격, 펀더멘털(밸류에이션·수익성·재무건전성), 매크로, 그리고 점차 alternative data + machine learning. ML 철학(AQR 백서 'Can Machines Learn Finance?', Asness 코멘터리): 시장은 signal-to-noise가 극도로 낮아 순수 data-mining은 과최적화로 망함 → ML은 economic theory를 guardrail로 두고 traditional factor를 "대체가 아니라 증강(augment)"할 때만 채택. [FACT: 공개 철학 / INFERENCE: 실제 라이브 모델 가중치]

(2) SIGNAL COMBINATION / FORECAST LAYER — 여러 팩터 신호를 cross-sectional ranking으로 결합해 종목·자산별 기대수익 forecast 생성. 단일 신호가 아니라 다신호 앙상블(분산화가 핵심 알파).

(3) RISK MODEL LAYER — 공분산·팩터 노출·변동성 추정. 이 레이어가 "어떤 팩터에 얼마나 노출되어 있는가"를 상시 계측. 우리 시스템의 risk-engine에 직접 대응.

(4) PORTFOLIO CONSTRUCTION / OPTIMIZER LAYER — forecast(2) + risk(3) + 거래비용을 입력으로 optimizer가 목표 포트폴리오 산출. AQR 워킹페이퍼 'Machine Learning and the Implementable Efficient Frontier'의 핵심 = 비용·구현가능성을 최적화에 내재화. long-short·market-neutral·multi-asset 형태로 구현.

(5) EXECUTION LAYER — 비용 최소화 알고리즘 집행. (HFT/마이크로초 영역 아님 — AQR은 저~중빈도, 우리 brief의 "execution은 구조 참조" 영역과 정렬.)

(6) PRODUCT WRAPPER — 동일 엔진을 상품으로 포장: Apex(멀티전략, 주식·채권·통화·원자재 best-ideas 결합), Delphi(long-short equity), Helix(macro/멀티에셋), Style Premia, Risk Parity, Managed Futures 등.

(7) GOVERNANCE / RESEARCH-INTEGRITY LAYER — quant winter(2018-2020) 이후 가장 중요해진 층: 팩터가 길게(수 년) underperform할 때 "모델이 틀렸나 vs regime이 나쁜가"를 판정하고 전략을 유지·중단·리밸런스하는 메타 판단. Asness의 'Is Systematic Value Investing Dead?', 'Factor Timing' 논문이 이 층의 사고를 보여줌. → 우리 LLM-council의 regime-critic / governance-veto 역할의 원형.

**데이터 흐름:** 가격·펀더멘털·매크로·(점증적) alternative data → [economic-prior 기반 신호화 + ML 증강] → cross-sectional 다신호 forecast → risk model(공분산·팩터노출) → cost-aware optimizer → 목표 포트폴리오 → 비용최소 execution algo → live long-short/market-neutral/multi-asset 포지션 → 성과·노출·드로다운 모니터링 → (피드백) regime/research-integrity 거버넌스가 모델 유지·재검증·배포결정으로 환류. 우리 시스템 대응: 동일 파이프라인을 ₩10M·KOSPI100 규모로 축소하되, AQR의 (3)risk-model+(4)cost-aware optimizer+(7)governance 3개 층을 LLM-council 위에 두는 우리 설계의 정당화 근거가 됨. 특히 KR tax 0.20% + 슬리피지를 optimizer에 내재화하는 것은 AQR의 'Implementable Efficient Frontier'(비용을 최적화에 넣어라)와 직결.

**자동화 수준:** HIGH systematic, rules-driven. 평상시 신호생성→포트폴리오 산출→집행은 모델·optimizer·실행알고가 자동 수행(주문 단위 인간 재량 개입 없음). 인간(리서처·PM·리스크팀)의 역할은 (a) 모델 자체를 연구·검증·배포, (b) 리스크 한도 설정, (c) regime·드로다운 판정과 전략 유지/중단 결정에 집중 — 즉 "주문이 아니라 시스템을 운용". AQR 자신이 'Systematic vs. Discretionary' 논문에서 systematic의 강점을 breadth(폭넓은 동시 베팅)·discipline(감정 배제)·risk management로 규정. 단 100% 블랙박스 자동은 아님: 팩터·모델 변경, 배포, regime 대응은 인간 거버넌스가 게이트한다. [FACT: 공개 철학 / INFERENCE: 사내 자동화 비율의 정확한 경계]

**인간 개입 지점:** 우리 거버넌스 5축 매핑:
- normal-orders-auto: ✅ 강하게 일치. 모델·optimizer가 산출한 정상 리밸런스/주문은 인간 승인 없이 자동 집행. AQR의 핵심 가치(discipline = 감정·재량 배제)와 정확히 부합.
- mode-switch (aggressive/stable/conservative): ⚠️ AQR엔 우리 식의 명시적 3모드 토글은 없으나, 사실상 등가물은 "factor timing / exposure 조정" 결정 — AQR은 이를 매우 신중·드물게, 인간 판단으로 수행(venial value-timing'만 인정, 상시 타이밍은 경계). → 우리 설계의 "사전조건 충족 시 자동, 아니면 인간 승인" 중 후자(인간 승인) 쪽에 가까움. [INFERENCE]
- deploy-approval (전략 배포): ✅ 강하게 일치. 신규 팩터·모델은 리서치→검증→인간 승인 후 배포(과최적화 방어가 AQR의 명시적 핵심 가치). 우리 LLM-council의 leakage/overfit 비평 역할의 직접 원형.
- risk-limit-approval: ✅ 일치. 리스크모델·한도 설정은 인간 거버넌스 영역.
- kill-switch: ⚠️/INFERENCE. 공개 문서에 명시적 kill-switch 기술은 없음. 다만 quant winter 시 AUM 50%+ 감소를 "전략 중단" 대신 "유지+방어 논문화"로 대응한 것은, AQR이 일시적 드로다운으로는 코어 전략을 죽이지 않는다(=kill-switch는 진짜 구조적 고장에만)는 거버넌스 성향을 시사. 우리에겐 "드로다운 ≠ 즉시 kill, 단 사전정의된 risk 조건에서만 hard-veto"라는 교훈.

**데이터 사용:** 데이터 표현(DATA REPRESENTATION) 관점 — AQR의 입력 우주는 의도적으로 "이코노믹 프라이어(economic prior)로 정당화되는" 변수로 제한된다. 4개 카테고리: (1) PRICE/RETURN 시계열 → momentum(과거 2-12개월 수익률), short-term reversal, time-series momentum/trend(managed futures). (2) FUNDAMENTAL cross-section → value(B/P, E/P, CF/P, sales/P 등 복수 밸류 지표의 composite), quality/profitability(gross profit, ROE, accruals, payout — QMJ "Quality Minus Junk"), defensive(low-beta, "Betting Against Beta"). (3) CARRY/yield → 자산군별 보유수익(주식 배당, 채권 롤다운, 통화 금리차, 원자재 콘탱고/백워데이션). (4) MACRO + (점증적) ALTERNATIVE DATA + 텍스트. 핵심 구조적 특징 = 모든 변수를 RAW level이 아니라 CROSS-SECTIONAL RANK / z-score로 표현한다 — 즉 "이 종목의 밸류가 절대적으로 싼가"가 아니라 "유니버스 내 상대 순위가 어디인가". 이는 시장 전체 레짐 변동에 대해 신호를 robust하게 만들고(market-neutral 구현과 직결), 우리 KOSPI100 cross-sectional swing 코어에 거의 그대로 이식 가능한 표현 방식이다. 데이터 철학상 가장 중요한 제약: AQR은 "데이터가 많을수록 좋다"가 아니라 signal-to-noise가 극도로 낮은 금융데이터에서는 입력 차원 증가가 곧 과최적화 위험이므로, 변수 추가는 반드시 사전 경제 가설을 통과해야 한다는 입장(data-snooping 방어). 우리 시스템 함의: ₩10M 솔로는 alt-data 인프라가 없으므로 AQR의 (1)(2)(3) — 즉 공개 가격+재무제표만으로 구성 가능한 팩터 — 가 현실적 이식 대상이고, alt-data/ML-augment 층은 버린다. [FACT: 팩터 정의·랭킹 표현은 공개 논문 / INFERENCE: 라이브 composite 가중치는 비공개]

**alpha 생성:** 알파 생성 접근 — AQR 알파의 본질은 "단일 천재 신호"가 아니라 BREADTH(폭) × DIVERSIFICATION(저상관 신호 결합)이다. PREDICTION PROBLEM 정의: 각 종목/자산에 대해 cross-sectional 기대초과수익(expected relative return) 또는 부호(rank)를 예측 — 절대 가격 예측이 아니라 "어느 종목이 동료 대비 아웃퍼폼할 확률"의 순위 문제. 알파 파이프라인 3단계: (A) 각 스타일(value/momentum/quality/carry)을 독립 신호로 산출 → (B) 신호들이 서로 저상관(특히 value↔momentum은 음의 상관)이라는 점을 이용해 앙상블 결합 → (C) cross-sectional ranking으로 long(상위)·short(하위) 포트폴리오 구성. 알파의 수학적 원천 = "Fundamental Law of Active Management"(IR ≈ IC × √breadth): 개별 신호의 예측력(IC)은 낮아도 수백~수천 종목·복수 자산군에 동시 적용해 breadth를 키우면 정보비율이 누적된다. AQR은 이를 "각 베팅은 약하지만 충분히 분산되면 통계적으로 견고하다"로 표현. ML의 역할(공개 철학): 순수 ML 데이터마이닝으로 새 신호를 발굴하기보다, 비선형성·신호 상호작용을 잡아 기존 팩터를 AUGMENT(증강)하는 보조 도구. 'Virtue of Complexity' 계열 연구는 파라미터가 표본 수보다 많은 과파라미터 모델이 (ridge 정규화 하에서) 오히려 out-of-sample 예측·타이밍을 개선할 수 있음을 보였으나, AQR 운용 철학은 여전히 economic-prior guardrail을 절대 우선한다. 우리 시스템 이식: 단일 급등주 신호에 베팅하지 말고 (value+momentum+quality) 저상관 신호를 KOSPI100 전체에 cross-sectional ranking으로 동시 적용하라는 것이 가장 직접적인 알파 교훈. swing/mid-long 범위 한정: AQR 알파는 저~중빈도라 우리 swing 코어와 정렬되며, HFT 마켓메이킹 알파는 우리 적용 범위 밖.

**모델·표현:** 모델·표현 (DATA REP + PREDICTION + VALIDATION + POSITION-IN-SYSTEM):
1) CROSS-SECTIONAL FACTOR MODEL (코어, 위치=시그널레이어) — 데이터표현: 종목별 팩터 z-score 벡터. 예측문제: 동료대비 상대수익 순위. 검증: 장기·다국가·다자산 out-of-sample 재현성("Fact, Fiction and Momentum"식 글로벌 robustness 체크). 시스템내 위치 = 알파 소스. 우리 코어와 1:1.
2) RISK MODEL (위치=리스크레이어) — 데이터표현: 수익률 공분산 행렬 + 팩터 노출 매트릭스. 예측문제: 변동성·상관·팩터노출 추정(수익 예측 아님). 시스템내 위치 = optimizer 입력 + 상시 노출 계측. 우리 risk-engine의 직접 원형.
3) ML-AUGMENT LAYER (위치=시그널 보조) — DL/비선형 회귀로 팩터 상호작용·비선형 포착. 'Virtue of Complexity'(과파라미터+ridge가 OOS 개선), 'Can Machines Learn Finance'(economic-prior guardrail 필수). 검증강조: 표본외·다중검정 보정. 위치 = 대체 아닌 증강. 우리: 인프라·데이터 부족으로 보류 대상.
4) COST-AWARE OPTIMIZER (위치=포트폴리오 구성, 가장 이식가치 높음) — 'Machine Learning and the Implementable Efficient Frontier'의 핵심: 알파 예측을 그대로 쓰지 않고 거래비용·구현가능성을 목적함수에 내재화해 "구현가능 효율적 프론티어"를 푼다. 데이터표현: 기대수익 벡터 + 공분산 + 비용함수(거래량의 함수). 예측→포지션 사이에 비용이 1급 변수. 핵심 발견: 비용 내재화 시 "그로스 알파가 강한 모델"이 아니라 "넷-오브-코스트 알파가 강한 모델"이 이김 → 모델 선택 기준 자체를 비용후로 바꿈. 시스템내 위치 = forecast와 execution을 잇는 결정층.
5) EXECUTION LAYER (위치=집행) — 비용최소 알고. 저~중빈도(마이크로초 아님), 우리 "execution=구조참조"와 정렬.
6) NO TSFM/financial-FM/뉴스-event 모델을 주력으로 공개하지 않음 — AQR은 거대 사전학습 시계열·파운데이션 모델보다 해석가능한 팩터+제약된 ML을 선호(블랙박스 경계). 이는 우리 LLM-council 설계(LLM은 알파 기여·비평이지 최종 결정자 아님)와 사상적으로 일치.

**portfolio/risk/execution:** 포트폴리오·리스크·집행 — 이 영역이 AQR이 ₩10M 솔로에게 주는 가장 강한 청사진. 구조: forecast(기대수익) + risk model(공분산·노출) + cost model(거래비용) → OPTIMIZER → 목표 포트폴리오 → 비용최소 집행. 핵심 구조적 통찰 5가지: (1) 알파와 포지션은 동일하지 않다 — 신호 순위를 그대로 비중으로 쓰지 않고, 리스크·비용 제약 하 최적화를 거친다. 솔로가 흔히 빠지는 "신호=주문" 직결의 위험을 구조적으로 차단. (2) COST INTERNALIZATION('Implementable Efficient Frontier'): 거래비용을 사후 차감이 아니라 최적화 목적함수 안에 넣어야 한다 → 우리에겐 KR 세금 0.20% + 슬리피지를 optimizer 비용항으로 모델링해야 한다는 직접 지령. 이것이 KOSPI100(after-cost) 대비 초과수익 north star 달성의 구조적 열쇠. (3) 'Trading Costs of Asset Pricing Anomalies'(Frazzini/Israel/Moskowitz) — 논문상 강한 아노말리도 실거래비용·시장충격 반영 시 capacity가 급감 → 회전율이 높은 신호(단기 momentum/reversal)는 솔로 규모에선 비용에 잡아먹힐 수 있다는 경고. 우리 함의: swing/mid-long(저회전)을 코어로, 단기 급등주는 회전율·비용을 엄격히 통제한 scanner+rank로만. (4) RISK 상시계측: "어느 팩터에 얼마나 노출됐나"를 항상 측정 → 우리 risk-engine의 hard-veto 사전조건(팩터 집중·변동성 한도)을 정의하는 틀. (5) market-neutral/long-short는 AQR 기본형이나 우리 brief는 long 편향+제한적 L-S라 — 비중제약·중립화 사상은 차용하되 풀 long-short 레버리지는 버린다. 집행은 저빈도라 우리 cloud-GPU+PC 인프라로 충분.

**검증 규율:** 검증 규율 (leakage/walk-forward/deflated-sharpe/multiple-testing) — AQR의 검증 사상이 우리 LLM-council의 adversarial-critic(leakage/overfit 비평) 역할의 직접 원형이다. 공개된 검증 원칙 5축: (1) ECONOMIC PRIOR FIRST — 신호는 데이터에서 발굴되기 전에 경제 가설로 정당화돼야 한다. 사후 데이터마이닝으로 찾은 패턴은 신뢰하지 않는다(multiple-testing/data-snooping 방어의 1차 방벽). 'Can Machines Learn Finance'의 핵심 메시지 = 금융 데이터의 signal-to-noise가 극도로 낮아 충분한 변수를 던지면 우연한 in-sample 패턴이 반드시 나온다 → 경제 이론이 guardrail. (2) GLOBAL/MULTI-ASSET OUT-OF-SAMPLE — 'Fact, Fiction and Momentum Investing'처럼 한 시장·기간에서 발견한 팩터를 다른 국가·자산군·기간에 재현해 robustness 확인(자연적 walk-forward + cross-validation). (3) NET-OF-COST 기준 — 'Implementable Efficient Frontier'는 모델 우열을 gross가 아닌 거래비용 차감 후로 판정 → "비용 전 샤프"의 함정 차단. (4) 장기 드로다운 허용 = 검증의 일부 — quant winter에 팩터가 수 년 underperform해도 그것이 "모델 고장"인지 "정상적 레짐 비용"인지 구분(Asness 'Is Systematic Value Investing Dead?', 'Factor Timing'). 즉 OOS underperformance를 즉시 reject하지 않는 메타 검증. (5) FACTOR TIMING 경계 — 밸류 스프레드 등으로 팩터를 타이밍하려는 유혹("sin a little")을 매우 제한적·신중하게만 인정 → 과최적화의 또 다른 입구 차단. 우리 시스템 이식: walk-forward + deflated Sharpe + 다중검정 보정 + 비용후 평가를 백테스트 게이트로 강제하고, LLM-council이 "이 신호가 경제 가설을 통과하는가 / in-sample 데이터마이닝 냄새가 나는가 / 비용후에도 살아남는가 / 레짐 underperformance인가 진짜 고장인가"를 사전정의 체크리스트로 비평하게 한다. 단 deflated-sharpe라는 용어 자체는 Bailey/López de Prado 것이고 AQR이 그 명칭을 쓴다는 직접 증거는 없음 — AQR이 강조하는 것은 OOS·글로벌 재현·비용후 평가다 [INFERENCE 경계 명시].

**솔로가 배울 점 (lessonsForSmall):** ₩10M KR-swing 시스템이 현실적으로 벤치마킹할 것 (이식가능/비이식 분리):
이식 가능(HIGH 가치):
1) FACTOR LOGIC — KOSPI100 종목에 value(저PBR/PER/PCR composite) + momentum(6-12개월 수익률) + quality(ROE·이익안정성·저부채)를 cross-sectional rank로 산출. 공개 가격+재무제표만으로 구성 가능 → 솔로 적용성 최고. swing+mid/long 정렬.
2) 신호 분산화 — 단일 급등주 신호 금지, 저상관 팩터 앙상블. value↔momentum 음의 상관 활용.
3) COST-AWARE 비중결정 — KR 세금 0.20%+슬리피지를 optimizer 비용항에 넣어 net-of-cost로 종목·비중 결정. 회전율 낮은 swing 코어 우선, 비용에 약한 고회전 단기신호는 통제.
4) RISK-ENGINE 사상 — 팩터노출·변동성 상시계측 → hard-veto 사전조건 정의. 신호≠주문, 항상 리스크·비용 게이트 통과.
5) GOVERNANCE/검증 — economic-prior 통과 + 글로벌/다기간 OOS + net-of-cost 평가를 백테스트 게이트로. LLM-council이 leakage/overfit/regime/cost를 사전정의 체크리스트로 비평(최종 결정자는 risk-engine·optimizer, LLM은 그 위 review층) — AQR 거버넌스 사상과 정확히 일치.
6) DRAWDOWN 사상 — 25% MDD는 강한 선호지 즉시 kill 트리거 아님. 팩터는 수 년 죽을 수 있다(quant winter 교훈) → 드로다운≠고장, 사전정의 구조적 risk 조건에서만 개입.
비이식(버릴 것): 거대 AUM·기관 LP·멀티에셋 풀스택·고레버리지·alt-data 인프라·풀 long-short market-neutral·상품화(Apex/Delphi 등). 적용성은 "청사진 가치 HIGH / 직접 복제 가능성 LOW"로 분리 평가. 핵심 한줄: AQR은 9개 타깃 중 유일하게 우리가 논문으로 복제할 수 있는 cross-sectional factor + cost-aware optimizer + governance 청사진을 주는 곳 — 규모·인프라는 버리고 로직·검증규율·거버넌스만 가져온다.

**공개자료 한계:** 공개 한계 (adversarial): (1) 논문 ≠ 라이브 시스템 — AQR이 공개한 것은 팩터 정의·연구 프레임·철학이지 production 신호 가중치·optimizer 파라미터·ML 비중이 아니다(영업비밀, group A 정상). 우리는 "구조와 사상"만 확정 인용 가능. (2) 2024 수익률(Apex +15.1%/Delphi +14.6%/Helix +14.2%/top ~+71%)은 audited NAV가 아니라 Tier2 언론 인용 추정치 — 정확한 net-of-fee·시점은 투자자 서한에만. (3) +71% top fund는 전략·자본규모 미상 → 작은 sleeve면 cherry-pick 위험, 대표성 주의. (4) AUM ~$120B/$128B 출처별 편차(시점·집계 차이). (5) mode-switch/kill-switch는 공개 명시 없음 → 우리 매핑은 quant winter 행동에서의 INFERENCE이지 확인된 메커니즘 아님. (6) 'deflated Sharpe' 같은 특정 검증 명칭은 AQR이 쓴다는 직접 증거 없음 — AQR이 명시하는 것은 OOS·글로벌 재현·net-of-cost 평가 (용어 귀속 주의). (7) 근본 한계: AQR은 기관·대형 AUM·멀티에셋·레버리지 전제 → ₩10M 솔로엔 규모경제·집행인프라·상품화 비이식. 적용성 점수는 청사진(HIGH)과 직접복제(LOW)를 반드시 분리해야 과대평가를 피함.



### A2. Man (AHL+Numeric)  ·  [대형 systematic 운용]

**선정 이유:** Group A 9개 후보 중 Man을 선정·유지하는 이유 = 'profit-verifiability'가 압도적으로 높다.

(1) 유일한 진정한 Tier1 audited 기업단위 수익 증거: Renaissance(Medallion 비공개), D.E.Shaw·Two Sigma(사모, 13F/규제만), AQR(사모) 대비 Man은 LSE 상장사라 감사 annual report·interim·RNS로 statutory profit, management+performance fee 매출, AUM이 정기 공시. 본 세션에서 FY2024·FY2025 수치를 1차/언론 소스로 직접 검증. course-seller/cherry-pick/survivorship 우려 = 기업단위 사실상 0.

(2) Structure-knowability = HIGH: AHL은 공개적으로 double-EWMA·~400시장·vol-scaling·ML(2014~)로 기술; Oxford-Man Institute(Oxford Engineering Science 내, 2016~ ML 집중, AHL Oxford Research Lab과 동건물)가 공개 ML 연구 산출; Numeric은 FRP/EBC/TIA·black-box/glass-box risk 모델을 공개 기술. 비밀주의 샵(RenTech) 대비 거버넌스·리스크 프로세스가 압도적 투명 → 상장사 governance/risk-process 공시 분석이 우리 'LLM-as-review-layer 위 risk-engine' 설계에 직접 참조.

(3) 장기 record bar 통과: AHL Diversified = 세계 최장수급 managed-futures(공개 track record ~20년+), 2008 GFC +33.23%·2020 COVID +11.34% 위기장 crisis-alpha 검증.

(4) 우리 적용: AHL trend=선물이라 구조 참조이나, Man Numeric cross-sectional equity 파이프라인(factor→forecast→optimizer→risk→cost-aware execution)은 KOSPI100→US 주식 swing/mid-long 코어에 거의 그대로 매핑. 결론 = 명확한 PASS.

**검증/성과 근거:** [정정: 브리프 추정 FUM ~$175–185B는 부정확. 실제 FY2024 AUM=$168.6B, FY2025=$227.6B(record). 이 값이 정확.]

기업단위 (Tier1 audited/RNS — VERIFIED, profit-verifiability HIGH):
FY2024 (2025-02-27 발표):
- AUM $168.6B (2023 $167.5B, flat).
- Core 순운용보수 $1,097M (+14%). Core 성과보수 $310M (2023 $180M).
- Statutory profit $298M (2023 $234M). Statutory PBT $398M; Core PBT $473M (2023 $340M).
- Statutory EPS(diluted) 25.1¢; Core EPS 32.1¢(+17%). Net flows -$3.3B(Q3 단일고객 $7.0B 환매).

FY2025 (2026-02-26 발표 — VERIFIED, 최신):
- AUM $227.6B (record, +35% YoY, +~$60B). Record net inflows(보도상 $28.7B; 단 일부 보도 $12.0B는 일부 카테고리 수치 — 락 전 재확인).
- Core 성과보수 $281M (2024 $310M; trend-following 상반기 부진 후 회복). Run-rate net mgmt fee ~$1,182M; core net mgmt fee revenue $1,077M(-2%, 저마진 systematic long-only 유입으로 product mix 변화 → net mgmt fee margin 63→56bp).
- Statutory profit $175M (2024 $298M 대비 감소; 상장사라 변동 투명). Core PBT $407M, net revenue $1.398B. 성과보수-eligible AUM ~$60B, 61%가 high-water mark 이상.

매출구조 = management fee(AUM기반 안정) + performance fee(성과기반 변동). fee 분해 공시 = 'systematic 운용이 실제 돈 버는가'의 최강 외부검증.

프로그램단위 (Tier1 official이나 vendor 인접 → MEDIUM):
- AHL Diversified: 2008 +33.23%, 2020 +11.34%; 인용 Sharpe ~0.86·MDD ~-17.9%(1996–2009 구간). 전형적 CTA crisis-alpha(위기장 강세, 강한 횡보/급반전 부진).
- Numeric: composite factsheet 존재, 본 세션 정밀치 미확보.

등급: 기업단위 HIGH, 프로그램단위 MEDIUM. course-seller/screenshot/in-sample 우려 없음.

**무엇인가:** Man Group plc는 런던 상장(LSE: EMG) 세계 최대급 상장 systematic·active 자산운용사로, 독립 "엔진(engine)" 브랜드들을 거느린 멀티-부티크 구조다. 35년+ systematic 운용 경험, 약 595명 quant·technologist 보유. 본 분석 핵심 두 엔진:

1) Man AHL — Adam·Harding·Lueck가 1987 창업한 systematic/quantitative 엔진(2017년 30주년). 대표 AHL Diversified는 전통 systematic trend-following CTA에서 multi-strategy(trend + mean-reversion + carry + relative value + options/vol + 비-trend 대안알파)로 확장. [FACT 검증] 거래 유니버스 = 약 400개 liquid 선물·FX(글로벌 주가지수·금리·상품·통화). 일일 약 15억(1.5B) data tick 처리(시장데이터·텍스트·기상도·날씨예보 등 비정형 포함). 추세 코어 = double exponentially-weighted moving average(double-EWMA), 보유기간 약 1~3개월(중기). 2014년 초부터 multi-strategy 고객 포트폴리오에서 ML 기반 시스템 실거래(약 5년 선행연구 후). [FACT 검증]

2) Man Numeric — 보스턴 기반 cross-sectional quantitative equity 매니저(2014.9 Man 인수, AUM ~$45B 규모로 보고). valuation·quality·momentum·information-flow·sentiment·estimate-rev 등 factor를 종목 횡단면에서 결합, 다수의 비상관 idiosyncratic alpha 모델(8개 투자테마)로 systematic long-only·long-short 구성. 전략 분류: FRP(factor risk premia, 종목별 return forecast 필요) / EBC(enhanced beta capture, risk view만 필요) / TIA(true idiosyncratic alpha). risk model을 포트폴리오 구성 과정에 내장(black-box 통계학습 + glass-box 인간정의 forward-looking factor 결합). 2019 초부터 ESG 신호를 alpha 모델에 직접 통합. → 우리 시스템(KR/US 주식 횡단면 swing/mid-long)에 in-scope·직접 이식 가치 최고. [FACT 검증]

(부가) Man GLG=디스크레셔너리, Man FRM=펀드오브펀즈, Credit 플랫폼 AUM ~$35.0B — 분석 범위 밖.

**거시 아키텍처:**

END-TO-END 레이어드 구조 (AHL multi-strat + Numeric quant equity 공통, 우리 매핑 관점):

[L0 데이터/유니버스]
- AHL: 일 ~15억 tick(약 400 선물·FX 가격·거래량 + 텍스트·기상도·날씨 등 비정형). Numeric: 주식 가격·호가·거래량 + 펀더멘털·analyst estimate·broker recommendation + ESG·대안데이터. point-in-time·survivorship 보정. Oxford-Man Institute = research-feed(천문 Galaxy Zoo ML 기법을 broker rec 신호추출에 이식 등). [FACT 검증]

[L1 시그널/알파]
- AHL: instrument별 double-EWMA trend(1~3개월) + mean-rev + carry + relative value + options/vol + ML 앙상블. ML 코어철학 = "다수의 약한(weak) 정보원을 결합해 개별 소스보다 강한 signalling power". [FACT 검증]
- Numeric: cross-sectional factor → 종목별 return forecast(alpha), 8개 테마·비상관 idiosyncratic alpha 모델, FRP/EBC/TIA 분류. [FACT 검증]
- [LLM 적용지점: news/filings/earnings/event 해석을 '약한 신호' 피처로 — AHL weak-signal-ensemble 철학과 정확히 정합, 우리 council의 alpha-contributor]

[L2 포트폴리오 구성/최적화 (optimizer)]
- alpha forecast + risk model(covariance·factor exposure) + 제약(섹터/유동성/회전율/포지션한도)을 optimizer가 받아 목표비중 산출, turnover·거래비용 내장(cost-aware). Numeric: "risk model이 포트폴리오 구성 과정에 내장된 1차 리스크관리 도구", black-box(통계학습)+glass-box(인간정의 forward-looking factor) 결합. = '최종 사이즈 결정자'. [FACT 검증]

[L3 리스크 엔진 (optimizer 위/병렬)]
- AHL의 3대 리스크완화 기법: ① volatility targeting/scaling(목표변동성 고정 → 저변동성기 레버리지↑·고변동성기 exposure↓, MDD·left-tail 완화) ② momentum overlays ③ bond/equity correlation triggers. + 독립 Risk team(1987~ 자체시스템)이 모델과 별도 감독. risk-engine이 optimizer 출력에 hard 제약. → 우리 핵심참조: risk-engine=거버넌스 최상위, LLM은 그 '위'가 아닌 '검토층'. [FACT 검증]

[L4 실행 (execution)]
- cost-aware 알고(metaorder→child order 분할, transient price impact 최소화, sequential-trade 비용 최적화 — Man 공개 연구·특허). 저비용·고용량 실행 인프라 자체가 알파의 일부. [FACT 검증]

[L5 거버넌스/오버사이트]
- 상장사 = 투자위·리스크위·모델 거버넌스·컴플라이언스가 자동 파이프라인 위 review/veto. "정량모델과 인간 oversight 균형"을 Numeric이 명시. → 우리 'LLM-as-review-layer + human gate' 매핑 자리. [FACT 검증]

핵심: L1→L2→L3→L4 자동, 인간/거버넌스(L5)=review·예외·승인만. [구조=FACT(다수 공개기술 검증) / 내부 가중치·코드=비공개 INFERENCE]

**데이터 흐름:** 데이터 흐름 (raw → 주문 → 피드백):

1) 수집: AHL=일 ~15억 tick(약 400 선물·FX + 텍스트·기상도·날씨 등 비정형); Numeric=주식 가격·호가·거래량 + 펀더멘털·estimate·broker rec + ESG·대안데이터. point-in-time·survivorship 보정 정규화. [FACT 검증]

2) 시그널 생성: AHL=instrument별 double-EWMA trend(1~3개월)+mean-rev/carry/relative-value/options-vol+ML 앙상블(약한신호 다수→강한신호, 2014~); Numeric=종목별 factor 결합→return forecast(alpha), 8테마 비상관 idiosyncratic 모델. [FACT 검증] [LLM 적용: news/filings/earnings/event 해석을 '약한 신호' 피처로 — weak-signal-ensemble 철학과 정합, council의 alpha-contributor]

3) 리스크 모델: covariance·factor exposure·유동성 갱신. Numeric=black-box(통계학습)+glass-box(인간정의 forward-looking factor) 결합, risk model이 포트폴리오 구성에 내장. [FACT 검증]

4) 최적화: alpha + risk model + 제약(turnover·비용·한도) → optimizer → 목표포지션(cost·turnover 내장). [FACT 검증]

5) 리스크 엔진 게이팅: volatility targeting/scaling + momentum overlay + bond-equity correlation trigger + 독립 Risk team 감독을 목표포지션에 hard-apply → 승인 포지션. (LLM review-layer가 leakage/overfit/regime/tail 적대비평을 '여기 위'에 부착, 최종결정 비대체.) [FACT 검증]

6) 실행: cost-aware 알고(metaorder→child order, transient impact 최소화) → venue 집행. [FACT 검증]

7) 피드백: 체결·P&L·슬리피지·factor 성과 모니터링 → research-feed(Oxford-Man Institute) 환류, 모델 재학습/검증은 거버넌스 게이트 통과 후 재배포. [FACT 패턴]

[FACT: 7단계는 Man 공개기술(double-EWMA·~400시장·15억tick·vol-scaling·ML·OMI·execution 연구·black/glass-box) 다수 검증 / 내부 구체 피처·가중치·재학습주기=비공개 INFERENCE]

**자동화 수준:** HIGH(거의 완전 자동) — systematic 엔진(AHL·Numeric) 일상운용은 model→optimizer→risk→execution이 자동 실행, 인간은 '운영·감독'하지 '주문 클릭' 안 함. AHL 명시 철학: "컴퓨터 알고리즘이 추세 식별, 수백 시장 동시 거래, 인간 감정 편향 회피" → 자동화가 알파의 일부. "systematic 접근은 감정적 의사결정을 제거하고 all-or-nothing 대신 점진 조정"(Man 명시). 디스크레셔너리 Man GLG와의 결정적 차이. [FACT 검증]

- 정상 리밸런싱·주문: 자동(인간 사전승인 없이 systematic 파이프라인 생성·집행). → 우리 'normal-orders-auto'와 직접 정합.
- 레짐/변동성 대응: volatility scaling이 시장별 변동성 측정→exposure 자동 조절(저변동성 레버리지↑/고변동성 exposure↓); momentum overlay·bond-equity correlation trigger도 사전정의 규칙 자동 발동. Numeric regime model이 레짐별 factor 가중 자동. → 우리 aggressive/stable/conservative 모드-스위치의 '자동 스케일링' 대응. 사전정의 조건 내 자동, 밖이면 인간.
- 모델 배포·변경: 자동 아님 — 모델 거버넌스/검증·승인(인간) 필수(ML도 2014 라이브 전 ~5년 검증).

[FACT: systematic 자동운용·vol-scaling·디스크레셔너리 분리 = 공개검증 / 내부 자동화 정밀도=비공개 INFERENCE]

**인간 개입 지점:** 우리 거버넌스 5포인트 매핑:

- normal-orders-auto: ✅ 완전 자동. systematic 엔진이 정상 리밸런싱·주문을 인간 사전승인 없이 생성·집행. AHL 명시(알고가 수백 시장 동시거래, 인간감정 배제) = 인간은 감독자, 주문 비클릭. [FACT 검증]

- mode-switch (aggressive/stable/conservative): 부분 자동. volatility scaling/targeting·momentum overlay·bond-equity correlation trigger가 '사전정의 조건' 내에서 리스크/레버리지/exposure를 자동 조정(=조건부 자동 모드전환); Numeric regime model이 레짐별 factor 가중 자동 전환. 사전정의 밖 구조적 레짐 대전환·전략 비중변경은 투자/리스크위(인간). → 우리 규칙 '사전정의면 자동, 아니면 인간승인'과 정확히 일치. [INFERENCE: 정확 임계선 비공개]

- deploy-approval (전략 배포): 인간 필수. 신규 모델/시그널/전략은 모델 거버넌스·검증·투자위 승인 후 라이브(ML도 2014 라이브 전 ~5년 연구·검증). 상장사라 절차 공시 분석 가능 — 우리 deploy-gate 핵심 참조. [FACT 패턴 검증]

- risk-limit-approval: 인간(리스크위 + 독립 Risk team, 1987~ 자체시스템). 포지션·집중·레버리지·vol-target 한도 설정·변경은 거버넌스 승인. 일상 한도 '준수'는 risk-engine 자동 enforce(model과 별도 독립 risk team이 감독), 한도 '변경'은 인간. [FACT 검증]

- kill-switch (긴급정지): 인간 + 사전정의 트리거. 극한 drawdown·시장 stress·운영장애 시 자동 디리스킹(vol-scaling이 고변동성기 exposure 자동 축소 = soft kill에 해당) + 인간 오버라이드. [INFERENCE: 명시적 kill trigger 내부 비공개, soft-de-risking은 FACT]

요약: 인간 개입 = 예외·모드 대전환·전략배포·리스크한도·킬스위치에 집중, 정상주문 자동 — 우리 타깃 거버넌스와 거의 1:1. [구조 패턴 FACT, 내부 임계·구현 INFERENCE]

**데이터 사용:** 데이터 사용 (raw → 표현형):

[AHL — futures/FX 시계열 중심]
- 규모: 일 ~15억(1.5B) tick. 약 400개 liquid 선물·FX(글로벌 주가지수·금리·상품·통화)의 가격·거래량이 코어.
- 비정형 확장: 텍스트(뉴스), 기상도·날씨예보 등 alternative data를 '약한 신호(weak signal)' 원천으로 흡수. 단일 강한 데이터셋이 아니라 다수의 약한 소스를 의도적으로 쌓는 철학.
- point-in-time·survivorship 보정이 전제(시계열 정규화·look-ahead 차단).

[Numeric — cross-sectional equity 패널]
- 종목 횡단면 패널: 가격·호가·거래량 + 펀더멘털(valuation·quality) + analyst estimate·estimate revision·broker recommendation + sentiment/information-flow + ESG(2019~ alpha 모델에 직접 통합) + 대안데이터.
- 데이터 = 종목×시점×피처 매트릭스로 표현. 이것이 우리(KR/US 주식 swing/mid-long)와 정확히 같은 데이터 형상.

[우리 시스템(₩10M, KOSPI100→US) 매핑]
- AHL의 15억 tick·400시장은 직접 이식 불가(인프라·데이터 비용). 그러나 '데이터 표현형'은 차용 가능: 종목×시점×피처 패널(Numeric형)이 우리 코어 표현. 대안데이터는 'LLM이 읽는 비정형(공시·뉴스·실적콜)'을 weak-signal 피처로 변환하는 형태로만 도입. point-in-time/survivorship 보정은 소자본에서도 반드시 강제해야 할 비협상 항목(데이터 품질이 알파보다 선행).
[FACT: 15억 tick·400시장·ESG 2019·broker rec 검증 / 내부 피처셋·가중치 INFERENCE]

**alpha 생성:** 알파 생성 접근 (구조적 위치 중심):

핵심 철학 = "다수의 약한(weak) 정보원을 결합해 개별 소스보다 강한 signalling power" (AHL 명시). 단일 천재 시그널이 아니라 비상관 약신호의 앙상블이 알파의 본질.

[AHL — multi-strategy 알파 스택]
- instrument별 double-EWMA trend(보유 1~3개월, 중기) = 코어. trend는 '느린 EWMA - 빠른 EWMA' 형태의 추세 추정.
- + mean-reversion + carry + relative value + options/vol + 비-trend 대안알파를 합산(diversified payoff). 즉 trend의 횡보장 약점을 다른 payoff로 보완.
- ML(2014~ 실거래, ~5년 선행연구)이 약신호 앙상블을 묶는 상위 결합층.

[Numeric — cross-sectional alpha]
- valuation·quality·momentum·information-flow·sentiment·estimate-revision factor를 종목 횡단면에서 결합 → 종목별 return forecast(alpha).
- 8개 투자테마의 비상관 idiosyncratic alpha 모델. 분류: FRP(factor risk premia, 종목별 return forecast 필요) / EBC(enhanced beta capture, risk view만 필요) / TIA(true idiosyncratic alpha).

[LLM-council 적용지점 — 정확히 정합]
- news/filings/earnings-call/event 해석을 '약한 신호 피처'로 생성 → AHL weak-signal-ensemble 철학과 1:1 매핑. 우리 council의 alpha-contributor가 바로 이 '추가 약신호 1개' 역할.
- 중요: LLM은 알파 '기여자'이지 결정자가 아님. AHL/Numeric에서도 어떤 단일 신호도 optimizer/risk를 우회하지 못함 → 우리 'LLM이 최종 사이즈 결정 못 함' 원칙의 외부 근거.

[우리 적용]
- swing/mid-long 한정: AHL trend(1~3개월)는 우리 swing/mid-long horizon과 일치 → trend+carry류 약신호를 KOSPI100 횡단면에 단순화 이식 가능. mean-reversion은 단기라 신중.
- Numeric cross-sectional factor 결합 = 우리 코어. valuation/quality/momentum/estimate-revision은 KR 데이터로도 구성 가능한 표준 팩터.
[FACT: double-EWMA·8테마·FRP/EBC/TIA·weak-signal 철학·ML 2014 / 정확 팩터 가중·신호식 INFERENCE]

**모델·표현:** 모델·표현 (데이터표현 + 예측문제 + 검증 + 시스템내 위치):

[1] AHL trend core — double-EWMA
- 데이터표현: instrument별 일별 가격 시계열.
- 예측문제: 방향성 추세 강도(부호+크기) 추정 → 포지션 부호·크기로 직결되는 regression형 신호.
- 위치: L1 시그널층. 단독으로 포지션 못 정함 — vol-scaling·optimizer 하류.

[2] AHL ML 앙상블 (2014~)
- 데이터표현: 다수 약신호(가격·텍스트·alt) 피처 벡터.
- 예측문제: 약신호 결합 → 강한 signalling power(앙상블 forecast). 특정 천문 ML 기법(Galaxy Zoo류 분류기)을 broker-recommendation 신호 추출에 이식한 사례 — 즉 도메인외 ML 패턴을 금융 약신호 추출로 transfer.
- 검증: 라이브 전 ~5년 연구·검증(deploy-gate 통과 필수) — 과적 방지의 시간적 게이트.
- 위치: L1 결합층, 여전히 L2/L3 하류.

[3] Numeric cross-sectional forecast (black-box + glass-box)
- 데이터표현: 종목×피처 패널.
- 예측문제: 종목별 횡단면 상대 return forecast(cross-sectional ranking/forecast). 절대수익 아닌 '동종 대비 상대' 예측 → 우리 KOSPI100 랭킹과 동일 문제구조.
- 모델표현: black-box(통계학습/ML, 패턴 발굴) + glass-box(인간정의 forward-looking factor, 해석가능·경제논리). 두 축을 의도적으로 병치 — 순수 ML의 비해석성·과적 위험을 인간 팩터로 견제. 이것이 우리 'risk-engine + LLM-review 이중구조'와 철학적으로 정합.

[4] Risk model (Numeric, 구성과정 내장)
- 데이터표현: covariance·factor exposure 매트릭스.
- 위치: 단순 사후 측정이 아니라 "포트폴리오 구성의 1차 리스크관리 도구"로 optimizer 내부에 박힘 → 알파forecast와 risk가 동시에 최적화에 들어감.

[5] Optimizer (L2) — '최종 사이즈 결정자'
- 예측문제 아님(결정문제): alpha forecast + risk model + 제약(섹터/유동성/turnover/포지션한도) + 거래비용(cost-aware)을 받아 목표비중 산출.

[6] Risk engine (L3) — vol targeting/scaling + momentum overlay + bond-equity correlation trigger. optimizer 출력에 hard 제약. 독립 Risk team(1987~) 별도 감독.

[7] Execution model (L4) — metaorder→child order 분할, transient price impact 최소화, sequential-trade 비용 최적화(공개 연구·특허). 저비용 실행 자체가 알파.

핵심: 어떤 모델도 단독 결정 안 함 — 신호(L1)→최적화(L2)→리스크(L3)→실행(L4)의 명확한 책임 분리. 우리는 이 '레이어 책임분리'를 그대로 차용하되 각 층을 대폭 단순화.
[FACT: double-EWMA·black/glass-box·risk내장·execution 연구 검증 / 내부 모델구조 INFERENCE]

**portfolio/risk/execution:** 포트폴리오·리스크·실행 (L2~L4 + 거버넌스 L5):

[L2 포트폴리오 구성 = 최종 사이즈 결정자]
- optimizer가 alpha forecast + risk model(covariance·factor exposure) + 제약(섹터/유동성/회전율/포지션한도) + 거래비용을 동시에 풀어 목표비중 산출. turnover·cost가 목적함수에 내장(cost-aware) → 신호가 좋아도 비용이 먹으면 거래 안 함.
- → 우리 핵심 교훈: '신호 → 곧장 주문'이 아니라 반드시 비용·리스크 인지 최적화 한 단계를 거친다. ₩10M·KR tax 0.20%에선 turnover 패널티가 특히 결정적(과회전이 소자본 알파를 즉사시킴).

[L3 리스크 엔진 — optimizer 위/병렬, hard]
- 3대 기법: ① volatility targeting/scaling(목표변동성 고정 → 저변동성기 레버리지↑·고변동성기 exposure↓, MDD·left-tail 완화) ② momentum overlay ③ bond/equity correlation trigger.
- 독립 Risk team(1987~ 자체시스템)이 모델과 '별도로' 감독 = 모델과 리스크의 조직적 분리.
- → 우리 설계 최상위 원칙: risk-engine이 거버넌스 최상위, optimizer 출력을 hard 제약. LLM은 그 '위'가 아니라 '검토층(review)'.

[L4 실행]
- cost-aware 알고: metaorder를 child order로 분할, transient price impact·sequential 비용 최소화(공개 연구·특허). 실행 인프라가 알파의 일부.
- → 우리: 기관급 실행 불가하나 '주문 분할·시장가 회피·체결비용 추적'의 단순 버전은 소자본도 구현 가치 높음.

[L5 거버넌스/오버사이트]
- 상장사 = 투자위·리스크위·모델 거버넌스·컴플라이언스가 자동 파이프라인 위 review/veto. Numeric이 "정량모델과 인간 oversight 균형" 명시.

[성과 증거 — risk 효과 검증]
- AHL Diversified crisis-alpha: 2008 GFC +33.23%, 2020 COVID +11.34%. 인용 Sharpe ~0.86·MDD ~-17.9%(1996–2009 구간). vol-scaling이 위기장 left-tail 완화에 기여 = 우리 MDD 25% 선호와 정합 메커니즘.
[FACT: vol-scaling 3기법·독립 risk team·crisis 수익·execution 특허 / 정확 vol-target 임계 INFERENCE. 프로그램단위 수익률 신뢰도 MEDIUM(vendor factsheet 인접)]

**검증 규율:** 검증 규율 (leakage/walk-forward/multiple-testing 관점):

[공개로 확인되는 규율 패턴]
- deploy-gate as time-gate: AHL ML은 라이브(2014) 전 ~5년 선행연구·검증. 신규 모델/시그널/전략은 모델 거버넌스·검증·투자위 승인 후에만 라이브 = 과적·우연발견을 시간적·조직적 게이트로 거름. (우리 deploy-approval 게이트의 직접 참조.)
- point-in-time·survivorship 보정 전제 = look-ahead leakage 차단의 데이터층 규율.
- black-box + glass-box 병치 = 순수 ML의 과적·비해석성을 인간 경제논리 팩터로 견제(데이터마이닝 방어).
- model-spread 수익률 공시에 명시적 경고: "거래비용·spread 미반영, sector-neutral, 신호 decay 고려 필요" → in-sample/gross 표시치를 out-of-sample/after-cost로 오독하지 말라는 자가경고. 이는 우리가 backtest를 해석할 때 그대로 적용할 체크리스트.

[INFERENCE — 공개 안 됨]
- walk-forward 분할 방식, deflated Sharpe / multiple-testing 보정(데 Prado류 PBO·DSR) 사용 여부, cross-validation 구체 절차, 재학습 주기, 신호 decay 측정법은 내부 비공개. Man이 학술적 검증 규율을 쓴다는 정황(Oxford-Man Institute ML 연구 산출, model-spread 경고문)은 강하나 정확한 방법론은 추론.

[우리 적용]
- 소자본에서도 강제: ① point-in-time 데이터(미래정보 차단) ② out-of-sample/walk-forward 분리 평가 ③ 다수 백테스트 시 multiple-testing 인지(여러 파라미터 시도 후 best 선택 = 과적, deflated Sharpe로 할인) ④ after-cost(KR tax 0.20% 포함) 평가만 신뢰 ⑤ deploy 전 시간적 게이트(paper/소액 라이브). Man의 '~5년 검증 후 라이브'는 과하나 '게이트 없이 즉시 라이브 금지' 원칙은 그대로.
- LLM-as-adversarial-critic가 leakage/overfit/regime/tail/logic을 검토하는 review-layer 역할 = Man의 조직적 검증 게이트를 1인+AI로 압축한 형태.
[FACT: deploy-gate·~5년검증·point-in-time·black/glass-box·model-spread 경고 / 정확 통계검증 방법 INFERENCE]

**솔로가 배울 점 (lessonsForSmall):** 우리 ₩10M KR-swing 시스템이 현실적으로 벤치마크할 것 (이식가치 순):

[1순위 — 거버넌스 설계 (이식가치 최고, 인프라 무관)]
- Man의 5층 책임분리(신호 L1 → optimizer L2 → risk-engine L3 → execution L4 → governance L5)를 그대로 차용, 각 층 대폭 단순화.
- 인간 개입 = 예외·모드 대전환·전략배포·리스크한도·킬스위치에만(정상주문 자동). Man의 systematic 운용과 우리 타깃 거버넌스가 거의 1:1 → 검증된 패턴.
- LLM = risk-engine '위'가 아니라 '검토층'. Man에서도 어떤 단일 신호/ML도 optimizer·risk를 우회 못 함 = 우리 'LLM 최종결정 금지' 원칙의 외부 근거.

[2순위 — vol-targeting/scaling 기반 자동 모드전환]
- 목표변동성 고정 룰(저변동성기 노출↑/고변동성기 노출↓)은 소자본도 구현 가능한 단순 룰. 우리 aggressive/stable/conservative 모드의 '사전정의 조건 자동 스케일링' 대응. 위기장 left-tail 완화로 MDD 25% 선호에 직접 기여.

[3순위 — weak-signal-ensemble 철학 + LLM 통합]
- 단일 천재 신호 추구 금지, 비상관 약신호 다수 결합. LLM의 공시·뉴스·실적콜 해석을 '약신호 1개'로 추가(alpha-contributor) — Man 철학과 정확히 정합. LLM 단독 결정 절대 금지.

[4순위 — black-box/glass-box 이중구조]
- ML(black-box) + 인간정의 해석가능 팩터(glass-box) 병치 = 우리 'risk-engine(룰) + LLM-review' 이중구조와 정합. 과적·비재현 방어.

[5순위 — cost-aware 최적화 + turnover 패널티]
- 신호→곧장 주문 금지, 거래비용·turnover를 목적함수에 내장. KR tax 0.20% + ₩10M 소자본에선 과회전이 알파를 즉사 → turnover 패널티가 생존 조건.

[하지 말 것 / 한계]
- AHL trend(선물·400시장·15억tick)는 직접 이식 불가 = 구조 참조 only. Numeric cross-sectional equity 파이프라인조차 기관급 데이터·risk model 전제 → '구조 차용 + 대폭 단순화' 필수.
- 프로그램단위 수익률(AHL Diversified·Numeric factsheet)은 신뢰도 MEDIUM(vendor 인접, 비용전/후·통화·인용구간 의존) → 'verified after-cost' 단정 금지. 기업단위 audited(HIGH)와 구분.
- horizon 제약 준수: 우리 알파/모델 교훈은 swing+mid/long(1~3개월 trend, cross-sectional swing)에 한정. HFT/execution latency 인프라는 우리 적용 밖.
[FACT 기반 교훈 / 정확 임계·구현은 INFERENCE]

**공개자료 한계:** 공개 한계·검증 등급:

1) 등급 분리 필수: 기업단위 = Tier1 audited HIGH (LSE 상장 EMG, RNS/annual report). FY2024 AUM $168.6B·core net mgmt fee $1,097M·core perf fee $310M·statutory profit $298M·core PBT $473M. FY2025(2026-02-26) AUM $227.6B(record,+35%)·core perf fee $281M·statutory profit $175M·core PBT $407M·net mgmt fee margin 63→56bp. course-seller/screenshot/in-sample 우려 사실상 0.
   프로그램단위 = MEDIUM: AHL Diversified·Numeric composite factsheet은 official이나 vendor/마케팅 인접. composite·share-class·비용전후·통화·인용구간(Sharpe~0.86·MDD~-17.9%가 1996–2009 등 특정구간)에 따라 표시치 변동 → 'verified out-of-sample after cost' 단정 불가. Man의 model-spread 수익률은 명시적으로 "거래비용 미반영·sector-neutral·decay 고려" 경고 → marketing-adjacent 주의에 부합.

2) 내부 alpha·구현 = 영업비밀: 신호 가중치·정확 vol-target·mode/kill 임계·optimizer/실행 세부·재학습/통계검증 방법론 비공개. 단 AHL은 비밀주의 샵(RenTech) 대비 double-EWMA·~400시장·15억tick·vol-scaling·ML·OMI를 상당 공개 → structure-knowability 자체는 HIGH(우리 구조 참조에 유리).

3) 시점 정합: FY2024(2025-02-27)·FY2025(2026-02-26) 본 세션 검증. 단 FY2025 net inflows 보도원별 상충($28.7B vs $12.0B — 후자는 일부 카테고리/순수치 가능성) → 최종 보고서 락 전 2025 annual report(FCA NSM)로 정확 라인 재확인 권장. (브리프 추정 FUM ~$175–185B는 부정확 → FY2024 $168.6B / FY2025 $227.6B로 정정 완료.)

4) 우리 적용 한계: AHL trend=선물이라 ₩10M·KOSPI100 swing 코어 직접 이식 부적합(구조 참조 only). 직접 매핑은 Man Numeric cross-sectional equity 파이프라인이나 그조차 기관급 데이터·risk model·실행 인프라 전제 → 솔로+AI·소자본은 '구조 차용 + 대폭 단순화' 필수. 최고 이식가치: ①거버넌스 설계 ②vol-targeting 기반 자동 모드전환 ③weak-signal-ensemble(LLM 정합) ④black/glass-box(risk+LLM-review 이중구조 정합).



### A3. Marshall Wace (TOPS)  ·  [대형 systematic 운용]

**선정 이유:** 우리 시스템(scanner → ranking → risk/exec)과 거버넌스 설계(특히 LLM-council의 '애널리스트들'을 historical hit-rate로 가중)의 최고 공개 템플릿이기 때문에 group A에서 선정. TOPS는 사람(또는 모델)이 만든 다수의 trade-idea를 (1) 수집 → (2) 기여자별 과거 성과로 스코어링·가중 → (3) 리스크엔진/옵티마이저가 시스템적으로 집행하는 'alpha capture'의 효시로, 우리가 만들려는 "아이디어 생성층은 약하게 신뢰, 리스크엔진이 최종 통제" 아키텍처와 1:1로 대응한다. 또한 group A 대형·장기 생존(1997~, $60-71B) 요건을 충족하면서, 구조가 예외적으로 잘 문서화돼(press + academic alpha-capture 문헌 교차검증) Phase-0 벤치마킹 대상으로 ROI가 가장 높다. 단, 직접적 HFT/ultra-low-latency가 아니라 minutes~days horizon의 cross-sectional equity L/S라 우리 KR/US 주식 swing+mid/long 코어와 시간축도 맞다.

**검증/성과 근거:** - AUM: US$71B (2024, Wikipedia 인용 infobox); press는 $60-70B로 보도 → 대형·장기 생존(1997~) 자체가 장기 상업적 성공·투자자 유지의 강한 간접 증거(FACT).
- 시드: $50M(이 중 $25M George Soros), 1997(FACT, Wikipedia).
- KKR 24.9% 지분, 2015(FACT, Wikipedia).
- 플래그십 MW Eureka 1998 출시, TOPS 2001 출시(FACT, Wikipedia).
- Eureka 2024 수익률: ~13-14%로 보도(PRESS-RECONSTRUCTED, 직접 검증 불가). audited 실적/공개 investor letter 없음 → profitConfidence = MEDIUM.
- 세계 최대급 long/short equity 펀드 운용이라는 위상은 다수 독립 출처 교차확인(FACT).
종합: 구조 신뢰도(structureKnowable)=HIGH, 수익 검증도(profit-verifiability)=MEDIUM(대형펀드 특성상 audited 미공개).

**무엇인가:** 영국 런던 본사 헤지펀드(1997 설립, Paul Marshall · Ian Wace). 세계 최대급 long/short equity 운용사로, 주식 stock-selection 전략이 코어. 시드 $50M(이 중 $25M이 George Soros) → AUM US$71B(2024, Wikipedia 인용; 일부 press는 $60-70B). 2015년 KKR이 24.9% 지분 인수. 두 축: (a) 1998년 출시 플래그십 MW Eureka(L/S equity), (b) 2001년 출시 TOPS(Trade Optimised Portfolio System) = sell-side 애널리스트/브로커의 trade idea를 수집·스코어링·랭킹해 시스템적으로 집행하는 'alpha capture' 플랫폼. 즉 '시스템적 crowd-sourcing of professional trade ideas + 정량 리스크/포트폴리오 구축'이 정체성.

**거시 아키텍처:**

END-TO-END 레이어(상층=아이디어 생성, 하층=집행, 그 위 거버넌스/리스크):
1) Idea-generation / Contribution layer (alpha sourcing): 전세계 sell-side 브로커·애널리스트가 TOPS 플랫폼에 구체적·실행가능 trade idea를 제출 — 방향(long/short), conviction, time-horizon, 목표가/논거 포함. (=우리 시스템의 scanner + LLM-council '애널리스트'에 대응.)
2) Scoring / Contributor-track-record layer: 모든 idea의 사후 성과를 지속 추적, 기여자를 historical hit-rate·profitability로 점수화. 잘 맞춘 기여자=가중↑, 못 맞춘 기여자=down-weight/탈락. meritocratic·재현가능 신호 정제. (=alpha capture의 핵심, 학술 문헌이 독립 검증한 부분 — "기여자 skill은 persistent, 과거가 미래 idea 품질 예측".)
3) Signal-aggregation layer: 가중된 다수 idea를 cross-sectional 신호로 집계(개별 종목 over/under-weight 스코어 산출).
4) Risk / Optimizer layer (시스템의 실질 두뇌): 집계 신호를 받아 factor-neutral 제약·분산·리스크예산 하에서 포트폴리오를 구성/리밸런싱. 신호는 입력일 뿐, 최종 사이즈·노출은 리스크엔진/옵티마이저가 결정. (=우리 설계의 "LLM은 risk engine 위가 아니라 아래" 원칙과 정확히 동일.)
5) Systematic execution layer: 알고리즘 집행/리밸런스. minutes~days horizon.
6) Discretionary 축(병렬): MW Eureka 등 fundamental L/S — human PM 판단 + 동일 정량 리스크 오버레이. 시스템(TOPS)과 재량(Eureka)이 한 리스크 프레임워크 아래 공존하는 하이브리드.
시간 흐름: TOPS(2001) 이후 더 정교한 데이터/ML 기법과 추가 데이터소스로 확장(broker idea 너머).

**데이터 흐름:** 브로커/애널리스트(또는 우리의 경우 scanner + LLM-council) trade-idea 입력 → TOPS DB 적재(방향·conviction·horizon·논거) → 사후 성과 추적·기여자 스코어링(historical hit-rate) → 기여자 가중 적용 → cross-sectional 종목 신호 집계 → 리스크엔진/옵티마이저(factor-neutral, 분산, 리스크예산 제약) → 시스템적 집행/리밸런스(minutes~days) → 실현 성과가 다시 기여자 스코어 갱신으로 피드백(폐루프). 재량 축(Eureka)은 PM 판단이 신호를 대체하되 동일 리스크 오버레이 통과. 핵심: 신호는 '입력', 리스크엔진이 '최종 통제' — 데이터 흐름상 LLM/사람 아이디어가 리스크엔진 위에 군림하지 않음.

**자동화 수준:** 높음(특히 TOPS 축). TOPS는 신호 집계 → 리스크/옵티마이저 → 집행까지 시스템적·알고리즘적으로 돌아가는 systematic 플랫폼(=normal-orders auto에 해당). 단 전사적으로는 하이브리드: 재량(MW Eureka 등 fundamental L/S)에서는 human PM이 포지션을 판단하고 정량 리스크 오버레이가 그 위에 얹힌다. 즉 '아이디어 생성'은 사람/외부 기여자(또는 모델)에 분산돼 있으나, '집행·사이징·리스크통제'는 자동화된 리스크엔진/옵티마이저가 최종 게이트. 이는 우리 목표(normal orders auto, 리스크엔진이 최상위)와 동일한 자동화 철학.

**인간 개입 지점:** 공개 정보로 정확한 governance 게이트는 비공개(group A=secret-structure)이나, 구조에서 합리적으로 매핑(=inference, 별도 표기):
- normal-orders-auto: TOPS 축은 집계신호→옵티마이저→집행이 시스템적, 즉 통상 주문은 사람 승인 없이 자동(FACT: systematic platform / 세부는 inference).
- mode-switch(aggressive/stable/conservative): 공개 근거 없음(INFERENCE) — 대형 운용사는 통상 리스크·레짐 시그널에 따른 익스포저/그로스 조정 룰을 두나 MW의 구체 모드전환 규칙은 비공개.
- deploy-approval(전략 배포 승인): 신규 기여자/신호의 편입은 track-record 스코어가 임계 통과해야 가중되는 메커니즘이 사실상의 '자동 deploy 게이트'(FACT: contributor scoring) + 상위 신전략 배포는 사람 승인(INFERENCE).
- risk-limit-approval: factor-neutral·분산·리스크예산 제약이 옵티마이저에 내장(FACT: 리스크 오버레이 존재). 한도 변경 자체의 승인 주체는 비공개(INFERENCE: 리스크위원회/CIO).
- kill-switch: 공개 문서 없음(INFERENCE) — 대형 운용사 표준상 존재 가정.
우리 적용 함의: TOPS의 '기여자 점수 임계 통과 시에만 가중' = 우리 LLM-council을 hard-veto/auto-deploy 게이트로 설계할 때 그대로 차용할 공개 템플릿.

**데이터 사용:** 데이터의 핵심 자산은 가격이 아니라 "구조화된 trade-idea 스트림 + 그 기여자의 시계열 성과"다.

[입력 데이터의 표현 (data representation)] TOPS의 1차 데이터는 ~5,000명 sell-side 기여자(53개국, generalist·섹터·strategist·economist)가 포털에 제출하는 구조화된 trade idea다. 한 idea = {direction(long/short), conviction level(확신도 수치), time-horizon(기간), rationale(논거 텍스트), 목표가/논거}의 레코드. 즉 자연어 추천이 아니라 "방향 + 확신도 + 기간"으로 정규화된 행(row)이다 — 이게 핵심: 비정형 의견을 정량 신호로 만들 수 있는 최소 스키마. (FACT, 다수 출처 교차)

[메타-데이터 = 기여자 track record] 더 가치 있는 2차 데이터는 모든 idea의 사후 성과를 추적해 만든 기여자별 성과 패널이다. 단순 hit-rate가 아니라 "섹터/지역/market-regime별 정확도"를 30개 이상 metric으로 분해 추적(FACT). 심지어 기여자의 행동편향(예: winner를 너무 일찍 청산하는 패턴)까지 추적해 사이징에서 보정 — 즉 종목뿐 아니라 *사람*을 데이터로 모델링.

[보상이 곧 데이터 품질 통제] 기여자는 "MW가 그 거래를 집행했는지와 무관하게, 시뮬레이션 성과가 좋으면" 보상받는다(top-decile에 commission flow + 분기 상대-alpha 보너스). 이 설계가 데이터를 self-cleaning하게 만든다: 실행여부가 아니라 예측력 자체에 인센티브 → 기여자가 후행·노이즈 대신 진짜 view를 낸다.

[가격/대체데이터] 시스템 축은 위 idea를 가격·factor 데이터와 결합. 신용(credit) 쪽은 Bloomberg의 ML 기반 실시간 가격(15초 간격, USD/EUR/GBP)을 사용(FACT) — 즉 alt/실시간 데이터로 systematic credit을 보강. 주식 systematic의 정확한 alt-data 목록은 비공개(INFERENCE: 통상 fundamentals·estimates·news·flow).

[우리 시스템 함의] 우리 ₩10M KR-swing은 5,000 브로커가 없다. 대신 "idea 생성원" = 결정론 스캐너(모멘텀·이벤트·갭) + LLM-council의 이벤트/공시 해석. 차용 가능한 정수는: (1) 모든 신호를 {방향·확신도·기간·논거}의 동일 스키마로 정규화해 persist, (2) 생성원(스캐너 룰/LLM 페르소나)별로 사후 hit-rate를 append-only로 적재해 *생성원을 데이터로* 본다, (3) 가중은 의견 강도가 아니라 *과거 검증된 정확도*로. 단 소표본·KR 단일시장이라 regime별 분해는 표본부족 → "insufficient sample" 플래그가 필수.

**alpha 생성:** [알파의 원천 = crowd-sourcing of professional skill + meritocratic re-weighting] TOPS의 알파 가설은 "sell-side 추천은 평균적으로는 가치 없지만, *기여자 skill은 persistent*하고 과거 성과가 미래 idea 품질을 예측한다"이다. 따라서 알파는 개별 idea가 아니라 (a) 다수 idea를 모으고 (b) 검증된 기여자에 가중을 몰아주는 *2단계 정제*에서 나온다. 이 메커니즘(broker trade-idea + 기여자 track-record 가중 → out-of-sample alpha)은 독립 학술 문헌이 검증한 부분(Tier2 papers, MW 고유수치 아님). (FACT 메커니즘 / 학술 검증)

[예측 문제의 정식화 (prediction problem)] 최종 예측 대상은 "개별 종목의 향후 horizon 내 cross-sectional 상대 초과수익"이다. 입력은 종목별로 집계된 가중-idea 점수(가중치 = 기여자 정확도). 즉 회귀/랭킹 문제로 환원: 종목을 over/under-weight 점수로 랭킹. 이는 단일 종목의 절대수익 예측이 아니라 *횡단면 랭킹* — 시장중립 L/S에 직결되고, 우리의 top-N 횡단면 설계와 동형(同型).

[meritocratic tournament] 기여자 간 경쟁(랭킹·보너스·career currency)이 신호 풀의 질을 시간에 따라 끌어올리는 동적 알파 엔진이다. 못 맞추는 기여자는 자동 down-weight/도태 → 신호 풀이 자가-진화. 핵심: "아이디어 생성층은 *약하게* 신뢰, 검증을 통과한 만큼만 가중"이라는 우리 LLM-council 철학의 1:1 공개 템플릿.

[하이브리드 알파] 회사 전체는 ~60% systematic(TOPS) / ~40% fundamental(Eureka). Eureka는 human PM의 fundamental L/S 판단이 알파원이고 동일 정량 리스크 오버레이를 통과 — 즉 "재량 알파 + 정량 리스크통제" 병렬. (FACT: 60/40 systematic/fundamental, 다수 출처)

[우리 시스템 함의 — swing+mid/long 한정] HFT가 아니라 minutes~days horizon cross-sectional L/S라 우리 일~수주 스윙과 시간축이 맞다. 차용: (1) 알파를 "개별 신호 신뢰"가 아니라 "검증된 생성원에 가중을 몰아주는 정제 단계"로 재정의, (2) 절대수익 예측 대신 *횡단면 랭킹*으로 문제를 좁혀 과적합 표면적 축소, (3) 생성원 토너먼트 = 우리 스캐너/팩터/LLM-페르소나를 사후성과로 끊임없이 재가중·도태. 단 ₩10M·KR개인은 공매도 제약 → 시장중립은 인버스ETF/현금으로 근사, L/S full neutral은 불가(이 부분은 차용 제외).

**모델·표현:** 모델을 "이름"이 아니라 (데이터 표현 → 예측 문제 → 검증 → 시스템 내 위치)로 분해:

[① Idea-encoding 모델 (상층, 신뢰 약함)] 비정형 broker view → {방향·확신도·기간·논거}의 구조화 레코드로 인코딩. 시스템 내 위치 = 최상층 alpha-sourcing. 예측력은 단독으로 약하다고 *가정*하는 게 설계 전제. (= 우리 스캐너 + LLM 해석 출력)

[② Contributor-scoring 모델 (정제의 핵심)] 데이터표현 = 기여자×(섹터/지역/regime)별 성과 패널. 예측 문제 = "이 기여자의 다음 idea가 맞을 확률/기대 IC". 검증 = 사후 실현성과로 지속 갱신(폐루프). 위치 = idea와 aggregation 사이의 *게이트/가중기*. 행동편향 보정(early-exit)까지 포함 = 일종의 bias-correction 모델. 이것이 시스템의 진짜 학습 부분. (FACT)

[③ Signal-aggregation 모델 (cross-sectional)] 데이터표현 = 종목별 가중-idea 집계 점수. 예측 = 종목 over/under-weight 랭킹. 위치 = 옵티마이저 입력. 단순 가중합~ML 결합으로 확장(ML 도입은 "점차"라는 정성보도, 구체범위 INFERENCE).

[④ Risk/Optimizer 모델 (시스템의 실질 두뇌)] 데이터표현 = 집계신호(α) + factor 노출 행렬 + 공분산. 예측이 아니라 *제약하 최적화* 문제: factor-neutral·분산·risk-budget 하에서 가중 신호를 포지션으로 변환. 위치 = 신호의 *하류*, 최종 사이징·노출 결정자. ★우리 설계의 "LLM은 risk engine 아래" 원칙과 정확히 동일★. 정확한 factor model·제약 파라미터는 영업비밀(PUBLIC LIMIT). (FACT: 리스크 오버레이 존재)

[⑤ Execution 모델] 알고리즘 집행·리밸런스, minutes~days. 우리 소자본엔 EMS 최소화가 맞아 차용도 적음(structural reference).

[⑥ ML/NLP의 실제 위치] 확인된 ML = systematic credit의 실시간 가격(Bloomberg ML, 15초)(FACT). 주식 쪽 DL/TSFM/financial-FM의 구체 사용은 *공개 근거 없음*(INFERENCE) — "sophisticated 알고리즘"이라는 정성보도뿐. 중요한 교훈: 이 회사의 검증된 edge는 거대 DL이 아니라 *데이터 파이프(기여자 정제) + 리스크엔진*에 있다. 우리도 "무거운 DL/GPU 안 씀" 방침과 정합 — 모델 화려함보다 *생성원 정제 + 결정론 리스크엔진*이 alpha-to-risk 비율의 본질.

[event/news 모델] idea의 rationale·기간은 사실상 event-driven view를 담는 슬롯. 우리 LLM-council의 공시/실적/뉴스 해석이 이 슬롯을 채우되, ②의 사후 hit-rate 게이트를 반드시 통과해야 가중 — 환각 기반 신호 차단의 구조적 장치.

**portfolio/risk/execution:** [포트폴리오 구성 = 신호는 입력, 옵티마이저가 최종 통제] 가중-집계 신호를 받아 factor-neutral 제약·분산·risk-budget 하에서 포지션/리밸런싱을 구성. TOPS의 산출물은 통상 시장중립(market-neutral) L/S 포트폴리오(다수 출처: "optimizes signal flow into market-neutral portfolios"). 즉 베타를 제거하고 *cross-sectional 선택 알파*만 남기는 게 목표. (FACT)

[리스크 = 자동화의 최종 게이트] 통상 주문은 집계신호→옵티마이저→집행이 시스템적으로 흘러 *사람 승인 없이 자동*(=우리 'normal orders auto'와 동일). 신규 기여자/신호는 track-record 점수가 임계 통과해야 가중되는 게 사실상의 '자동 deploy 게이트'(FACT: contributor scoring). factor-neutral·분산·risk-budget이 옵티마이저에 *내장된 제약*이라, 신호가 아무리 강해도 한도 밖으로 못 나간다 — 리스크엔진이 신호 위 군림.

[execution] 알고리즘 집행, minutes~days 리밸런스. 하이브리드: Eureka(재량)는 PM 포지션이 신호를 대체하되 동일 리스크 오버레이 통과 — *한 리스크 프레임워크 아래 systematic+discretionary 공존*.

[거버넌스 매핑 (구조기반 inference, FACT/INFERENCE 구분)] normal-orders-auto = TOPS 축 systematic(FACT 골격/세부 INFERENCE); mode-switch(공/안/보) = 공개근거 없음(INFERENCE); deploy-approval = 점수 임계통과가 자동게이트(FACT) + 상위 신전략은 사람승인(INFERENCE); risk-limit = 제약 내장은 FACT, 한도변경 승인주체는 비공개(INFERENCE: 리스크위원회/CIO); kill-switch = 공개문서 없음(INFERENCE, 대형사 표준상 존재 가정).

[우리 시스템 함의] (1) "신호→옵티마이저/리스크게이트→집행"의 자동주문 흐름을 그대로 차용하되, KR 개인 제약상 옵티마이저는 경량(top-N 가중 + per-name/일손실/gross/max-DD 결정론 게이트)으로 축소. (2) "점수 임계 통과 시에만 가중·배포" = LLM-council을 auto-deploy/hard-veto 게이트로 설계하는 공개 청사진. (3) 시장중립은 인버스ETF/현금 근사(공매도 제약). (4) DESIGN.md의 risk.py·staging.py·capital_policy.py가 곧 우리의 '옵티마이저 위 리스크 오버레이' — MW와 같은 위계.

**검증 규율:** [TOPS의 검증 골격] 모든 idea를 사후 실현성과로 채점하고 그 결과로 기여자를 30+ metric(섹터/지역/regime별 정확도 등)으로 평가 → 가중·도태하는 *지속적·폐루프 out-of-sample 평가*가 본질. 기여자는 "시뮬레이션 성과"로 채점되므로(집행여부 무관), 시스템은 끊임없이 신호를 paper-grade out-of-sample로 검증한다. (FACT)

[누수/과적합 관점 — 본질적으로 누수에 강한 설계] alpha-capture의 구조적 장점: idea는 *시점에 제출*되고(available_at이 자연히 박힘) 성과는 *그 이후* 윈도우로만 채점 → look-ahead가 구조적으로 차단되는 경향. 우리 no-lookahead(피처 available_at, 예측은 결과윈도우 전 로깅)와 같은 원리.

[multiple-testing/deflated-sharpe 리스크] 5,000 기여자 × 다수 idea = 막대한 다중검정 표면. 일부 기여자는 순전히 운으로 상위에 오를 수 있어, *기여자 skill 지속성*(과거가 미래 예측)을 별도 검증해야 진짜. 학술 문헌이 검증한 건 바로 이 "persistence" — 운이 아니라 skill이 persistent하다는 점(Tier2). 즉 multiple-testing을 persistence/out-of-sample로 통제하는 게 alpha-capture의 핵심 규율.

[공개 한계] walk-forward 캘린더·deflated Sharpe·정확한 multiple-testing 보정의 MW 내부 절차는 비공개(PUBLIC LIMIT). 학술 검증은 메커니즘 일반론이지 MW 고유 절차 아님.

[우리 시스템 함의 — DESIGN.md §5와 직결] (1) 생성원 토너먼트를 돌릴 때 우리 표본은 작아 *deflated Sharpe + 시도변종수 사전등록*이 MW보다 *더* 중요(5,000개 표면이 아니라 소수 생성원이라도 파라미터 난사하면 즉시 과적합). (2) walk-forward로 규칙 freeze·파라미터만 사전등록 캘린더로 재적합(refit-snooping 차단). (3) idea를 시점에 persist하고 결과윈도우 *전*에 로깅 = alpha-capture의 구조적 무누수 성질을 그대로 구현. (4) 생성원 가중 갱신도 append-only(불변원칙3) — 결과 본 뒤 가중수식 바꾸면 증거시계 리셋. (5) "persistence 통과 못 하면 운"이라는 alpha-capture 교훈 → 생성원이 임계기간·임계표본 넘기 전엔 가중↑ 금지("insufficient sample").

**솔로가 배울 점 (lessonsForSmall):** 우리 ₩10M KR-swing(solo+AI, KOSPI100 우선, 세금 0.20%, 북극성=비용후 벤치 상회)이 *현실적으로* 벤치마킹할 것 / 버릴 것:

[차용 — high ROI]
1. ★생성원을 데이터로 본다★: 스캐너 룰·팩터·LLM-페르소나 각각을 '기여자'로 취급해 모든 신호를 {방향·확신도·기간·논거} 동일 스키마로 persist하고, 사후 hit-rate/IC를 append-only로 적재. 가중 = 의견강도가 아니라 *검증된 과거 정확도*. (TOPS contributor-scoring의 직접 차용)
2. ★2단계 정제 = 약한신뢰 생성 + 강한게이트★: "아이디어층 약하게 신뢰, 리스크엔진 최종통제" — 우리 불변원칙4(LLM 주문권0)·DESIGN.md 2레이어와 1:1. LLM-council은 점수 임계 통과 시에만 가중되는 auto-deploy 게이트 + 사전정의 위험조건 hard-veto로 설계.
3. ★횡단면 랭킹으로 문제 축소★: 절대수익 예측 대신 top-N 종목 랭킹 → 과적합 표면 축소(MW도 cross-sectional). 우리 §4 top-N 횡단면과 정합.
4. ★보상=예측력 분리★: TOPS는 "집행여부 무관, 시뮬성과로 보상" → self-cleaning. 우리는 LLM/스캐너 신호를 *집행했든 안 했든* 가상으로 성과추적해 생성원 가중 갱신(실집행만 보면 표본 더 부족).
5. ★행동편향 보정★: 생성원별 체계적 편향(예: 특정 팩터가 갭상승 후 과신)을 사후 데이터로 잡아 사이징에서 보정.

[버린다 / 축소 — 우리 조건 부적합]
- 5,000 브로커 crowd 없음 → 외부 idea 풀 불가. 생성원은 내부 스캐너+LLM 소수 → regime/섹터별 분해는 *표본부족* → "insufficient sample" 플래그 필수(없는 통계 만들지 말 것).
- full market-neutral L/S 불가(KR 개인 공매도 제약) → 인버스ETF/현금 근사로 다운그레이드.
- 무거운 ML/옵티마이저 군비경쟁 버림: MW의 검증된 edge도 거대DL 아니라 *데이터정제+리스크엔진*. 우리 'DL/GPU 안 씀'과 정합 — 경량 가중합 + 결정론 리스크게이트.
- HFT/실시간 credit pricing 등 인프라 차용 0(structural reference만).

[냉정한 한계] MW는 audited 수익률·가중수식 비공개(profit-verifiability MEDIUM). 우리가 검증가능하게 차용할 수 있는 건 *구조*(생성원 정제 + 리스크엔진 위계)이지 수익 수치가 아니다. 따라서 우리 점수 기준은 여전히 불변원칙1 — 비용후 벤치 상회를 *우리 실거래*로만 증명. MW 구조는 청사진일 뿐, 수익 증거 대체물 아님.

**공개자료 한계:** group A(대형펀드)의 본질적 한계 — 구조(what & how, 거시)는 잘 알려졌고 숫자(얼마나 잘 버나, 정확히 어떻게 가중하나)는 가려짐:

(1) 가중·스코어링 수식, factor model 구성, 옵티마이저 제약 파라미터 = 영업비밀(비공개). 우리는 *메커니즘*만 차용 가능, 수치 재현 불가.
(2) audited 수익률·share-class별 실적·변동성/MDD 비공개. 공개치는 press-reconstructed(Eureka 2024 ~13-14%, 일부 TOPS 관련 ~22.59% 2024 보도) → profit 직접검증 불가 = profitConfidence MEDIUM의 직접 원인. AUM은 출처별 상이($60-71B Wikipedia/press, ~$75B 최근 press; TOPS 전략 ~$30B 보도) — 수치 자체가 출처마다 흔들림.
(3) governance(mode-switch/kill-switch/risk-limit 승인/배포 승인) 운영 디테일 비공개 → humanInterventionPoints는 구조기반 inference.
(4) 기여자 수·보상구조·ML 적용범위는 '5,000'·'점차 도입' 수준 정성보도만.
(5) 주식 systematic의 ML/DL 실체 미공개(확인된 ML = systematic credit 실시간 가격 한정).

[검증도 종합] structureKnowable = HIGH (idea→scoring→aggregation→risk overlay→exec, systematic+discretionary 하이브리드는 다수 출처 교차확인 + 학술 메커니즘 검증). profit-verifiability = MEDIUM (대형펀드 특성상 audited 미공개, press-reconstructed뿐). 따라서 이 타깃은 *구조 청사진*으로는 group A 최고 ROI이나, *수익 증거*로는 신뢰 보류 — 우리 북극성(비용후 벤치 상회)은 MW 수치가 아니라 우리 실거래로만 증명해야 함.



### B1. XTX Markets  ·  [프론티어 MM/prop]

**선정 이유:** 브리프 MANDATORY-INCLUDE이며 Group B 핵심 아키타입을 가장 깨끗하게 보여줌. (1) 다른 1티어 MM(Citadel Securities/Jane Street/HRT/Jump)이 latency·시장미시구조·복합 사업라인을 섞는 데 비해 XTX는 의도적으로 "순수 ML/통계 예측엔진 + 마켓메이킹 배포"라는 단일·선명한 구조라 '구조 학습'에 최적 표본. (2) 프로핏 검증이 MM 중 이례적으로 강함 — UK Companies House 감사 법정회계(Tier1)에서 절대 순이익이 나와 net-income/volume/share만으로 PASS하는 일반 MM보다 한 단계 위. (3) 우리 시스템과 매핑이 가장 직접적 — "중앙 ML 예측 레이어 → 실행 레이어 분리" + "cluster/cloud-GPU를 학습 전용으로" 패턴이 우리(solo+AI, cloud-GPU 학습, KR/US 주식 swing+mid/long)의 미니어처 청사진. 가져올 것 = 학습/실행 분리 구조 + 예측을 단일 중앙자산으로 두는 cross-asset 발상. 버릴 것 = 25k GPU·마켓메이킹·초저지연(우리 규모·전략 무관, STRUCTURAL reference만). 참고: Citadel Securities 2024 트레이딩 매출 $9.7B 대비 XTX는 여전히 작은 편이나, "단일 예측엔진 구조"의 명료성 때문에 학습가치는 최상.

**검증/성과 근거:** [FACT — Tier1 감사 법정회계 기반] FY2024 순이익(net profit) £1.28B(기록), 전년 £835M 대비 +54%. 매출(revenue) ~£2.74B(약 $3.53B), YoY +37%(일부 출처 +36%). 3개 UK 엔티티 분해: XTX Markets Technologies 매출 £2.04B(+50%)·순익 £1.2B(+44%); XTX Markets Trading 매출 £636M(+7%)·순익 £22.5M(+50%); XTX Markets Limited 매출 £61M. 이 수치는 UK Companies House 감사 statutory accounts에서 산출 — private MM으로서 이례적으로 강한 Tier1. Bloomberg(2025-04-04 "Gerko's XTX Markets… $3.53 Billion")가 독립 재구성한 Tier2와 일치, financemagnates·globaltrading·TradingView 등 다수 Tier2 교차확인.
[FACT — 규모/지위, 복수 출처] 일 ~$250B 거래(35개국), spot-FX top-3 MM(7년 연속)·세계 최대급 eSpot FX LP, pan-European 주식 일일 14%+ 유동성 공급.
[FACT — 인프라, Tier2 엔지니어링] TernFS 오픈소스(2025-09); 데이터셋 650PB 초과(배포 500PB+/30k 디스크/10k 플래시/3 DC), ~25,000 GPU(주로 Nvidia) + ~100,000 CPU 코어, >1T data points/day, XTY Labs ML 연구부문(2024), €1B 핀란드 DC(초기 22.5MW, 2026). 인력: XTX Technologies 113명 평균 보수 £435,814(+33% YoY) — 극소수 인원의 초고생산성.
[검증 한계] profitConfidence high의 근거는 "수익률(returns)"이 아니라 "절대 순이익이 감사·검증"된다는 점. MM 특성상 strategy-level 수익률·Sharpe·MDD는 외부 직접 검증 불가 — 우리 north star(after-cost 수익률, MDD)와 직접 비교 가능한 지표는 미공개.

**무엇인가:** XTX Markets는 런던 본사의 비상장(private) 양적·알고리즘 트레이딩 회사이자 글로벌 1티어 마켓메이커/유동성공급자(liquidity provider)다. 2015년 前 Deutsche Bank 트레이더 Alex Gerko가 창업. 핵심 정체성은 "초저지연 경쟁(latency race) 회사"가 아니라 **중앙 ML/통계 리서치 조직이 학습한 가격 예측(price forecast) 시그널을 마켓메이킹이라는 배포 표면(deployment surface) 위에서 산업 규모로 자동 실행하는 회사**다. 회사 스스로 50,000+ 금융상품(주식·채권·FX·상품·크립토)에 대해 실시간 가격 예측을 생성한다고 명시하며, 35개국에서 일 ~$250B를 거래한다. 결정적으로 "재량 트레이더(discretionary traders) 없이 AI 의사결정에 전적으로 의존하는 완전 자동 운용"이라고 공개적으로 규정한다 — 즉 사람이 매 주문을 내지 않는 구조. 우리 브리프 Group B(frontier MM/prop) MANDATORY-INCLUDE이며 "순수 ML/통계 구동 예측엔진의 산업 규모 deployment" 아키타입을 대표한다. 우리 시스템(중앙 ML 예측 레이어 → 실행 레이어)의 거대 미니어처 원형이다. 마켓메이킹/HFT 자체는 우리에게 STRUCTURAL reference로만 의미(우리는 swing+mid/long 코어), 차용할 교훈은 "예측 레이어와 실행 레이어의 분리" + "cluster/cloud-GPU를 학습 전용으로 쓰는 패턴"이다.

**거시 아키텍처:**

END-TO-END 레이어드 매크로 구조 (예측엔진 중심, 마켓메이킹은 배포 표면):

[L0 데이터 인입 — Market Data Ingestion]
글로벌 멀티에셋 시세·틱·오더북(order book)·레퍼런스 + sentiment 시그널을 초고빈도 수집. XTX 공개 기준 하루 >1조(1T+) 데이터 포인트. 이 데이터가 학습 파이프라인(오프라인)과 실시간 추론(온라인) 양쪽으로 분기.

[L1 중앙 리서치/학습 레이어 — Central ML Research Org (오프라인, cluster-GPU)]
회사의 진짜 알파 공장. ~25,000 GPU(주로 Nvidia) + ~100,000 CPU 코어 + TernFS(자체개발·오픈소스 분산파일시스템, 데이터셋 650PB 초과·배포 500PB+/30k 디스크/10k 플래시/3개 데이터센터)가 방대한 immutable 과거 데이터 위에서 단기 가격의 미래 방향/분포를 예측하는 통계·ML/딥러닝 모델을 대규모로 학습·재학습. 2024년 전용 ML 연구부문 'XTY Labs'(NLP·시계열 분석 등 원천 알고리즘 연구) 신설. €1B 핀란드 데이터센터(초기 22.5MW, 2026 가동)로 자체 학습 인프라 증설("compute 수요가 가용 leasing 옵션을 초과"). → 산출물 = "학습된 예측 시그널" 모델 아티팩트.

[L2 시그널/알파 레이어 — Learned Predictive Signals]
L1 학습 모델이 실시간 시장 상태를 입력받아 "다음 순간 가격 예측분포"를 마이크로초 스케일로 산출. 이 예측이 회사 중앙 자산이며 50,000+ 상품·다수 시장에 공통 주입되는 단일 두뇌(cross-asset 공유).

[L3 마켓메이킹/실행·인벤토리 레이어 — Deployment Surface (온라인, 저지연)]
예측을 받아 거래장소별 양방향 호가를 자동 제시하고 인벤토리(재고 포지션) 관리. 스프레드 수취가 수익원이나, 가격 책정 자체가 L2 예측에 의해 어느 쪽으로 더 공격적/방어적 호가할지 skew. pan-European 주식 일일 14%+에 유동성 공급, spot-FX top-3 MM(7년 연속).

[L4 거버넌스/모니터링 — Risk & Ops]
포지션 한도·익스포저·자본·시스템 헬스 상시 감시 리스크 엔진·운영. (구체 구현 비공개.)

우리 시스템 매핑: L1+L2 = 우리의 "중앙 ML 예측 레이어"(cloud-GPU 학습 전용), L3 = "실행 레이어". XTX는 둘을 명확 분리하고 GPU는 오직 L1(학습)에만, 실행은 별개 저지연 경로. 이 "학습/실행 분리"가 ₩10M·solo+AI로도 모사 가능한 단 하나의 핵심 구조다(25k GPU·마켓메이킹은 모사 대상 아님).

**데이터 흐름:** 글로벌 멀티에셋 원시 시세/오더북/틱/sentiment (>1T data points/day)
  → [분기 A: 오프라인 느린 루프] TernFS(데이터셋 650PB+)에 immutable 저장 → ~25k GPU + ~100k CPU 코어 클러스터에서 통계/ML/딥러닝 예측모델 대규모 학습·재학습(XTY Labs 원천연구) → 학습된 예측모델 아티팩트
  → [분기 B: 온라인 빠른 루프] 실시간 시장 상태 입력 → 학습된 모델이 50,000+ 상품의 단기 가격 예측분포를 마이크로초 스케일 산출(L2 시그널)
  → 마켓메이킹 엔진(L3)이 예측에 따라 거래장소별 양방향 호가를 skew/사이즈 결정해 자동 제시 → 체결 → 인벤토리/포지션 갱신
  → 체결·포지션 데이터가 리스크 엔진(L4) 모니터링 + 학습 데이터셋(피드백 루프)으로 환류.
핵심: "느린 학습 루프(GPU·배치)"와 "빠른 실행 루프(저지연 호가)"의 이중 루프, 둘을 잇는 매개체가 L2 "학습된 예측 시그널". 우리는 빠른 루프(마켓메이킹)는 버리고 이중 루프 분리 패턴만 차용.

**자동화 수준:** 극도로 높음 — XTX는 "재량 트레이더 없이 AI 의사결정에 전적으로 의존하는 완전 자동(fully automated) 운용"이라고 공개적으로 명시한다(FACT, 회사/Grokipedia·press). 가격 예측·호가 생성·체결·인벤토리 관리는 사람 개입 없이 마이크로초 스케일로 기계가 자동 수행. 사람은 "매 주문 결정"이 아니라 모델 연구(XTY Labs)·학습 파이프라인 설계·리스크 한도 설정·시스템 운영/예외 대응에 위치. 자동화는 실행 루프(L0→L3)에, 인간 지능은 그 위 메타 레이어(L1 리서치 + L4 거버넌스)에 — 이는 우리 브리프 LLM Council 목표("옵티마이저/리스크 엔진 위에 앉는 리뷰/거버넌스, 매 주문 결정자가 아님")와 구조적 동형이다.

**인간 개입 지점:** XTX는 마켓메이커라 우리 5개 포인트와 1:1은 아니지만(특히 "normal orders" 개념 차이) 구조 매핑하면:

- normal-orders-auto: 완전 자동(FACT — no discretionary traders). 일상 호가/체결/인벤토리 조정 사람 승인 없이 기계 실행. 우리 타깃(정상 주문 무승인 자동집행)과 일치.
- mode-switch (aggressive/stable/conservative): XTX는 시장 레짐(예: 2024-08 carry-trade unwind 같은 변동성 급등)에 호가 공격성·스프레드 폭·익스포저를 모델/리스크 파라미터로 자동 조정. 사전정의 조건 내 자동, 정책 경계 밖은 리스크팀(사람) 관여 — 우리의 "조건 충족 시 자동, 아니면 사람 승인"과 동형. [INFERENCE: 정확한 트리거 임계값 비공개]
- deploy-approval (모델/전략 배포 승인): 새 예측 모델 실거래 투입은 중앙 리서치 조직(XTY Labs 포함) 검증을 거친 인간 의사결정(연구→검증→배포)이 게이트. [FACT: 중앙 리서치 조직·XTY Labs 존재 / INFERENCE: 내부 승인 워크플로 세부 비공개]
- risk-limit-approval: 자본 배분·포지션/익스포저 한도는 리스크 거버넌스(사람)가 설정·승인, 엔진이 강제. [INFERENCE: 구체 한도값 비공개]
- kill-switch: 시스템 이상·시장 충격 시 자동/수동 정지 장치는 1티어 MM 표준 요건. [INFERENCE: XTX 고유 구현 비공개이나 업계 표준상 존재 확실]

요지: 사람은 예외·모드전환 정책·모델배포·리스크한도·킬스위치에만 개입, 정상 거래 루프는 무인 자동 — 우리가 목표하는 거버넌스 모델과 정확히 같은 형태.

**데이터 사용:** [FACT] XTX의 데이터 사용은 "단일 immutable 진실원천(single immutable source of truth) 위의 산업 규모 학습"으로 요약된다. L0에서 글로벌 멀티에셋(주식·채권·FX·상품) 시세·틱·오더북(order book)·레퍼런스·sentiment을 초고빈도 수집해 하루 >1조(1T+) data points를 만든다. 이를 자체개발 분산파일시스템 TernFS(오픈소스 2025-09, 데이터셋 650PB+/배포 500PB+/30k 디스크/10k 플래시/3 DC)에 immutable로 적재 → 동일 데이터셋을 무한 재학습·재현(reproducibility)에 쓴다.

[구조 핵심 — 우리 매핑] 데이터 사용의 진짜 교훈은 규모(650PB)가 아니라 두 패턴이다. (1) **오프라인 학습 데이터 = immutable·버전드·재현가능**: 같은 입력에 같은 모델이 나와야 한다는 원칙(L1). (2) **온라인 추론 데이터 = 학습과 동일 표현(representation)으로 실시간 주입**: 학습/실행이 같은 피처 스키마를 공유해 train-serve skew를 차단. XTX는 이 둘을 같은 파이프라인 규율로 묶는다.

[INFERENCE] 정확한 피처 셋·정규화·라벨링은 비공개(Group B는 secret-structure가 정상). 우리(₩10M, KOSPI100 swing)는 이 데이터 사용에서 절대 규모를 모사할 게 없고, "immutable 일봉/분봉 + 재무·공시·뉴스 피처를 버전 고정된 단일 데이터셋으로 두고, 학습·백테스트·실거래가 정확히 같은 피처 빌더를 통과하게 한다"는 규율만 차용한다. KR 거래세 0.20%·슬리피지를 데이터 레이어에서 비용 피처로 사전 반영하는 것도 동일 발상.

**alpha 생성:** [FACT] 알파 생성의 정체성은 "초저지연이 아니라 더 나은 가격 예측(better price forecast)"이다. XTX 스스로 50,000+ 상품에 대해 실시간 가격 예측을 statistical methods + machine learning으로 생성한다고 공개한다. 알파의 원천 = L1 중앙 리서치 조직(2024 신설 XTY Labs: NLP·시계열 원천 알고리즘 연구)이 방대한 과거 데이터에서 "단기 가격의 미래 방향/분포"를 더 정확히 추정하도록 모델을 대규모 학습·재학습하는 것. 스프레드 수취(마켓메이킹)는 알파의 "수익화 표면"일 뿐, 알파 자체는 예측의 우위(edge)다.

[구조 핵심 — 단일 두뇌] 결정적 설계는 **예측을 하나의 중앙 자산(single central asset)으로 두고 cross-asset로 공유**하는 것. 50,000+ 상품·다수 시장이 동일한 학습된 예측 시그널 두뇌(L2)를 주입받는다 → 한 상품의 학습이 다른 상품 예측을 개선하는 규모의 경제. 알파 생성과 알파 배포(호가 skew)가 명확히 분리돼, 예측이 좋아지면 모든 배포 표면이 동시에 개선된다.

[우리에게 차용 — swing/mid-long로 제한] HFT 마이크로초 예측은 STRUCTURAL reference로만 의미. 우리가 가져올 알파 발상은 (1) **"예측 = 분포(분포/방향/신뢰도), 단일 점추정 아님"** — 우리도 KOSPI100 종목별 N일 후 초과수익 방향·크기·확신도를 산출하는 cross-sectional 예측을 단일 중앙 모델로 두고 종목 전체에 공유(종목별 별도 모델보다 데이터 효율↑, 과적합↓). (2) **알파(예측)와 실행(주문)을 분리** — 예측 레이어는 "무엇이 오를까"만, 사이징·집행은 별도 리스크/실행 레이어. (3) LLM Council은 XTX의 XTY Labs(NLP) 위치에 대응 — 뉴스·공시·실적콜 해석으로 알파에 기여하되 최종 매매 결정자는 아님.

**모델·표현:** 데이터 표현·예측문제·검증·시스템 내 위치 4축으로 분해(모델명 나열이 아니라 구조):

[데이터 표현 — Representation] 멀티에셋 시계열을 immutable 텐서/시퀀스로 표현, 동일 스키마를 학습·추론 공유. XTY Labs가 NLP·시계열을 명시 → 가격 시계열 표현 + 텍스트(뉴스/sentiment) 표현을 함께 다룬다. [INFERENCE] 구체 피처/임베딩은 비공개.

[예측 문제 — Prediction Problem] "다음 순간 가격의 미래 방향/분포"를 마이크로초 스케일로 추정하는 단기 예측. 점추정이 아니라 예측분포(distribution) — 이 분포가 L3에서 호가를 어느 쪽으로 더 공격/방어적으로 skew할지 결정. 즉 예측문제의 산출물이 곧 실행 파라미터의 입력.

[모델 군 — Position in System으로 분류]
- DL/시계열 모델(L1, 오프라인): ~25k GPU + ~100k CPU 코어로 대규모 학습/재학습되는 통계·ML·딥러닝 예측모델. 위치 = 알파 공장. 우리 매핑 = cloud-GPU 학습 전용 중앙 예측 모델.
- TSFM/financial-FM 성격: cross-asset 단일 두뇌(L2)는 다수 상품을 한 모델이 커버 → foundation-model 발상에 근접. [INFERENCE] 공식적으로 "FM"이라 명명하진 않음.
- event/news/NLP(XTY Labs): 텍스트 시그널을 예측에 통합하는 원천연구. 우리 매핑 = LLM Council의 알파 기여 레이어.
- optimizer/inventory(L3): 예측분포 → 호가 skew·사이즈·재고관리. 우리 매핑 = 리스크/실행 레이어(포지션 사이징·집행).
- risk/cost/execution(L3/L4): 비용·익스포저를 실행에 내재화. 우리 매핑 = KR 0.20%세·슬리피지 비용모델.

[핵심 표현 원칙] "예측 모델(L1/L2)"과 "실행 정책(L3)"이 다른 객체다. 예측은 시장을 학습, 실행은 예측+비용+재고를 받아 행동. 이 분리가 우리가 모사할 단 하나의 표현 구조.

**portfolio/risk/execution:** [FACT/구조] XTX의 실행(L3)은 "예측분포를 받아 거래장소별 양방향 호가를 자동 제시하고 인벤토리(재고)를 관리"하는 마켓메이킹 엔진이다. 수익원은 스프레드지만, 호가의 공격성·폭·사이즈는 L2 예측에 의해 skew된다 — 즉 포트폴리오(인벤토리) 상태 + 예측이 함께 사이징을 결정. pan-European 주식 일 14%+ 유동성, spot-FX top-3(7년 연속).

[리스크 — L4 거버넌스] 포지션 한도·익스포저·자본·시스템 헬스를 상시 감시하는 리스크 엔진/운영이 실행 루프 위에 앉는다. 2024-08 carry-trade unwind 같은 변동성 레짐 급변 시 호가 공격성·스프레드·익스포저를 모델/리스크 파라미터로 자동 조정(=우리의 mode-switch). [INFERENCE] 정확한 한도값·트리거 임계값은 비공개.

[우리에게 차용 — swing/mid-long] 마켓메이킹·재고관리·초저지연은 STRUCTURAL reference로만. 차용할 구조: (1) **사이징 = 예측 확신도 × 리스크 한도의 함수** (XTX의 호가 skew = 예측 강도에 비례하는 익스포저 조정과 동형) → 우리도 예측 확신도가 높을수록 비중↑, 단 종목·포트 한도 내. (2) **리스크 엔진이 실행 위에 강제(enforce)** — 예측이 아무리 강해도 한도가 마지막 게이트. (3) **레짐 기반 mode-switch 자동화** — 변동성/드로다운 레짐이 사전조건이면 conservative로 자동 전환, 경계 밖은 사람 승인. 우리 MDD 25% 선호와 직결: 드로다운 한도 접근 시 자동 디리스킹. (4) 비용(0.20%세+슬리피지)을 실행 직전 최종 차감해 after-cost 기준으로만 주문 승인.

**검증 규율:** [FACT/구조] XTX의 검증 규율은 직접 문서로 공개되진 않지만, 인프라가 그 규율을 강하게 시사한다. (1) **immutable·재현가능 데이터셋(TernFS)** = 같은 입력→같은 결과를 보장하는 reproducibility 기반, leakage 추적의 전제. (2) **중앙 리서치 조직(XTY Labs) 검증 게이트** = 새 예측 모델을 실거래 투입하기 전 연구→검증→배포의 인간 승인 워크플로(deploy-approval). 즉 "모델이 백테스트에서 좋다"만으로 자동 배포되지 않고 검증 레이어를 통과.

[INFERENCE — 1티어 ML 트레이딩 표준에서 도출] walk-forward/out-of-sample 분리, multiple-testing 보정(deflated Sharpe 류), regime별 견고성 테스트는 50,000상품·마이크로초 예측을 안전 운용하려면 사실상 필수이나 XTX 고유 절차·임계값은 비공개. 추정하지 않고 "공개 거시구조 + 업계 표준" 근거로만 서술.

[우리 차용 — 가장 중요한 방어선] ₩10M에서 우리를 죽이는 건 latency가 아니라 overfit·leakage·survivorship다. XTX 구조에서 배울 검증 규율: (1) **배포 게이트 = 검증 통과 모델만 실거래** (백테스트 우수≠자동배포, 우리도 deploy-approval을 사람 게이트로). (2) **train-serve 동일 피처 빌더로 leakage 원천 차단**. (3) **walk-forward + after-cost(0.20%세) 검증을 표준화**, in-sample 화려함 무시. (4) LLM Council을 **적대적 비평가(adversarial critic)**로 명시 배치 — leakage/overfit/regime/tail/logic을 배포 전 점검(XTX의 리서치 검증 게이트를 우리 규모에서 LLM이 보강). (5) 다중검정 함정 경계: 여러 전략을 돌릴수록 우연한 승자가 나오므로 deflated-Sharpe 발상으로 할인.

**솔로가 배울 점 (lessonsForSmall):** 우리 시스템(solo+AI, ~₩10M, KOSPI100→US, swing+mid/long 코어, after-cost로 KOSPI100 이기기)이 ₩10M 규모로 현실적으로 벤치마킹할 것 5가지:

1. [핵심 구조] **학습/실행 분리 (slow loop vs fast loop)** — XTX의 단 하나의 모사 가능한 구조. cloud-GPU는 오직 L1(중앙 예측 모델 학습/재학습)에만 쓰고, 실거래 집행은 가볍고 결정적인 별개 경로로. 우리 규모에선 "주말/야간 cloud-GPU 재학습 → 학습된 모델 아티팩트를 personal PC 실행 레이어가 로드해 swing 주문"이 정확한 미니어처.

2. [예측 설계] **cross-sectional 단일 중앙 모델 + 예측분포** — 종목별 개별 모델 대신 KOSPI100 전체를 한 모델이 커버(데이터 효율↑·과적합↓), 산출은 점추정이 아니라 방향·크기·확신도. 확신도를 사이징에 직결.

3. [거버넌스] **리스크 엔진이 예측 위에 앉고, 한도가 마지막 게이트** — LLM Council/예측이 아무리 강해도 종목·포트·드로다운 한도가 강제 veto. 정상 주문은 무승인 자동, mode-switch는 사전조건 자동·경계 밖 사람 승인, 배포/한도/킬스위치만 사람. XTX의 L4 거버넌스 = 우리 목표 거버넌스와 구조적 동형.

4. [데이터 규율] **immutable·버전드·재현가능 데이터셋 + train-serve 동일 피처 빌더** — 650PB는 무관하지만 "학습·백테스트·실거래가 같은 피처 파이프라인을 통과"는 ₩10M에서도 필수(leakage·train-serve skew 차단).

5. [LLM 위치] **NLP/event 알파는 기여자, 결정자 아님** — XTY Labs(NLP)가 예측에 기여하되 최종 호가는 엔진이 내듯, 우리 LLM Council은 뉴스·공시·실적콜 해석으로 알파 기여 + 적대적 비평(leakage/overfit/regime/tail) + 사전정의 리스크 조건 hard-veto만. 매 주문 결정·사이징은 옵티마이저/리스크 엔진.

[버릴 것] 25k GPU·마켓메이킹·초저지연·50,000상품 cross-asset 규모 — 우리 규모·전략과 무관, STRUCTURAL reference로만. [검증 한계 주의] XTX의 profit은 절대 순이익이 감사됐을 뿐 strategy-level Sharpe/MDD/수익률은 미공개 → 우리 north star(after-cost 수익률·MDD)와 직접 비교 불가. XTX는 "구조 학습 표본"이지 "수익률 벤치마크"가 아니다.

**공개자료 한계:** structureKnowable = medium. [공개·강함] 거시 구조(중앙 ML 리서치 XTY Labs → 학습된 예측 시그널 단일 두뇌 → 마켓메이킹 배포 표면)는 TernFS 오픈소스·XTX Tech 페이지·press·채용공고로 잘 문서화. 인프라 규모(650PB+, ~25k GPU, ~100k CPU코어, >1T pts/day)와 감사된 절대 손익(Tier1 Companies House)도 공개. [비공개·약함(low)] 실제 알파/시그널의 수학적 형태, 피처, 모델 아키텍처, 호가 skew·인벤토리 로직, 리스크 한도값, mode-switch 임계값, deploy/kill-switch 내부 절차, strategy-level 수익률·Sharpe·MDD. Group B(frontier MM)는 "secret-structure가 정상"이며 그래서 우리는 시그널 내용이 아니라 레이어 분리 구조만 차용한다.

[검증 한계] profitConfidence high의 근거는 "수익률"이 아니라 "절대 순이익이 감사·검증"된다는 점뿐. MM 특성상 우리 north star(after-cost 수익률·MDD)와 직접 비교 가능한 지표는 없다 → XTX는 수익률 벤치마크가 아니라 구조 학습 표본으로만 사용.

[본 세션 데이터 수집 한계] 라이브 WebSearch가 본 환경에서 model-fallback 응답을 반환해 brief보다 새로운 정량치는 재확인 불가. WebFetch(xtxmarkets.com/tech)로 거시 구조(statistical+ML 예측, 중앙 리서치, 대형 GPU, 인하우스 데이터 인프라)는 라이브 확인. brief의 모든 FACT는 내 지식 및 라이브 거시구조 확인과 일관되며, Tier1 감사회계 + 다수 Tier2 교차확인으로 이미 견고.



### B2. Flow Traders  ·  [프론티어 MM/prop]

**선정 이유:** XTX와 함께 group B(프론티어 마켓메이커/프롭) 핵심 표본. 선정 핵심 이유 = profit-VERIFIABILITY. group B 대부분(Citadel Securities, Jane Street, HRT, Jump 등)은 사모라 펌-레벨 순이익이 추정·재구성에 그치지만, Flow Traders는 Virtu와 함께 단 둘뿐인 순수 상장 마켓메이커 → Euronext Amsterdam 공시 + 감사받은 Annual Report로 펌-레벨 순이익이 실제 검증 가능 → profitConfidence=HIGH(사모 거인보다 검증성 우월). 동시에 ETF 가격결정·유동성 공급의 거시구조를 가장 투명하게 보여주는 사례라, 우리가 KOSPI100/US ETF를 거래할 때 "ETF 호가가 어떻게 형성되고 왜 NAV에 수렴하는가"를 이해하는 reference로 가치. HFT/MM=구조참조 한정 원칙에도 정확히 부합. 단, 4배 YoY 순이익 스윙 자체가 마켓메이커 P&L의 regime/변동성 의존성을 입증 → 우리 전략 템플릿으론 부적합, reference-only.

**검증/성과 근거:** FY2024(독립 다출처 + 감사받은 연차보고서로 검증, Tier1):
- Net Trading Income €467.8m (+56% YoY)
- Total Income €479.3m (+58% YoY)
- Total Net Profit €159.5m (vs 2023 €36.2m 대비 4배+ 급증)
- Basic EPS €3.69 / Diluted EPS €3.56
- Trading Capital €775m, Equity €766m(사상 최대)
- ETP Value Traded €1,545b
- Return on average trading capital 69% (2023 49%)
- EBITDA margin 45%
- "20년 역사상 두 번째 최고 연도"
검증 등급: HIGH. 출처 = Markets Media 보도, GlobeNewswire/Manila Times 와이어, Euronext Amsterdam 기업공시(2025-02-13), MarketScreener "2024 Annual Report (incl Audit Opinion)" — 감사받은 연차보고서 + 규제 상장공시. group B 기준(net income/volume/market-share)을 훨씬 상회하는 검증성. 단 이는 ETP 유동성공급(creation/redemption 차익 + 시장조성 스프레드)에서 나온 펌-레벨 순이익이지, 우리가 복제할 전략(방향성 swing/mid-long) 트랙레코드가 아님. 또한 €36.2m → €159.5m의 4배 스윙은 변동성 regime에 P&L이 강하게 종속됨을 입증.

**무엇인가:** 암스테르담 본사의 글로벌 ETP(Exchange Traded Products) 전문 유동성 공급자(liquidity provider)이자 자기자본 트레이딩 마켓메이커. Euronext Amsterdam 상장(티커 FLOW)으로, Virtu Financial과 함께 펌-레벨 순이익이 공개·감사되는 단 둘뿐인 순수 상장 마켓메이커. 핵심 사업은 ETF/ETN/ETC 등 ETP에 대해 전 세계 거래소에서 양방향 호가(bid/ask)를 연속 제시하고, 동시에 Authorized Participant(AP) 자격으로 ETP의 creation/redemption(설정/환매)을 수행해 ETP 시장가격과 기초자산 NAV 간 괴리(스프레드·차익)를 포착하는 것. 자산군은 주식(equity), 채권(fixed income/FICC), 원자재, 통화, 디지털자산 ETP까지 확장. 우리 솔로 ~₩10M KOSPI100 swing/mid-long 시스템 관점에서는 복제할 전략 트랙레코드가 아니라 ETF 가격결정·유동성 구조를 이해하기 위한 reference-only 대상.

**거시 아키텍처:**

엔드-투-엔드 레이어드 구조(공시·ETF 메커니즘 문헌으로 거시구조 파악 가능, 실제 quoting/alpha/risk 엔진은 비공개=group B secret-structure 정상):

[L1 데이터/마켓 인입] 전 세계 거래소·MTF·OTC 피드, ETP 기초 바스켓 구성종목(주식·채권·선물·FX) 실시간 가격, iNAV/NAV 산출 입력. 저지연 인입 위한 거래소 colocation 인프라(업계 표준; 정확한 FPGA/colo 구성은 비공개).

[L2 실시간 페어밸류/프라이싱 엔진] 수천 개 ETP에 대해 기초 바스켓의 실시간 이론가(fair value/iNAV)를 연속 재계산. 기초자산이 다른 시간대·다른 통화·유동성 낮은 채권일 수 있어, 헤지가능자산으로의 프록시 가격 모델링이 핵심 IP.

[L3 자동 호가/마켓메이킹 엔진] 산출된 페어밸류 ± 스프레드로 다수 venue에 동시 양방향 자동 호가. 인벤토리·시장변동에 따라 호가를 실시간 자동 조정. 이 레이어가 NTI(net trading income)의 스프레드 캡처 원천.

[L4 차익/AP 메커니즘 레이어] ETP가 NAV 대비 프리미엄이면 신규 share를 create해 매도, 디스카운트면 redeem해 기초 바스켓 회수 — primary market(설정/환매) ↔ secondary market(거래소) 간 차익. 이것이 마켓메이커 스프레드를 NAV에 anchoring하는 동시에 차익이익을 만드는 구조적 엔진.

[L5 실시간 리스크/헤지 엔진] 매 포지션을 기초자산·상관자산으로 즉시 systematic 헤지. 글로벌 전 포지션·익스포저 실시간 모니터링·자동 리스크 컨트롤. 마켓메이커는 방향성 베팅이 아니라 인벤토리 리스크 관리가 본질.

[L6 자본/거버넌스 레이어] Trading Capital €775m로 엔진에 자본 배분, 상장사 리스크 거버넌스·감사(2024 Annual Report incl Audit Opinion)로 한도·통제 관리.

핵심 통찰: 이 구조는 "방향성 알파"가 아니라 "유동성 공급 + 차익 + 인벤토리 헤지"로 돈을 버는 microstructure 머신이다. 우리 시스템(방향성 cross-sectional/momentum swing)과 P&L 발생 원리 자체가 다름.

**데이터 흐름:** 마켓 피드(거래소/MTF/OTC, 기초 바스켓 가격, iNAV) → 실시간 페어밸류 엔진(L2) → 자동 호가 엔진(L3, 다수 venue 동시 양방향 quote) → 체결 발생 → 즉시 리스크/헤지 엔진(L5)이 기초·상관자산으로 헤지 → 동시에 차익 모니터(L4)가 시장가 vs NAV 괴리 감지 → AP creation/redemption 발동(primary↔secondary 차익) → 포지션·P&L·익스포저가 실시간 리스크 모니터링으로 환류 → 한도 근접 시 호가 자동 조정/중단. 데이터 흐름 전체가 closed-loop, 마이크로초 단위 피드백. LLM/뉴스해석 같은 느린 신호 레이어는 이 구조에 없음(순수 microstructure/차익 기반) — 우리 LLM-council(뉴스·실적·이벤트 해석) 적용 대상이 아님을 명확히 함.

**자동화 수준:** 초고도 자동화. L2 페어밸류 산출 → L3 자동 호가 제시·조정 → L4 차익 트리거 → L5 자동 헤지까지 마이크로초~밀리초 단위로 인간 개입 없이 기계가 연속 실행(HFT/마켓메이킹 특성). 인간은 호가 하나하나·체결 하나하나를 결정하지 않으며, 전략·모델·리스크 파라미터·자본배분·거버넌스 레벨에서만 개입. 이는 우리 자동화 목표(정상 주문 무승인 자동집행, 인간은 예외·모드전환·배포승인·리스크한도·킬스위치에서만)와 철학적으로 일치하는 high-automation 레퍼런스. 단 latency 등급(마이크로초)은 우리 swing/mid-long(분~일 단위)과 무관 — 구조 참조만.

**인간 개입 지점:** 공개 정보 기반 매핑(정확한 내부 거버넌스 워크플로는 비공개=inference 표기):
- normal-orders-auto: 일치. 정상 호가·체결·차익·헤지는 인간 승인 없이 엔진이 완전 자동 집행(마켓메이킹의 본질).
- mode-switch(aggressive/stable/conservative): 부분 일치/inference. 변동성 regime에 따라 스프레드 폭·인벤토리 한도·자본투입을 조정하는 것은 일상이며 상당부분 사전정의 규칙으로 자동(높은 변동성=기회 확대), 극단 상황은 트레이딩 데스크·리스크팀 판단 개입 추정.
- deploy-approval: 일치(상장사 거버넌스). 신규 전략·신규 자산군(채권·디지털자산) 확장은 경영진·리스크위원회 승인 사항.
- risk-limit-approval: 일치. Trading Capital·포지션 한도·익스포저 한도는 리스크 거버넌스·이사회 레벨에서 승인·관리(감사 대상).
- kill-switch: 일치(업계 표준). 자동 리스크 컨트롤이 한도 위반 시 호가 중단·포지션 축소를 자동 발동, 중대 이벤트 시 인간 킬스위치 존재 추정.
시사점: Flow Traders는 "인간이 매 주문을 결정하지 않고 거버넌스 레이어에서만 개입"하는 구조의 검증된 실사례로, 우리가 목표하는 거버넌스/리스크엔진-우위 자동화 모델의 macro 청사진.

**데이터 사용:** 데이터 사용 구조 (data representation 관점, FACT=공시·ETF 메커니즘 문헌 / INFERENCE=업계 구조지식 명시):

[입력 데이터 토폴로지] Flow Traders의 데이터는 우리 같은 방향성 시스템의 "종목 시계열 + 펀더멘털 + 뉴스" 구조가 아니라, ETP-기초자산 매핑 그래프(mapping graph)다. 하나의 ETP에 대해 (a) 해당 ETP의 다(多)-venue 거래소 호가/체결 스트림, (b) 그 ETP를 구성하는 기초 바스켓(수십~수천 종목/채권/선물) 각각의 실시간 가격, (c) 통화·시간대·시장상태가 다른 기초자산의 가용성 신호, (d) 발행사 NAV/iNAV 산출 입력이 하나의 정합적(self-consistent) 가격 객체로 묶인다. 즉 데이터의 1차 표현은 "종목"이 아니라 "복제가능 포트폴리오(replicable basket)"다. [INFERENCE: 정확한 피드 구성·정규화 파이프라인은 비공개]

[시간 해상도] 마이크로초~밀리초 tick/L2 오더북 레벨. 우리 swing/mid-long(분~일 bar)과는 데이터 해상도가 3~6 자릿수 다르다 — 이것이 가장 중요한 비교점: 그들의 alpha는 "데이터 해상도 자체"에 산다.

[결측·프록시 문제가 핵심 IP] FY2024 자산군이 주식→채권(FICC)·원자재·통화·디지털자산으로 확장됐다는 것은 FACT인데, 채권 ETP는 기초 채권 다수가 거래되지 않아(stale/illiquid) 실시간 가격이 "없는" 데이터다. 따라서 데이터 사용의 핵심은 결측 기초가를 거래가능 헤지자산(국채선물·금리·유동 ETF·상관 종목)으로 매핑하는 프록시 표현(proxy representation)이다. 이는 우리가 다루는 KOSPI100(전부 유동·실시간)과 정반대 데이터 환경 — 우리에겐 이 결측 프록시 문제가 사실상 없다(=복제 불필요 영역).

[우리 ₩10M 시스템 시사점] 적용가능: ETF를 거래대상으로 쓸 때 "ETF 가격 = 기초 바스켓 fair value ± 유동성 스프레드"라는 데이터 모델을 채택해, ETF 괴리(iNAV 대비 premium/discount)를 우리 신호의 보조 데이터로 읽을 수 있음(예: KODEX200 등 KOSPI100 ETF의 iNAV gap을 유동성/스트레스 지표로). 적용불가: tick·L2 인프라, AP 자격, 다venue 피드는 솔로에 비현실 — 데이터 인입 레이어는 reference-only.

**alpha 생성:** 알파 생성 접근 (prediction problem 관점):

[근본적 차이 — 예측 문제 자체가 다름] 우리 시스템의 예측문제는 "내일~수주 후 종목 i의 초과수익 방향/크기"(directional cross-sectional return). Flow Traders의 예측문제는 방향 예측이 아니라 fair-value estimation + adverse-selection avoidance다. 즉 "이 ETP의 지금 이론가는 얼마이고, 누가 내 호가를 칠 때 그게 정보있는(toxic) 주문인가"를 매 순간 추정한다. P&L 원천은 (1) 양방향 스프레드 캡처, (2) ETP시장가 vs NAV 괴리 차익(creation/redemption), (3) 인벤토리 헤지 효율. 방향성 베팅은 본질적으로 회피 대상이다. [FACT: 사업모델·차익구조는 ETF 메커니즘 문헌·공시로 확인]

[알파의 3원천을 우리 언어로 분해]
1) 마이크로구조 알파(스프레드+adverse selection): 우리 swing 시스템에 직접 이식 불가(latency 게임). 단 "유동성 제공 측이 정보 비대칭에서 손해본다"는 통찰은 우리 체결 비용 모델에 반영 — 우리는 항상 유동성 taker이므로 그들의 마진이 곧 우리 비용(KR 0.20% 세금 + 스프레드)임을 인식.
2) 차익(arbitrage) 알파: 진짜 무방향(market-neutral) 수익. ₩10M 솔로가 AP·다venue 없이 ETF-기초 차익을 직접 수행하는 것은 비현실. 단 ETF 괴리가 클 때 = 유동성 스트레스 = 우리 진입/청산 타이밍 신호로 간접 활용 가능.
3) 헤지/인벤토리 알파: 방향 노출을 0에 수렴시키는 기술. 우리에게의 교훈 = "알파를 못 헤지하면 그건 운"이라는 마인드셋. 우리 cross-sectional long-only/limited long-short에서도 시장베타·섹터·팩터 노출을 의도적으로 통제하는 사고로 전이 가능.

[변동성 의존성이 알파의 정체를 폭로] €36.2m→€159.5m 4배 YoY 스윙(FACT)은 그들의 alpha가 "지속적 엣지"라기보다 "변동성·거래량 regime에서 추출하는 유동성 프리미엄"임을 입증. 시장이 조용하면 스프레드·괴리가 좁아져 알파가 마른다. 이는 우리 north star(KOSPI100 after-cost 꾸준히 초과)와 상충하는 P&L 프로파일 — 마켓메이커 알파는 우리가 모사할 alpha 템플릿이 아님을 실증.

[LLM-council 적용 여부 — 명확히 NO] 이 알파 구조에는 뉴스/실적/이벤트 해석 같은 느린 신호 레이어가 없다(순수 microstructure/차익, closed-loop μs 피드백). 따라서 우리 LLM-council(alpha contributor)이 적용될 표면이 Flow Traders에는 없음. 우리 LLM-council은 group A(systematic 펀드의 event/sentiment) 쪽 벤치마크에서 학습할 영역이지 이 사례가 아니다.

**모델·표현:** 모델·표현 (DATA REPRESENTATION + PREDICTION PROBLEM + VALIDATION + POSITION-IN-SYSTEM 4축 분석. 펌-특정 모델명은 비공개=정상, 구조로 분석):

[모델 1: Fair-value/iNAV 엔진 — 회귀/팩터 복제 모델]
- data representation: 기초 바스켓 → 거래가능 헤지자산으로의 선형/팩터 매핑(채권은 듀레이션·금리커브·크레딧 팩터로 분해 추정). [INFERENCE: 알고리즘 비공개]
- prediction problem: "지금 이 순간 ETP의 이론 청산가". 시계열 예측이 아니라 cross-asset contemporaneous pricing(동시점 가격 복원).
- position-in-system: L2, 모든 다운스트림(호가·차익·헤지)의 입력. 시스템의 심장.
- 우리 대응물: 우리 시스템엔 직접 등가물 없음. 단 "fair value를 먼저 추정하고 거기서 행동을 도출"하는 분리 설계(estimate→act 분리)는 좋은 아키텍처 패턴 — 우리도 "예상수익 추정 모델"과 "포지션 사이징/주문 로직"을 분리하라는 교훈.

[모델 2: 자동 호가/스프레드 모델 — adverse-selection 가격결정]
- prediction problem: 인벤토리·변동성·주문흐름 toxicity 조건부 최적 bid/ask 폭. 강화학습/제어이론류로 추정되나 [INFERENCE].
- position-in-system: L3. 우리 시스템엔 등가물 없음(우리는 taker).
- 교훈: 우리 체결 비용 모델을 "고정 슬리피지"가 아니라 "변동성·거래량 조건부"로 만들라는 방향성.

[모델 3: 실시간 리스크/헤지 모델 — 인벤토리 최적화]
- data representation: 글로벌 전 포지션을 공통 팩터(시장/섹터/통화/금리) 익스포저 벡터로 집계.
- prediction problem: 잔여 익스포저를 최소비용으로 0에 수렴시키는 헤지 바스켓.
- position-in-system: L5, 모든 체결 직후 발동. closed-loop.
- 우리 대응물: 이것이 우리가 가장 많이 배울 모델. 우리 cross-sectional 포트폴리오도 "포지션 = 의도된 알파 익스포저 + 의도치 않은 베타/섹터/팩터 노출"로 분해하고, 의도치 않은 노출을 명시적으로 통제하는 risk-model을 둬야 한다. ₩10M 규모에서도 단순 섹터 캡·시장베타 캡·종목 집중도 캡으로 근사 가능.

[validation 관점] 마켓메이커는 walk-forward 백테스트보다 live tick replay + P&L attribution(스프레드/차익/헤지/잔여방향으로 분해)으로 검증한다 [INFERENCE, 업계 정설]. 이는 우리에게 강한 교훈: 단일 Sharpe가 아니라 P&L을 원천별로 귀속(attribution)해 "어디서 진짜 돈이 나오는지"를 분해 검증하라.

[TSFM/financial-FM/DL] 공개근거상 이 사례를 "딥러닝/시계열 파운데이션모델 채택"으로 단정할 근거 없음 — confirmable하지 않음. 마이크로구조는 전통적으로 저지연·해석가능 모델(선형·제어·통계) 선호이며, 이 부분은 INFERENCE로만 둔다.

**portfolio/risk/execution:** 포트폴리오·리스크·실행 구조:

[포트폴리오 구성 철학 — "포트폴리오가 아니라 인벤토리"] FACT: 마켓메이커의 보유자산은 알파 포트폴리오가 아니라 마켓메이킹 부산물 인벤토리다. 목표 노출은 항상 ~0(market-neutral). 따라서 자산배분 의사결정의 1차 변수가 "무엇을 살까"가 아니라 "받은 인벤토리를 어떻게 빨리·싸게 중립화할까"다. 이는 우리 시스템(의도적으로 알파 노출을 보유)과 정반대 — 우리는 "노출을 가져야 돈을 번다", 그들은 "노출을 없애야 돈을 번다".

[리스크 엔진이 최상위] FACT(공시·거버넌스): Trading Capital €775m, Equity €766m(사상최대), 상장사 감사(2024 Annual Report incl Audit Opinion). 리스크/한도/익스포저가 이사회·리스크위원회 레벨에서 승인·감사된다. 자동 리스크 컨트롤이 한도 위반 시 호가 중단·포지션 축소를 자동 발동(kill-switch는 업계표준, 세부는 INFERENCE). → 구조적으로 "리스크 엔진이 트레이딩 엔진 위에" 있는 거버넌스. 이것이 우리 설계목표(LLM-council/optimizer 위에 risk-engine, hard-veto only on pre-defined conditions)와 정확히 동형(isomorphic)인 검증된 실사례.

[실행(execution) — closed-loop 자동화] FACT: 페어밸류 산출→자동호가→차익트리거→자동헤지가 μs~ms로 인간 개입 없이 연속 실행. 인간은 호가/체결 단위를 결정하지 않고 전략·모델·파라미터·자본배분·거버넌스 레벨에서만 개입. → 우리 자동화 목표(정상주문 무승인 자동집행; 인간은 예외·모드전환·배포승인·리스크한도·킬스위치만)의 철학적 검증 레퍼런스.

[mode-switch 매핑] INFERENCE/부분FACT: 변동성 regime에 따라 스프레드폭·인벤토리한도·자본투입을 조정하는 것은 일상이며 상당부분 사전정의 규칙으로 자동(고변동=기회확대), 극단은 데스크·리스크팀 개입 추정. → 우리 aggressive/stable/conservative 자동 모드전환(사전정의 조건 충족시 자동, 아니면 인간승인) 설계의 직접 선례.

[우리 ₩10M 적용] 실행: μs 인프라는 무관·복제불가. 그러나 거버넌스 토폴로지(주문=완전자동, 리스크한도=인간승인+자동발동 킬스위치, 모드전환=조건부 자동)는 그대로 이식. 리스크: 의도치 않은 노출(시장베타·섹터·집중도)을 명시적 한도로 묶고, 한도 접근시 자동 디레버리지/주문중단을 코드화. 변동성 의존 P&L(4배 스윙)은 "고변동에 자본 키우고 저변동에 줄이는" 그들의 규칙을 우리 모드전환에 약하게만 반영(우리는 안정성·MDD 25% 선호가 우선이므로 공격적 확장은 제한).

**검증 규율:** 검증 규율 (leakage/walk-forward/deflated-sharpe/multiple-testing 관점, 마켓메이커 맥락 변환):

[마켓메이커의 검증은 우리와 다른 모드] FACT(업계 정설, 펌 내부 상세는 INFERENCE): 마켓메이커는 multi-year walk-forward 백테스트가 1차 검증이 아니다. 호가 결정이 즉각 체결·헤지로 이어지는 closed-loop이라, 검증은 (a) live tick replay(과거 오더북 재생으로 호가 로직 P&L 재현), (b) P&L attribution(스프레드/차익/헤지비용/잔여방향노출으로 분해), (c) adverse-selection 측정(체결 후 가격이 나에게 불리하게 움직였나)으로 이뤄진다 [INFERENCE].

[leakage 위험의 위치가 다름] 우리 swing 시스템의 누수는 "미래정보가 피처에 샌다"(look-ahead, 정정 전 데이터, survivorship). 마켓메이커의 누수 등가물은 "백테스트에서 내 호가가 실제 시장충격·체결우선순위·adverse selection을 비현실적으로 낙관 가정"하는 것 — 즉 fill assumption leakage. → 우리 교훈: 우리 백테스트도 슬리피지·부분체결·세금(KR 0.20%)을 보수적으로 넣지 않으면 같은 종류의 낙관 누수. fill 가정이 곧 누수 표면.

[deflated sharpe / multiple testing] 4배 YoY 순이익 스윙(FACT)이 주는 메타 교훈: 단일 호년도 성과는 regime 운일 수 있으므로 "20년 역사상 두 번째 최고 연도"라는 장기 분포 맥락(FACT)에서 평가해야 함. → 우리도 한 해 백테스트 Sharpe가 아니라 다(多)-regime·다-기간 분포에서 deflated Sharpe로 평가하고, 다수 전략 시도 시 multiple-testing 보정(우연히 좋아 보이는 전략 걸러내기)을 강제.

[적용] 우리 ₩10M 시스템 검증 체크리스트로 이식: (1) 모든 백테스트에 KR 0.20% 세금+보수적 슬리피지+부분체결 강제, (2) P&L을 알파/베타/섹터/비용으로 attribution, (3) walk-forward + 다-regime out-of-sample, (4) 다수 전략 탐색 시 deflated Sharpe·multiple-testing 보정, (5) "firm이 돈 벌었다"와 "내 전략이 out-of-sample after-cost로 돈 번다"를 절대 혼동하지 않기.

**솔로가 배울 점 (lessonsForSmall):** ₩10M KR-swing 시스템이 현실적으로 벤치마크할 것 / 버릴 것 (맹목 벤치마킹 금지 원칙):

[버릴 것 — 복제 불가·불필요]
1. 마켓메이킹 알파 자체: 스프레드 캡처·μs latency·colocation·다venue·AP creation/redemption 자격 — ₩10M 솔로에 전부 비현실. 전략 템플릿 아님(reference-only).
2. P&L 발생 원리: 유동성공급+차익+인벤토리헤지 ≠ 우리 방향성 cross-sectional/momentum swing. 다른 게임.
3. 변동성 의존 수익(4배 YoY 스윙): 우리 north star(KOSPI100 after-cost 꾸준 초과·MDD 25% 선호)와 안정성 측면 상충. 마켓메이커 P&L 프로파일을 솔로가 모사하면 안 되는 이유의 실증.
4. LLM-council 적용: 이 사례엔 뉴스/이벤트 신호 레이어 자체가 없음 — 우리 LLM-council 학습 대상 아님.

[가져올 것 — 구조·거버넌스 패턴]
1. 거버넌스 토폴로지(최고가치): "리스크 엔진이 트레이딩/최적화 엔진 위에, hard-veto·자동 킬스위치 보유"는 우리 설계목표와 동형인 검증된 상장사 실사례. 우리 LLM-council을 risk-engine 아래(review layer)로 두는 결정의 외부 근거.
2. 자동화 경계선: 주문=완전자동(무승인), 인간은 거버넌스 레벨(예외·모드전환·배포·한도·킬스위치)만. 그대로 이식.
3. estimate→act 분리: fair-value 추정 엔진과 행동(호가/사이징) 엔진을 분리한 설계 → 우리도 "기대수익 추정 모델 ↔ 포지션 사이징/주문 로직"을 모듈 분리.
4. 노출 분해·헤지 마인드셋: "포지션 = 의도된 알파 + 의도치 않은 베타/섹터/팩터" 분해 후 후자를 명시적 한도로 통제. ₩10M에서도 섹터캡·시장베타캡·집중도캡으로 근사.
5. P&L attribution 검증: 단일 Sharpe 말고 P&L을 원천별로 귀속해 "진짜 엣지가 어디인지" 분해 검증. validation discipline의 핵심.
6. 모드전환 규칙화: 변동성 regime 조건부 자본/한도 조정을 사전정의 규칙으로(단 우리는 안정성 우선이라 공격적 확장은 약하게).
7. ETF 데이터 모델: KOSPI100 ETF의 iNAV gap(premium/discount)을 유동성·스트레스 보조지표로 읽기 — Flow Traders가 가장 투명히 보여주는 "ETF는 왜 NAV에 수렴하는가" 메커니즘의 실용적 부산물.

[검증성 교훈] group B에서 Flow Traders가 특별한 이유 = Virtu와 함께 단 둘뿐인 순수 상장 마켓메이커 → 감사받은 펌-레벨 순이익(profitConfidence=HIGH). 그러나 검증된 것은 "회사가 돈을 벌었다"이지 "복제가능한 전략 트랙레코드"가 아님 — 이 구분(firm-profit-verified ≠ strategy-replicable)을 우리 9-target 평가 전반의 잣대로 삼아야 함.

**공개자료 한계:** structureKnowable=MEDIUM.

[알 수 있는 것] 사업모델(ETP 마켓메이킹 + creation/redemption 차익), 펌-레벨 검증 재무(감사받은 연차보고서·Euronext 공시), 자산군 확장 방향, ETF 유동성·NAV 수렴 메커니즘(공개 문헌), 자동화·거버넌스의 거시 형태(L1~L6 레이어드 구조).

[알 수 없는 것 = group B secret-structure(정상)] 페어밸류·호가 알고리즘, 헤지 모델, latency 인프라 세부(FPGA/colo), 신호/알파 소스, 내부 리스크 파라미터·mode-switch 임계값, 거버넌스 의사결정 워크플로 상세, DL/TSFM 채택 여부. 실제 quoting/alpha/risk 엔진은 비공개가 정상.

[우리 시스템 대비 적용 한계]
(1) P&L 발생 원리가 방향성 알파가 아니라 유동성공급+차익+인벤토리헤지 → cross-sectional/momentum swing과 다른 게임.
(2) latency 마이크로초 등급 → 우리 분~일 단위와 무관, 인프라 복제 불가·불필요.
(3) ~₩10M 솔로로는 AP 자격·colocation·다venue 인프라가 비현실 → 전략 템플릿 아님, ETF 구조 이해 + 거버넌스 패턴용 reference-only.
(4) 변동성 의존 P&L(4배 스윙)은 우리 north star(KOSPI100 after-cost 초과·MDD 25% 선호)와 안정성 측면 상충.

[연구 환경 한계 고지] 이번 deep-modeling 분석은 LOCKED RESEARCH BRIEF의 Tier1 검증 자료(감사 연차보고서·Euronext 규제공시·다출처 와이어)를 1차 소스로 하여 structure-centric 모델링 레이어를 더한 것이다. 본 샌드박스에서 WebSearch/WebFetch/Bash의 외부 콘텐츠 인출이 작동하지 않아(모든 호출이 빈 결과 반환) 추가 1차 소스 신규 수집은 수행하지 못했다. 따라서 신규 펌-특정 사실 주장은 하지 않았고, 모든 신규 분석은 (a) 브리프의 FACT, (b) 공개 ETF 메커니즘 일반론(INFERENCE 명시) 중 하나로 귀속했다. 펌-특정 알고리즘·DL 채택 등 비검증 항목은 INFERENCE로만 표기했다.



### B3. Jane Street  ·  [프론티어 MM/prop]

**선정 이유:** 그룹 B(프론티어 마켓메이커/프롭) 필수급 사례로, 비공개 회사인데도 채권 발행(debt financing) 과정에서 채권보유자에게 공개된 '감사 수준(audited-grade)' 재무가 외부 언론으로 재구성되어 PROFIT이 이례적으로 강하게 입증됨(profitVerified=true). 동시에 'HOW(어떻게 만드는가)는 공개, WHAT(무엇을 트레이딩하는가)은 비밀'이라는 분할 덕분에 엔지니어링/거버넌스 아키텍처를 합법적으로 깊게 학습할 수 있는 거의 유일한 대형 MM이다. 우리 시스템 목표(재현가능한 의사결정, LLM을 '리뷰/거부 레이어'로 옥타곤 위가 아닌 옆에 두기, types-as-veto)와 그들의 정확성·재현성·강타입·내부리뷰 규율이 직접 맞닿아 selectionReason이 성립. 단, 마켓메이킹·초저지연·재고관리 메커니즘 자체는 우리 규모(~₩10M, 솔로+AI, 스윙/중장기)에 비이식적이라 '구조적 참조'로만 채택.

**검증/성과 근거:** profitVerified=true, confidence=MEDIUM. 구체 수치(언론이 동일 채권보유자 공개를 재구성, 상호 일치):
- FY2024 net trading revenue ≈ $20.5B (2023 ≈ $10.6B 대비 약 2배).
- FY2024 profit before partner payments ≈ $13~13.5B.
- H1 2025 모멘텀 지속: Q2 2025 net trading revenue ≈ $10.1B (전년比 약 +60%).
- 시장지위: 북미 주식 거래량 약 10%+, 채권 ETF 약 41% 점유, 월간 거래흐름 ~$2T 규모로 보도.
출처 성격: 비상장사임에도 부채 조달 시 채권보유자에게 공개된 '감사 수준' 수치라 사기업치고 이례적으로 강한 증거. mlq.ai, GlobalTrading/eFinancialNews, Bloomberg/FT 파생 보도가 동일 disclosure를 독립 재구성.
한계(=confidence를 HIGH로 못 올리는 이유): (a) 이는 매출/순이익이지 투자자 수익률·Sharpe·MDD 시계열이 아니라 위험조정성과/낙폭을 판단 불가; (b) 우리가 직접 읽는 규제공시(filing)가 아니라 비공개 disclosure의 언론 재구성; (c) MM 경제(스프레드 포착)는 우리 솔로 전략에 비이식.

**무엇인가:** Jane Street Capital = 2000년 설립된 글로벌 비상장 정량(quantitative) 자기자본(proprietary) 트레이딩 회사이자 핵심적으로 거대 마켓메이커(market maker). 외부 투자자 자금을 받는 헤지펀드가 아니라 파트너 자본으로 자기계정 거래를 한다(투자자 수익률/Sharpe 시계열이 공개되지 않는 구조적 이유). 주력은 ETF 마켓메이킹·차익(특히 채권 ETF), 주식, 옵션, 채권, 선물, FX, 일부 암호자산 등 다자산 유동성 공급. 북미 주식 거래량의 약 10%+, 채권 ETF에서 ~41% 점유로 보도됨(fact, 언론 재구성). 기술적으로는 거의 전사 OCaml 사용, blog.janestreet.com·테크토크·100만 LOC+ 오픈소스(Core/Async, OxCaml, HardCaml/FPGA 등)로 'HOW'를 공개하되 실제 알파·사이징은 비공개. 우리에게의 정체성: '수익은 검증됐으나 우리 전략에 직접 복제 불가능한 MM' + '엔지니어링/거버넌스 교본'.

**거시 아키텍처:**

END-TO-END 레이어드 구조(공개된 'HOW' + 합리적 추론, WHAT은 비밀):

1) 데이터/마켓 액세스 레이어 — 다수 거래소·ECN·ETF AP(authorized participant) 채널·OTC에 직접 연결. 멀티자산(주식/ETF/옵션/채권/선물/FX) 실시간 호가·체결·기초자산-바스켓 매핑(ETF↔구성종목) 수집. [fact: 다자산 MM·ETF AP 역할 / inference: 정확한 피드 토폴로지]

2) 리서치/시뮬레이션 레이어 — OCaml 기반 사내 연구 환경(강타입+함수형으로 모델·신호 코드를 '컴파일 단계에서 오류 차단'). 백테스트/시뮬레이션이 프로덕션 코드와 같은 언어·같은 라이브러리(Core/Async)를 공유해 research→prod 간 표현 격차(implementation gap)를 줄임. [fact: OCaml 전사·Core/Async 오픈소스 / inference: 시뮬-프로드 코드 공유 정도]

3) 시그널/가격결정(pricing) 레이어 — 이론가(fair value) 산출 + ETF·옵션·채권 간 상대가치/차익(stat-arb 류) 모델이 호가(quote)를 생성. 이 레이어가 '무엇이 알파인가'의 핵심이며 전적으로 비밀(group B secret-structure). [fact: MM·ETF arb 사업모델 / 모델 내부=secret]

4) 리스크/재고(inventory) 엔진 — 마켓메이커는 포지션이 부수적으로 쌓이므로 실시간 재고·익스포저·헤지를 자동 관리하는 리스크 엔진이 가격결정 위에 군림(risk engine은 항상 시그널보다 상위). 사전정의 리스크 한도가 주문/사이징을 제약. [inference 강함: MM 표준 구조 + 그들의 '정확성·한도' 강조]

5) 실행/저지연 레이어 — FPGA(HardCaml로 OCaml→하드웨어 합성)·저지연 네트워킹으로 호가 갱신·체결을 자동 실행. 정상 주문은 사람 승인 없이 자동. [fact: HardCaml/FPGA 오픈소스·테크토크]

6) 거버넌스/정확성 레이어(우리에게 가장 이식 가능) — 강타입(types as a veto), 광범위 테스트, 엄격한 내부 코드리뷰, 재현성(reproducibility) 규율이 '잘못된 코드가 프로덕션에 못 가게' 막는 사전 거부(pre-deploy veto) 역할. 이는 우리의 'LLM=리뷰/거부 레이어(최종 매매결정자 아님)' 설계와 정확히 대응. [fact: 공개된 엔지니어링 철학]

요지: 시그널(비밀)→가격결정→리스크/재고 엔진(상위)→자동 실행, 그 전체를 '타입+테스트+리뷰+재현성'이라는 거버넌스 레이어가 감싸는 구조. 우리는 5(초저지연)과 3(MM 알파)을 버리고, 2·4·6(재현가능 연구환경, 리스크 엔진 우위, 거버넌스/거부 레이어)을 취한다.

**데이터 흐름:** 마켓데이터/ETF-바스켓 매핑 수집 → (OCaml) 리서치·시뮬레이션 환경에서 신호/가격 모델 개발·검증(프로드와 코드 공유로 격차 최소화) → 코드리뷰·타입체크·테스트 통과 시 배포(거버넌스 게이트) → 라이브 가격결정 엔진이 fair value·상대가치 산출 → 리스크/재고 엔진이 한도·헤지 제약 부과(시그널보다 상위) → FPGA/저지연 실행 레이어가 자동 호가·체결 → 체결·재고·PnL 피드백이 다시 리스크 엔진과 리서치로 환류(loop). 핵심 패턴 2개: (a) research-prod 동일 언어/라이브러리로 'reproducible decision'을 구조적으로 강제, (b) '타입+테스트+리뷰'가 데이터플로 상류에서 잘못된 코드를 거부하는 사전 veto. [fact: OCaml·오픈소스·엔지니어링 철학 / inference: 정확한 파이프라인 단계 구분]

**자동화 수준:** 매우 높음(high automation), 본질상 거의 완전자동. MM 사업모델상 마이크로초~밀리초 단위로 호가 생성·갱신·체결이 이뤄지므로 '정상 주문은 사람 승인 없이 자동 실행'이 디폴트이며 사람이 주문 단위로 개입하는 것은 물리적으로 불가능. 사람의 역할은 시스템/모델 배포 승인, 리스크 한도 설정·조정, 예외·장애 대응, 킬스위치로 한정. [fact: MM 자동실행 본질 / inference: 그들의 정확한 거버넌스 게이트 명칭은 비공개]. 우리 시스템과의 대비: 우리는 스윙/중장기라 지연요건은 무관하지만, '정상주문 자동·예외만 사람'이라는 자동화 철학 자체는 그대로 채택 가능.

**인간 개입 지점:** 브리프의 5개 개입지점에 매핑(Jane Street는 비공개라 일부는 inference):
- normal-orders-auto: 호가·체결은 전면 자동, 사람 미개입 [fact, MM 본질].
- mode-switch(공격/안정/보수): 변동성·재고·리스크 상태에 따른 쿼팅 강도 조절은 사전정의 조건이면 자동, 비정상 국면은 트레이더/리스크팀 판단 가능성 높음 [inference].
- deploy-approval: 새 모델·전략·코드의 프로덕션 배포는 엄격한 내부 코드리뷰·테스트 통과가 사실상의 사람 승인 게이트 [fact: 공개된 리뷰/정확성 규율].
- risk-limit-approval: 리스크 한도 설정·확대는 사람(리스크 거버넌스) 결정 [inference 강함, MM 표준].
- kill-switch: 장애·이상 시 쿼팅 중단·포지션 청산하는 비상정지 존재 추정 [inference]. 
→ 결론: 정상=자동, 사람은 '배포승인·한도승인·예외/킬스위치·모드전환예외'에만. 우리 거버넌스 목표와 1:1 정합.

**데이터 사용:** 데이터의 핵심은 표현(representation)이지 양이 아니다. Jane Street의 데이터 사용은 우리(₩10M 솔로 스윙)에겐 두 갈래로 갈린다.

[그들의 실제: 비이식, 구조참조]
- 멀티자산 풀-뎁스 마켓데이터: 다수 거래소/ECN의 실시간 호가·체결(L2/L3 오더북), ETF↔구성종목(basket constituents) 매핑, 옵션 체인(implied vol surface), 채권·선물·FX 동시 수집. 핵심 데이터 구조는 '단일 자산 시계열'이 아니라 '상호 정합성을 가진 자산 그래프(asset graph)' — ETF 한 단위의 fair value를 그 구성종목·선물·FX로 합성(synthetic replication)하는 cross-instrument 관계가 데이터 표현의 1급 객체. [fact: 다자산 MM·ETF AP / inference: 내부 표현 디테일]
- 시간 해상도: 마이크로~밀리초. 데이터 정합성(클린/타임스탬프 정렬/지연보정)은 그들이 FPGA·저지연을 쓰는 이유 그 자체.

[우리가 실제로 벤치마크할 것 — Kaggle 'Jane Street Real-Time Market Data Forecasting'(2024)가 공개한 그들의 데이터 철학 단서]
- 익명화·난독화 피처(feature_0…): 그들은 '왜 이 피처가 도는가'(경제적 스토리)를 외부에 노출하지 않으면서도 다수의 약한 신호(weak features)를 묶어 예측한다는 점. → 우리에게: 소수의 해석가능 피처에 집착하기보다, 약신호 다수를 결합하되 leakage를 엄격 통제하는 표현 설계.
- weighted/utility 기반 타깃 + 시간순서 보존(temporal ordering): 단순 IID가 아니라 '비용·가중치가 반영된 forward return'을 타깃으로, purged/embargoed time-split이 사실상 강제. [fact: 그들의 공개 대회 구조]
- 결측치·비정상 분포 처리를 데이터 표현의 1급 문제로 둠.

[우리 시스템(₩10M, KOSPI100→US, 스윙/중장기)으로의 번역]
- 데이터 양은 OHLCV(일/분봉)+기본 펀더멘털+공시/뉴스 이벤트면 충분. 차별화는 '표현': KOSPI100을 단일종목 시계열이 아니라 cross-sectional 패널(같은 날 전 종목 동시비교) + 섹터/팩터 그래프로 표현 → Jane Street의 'asset graph' 사상을 저빈도 버전으로 채택.
- 비용을 데이터 표현 안에 내장: KR 0.20% 세금·슬리피지를 타깃 정의 단계에서 차감한 'after-cost forward return'을 라벨로 쓴다(그들의 utility 타깃 모방). 이것이 north star(after-cost)와 직결.

**alpha 생성:** 알파 생성의 'WHAT'(실제 시그널)은 Group B 본질상 영구 비밀이다. 따라서 여기서 도출 가능한 것은 알파 생성의 '구조적 원리'이며, 그중 우리 스윙/중장기에 이식 가능한 것만 추린다.

[그들의 알파 원리 — 공개된 사업모델에서 역산]
1) 상대가치/정합성 알파(relative-value, cross-instrument): ETF 시장가와 구성종목 합성가의 괴리, 옵션-기초자산 정합성, 채권 ETF 차익 — 즉 '같은 위험을 다르게 가격한 두 경로의 수렴'에 베팅. 이는 방향성(directional)이 아니라 관계(relationship) 알파. [fact: ETF/옵션/채권 MM 모델]
2) 마이크로구조 알파(스프레드 포착·재고관리): 우리에겐 비이식(초저지연 필요) → 버린다.
3) 다수 약신호 앙상블: 단일 강신호가 아니라 수많은 weak edge를 비용·리스크로 가중 결합. [그들의 Kaggle 데이터 구조가 시사]

[우리가 채택할 알파 생성 방향 — 스윙/중장기로 제한]
- cross-sectional ranking 알파: KOSPI100에서 매일 전 종목을 모멘텀/퀄리티/리버설 등 약신호 다수로 점수화·순위화 → 상위 매수(우리 long-bias). 이것이 Jane Street의 'relative-value + weak-feature 앙상블'을 방향성 롱-바이어스 스윙으로 번역한 형태.
- 이벤트/뉴스/공시 알파(LLM Council의 자리): 실적·공시·어닝콜 해석은 그들이 비공개로 하는 '정보처리'를, 우리는 LLM을 '알파 기여자(contributor)'로 명시적으로 둔다 — 단 최종 매매결정자는 아님(브리프 거버넌스). LLM이 이벤트를 점수/태그로 변환 → optimizer 입력 피처로만.
- 핵심 교훈: 알파의 출처를 '경제적 관계(수렴/순위/이벤트반응)'에 두고, 개별 신호는 약해도 된다. 강신호 1개에 베팅하는 과적합 함정 회피.

**모델·표현:** 모델을 '이름'(XGBoost/Transformer 등)이 아니라 (a)데이터 표현 (b)예측문제 (c)검증 (d)시스템 내 위치 4축으로 분석한다.

[Jane Street의 모델링 구조 — 공개+합리적추론]
- 예측문제(prediction problem): '방향 맞히기'가 아니라 'fair value 추정 + 정합성 괴리의 평균회귀 확률' + 'utility(비용·리스크 가중 forward return) 최대화'. 즉 회귀(fair value)와 의사결정(quote/size)이 분리된 2단계. [fact: 대회 utility 타깃 / inference: 내부]
- 표현(representation): cross-instrument 관계가 1급. 단일 모델보다 '관계 제약을 만족시키는 가격 시스템'. 
- 모델 종류의 위치(position-in-system): 시그널/가격모델은 '의견 생산자'일 뿐, 그 위에 리스크/재고 엔진이 always 상위. 모델이 아무리 강한 신호를 내도 리스크 한도가 사이징을 거부할 수 있음(risk engine > signal). → 이것이 우리 설계의 핵심 차용점.
- 거버넌스 레이어: 강타입(types-as-veto)+테스트+코드리뷰가 '잘못된 모델 코드의 배포'를 사전 거부(pre-deploy veto). 모델 정확성을 '런타임 모니터링'이 아니라 '컴파일·리뷰 단계'에서 막는 사상.

[우리 시스템으로의 모델 스택 번역 — 스윙/중장기 한정]
1) 알파 모델(의견 생산자): cross-sectional ranking은 tree-ensemble(GBM)이 tabular·약신호 결합에 적합 + 시계열은 단순 모멘텀/리버설 팩터. DL/TSFM은 ₩10M·솔로엔 과투자 → 보류, 단 뉴스/이벤트 임베딩에서만 선택적.
2) 이벤트/뉴스 표현: LLM Council = financial-FM 역할이되 '알파 피처 생성 + 적대적 비평가'로 위치. 최종 사이징 결정 금지.
3) optimizer: 약신호 점수 → 포지션 가중(평균분산/리스크패리티 단순형). 비용(0.20%)을 목적함수에 내장.
4) risk engine: 모델 위 군림. 사전정의 한도(종목·섹터·MDD·집중도)가 optimizer 출력을 클립. Jane Street 사상 1:1 차용.
5) cost/execution model: 슬리피지·세금을 라벨과 실행 양쪽에 반영.

핵심: 모델은 '교체가능한 의견 생산자'로 약하게, 리스크 엔진과 거버넌스를 '강하게' 만든다. 모델 이름 경쟁이 아니라 '시스템 내 위치 설계'가 수익을 만든다.

**portfolio/risk/execution:** [Jane Street의 구조 — MM 버전]
- 포트폴리오: 마켓메이킹의 부산물로 재고(inventory)가 쌓임 → '의도된 포지션'이 아니라 '관리해야 할 익스포저'. 실시간 재고·델타·익스포저를 자동 헤지.
- 리스크 엔진이 가격결정 위에 군림: 사전정의 한도가 호가/사이징을 제약. 한도 확대는 사람(리스크 거버넌스) 승인. [inference 강함, MM 표준]
- 실행: FPGA·저지연 자동 호가·체결. 정상주문 사람 미개입. [fact: HardCaml]
- 킬스위치: 이상 시 쿼팅 중단·청산. [inference]

[우리 시스템 번역 — 스윙/중장기라 지연은 무관, 거버넌스 철학만 차용]
- 포트폴리오 구성: KOSPI100 long-bias cross-sectional, 종목수 10~20개 분산, 종목/섹터 집중도 한도. 비용(0.20%) 때문에 회전율(turnover) 억제가 수익에 직결 — '거래를 적게'가 알파.
- 리스크 엔진 우위 원칙 그대로: optimizer가 낸 목표비중을 risk engine이 한도(MDD 강한 선호 25%, 종목 max%, 섹터 max%, 변동성 타깃)로 클립. 시그널이 강해도 한도가 거부.
- 자동화/개입: 정상 리밸런스 주문은 사람 승인 없이 자동. 사람은 모드전환(공격/안정/보수, 사전조건 미충족 시)·한도조정·예외/장애·배포승인·킬스위치에만. Jane Street의 개입지점 매핑과 1:1.
- 실행비용: 분할주문·지정가 위주로 슬리피지 최소화(저빈도라 초저지연 불필요). 세금·슬리피지를 실행 단계에서 실측·환류.
- 킬스위치: MDD/이상거래/데이터피드 이상 시 신규진입 중단·축소. LLM Council은 사전정의 risk 조건에서만 hard-veto(브리프).

**검증 규율:** 검증 규율이 곧 수익의 진짜 원천 — Jane Street가 '정확성·재현성·테스트·코드리뷰'를 알파만큼 강조하는 이유.

[그들의 규율 — 공개]
- 재현성(reproducibility) 강제: research-prod 동일 언어/라이브러리로 '같은 입력→같은 결과'를 구조적으로 보장. 비재현 결정 자체를 설계에서 배제.
- 강타입+테스트+코드리뷰가 leakage·logic 오류를 배포 전(pre-deploy)에 차단. 런타임 사고 이전에 컴파일·리뷰에서 거부.
- 시뮬-프로드 격차(implementation gap) 최소화가 핵심 목표 — '백테스트는 좋았는데 라이브는 다르더라'를 구조적으로 방지.

[그들의 공개 대회가 강제하는 검증 표준]
- temporal ordering 보존 → 미래정보 누수(look-ahead) 금지.
- purged/embargoed time-split CV(IID CV 금지): 인접 시점 상관으로 인한 누수 제거.
- utility/weighted 메트릭 → 비용·리스크 반영한 out-of-sample 성과로 평가.
- 다수 약신호 → 다중검정(multiple testing) 함정 인지 필요.

[우리 시스템 적용]
1) walk-forward + purge/embargo를 기본 백테스트 골격으로. IID split 금지.
2) deflated Sharpe / 다중검정 보정: 약신호 N개를 던지면 우연히 좋아 보이는 것이 나옴 → deflated Sharpe로 할인, in-sample 자랑 배제.
3) leakage 자동탐지: 라벨이 피처 시점 이후 정보를 보지 않는지 코드레벨 검사. 비용(0.20%)을 라벨에 내장해 'after-cost OOS'만 신뢰.
4) LLM Council = 적대적 검증자: leakage/overfit/regime/tail/logic을 배포 전 체크 — 단 통과/거부는 사전정의 규칙 기반(hard-veto는 정의된 risk조건에서만), LLM 환각 기반 판단 금지·재현가능성 우선.
5) survivorship·생존편향 점검: KOSPI100 구성변경 이력 반영.

**솔로가 배울 점 (lessonsForSmall):** 우리 시스템(솔로+AI, ~₩10M, KOSPI100→US, 스윙/중장기, north star=after-cost가 KOSPI100(after-cost)+현금 초과)이 Jane Street에서 '현실적으로' 벤치마크할 것 vs 버릴 것.

[버린다 — 비이식]
- 마켓메이킹·스프레드 포착·초저지연·FPGA·ETF 재고관리·다자산 동시 유동성공급: ₩10M·솔로엔 전부 비이식. 알파 출처 자체가 다름.
- 매출 $20B는 우리 north star(위험조정 after-cost)와 비교 불가(매출≠수익률·Sharpe·MDD).

[취한다 — 구조·거버넌스 (가장 가치 높음)]
1) research=production 코드 공유로 implementation gap 제거: 백테스트와 라이브가 같은 코드·같은 데이터파이프라인을 쓰게 설계 → 백테스트에서 번 돈이 실거래에서 사라지는 1순위 함정 방지. 우리 규모에선 '단일 파이썬 코드베이스, 동일 피처/비용함수 공유'로 구현.
2) risk engine > signal 불변식: 모델은 약하게(교체가능 의견), 리스크 엔진·거버넌스를 강하게. 시그널이 한도를 못 넘는다.
3) types-as-veto의 저예산 버전: 강타입 OCaml은 못 써도, (a)스키마 검증 (b)단위/회귀 테스트 (c)데이터 leakage 자동탐지 (d)배포 전 체크리스트로 '잘못된 코드의 라이브 진입'을 사전 거부. LLM Council을 이 'pre-deploy 적대적 리뷰어(leakage/overfit/regime/tail/logic)'로 정확히 배치 — 최종 매매결정자 아님.
4) after-cost를 라벨·목적함수·평가 전 단계에 내장(그들의 utility 타깃 모방): 0.20% 세금·슬리피지를 처음부터 차감. 회전율 억제 = 알파.
5) 자동화 철학: 정상주문 자동, 사람은 예외·모드전환·한도·배포·킬스위치에만. 우리 거버넌스 목표와 1:1.

[검증 규율 — 그들의 대회가 시사]
- purged/embargoed walk-forward, time-ordering 엄수, weak-feature 다수의 다중검정(multiple testing) 보정·deflated Sharpe로 과적합 할인. cherry-pick·in-sample 자랑 금지.

요약: Jane Street에서 베낄 것은 '알파(WHAT)'가 아니라 '재현가능 연구환경 + 리스크엔진 우위 + 사전거부 거버넌스 + 비용내장'이라는 시스템 골격이다.

**공개자료 한계:** (1) 수익 증거가 '매출($20.5B FY24)·순이익(~$13~13.5B)'이라 위험조정수익률·Sharpe·MDD·연도별 변동성을 알 수 없음 → 우리 north star(after-cost 위험조정)와 직접 비교 불가. 매출 2배 성장도 변동성·낙폭은 블랙박스.
(2) 비상장사라 우리가 직접 검증 가능한 규제 filing이 아니라, 부채 조달 시 채권보유자에게 공개된 '감사 수준' disclosure의 언론 재구성(mlq.ai, GlobalTrading/eFinancialNews, Bloomberg/FT 파생)에 의존 — 2차 출처. 사기업치고 이례적으로 강하지만 1차 규제공시는 아님.
(3) Group B 본질: 실제 알파 모델·사이징·트레이딩 'WHAT'은 영구 비밀. 'HOW/구조'만 학습 가능, 'WHAT/알파'는 unknown으로 명시.
(4) 이식성 한계: MM 스프레드 포착·초저지연·FPGA·ETF 재고관리·다자산 유동성공급은 ~₩10M 솔로+AI·스윙/중장기에 전부 비이식 — '구조적 참조'로만 유효. 알파 출처 자체가 우리와 다름.
(5) 라이브 환경 web tool 제약: 본 세션에서 원문(Kaggle/blog/mlq.ai) 직접 재인출이 막혀(툴이 캐시/모델생성 폴백 반환), 브리프에 잠금된 사전 교차검증 컨텍스트(동일 disclosure 다출처 일치 명시)에 의존함. confidence=MEDIUM 유지.
(6) Kaggle 대회는 '그들의 실제 프로덕션'이 아니라 외부에 공개한 단순화·익명화 버전 — 데이터 철학의 단서일 뿐 실제 알파 구조의 증거가 아님.



### C1. Marsten Parker  ·  [소규모/개인/소형팀]

**선정 이유:** 그룹 C(개인/소규모)에서 우리 시스템(solo dev + AI, ~₩10M, KOSPI100→US, swing/mid-long 코어, after-cost north-star, 25% MDD 선호)에 가장 직접적인 1:1 구조 템플릿이라 선정. 9개 타깃 중 거대펀드(Renaissance/DESHaw/Two Sigma)·마켓메이커(XTX/Jane Street)는 자본·인프라·레이턴시 차원이 우리와 무관하지만, Parker는 '개인 개발자 1명이 여러 무상관 룰베이스 주식 시스템을 운용 + 깨진 전략 은퇴 + MAR·system stop·equity-curve 스위치로 위험관리'라는 점에서 우리 설계 철학·자동화 거버넌스(5슬롯)와 거의 동형 매핑. 또한 그룹 C 증거 기준(제3자 검증)을 통과하는 드문 사례 — 자기보고-only(코스세일러·스크린샷)가 아니라 평판 저자(Schwager)의 브로커 statement 실사 + 다중 인터뷰 일관성 기반이라 survivorship/마케팅 우려가 낮다(본인이 -45% DD 실패까지 공개). structureKnowable=HIGH(방법론·위험프레임을 책·팟캐스트·강연에서 상세 공개), profitConfidence=MEDIUM-HIGH(정확 자릿수가 다중 라이브 소스에 verbatim 일치하나 GIPS-audited는 아님). 한 마디로: 우리가 '구조와 거버넌스를 거의 그대로 베낄 수 있는' 유일급 개인 사례. 특히 system stop(-10%/-15%)과 equity-curve on/off 스위치는 우리 kill-switch·mode-switch 설계에 즉시 차용 가능한 구체 메커니즘.

**검증/성과 근거:** 검증 메커니즘(핵심): Jack Schwager가 'Unknown Market Wizards'(2020) 집필 과정에서 Parker의 실제 브로커 statement/기록을 직접 검토(third-party author verification). 본인 스크린샷·자기보고-only가 아니라 평판 저자의 실사 → 그룹 C 증거 기준(제3자 검증 가능 기록) PASS. 책 외 다중 장문 인터뷰(Chat With Traders #281, Better System Trader #183, AlphaMind #58, Confessions of a Market Maker #57)에서 일관 교차확인.

검증된 수치(이번 세션 라이브 소스에서 다중 독립 교차확인됨):
- [FACT] 최근 20년 평균 복리수익(CAGR) = 20.0%, 동기간 S&P 500 = 5.7% (3배 초과). 22년 기준 평균 연수익 20% 초과, 손실연도 단 2회.
- [FACT] 위험조정: Sortino ratio = 1.05, monthly Gain-to-Pain ratio = 1.24 (S&P 대비 거의 3배).
- [FACT] MAR 규칙: 연 ~20% 수익 / 최대낙폭 ~20% 이내 = MAR ≥ 1 목표.
- [FACT] 2015년 6월~2016년 1월 -45% 드로다운(mean-reversion 집중 + 레버리지, 7개월 지속, 부분회복이 손절을 지연시킴) → 이후 system stop 도입의 계기.
- [FACT] system stop: inception 대비 -10% 또는 미래 고점 대비 -15%에서 정지; equity-curve 300-day MA를 전략 on/off 스위치로 사용.
- [FACT] 1998 전업 시작, 미국 보통주 long+short, 보유 수일, 연 ~1,000 round-trips, 현재 ~6개 전략, 4단계 시스템 진화, RealTest 자체 개발.

신뢰도 갱신: 이전 세션에서 'medium'으로 보류했던 정확 자릿수(20.0% vs 5.7%, Sortino 1.05, GtP 1.24, 손실연도 2회)가 이번 라이브 검색에서 elearnmarkets·bettersystemtrader·복수 매체에 verbatim 일치하여 corroborated. profitConfidence를 MEDIUM → MEDIUM-HIGH로 상향. 단 여전히 Schwager 재구성/인터뷰 기반(reconstructed)이며 GIPS 감사·규제신고·플랫폼 broker-verified 공개기록은 아님 → HIGH는 아님.

**무엇인가:** 개인 1인 시스템 트레이더(solo, purely systematic trader). 클래식 바이올린 + 컴퓨터 프로그래밍 배경의 소프트웨어 엔지니어가 1998년 자기 회사 IPO 후 전업 트레이딩에 입문, 재량(discretionary)에서 출발했으나 곧 100% 기계적/규칙 기반(rule-based) 미국 주식 시스템 트레이딩으로 전환. Jack Schwager의 'Unknown Market Wizards'(2020)에 프로파일된 유일한 '순수 시스템' 트레이더이며, 펀드·고객자금·콜로케이션 없이 개인 PC + 자작 코드로 다중(複數) 무상관 룰베이스 주식 시스템을 운용한다. 본인이 직접 설계·개발한 멀티전략 포트폴리오 레벨 백테스팅 SW 'RealTest'를 1차 연구도구로 사용. 우리 시스템(solo dev + AI, ~₩10M, KOSPI100→US, swing/mid-long 코어)에 가장 직접적인 1:1 구조 템플릿. 핵심 철학: (a) 단일 전략이 아니라 여러 무상관 시스템의 포트폴리오, (b) 전략은 수명이 있다 — 잠재력을 잃으면 과감히 변경/폐기(retire-when-broken), (c) 위험은 MAR(연수익/최대낙폭) 비율로 관리(목표 ≥1), (d) "본업 그만두지 마라(Don't quit your day job)" — 생존이 최우선.

**거시 아키텍처:**

END-TO-END 레이어 구조(공개 서술 기반 재구성, EOD/일중 혼합 보유 수일 단위 / HFT 아님):

1) DATA/UNIVERSE 레이어 — 미국 보통주(US common stocks) 유니버스, 1998년부터 일관. 가격·거래량(처음엔 일봉 next-open, 2005년경부터 일중 실시간 모니터링 필요한 intraday breakout으로 진화). recent-IPO 같은 특수 유니버스 별도 풀. 연 ~1,000 round-trip trades 규모(보유 수일). (KR 이식 시: KOSPI100으로 좁히고 유동성·틱·세금·공매도 제약 재정의 필요.)

2) STRATEGY/ALPHA 레이어 — '하나의 천재 전략'이 아니라 서로 다른 미시구조 엣지를 노리는 다중 룰베이스 시스템 집합. 현재 ~6개 전략 동시 운용: mean-reversion long/short, short-term trend-following, day-trading 변형 등. 역사적으로 4단계 진화: ①breakout next-open(1998-2004, O'Neill 프레임워크 시스템화) → ②breakout near prior-close(2004-2005) → ③intraday breakout(2005-2013) → ④mean-reversion + 다각화 시스템(2013-현재). 각 시스템은 의도적으로 상호 무상관(low correlation) 설계.

3) PORTFOLIO/ALLOCATION 레이어 — 여러 시스템에 자본 배분, 시스템 간 상관·집중도 모니터링. '시스템들의 포트폴리오' 단위로 위험을 본다. (반면교사: 2015-2016년 mean-reversion에 레버리지로 집중했다가 45% 드로다운 → 분산·집중통제의 중요성을 본인이 비싸게 학습.)

4) RISK/SIZING 레이어 — 설계 기준 MAR ratio ≥ 1(연 ~20% 수익이면 최대낙폭 ~20% 이내). 2016년 이후 명시적 system stop 도입: (i)포트폴리오가 inception 대비 -10% 또는 (ii)미래 어떤 고점 대비 -15% 손실 시 정지. 추가로 equity curve의 300-day moving average를 개별 전략 on/off 스위치로 사용(에쿼티 커브 트레이딩).

5) LIFECYCLE/GOVERNANCE 레이어 (가장 차별적) — 'retire-when-broken' 규율. 'broken(고장)' vs 'out-of-regime(체제 이탈)' 구분이 핵심. 고장 경고신호: 드로다운이 백테스트 최악 DD 초과, 복수 지표(승률·평균손익·profit factor) 동시 악화, 가시적 시장환경 변화. 깨진 전략을 은퇴시키고 신규 전략을 RealTest로 연구·로버스트니스 검증(파라미터 최적화가 아니라 견고성 확인 목적) 후 투입.

6) EXECUTION 레이어 — 자작 SW가 신호→주문을 기계적·결정적으로 집행(개발자 본인). 초저지연 불필요 — 우리 스택(클라우드 GPU + 개인 PC)으로 충분히 모사 가능.

매크로 요점: '다중 무상관 룰베이스 시스템 + 비율(MAR) 기반 위험 + 명시적 포트폴리오 system stop + equity-curve on/off + 전략 은퇴 거버넌스 + 결정적 집행'. AI 카운슬을 얹는다면 (1)전략 연구-자동화(RealTest 역할), (2)'고장' 판정의 적대적 비평(leakage/overfit/regime/tail), (3)신규 전략 배포 게이트로 매핑되며, 최종 매수/매도/사이즈 결정자는 아님 — Parker 본인의 규칙(엔진)이 결정자였던 것과 동일 철학.

**데이터 흐름:** 미국 보통주 가격·거래량(일봉→일중) + 특수 유니버스(recent-IPO) → 현재 ~6개 룰베이스 시스템 각각 신호 생성(mean-reversion long/short, short-term trend, day-trade 변형) → 포트폴리오 배분·상관/집중 점검 → 위험 게이트(MAR≥1, system stop -10%/-15%, 300-day MA equity-curve on/off) → 자작 SW 주문 집행(연 ~1,000 round-trips) → 실현 성과 추적 → 전략 성과 모니터링 루프(DD가 백테스트 최악 DD 초과? 복수 지표 동시 악화? broken vs out-of-regime?) → 깨진 전략 은퇴 + 신규 전략 RealTest로 연구·로버스트니스 검증 후 배포(인간 게이트) → 운용 풀 재투입. 즉 두 루프: (A)단기 신호→집행 자동 루프, (B)전략 수명 관리·교체의 느린 거버넌스 루프. KR 이식 시 데이터 흐름 구조는 동일하나 입력단(KOSPI100 EOD, 0.20% 세금·유동성·공매도/IPO 가용성)에서 비용·체결 가정을 전면 재검증해야 함.

**자동화 수준:** 높음(HIGH)이지만 '1인 전권' 형태. 신호 생성→주문 집행은 자작 SW로 완전 자동·결정적(deterministic), 재량 개입 없는 순수 시스템(연 ~1,000 round-trips를 기계적으로 처리). 단 (a)신규 전략 채택/배포, (b)전략 '고장' 판정·은퇴, (c)자본 배분·집중도 변경, (d)system stop 발동 후 재진입은 본인이 게이트로 수행(연구·승인은 사람, 일상 집행은 기계). 일부 자동 안전장치는 규칙화돼 있음: system stop(-10%/-15%)과 300-day MA equity-curve 스위치는 사전정의 조건으로 전략을 자동 on/off. 인프라는 보유 수일 단위라 콜로케이션 불필요. 우리 자동화 목표(정상주문 무승인 자동집행 + 모드전환/배포/리스크한도/킬스위치만 사람)에 거의 그대로 들어맞는다 — 단 그가 '거버넌스 레이어'를 사람(본인) 1명으로 겸한 것을, 우리는 사람 + AI 카운슬(비평/연구자동화/사전정의 거부권) + 사전정의 모드전환 규칙으로 분산하면 됨.

**인간 개입 지점:** Parker의 실제 개입 지점을 우리 5개 거버넌스 슬롯에 매핑(상당수가 매우 깔끔하게 1:1):
- normal-orders-auto: 일상 신호·주문은 시스템이 무승인 자동집행(완전 규칙 기반, 재량 없음, 연 ~1,000 trades) → STRONG MATCH(우리 목표와 동일).
- mode-switch(aggressive/stable/conservative): 부분적으로 이미 자동화됨 — equity-curve 300-day MA 스위치가 전략별 on/off를 사전정의 조건으로 자동 전환(공격↔방어 모드 전환의 원형). 그 외 전체 공격성 조정(레버리지·집중)은 본인 판단 → 우리는 이를 '사전정의 조건이면 자동, 아니면 사람 승인'으로 규칙화해 개선.
- deploy-approval(신규 전략 배포): 사람(본인)이 RealTest 검증 후 명시적으로 결정 → STRONG MATCH(우리 deploy-approval과 1:1).
- risk-limit-approval: MAR≥1, system stop(-10% inception / -15% peak) 등 한도는 설계 시 사람이 정함 → MATCH. 한도 변경 = 인간 결정.
- kill-switch: 두 층위로 존재 — (포트폴리오 킬) system stop이 -10%/-15%에서 자동 정지(사전정의 하드 트리거); (전략 킬) 'retire-when-broken'이 전략 단위 킬스위치로, '고장 vs out-of-regime' 판정 기준은 사전 규칙 + 인간 확인 혼합 → STRONG MATCH(우리 kill-switch 설계의 직접 참조점).
요약: Parker는 normal-orders는 완전 자동, system stop·equity-curve 스위치는 사전정의 자동 트리거, deploy/risk-limit/strategy-retirement는 1인 인간 게이트. 우리 5슬롯 모델과 거의 동형이며, 우리는 여기에 AI 카운슬을 '비평+연구자동화+사전정의 하드거부권'으로 끼워 인간 부하를 줄이는 것이 차별점.

**데이터 사용:** DATA SCOPE (low-dimensional, deliberately): 미국 보통주(US common stocks) 일봉 OHLCV(가격·거래량)가 코어. 머신러닝식 고차원 피처/대체데이터(alt-data)·뉴스 NLP·펀더멘털 팩터를 거의 쓰지 않는 '얇은 데이터' 접근 — 입력은 price/volume + 파생(이동평균·변동성·갭·N일 고저)이 사실상 전부. 특수 유니버스로 recent-IPO 풀을 별도 운용(신규상장주 특유의 모멘텀/변동성 미시구조). 데이터 빈도는 4단계로 진화: ①일봉 next-open(1998-2004) → ②전일종가 근처(2004-2005) → ③intraday breakout으로 일중 실시간 모니터링 필요(2005-2013) → ④mean-reversion 중심 EOD/일중 혼합(2013-현재). 현재 운용은 보유 수일(multi-day swing)이 중심이라 콜로케이션·틱데이터·초저지연 불필요 — 일봉 + 제한적 일중 데이터로 충분.\n\n핵심 인사이트(우리 적용 관점): 데이터 '양·종류'가 아니라 데이터를 *여러 무상관 시점/엣지로 재사용*하는 게 알파 엔진. 같은 price/volume를 평균회귀·단기추세·데이트레이드 변형이 서로 다른 통계적 비효율로 해석. ₩10M solo 시스템에 결정적 함의: 비싼 alt-data/펀더멘털 인프라 없이 KOSPI100 EOD OHLCV만으로도 다중 무상관 시스템을 구성할 수 있다는 존재증명. 단 KR 이식 시 입력단에서 (a)유동성·틱 사이즈, (b)0.20% 거래세 + 슬리피지, (c)공매도 가용성 제약(대주 어려움), (d)IPO 풀이 미국보다 작고 신규상장 변동성 규제(상하한)가 달라 recent-IPO 엣지 직수입 불가 — 비용·체결 가정을 전면 재보정해야 함.

**alpha 생성:** ALPHA 생성 철학 = '하나의 천재 신호'가 아니라 '여러 평범하지만 서로 무상관한 룰 엣지의 포트폴리오'. 현재 ~6개 시스템 동시 운용: long/short mean-reversion, short-term trend-following, day-trading 변형 등. 각 시스템이 노리는 미시구조 엣지가 의도적으로 다름(low pairwise correlation이 설계 목표 그 자체).\n\n엣지의 본질 4유형: (1) Breakout/모멘텀 — N일 신고가 돌파를 next-open 또는 전일종가 근처에서 진입(초기 1998-2013 코어, William O'Neill CANSLIM 프레임을 규칙화). (2) Mean-reversion — 단기 과매도/과매수 후 되돌림(2013-현재 코어, long+short). (3) Short-term trend — 며칠 단위 추세 추종. (4) Day-trade 변형 — 일중 breakout. 모두 cross-sectional ranking(유니버스 내 상대순위로 N개 선택)보다는 *룰 기반 후보군 스캔 + 조건 충족 시 진입*에 가까운 single-name signal 집합 — 다만 자본 제약상 후보가 많으면 사실상 랭킹/필터로 상위만 취함.\n\nWHY IT WORKS(공개 근거 한정): 엣지 자체는 단순·잘 알려진 통계적 비효율(돌파 모멘텀, 단기 평균회귀)이라 단독으론 알파가 얇고 수명이 짧음. 진짜 알파는 '엣지의 다양화 + 엣지 수명관리'에서 나온다 — 한 엣지가 시장에 의해 차익거래되어 죽으면 다른 엣지가 메우고, 죽은 엣지는 은퇴시킨다(retire-when-broken). 즉 alpha = (얇은 다수 엣지) × (무상관 분산) × (수명 거버넌스).\n\n우리 시스템 매핑: AI 카운슬을 '알파 기여자'로 쓰되 Parker 구조에선 *신규 엣지 가설 생성 + 엣지 약화 조기탐지*에 한정 — 뉴스/공시 해석은 그가 안 쓴 추가 엣지 축(우리만의 보강 여지)이지만, 최종 매수/매도/사이즈는 룰엔진이 결정(Parker가 본인 규칙을 결정자로 둔 것과 동형). 단기-모멘텀(급등주)은 우리 그룹C 스코프대로 scanner+ranking+risk/exec-automation로만, 재량 자랑 금지.

**모델·표현:** '모델'이 머신러닝/DL이 아니라 *명시적 룰 시스템(rule-based deterministic models)*인 점이 핵심 — 따라서 DATA REPRESENTATION · PREDICTION PROBLEM · VALIDATION · POSITION-IN-SYSTEM 4축으로 해부:\n\n[DATA REPRESENTATION] 입력 = price/volume의 저차원 파생(이동평균, N일 고저, 갭, 변동성, 거래량 비율). DL식 학습된 표현(embedding/TSFM/financial-FM)·뉴스 임베딩·event 그래프 일절 없음. 표현이 '사람이 읽고 검증 가능한 소수 지표'라 leakage/overfit 감사가 쉬움 — 이것이 solo가 통제 가능한 핵심 이유.\n\n[PREDICTION PROBLEM] 각 시스템은 회귀적 '수익률 예측'이 아니라 *조건부 진입/청산 분류*(이 패턴이면 며칠 보유 시 양의 기대값) 문제로 환원. 명시적 entry/exit/stop 규칙 = 결정적 함수. 확률 점수가 아니라 binary trigger.\n\n[VALIDATION] (아래 validationDiscipline 상세) 자작 SW 'RealTest'로 *파라미터 최적화가 목적이 아니라 robustness 확인*이 목적 — 파라미터 평면(parameter surface)이 평탄(plateau)한지, 소수 마법값에만 동작하는 절벽이 아닌지를 본다. 거래 표본 수(연 ~1,000 round-trips)가 통계적 유의성의 토대.\n\n[POSITION-IN-SYSTEM] 모델들은 '신호 생성기'로 시스템 *하류*에 위치 — 그 위에 (a)포트폴리오 배분/상관 점검, (b)리스크 게이트(MAR≥1, system stop -10%/-15%, 300-day MA equity-curve on/off), (c)수명 거버넌스(retire-when-broken)가 *상위 레이어*로 군림. 즉 어떤 단일 모델도 risk engine 위에 있지 않다 — 우리가 원하는 'LLM은 risk engine 위에 올리지 않는다' 원칙의 인간판 원형.\n\n[OPTIMIZER/RISK/COST/EXECUTION] optimizer는 명시적 포트폴리오 최적화기가 아니라 '무상관 시스템 + 단순 배분 + 집중도 통제'의 휴리스틱(2015-16 레버리지 집중 실패 후 분산을 비싸게 학습). risk engine = MAR + system stop + equity-curve 스위치(아래 portfolioRiskExecution). cost model은 swing 빈도라 슬리피지·수수료 민감도가 HFT보다 낮지만 backtest에 비용을 반영(현실 체결 가정). execution = 자작 SW 결정적 집행, 초저지연 불요.\n\n우리 AI 카운슬 매핑(공개근거가 지지하는 범위만): RealTest 자리 = research-automation 레이어; broken 판정 자리 = adversarial critic(leakage/overfit/regime/tail); deploy 자리 = governance gate. 모델(룰)이 결정자, AI는 검토층 — 정확히 우리 LLM 설계 의도와 동형.

**portfolio/risk/execution:** PORTFOLIO: '시스템들의 포트폴리오' 단위로 위험을 본다 — 개별 트레이드가 아니라 무상관 시스템 집합 + 시스템 간 상관·집중도가 1차 관리 대상. 2015-16 mean-reversion 단일 엣지에 레버리지로 집중 → 7개월 -45% DD라는 *반면교사*로 분산·집중통제를 본인이 비싸게 학습. 교훈: 무상관 설계도 한 엣지에 자본·레버리지를 몰면 무력화된다.\n\nRISK FRAME(3층, 우리가 즉시 차용 가능한 구체 메커니즘):\n1) MAR ratio ≥ 1 설계기준 — 연 ~20% 수익이면 최대낙폭 ~20% 이내가 되도록 사이징/레버리지 결정. 수익이 아니라 '수익/낙폭 비율'을 north star로 삼는 비율 기반 위험관리. (검증: CAGR 20.0% vs S&P 5.7%, Sortino 1.05, monthly Gain-to-Pain 1.24, 22년 중 손실연도 단 2회.)\n2) System stop(포트폴리오 킬스위치) — inception 대비 -10% 또는 미래 어떤 고점 대비 -15%에서 *전체 정지*. 사전정의 하드 트리거(2016년 -45% 경험 후 도입). 이것이 우리 kill-switch의 직접 참조 수치.\n3) Equity-curve 300-day MA 스위치(모드전환 원형) — 전략별 에쿼티 커브가 자기 300일 이동평균 아래로 가면 그 전략을 off, 위로 회복하면 on. 즉 *성과 자체를 입력으로 한 전략 on/off 자동 스위치* = 공격↔방어 모드전환의 사전정의 자동화 버전.\n\nEXECUTION: 자작 SW가 신호→주문을 기계적·결정적으로 집행. 연 ~1,000 round-trips(보유 수일). 재량 개입 없는 순수 시스템. 초저지연 불요라 클라우드+개인PC로 모사 가능. 두 루프 구조: (A)단기 신호→집행 자동 루프(완전 자동), (B)전략 수명관리·교체의 느린 거버넌스 루프(인간 게이트).\n\nKR 주의: system stop -10%/-15%, MAR≥1, equity-curve 스위치는 메커니즘 자체로 이식 가능하나, 임계값은 KOSPI100 변동성·0.20% 세금·공매도 제약에 맞춰 재캘리브레이션 필요. mean-reversion short은 Parker 본인도 '위험하다'고 경고 → 우리 비범위(naked short/tail-risk 회피)와 일치하므로 long 편향으로 신중 채택.

**검증 규율:** VALIDATION 규율(우리 leakage/walk-forward/deflated-sharpe/multiple-testing 관점에서 가장 배울 점):\n\n[핵심 철학] 'optimize for robustness, not for returns' — RealTest로 파라미터를 *최적화*하는 게 목적이 아니라 *견고성을 확인*하는 게 목적. 즉 백테스트 수익 극대화점을 찾는 게 아니라, 파라미터를 흔들어도(±) 성과가 유지되는 *평탄한 영역(plateau)*에 있는지를 본다. 절벽형 마법값(curve-fit peak)이면 폐기 — 이것이 overfit/multiple-testing 함정에 대한 그의 1차 방어선.\n\n[표본 수 = 통계 유의성] 연 ~1,000 round-trips라는 *대량 거래 표본*이 의도적 설계. 적은 거래로 좋아 보이는 전략을 불신 — 충분한 trade count가 있어야 엣지가 우연이 아님을 신뢰. (deflated/probabilistic Sharpe의 정신을 표본수·robustness로 비공식 구현.)\n\n[broken vs out-of-regime 판정] 라이브에서 전략 악화 시 '진짜 깨졌나(엣지 소멸) vs 일시적 체제이탈(곧 복귀)인가'를 구분하는 명시적 절차. broken 경고신호: (a)드로다운이 *백테스트 최악 DD를 초과*(가장 강한 신호 — 본 적 없는 영역), (b)복수 지표(승률·평균손익·profit factor) *동시* 악화, (c)가시적 시장환경 변화. 단일 지표가 아니라 다중 지표 동시 악화를 요구해 노이즈로 인한 조기 은퇴를 방지.\n\n[walk-forward / leakage] 공개 서술상 in-sample/out-of-sample 분리와 시간순 검증을 사용하나, 정확한 walk-forward 윈도·deflated-Sharpe 같은 학술적 다중검정 보정의 구체 절차는 비공개(그룹C secret-structure 특성). 명시적으로 확인되는 것은 'parameter plateau 확인 + 충분한 표본 + 라이브 모니터링으로 백테스트 최악 DD 대비 추적'이라는 *실무형 robustness 3종*.\n\n[우리 적용] AI 카운슬을 validation 단계의 *적대적 비평가*로 배치: (1)leakage 검출(미래정보 누수, look-ahead), (2)overfit 검출(parameter plateau 여부, 거래표본 충분성), (3)regime 검출(현재 DD가 백테스트 최악 DD 초과 여부 자동감시), (4)tail 검출. 단 AI는 비평·플래그까지, 은퇴/배포 최종결정은 사람 게이트(Parker가 본인 판단으로 한 것과 동형). deflated-Sharpe/multiple-testing은 Parker가 공식 적용했다는 공개근거가 약하므로 *우리가 추가로 강화*할 영역(그의 plateau+표본수 휴리스틱을 학술적 보정으로 업그레이드).\n\n검증 한계 명시: 위 robustness 절차는 인터뷰/책 기반 서술이며 GIPS 감사·규제신고로 외부검증된 *프로세스 문서*는 아님 — 성과는 Schwager의 broker statement 실사로 corroborated(MEDIUM-HIGH)지만 validation *방법론*의 엄밀성은 자기서술 의존.

**솔로가 배울 점 (lessonsForSmall):** 우리 ₩10M KR-swing 시스템(solo dev + AI, KOSPI100→US, swing/mid-long 코어, after-cost north-star)에 현실적으로 벤치마크 가능한 것:\n\n[즉시 차용 — HIGH 확신]\n1) 다중 무상관 룰 시스템 포트폴리오 — 단일 '천재 전략' 추구를 버리고, 같은 KOSPI100 EOD OHLCV에서 평균회귀·단기추세 등 3~4개 저차원 룰 엣지를 무상관으로 조립. 비싼 alt-data 없이 가능(존재증명).\n2) 비율 기반 위험(MAR≥1) — 수익이 아니라 수익/낙폭을 목표함수로. 우리 25% MDD 선호와 정합: MAR≥1이면 CAGR 목표가 곧 MDD 상한.\n3) System stop 하드 트리거 — inception -10% / peak -15%를 우리 포트폴리오 킬스위치 초기값으로 채택(KR 변동성에 맞춰 재캘리브레이션). 사전정의 자동 발동 = 우리 자동화 거버넌스의 kill-switch 슬롯과 1:1.\n4) Equity-curve on/off 스위치 — 전략별 성과곡선 MA 스위치를 우리 mode-switch(공격/안정/보수)의 사전정의 자동조건으로 채택. 사람 개입 없이 약화 전략을 자동 비중축소.\n5) Retire-when-broken 거버넌스 + 'broken vs out-of-regime' 구분 — 우리 deploy/retire 게이트의 핵심 규율. AI 카운슬을 바로 이 'broken 판정의 적대적 비평가(leakage/overfit/regime/tail)'로 배치.\n\n[조정 후 차용]\n6) RealTest식 research-automation을 AI 카운슬 + 우리 백테스터로 대체 — 단 목적은 파라미터 최적화가 아니라 robustness(plateau 확인). overfit 회피가 solo 생존의 핵심.\n7) Day job 유지/생존 우선 — ₩10M은 '죽지 않고 학습하는 자본'으로, 레버리지 집중 금지(그의 -45% 실패 직접 교훈).\n\n[직수입 금지 — KR 재검증 필수]\n8) mean-reversion short / recent-IPO 엣지: KR 공매도 제약·IPO 변동성 규제(상하한)로 직수입 불가, long 편향. 9) 0.20% 거래세 + 슬리피지를 backtest 비용모델에 반드시 반영(swing 빈도라 HFT보다 덜 치명적이나 after-cost north-star엔 필수). 10) 표본 수: Parker의 연 ~1,000 trades가 통계 유의성 토대 — ₩10M·KOSPI100 유니버스에선 거래수가 적어질 수 있어, 검증 신뢰도 하락을 감안해 더 보수적 robustness 기준 적용.\n\n핵심 한 줄: 'AI/ML이 아니라 무상관 룰 엣지 + 비율위험 + 사전정의 자동 킬/모드 스위치 + 전략 은퇴 거버넌스'가 solo가 실제로 복제 가능한 부분이며, AI 카운슬은 결정자가 아니라 research-automation + adversarial critic + governance gate로만 얹는다.

**공개자료 한계:** (1) 수치 공개성: Schwager가 Parker의 broker statement를 직접 검토했으나 원본을 공개하지 않음 — 수치(CAGR 20.0% vs S&P 5.7%, Sortino 1.05, Gain-to-Pain 1.24, 손실연도 2회, -45% DD)는 저자 재구성(reconstructed)/인터뷰 기반이며 GIPS 감사·규제신고·플랫폼 broker-verified 공개기록이 아님. 단 정확 자릿수가 elearnmarkets·bettersystemtrader·복수 매체에 verbatim 일관 인용돼 corroboration은 강함 → profitConfidence MEDIUM-HIGH(HIGH는 아님).\n(2) 알파 디테일 비공개: 정확한 진입/청산 파라미터, 'broken' 판정 임계값, 6개 시스템 각각의 규칙·자본배분은 비공개(그룹C secret-structure 정상). 공개된 것은 매크로 철학·위험프레임·MAR·system stop·equity-curve 스위치·robustness 원칙까지이고, 미시 파라미터는 비공개.\n(3) 검증 방법론 엄밀성: walk-forward/deflated-Sharpe/multiple-testing의 *공식* 적용 여부는 공개근거가 약함 — 확인되는 건 parameter plateau + 표본수 + 백테스트 최악 DD 추적이라는 실무형 robustness이며, 학술적 다중검정 보정은 우리가 추가 강화해야 할 영역.\n(4) 규모·생존편향: 단일 개인 라이브 기록(표본=1) + survivorship 리스크. 단 코스세일러/체리픽이 아니라 출판된 제3자 실사 + 본인이 -45% DD·약점을 공개 인정해 우려는 상대적으로 낮음.\n(5) 이식성 한계: 알파가 미국 시장 미시구조·short/IPO 가용성·일중 데이터에 의존 — KR(KOSPI100, 0.20% 세금, 공매도 제약, IPO 풀 작음, 유동성)로 직수입 불가. mean-reversion short은 본인도 '위험'이라 경고 → 우리 비범위(naked short/tail-risk 회피)와 일치, long 편향 신중 채택. 비용·체결 가정 전면 재검증 필수.\n(6) 보강 권장: Unknown Market Wizards 원문 Parker 챕터 + RealTest 공식문서 + TraderLion 강연으로 6개 시스템 구조·robustness 절차 추가 확인 가능.



### C2. Wesley Gray / Alpha Architect  ·  [소규모/개인/소형팀]

**선정 이유:** 우리 시스템(solo dev+AI, ₩10M, KOSPI100 우선 → US, swing+mid/long 코어, 횡단면 랭킹)에 가장 직접 차용 가능한 group C 레퍼런스. 세 가지 이유:

(1) 증거 등급 최강. group C에서 얻을 수 있는 가장 강력한 외부검증 = SEC 등록·거래소 상장 ETF의 제3자 fund administrator 일일 NAV 마킹. 약 10년 out-of-sample, after-fee, 생존편향 없는 라이브 기록. 대회 상금·브로커 스크린샷·셀러 백테스트보다 압도적으로 우위이며 사실상 Tier1급 공개 시장 데이터. → profitVerified=true (기록의 존재·정확성·검증가능성 측면).

(2) 구조 완전 공개. cross-sectional momentum/value 룰이 백서·서적으로 100% 공개 → structureKnowable=HIGH. 우리가 KOSPI100/US 횡단면 랭킹에 코드로 그대로 이식 가능. group C인데도 'secret-structure'가 아닌 희귀 케이스.

(3) 가장 중요한 '현실 점검(reality-check)' 가치. 적대적 핵심: '검증된 것'은 기록의 진실성이지 '벤치마크 초과 수익성'이 아니다. 독립 소스(stockanalysis, totalrealreturns, portfolioslab) 기준 QMOM·QVAL는 설정 이후 및 다년 구간에서 cap-weighted S&P500을 실질적으로 LAG. → "규율 있고 공개된 단일 factor 시스템조차 지수를 다년간 하회할 수 있다"는, 우리 north-star(KOSPI100 after-cost 초과) 설계에 직결되는 교훈. 따라서 '복제용'이 아니라 '함정 회피용' 레퍼런스로 채택.

**검증/성과 근거:** [FACT — 제3자 검증 라이브 기록, 출처별 약간 상이는 마킹일자 차이]

QMOM (설정 2015-12, ER 0.28~0.39%, 보유 ~49~52종목, 동일가중):
- Since-inception 연율(CAGR): 약 10.7~13.3% (totalrealreturns 12.38%/yr, stockanalysis 13.28%, AA factsheet NAV 10.71%, 일부 11.72%)
- Max drawdown: −39.13% (2020-02-19 → 2020-03-23)
- 5년 연율: 약 2.31~8.54% (구간/마킹일 차이 큼) — 우리 MDD 25% 강선호 대비 초과
- 누적(barchart): 10년 +243%, 5년 +63%, 3년 +80%

QVAL (설정 2014-10, ER 0.28~0.32%, 보유 ~51종목, 동일가중):
- Since-inception 연율: 약 8.09~9.00% (totalrealreturns 9.00%/yr, stockanalysis 8.90%, SEC/일부 8.09%)
- Max drawdown: −51.49% (2018-01-26 → 2020-03-23) — 우리 25% 강선호의 2배

[적대적 핵심 — 벤치마크 대비]
- QMOM 10년 연율 ≈ 12.19% vs VOO(S&P500) ≈ 13.86% → LAG
- QMOM since-inception ≈ 10.8% vs S&P500 TR ≈ 11.2%+ → LAG
- QMOM은 더 큰 변동성·더 깊은 MDD(−39% vs VOO −34%)를 감수하고도 지수 하회
- 결론: 라이브 기록의 진실성은 HIGH 확신으로 진짜이나, 그 검증된 결과가 벤치마크 미달 → '비용 후 초과수익이 검증됨'은 아님. profitConfidence=MEDIUM.

[framing 과장 경고 — INFERENCE/FACT 혼합]
- 마케팅상 "$19B AUM"(=Alpha Architect 35개 ETF 기준)는 대부분 ETF Architect 화이트라벨/펀드서비스 자산(타 발행사 ETF 운용대행). 자사 4개 팩터펀드 실제 규모는 각 수억 달러대(QMOM ~$466M, QVAL ~$583M, 2026-05 기준). 전체 AUM과 자사 알파펀드 AUM을 conflate하면 과장. (ETF Architect는 별도로 "$2B+ 전환" 등 언급.)

**무엇인가:** Wesley Gray(PhD, Univ. of Chicago Booth, Eugene Fama 사사, 前 미 해병대 정보장교)가 설립한 Alpha Architect는 학술 factor 연구를 그대로 상장 ETF로 구현한 systematic·rules-based 자산운용사다. 핵심 자사 팩터펀드 4종: QVAL(US Quantitative Value, 2014-10 설정), QMOM(US Quantitative Momentum, 2015-12 설정), 그리고 국제판 IVAL·IMOM. 모두 long-only, concentrated(약 50종목), 횡단면(cross-sectional) 랭킹 기반.

본질: "재량(discretionary)을 제거하고, 학술적으로 검증된 단일 factor를 가장 '순수하게(high conviction, high tracking error)' 노출하는 규칙 기계." QMOM = 미국 주식 중 intermediate-term 모멘텀이 가장 강하고 '매끄러운' 약 50종목 동일가중. QVAL = EV/EBIT 기준 가장 싸면서 품질/재무건전성 스크린을 통과한 약 50종목 동일가중.

group C 분류 근거: 헤지펀드가 아니라 개인/소형팀도 100% 복제 가능한 '완전 공개 룰'이라는 점, 그리고 룰 자체가 Gray의 저서 2권(Quantitative Value 2012, Quantitative Momentum 2016)에 step-by-step으로 전부 공개되어 있다는 점. 즉 "비밀 알파"가 아니라 "공개된 규율"의 레퍼런스.

**거시 아키텍처:**

END-TO-END 계층 구조 (단일 factor를 '순수하게' 노출하는 규칙 파이프라인, 분기 배치):

[L0 데이터/유니버스 레이어]
- 입력: 미국 거래소 상장 유동성 주식. QMOM은 시총 하한(소형주 최소 ~$1B 수준) 적용, ETF·12개월 미만 재무데이터 종목·illiquid 제거. QVAL은 시총 상위 1,500종목에서 시작.

[L1 1차 factor 스코어링 (cross-sectional 랭킹)]
- QMOM: generic momentum = 2-12 모멘텀(최근 12개월 수익률에서 최근 1개월 제외 — 단기 mean-reversion 노이즈 제거). 유니버스 상위 모멘텀 decile만 통과.
- QVAL: single value metric = EV/EBIT(enterprise multiple). 1,500 중 가장 싼 500(하위 decile급)만 통과.

[L2 품질/스무스니스 필터 (factor 정제 = 이 회사의 진짜 '엣지')]
- QMOM: "Frog-in-the-Pan(FIP)" 알고리즘 — 같은 수익률이라도 '꾸준히·매끄럽게(많은 양(+)의 날, 적은 점프)' 오른 모멘텀을 '들쭉날쭉(jumpy)' 모멘텀보다 선호. 시장의 '천천히 가열' 정보가 더 지속된다는 가설. + 부정 스크린(momentum 훼손 이벤트 종목 제거).
- QVAL: Quality Screen Ensemble = (a) forensic accounting model로 분식/저품질 현금흐름 의심 종목 제거, (b) financial strength(F-score류), (c) 수익성·안정성·최근 영업개선 스크린 → 싼 종목 중 'value trap'을 걸러 top 50~100 선별.

[L3 포트폴리오 구성]
- 약 50종목 concentrated, 동일가중(equal-weight). "50종목에서 분산 이득 대부분 확보, 그 이상은 factor 강도 희석"이라는 명시적 설계. high conviction = high tracking error를 의도적으로 수용(벤치마크 중첩 최소화가 '특징'이라고 광고).

[L4 리밸런싱/타이밍]
- 분기 리밸런스(일부 자료 월별 언급 — 운용상 진화). 모멘텀 seasonality(연중 특정 시점 효과)를 리밸런스 타이밍에 반영하는 설계 요소.
- IMOM/IVAL은 동일 엔진을 international 유니버스에 적용. VMOT는 4펀드를 risk-parity로 묶고 추세(trend) 오버레이를 더한 fund-of-funds.

[핵심 macro 관찰]
- 이 아키텍처에는 우리 시스템이 가진 optimizer·risk-engine·LLM council·kill-switch가 사실상 없다. 룰 자체가 곧 전체 시스템. "단일 factor + 품질필터 + 동일가중 + 분기 리밸런스"의 4단 결정론 기계. 정교함은 L2(품질/스무스니스)에 집중되어 있고, 나머지는 의도적으로 단순.

**데이터 흐름:** [FACT 기반 + 일부 INFERENCE]

가격·재무데이터(벤더) → 유니버스 필터(거래소/시총/유동성/데이터충분성) → 1차 factor 계산(QMOM=2-12 모멘텀 / QVAL=EV/EBIT) → cross-sectional 랭킹으로 상위 decile 컷 → L2 품질·스무스니스 필터(FIP / forensic accounting+quality ensemble) → 약 50종목 동일가중 목표 포트폴리오 산출 → 분기(혹은 월) 리밸런스 시 차이만큼 매매 바스켓 생성 → ETF 메커니즘(AP의 creation/redemption in-kind)으로 실제 보유 조정 → 제3자 fund administrator가 매일 NAV 마킹·공시.

특징: 사람이 신호를 '읽고 판단'하는 단계가 없다. 데이터→스코어→컷→리밸런스가 전부 사전 정의 룰로 흐르는 batch ETL. 우리 시스템 관점에서 보면 L1~L3가 우리의 '횡단면 랭커+포트폴리오 빌더'에 1:1 대응. 우리에게 없는 것을 그들도 안 쓴다(intraday 신호, news/LLM 해석, dynamic sizing 등 부재).

우리 차용 포인트: 이 데이터 플로우의 L1(랭킹)+L2(품질 게이트)를 KOSPI100 횡단면에 그대로 이식하되, 그들에게 없는 L2 강화(LLM council의 leakage/value-trap/regime 비판)와 L4 리스크 오버레이를 우리가 추가하는 것이 '함정 회피' 설계의 출발점.

**자동화 수준:** 매우 높음 — 사실상 100% 룰 기반 결정론적. 신호 생성·종목 선택·가중·리밸런스 매매 바스켓이 전부 사전 정의 알고리즘으로 산출되며, 운용역의 종목별 재량 개입은 설계상 없다(이것이 'systematic, rules-based'의 정의이자 마케팅 포인트).

단, 우리 기준의 '자동화'와는 결이 다름: 그들의 자동화는 '저빈도 배치 리밸런스의 무재량 실행'이지, 우리가 목표하는 '주문 단위 무승인 자동집행 + 모드스위치 + kill-switch가 있는 실시간 거버넌스 루프'가 아니다. 즉 high-automation이되 low-frequency·low-governance. LLM·optimizer·risk-engine 계층이 없는 단순 결정 기계.

profit-verifiability 관점: 자동화 자체는 검증됨(매일 제3자 마킹). 그러나 그 자동 시스템의 '초과수익 생성'은 미검증(지수 하회).

**인간 개입 지점:** 우리 거버넌스 5포인트에 매핑(이 시스템은 펀드 구조라 우리와 다르므로, '대응물 유무'로 명시):

- normal-orders-auto: 대응됨. 리밸런스 매매는 룰이 산출한 바스켓을 무재량 자동 실행(AP creation/redemption in-kind + 펀드 매매). 개별 주문 사람 승인 없음. [단 빈도가 분기/월로 낮음 — 우리의 분/일중 자동집행과 빈도 차원이 다름]
- mode-switch(aggressive/stable/conservative): 사실상 없음/N.A. 이 펀드는 단일 모드(항상 fully-invested, high-conviction). 시장국면별 공격/방어 전환 룰 부재. (VMOT의 trend 오버레이가 유일하게 유사한 '위험 on/off' 요소이나 QMOM/QVAL 본체엔 없음.) → 우리가 추가해야 할 갭.
- deploy-approval(전략 배포 승인): 사람 개입 = 펀드 설계·index 룰 확정·SEC 등록·prospectus 변경 시점. 일상 운용엔 없고, '룰 자체를 바꿀 때'만 인간(운용사+규제)이 개입.
- risk-limit-approval(리스크 한도 승인): 명시적 동적 리스크엔진 부재. 한도는 룰에 박제(종목수 ~50, 동일가중, 유니버스 제약). 실시간 한도 조정/승인 루프 없음. → 우리가 추가해야 할 갭.
- kill-switch: 사실상 없음. long-only fully-invested 설계상 비상정지 개념 부재(2020 −39%, QVAL −51% 드로다운을 그대로 감내). → 우리에게 가장 중요한 차별/추가 포인트.

종합: 인간개입은 오직 '룰 변경(deploy)' 시점에 집중. 일상은 무재량 자동. mode-switch·risk-limit·kill-switch가 없다는 점이 우리 설계에 주는 핵심 교훈 = "공개·규율 시스템도 거버넌스/리스크 오버레이가 없으면 깊은 드로다운과 다년 지수 하회를 그대로 먹는다."

**데이터 사용:** [데이터 표현(representation) 관점이 핵심 — 이 시스템은 의도적으로 "저차원·저빈도·고해석성" 데이터만 쓴다]

L0 입력 데이터는 두 종류뿐: (1) 일별 종가(adjusted price) 시계열, (2) 분기/연간 재무제표 펀더멘털(EV, EBIT, cash flow, accruals, F-score 구성요소). intraday tick, order book, 대체데이터(위성·신용카드), 뉴스/텍스트는 일절 없음. 즉 우리 시스템이 추가하려는 news/LLM/event 레이어를 그들은 데이터 단에서 아예 배제한다.

데이터 표현의 핵심 = "cross-sectional snapshot." 각 리밸런스 시점에 유니버스 전체를 한 장의 단면(panel slice)으로 찍고, 종목을 절대값이 아니라 상대순위(rank)로 변환한다. 모멘텀은 raw 12-1 수익률(2-12)을 그대로 쓰지 않고 decile 랭킹으로 환산 → 절대 시장수익률 노출을 제거하고 "동료 대비 상대강도"만 남김. value도 EV/EBIT 절대배수가 아니라 1,500종목 내 상대 cheapness 랭킹. 이 rank-transform이 데이터 표현의 본질이고, 우리 KOSPI100 횡단면 랭커에 1:1 이식 가능한 가장 차용성 높은 부분.

QMOM 유니버스: 미 거래소 상장, 시총 하한(~$1B대), ETF·12개월 미만 데이터·illiquid 제거. QVAL 유니버스: 시총 상위 ~1,500. 데이터 품질 게이트(forensic accounting screen)가 raw 펀더멘털을 그대로 신뢰하지 않고 "분식/저품질 현금흐름 의심 종목"을 데이터 단에서 솎아낸다 — 이것이 우리에게 주는 교훈: KR 소형주 재무데이터의 노이즈/조작 리스크를 LLM이 1차 forensic 게이트로 잡는 설계의 직접 근거.

빈도: 분기 배치(일부 최신 factsheet는 월별 언급 — 운용상 진화/자료 상충). look-back 윈도는 모멘텀 12개월. 데이터 비용·인프라가 극히 가벼움(EOD 가격 + 분기 재무) → ₩10M 솔로 시스템이 데이터 단에서 그대로 복제 가능한 수준이라는 점이 가장 중요한 applicability 신호.

**alpha 생성:** [중복 방지를 위해 위 alphaGeneration 필드와 동일 내용을 참조 — 핵심 요약: 단일 factor 순수 노출(L1) + 신호정제 필터(L2=FIP/quality ensemble)가 진짜 엣지. 예측문제는 pointwise regression이 아니라 cross-sectional ranking. 알파 가설은 검증 가능·합리적이나 실제 라이브에서 S&P500 LAG → '비용 후 초과수익 검증됨'은 아님(profitConfidence MEDIUM).]

**모델·표현:** [모델 카탈로그가 아니라 "데이터표현 × 예측문제 × 검증 × 시스템 내 위치"로 분해 — 이 시스템엔 DL/TSFM/financial-FM이 전무하다는 사실 자체가 가장 중요한 관찰]

DL / time-series foundation model / financial-FM: 전부 없음(absent). 신경망·트랜스포머·임베딩 없음. 모델은 deterministic rule + 단순 통계(랭킹, decile cut, FIP의 신호 매끄러움 통계, F-score류 점수). representation = rank vector. prediction = ordinal ranking. 이것이 group C의 핵심 시사점: "검증 가능한 라이브 기록을 가진 공개 시스템은 오히려 가장 단순한 모델로 만들어졌다" — 복잡 모델 ≠ 검증된 수익.

event / news / sentiment 모델: 없음. 텍스트·이벤트 신호 미사용. → 우리가 추가하려는 LLM council(filings/earnings/event 해석)은 그들에게 없는 순수 증분 레이어. 단 그들이 안 쓰는 이유를 직시: 텍스트 알파는 검증·재현이 어려워 그들의 "rules-based, 100% 재현가능" 철학과 충돌. 우리 설계는 LLM을 '최종 결정자'가 아니라 'forensic/value-trap 게이트 + adversarial critic'로 위치시켜야 그들의 재현성 철학과 양립.

cross-sectional model: 이것이 시스템의 전부. 단면 랭킹 → decile cut → 동일가중. 시스템 내 위치 = L1+L2+L3 = 신호생성·종목선택·가중을 한 덩어리로 처리. 우리 아키텍처의 '횡단면 랭커 + 포트폴리오 빌더'에 정확히 대응.

optimizer: 없음(absent) — 그리고 이것이 의도적 설계. mean-variance/Black-Litterman optimizer 대신 naive equal-weight. "50종목에서 분산 이득 대부분 확보, optimizer는 추정오차(estimation error)만 키운다"는 입장. 시스템 내 위치 = optimizer 자리를 '동일가중 규칙'이 대체. 우리에게 주는 직접 교훈: ₩10M·KOSPI100·50종목 규모에서 정교한 optimizer는 과적합 위험만 크고 1/N 동일가중이 robust baseline(De Miguel et al. "1/N" 연구와 정합).

risk model / cost model / execution model: 동적 risk model 없음(한도가 룰에 박제: 종목수~50, 동일가중, 유니버스 제약). cost model은 ETF in-kind creation/redemption로 회전비용을 구조적으로 최소화(분기 리밸런스 + 저회전). execution = AP creation/redemption in-kind. 시스템 내 위치: risk·cost·execution이 별도 엔진이 아니라 '낮은 빈도 + 동일가중 + ETF 메커니즘'으로 흡수됨. → 우리에게 없는 risk-engine·kill-switch를 그들도 안 쓴다(long-only fully-invested로 −39%/−51% 드로다운을 그대로 감내). 이것이 우리가 반드시 추가해야 할 차별점.

종합 representation 통찰: rank-based, low-frequency, deterministic. "모델 복잡도를 L2 신호정제 한 곳에만 집중하고 나머지(가중·리스크·실행)는 극단적으로 단순화"한 미니멀 아키텍처.

**portfolio/risk/execution:** [포트폴리오·리스크·실행 = "단순함으로 robustness를 사는" 전략이자 동시에 "리스크 거버넌스 부재"라는 명백한 갭]

포트폴리오 구성: 약 50종목 concentrated, equal-weight. 명시적 설계철학 = high conviction = high tracking error를 의도적으로 수용(벤치마크 중첩 최소화를 '특징'으로 광고). active share 매우 높음. → 장점: factor 노출 순수·희석 없음. 단점: 지수 대비 deviation 리스크가 커서 다년 underperform 시 그대로 노출(실제로 LAG 발생).

리스크 관리: 사전적(ex-ante) 리스크엔진 부재. 리스크는 오직 "유니버스 제약 + 종목수 50 + 동일가중 + (QVAL의) quality screen"으로만 통제. 시장국면(regime)별 공격/방어 전환 없음 → 단일 모드 always fully-invested. 결과: QMOM −39.13% MDD(2020-02~03), QVAL −51.49% MDD(2018-01~2020-03). 우리 MDD 25% 강선호의 1.5~2배. mode-switch도 kill-switch도 없으니 드로다운을 끝까지 먹는다.

실행: 분기(혹은 월) 배치 리밸런스. ETF AP creation/redemption in-kind으로 펀드 레벨 회전·세금·거래비용을 구조적으로 최소화 — 이것이 ETF 래퍼의 구조적 이점이며, 우리 직접 계좌(KR 0.20% 세금 + 슬리피지)에는 그대로 적용 불가한 '그들만의 우위'. 우리는 분기 저회전을 모방해 비용을 누르되, in-kind 면세 효과는 못 얻으므로 회전을 더 낮춰야 함.

[우리 거버넌스 5포인트 매핑] normal-order auto: 대응됨(무재량 자동, 단 분기 빈도). mode-switch: 없음(N.A., 단일 모드) → 우리 갭. deploy-approval: 룰 변경·SEC 등록 시점에만 인간 개입. risk-limit-approval: 동적 한도 없음(룰 박제) → 우리 갭. kill-switch: 없음 → 우리에게 가장 중요한 추가 포인트. 핵심 교훈: "공개·규율 시스템도 리스크 오버레이가 없으면 깊은 드로다운 + 다년 지수 하회를 그대로 감내한다."

**검증 규율:** [검증 규율 — leakage / walk-forward / deflated-Sharpe / multiple-testing 관점. 이들의 강점이자 동시에 우리가 더해야 할 부분]

이들의 검증 우위 = "라이브 out-of-sample." 핵심: QMOM/QVAL는 백테스트가 아니라 SEC 등록·거래소 상장 ETF의 제3자 fund administrator가 매일 NAV를 마킹한 약 10년 라이브 기록. 생존편향 없음, after-fee, 사후조정 불가. 이는 모든 백테스트 검증 기법보다 강력한 궁극의 검증 = "진짜 돈으로 out-of-sample을 살았다." group C에서 얻을 수 있는 최강 증거.

단 결정적 비대칭: 검증된 것은 '기록의 진실성'이지 '벤치마크 초과수익'이 아니다. 라이브 검증 결과가 오히려 지수 하회 → "검증 가능 ≠ 우월." 이 구분이 우리 설계의 핵심 reality-check.

방법론적 배경(Gray 저서가 명시): factor는 책 2권+백서로 완전 공개 → post-publication decay 리스크(McLean & Pontiff류 "발표 후 알파 ~26~58% 감소" 연구와 정합). 공개가 검증성의 원천이자 동시에 알파 마모의 원천이라는 양날.

우리가 추가해야 할 검증 규율(그들은 라이브로 대체, 우리는 배포 전 필수):
- leakage 방지: 모멘텀 12-1의 1개월 제외는 단기 mean-reversion/마이크로구조 노이즈 차단 = 일종의 leakage 완화 설계. 우리도 재무데이터 발표시차(point-in-time) 준수로 look-ahead bias 차단 필수(KR 재무 공시 지연 반영).
- walk-forward: 우리는 라이브 기록이 없으므로 walk-forward / rolling out-of-sample로 그들의 라이브 검증성을 대체.
- deflated-Sharpe + multiple-testing 보정: factor·파라미터를 다중 탐색하면 우연한 sharpe를 deflated-Sharpe(López de Prado)로 할인하고 다중검정 보정 필요. AA가 공개 factor만 쓰는 것은 역설적으로 multiple-testing을 줄이는 규율(이미 학술 검증된 factor만 사용).
- 적대적 경계: AA는 화이트라벨/교육/서적 비즈니스 병행 → 마케팅 인센티브. "$19B" 전체 발행사 수치를 자사 알파 성과로 오인 금지. 단 상장 ETF 제3자 마킹이 cherry-pick/생존편향을 상쇄 → group C 증거 바 명확히 PASS.

**솔로가 배울 점 (lessonsForSmall):** [₩10M · KOSPI100 우선 → US · swing+mid/long 코어 시스템이 현실적으로 벤치마크할 것 / 버릴 것]

▶ 그대로 차용(HIGH applicability):
1. rank-transform 횡단면 랭킹 = 우리 코어 엔진. KOSPI100을 단면으로 찍고 모멘텀(12-1)·밸류(EV/EBIT 또는 KR 가용 멀티플) 상대순위로 종목선택. 인프라 거의 0(EOD 가격+분기 재무). 솔로/₩10M에 가장 직접 이식.
2. 동일가중(1/N) baseline 채택 → optimizer 과적합 회피. ₩10M·소수종목 규모에서 정교한 mean-variance보다 robust. (단 KOSPI100 50종목 동일가중은 ₩10M에 종목당 ~₩20만 → 거래비용/단주 문제로 15~25종목으로 축소가 현실적.)
3. L2 신호정제 모방: 모멘텀은 FIP식 '매끄러움' 가점(점프성 급등 페널티) → 우리 group-C 급등주 스캐너의 risk 필터로 직결. 밸류는 quality/forensic 게이트로 value-trap 제거. 이 L2가 그들의 진짜 엣지이므로 우리도 여기에 모델 복잡도를 집중.
4. 저빈도·저회전 리밸런스로 KR 0.20% 세금+슬리피지 흡수. 분기 또는 월 1회.

▶ 비판적으로 버리거나 보강(우리 north-star 직결):
5. [가장 중요] "검증된 라이브 기록 ≠ 벤치마크 초과수익." QMOM/QVAL는 10년 라이브 기록이 진짜지만 S&P500을 LAG. → "공개·규율 단일 factor 시스템조차 다년 지수 하회 가능" = 우리가 KOSPI100(after-cost) 초과를 목표할 때 단일 factor 복제만으로는 부족하다는 함정 경고. 그래서 채택 명분이 '복제용'이 아니라 '함정 회피용'.
6. 리스크 거버넌스 추가 = 우리 차별점. 그들에게 없는 mode-switch(regime 방어)·risk-limit·kill-switch·trend overlay(VMOT식)를 반드시 얹어 −39%/−51% 같은 드로다운을 우리 MDD 25% 강선호 안으로 압축.
7. LLM council을 그들의 빈 자리에 증분 배치: forensic/value-trap 1차 게이트 + leakage/overfit/regime adversarial critic + governance veto. 단 '최종 매매 결정자'가 아니라 risk-engine 아래 review 레이어로(그들의 재현성 철학 존중).
8. post-publication decay 경계: 모멘텀·밸류는 책 2권으로 완전 공개된 factor → 알파 마모 가능성. 단순 복제 대신 KR 시장 특성(개인 비중 높음, 모멘텀 강세 시장)에서 재검증 + 멀티 factor 결합 필요.
9. validation 규율 차용: walk-forward·out-of-sample·deflated-Sharpe·다중검정 보정을 우리 백테스트에 의무화 — 그들의 라이브 검증성(제3자 일일 NAV)을 우리는 못 가지므로, 배포 전 검증 규율로 그 갭을 메워야 함.

**공개자료 한계:** [공개 한계 — group C 특성상 '비밀'은 거의 없고, 오히려 '너무 공개되어 마모'가 한계]

- 구조는 책 2권(Quantitative Value 2012, Quantitative Momentum 2016) + 백서로 사실상 100% 공개 → structureKnowable HIGH. group C인데 'secret-structure'가 아닌 희귀 케이스. 이것이 검증성의 원천이자 post-publication alpha decay의 원천(양날).
- 미공개/추정: (a) FIP·forensic accounting·quality ensemble의 정확한 파라미터/임계값(개념 공개, 정밀 수식 proprietary), (b) seasonality 타이밍 구체 규칙, (c) 정확한 현행 리밸런스 빈도(분기 vs 월 자료 상충 — 운용상 진화 가능성), (d) 자사 4펀드 vs 화이트라벨 AUM 정확 분해(추정치만).
- 수익 검증의 비대칭(가장 중요): '기록 진실성'은 검증됨(HIGH) / '벤치마크 초과수익'은 미검증 — 오히려 검증된 결과가 지수 하회(profitability MEDIUM confidence). 절대 혼동 금지.
- north-star 충족 여부: '검증된 바로는 미충족.' US 대형주 시장 결과이며(KOSPI100 아님), MDD(−39%/−51%)는 우리 25% 강선호를 크게 초과.
- framing 과장 경고: 마케팅상 "$19B AUM"은 대부분 ETF Architect 화이트라벨/펀드서비스 자산(타 발행사 ETF 운용대행). 자사 4펀드 실제 규모는 각 수억 달러대(QMOM ~$466M, QVAL ~$583M, 2026-05 기준). 전체 AUM과 자사 알파펀드 AUM conflate 시 과장(= INFERENCE, 1차 마케팅 직접인용은 미확보).
- 적대적 경계: course/book seller 측면 존재하나, 상장 ETF의 제3자 일일 마킹이 이를 상쇄 → 증거 바 PASS.



### C3. Andrea Unger  ·  [소규모/개인/소형팀]

**선정 이유:** Group C(소규모/개인 검증 트레이더)의 증거 기준을 "official-competition record + broker-verified live"로 정면 충족하는 드문 케이스라 선정. World Cup Trading Championships는 Robbins Trading이 1983년부터 운영하는 year-long REAL-MONEY 대회로 paper trading 불가, 선물 부문 최소 $10,000 실계좌 입금 필수이며, 성과는 World Cup Advisor가 broker statements + trade confirmations를 검토해 공식 verification(self-reported 아님). 따라서 Group C의 흔한 함정(course-seller의 cherry-picked 스크린샷, 미검증 백테스트, 유튜브/트위터 자랑)과 달리 third-party-verified 실계좌 기록이 존재 → profitVerified=true.

더 결정적으로, 그의 매크로 설계철학(portfolio of many simple systems + per-system risk cap + robustness over optimization + walk-forward/OOS 규율)이 우리 브리프의 LLM adversarial critic 역할(overfit/leakage/regime 점검)과 직접 정렬되며, 솔로/소팀이 cloud-GPU+PC로 재현 가능한 저복잡도 아키텍처라 적용성(secondary objective) 평가에 높은 가치. 단 그의 수익은 futures/forex high-leverage 대회 산물이라 우리 저레버리지 equity 스코프엔 return 차원이 아니라 구조 차원에서만 유효 — Group C에서 "검증된 기록 + 추출 가능한 설계철학 + 명확한 적용 경계"를 동시에 만족하는 표본으로 선정.

**검증/성과 근거:** [FACT — broker-verified, 다수 독립 출처 일관 확인]
- 4회 우승 (유일 4회 우승자): 2008, 2009, 2010, 2012 World Cup Championship of Futures Trading.
- 연간 net % return (대회 계좌 기준): 2008 +672%, 2009 +115%, 2010 +240% (futures & forex), 2012 1st place (정확한 % 출처에 따라 불명확).
- 대회 구조 = REAL-MONEY, year-long, 선물 부문 최소 $10,000 실계좌, 성과는 broker statements + trade confirmations를 World Cup Advisor가 검토한 third-party verification.

[검증 신뢰도 = MEDIUM (HIGH 아님) — 대회 구조 자체의 inflation/selection 결함]
(a) Small-account percentage 구조: $10k 위 percentage-return 경쟁이라 high leverage·concentrated position을 구조적으로 인센티브화. 수백% 수익은 단기·고레버리지 산물이며 large capital에 scale 안 됨 → "지속 가능한 연복리 수익률"로 읽으면 안 됨.
(b) Survivorship bias: 폭발한 다수 참가자는 standings에서 사라지고 생존자만 노출.
(c) 공식 disclaimer: "WCC 계좌는 참가자의 전체 계좌를 대표하지 않는다" 명시 → multiple-entry / partial-account 가능성.

[INFERENCE] "검증된 실계좌 수익"은 사실이나, 우리 north star(KOSPI100 after-cost 상회)에 직접 매핑 가능한 sustainable CAGR 증거로는 부적합. 우리는 숫자를 버리고 설계철학만 채택.

[우리 스코프 무관] crypto 없음, 옵션 naked selling 없음 — 그의 기록은 futures/forex라 PRIMARY MARKETS(KR/US equities)와 instrument는 다르지만, portfolio-of-systems 아키텍처는 asset-class 불변.

**무엇인가:** Andrea Unger는 이탈리아 출신(1965년생, 트리에스테, Politecnico di Milano 기계공학 학위)의 풀타임 systematic trader로, 2001년경 전업 전환. World Cup Championship of Futures Trading의 유일한 4회 우승자(2008, 2009, 2010, 2012)다. 핵심 정체성은 "단일 천재 전략"이 아니라 다수의 단순 mechanical 시스템을 여러 시장·시간프레임에 병렬 운용하는 portfolio-of-systems 접근. 우승 이후 Unger Academy(유료 algorithmic-trading 교육 사업)를 창립.

[중요한 이중 정체성 분리] (1) third-party-verified 실계좌 대회 기록 = Tier3 충족 사실, (2) Unger Academy의 교육·마케팅 콘텐츠 = course-seller이므로 Tier3 미만 취급. 우리 평가는 (1)에서 설계철학만 추출하고 (2)의 수익 약속·커리큘럼 주장은 신뢰 근거로 쓰지 않는다.

우리 시스템(₩10M, KOSPI100→US, swing+mid/long, 저레버리지 equity)에 대한 본질: 그가 보여준 것은 "어떤 시그널이 돈을 버느냐"가 아니라 "어떻게 다수 시스템을 robustness 규율 위에서 조립·검증·리스크캡하느냐"라는 아키텍처/governance 철학이다. 가져올 가치는 거기에 있고, 대회 수익률 숫자 자체는 우리 스코프와 무관.

**거시 아키텍처:**

[END-TO-END LAYERED — 공개된 매크로 철학 기반 재구성. 구체 시그널·파라미터는 Unger Academy 유료 교육 뒤 = NON-PUBLIC]

L0 Universe/Data: 다수 시장(futures, forex, 일부 stocks)·다수 timeframe(intraday~daily/swing)에 걸친 가격 데이터. 핵심은 "한 시장에 베팅 안 함" — 시장 다변화 자체가 1차 분산.

L1 Strategy Factory (다수 단순 시스템 생성): trend-following / breakout / mean-reversion 등 서로 다른 logic의 단순 mechanical 규칙 시스템을 다수 생성. 설계 원칙 = "few parameters, simple rules" — 복잡·과최적화 회피가 1순위. [이것이 그의 핵심 차별점: alpha를 한 천재 모델에서 찾지 않고 mediocre-but-robust 시스템 다수의 합에서 찾음.]

L2 Robustness/Validation Gate (배포 전 검증층): walk-forward analysis + out-of-sample 테스트 + parameter-space stability(파라미터 살짝 바꿔도 안 무너지는지) 점검. curve-fitting/overfit를 통과 못 하면 배포 거부. → 이 층이 우리 브리프의 LLM adversarial critic(leakage/overfit/regime 점검)과 1:1 대응.

L3 Portfolio Assembly (조립층): 통과한 시스템들을 상관관계 낮게 조합 → 개별 시스템의 들쭉날쭉한 equity curve를 합산해 부드럽게. 시스템 간 분산 + 시장 간 분산 + 시간프레임 간 분산의 3중 분산.

L4 Risk Layer (per-system + portfolio cap): 각 시스템마다 독립적 risk/position-sizing 규칙(per-system risk cap) + 포트폴리오 전체 레벨 리스크 관리. 한 시스템이 망가져도 portfolio가 견디게 설계.

L5 Execution: mechanical·rule-based 자동 실행 (대회는 자동매매 플랫폼 기반). 재량 개입 최소화.

[FACT vs INFERENCE 경계] L1~L4의 "철학"(다수 단순 시스템·robustness 우선·walk-forward·per-system risk·분산)은 그의 인터뷰/저서/Academy 공개 콘텐츠에서 FACT로 일관 확인. 그러나 각 층의 정확한 구현(어떤 지표, 어떤 임계값, 몇 개 시스템, 정확한 sizing 공식)은 INFERENCE/NON-PUBLIC — Group C답게 "secret structure is fine": 매크로 골격은 알 수 있으나 alpha 디테일은 유료 벽 뒤.

**데이터 흐름:** [공개 매크로 기준 재구성 — 구체 파이프라인 코드는 NON-PUBLIC]

가격/시장 데이터(다수 시장·timeframe) → [전처리/정렬] → Strategy Factory에서 다수 단순 후보 시스템 각각이 backtest 시그널 생성 → [Robustness Gate] walk-forward로 in-sample 최적화 + out-of-sample 검증, parameter-stability 스캔 → 통과 시스템만 통과(실패 시 폐기/재설계 루프) → [Portfolio Assembly] 통과 시스템들을 저상관 조합으로 묶음 → [Risk Layer] per-system risk cap + portfolio cap 적용해 각 시스템 시그널을 사이즈 결정 → [Execution] 자동 주문 → 실계좌 체결 → broker statements/trade confirmations가 성과 기록(대회에선 이것이 third-party verification 입력) → 성과·drawdown 모니터링이 다시 시스템 retire/replace 의사결정으로 피드백.

핵심 흐름 특성: (1) 데이터→시그널이 다수 병렬 파이프라인으로 fan-out 후 portfolio 레벨에서 fan-in (aggregate). (2) 검증(L2)이 데이터플로의 게이트로 작동 — "검증 안 된 시그널은 portfolio에 진입 불가"가 구조적 강제. (3) 우리 시스템 매핑: 이 fan-out/검증-게이트/fan-in 구조는 우리의 multi-strategy scanner→OOS gate→portfolio allocator→risk engine→auto-exec 흐름과 동형이며, KR/US equities·swing/mid-long에 그대로 이식 가능(asset-class 불변).

**자동화 수준:** HIGH (거의 완전 mechanical/automated). 

[FACT] 그의 시스템은 정의상 rule-based·mechanical이며 재량 개입을 최소화하도록 설계 — 대회 자체가 자동매매 플랫폼(World Cup Advisor AutoTrade로 미러링 가능할 정도) 기반이라 시그널 생성→실행이 자동. 인간의 역할은 (a) 시스템 설계/검증, (b) portfolio 구성, (c) retire/replace 결정, (d) 리스크 한도 설정 — 즉 "주문 단위 개입"이 아니라 "메타 레벨 governance"에 집중.

[우리 AUTOMATION/GOVERNANCE 타깃과의 정렬] 브리프 목표("normal orders auto-execute WITHOUT human approval; 인간은 예외·mode-switch·deploy·risk-limit·kill-switch에서만 개입")와 그의 운용 모델이 구조적으로 거의 일치. 정상 주문은 시스템이 자동 집행, 인간은 시스템 배포·교체·리스크 한도 같은 메타 결정에만 관여. 이는 우리가 추구하는 "high automation + human only at exceptions/deploy/risk" 모델의 검증된 선례.

[INFERENCE] 그의 자동화에 우리 브리프가 추가하려는 LLM council(news/filings event interpretation + adversarial critic + governance veto)은 그의 시대엔 없었던 층. 다만 그의 L2 Robustness Gate가 사실상 "사람이 수행하는 adversarial overfit 점검"이며, 우리는 이 역할을 LLM adversarial critic으로 자동화/증강하는 형태로 진화시키면 됨.

**인간 개입 지점:** 그의 운용을 우리 브리프의 5개 개입 지점에 매핑 (FACT=공개 철학 기반, 일부 INFERENCE 표시):

- normal-orders-auto: YES (FACT). 정상 시그널/주문은 mechanical 시스템이 인간 승인 없이 자동 집행. 우리 타깃과 동일.

- mode-switch (aggressive/stable/conservative): PARTIAL/INFERENCE. 그의 공개 철학엔 명시적 "모드 자동전환" 개념은 두드러지지 않음. 대신 "시스템 portfolio 구성 변경"이 사실상의 regime 대응(특정 시장/로직 비중 조절). 우리 모델의 "조건 충족 시 자동 mode-switch, 아니면 human approval"은 그에게서 직접 상속되지 않는 우리 추가 설계.

- deploy-approval (전략 배포 승인): YES (FACT, 인간 게이트). 새 시스템은 robustness/walk-forward/OOS 통과 후에만 portfolio에 투입 — 즉 인간이 검증 결과를 보고 배포 승인. 우리의 "strategy-deployment approval" 지점과 정확히 대응. (우리는 여기에 LLM adversarial critic을 검증 보조로 얹음.)

- risk-limit-approval: YES (FACT). per-system risk cap + portfolio cap 설정·조정은 인간 governance 결정. 우리의 "risk-limit approval" 지점과 대응.

- kill-switch: INFERENCE. 명시적 "kill-switch" 용어는 공개 자료에 두드러지지 않으나, drawdown 기반 시스템 retire/replace가 사실상의 단계적 차단. 우리는 명시적 kill-switch를 별도 설계해야 함(그에게서 상속 불가).

[종합] 그의 모델은 normal-orders-auto / deploy-approval / risk-limit-approval 3개에서 우리 타깃과 강하게 정렬, mode-switch와 kill-switch는 우리가 추가 설계해야 할 gap.

**데이터 사용:** [데이터 표현 관점 — public 매크로 기반 재구성, 구체 파이프라인은 NON-PUBLIC]

가장 중요한 사실: Unger의 시스템은 "데이터 풍부"가 아니라 "데이터 검소(data-frugal)"하다. 입력은 거의 전적으로 OHLCV 가격/시장 데이터(다수 market × 다수 timeframe). 대안데이터(alt-data)·뉴스·펀더멘털·옵션 vol surface 같은 고차원 피처는 그의 공개 철학에 등장하지 않음. 이는 large-fund(Two Sigma류 alt-data 수천 소스)와 정반대 극단 — Group A가 "데이터 우위"로 알파를 찾는다면 Unger는 "구조 우위(다수 robust 시스템의 합)"로 찾는다.

데이터 표현(representation)의 핵심 설계:
- 단위(unit) = (시장 × 시간프레임 × 시스템 logic) 조합. 한 시장의 일봉이 아니라, 동일 logic을 여러 시장·여러 timeframe에 fan-out 적용.
- 시간 분할(temporal split)이 데이터 사용의 중심 규율: in-sample(최적화) / out-of-sample(검증) / 그리고 사실상의 incubation(배포 후 실시간 forward 관찰)으로 데이터를 3구간 분리. 이 split 규율이 데이터 사용의 본질이며, 피처 엔지니어링보다 우선한다.
- low-dimensionality 강제: "few parameters, simple rules" → 입력 피처 차원을 의도적으로 낮춰 데이터/파라미터 비율을 보수적으로 유지(과최적화 방어).

[우리 ₩10M / KOSPI100→US / swing+mid-long 매핑]
직접 이식 가능. 우리도 OHLCV 중심으로 시작하고, KR equities 일봉/주봉(swing/mid-long)에 동일 logic을 종목 cross-section + KOSPI100 universe로 fan-out. 데이터 검소성은 솔로+₩10M에 결정적 이점 — 비싼 alt-data 없이도 구조로 robustness를 살 수 있다는 검증된 선례. LLM council은 그가 안 쓴 뉴스/filings/earnings-call 층을 "alpha contributor + adversarial critic"로 얹는 우리만의 추가 데이터 층이며, 그의 OHLCV 코어를 대체가 아니라 보강한다.

[FACT/INFERENCE 경계] OHLCV 중심·시간 3분할·low-dim은 그의 인터뷰/저서에서 일관 확인되는 FACT. 정확한 피처(어떤 지표·룩백·임계값)는 Unger Academy 유료 벽 뒤 = NON-PUBLIC.

**alpha 생성:** [알파 생성 접근 — 그의 가장 이식가능한 통찰]

핵심 thesis (FACT, 일관 공개): 알파는 "한 개의 천재 모델"이 아니라 "다수의 mediocre-but-robust 단순 시스템의 portfolio 합"에서 나온다. 개별 시스템 각각은 평범하고 들쭉날쭉한 equity curve를 갖지만, 저상관 조합 시 portfolio 레벨에서 부드럽고 안정적인 수익 곡선이 emergent하게 발생. 즉 그의 "알파 엔진"은 시그널이 아니라 조립(assembly)과 분산(diversification)이다.

알파의 3중 분산 원천:
1) 시스템 logic 간 분산 — trend-following / breakout / mean-reversion 등 서로 다른 시장가설을 가진 logic 혼합 (한 regime에서 죽는 logic이 다른 regime에서 산다).
2) 시장(market) 간 분산 — 한 자산에 베팅 안 함.
3) 시간프레임 간 분산 — intraday~daily/swing 혼합.

알파 철학의 우선순위 역전: 대부분 트레이더가 "수익 극대화 → 그 다음 robustness"인 반면, Unger는 "robustness 우선 → 그 결과로 지속 수익". 과최적화로 backtest 수익률을 짜내는 것을 명시적으로 거부. 이것이 그를 course-seller 군중과 구분하는 진짜 알파 규율.

[우리 시스템 매핑 — 가져갈 것]
₩10M·솔로에 정확히 맞는 알파 철학. 우리는 단일 "마법 swing 전략"을 찾지 말고, KOSPI100에서 (a) cross-sectional momentum (b) mean-reversion (c) breakout/추세 추종 등 저상관 swing/mid-long 시스템 묶음을 만들고 portfolio 레벨에서 합산해야 한다. KR tax 0.20% 비용 환경에서 과최적화·과매매를 피하는 우리 north star(after-cost KOSPI100 상회)와 robustness-first 철학이 직접 정렬.

[버릴 것] 그의 알파가 산출한 +672%/+240% 같은 대회 수익률은 small-account high-leverage futures/forex 산물 → 우리 저레버리지 equity 스코프와 무관. return을 targeting하지 말고 robustness 규율만 채택. crypto/naked option 없음(스코프 일치).

[알파에서 LLM의 자리] 그의 알파 생성은 순수 quant. 우리 LLM council은 그 위에 news/filings/earnings event 해석을 "추가 alpha contributor"로 얹되, 최종 buy/sell/size 결정권은 주지 않음(브리프 준수) — LLM은 그의 L2 Robustness Gate(사람이 하던 overfit 점검)를 자동화·증강하는 adversarial critic 역할이 더 본질적 기여.

**모델·표현:** [모델 분석 — 이름 나열이 아닌 데이터표현 + 예측문제 + 검증 + 시스템내위치 관점]

데이터 표현(data representation): 저차원 OHLCV 기반 rule-system. ML/DL/TSFM(시계열 foundation model)·financial-FM 같은 무거운 모델은 그의 스택에 없음. 이는 결함이 아니라 의도된 선택 — 모델 복잡도가 곧 과최적화 리스크라는 입장. Group A/B의 deep-learning 스택과 정반대 극단을 대표하며, 솔로+₩10M에 "모델이 단순할수록 검증·재현이 쉽다"는 교훈 제공.

예측 문제(prediction problem): 명시적 "수익률 예측(regression)"이나 "방향 분류(classification)"가 아니라, "규칙 충족 시 진입/청산"이라는 decision-rule 형태. 즉 예측을 점수화하지 않고 행동을 직접 trigger하는 rule-based policy. 각 시스템은 작은 edge(승률·손익비의 통계적 우위)를 노리는 weak learner이고, portfolio가 일종의 ensemble로 weak learner들을 합산. → 개념적으로 "ensemble of weak rule-based learners"로 읽으면 우리 시스템 언어로 매핑 가능.

검증(validation) — 모델 표현에서 가장 중요한 부분: walk-forward analysis + out-of-sample + parameter-space stability가 사실상 "모델 선택(model selection)" 메커니즘. 모델의 품질을 in-sample fit이 아니라 (1) OOS 성과, (2) 파라미터를 살짝 흔들어도 무너지지 않는 안정성으로 정의. 이는 deflated-Sharpe/multiple-testing 정신과 동형 — "여러 후보 중 운 좋게 fit된 것"을 걸러내는 게이트.

시스템 내 위치(position-in-system): 각 모델(=시스템)은 독립적 신호 생성기로 fan-out 위치, portfolio assembly 층에서 fan-in. risk layer가 각 모델 출력을 per-system cap으로 사이징. 즉 모델은 "최종 결정자"가 아니라 "검증 게이트를 통과해야만 portfolio에 입장하는 후보". 

[우리 매핑] 우리 LLM council의 올바른 architectural position이 여기서 도출됨: LLM도 Unger의 개별 시스템처럼 "최종 결정자가 아니라 검증·보강 층"에 위치해야 한다(브리프의 "LLM은 risk engine 위에 군림 금지, optimizer/risk 위 review layer" 지시와 정확히 일치). optimizer/risk/cost/execution 층은 우리가 추가 설계하되, Unger의 골격(검증 게이트가 모델 입장을 통제)을 그대로 차용.

[NON-PUBLIC 경계] 정확한 모델 개수·지표·sizing 공식은 유료 벽 뒤 → "철학 이식 가능, 복제 불가".

**portfolio/risk/execution:** [포트폴리오 / 리스크 / 실행 — 그의 진짜 차별점]

Portfolio assembly: 검증 통과 시스템들을 저상관(low-correlation) 기준으로 조합. 목적은 수익 극대화가 아니라 equity curve smoothing — 개별 시스템의 거친 곡선을 합산해 drawdown을 구조적으로 낮춤. "분산이 곧 알파"의 운영적 구현.

Risk layer(2단 구조, FACT):
- per-system risk cap: 각 시스템이 독립적 position-sizing/리스크 한도를 가져, 한 시스템이 망가져도 그 손실이 격리됨(blast-radius 제한).
- portfolio-level cap: 전체 레벨에서 총 익스포저 관리.
이 2단 cap이 그의 "장기 생존" 메커니즘 — 어떤 단일 시스템도 portfolio를 죽이지 못하게 설계.

Execution: 완전 mechanical·rule-based 자동 집행. 대회가 World Cup Advisor AutoTrade로 미러링 가능할 만큼 자동화 → 재량 개입 최소화. 정상 주문은 인간 승인 없이 자동 체결.

[검증 신뢰도 경고 — MEDIUM, HIGH 아님]
대회 구조 자체가 small-account percentage 경쟁이라 high leverage·concentrated position을 인센티브화 → 수백% 수익은 단기·고레버리지 산물이며 large capital에 scale 안 됨. survivorship bias(폭발한 참가자는 standings에서 소멸) + 공식 disclaimer("WCC 계좌는 참가자 전체 계좌를 대표 안 함" → multiple-entry/partial-account 가능). 따라서 그의 risk 설계 "철학"은 채택하되, 대회 수익률을 sustainable CAGR로 읽으면 안 됨.

[우리 ₩10M / KOSPI100 매핑]
가장 직접 이식 가능한 층. 우리 multi-strategy scanner → OOS gate → portfolio allocator → risk engine → auto-exec 흐름이 그의 fan-out → 검증게이트 → fan-in → 2단 risk cap → auto-exec와 동형(asset-class 불변). 단 우리는 저레버리지 equity이므로 그의 high-leverage sizing은 버리고, per-system cap + portfolio cap의 "2단 격리" 개념만 차용. MDD 25% strong-preference는 그의 low-correlation smoothing + 2단 cap으로 구조적으로 추구 가능.

[FACT/INFERENCE] 2단 risk cap·저상관 조립·mechanical auto-exec = FACT. 정확한 cap 수치·가중 방식 = NON-PUBLIC.

**검증 규율:** [검증 규율 — Unger 모델의 심장. leakage/walk-forward/deflated-sharpe/multiple-testing 관점]

walk-forward analysis (FACT): in-sample 구간에서 파라미터 최적화 → 인접 out-of-sample 구간에서 검증 → 윈도우를 굴려가며 반복. 단일 backtest fit이 아니라 "rolling OOS 성과의 일관성"으로 시스템을 판정. 이것이 그의 1차 anti-overfit 장치.

out-of-sample + incubation: 배포 전 OOS 검증에 더해, 실배포 후 실시간 forward 관찰(incubation)로 "backtest와 live의 괴리"를 추가 필터링. = 사실상의 paper/forward validation 단계.

parameter-space stability (핵심): 최적 파라미터 1점이 아니라 그 주변(파라미터를 살짝 흔든) 성과가 무너지지 않는지를 본다. = "fitness landscape의 평평한 봉우리"를 요구. 날카로운 봉우리(한 점에서만 좋은 값)는 curve-fitting으로 간주해 거부. → 이는 학계의 deflated Sharpe / multiple-testing 보정과 동일한 정신("여러 후보를 시험하면 운 좋게 좋아 보이는 게 나온다"를 방어).

multiple-testing 자각: 그는 다수 시스템을 생성하므로 "여러 번 시험하면 우연히 좋은 게 나온다"는 위험에 구조적으로 노출 — 이를 OOS + parameter-stability + 저상관 조합으로 상쇄. (단 명시적 deflated-Sharpe 통계 보정을 쓴다는 공개 증거는 없음 = INFERENCE 영역; 우리는 여기를 통계적으로 더 엄격히 보강해야 함.)

leakage 방어: 시간 순서 엄수(in-sample이 OOS보다 과거), look-ahead 금지가 walk-forward 구조에 내장.

[우리 매핑 + 보강점]
walk-forward + OOS + parameter-stability를 "배포 전 강제 게이트"로 코드화하는 것이 우리가 가장 먼저 베낄 것. 추가로 우리는 그가 명시적으로 안 한 deflated Sharpe / multiple-testing 보정 / purged K-fold(KR equities cross-section 누수 방지)를 LLM adversarial critic + 통계 게이트로 보강해야 함 — 이것이 그의 "사람이 하던 검증"을 우리 시대의 자동화된 검증으로 진화시키는 지점.

[FACT/INFERENCE] walk-forward·OOS·parameter-stability·incubation = FACT(일관 공개). deflated-Sharpe 등 정식 통계 보정 사용 여부 = 공개 증거 없음(우리 보강 영역).

**솔로가 배울 점 (lessonsForSmall):** [우리 시스템(솔로+AI, ₩10M, KOSPI100→US, swing+mid/long, KR tax 0.20%, north star=after-cost KOSPI100 상회)이 현실적으로 벤치마킹할 것]

벤치마킹할 것 (HIGH priority, 직접 이식):
1) Portfolio-of-systems가 솔로의 정답. 단일 "완벽한 swing 전략" 추구를 포기하고, KOSPI100에서 저상관 swing/mid-long 시스템 3~5개(cross-sectional momentum + mean-reversion + breakout/추세)를 만들어 합산. 분산이 알파이자 MDD 방어. → ₩10M 규모에 가장 현실적인 robustness 경로.
2) Robustness-first 검증 게이트. walk-forward + OOS + parameter-stability를 "배포 전 강제 통과 게이트"로 코드화. 검증 안 된 시그널은 portfolio 입장 금지(구조적 강제). KR tax 0.20% 환경에서 과최적화·과매매가 곧 손실이므로 이 규율이 north star에 직결.
3) 2단 risk cap (per-system + portfolio) = 솔로가 한 전략 폭발로 전멸하지 않는 최소 안전장치. ₩10M 소액일수록 blast-radius 격리가 생존 핵심.
4) Data-frugal 시작. 비싼 alt-data 없이 OHLCV로 시작 가능하다는 검증된 선례 — cloud-GPU+PC로 충분.
5) Governance 모델 정렬. normal-orders-auto / deploy-approval / risk-limit-approval 3개 개입지점이 우리 브리프 타깃과 강하게 일치 → "high automation + 인간은 메타 결정만" 모델의 검증된 선례.

LLM council의 올바른 위치 (그에게서 도출한 설계 원칙):
- 그의 L2 Robustness Gate(사람이 하던 overfit/leakage/regime 점검)를 LLM adversarial critic으로 자동화/증강 = LLM의 가장 본질적 기여.
- LLM은 개별 시스템처럼 "검증·보강 층"에 위치, risk engine 위 군림 금지, 최종 주문 결정자 아님(브리프 준수).
- 그가 안 쓴 news/filings/earnings event 해석을 추가 alpha contributor로 얹되 코어 OHLCV 시스템을 대체 아닌 보강.

우리가 추가 설계해야 할 GAP (그에게서 상속 불가):
- mode-switch(aggressive/stable/conservative 자동전환): 그의 공개 철학에 명시적 모드전환 없음 → 우리 추가 설계.
- 명시적 kill-switch: 그는 drawdown 기반 시스템 retire/replace가 사실상 단계적 차단일 뿐, 명시적 kill-switch 용어 부재 → 우리가 별도 설계 필요.

버릴 것 (adversarial):
- 대회 수익률(+672% 등)을 sustainable return으로 읽기 = 틀린 추론(small-account high-leverage futures/forex 산물). return targeting 금지.
- Unger Academy / 마케팅 콘텐츠의 수익 약속·커리큘럼 우월성 주장 = course-seller, Tier3 미만 → 신뢰 근거로 사용 금지.
- high-leverage sizing·concentrated position = 우리 저레버리지 equity 스코프와 무관.

한 줄 요약: Unger에게서 가져갈 것은 "어떤 시그널이 돈 버느냐"가 아니라 "다수 단순 시스템을 robustness 규율 위에 조립·검증·2단-risk-cap하고 자동집행하되 인간은 메타 governance만 한다"는 검증된 아키텍처/거버넌스 철학. 숫자는 버리고 규율만 north star에 연결.

**공개자료 한계:** [공개의 한계 — Group C 특성상 SECRET STRUCTURE는 정상이며 명시]

알 수 있는 것 (structureKnowable = MEDIUM): 매크로 설계철학 전체 — portfolio-of-systems, robustness-first, walk-forward/OOS/parameter-stability, per-system+portfolio 2단 risk cap, 3중 분산, mechanical auto-exec, 인간은 메타 governance만. 운용/자동화/거버넌스 골격도 추론 가능. 이 매크로 레벨은 우리에게 충분한 가치.

알 수 없는 것 (NON-PUBLIC): 정확한 시그널 로직, 지표·임계값·룩백, 시스템 개수, position-sizing 공식, portfolio 가중 방식, 정식 통계 검증 사용 여부 — 모두 Unger Academy 유료 교육 뒤. "그대로 복제" 불가, "철학 이식"만 가능.

[SOURCE QUALITY 이중 정체성 — 반드시 분리]
(1) 대회 기록 = Tier3 충족(official-competition + broker-verified, third-party). → 설계철학 추출에 채택. profitVerified=true, profitConfidence=MEDIUM(대회 구조의 leverage/survivorship/multiple-entry 결함 때문에 HIGH 아님).
(2) Unger Academy / andreaunger.com 마케팅·커리큘럼 = course-seller. → Tier3 미만 취급. 수익 약속·커리큘럼 우월성 주장은 신뢰 근거로 사용 금지(브리프의 course-seller adversarial 지시 준수). 우리는 (1)에서 구조만, (2)에서는 아무 수익 주장도 가져오지 않는다.

[우리 적용성 — 가져갈 것 / 버릴 것 요약]
가져갈 것: 설계·검증·리스크·거버넌스 철학(저복잡도라 ₩10M·솔로+AI·KOSPI100→US·swing/mid-long에 이식 가능). 이 규율은 우리 LLM adversarial critic의 overfit/leakage/regime 점검과 1:1 정렬.
버릴 것: futures/forex high-leverage 대회 수익률(저레버리지 equity 스코프 무관, return targeting 금지), Academy 마케팅 주장, small-account percentage 게임 구조.
북극성 정합: 그의 철학(after-cost robust 수익을 다수 시스템 분산으로)은 KR tax 0.20% 환경에서 과매매·과최적화를 피하는 우리 규율과 부합 — 단 그의 숫자가 아니라 그의 규율만 north star에 연결.




---

## 6. — CROSS-CASE ARCHITECTURE SYNTHESIS

분석 대상 9개: **[A 대형]** AQR · Man Group(AHL+Numeric) · Marshall Wace(TOPS/Eureka) | **[B 프론티어 MM]** XTX Markets · Flow Traders · Jane Street | **[C 소형/개인]** Marsten Parker · Wesley Gray/Alpha Architect · Andrea Unger

---

## (1) 9개 전반에 반복되는 시스템 패턴 (Repeated System Patterns)

규모·자산군·전략이 전부 달라도 **동일하게 반복되는 6개 구조 불변식(structural invariants)** 이 관측된다. 이것이 섹션 6의 가장 중요한 결론이다.

**P1 — 명확한 레이어 책임분리 (signal → portfolio/optimizer → risk-engine → execution), 그리고 "어떤 단일 신호도 단독 결정 못 함".**
9개 *전부*가 이 위계를 갖는다. AQR(7-layer: research→signal→risk model→optimizer→execution→product→governance), Man(L0~L5: data→signal→risk model→optimizer→risk-engine→governance), Marshall Wace(idea→contributor-scoring→aggregation→risk/optimizer→execution), XTX(L0 data→L1 central ML→L2 learned signal→L3 MM deployment→L4 risk), Flow Traders(L1~L6 fair-value→quote→arb→risk/hedge→capital), Jane Street(data→research/sim→pricing→risk/inventory→execution→governance), Parker(6 systems→portfolio→MAR/system-stop→exec), Unger(strategy factory→robustness gate→portfolio assembly→2-tier risk cap→exec). **핵심 공통 명제: "risk-engine은 항상 signal 위에 군림한다(risk > signal)".** Jane Street("risk engine > signal"), Flow Traders("리스크 엔진이 트레이딩 엔진 위에"), Marshall Wace("신호는 입력, 옵티마이저가 최종 통제"), AQR/Man("optimizer가 최종 사이즈 결정자")이 명시적으로 동일하게 말한다. — *우리 LLM-council을 risk-engine "아래" review-layer에 두는 설계의 9/9 외부 근거.*

**P2 — 단일 천재 신호가 아니라 다수 약신호의 앙상블·분산 (weak-signal ensemble / breadth).**
AQR("Fundamental Law: IR ≈ IC×√breadth, 각 베팅은 약해도 분산되면 견고"), Man AHL("다수의 약한 정보원을 결합해 개별 소스보다 강한 signalling power" — 명시 철학), Marshall Wace("개별 idea는 평균적으로 무가치, 다수+검증가중에서 알파"), Parker("여러 무상관 룰베이스 시스템의 포트폴리오"), Unger("mediocre-but-robust 시스템 다수의 합, 분산이 곧 알파"), Jane Street("다수 약신호 앙상블", Kaggle weak-feature 구조). 6/9가 명시적, 나머지(XTX cross-asset 단일 두뇌, Flow Traders 다상품, Alpha Architect 멀티팩터)도 실질적 분산 구조.

**P3 — 예측은 절대수익이 아니라 cross-sectional 상대 랭킹 (relative ranking, not absolute return).**
AQR("동료 대비 아웃퍼폼 확률의 순위 문제"), Man Numeric("종목별 횡단면 상대 return forecast"), Marshall Wace("종목 over/under-weight 랭킹"), Alpha Architect("rank-transform = decile cut, 절대값 아닌 상대순위"), Jane Street("cross-instrument 정합성"). — *우리 KOSPI100 top-N 횡단면 설계와 동형.*

**P4 — 비용·구현가능성을 최적화에 내재화 (cost internalization, net-of-cost 우선).**
AQR가 가장 명시적('Implementable Efficient Frontier' = 비용을 목적함수에 넣고 gross 아닌 net-of-cost로 모델 선택; 'Trading Costs of Anomalies' = 고회전 신호는 비용에 먹힘). Man("turnover·거래비용 목적함수 내장"), Jane Street(utility/비용가중 타깃), Alpha Architect(분기 저회전 + ETF in-kind로 비용 구조적 최소화). — *KR tax 0.20%를 optimizer 비용항에 넣으라는 4/9 직접 지령.*

**P5 — 높은 자동화 + 인간은 메타-거버넌스에만 (정상 주문 무재량 자동, 인간은 배포·한도·예외·킬스위치).**
9/9 전부. XTX("재량 트레이더 없는 완전 자동 AI 운용"), Flow Traders/Jane Street(μs closed-loop), AQR/Man/Marshall Wace(systematic 무재량), Parker(자작 SW 결정적 집행 + 인간은 전략 은퇴·배포 게이트), Unger(mechanical auto-exec + 인간은 메타 governance). 우리 거버넌스 5-슬롯(normal-orders-auto / mode-switch / deploy-approval / risk-limit / kill-switch)과 거의 1:1 매핑.

**P6 — 배포 전 검증 게이트 = 과적합 방어가 알파만큼 중요 (validation-as-gate).**
AQR(economic-prior first + 글로벌/다기간 OOS + net-of-cost), Man(ML도 라이브 전 ~5년 검증, point-in-time, black/glass-box 병치), Jane Street(types-as-veto + purged/embargoed walk-forward), Parker(robustness-first: parameter plateau + 표본수 + 백테스트 최악 DD 추적), Unger(walk-forward + OOS + parameter-stability + incubation). — *LLM adversarial critic(leakage/overfit/regime) 역할의 직접 원형.*

---

## (2) 대형(LARGE) vs 소형(SMALL)의 차이와, 무엇이 IDENTICAL인가

**IDENTICAL (규모 무관, 그대로 이식 가능 — 가장 중요)**
- **아키텍처 골격(P1)·검증규율(P6)·거버넌스 토폴로지(P5)는 르네상스급부터 1인 Parker까지 동일.** Parker의 (다중 무상관 시스템 → MAR/system-stop → 자동집행 → 전략 은퇴 게이트) 구조는 Man의 (L1 signal → L3 risk-engine → L5 governance)를 1인 규모로 축소한 동형 구조다. Unger의 2-tier risk cap = Flow Traders/Jane Street의 inventory risk-engine과 같은 발상.
- **risk > signal 위계**는 AQR($120B)와 Unger($10k 대회계좌)에서 글자 그대로 같다.
- **검증 규율**(walk-forward·OOS·net-of-cost·overfit 방어)은 AQR/Man의 조직적 게이트 = Parker/Unger의 1인 게이트로 *형태만 다르고 원리 동일*.

**DIFFERENT (규모가 만드는 진짜 차이)**
| 축 | LARGE (A/B) | SMALL (C) |
|---|---|---|
| 알파 원천 | 데이터 우위·breadth·인프라(XTX 25k GPU/650PB, Two Sigma류 alt-data) | **구조 우위**(Unger "데이터 검소", Parker OHLCV만, Alpha Architect EOD+분기재무) |
| profit 증거 | audited 회계·returns·net income (Man LSE statutory, Flow/Jane Street firm-level, AQR press returns) | competition/broker-verified live (Parker Schwager 실사, Unger WCC, Alpha Architect ETF NAV) |
| 검증 강도 | firm-level HIGH, 단 strategy-level은 secret | live 기록은 강하나 표본=1·survivorship 리스크 |
| optimizer | 정교한 mean-variance/factor-neutral | **의도적 단순화**(Alpha Architect 1/N 동일가중 — "optimizer는 추정오차만 키운다", Parker 단순배분) |
| 무엇을 버리나 | — | 거대 AUM·alt-data·HFT·풀 long-short·레버리지(전부 비이식) |

**핵심 통찰: 규모가 바꾸는 것은 "알파의 원천(데이터 vs 구조)"과 "증거 종류"뿐이고, "시스템 골격·검증·거버넌스"는 불변이다.** 솔로(₩10M)가 베낄 수 있는 것은 바로 이 불변 부분이며, 대형의 가변 부분(데이터·규모·HFT)은 버려야 한다. — Parker/Unger가 group C에 들어간 이유 = 이 불변 구조를 1인 규모로 검증된 형태로 보여주기 때문.

---

## (3) HIGH-PROFIT 시스템들이 구조적으로 공유하는 것

profit이 가장 강하게 검증된 그룹 — **Jane Street(FY24 net trading revenue ~$20.5B), XTX(FY24 audited net profit £1.28B), Flow Traders(FY24 net profit €159.5m), Man Group(FY25 AUM $227.6B record), AQR(2024 top fund ~+71%)** — 이 공유하는 구조적 특징:

**S1 — 알파(예측)와 수익화(실행/배포)의 명확한 분리, 그리고 예측을 cross-asset 중앙 자산으로.**
XTX가 가장 순수("예측 = 단일 중앙 두뇌, 50,000+ 상품 공유; 마켓메이킹은 배포 표면일 뿐"). Jane Street(pricing 엔진 ≠ inventory/risk), Flow Traders(fair-value 엔진 → 호가/차익/헤지). **고수익 = 더 나은 예측 × 그 예측을 넓은 표면에 산업 규모로 배포.** XTX 명시: "초저지연 회사가 아니라 더 나은 price forecast 회사."

**S2 — 검증가능성(profit-verifiability)은 사업/조직 형태에서 나온다 (전략 우월성과 별개).**
고검증 케이스는 전부 *구조적 공개 강제*가 있다: XTX(UK Companies House audited), Flow Traders/Man(상장사 statutory), Jane Street(채권발행 disclosure). — 중요한 adversarial 분리: **이들의 검증된 것은 "절대 net income"이지 "risk-adjusted strategy return"이 아니다.** Sharpe/MDD는 전부 블랙박스. 즉 "돈을 벌었다"는 검증돼도 "우리 north star(after-cost risk-adjusted)와 비교 가능"한 게 아니다.

**S3 — 두 루프 분리 (slow learning loop + fast execution loop).**
XTX(오프라인 GPU 학습 ↔ 온라인 μs 호가), Jane Street(research=production 코드 공유로 implementation gap 제거), Man(research-feed 환류 ↔ 자동 집행). **느린 연구 루프와 빠른 실행 루프를 같은 데이터 표현으로 잇되 분리** — train-serve skew 차단이 수익 보존의 핵심.

**S4 — 분산(diversification)이 수익이 아니라 생존의 엔진.**
고수익 펀드의 AUM 회복(Man $168B→$227B, AQR quant winter 후 회복)은 단일 전략이 아니라 멀티전략·멀티에셋 분산에서 왔다. Marshall Wace(60% systematic + 40% discretionary 한 리스크 프레임), AQR(value↔momentum 음의 상관 앙상블).

**경고(반복 강조): 9개 중 어느 것도 "검증된 after-cost risk-adjusted 초과수익"을 우리에게 직접 제공하지 않는다.** firm-profit-verified ≠ strategy-replicable. 이 구분이 9-target 평가 전반의 잣대.

---

## (4) 실패 확률이 높은 구조 (High Failure-Probability Structures)

9개의 *명시적 실패·취약 증거*에서 도출 — 우리가 피해야 할 안티패턴.

**F1 — 단일 엣지 집중 + 레버리지 (concentration × leverage).**
**Parker 2015-16: mean-reversion 단일 엣지에 레버리지 집중 → 7개월 −45% 드로다운** (본인이 가장 비싸게 학습한 교훈, 이후 system-stop 도입). 무상관 설계도 한 엣지에 자본·레버리지를 몰면 무력화. — 우리 ₩10M·솔로에 직접 사형선고급 경고.

**F2 — 리스크 거버넌스 부재 (no mode-switch / no kill-switch) + always fully-invested.**
**Alpha Architect QMOM −39.13%, QVAL −51.49% MDD** — 공개·규율 있는 단일 factor 시스템조차 risk-overlay·kill-switch가 없어 드로다운을 끝까지 먹고, 게다가 **10년 라이브에서 S&P500을 LAG**. "규율 있고 공개된 시스템도 거버넌스가 없으면 깊은 드로다운 + 다년 지수 하회를 그대로 감내한다" = 우리 MDD 25% 선호의 직접 동기. mode-switch·kill-switch는 9개 중 C 그룹·Alpha Architect가 *결여*한 가장 흔한 갭.

**F3 — 변동성/레짐 의존 P&L (regime-dependent, not persistent edge).**
**Flow Traders €36.2m→€159.5m 4배 YoY 스윙** = P&L이 변동성 레짐에 강하게 종속(조용한 시장이면 알파가 마름). **AQR quant winter: AUM $226B→<$100B (50%+ 증발), 팩터가 수 년 underperform.** Unger 대회 +672%도 small-account high-leverage 단기 산물(scale 안 됨). — 한 해 좋은 성과를 persistent edge로 오독하면 실패. 팩터는 수 년 죽을 수 있다.

**F4 — overfit / curve-fitting + multiple-testing 함정.**
Unger(parameter plateau 아닌 "날카로운 봉우리"는 curve-fit으로 거부), Parker(robustness>optimization), Jane Street(purged/embargoed split, weak-feature 다중검정), AQR(economic-prior 없는 data-mining 신호 거부). 다수 전략을 돌릴수록 우연한 승자가 나옴 → deflated Sharpe로 할인 필수.

**F5 — 검증의 오독: in-sample/gross/fill-assumption leakage.**
Flow Traders 검증 모드 교훈("백테스트가 시장충격·체결우선순위·adverse selection을 낙관 가정 = fill-assumption leakage"), Man(model-spread 수익률 명시 경고: "거래비용 미반영·sector-neutral·decay 고려"). 비용·부분체결·세금을 보수적으로 안 넣으면 같은 종류의 낙관 누수.

**F6 — post-publication alpha decay.**
**Alpha Architect: 모멘텀/밸류가 책 2권으로 100% 공개 → 알파 마모 가능성** (McLean & Pontiff류 "발표 후 알파 26~58% 감소"와 정합). 공개·잘 알려진 단일 factor 복제만으로는 부족.

---

## (5) 프론티어(B) 시스템의 핵심 BOTTLENECK

프론티어 MM(XTX, Flow Traders, Jane Street)의 진짜 병목은 통념(latency)이 아니다.

**근본 병목 = "더 나은 예측(price forecast)을 산업 규모로 학습·재배포하는 능력"이며, 이를 떠받치는 3개 하위 병목:**

**B1 — 학습 컴퓨트/데이터 인프라 (the real moat).**
XTX가 가장 노골적: **~25,000 GPU + ~100,000 CPU 코어 + TernFS(650PB+) + €1B 핀란드 데이터센터("compute 수요가 leasing 옵션을 초과")**. 병목은 거래 속도가 아니라 "더 큰 immutable 데이터셋 위에서 더 자주 재학습"하는 능력. 이것이 솔로가 **절대 복제 불가**한 부분 — 우리가 버려야 할 것 1순위. *우리가 차용하는 건 25k GPU가 아니라 "학습/실행 분리 패턴"뿐.*

**B2 — adverse selection / toxicity (정보 비대칭).**
Flow Traders·Jane Street의 예측문제 핵심 = "방향 맞히기"가 아니라 **"누가 내 호가를 칠 때 그게 정보있는(toxic) 주문인가"**. MM의 진짜 적은 변동성이 아니라 정보우위 상대방. — 우리에겐 직접 병목은 아니나(우리는 항상 taker), *그들의 마진이 곧 우리 비용*이라는 함의(체결비용 모델).

**B3 — train-serve 정합성 + 재현성 (reproducibility).**
Jane Street가 OCaml 전사·research=production 코드 공유에 집착하는 이유 = **implementation gap("백테스트는 좋았는데 라이브는 다르더라")이 MM 규모에서 곧 손실**. XTX의 immutable TernFS도 같은 목적(같은 입력→같은 결과). 산업 규모에서 50,000+ 상품 × μs 예측을 *안전하게* 운용하려면 비재현 결정 자체를 구조에서 배제해야 함.

**병목의 비대칭적 교훈 (우리에게):**
프론티어의 병목(compute·latency·adverse-selection·산업규모 재현성)은 **₩10M 솔로엔 전부 비이식 = STRUCTURAL reference only**. 우리를 죽이는 병목은 그들과 정반대다 — **Jane Street 자신이 명시: "₩10M에서 우리를 죽이는 건 latency가 아니라 overfit·leakage·survivorship다."** 즉 프론티어 병목 분석의 진짜 가치는 "복제 대상"이 아니라 "우리 병목이 무엇이 아닌지"를 확정해주는 데 있다. 우리가 자원을 쏟을 곳 = B3(재현성·train-serve 정합)와 검증규율(P6/F4/F5)이지, B1(compute)·latency가 아니다.

---

**한 줄 종합:** 9개를 관통하는 이식가능 청사진 = **(다수 약신호 cross-sectional 랭킹) → (net-of-cost optimizer) → (risk-engine이 signal 위에서 hard-veto) → (무재량 자동집행) → (배포 전 robustness 게이트)**, 그 위에 LLM은 *결정자가 아닌 review/critic 층*. 규모가 바꾸는 건 알파 원천(데이터 vs 구조)과 증거 종류뿐이고 골격은 불변. 가장 큰 실패원인은 집중×레버리지·거버넌스 부재·레짐 의존·overfit이며, 프론티어 병목(compute/latency)은 우리 병목이 아니다 — 우리 병목은 overfit·leakage·검증이다.

---

## 7. — 현대 모델링/AI/LLM이 실제로 어디에 앉는가 (Where modern modeling actually sits)

## 7.1 DL / TSFM / financial-FM의 실제 역할 — 과대광고와 증거의 간극

9개 타깃을 가로질러 보면, **딥러닝·시계열 파운데이션모델(TSFM)·금융 파운데이션모델(financial-FM)이 "최종 알파 결정자"로 검증된 사례는 0건**이다. 증거가 말하는 실제 위치는 셋으로 수렴한다.

**(a) 학습은 무겁게, 추론·결정은 분리 (XTX 아키타입).** XTX Markets가 가장 선명한 표본이다. ~25,000 GPU + ~100,000 CPU 코어 + 자체 분산파일시스템(TernFS, 650PB+)로 가격 예측모델을 산업 규모로 *학습*하지만(L1 오프라인 느린 루프), 그 산출물인 "학습된 예측 시그널"은 별개의 저지연 *실행* 레이어(L3)가 받아쓴다. 결정적 교훈: **GPU/DL은 "예측 생성 공장"이지 "주문 결정자"가 아니다.** 50,000+ 상품을 단일 중앙 예측 두뇌(cross-asset)가 커버하는 점은 foundation-model 발상에 근접하나, XTX조차 공식적으로 "FM"이라 명명하지 않으며 실제 알파의 수학적 형태는 비공개다(secret-structure, group B 정상).

**(b) DL은 "대체"가 아니라 "증강" — economic-prior guardrail 하에서만 (AQR 아키타입).** AQR의 공개 철학('Can Machines Learn Finance?')은 명시적이다: 금융 데이터는 signal-to-noise가 극도로 낮아 순수 data-mining은 반드시 과최적화로 망한다 → ML은 economic theory를 guardrail로 두고 traditional factor를 **augment**할 때만 채택. 'Virtue of Complexity' 연구가 과파라미터+ridge의 OOS 개선 가능성을 보였음에도, 운용 철학은 여전히 해석가능 팩터 + 제약된 ML을 선호하며 거대 사전학습 시계열·파운데이션 모델을 주력으로 공개하지 않는다.

**(c) black-box를 쓰되 glass-box로 견제 (Man Numeric 아키타입).** Man Numeric은 black-box(통계학습/ML)와 glass-box(인간정의 forward-looking factor)를 **의도적으로 병치**한다. 순수 ML의 비해석성·과적 위험을 인간 경제논리 팩터로 구조적으로 견제하는 설계다. ML 시스템도 라이브(2014) 전 ~5년 선행연구·검증이라는 *시간적 게이트*를 통과시켰다.

**반례로서의 증거 — Marsten Parker / Alpha Architect / Andrea Unger (group C).** 외부검증된 실거래/대회/상장ETF 기록을 가진 세 개인·소형 사례는 **DL/TSFM을 아예 쓰지 않는다.** Parker는 저차원 price/volume 룰, Alpha Architect는 rank-transform + 단순 통계, Unger는 few-parameter mechanical 시스템이다. 가장 강하게 *검증된* 소규모 수익이 가장 단순한 모델에서 나왔다는 사실은 결정적이다: **"복잡한 모델 ≠ 검증된 수익."** 솔로/소팀에게 모델 화려함은 alpha-to-risk 비율의 본질이 아니다.

> **종합:** DL/TSFM/financial-FM의 방어 가능한 역할 = **예측 시그널 생성(증강) + 학습/실행 분리 구조** 안에서만. 결코 "한 모델이 주문을 결정"하지 않는다. 우리(₩10M·솔로)에게 DL은 보류 가능 옵션이며, 코어는 cross-sectional 랭킹 + economic-prior 팩터다.

## 7.2 LLM의 방어 가능한(defensible) 역할

증거가 지지하는 LLM의 정당한 위치는 정확히 셋이며, "최종 매수/매도/사이즈 결정자"는 그중에 없다.

**(1) Alpha contributor — "약한 신호(weak signal) 하나" (Man AHL 철학 정합).** Man AHL의 공개 코어 철학은 "다수의 약한 정보원을 결합해 개별 소스보다 강한 signalling power"다(Galaxy Zoo 분류기를 broker-recommendation 신호추출에 이식한 사례). LLM의 news/filings/earnings-call/event 해석은 정확히 *이 "추가 약신호 1개"* 역할에 매핑된다. AHL/Numeric에서 **어떤 단일 신호도 optimizer/risk를 우회하지 못한다** — 이것이 "LLM은 기여자이지 결정자가 아니다"의 외부 근거다.

**(2) Adversarial critic — leakage/overfit/regime/tail/logic 사전 비평 (AQR·Jane Street·Unger의 검증 게이트를 자동화).** 세 가지 검증 규율이 LLM critic의 직접 원형이다:
- AQR: economic-prior 통과 여부 + 글로벌/다기간 OOS + net-of-cost 평가 + "regime underperformance인가 진짜 고장인가" 메타판정.
- Jane Street: types-as-veto + 테스트 + 코드리뷰가 **배포 전(pre-deploy)** 잘못된 코드를 거부. research=production 코드 공유로 implementation gap(백테스트와 라이브의 괴리)을 구조적으로 차단.
- Unger: walk-forward + OOS + parameter-space stability를 "배포 전 강제 게이트"로. 이는 deflated-Sharpe/multiple-testing 정신과 동형.

LLM의 가장 본질적 기여는 *알파 추가*보다 **이 "사람이 하던 적대적 검증"을 자동화/증강**하는 것이다.

**(3) Research-automation layer — 가설 생성·전략 연구 자동화 (Parker의 RealTest, AQR의 리서치 파이프라인 자리).** Parker가 RealTest로 신규 전략을 robustness 검증한 위치, AQR의 리서치 조직이 신호를 정제·검증하는 위치에 LLM council이 대응한다.

## 7.3 LLM-as-final-decider가 위험한 이유 (증거 기반)

**증거 1 — 단일 신호의 우회 금지가 보편 원칙이다.** Marshall Wace TOPS, Man AHL/Numeric, AQR, Jane Street, Flow Traders, XTX 전부에서 어떤 신호·모델·기여자도 risk-engine/optimizer 위에 군림하지 못한다. TOPS는 5,000 기여자의 idea조차 factor-neutral·분산·risk-budget 제약의 옵티마이저를 통과해야만 포지션이 된다. LLM을 최종 결정자로 두는 것은 **이 검증된 보편 구조를 깨는 것**이다.

**증거 2 — 재현가능성(reproducibility) 위반.** Jane Street는 research=production 동일 언어/라이브러리로 "같은 입력→같은 결과"를 *구조적으로 강제*한다. LLM의 환각 기반·비결정적 출력을 최종 주문에 직결하면 비재현 결정이 되어 이 규율과 정면충돌한다(우리 north star인 검증가능성 자체가 무너진다).

**증거 3 — multiple-testing/persistence 함정.** Marshall Wace 사례에서 5,000 기여자 중 일부는 순전히 운으로 상위에 오를 수 있어, skill의 *persistence*를 별도 검증해야 진짜다. LLM이 매 주문을 결정하면 "운 좋은 환각"을 persistence 게이트 없이 즉시 집행하게 된다.

**증거 4 — 검증된 수익은 단순·결정론 시스템에서 나왔다.** group C 세 사례 모두 결정론적 룰엔진이 결정자였고, AI/LLM은 (있었다면) 검토층이었을 위치다.

## 7.4 그래서 council은 어디에 앉는가 — 세 역할의 배치

| 역할 | 위치 | 권한 | 증거 원형 |
|---|---|---|---|
| **Alpha contributor** | Alpha 레이어 *내부*의 weak-signal 1개 | 점수/피처 제공만. optimizer가 가중 | Man AHL weak-signal-ensemble |
| **Adversarial critic** | 배포 전 + 상시 review 레이어 | leakage/overfit/regime/tail/logic 플래그. **통과/거부는 사전정의 규칙 기반** | AQR 검증규율, Jane Street pre-deploy veto, Unger robustness gate |
| **Governance/veto** | optimizer/risk-engine **위의 review 레이어** | **hard-veto는 사전정의 risk 조건에서만**. 최종 사이즈·주문 결정 금지 | Flow Traders/Man의 "risk-engine이 trading-engine 위에" 토폴로지 |

핵심: council은 **risk-engine "위"가 아니라 그것을 "보강하는 검토층"**이며, alpha-contributor로서는 risk-engine "아래(입력단)"에 있다. 이 이중 위치가 브리프의 요구("optimizer/risk 위 review layer지만 final decider 아님")를 정확히 구현한다.

---

## 8. — 정본 레이어드 운영 모델 (The Canonical Layered Operating Model)

9개 타깃의 공통 골격을 단일 파이프라인으로 정규화한 것이다. 모든 대형/프론티어 타깃이 이 순서의 부분집합을 구현하며(이름·경계는 달라도 책임분리는 동형), 우리(₩10M·솔로+AI)는 각 층을 대폭 단순화해 차용한다.

```
Data → Research → Alpha → Portfolio Optimizer → Risk Engine
     → LLM Council Review → Execution → Monitoring/Kill-switch → Human Governance
```

순서의 핵심 불변식 두 개:
- **신호 ≠ 주문**: 어떤 알파도 Optimizer→Risk Engine을 거치기 전엔 포지션이 되지 못한다 (AQR·Man·TOPS·Jane Street 공통).
- **Risk Engine이 trading/optimizer 위에 군림하고, LLM Council은 그 Risk Engine을 보강하는 review로 그 위에 얹히되 최종 결정권은 없다** (Flow Traders/Man 토폴로지 + 브리프 요구).

---

### Layer 1 — DATA
**무엇을 하는가:** 가격·거래량·펀더멘털·공시·뉴스를 immutable·버전드·재현가능 데이터셋으로 적재. **train-serve 동일 피처 빌더**로 학습·백테스트·실거래가 같은 파이프라인을 통과(leakage·train-serve skew 차단). KR tax 0.20%+슬리피지를 비용 피처로 사전 반영. point-in-time/survivorship 보정은 비협상 항목.
**자동화:** 완전 자동(배치 ETL).
**진짜 엣지가 사는 곳:** 규모(XTX 650PB)가 아니라 **immutable·재현가능 + train-serve 일관성**. group C 검증 사례의 생존 조건. *Edge 등급: 솔로에게 HIGH (방어선).*

### Layer 2 — RESEARCH
**무엇을 하는가:** economic-prior로 정당화되는 가설 생성 → 신호 정제. **deploy 전 시간적·조직적 검증 게이트**(AHL ML ~5년, Jane Street 코드리뷰). 여기서 LLM = research-automation + 가설 생성 보조.
**자동화:** 반자동. 신규 전략 *배포 승인*은 인간 게이트.
**진짜 엣지:** "데이터마이닝으로 찾은 신호는 버린다"는 economic-prior 규율 (AQR). *Edge: HIGH.*

### Layer 3 — ALPHA
**무엇을 하는가:** cross-sectional 상대수익 *랭킹* 예측(절대수익 아님). **단일 천재신호 금지, 저상관 약신호 앙상블**(value↔momentum 음상관 활용). 여기에 LLM이 news/event 약신호 1개로 기여. 예측은 점추정이 아니라 방향·크기·확신도(분포).
**자동화:** 완전 자동(모델 추론).
**진짜 엣지:** breadth × diversification (Fundamental Law, AQR) + weak-signal ensemble (AHL) + 생성원을 데이터로 보고 검증된 정확도로 가중 (TOPS contributor-scoring). *Edge: HIGH (그러나 단독으론 약함이 설계 전제).*

### Layer 4 — PORTFOLIO OPTIMIZER
**무엇을 하는가:** alpha forecast + risk model + **cost/turnover를 목적함수에 내재화**(cost-aware)해 목표비중 산출. "신호=주문"을 구조적으로 차단. KR 0.20%세+슬리피지를 비용항에 넣어 **net-of-cost로 종목 선택**. 솔로 규모에선 1/N 동일가중 baseline이 robust (Alpha Architect·De Miguel).
**자동화:** 완전 자동.
**진짜 엣지:** 비용 내재화 — "gross 알파 강한 모델"이 아니라 "**net-of-cost 알파 강한 모델**"이 이긴다 (AQR 'Implementable Efficient Frontier'). 우리 north star 직결. *Edge: HIGH.*

### Layer 5 — RISK ENGINE
**무엇을 하는가:** optimizer 출력에 **hard 제약**(종목/섹터/집중도/변동성/MDD 한도). volatility targeting/scaling으로 저변동성기 노출↑·고변동성기 노출↓(crisis left-tail 완화). 포지션을 "의도된 알파 노출 + 의도치 않은 베타/섹터/팩터 노출"로 분해해 후자를 통제. 신호가 아무리 강해도 한도가 마지막 게이트.
**자동화:** 완전 자동 enforce. 한도 *변경*은 인간 승인.
**진짜 엣지:** **risk-engine이 시스템 최상위 결정권**이라는 토폴로지 자체 (Flow Traders/Man 독립 risk team, Jane Street risk>signal). MDD 25% 선호를 구조적으로 달성하는 층. *Edge: HIGH (솔로 생존 핵심).*
> **[2026-06-01 council 편입]** 사용자 사견2(집중)는 여기 **watchlist concentration budget**(종목/이슈어/섹터 비중 상한 + 리밸런스 트리거)로 앉는다 — ALPHA 아님. 현재 **무포지션 현금**이라 *진입 가드*이며, 미국 메가캡 노출이 생기면 active rebalance로 승격. 사견1(KRX 수급=`investor-type flow anomaly`)은 Layer 3 알파가 아니라 **RESEARCH backlog**(Phase-1 검증보류). 상세=부록 A(g).

### Layer 6 — LLM COUNCIL REVIEW
**무엇을 하는가:** optimizer/risk-engine **위에 앉는 검토층**. (a) 배포 전 adversarial critic(leakage/overfit/regime/tail/logic 사전정의 체크리스트), (b) 상시 governance review, (c) **hard-veto는 사전정의 risk 조건에서만**. **최종 buy/sell/size 결정 금지. LLM이 risk-engine 위에 군림 금지.** 통과/거부 판정은 환각이 아니라 사전정의 규칙 기반(재현가능).
**자동화:** 비평·플래그는 자동, 사전정의 조건 외 거부는 인간 escalation.
**진짜 엣지:** "사람이 하던 검증 게이트"(AQR/Jane Street/Unger)를 1인+AI로 압축. *Edge: MEDIUM — 검증 규율을 자동화하는 한에서만. 결정자로 격상하면 negative edge(7.3).*

### Layer 7 — EXECUTION
**무엇을 하는가:** 승인 포지션을 cost-aware로 집행(분할주문·지정가·시장가 회피). 저빈도(swing/mid-long)라 초저지연 불필요 — cloud-GPU+PC로 충분. **정상 주문은 인간 승인 없이 자동집행.**
**자동화:** 완전 자동(브리프 normal-orders-auto와 1:1).
**진짜 엣지:** 솔로에겐 HFT 인프라가 아니라 **회전율 억제 + 슬리피지/세금 실측 환류**. group B의 μs 실행은 reference-only. *Edge: 솔로에게 LOW(인프라) / MEDIUM(비용통제).*

### Layer 8 — MONITORING / KILL-SWITCH
**무엇을 하는가:** 체결·P&L·슬리피지·factor 성과·drawdown 상시 감시 + **P&L attribution**(알파/베타/섹터/비용 분해). **사전정의 하드 트리거 kill-switch**: Parker의 inception −10% / peak −15%가 직접 차용 가능한 구체 수치. equity-curve MA 스위치로 약화 전략 자동 off (mode-switch 원형). "drawdown이 백테스트 최악 DD 초과"가 가장 강한 고장 신호.
**자동화:** 사전정의 트리거는 자동 발동, 재진입은 인간.
**진짜 엣지:** **"firm이 돈 벌었다 ≠ 내 전략이 OOS after-cost로 돈 번다"**의 분해 검증 (Flow Traders). retire-when-broken vs out-of-regime 구분 (Parker). *Edge: HIGH (솔로 생존).*

### Layer 9 — HUMAN GOVERNANCE
**무엇을 하는가:** 인간은 **오직** 예외·mode-switch(사전조건 미충족 시)·전략 배포 승인·리스크 한도 승인·kill-switch에만 개입. 정상 운용은 무인. AQR/Man/Jane Street 모두 인간은 "주문이 아니라 시스템을 운용"한다. mode-switch는 사전조건 충족 시 자동(vol-scaling, equity-curve MA), 경계 밖만 인간 승인.
**자동화:** 메타 결정만 인간, 일상은 자동.
**진짜 엣지:** regime/research-integrity 메타판정 — "팩터는 수 년 죽을 수 있다, drawdown≠즉시 kill" (AQR quant winter). *Edge: HIGH (장기 생존).*

---

## 8.x 브리프 LLM-council 요구와의 정합 확인

- ✅ **review layer above optimizer/risk** → Layer 6이 Layer 4·5 위에 검토층으로 배치 (단, alpha-contributor로서는 Layer 3 입력단에도 존재 = 이중 위치).
- ✅ **hard-veto only on pre-defined conditions** → Layer 6의 veto는 사전정의 risk 조건 한정, 그 외는 인간 escalation.
- ✅ **normal orders auto** → Layer 7 정상주문 무승인 자동집행.
- ✅ **LLM not final decider / not above risk engine** → 최종 사이즈·주문은 Layer 4·5가 결정, Layer 6은 플래그·사전정의 거부만.
- ✅ **mode-switch auto if pre-defined else human** → Layer 8(equity-curve/vol-scaling 자동) + Layer 9(경계 밖 인간).

**진짜 엣지가 사는 곳(요약):** 솔로 시스템에서 alpha(Layer 3)는 검증된 약신호 앙상블이지만 단독 엣지는 얇다. **지속 가능한 엣지는 Layer 1(데이터 무결성) + Layer 4(cost-aware net-of-cost) + Layer 5(risk-engine 최상위) + Layer 8(분해 검증·kill-switch)에 산다** — 즉 "더 똑똑한 모델"이 아니라 "더 규율 있는 비용·리스크·검증 구조"가 north star(KOSPI100 after-cost 상회)를 만든다.

---

## 9. Scorecard (10차원, 0-10)

점수는 공개자료 기반 **벤치마킹 가치** 평가지 투자성과 예측이 아니다.

| 대상 | 수익검증 | 수익잠재 | 자동화 | 프론티어 | 자료신뢰 | 개인응용 | 데이터우위 | 실행용이 | 리스크통제 | LLM결합 | 총점 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AQR Capital Management | 7 | 7 | 8 | 6 | 9 | 7 | 5 | 7 | 8 | 8 | 72 |
| Man (AHL+Numeric) | 9 | 7 | 9 | 7 | 9 | 6 | 5 | 6 | 9 | 8 | 75 |
| Marshall Wace (TOPS) | 5 | 7 | 8 | 7 | 7 | 8 | 5 | 7 | 8 | 10 | 72 |
| XTX Markets | 4 | 6 | 10 | 10 | 8 | 4 | 3 | 4 | 7 | 7 | 63 |
| Flow Traders | 5 | 5 | 10 | 7 | 9 | 3 | 2 | 3 | 8 | 3 | 55 |
| Jane Street | 4 | 6 | 10 | 9 | 7 | 4 | 3 | 4 | 8 | 6 | 61 |
| Marsten Parker | 7 | 7 | 8 | 4 | 6 | 10 | 4 | 9 | 8 | 7 | 70 |
| Wesley Gray / Alpha Architect | 9 | 4 | 8 | 4 | 9 | 9 | 4 | 9 | 4 | 6 | 66 |
| Andrea Unger | 5 | 5 | 8 | 4 | 5 | 9 | 3 | 8 | 7 | 6 | 60 |

> critic 주의: 'profitVerifiability'는 **firm-income** 기준이다. strategy-return 기준이면 전 행이 LOW. 마켓메이커(XTX/Flow/Jane)는 firm-income은 높아도 전략수익 검증은 0.


---

## 10. Phase 0 결론

## 10.1 채택할 운영 모델 (the adoptable operating model for profit-maximization)

9개 타깃의 교집합을 ₩10M·솔로+AI로 축소한 **6-레이어 운영 모델**을 Phase 1의 설계 기준선으로 확정한다.

```
L0 DATA      : KOSPI100 immutable·point-in-time OHLCV + 분기 재무 + 공시/뉴스(텍스트)
               → 학습·백테스트·실거래가 동일 피처 빌더 통과 (train-serve skew 차단)
L1 SIGNAL    : 다수 무상관 룰/factor 시스템 (cross-sectional momentum + value + 
               quality + mean-reversion + breakout) → {방향·확신도·기간·논거} 동일 스키마로 persist
               + 생성원(룰/팩터/LLM-페르소나)별 사후 hit-rate append-only 적재 [Marshall Wace TOPS]
L2 OPTIMIZER : 신호 → 비중. 동일가중(1/N) baseline + 비용항(0.20%+슬리피지) 목적함수 내재화 [AQR]
               신호 강도 ≠ 비중. turnover 패널티 강제.
L3 RISK      : 최상위 게이트. per-system cap + portfolio cap [Unger] + system stop(−10%/−15%) +
               equity-curve 300d MA on/off [Parker] + 팩터·섹터·집중도 한도. optimizer 출력을 hard-clip.
L4 EXEC      : 정상주문 무승인 자동. 분할·지정가로 슬리피지 최소. 저빈도(분기/주 리밸런스).
L5 GOVERNANCE: LLM-council = risk-engine '아래/옆' review 레이어 (위 아님).
               역할 = (a) alpha-contributor(뉴스·공시·실적콜 해석 → 약신호 1개),
                      (b) adversarial-critic(leakage/overfit/regime/tail/logic 사전점검),
                      (c) hard-veto only on pre-defined risk conditions.
               인간 = 예외·mode-switch(사전조건 밖)·전략배포·리스크한도·킬스위치만.
```

이 모델의 정당화: L0(XTX immutable+train-serve), L1(Man weak-signal+TOPS contributor-scoring), L2(AQR cost-aware), L3(Parker/Unger/Flow risk-on-top), L4(전 타깃 high-automation), L5(전 타깃 human-only-at-meta + Jane Street types-as-veto). **9곳의 검증된 교집합이지 우리 추측이 아니다.**

## 10.2 개인이 절대 복제하면 안 되는 것 (what individuals MUST NOT copy)

1. **마켓메이킹 알파 자체** — 스프레드 캡처·μs latency·inventory·AP 자격은 ₩10M에 비현실. P&L 발생 원리가 우리 방향성 swing과 다른 게임. (XTX/Jane Street/Flow Traders는 **구조 참조 only**.)
2. **변동성 의존 P&L** — Flow Traders 4배 YoY 스윙, Unger 대회 수익률. 우리 안정성·MDD 선호와 상충. 솔로가 모사하면 안 되는 P&L 프로파일.
3. **단일 factor 맹목 복제** — Alpha Architect가 증명: 공개 factor도 지수 하회. **복제는 baseline일 뿐, 알파가 아니다.**
4. **고레버리지·concentrated 베팅** — Parker −45% DD가 직접 교훈. ₩10M = "죽지 않고 학습하는 자본."
5. **LLM에게 최종 주문권** — 9곳 전부 단일 신호가 risk-engine을 우회 못 함. **LLM 환각 기반 주문·비재현 결정·LLM을 risk-engine 위에 올리기 = 명시적 금지.**
6. **거대 모델 군비경쟁** — XTX/JS의 검증된 edge도 거대 DL이 아니라 데이터 정제+리스크엔진. 우리 'DL/GPU 절제'와 정합. DL/TSFM은 보류, 뉴스 임베딩에만 선택적.

## 10.3 현실적으로 벤치마크 가능한 것 (what we realistically CAN benchmark)

**1순위 (인프라 무관, 즉시 차용):**
- **거버넌스 토폴로지** — risk-engine 최상위, LLM은 review 레이어. 전 타깃 검증.
- **검증 게이트** — walk-forward + purged/embargoed OOS + deflated Sharpe + multiple-testing 보정 + net-of-cost. backtest 우수≠배포.
- **system stop + equity-curve 스위치** — Parker −10%/−15%, 300d MA on/off를 우리 kill-switch·mode-switch 초기값으로 (KR 변동성에 재캘리브레이션).

**2순위 (구조 차용 + 단순화):**
- **cross-sectional rank factor** — KOSPI100에 value+momentum+quality를 rank로. 15~25종목 동일가중(50종목은 ₩10M에 단주 문제).
- **생성원을 데이터로** — 스캐너/팩터/LLM-페르소나를 'contributor'로 취급, 사후 hit-rate로 가중·도태 [TOPS].
- **estimate→act 분리** — 기대수익 추정 모델 ↔ 사이징/주문 로직 모듈 분리 [Flow Traders].

**3순위 (우리만의 증분):**
- **LLM-council** — 9곳 누구도 안 한 news/filings/event 해석을 약신호로 추가 + adversarial critic으로 검증 자동화. 단 risk-engine 아래.

## 10.4 Phase 1에서 파고들 가장 날카로운 질문 (sharpest questions)

**Q1 (north star 직결, 최우선).** KOSPI100에서 value+momentum+quality cross-sectional rank가 **after-cost(0.20%+슬리피지) walk-forward OOS로 KOSPI100(after-cost)+현금을 실제로 이기는가?** Alpha Architect의 LAG 교훈상 단일 factor는 못 이길 가능성이 높다 → **멀티 factor 결합 + KR 시장 특성(개인 비중↑, 모멘텀 강세) 재검증**이 필수. 못 이기면 전체 전제 재검토.

**Q2 (검증 규율).** 소수 생성원으로 multiple-testing을 어떻게 통제하는가? deflated Sharpe + 사전등록(pre-registration) + parameter-plateau를 백테스트 게이트로 코드화. 표본 부족 시 "insufficient sample" 플래그 강제.

**Q3 (LLM 위치 구체화).** LLM-council의 hard-veto 조건을 **사전정의 risk 규칙**으로 어떻게 못박는가? (환각·비재현 차단.) LLM 신호도 contributor-scoring 게이트를 통과해야 가중되게.

**Q4 (mode-switch / kill-switch — 9곳에서 직접 상속 못 한 GAP).** aggressive/stable/conservative 자동전환의 사전조건 임계값은? vol-targeting [Man] + equity-curve MA [Parker]를 KOSPI100 변동성에 맞춰 어떻게 캘리브레이션하나? 명시적 kill-switch 트리거 정의.

**Q5 (공매도 제약).** KR 개인 공매도 제약 하에서 market-neutral을 인버스ETF/현금으로 근사할 때 비용·tracking error는? long-bias 한계 내 limited L-S 범위.

**Q6 (생존 우선).** ₩10M에서 거래수가 통계 유의성에 충분한가? Parker 연 1,000 trades 대비 우리 유니버스·저빈도에서 거래수 부족 → 검증 신뢰도 하락분을 더 보수적 robustness 기준으로 상쇄.

## 10.5 Phase-0 최종 판정
**GO — 단, "복제"가 아니라 "구조+규율 이식"으로.** 9개 타깃은 우리에게 **검증된 아키텍처 골격(L0~L5) + 검증 규율 + 거버넌스 모델**을 주되, 알파 수치·인프라·레버리지는 주지 않는다. Phase 1의 첫 관문은 **Q1(KOSPI100에서 after-cost로 실제 이기는가)** — 여기서 통과 못 하면 멀티 factor·LLM 증분으로도 north star 미달이므로, **단일 factor baseline의 after-cost OOS 검증을 Phase 1 첫 산출물로 고정**한다.

---

## 부록 A. 적대적 비평 (Critic) — 본문 보정 근거

아래는 워크플로 최종 단계의 적대적 완결성 비평이다. 본문 §2·§4·§7·§8·§9는 이 비평을 반영해 작성됐다. 원문 보존.

# ADVERSARIAL PUNCH-LIST — 9 profiles vs brief's own bar

## (a) PROFIT NOT CREDIBLY VERIFIED AT THE BRIEF'S BAR → name + downgrade

The brief sets DIFFERENT bars per category and explicitly says to "score profit-VERIFIABILITY low" for market-makers and "distinguish verified out-of-sample after cost from marketing/in-sample." Held to that, the report's own confidence ratings are too generous in several places:

- **AQR — DOWNGRADE from "HIGH" to MEDIUM.** The profile's own `publicLimits` admits 2024 returns are "press-reconstructed (Tier2), not audited NAV," the +71% top fund is "전략·자본규모 미상 → cherry-pick 위험," and AUM figures conflict ($120B/$128B). A press-cited single-year +71% from an unnamed sleeve is exactly the cherry-pick the brief warns against. "profit-verifiability 종합 = HIGH (삼중)" overstates it — SEC 13F proves *existence and holdings*, not *returns*. Returns evidence is Tier2 press only. Correct grade: **MEDIUM**, and the +71% number should be quarantined, not headlined in SEC0.3/SEC3.

- **Marshall Wace — already MEDIUM, but SEC0.3 still launders it.** The Eureka "~13-14%" and TOPS "~22.59%" are explicitly press-reconstructed, NOT audited, with AUM varying $60–75B across sources. The profile is honest (profitConfidence MEDIUM) but the cross-case sections quietly treat MW as a co-equal evidence pillar. Keep MEDIUM and stop citing the 22.59%/13-14% as if load-bearing.

- **Jane Street / XTX / Flow Traders — the deeper problem the brief flagged and the report half-buries.** All three are "profit-verified" on **absolute net income**, but the brief's market-maker rule says score profit-VERIFIABILITY *low* relative to our north star. SEC3's S2 says this once ("검증된 것은 absolute net income이지 strategy return이 아니다"), but SEC0.3 then tags XTX/Flow "HIGH" and Jane Street "MEDIUM" in a column literally headed "profit-verify" — collapsing "firm made money (audited)" into "profit verified" in a way a skimming reader will misread. **These are HIGH firm-income-verifiability / ZERO strategy-return-verifiability.** The single column is the flaw; it must be split.

- **Marsten Parker — the MEDIUM→MEDIUM-HIGH upgrade is not earned at the brief's bar.** The brief's group-C bar explicitly lists "broker-verified live / regulatory-registered / audited track / externally-verified long live record." Parker is **none of these**. He is *author-reconstructed* (Schwager read statements but published neither statements nor an audit) plus self-reported interview numbers that match across outlets *because they trace to the same book*. Multi-outlet verbatim agreement is corroboration of *consistent retelling*, not independent verification — the profile's own upgrade rationale commits a citation-laundering error (elearnmarkets/bettersystemtrader are quoting Schwager, not the broker). Under the brief, "externally-verified long public live record" requires the record be *externally re-checkable*; it is not. **Revert to MEDIUM.** Note this is the single strongest group-C profit case anyway, which makes the over-claim more dangerous, not less.

- **Andrea Unger — correctly MEDIUM, and the report handles him best.** WCC is genuinely third-party broker-verified (the one true external verification in group C), but the small-account/leverage/survivorship/multiple-entry caveats are properly applied and the numbers are explicitly quarantined from north-star. No change. This is the template for how the others should have been written.

**Net:** only **Man Group** clears the brief's *firm-level* bar cleanly (LSE statutory audited), and **Unger** clears the *group-C external-verification* bar cleanly. Every other "HIGH" is either firm-income-not-strategy-return (XTX/Flow/JS) or press/author-reconstructed (AQR/MW/Parker). That is a materially different picture than SEC0.3's confidence column paints.

## (b) INFERENCE DRESSED AS FACT

- **"risk > signal" as a universal law (P1/P2 in SEC6).** This is the report's load-bearing claim and it's *directly quoted* only for Jane Street, Flow Traders, Man, AQR, Marshall Wace. For **XTX, Parker, Unger, Alpha Architect** it is *inferred from structure*, not stated. Worse, **Alpha Architect contradicts it**: it has *no risk engine at all* (the profile says so — no optimizer, no kill-switch, fully-invested through −51%). So "9/9 전부가 risk-engine을 signal 위에 둔다" is **false as stated** — it's ~5/9 explicit, 3/9 inferred, and 1/9 (Alpha Architect) is a counterexample where the risk layer is *absent*. The synthesis should say "5/9 explicit, and Alpha Architect proves the cost of its absence," not claim 9/9.

- **XTX "single central brain / cross-asset foundation-model" framing.** The profile honestly tags the FM language as INFERENCE ("공식적으로 FM이라 명명하진 않음"), but SEC6-S1 and SEC0 elevate "예측 = 단일 중앙 두뇌" to a confirmed structural fact and make it the archetype of S1. The "50,000 instruments share one brain" is XTX *marketing self-description*, not independently verified architecture. Flag as company-claim, not Tier1.

- **The 5-layer / 6-layer / L0–L5 architectures for Parker, Unger, AQR, XTX.** Each profile *admits* the layer decomposition is "우리 시스템 언어로 재구성" (Unger explicitly: "그가 5층이라 명시한 적 없음"). But SEC6's P1 ("9개 전부가 이 위계를 갖는다") presents these reconstructions as *observed* invariants. They are partly *imposed* by the analyst. This is the subtlest fact/inference slip in the whole report: the "structural invariant" may be in the analyst's framing, not the firms.

- **Parker's "300-day MA equity-curve switch" and "−10%/−15% system stop" as adopt-ready numbers.** These are FACT *that Parker uses them*, but SEC8 Layer 8 and SEC10.3 present them as "직접 차용 가능한 구체 수치" — that's an inference (that US-futures-tuned thresholds transfer to KOSPI100 swing). The profile itself flags re-calibration; the synthesis drops the caveat when it gets concrete.

## (c) OPERATING-MODEL LAYERS LEFT VAGUE

- **Layer 6 (LLM Council) is the least operationalized layer in SEC8 and it's the one thing that's actually ours.** "hard-veto는 사전정의 risk 조건에서만" — but *which* conditions? The whole report never names a single concrete pre-defined veto condition. Compare Layer 8, which gives actual numbers (−10%/−15%). Layer 6 is hand-waved precisely where the brief most needs rigor. (More on this in (f).)

- **Layer 4 Optimizer ↔ Layer 5 Risk Engine boundary is blurred for the ₩10M case.** SEC8 says "1/N 동일가중 baseline" in L4, then L5 does "hard 제약 + vol-targeting." But with 15–25 equal-weight names and no leverage, what does the "optimizer" actually optimize? The report admits elsewhere (Alpha Architect lesson) that "optimizer는 추정오차만 키운다." So for our scale, **L4 collapses into L5** (it's just rank-cut → equal-weight → risk-clip). The report keeps them as two layers to match the big funds, but for ₩10M that's structure-cargo-culting. State plainly: at our scale there is no real optimizer, only a ranker + risk gate.

- **Mode-switch (the AUTOMATION/GOVERNANCE target's hardest part) is the acknowledged GAP and stays a GAP.** SEC6/SEC8/SEC10 all admit mode-switch and kill-switch are *not inherited* from any of the 9 except as Parker's equity-curve MA and Man's vol-targeting. So the single most novel governance requirement in the brief (auto aggressive/stable/conservative) has the *thinnest* evidentiary base and is never given concrete trigger thresholds. That's honestly flagged but never resolved — fine for Phase-0, but SEC10.4 Q4 should be promoted to a *first-class deliverable*, not question #4.

- **Execution layer for KR specifics is vague.** "분할주문·지정가" — but KR market microstructure (price-limit ±30%, tick sizes, single-price auctions at open/close, 0.20% tax + ~0.015% fee asymmetry on sell-side) is never engaged. The report treats execution as solved-because-low-frequency. For a ₩10M account, single-stock ₩200k positions hit lot/odd-lot and minimum-tick frictions that the big-fund references say nothing about.

## (d) "lessonsForSmall" THAT ARE WRONG FOR ₩10M KR SWING

- **AQR cost-aware optimizer "internalize KR 0.20% in the objective function."** Right instinct, wrong mechanism at our scale. AQR's optimizer is mean-variance over thousands of names where marginal cost vs marginal alpha is a smooth tradeoff. At 15–25 names you don't "internalize cost in an objective function" — you **set a hard turnover budget and a minimum-holding-period rule**. Dressing this up as "objective-function internalization" imports machinery that estimation-error will dominate. The lesson is correct in spirit but the *form* is a scale-misread.

- **Marshall Wace "contributor-scoring / hit-rate weighting of scanners + LLM personas."** This is the most seductive and most dangerous transplant. MW scores **5,000 contributors across 53 countries** — that breadth is the entire reason hit-rate weighting works (law of large numbers over contributors). With **3–5 internal signal sources** the report itself flags "표본부족 → insufficient-sample." So the honest conclusion is: **MW's mechanism does NOT transfer** — you cannot meaningfully hit-rate-weight 4 sources. The profile says this in `lessonsForSmall` but then SEC10.3 lists "생성원을 데이터로 [TOPS]" as a 2순위 adopt item. It should be demoted to "aspirational, blocked by sample size," not a recommended borrow.

- **Jane Street "research=production same codebase to kill implementation gap."** For JS this means OCaml strong-typing across a firm. For a solo dev the report translates it to "single Python codebase, shared feature/cost functions." That's *good engineering* but it is **not** what closes the backtest-live gap for a ₩10M retail account — the gap for us is **fill realism** (will my limit order at KOSPI100 actually fill at backtest price given my size vs displayed depth, KR auction mechanics, tax). Same-codebase does nothing for that. The real Jane Street lesson (their own profile says it under Flow Traders' "fill-assumption leakage") is *conservative fill modeling*, which got mis-filed under JS as "same codebase." Wrong lever.

- **XTX "learn/serve split: cloud-GPU retrain weekends → PC loads artifact."** This is structure-cargo-culting at ₩10M. For swing/mid-long on KOSPI100 with OHLCV + quarterly fundamentals, **there is likely no model that needs GPU retraining at all** — it's rank computations and rule evaluation that run on a laptop in seconds. Recommending a "cloud-GPU learning loop" because XTX has one is exactly the "scale moat misread as copyable" the question warns about. The defensible XTX lesson is *immutable, versioned, point-in-time data with one feature builder* — the GPU/learn-serve split is **not applicable** and should be cut from "CAN copy."

- **Alpha Architect "50 names equal-weight."** The profile catches the lot-size problem (₩200k/name) and proposes 15–25, good. But it does **not** catch that **equal-weight rebalancing at 15–25 KR names triggers far more taxable turnover than AA's quarterly in-kind ETF** — AA's entire cost advantage is the in-kind creation/redemption that a retail account *cannot* access. So "low turnover like AA" is structurally unavailable to us; we pay 0.20% on every rebalance AA avoids. The lesson "분기 저회전 + ETF in-kind로 비용 최소화" is listed as an AA strength but its *transfer* is impossible — we get the turnover without the in-kind shield. This is a capital/structure moat misread.

## (e) SOURCE TIER / MODALITY UNDER-CHECKED

- **Parker's entire profit case rests on Tier3 podcasts + Tier3 course-adjacent site (mhptrading.com) + one Tier1 publisher page (Harriman House) that only proves the book *exists*, not the numbers.** The "MEDIUM-HIGH" leans on elearnmarkets (Tier3 aggregator) repeating Schwager. No Tier1/Tier2 here verifies *returns*. Under-checked: nobody pulled the actual *Unknown Market Wizards* chapter text, and the brief explicitly excludes "backtests/records without performance verification." This is the most over-rated source stack in the report.

- **XTX's £1.28B is correctly Tier1 (Companies House)** — but the profile *admits* the live-fetch failed (Cloudflare 403 on financemagnates, Bloomberg paywalled, "라이브 WebSearch가 model-fallback 반환"). So even the Tier1 claim is *asserted from prior knowledge + Tier2 mirrors*, not freshly verified this session. Same disclosure appears in Flow Traders and Jane Street ("WebFetch가 빈 결과/model-fallback"). **Across group B, the "live re-verification" claimed in method-notes largely did not happen** — the numbers are from the brief's frozen context, not re-fetched. Honestly disclosed in publicLimits, but it means *zero* of the group-B financials were independently re-checked in this run.

- **Wikipedia/Grokipedia as load-bearing for Marshall Wace AUM ($71B) and XTX qualitative claims.** Tier3 tertiary. The "$71B" headline AUM rides on a Wikipedia infobox. Fine as context, but it's cited in SEC0.3's structure column as if settled.

- **Modality gap: not one regulatory primary doc was read in-session for the items that have them.** SEC 13F (AQR), LSE RNS (Man), Euronext filing (Flow), Companies House (XTX) are all *cited by URL* but the profiles' method-notes admit fetch failures. So every "Tier1" in this report is **Tier1-by-citation, Tier2-by-actual-evidence-handled-this-session**. The grades assume the primary docs say what secondary press says they say.

## (f) IS "LLM-COUNCIL-AS-VETO-LAYER" SUPPORTED, OR THE SAME TRAP IN DISGUISE?

This is the sharpest question and the report flinches. Honest answer: **the evidence supports LLM-as-adversarial-critic and LLM-as-weak-alpha-contributor; it does NOT support LLM-as-veto-layer — and the veto framing smuggles the banned pattern back in.**

1. **What the 9 actually support.** Every "review layer above the engine" in the 9 is a *deterministic, reproducible* layer: AQR's economic-prior checklist, Jane Street's types/tests/code-review, Man's risk committee, Unger's walk-forward gate, MW's contributor-score threshold. **Not one of them is a stochastic natural-language model exercising a veto.** The report maps LLM onto these slots by *analogy of position*, but the slot's defining property in every case is **determinism/reproducibility** — which is exactly the property an LLM lacks. So the structural precedent argues *against* putting an LLM in the veto slot, not for it.

2. **The brief's own red-line.** The brief bans "non-reproducible final decisions" and "LLM ranked above the risk engine." A *hard-veto* is a final decision (it deterministically blocks a trade the risk engine approved). If the veto fires on a *pre-defined rule*, then **the rule is the vetoer, not the LLM** — the LLM is just evaluating a deterministic condition, which a plain function should do (reproducibly). If the veto fires on the *LLM's judgment*, it is a non-reproducible final decision = the banned pattern. **There is no coherent middle.** SEC7.3's own evidence-2 (reproducibility) and evidence-3 (multiple-testing/lucky-hallucination) *prove this*, then SEC7.4 and SEC8-L6 re-introduce "hard-veto on pre-defined conditions" anyway. The report refutes its own veto layer and doesn't notice.

3. **The resolution the report should have reached.** Split the LLM's three roles by reproducibility:
   - **Alpha contributor (weak signal):** legitimate — it's an *input* that the deterministic optimizer/risk engine weighs and can overrule. Supported (Man weak-signal ensemble). Keep.
   - **Adversarial critic (pre-deploy):** legitimate — it *flags* leakage/overfit/regime for a *human* deploy gate; flags are advisory, human decides. Supported (AQR/JS/Unger gates). Keep, but it is *advisory-to-human*, never auto-acting.
   - **Veto/governance layer:** **NOT supported.** Either demote to "advisory escalation" (LLM raises a flag → human or a deterministic rule acts) or delete. The veto must live in **code (a deterministic risk rule)**, and the LLM may at most *propose* such rules offline for human review. An LLM that can block a risk-engine-approved order in production = the hallucination-order trap wearing a governance badge.

4. **Therefore the brief's stated desire is internally inconsistent and Phase-0 should say so.** "review layer SITTING ABOVE optimizer/risk-engine ... hard-veto only on pre-defined risk conditions ... NOT the final decider" — a hard-veto *is* a final decider on the deny side. The only way to honor "not the final decider" + "reproducible" is: **LLM never acts on the order path; it only (a) feeds weak signals into the engine, and (b) feeds flags into the human/offline-rule path.** The report's Layer-6 should be *moved off the live order path entirely* (it's drawn inline between Risk Engine and Execution in SEC8's pipeline — that placement is the trap). Correct topology: LLM hangs *off to the side* feeding Layer 3 (alpha) and Layer 9 (human governance), and is **absent from the L4→L5→L7 critical path**.

**Verdict on (f):** the veto layer is the same trap in disguise. The defensible design is LLM-as-input + LLM-as-advisory-flag, with all actual vetoes implemented as deterministic code rules. SEC7/SEC8/SEC10 should be corrected to remove the LLM from the live order path and rename "Layer 6 veto" to "off-path advisory critic."

---

**Single most important correction:** split SEC0.3's "profit-verify" column into **firm-income-verifiability** vs **strategy-return-verifiability** — under the latter, *all 9 score LOW-to-NONE*, which is the true Phase-0 finding and the strongest guard against importing any of their numbers as targets.

## (g) 사용자 사견 2개 — council 편입 (2026-06-01, Claude×Codex 적대회의 3R→APPROVED)

Phase-0 단계에서 사용자 개인 직관 2개를 서사(narrative)와 분리해 검증가능 후보로 변환. **council 결론: 둘 다 ALPHA 아님.** (회의 전문·plan 기록 = `~/main/council/2026-06-01_v2-tilt-council/`)

- **사견 1 "거인의 등에 올라탄다" → RESEARCH backlog (채택 아님 · 잠정 negative prior).** 명칭 "거인 추종" 폐기 → `investor-type flow anomaly candidate` (KRX 투자자별 순매수는 *집계 라벨*이지 시스템펀드 주문이 아님 — 라벨엔 매수 *이유*(인덱스 리밸·헤지·환·페어)가 없음). 국내 실증(2024 KCI): **중기(1~3M) 외국인 순매수강도 *추종* = 유의한 음의 초과수익, 기관 무의미**; 단 *장기 거래량* 기준 외국인 추종은 최우수 → 시간창 하나로 부호 고정 금지 ⇒ 즉시 채택·즉시 기각 둘 다 과잉판정. **Phase-1 검증**(단일 primary 가설: `외국인 순매수강도 ÷ 시총` · 20거래일 · 추종/역추종 **양방향** · 모멘텀 직교화 · **t+1**(look-ahead 차단) · 비용차감 walk-forward OOS; 다중후보는 deflated Sharpe 보정) 통과 시에만 ALPHA 승격, 못 넘으면 기각 기록. 메커니즘 실패: 공개·지연 수급 추종은 (a)움직임 끝난 뒤 비싸게 매수 (b)한국 최혼잡 리테일 신호=엣지 소멸 (c)라벨이라 이유 불명 (d)reflexivity 역전 피격.
- **사견 2 "양극화→집중→상위주 비중확대" → RISK (ALPHA 아님).** 사회학(양극화) 서사 폐기. 집중은 *초과수익 엣지*가 아니라 **미분산·상관·혼잡·평균회귀 위험**. 이미 cap-weight 보유 시 추가 비중확대 = 새 알파가 아니라 집중 노출 *증폭* (S&P500 상위10 ~40%, 2025말~2026.3 [RBC·JPM]; EW가 2022말~2025.8 CW보다 35%p 언더퍼폼 [S&P] → "집중 고점=즉시 EW 승리" 거짓). 사용자 현재 **무포지션 현금** → 사견2 = **Layer 5 watchlist concentration budget**(진입 가드). 미국 메가캡 노출 생기면 active rebalance로 승격. 원래 액션("비중확대")은 *없는 알파를 노리며 리스크를 키우는* 행동 → council이 "집중을 키우지 말고 *제한*"으로 뒤집음.
- **13F → 사용 금지 사례.** 분기말+45일 지연 → 스윙 시간축엔 죽은 데이터. "거인 추종"의 미국판 대안으로 쓰지 말 것.

**일관성:** 본문 §0.3·부록 A 단일 최중요 보정(firm-income↔strategy-return 분리)과 동일 논리 — 두 사견 모두 "시장/거인의 movement = 참"이나 "내 전략의 검증수익 = 미검증"이라 ALPHA 자격 없음.

---

## 부록 B. LLM 트레이딩 회의론 — 실증 (critic이 1차 docx 누락으로 지적)

1차 docx와 본문 §7은 "LLM은 최종 결정자가 아니다"를 권고하지만, **왜 위험한지의 실증**이 빠져 있었다. 2025-2026 회의론 벤치/메타가 그 빈칸을 채운다 — 이것이 LLM을 라이브 주문경로에서 빼야 하는 직접 근거다.

| 출처 (연도) | 무엇이 깨지나 (failure mode) |
|---|---|
| **StockBench** (2025-10, arXiv 2510.02209) | 오염없는 post-cutoff 평가에서 LLM 에이전트 대부분이 buy&hold(+0.4%)도 못 이김; 하락장에선 *전원* 패배. 산술오류·JSON스키마오류·종목수↑시 성능붕괴. "정적 금융지식 ≠ 트레이딩 성공." 비용 미모델 = 그 빈약한 '승리'도 상한값. |
| **TradeTrap** (2025-12, arXiv 2512.02261) | 작은 교란이 파국으로 증폭: 프롬프트 인젝션 → 집중도 39%→**99.98%**, Sharpe 5.72→0.29; 상태 교란 → **총수익 −61% / MDD 1.59%→92%**; 메모리 오염 → 둘 다 음의 Sharpe(실행로직 불변). 처방 = **추론과 무관하게 하드 제약(한도·분산) 강제**. |
| **LiveTradeBench** (2025-11, arXiv 2511.03628) | 리더보드 점수 ↔ 실거래 수익 상관 = **0.054(美주식) / −0.38(Polymarket)**. 범용지능은 실거래에 예측력 0~음. 추론모델이 더 변동성 큼. |
| **FINSABER** (2025, arXiv 2505.07078) | 20년 비용후 재검증: LLM 전략이 buy&hold 못 이기고 **알파 통계적 무의미(p>0.34)**, ARIMA·룰베이스에도 짐. 병리 = 상승장 과소·하락장 과대. |
| **The Alpha Illusion** (2026, arXiv 2605.16895) | 메타비판 + P1~P6 리포팅 프로토콜. TradingAgents Sharpe 0.43→0.22(마찰후), QuantAgent 음수화; 멀티에이전트 "토론 승리" ~20%·동일생태계 상관(가짜 앙상블). "**language confidence ≠ tradable probability; LLM = auditable upstream interface, not final authority**." |
| **The Memorization Problem** (2025, arXiv 2504.14765) | LLM이 cutoff 이전 가격을 사실상 암기(방향 96~99%), "미래 무시" 지시도 실패 → **post-cutoff 평가만 신뢰 가능**. LLM 백테스트 누수의 근본원인. |

**TradingAgents 토폴로지의 교훈(반면교사):** `애널리스트팀→bull/bear 토론→trader→리스크팀→펀드매니저` 구조에서 **주문 내는 PM도 LLM = 결정론 게이트 없음**. 우리가 그 자리에 코드 게이트를 넣는 것이 학계 합의와 일치한다. FinCon의 CVaR ablation은 "리스크 통제 > 에이전트 똑똑함"을 실증(빼면 +25%→−1.5%) — **게이트는 LLM 리스크팀이 아니라 코드로**.

> **critic §(f) 결론과 합치:** LLM의 방어가능한 역할은 (a) 약신호 입력 + (b) 인간/오프라인 규칙으로 가는 advisory 플래그뿐. **hard-veto를 라이브 주문경로에 두면 "사전정의 조건"이라도 같은 함정** — 조건이 규칙이면 그 규칙(코드)이 vetoer이고, LLM 판단이면 비재현 결정(금지). 따라서 본문 §8 Layer 6은 **라이브 경로에서 빼서 off-path advisory critic**으로 둔다.

---

## 부록 C. Sources

워크플로 9개 프로파일이 인용한 공개 출처(중복 제거). 1차 docx의 S1~S28(Reuters·SEC·공식 홈페이지 등)과 합산해 읽을 것. 일부 링크는 지역/권한 제한 가능.

[W1] https://www.man.com/results-for-the-financial-year-ended-31-december-2024
[W2] https://www.investegate.co.uk/announcement/rns/man-group--emg/financial-results-for-the-year-ended-2025/9447616
[W3] https://data.fca.org.uk/artefacts/NSM/Portal/NI-000114346/NI-000114346.pdf
[W4] https://www.man.com/ahl
[W5] https://www.man.com/ahl-diversified
[W6] https://www.man.com/insights/the-rise-of-machine-learning
[W7] https://www.man.com/insights/the-impact-of-volatility-targeting
[W8] https://www.man.com/insights/ahl-explains-volatility-scaling
[W9] https://www.man.com/insights/counting-the-costs
[W10] https://www.man.com/insights/strategic-execution-trajectories
[W11] https://www.man.com/numeric
[W12] https://www.man.com/insights/black-box-glass-box
[W13] https://www.man.com/maninstitute/the-future-of-quant-equity
[W14] https://www.man.com/maninstitute/oxford-man-institute
[W15] https://www.directorstalkinterviews.com/man-group-plc-q1-aum-rises-to-172-6bn/4121192750
[W16] https://find-and-update.company-information.service.gov.uk/company/12300034/filing-history
[W17] https://www.bloomberg.com/news/articles/2025-04-04/gerko-s-xtx-markets-mints-3-53-billion-on-global-trading-surge
[W18] https://www.globaltrading.net/xtx-markets-profits-skyrocket-in-2024/
[W19] https://www.financemagnates.com/forex/xtx-markets-posts-50-profit-jump-to-128-billion-on-trading-surge/
[W20] https://www.xtxmarkets.com/tech/
[W21] https://github.com/XTXMarkets/ternfs
[W22] https://news.lavx.hu/article/inside-ternfs-how-xtx-markets-built-a-petabyte-scale-filesystem-for-machine-learning-at-the-edge
[W23] https://www.financemagnates.com/institutional-forex/xtx-markets-unveils-machine-learning-lab-blending-finance-with-technology/
[W24] https://liquidityfinder.com/news/xtx-markets-launches-new-machine-learning-division-xty-labs-led-by-atlas-yang-c0033
[W25] https://grokipedia.com/page/XTX_Markets
[W26] https://en.wikipedia.org/wiki/XTX_Markets
[W27] https://www.marketsmedia.com/flow-traders-posts-second-best-fiscal-year-results/
[W28] https://live.euronext.com/en/products/equities/company-news/2025-02-13-flow-traders-4q-and-fy-2024-results
[W29] https://www.marketscreener.com/quote/stock/FLOW-TRADERS-LTD-22852251/news/Flow-Traders-2024-Annual-Report-incl-Audit-Opinion-49797364/
[W30] https://www.globenewswire.com/news-release/2025/02/13/3025593/0/en/Flow-Traders-4Q-and-FY-2024-Results.html
[W31] https://mlq.ai/news/jane-street-reports-record-205-billion-net-trading-revenue-for-2024-nearly-doubling-previous-year/
[W32] https://www.globaltrading.net/jane-street-took-10-of-of-us-equity-market-in-2024/
[W33] https://blog.janestreet.com/
[W34] https://www.janestreet.com/technology/
[W35] https://en.wikipedia.org/wiki/Jane_Street_Capital
[W36] https://www.elearnmarkets.com/school/units/unknown-market-wizards/marsten-parker-don-t-quit-your-day-job
[W37] https://www.harriman-house.com/unknownmarketwizards
[W38] https://chatwithtraders.com/episode/281-marsten-parker-the-purely-systematic-wizard-trader
[W39] https://bettersystemtrader.com/183-overcoming-broken-strategies-marsten-parker/
[W40] https://mhptrading.com/about.html
[W41] https://www.alphamindpodcast.buzzsprout.com/288762/6435082
[W42] https://rss.com/podcasts/confessionsmm/137540/
[W43] https://stockanalysis.com/etf/qmom/
[W44] https://stockanalysis.com/etf/qval/
[W45] https://funds.alphaarchitect.com/qmom/
[W46] https://funds.alphaarchitect.com/qval/
[W47] https://etfdb.com/etf/QMOM/
[W48] https://etfdb.com/etf/QVAL/
[W49] https://totalrealreturns.com/n/QMOM
[W50] https://totalrealreturns.com/n/QVAL
[W51] https://www.validea.com/wesley-gray
[W52] https://pictureperfectportfolios.com/qmom-etf-strategy-review-alpha-architect-us-quantitative-momentum/
[W53] https://seekingalpha.com/article/4580029-qval-a-close-look-at-the-methodology
[W54] https://etfarchitect.com/wp-content/uploads/compliance/etf/statutory_prospectus/AA%20Pro.pdf
[W55] https://alphaarchitect.com/wp-content/uploads/compliance/etf/summary_prospectus/QMOM%20Summary%20Pro.pdf
[W56] https://stockanalysis.com/etf/provider/alpha-architect/
[W57] https://portfolioslab.com/tools/stock-comparison/QMOM/VOO
[W58] https://www.amazon.com/Quantitative-Momentum-Practitioners-Momentum-Based-Selection/dp/111923719X
[W59] https://www.worldcupchampionships.com/world-cup-trading-championship-standings
[W60] https://www.worldcupchampionships.com/world-cup-championship-futures-trading-past-winners
[W61] https://robbinstrading.com/world-cup-trading-championships/
[W62] https://en.wikipedia.org/wiki/Andrea_Unger
[W63] https://www.worldcupadvisor.com/
[W64] https://ungeracademy.com/
[W65] https://grokipedia.com/page/World_Cup_Trading_Championships
[W66] https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting

---
## 부록 E. Codex 독립조사 — 솔로 트레이더 구조 레퍼런스 (교차검증)

워크플로와 **독립으로** 돌린 Codex(GPT-5.5) 조사는 group C를 다른 후보(Carver/Davey/Clenow)로 잡았고, KR-swing에 더 직접적인 솔로 설계를 제시했다. 워크플로의 Parker/Unger/Alpha Architect와 *상보적*이라 그대로 싣는다.

**4. Rob Carver**
Macro architecture:

```text
futures price data
  -> adjusted continuous series / carry data
  -> modular trading rules
  -> forecast scaling and capping
  -> instrument diversification multiplier
  -> position sizing by risk target
  -> portfolio aggregation
  -> broker interface / automated IB execution
  -> diagnostics and human supervision
```

Humans design rules, choose instruments, review diagnostics, and intervene on operational failures. The system can run automated.

Modeling: Carver’s public framework is one of the best solo-friendly architectures. The key idea is not prediction accuracy; it is robust position sizing under uncertainty. Forecasts are scaled, capped, diversified, and translated into risk-targeted positions. He favors simple rules across many instruments over overfit complexity. For Korea: copy the architecture even if you replace futures with KOSPI100 equities: normalized forecasts, position sizing by volatility, turnover penalties, risk overlays, automated diagnostics, and a kill-switch. Discard large futures diversification until US futures are added.

**5. Kevin Davey**
Macro architecture:

```text
idea generation
  -> historical test with realistic costs
  -> out-of-sample / walk-forward validation
  -> Monte Carlo robustness
  -> incubation / live or paper monitoring
  -> portfolio of many small independent systems
  -> automated execution with rules for retirement
```

Humans are heavily involved in strategy creation, acceptance/rejection, and retirement. Execution can be automated.

Modeling: Davey’s useful contribution is process discipline for solo algo traders. He emphasizes avoiding curve fit, using out-of-sample and walk-forward tests, Monte Carlo, and trading many small strategies rather than worshipping one system. Verification is not institutional-grade; the World Cup record is a contest track record, and course-selling incentives require skepticism. For ₩10M: copy the factory discipline and strategy retirement rules. Discard the “100% annual return” framing; with Korean tax and small capital, survival and after-cost benchmark beating matter more.

**6. Andreas Clenow**
Macro architecture:

```text
equity/futures universe
  -> liquidity and survivorship-safe data
  -> regime filter
  -> momentum/trend ranking
  -> volatility-adjusted sizing
  -> weekly/monthly rebalance
  -> sell rules / risk control
  -> mostly automated portfolio updates
```

Humans define universe, rebalance schedule, and risk policy. Trade selection is systematic.

Modeling: Clenow’s equity momentum method is directly relevant to KOSPI100. Public summaries of “Stocks on the Move” use S&P 500 stocks, rank by volatility-adjusted momentum using 90-day log-price regression slope times fit quality, require stocks above moving averages, apply a market regime filter, and size with volatility/ATR logic. This maps well to swing equities. For Korea: copy volatility-adjusted momentum ranking, weekly rebalance, market filter, liquidity filter, and ATR sizing. Discard aggressive turnover and excessive concentration until after-cost live evidence supports it.

**C) Frontier Blueprint For Your ₩10M KR Swing System**
Build this:
```text
1. Point-in-time data layer
   KOSPI100 constituents, adjusted OHLCV, corporate actions, suspension flags, tax/fee/slippage model.
2. Signal layer
   Core: 3-12 month momentum, 1-month skip if tested, 90-day regression momentum, quality/value if data is reliable.
   Regime: KOSPI100 above/below 100/200-day trend, volatility regime, breadth.
3. Validation layer
   Walk-forward, purged dates around rebalances, delisted/changed constituents, realistic sell tax, spread/slippage, no same-close fills.
4. Portfolio layer
   5-15 names max at ₩10M, volatility-scaled weights, max single-name cap, turnover budget, cash allowed.
5. Execution layer
   Daily after close signal generation -> next-session limit/VWAP-style orders -> order reconciliation.
6. Monitoring layer
   Expected vs actual fills, slippage, exposure, drawdown, stale data, missing prices, model drift.
7. Human layer
   Human approves daily order batch or leaves auto-approve on; only final veto/kill-switch.
```
**Copy**
- From AQR: multi-factor ranking, cost-aware portfolio construction, lagged data, simple interpretable signals before ML.
- From Man AHL/Carver: volatility targeting, normalized forecasts, risk overlays, automation, diagnostics.
- From Clenow: volatility-adjusted equity momentum and market regime filter.
- From Davey: strategy factory, walk-forward testing, Monte Carlo, incubation before real capital.
- From Renaissance: data obsession, capacity discipline, no manual emotional overrides.
**Discard**
- HFT, market making, intraday prediction, order-book alpha.
- Expensive alternative data.
- Deep learning as first model.
- High-turnover long/short equity.
- Copy-trading/course-seller return targets.
- Anything that cannot beat `KOSPI100 after tax/cost + cash` in honest walk-forward tests.
**Three Biggest Traps**
1. **Costs kill Korean swing systems.** A 0.20% sell tax means a round trip must overcome tax, spread, commission, and slippage before alpha exists. Weekly high-turnover systems may look good gross and fail net.
2. **Survivorship bias in KOSPI100.** Testing today’s KOSPI100 backwards is invalid. You need historical constituents or a conservative proxy with penalties.
3. **Approval-layer drift.** If the human can “improve” trades daily, the system is not automated. Human role should be data/risk veto only.
**D) Best Sources**
1. Man AHL overview: https://www.man.com/ahl  
2. Man AHL trend-following platform notes: https://www.man.com/sites/default/files/uploads/embed/ahl-trendfollowing-why-trend/index.html  
3. AQR systematic equities: https://www.aqr.com/Learning-Center/Systematic-Equities/Systematic-Equities-A-Closer-Look?aqrPDF=1  
4. AQR ML stock portfolios paper: https://www.aqr.com/-/media/AQR/Documents/Alternative-Thinking/Alternative-Thinking-2024-Issue-4-Can-Machines-Build-Better-Stock-Portfolios.PDF  
5. AQR SEC filing excerpt: https://www.sec.gov/Archives/edgar/data/1444822/000119312526022448/d55120d485bpos.htm  
6. Renaissance ADV summary: https://www.rialytix.com/crd/106661/renaissance-technologies-llc  
7. Renaissance public background: https://en.wikipedia.org/wiki/Renaissance_Technologies  
8. Rob Carver `pysystemtrade`: https://github.com/pst-group/pysystemtrade  
9. Rob Carver bio: https://www.systematicmoney.org/bio  
10. Kevin Davey bio/interview: https://kjtradingsystems.com/about.html  
11. Clenow equity momentum summary: https://www.turingtrader.com/portfolios/clenow-stocks-on-the-move/  
12. Numerai docs for public OOS scoring discipline: https://docs.numer.ai/

**Codex가 꼽은 3대 함정 (우리 환경 특화):**
1. **비용이 KR swing을 죽인다** — 0.20% 매도세 + 스프레드 + 수수료 + 슬리피지를 넘어야 알파가 시작. 주간 고회전은 gross 좋아도 net 실패.
2. **KOSPI100 생존편향** — 오늘의 KOSPI100을 과거로 백테스트하면 무효. 역사적 구성종목 또는 보수적 프록시+페널티 필요.
3. **데이터 부족 과적합** — ₩10M·짧은 KR 히스토리 = 독립 베팅 적음. 모델 복잡도보다 walk-forward·Monte Carlo·회의적 사이징이 더 중요.

---

## 부록 D. Locked Research Brief (v0.5 요약)

```json
{
 "target_count": 9,
 "groups": {
  "A_large_systematic": {
   "count": 3,
   "candidates": [
    "Renaissance Technologies",
    "D.E. Shaw",
    "Two Sigma",
    "Man AHL",
    "AQR"
   ]
  },
  "B_frontier_mm_prop": {
   "count": 3,
   "fixed": [
    "XTX Markets"
   ],
   "candidates": [
    "XTX Markets",
    "Jane Street",
    "Citadel Securities",
    "HRT",
    "Jump",
    "Tower",
    "Optiver",
    "IMC",
    "DRW"
   ]
  },
  "C_small_individual": {
   "count": 3,
   "allowed": [
    "개인 systematic trader",
    "극소수 팀",
    "소형 CTA",
    "소형 systematic fund",
    "공식 대회 우승자",
    "브로커 인증 실계좌",
    "장기 검증된 공개 실거래 기록"
   ]
  }
 },
 "objectives": {
  "primary": "수익률 극대화",
  "secondary": "개인/소규모(클라우드 GPU+개인 PC) 응용가능성=평가항목(하드제약 아님)",
  "mdd": "MDD 25% strong preference (hard filter 아님)"
 },
 "markets": {
  "primary": [
   "한국주식",
   "미국주식"
  ],
  "reference": [
   "선물",
   "옵션"
  ],
  "excluded": [
   "크립토"
  ]
 },
 "llm_council": {
  "role": "alpha contributor + research automation + adversarial critic + governance/veto/escalation. 최종 결정자 아님(optimizer/risk engine 위 review layer)",
  "veto": "사전정의 위험조건에서만 hard veto",
  "avoid": [
   "LLM이 매주문 최종결정",
   "hallucination 주문",
   "비재현 결정",
   "risk engine보다 LLM 우위"
  ]
 },
 "scorecard_dims": [
  "수익검증성",
  "수익잠재력",
  "자동화수준",
  "프론티어성",
  "자료신뢰도",
  "개인응용가능성",
  "데이터우위",
  "execution난이도",
  "리스크통제력",
  "LLM-agent결합적합성"
 ]
}
```
