# PRAMANA V4 — LOCK SHEET v0.1

> **확정된 것만** 정리. 각 LOCK 아래 `근거:`에 *왜 그렇게 정해졌는지*(데이터·회의·문헌) 자세히 적음.
> 미확정은 맨 끝 **OPEN**에 분리. 작성 2026-06-11 · 상태 **PAPER only / NO LIVE**.
> 명명: 여기 **V4** = core-satellite 재설계. 내부 v1·v2·v3 = 이전 작업(연구·검증 엔진 + 페이퍼 북).

---

## 0. 프로젝트 정체성 (LOCK)

- **L0.1** PRAMANA V4 = 솔로 + AI용 **US 주식/ETF systematic 페이퍼 트레이딩·검증 OS**. 종목 찍는 AI 아님.
- **L0.2** **PAPER first / NO LIVE.** 가상자본 ₩100M.
- **L0.3** 시장 = **US equities/ETFs only.** crypto 제외. KR = 무기한 보류.
- **L0.4** 거래주기 = **일봉(daily) 중심.** 실시간/분봉 매매 아님.

> **근거:** 일봉인 이유 — 미국 주식은 24h 시장이 아니고 우리 신호(추세·레짐)는 일별로 충분. 분봉/단타는 (a) 리테일 데이트레이더 **74~89% 손실**(검증된 base rate), (b) 매 거래 스프레드+수수료가 엣지를 잠식, (c) ORB/VWAP 백테스트는 화려하고 라이브는 슬리피지로 처참 — 그래서 분봉은 "고도화"가 아니라 *가장 강하게 격리할 실험실*로만(L8.4). GPU·클라우드 불필요 — ML 미사용이라 전부 CPU pandas 산술(밀리초).

---

## 1. 목적함수·철학 (LOCK)

- **L1.1 Core-satellite 구조.** SPY/QQQ 코어를 기본 장착하고 그 위에 검증된 위성으로 초과수익. **"SPY를 버리고 이기기" 금지 — "SPY를 깔고 위에 얹기".**
- **L1.2 목적함수 = maximize 초과수익 over core, s.t. MDD ≤ X.** **생존(낙폭 한도)이 제약, 수익이 목적.** (X 값은 OPEN.)
- **L1.3 데이터·비용 정직 → 검증 → 그 다음 모델.** 사전등록 kill 조건(결과 보기 전 확정).
- **L1.4 금지 원칙:** 최근 성과 보고 *즉흥* 전략 변경 금지 · LLM/TSFM 직접 주문·비중·리스크한도 변경 금지.

> **근거(L1.1·L1.2):** 멀티시점 net 백테스트에서 **풀북이 SPY를 어느 horizon(3M/6M/1Y/풀사이클)에서도 위험조정으로 못 이겼다.** 풀사이클 3x가 +699% vs SPY +307%로 이긴 것처럼 보여도 MDD −45% vs −34%·**Sharpe 0.82 < 0.90** = 레버리지 효과지 엣지 아님. → "SPY 이기기"를 정면 목표로 두면 진다. 코어로 SPY 베타를 *깔면* 최악이라도 "코어−위성비용"이고 위성은 조금만 보태면 된다. "수익 최대화"만으론 안 되는 이유 = *얼마나 잃는 걸 견디나*가 빠지면 같은 전략도 살릴지 죽일지 판단 불가 → V1이 망한 뿌리(기관용 잣대를 소액 계좌에 적용).
> **근거(L1.4):** Codex 거버넌스 리뷰 — 즉흥 변경/자기최적화는 "multiple-testing 기계"가 되어 최근 차트에 과적합. 레퍼 회의(Codex+Claude 3)도 "방금 지나간 차트에 춤추기"를 핵심 위험으로 지목.

---

## 2. 실증 사실 (LOCK — 측정됐으므로 가장 강한 락)

- **L2.1 단순/선형 횡단면 팩터 = 강건한 net 엣지 없음.** value/momentum/lowvol **DEAD**, quality는 broad에서 SURVIVE-screen(IC-IR 0.220) 후 **quarantine FAIL**.
- **L2.2 풀 v3 북 = SPY를 위험조정으로 못 이김** (전 horizon).
- **L2.3 Phase 1 (core-satellite): trend+LETF 위성은 수익을 안 보탠다.** 풀사이클서 연 ~−1% 수익 + MDD −3%p, **Sharpe 0.95→0.98(노이즈).** 위성 = 약한 낙폭 헤지지 알파 아님.
- **L2.4 파이프라인은 정확하다.** self-built S&P500 PIT cap-weight가 실제 SPY와 **corr 0.998**.
- **L2.5 결론: 솔로에게 베껴올 쉬운 알파 엣지는 없다.**

> **근거(L2.1):** B2~B5 broad retest(비용후, 사전등록 kill) — momentum net +7.6%지만 IC-IR 0.10·turnover 301%→DEAD; quality는 IC-IR 0.220이나 quarantine서 **최근 절반 decay(2016-20 IC-IR 0.42 → 2021-26 0.046)** + long-only가 cap-weight를 −1.15%/yr 밑돎 → 거래가능 형태론 실패.
> **근거(L2.3):** phase1a/engine/phase1_core_satellite.py — Core(SPY/QQQ 50/50) vs Core+Trend+LETF(고정 70/25/5, 비용후, 레버 없음). 풀사이클 9.6년: Core +411%·MDD −31%·Sharpe 0.95 / Core+Sat +369%·MDD −28%·Sharpe 0.98. 위성이 수익 41%p 깎고 낙폭 3%p 줄임 — Sharpe +0.03은 노이즈. 강세장(1Y/6M/3M)선 순드래그.
> **근거(L2.4):** B0 broad — SHARADAR/SP500 add/remove 역재생으로 PIT 멤버십 구축(future-leakage 차단), cap-weight TR이 실제 SPY와 corr 0.998·연차 +0.55%p. = PIT·survivorship·배당·CA 처리 정확성 강력 검증. **데이터/기계는 믿어도 됨 — 문제는 알파지 파이프라인 아님.**
> **근거(L2.5):** L2.1~L2.3 + 레퍼 회의 결론(아래 L6). 알파가 있었으면 차익거래로 사라졌을 것 — 그래서 책·레퍼가 알파를 안 준다. 이건 실패가 아니라 *퀀트에서 가장 값진 앎*이며 달성가능 목표(규율 코어 + 리스크 control + 정직 forward)를 정의함.

---

## 3. 모델·방법 (LOCK)

- **L3.1 ML/딥러닝/TSFM = alpha 용도 reject.** 직접 수익 예측기로 안 씀.
- **L3.2 DL/LLM 허용 위치 = off-path 보조만:** 스캐너·필터·메타라벨러·레짐 feature·sentiment 요약·red-team. **금지:** 직접 주문·종목선택·비중산출·risk veto·live config 변경. (schema-locked·versioned 예외 외 alpha 금지.)
- **L3.3 boring baseline 먼저 = 1/N·고정비중** (추정 MVO 아님).
- **L3.4 meta-allocator는 고정비중 baseline을 OOS·비용후 이겨야 채택.** 못 이기면 고정비중. (사전 기대 = 고정비중이 이김.)
- **L3.5 next-bar 실행** (신호 t → 진입 t+1). same-close 체결 금지.
- **L3.6 추세 = 레짐의존 크래시 보험/리스크 도구지 수익 엔진 아님.**
- **L3.7 벤치마킹은 2개 레이어만** (trend·allocator). 전 레이어 모델 비교 = data-mining theater 금지.

> **근거(L3.1):** 3원 수렴 — ① DR-4 모델맵(deep-research 104에이전트): TSFM/deep = reject-for-alpha; ② Codex: 일별 Sharadar에 deep = theater; ③ 자체 walk-forward bake-off: ridge +0.15·GBM +0.02 net Sharpe 모두 3-feature 선형(0.33) 못 넘음. + Gu-Kelly-Xiu(2020): 최고 ML도 월 OOS R² ~0.4%, 그 엣지가 마이크로캡·숏·비용전에 집중(대형주·VW·ex-microcap서 66~78% 증발), **얕은 게 깊은 걸 이김**(NN 3층서 정점). + 자유도 논리: TSFM 수백만 파라미터를 실효 독립표본 수십 개(독립 거시국면)에 맞춤 = 과적합 보장. + 비정상성: McLean-Pontiff(2016) 아노말리 발표후 ~58% 소멸 — DL은 *어제의 규칙성*을 배우는데 시장이 지움. → 입증책임은 DL에 있고 네 데이터/스케일/비용에선 반복 실패. (포기 아니라 맞는 자리=L3.2.)
> **근거(L3.3·L3.4):** DeMiguel-Garlappi-Uppal(2009) — 14개 최적화 배분 중 **어느 것도 1/N을 OOS로 일관되게 못 이김**(표본 MVO는 25자산에 >3000개월 필요). → 똑똑한 allocator가 v4의 새 #1 과적합 표면. "고정비중 OOS 못 이기면 폐기"로 강제.
> **근거(L3.5):** Codex 리뷰가 v3 코드서 **same-close 누수**(신호=종가→진입=같은 종가) 발견 → next-bar로 수정. look-ahead의 가장 흔한 잠입 경로.
> **근거(L3.6):** 풀파워 회의 — CTA "잃어버린 10년"(SG Trend 지수 연 +0.4% 2009-18 vs SPY +200%), 추세는 2008·2022 방향성 레짐서만 작동·2011-21 chop서 실패. + Phase 1(L2.3)이 위성=낙폭헤지지 알파 아님을 확정.
> **근거(L3.7):** Codex — 전 레이어 모델 비교는 Phase 1 baseline도 없이 자유도 폭발 → deflated Sharpe가 경고하는 가짜 Sharpe 양산. "near-term 결정 바꿀 모델만 벤치마킹, 나머진 멍청한 baseline." 서브에이전트 분석도 7개 중 trend·allocator 2개만 가치(그것도 allocator는 baseline이 이길 것).

---

## 4. 8 레이어 + 권한 (LOCK)

- **L4.1** 레이어 = **Data&Integrity → Regime Engine → Sleeve Library → Meta-Allocator → Risk Engine → Execution → Attribution&Monitoring → Governance.**
- **L4.2 권한 위상:** 신호 ≠ 주문 · 알파 ≠ 포지션 · **결정적 risk engine이 최종 veto** · LLM off-path · **사람이 capital(실제 돈) 게이트.**
- **L4.3 Capital Allocator만 자본 배분권 보유.** Intraday Lab의 요청을 직접 안 받음.
- **L4.4 Attribution 레이어 필수:** core / 각 위성 한계기여 / allocator 타이밍(고정비중 대비) / intraday gross−비용 분해.

> **근거(L4.2):** LEAN(Alpha→Insight→PortfolioTarget→Risk→Execution 일방향, 주문은 Execution서만)·Nautilus(pre-trade RiskEngine 게이트) 골격 차용 — 견고하고 솔로도 그대로 베낄 수 있는 *구조*. DR 전 시퀀스서 authority topology로 LOCK 유지.
> **근거(L4.4):** v3의 교훈 — 전체 성과만 보면 "시스템이 벌었다" 착각하는데 실제론 trend가 다 캐리하고 equity가 희석. attribution 없으면 "누가 벌었나" 구분 불가 = 자기기만. Phase 1도 attribution(위성 기여 분해)으로 "위성 −1%/yr"를 잡아냄.

---

## 5. 리스크 엔진 (LOCK)

- **L5.1 없애지 않는다.** 판정 *언어*만 교체: **live 가능 / paper 유지 / 변형 후 재검증 / sandbox 전용 / 영구 폐기.**
- **L5.2 capital-veto ↔ research-veto 분리.** (예: VRP short-vol은 MDD −92%라 capital-veto[live 영구불가]지만 tail-hedge 변형 *연구*까지 막진 않음.)
- **L5.3 vol-target은 리스크 *캡*이지 알파 아님.** + DD ladder · per-name cap · gap risk · 결정적 최종 veto.

> **근거(L5.1·L5.2):** V1의 이진 폐기(통과/폐기)가 너무 경직 → "standalone 엣지 없지만 앙상블/특정 레짐선 쓸모"를 못 살림. 세분화 + "죽은 전략 살리기 아니라 *죽은 이유 분류*"(Parker의 수익곡선 기반 시스템 은퇴 차용). 단 reversal처럼 *비용 전에도 음수*면 완화로 안 살아남 = 영구폐기.
> **근거(L5.3):** Moreira-Muir(2017)의 vol-target Sharpe 개선은 Cederburg 등이 103전략서 반박(체계적 이득 없음) — 그래서 vol-target의 *방어적* 가치(낙폭 통제)만 인정, 알파로 안 봄. fractional-Kelly는 사이징 oracle 아니라 *상한*(풀 Kelly는 ~50% DD).

---

## 6. 레퍼런스 사용 원칙 (LOCK — 풀파워 회의 후 교정)

- **L6.1 레퍼 = "부품 창고"지 "전략 쇼핑몰" 아님.** 레퍼별 *전체 전략 베끼기 금지* — 역할당 *검증된 부품 하나*, baseline 이겨야 승격.
- **L6.2 레퍼는 V4의 *리스크 구조*는 지지하나 *알파*는 검증 못 함.** (그들 알파는 시대·스케일 의존, 지금 decay/marginal.)
- **L6.3 "구조 차용, 스케일 폐기"** — 단 *엣지가 스케일에 살았을 수 있음*을 인정(구조는 살아도 알파는 죽을 수 있다).
- **L6.4 교정된 매핑:**

| 레퍼 | 가져올 부품 | 주의 |
|---|---|---|
| Carver | 리스크 사이징·vol-target (배관) | 수식 복붙 금지·단순형부터·그의 수식은 20~40 futures breadth 가정(우린 그게 빠짐)·"Sharpe 1.0 넘는 일 드물다" 경고 |
| Clenow | trend 위성·200일선 gate·ATR/vol sizing | 200일 필터는 *fragile*(whipsaw 느림)·개별주 모멘텀은 비용·회전율 검증 필요 |
| Marsten Parker | **수익곡선 기반 시스템 은퇴 규율만** | **그는 trend 아님 — long-only 단일주식 *평균회귀* 트레이더(모멘텀→MR 전향). 내 최초 매핑 오류 교정.** |
| Alpha Architect | quality/momentum long-only 위성 *후보* | 코어 대비 한계기여로만 평가 |
| AQR / Man | factor·trend의 *학술 근거만* | 수익모델 복제 금지(스케일 다름) |
| LEAN / Nautilus | alpha→risk→execution 권한 골격 | (견고·직접 참고 OK) |
| XTX / Jane Street | 거버넌스·재현성·리스크 문화만 | 수익전략 복제 불가(게임 다름) |

> **근거(L6.1·L6.2):** 풀파워 회의(Codex + Claude 서브 3, 각자 웹검색) 만장일치 = "레퍼 수렴 → V4 검증"은 **순환논법**(V4 먼저 짓고 맞는 레퍼 골라 검증이라 함) + **생존편향**(Carver/Clenow/Parker는 살아남아 책 쓴 사람들·동일방법 실패자 무덤은 안 보임·리테일 74~89% 손실). 수렴이 가리킨 trend/momentum은 decay·레짐의존(L3.6). → 레퍼는 V4의 *미학·리스크 구조*는 방어하나 *엣지*는 못 함.
> **근거(L6.4 Parker):** 웹 검증 — Parker는 100% systematic **long-only 단일주식 평균회귀**, 모멘텀에서 평균회귀로 전향, 시스템의 *자기 수익곡선이 200일선 깨지면* 은퇴. 내가 그를 trend/portfolio-of-systems로 매핑한 건 사실오류 → 교정. (그가 전향한 *평균회귀*는 우리가 무시한 방향 = chop장서 trend 실패할 때 작동 가능 → 미래 위성 후보로만 기록, 지금 추격 금지.)

---

## 7. 거버넌스·자율성 (LOCK)

- **L7.1 줄일 수 없는 인간 게이트:** 자본 증액 · 코드/전략 변경 live 반영 · 리스크 한도 변경 · 데이터 벤더 변경 · kill 후 재시작.
- **L7.2 자동개선 = research candidate 생성까지만.** live 변경은 사람 승인 + 동결 프로토콜.
- **L7.3 레버리지 실자본 *완전* 자율 = 솔로엔 무책임.** (목표는 인간개입 *최소화*지 *제거*가 아님.)
- **L7.4 자기개선 2종 구분:** within-strategy 적응(allocator 비중)= 지금 자동 OK·안전 / meta 재설계(V1→V4류)= 판단·적대 다양성 필요 → 자동화 최후·오래도록 *제안만*.

> **근거:** Codex 거버넌스 리뷰(출처: SEC market-access rule·FINRA 15-09·ProShares LETF daily·yfinance 약관) — 솔로는 독립 리스크/컴플라이언스 데스크 없고 레버리지가 그 약점을 분산불가하게 만듦. 자기최적화는 multiple-testing 기계(최근 레짐 과적합). **V1→V4가 된 이유 = 세 적대지능(용하·Claude·GPT)이 *불일치*하고 증거로 서로 깸** — 단일 자기최적화는 이 적대 다양성을 잃고 자기편향 수렴. → 자율은 *동결 검증 프로토콜이 신뢰 쌓은 뒤* 점진 위임, 그게 진짜 빌드물.

---

## 8. 빌드 순서·현재 위치 (LOCK)

- **L8.1 빅뱅 금지.** 한 부품씩, baseline 이기는지 확인 후 승격.
- **L8.2 Phase 1 = Core + trend/LETF 위성 + 고정 allocator + attribution.** → **완료. 결과: 위성은 알파 아님(L2.3).**
- **L8.3 다음 = A1(목적함수) 확정 → "core만" vs "core+가벼운 trend 오버레이(낙폭 도구)" 결정 → forward 투입.**
- **L8.4 나머지(cross-sectional alpha 부활·기관신호·분봉 lab·TSFM/LLM)는 보류가 아니라 — *forward가 실제 gap을 보일 때만* 연다.** 분봉은 열려도 paper-only·capital 침범 금지·gross−비용 분해.

> **근거:** V1 사후분석 — 문서 15·게이트 14·registry 60필드인데 코드/데이터 0이던 시기 = analysis-paralysis("wrong scale이 모델 아닌 *프로세스*에 발생"). → 크루드한 것부터 ship. Phase 1이 부품 4개로 핵심 질문에 답한 게 그 증명. L8.4의 "forward gap 보일 때만"인 이유 = 더 추가할수록 *검증할 과적합 표면*이 늘고(레퍼·모델 더 넣기 = V1 실수 반복), 알파 부재가 이미 확인됨(L2.5) — 시장(forward)이 유일한 오라클.

---

## 9. 운영 (LOCK)

- **L9.1 forward 페이퍼 = 일 1회(미국 장마감 후).** 무인. free EOD(yfinance). fail-closed 무결성 가드(stale/NaN/바개수/배드틱). append-only(재현성). look-ahead 없음.
- **L9.2 GPU·클라우드 불필요** — ML 미사용·CPU pandas. 미니PC cron `0 6 * * 2-6`.
- **L9.3 실자본 전 데이터 이원화** = 2 독립 피드 + 브로커 대조 필요(무료 단일 피드는 레버 실자본 부적합). 페이퍼 단계는 무료로 충분.

> **근거:** Codex 리뷰 — 무료 단일 EOD는 배당/분할 조정 오류 1건이 3x 레버서 신호를 뒤집음(조용한 오염 = 깨끗한 대시보드 + 오염된 기록). → fail-closed 가드 + 실자본 전 이중화. 일봉 1회면 충분한 이유 = L0.4 근거.

---

## OPEN (미확정 — 정해지면 이 시트에 승격)

- **A1** 감내 MDD `X` · 실제 운용 자본 · 투자 시계 → **다음 행동의 전제.** (위성 채택 여부 = 리스크 선택이지 엣지 아님 → A1이 "core만" vs "core+오버레이" 결정.)
- **A3** quality 부활 여부 (원본 B3 재검토 필요·decay 우려).
- **A4** 기관신호(13F/ETF flow) 사용 여부·소스·복제규칙 (45일 지연=느린 틸트만).
- **A5** 분봉 = 진짜 일중 단타냐 vs 잦은 스윙이냐.
- **A6** short/borrow 사용 여부·차입비용 모델 (Codex: 0.5% 차입은 환상).
- **A7** intraday 데이터 벤더 · 데이터 이원화 시점 · LLM council 운영 프로토콜.

---
*정본: phase1a/engine/ (forward_runner·multi_anchor_sim·phase1_core_satellite·build_v4_docs) · 산출물 PRAMANA_V4/ · 통합 아카이브 PRAMANA_ARCHIVE/. 근거 원본은 PRAMANA_MASTER_DOSSIER.docx 및 phase1a/reports/.*
