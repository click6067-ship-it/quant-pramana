# PRAMANA V4 — LOCK SHEET v0.2

> **v0.1을 대체.** 핵심 변경 = **Production(엄격) / Research(개방)** 분리. v0.1이 Phase 1 실망 때문에 *연구 가능성까지* 너무 빨리 닫은 걸 교정.
> 원칙: **자본권한은 엄격, 연구는 열어두되 격리.** 융통성 = 바를 낮추는 게 아니라 *상태를 여러 개로 + 연속적으로.*
> 작성 2026-06-12 · 상태 **PAPER only / NO LIVE** · 명명: V4 = core-satellite 재설계, 내부 v1·v2·v3 = 이전 작업.
> 구조: **① Hard LOCK(불변) · ② Evidence LOCK(측정된 사실만 좁게) · ③ Research OPEN(자본권한 없이 살아있음) · ④ Provisional(임시) · ⑤ Operating Priors(락 아님).**

---

## ④ PROVISIONAL — 임시 확정 (흔들림 방지용, 용하가 언제든 덮어쓰기)

- **자본:** 가상 ₩100M (이미 hard).
- **시계:** 1~3년.
- **감내 MDD: X = −35%.**
- → 이 임시값으로 잣대가 선다. "core만 vs core+가벼운 오버레이" 결정·레버 한도·승격 판정 전부 −35% 기준. **확정 아님 — 진짜 운용 규모/성향 정해지면 갱신.**

> **근거:** "임시값이라도 없으면 모든 후속 선택이 계속 흔들린다"(GPT). −35%는 공격형이되 파산 회피 가능한 현실선(Phase 1.5도 −35% 예산으로 측정). 1~3년 = 추세/팩터가 레짐 한 바퀴 도는 최소 시계.

---

## ① HARD LOCK — 절대 안 바꿈

- **H1** PAPER only / NO LIVE. 가상 ₩100M. US 주식·ETF only. crypto 제외.
- **H2** **Core-satellite.** SPY/QQQ 코어 기본 + 위성은 코어 위에 *비용후 한계기여* 있을 때만. "SPY 버리고 이기기" 금지.
- **H3** 목적함수 = **maximize 초과수익 over core, s.t. MDD ≤ X.** 생존=제약, 수익=목적.
- **H4** **next-bar 실행** (신호 t → 진입 t+1). same-close 금지.
- **H5** **Attribution 필수** — core/위성/allocator/intraday 손익 분해. "누가 벌었나" 항상 분리.
- **H6** **결정적 risk engine = 최종 veto.** 신호≠주문·알파≠포지션.
- **H7** **LLM/TSFM 직접 트레이딩 금지** — 주문·종목선택·비중·risk veto 해제·live config 변경 불가.
- **H8** **단순 baseline이 복잡성보다 먼저.** 복잡한 모델/allocator는 고정비중·1/N을 OOS 비용후 이겨야 채택.
- **H9** **Production = 일봉.** (분봉은 Research sandbox서만 — H 아님, ③ 참조.)
- **H10** **데이터 무결성** — PIT·survivorship·CA·fail-closed 가드. 실자본 전 2 독립 피드 + 브로커 대조.
- **H11** **사람이 자본 게이트.** 자본 증액·코드 live 반영·리스크한도·벤더 변경·kill 후 재시작 = 인간 승인.

> **근거:** H4 = Codex가 v3서 same-close 누수 발견(look-ahead 최빈 함정). H5 = v3서 trend가 벌고 equity가 희석한 걸 전체성과만 봐선 못 잡음 → 자기기만 방지. H6/H7 = LEAN/Nautilus 권한 골격 + LLM 트레이딩 벤치(StockBench/FINSABER) "직접매매 비용후 알파 0". H8 = DeMiguel 2009(14개 최적화 중 1/N 못 이긴 것 없음). H11 = SEC market-access·FINRA 15-09 + 솔로엔 독립 리스크데스크 없음 → 레버 자율 무책임.

---

## ② EVIDENCE LOCK — 측정된 사실만 (좁게)

- **E1** **고정 70/25/5 *unlevered* trend+LETF 위성은 core 대비 수익을 못 보탰다** (Phase 1: 풀사이클 −41%p 누적·MDD −3%p·Sharpe 0.95→0.98).
- **E2** **risk-matched(동일 vol·동일 −35% MDD)로 *공정하게* 재검증해도 위성 기여 = +0.15%p/yr ≈ 노이즈** (Phase 1.5). → 위성은 드래그도 아니지만 *확인된 엣지도 아님.* 양쪽으로 테스트함 = false negative 아님.
- **E3** **v3 풀북은 SPY를 어느 horizon(3M/6M/1Y/풀)에서도 위험조정으로 못 이김** (풀사이클 3x +699% vs SPY +307%는 레버지 엣지 아님·Sharpe 0.82<0.90).
- **E4** **단순/선형 횡단면 팩터(value/momentum/lowvol)는 비용후 강건한 net 엣지 없음**(IC≈0). quality는 broad서 보였다(IC-IR 0.22) **최근 절반 식음**(0.046)·long-only<cap-weight.
- **E5** **파이프라인은 정확** — self-built S&P500 PIT cap-weight가 실제 SPY와 **corr 0.998.**

> **근거:** 전부 phase1a 코드로 측정 — phase1_core_satellite.py(E1)·phase1_5_risk_matched.py(E2)·multi_anchor_sim.py(E3)·B2B5_broad/B3_quarantine(E4)·B0broad(E5). **이게 Evidence LOCK인 이유 = 측정됐으므로 가장 강함. 단 "그래서 알파는 영영 없다"로 일반화 금지(그건 ⑤ prior).**

---

## ③ RESEARCH OPEN — 자본권한 없이 살아있음 (네 알파 걱정의 안전장치)

**원칙: 높은 기대치 = 연구 금지 아님 = production *승격 기준*이 높다는 뜻.** 좋은 아이디어 안 버림, 근데 바로 자본 안 줌.

**Alpha Candidate Registry 파이프라인 (모든 후보 동일 경로):**
`등록 → 싸고 빠른 1차 스크린 → Paper Sandbox(자본 0) → Attribution(core 대비 한계기여) → OOS·비용후 → Promotion Review → Production Candidate`

**열어두는 후보(우선순위순):**
1. **quality 레짐 retest** — 식었지만 value/quality 레짐서 부활 가능(E4). 어느 레짐서 core와 무상관 기여했나.
2. **mean-reversion** — *미탐색.* Parker가 전향한 방향, 추세 죽는 chop장서 작동 가능. (회의가 찾아낸 disconfirming 단서.)
3. **trend/LETF overlay variant** — 100% core 위 작은 overlay, adaptive 게이팅 등(E1/E2는 *고정 70/25/5*만 부정).
4. **adaptive allocator** — trend strength×inv-vol, 단 고정비중 OOS 못 이기면 폐기.
5. **기관 slow-tilt** — 13F/ETF flow(45일 지연=느린 bias, entry 아님).
6. **intraday lab** — VWAP/ORB/RVOL, paper-only·capital 침범 금지·gross−비용 분해.
7. **TSFM/DL/LLM 보조** — meta-labeler/scanner/sentiment regime feature.

**거버넌스(Research→Production 통과 조건):** 사전등록 kill · 비용후 · OOS · attribution(core 대비 한계기여) · risk-veto. 통과해야 *Production Candidate*, 그 다음에야 사람 자본 게이트.

> **내 refine (회의 합의):**
> - **순차·예산제한.** research도 *한 번에 한 스레드*(production이 forward 도는 동안). 5개 병렬 = V1 analysis-paralysis가 연구 옷 입고 복귀. *시간·집중이 솔로의 최희소 자원.*
> - **TSFM/DL는 열되 저우선·고바.** 증거가 강하게 불리(자유도·비정상성·SNR·마이크로캡 집중) → 단순법보다 *높은* 바, 우선순위 맨 뒤(수익 base 생긴 뒤).
> - **fair-reframe(예: risk-matched)는 OK, config-mining(변형 N개 난사)은 사전등록으로 차단.**

> **근거:** GPT — "forward gap 보일 때만 연구"하면 알파 탐색이 멈추고 V4가 SPY/QQQ 대시보드로 쪼그라듦. 자본 금지 ≠ 연구 금지. + 네 우려(진짜 신호 놓침=Type II): 해결은 바 낮추기가 아니라 *결정과 증거축적 분리* — 후보를 paper로 살려 데이터·forward 증거를 쌓으면 진짜-작은/레짐의존 신호는 드러나고 가짜는 평평. research 트랙이 곧 anti-false-negative 기계.

---

## ⑤ OPERATING PRIORS — 락이 아니라 *기대치* (모든 후보가 싸워야 할 높은 바)

- **P1** *지금까지 검증한* 공개 레퍼 단순팩터·v3 풀북·고정 trend/LETF에선 비용후 강건한 알파 미확인. → **신규 후보는 강한 회의 prior와 싸워야**(쉽게 통과시키지 말 것). 단 "영영 없다"는 *닫는 결론 금지.*
- **P2** trend/momentum = 쇠퇴·레짐의존·대부분 크래시보험(CTA 잃어버린 10년·McLean-Pontiff 발표후 −58%). 추세는 *수익 엔진 아니라 리스크 도구*로 기대.
- **P3** 레퍼 = 부품 창고지 전략 쇼핑몰 아님 — 역할당 검증된 부품 하나, baseline 이겨야. 레퍼는 V4 *리스크 구조*는 지지하나 *알파*는 검증 못 함(시대·스케일 의존).
- **P4** 알파는 책·레퍼에 없다(있었으면 차익거래로 소멸) → 남은 오라클 = 시장(forward paper).

> **근거:** ⑤를 ②(Evidence LOCK)와 분리하는 게 v0.2의 핵심. v0.1은 prior("쉬운 알파 없다")를 LOCK으로 박아 연구를 닫았다 = V1의 과폐기를 *반대 방향으로* 반복. prior는 기대치를 높이지(가짜 차단), 탐색을 금지하지 않는다.

---

## DATA SOURCES (정리 — v0.1 충돌 해소)

- **Research/backtest primary = Sharadar** (PIT·survivorship·CA, 유료).
- **Forward paper = yfinance 무료 EOD** (임시·무인 데모·sanity용. Sharadar 구독 lapse 대비).
- **실자본 전 = 2 독립 피드 + 브로커 대조** (무료 단일은 레버 실자본 부적합 — 조정오류 1건이 신호 뒤집음).

---

## BUILD STATUS & 다음

- ✅ **Phase 1**(Core+trend+LETF+고정 allocator+attribution) — 완료. 위성=알파 아님(E1).
- ✅ **Phase 1.5**(risk-matched) — 완료. 위성 +0.15%/yr=노이즈(E2). *공정하게* 확인.
- ▶ **다음 = A1 임시값(④)으로 Production 결정 → forward 투입:** Phase 1.5에서 Core·CoreSat이 −35%서 거의 동일(20.25 vs 20.40%) → **Production = Core(SPY/QQQ) 중심, 위성은 ~노이즈라 *선택적 가벼운 오버레이*.** 그걸 forward로.
- ▶ **Research 첫 스레드 = mean-reversion 또는 quality 레짐 retest** (한 개만, forward 도는 동안).

> **요약 한 줄:** V4 = **유연한 연구 + 엄격한 자본권한.** Production은 단순·단단(Core 중심 forward), Research는 격리·개방(후보 살려 증거축적), 승격은 천천히(게이트 통과), 비중은 연속적으로, 변경은 attribution 근거로.

---
*정본 코드: phase1a/engine/ · 산출물 PRAMANA_V4/ · 통합 PRAMANA_ARCHIVE/ · 근거 원본 PRAMANA_MASTER_DOSSIER.docx + phase1a/reports/. v0.1 superseded.*
