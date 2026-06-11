# PRAMANA V4 — LOCK SHEET v0.3 (정본)

> **v0.1/v0.2 대체** (git에 보존·이유는 docs/context/DECISION_LOG.md). 이번 통합 = GPT 2라운드 비판 + Claude refine + 용하 확인 + Phase 1.5 + 판정라벨·공유기억 체계.
> **핵심 원칙:** 자본권한은 **엄격**, 연구는 **개방하되 격리.** 융통성 = 바를 낮추는 게 아니라 *상태를 여러 개로 + 비중을 연속적으로.*
> **V1 정밀 교정(GPT):** V1은 *연구 시스템으로선 성공*(가짜 알파 잘 죽임 = 자산), *수익 포트폴리오로선 실패*(core 부재·기관잣대·이진폐기·강세장 못 따라감). → V4는 검증을 *약화*하는 게 아니라 **자본권한 엄격 + 연구 개방.**
> 작성 2026-06-12 · **PAPER only / NO LIVE** · V4 = core-satellite 재설계, 내부 v1·v2·v3 = 이전 작업.
> 구성: **A 임시 · B Hard LOCK · C Evidence LOCK · D Research OPEN · E Operating Priors · F 판정 라벨/veto · G 데이터 · H 공유기억·운영 · I 빌드현황.**

---

## A. PROVISIONAL — 임시 확정 (흔들림 방지, 언제든 덮어쓰기)
- 자본 = 가상 ₩100M (이미 hard) · 시계 = **1~3년** · 감내 **MDD X = −35%.**
- → 이 잣대로 "core만 vs core+가벼운 오버레이"·레버 한도·승격 판정 전부 결정. *확정 아님 — 실제 규모/성향 정해지면 갱신.*

> **근거:** 임시값 없으면 모든 후속 선택이 계속 흔들림(GPT). −35% = 공격형이되 파산 회피 가능선(Phase 1.5도 −35% 예산으로 측정).

---

## B. HARD LOCK — 절대 안 바꿈
- **B1** PAPER only / NO LIVE · 가상 ₩100M · US 주식·ETF only · crypto 제외.
- **B2** **Core-satellite** — SPY/QQQ 코어 기본 + 위성은 *core 대비 비용후 한계기여* 있을 때만. "SPY 버리고 이기기" 금지.
- **B3** 목적함수 = **max 초과수익 over core, s.t. MDD ≤ X.** 생존=제약, 수익=목적.
- **B4** **next-bar 실행**(신호 t → 진입 t+1). same-close 금지.
- **B5** **Attribution 필수** — core/위성/allocator/intraday 손익 분해.
- **B6** **결정적 risk engine = 최종 veto.** 신호≠주문 · 알파≠포지션.
- **B7** **LLM/TSFM 직접 트레이딩 금지**(주문·비중·종목·risk veto 해제·live config 변경 불가, off-path 보조만).
- **B8** **단순 baseline 우선** — 복잡 모델/allocator는 1/N·고정비중을 OOS 비용후 이겨야 채택.
- **B9** Production = **일봉.** (분봉은 Research sandbox만 — D 참조.)
- **B10** 데이터 무결성(PIT·survivorship·CA·fail-closed). 실자본 전 2 독립 피드 + 브로커 대조.
- **B11** **사람이 자본 게이트** — 자본 증액·코드 live 반영·리스크한도·벤더 변경·kill 후 재시작 = 인간 승인.
- **B12 (신규) 거버넌스 = 판정 라벨 + capital/research veto 분리** (F 참조). 모든 전략·후보에 라벨 하나 부여.
- **B13 (신규) 기억은 repo 파일에 고정** — AGENTS.md/CLAUDE.md → docs/context/*. 대화 기억 의존 금지(H 참조).

> **근거:** B4 = Codex가 v3 same-close 누수 발견. B5 = v3서 trend가 벌고 equity가 희석을 전체성과론 못 잡음 → 자기기만 방지. B6/B7 = LEAN/Nautilus 권한 골격 + LLM 트레이딩 벤치(직접매매 비용후 알파 0). B8 = DeMiguel 2009. B11 = SEC market-access·FINRA 15-09 + 솔로 무책임. B13 = Codex stateless → 붙여넣기 비효율, 파일 고정이 정답.

---

## C. EVIDENCE LOCK — 측정된 사실만 (좁게, 재논쟁은 새 데이터로만)
- **C1** 고정 70/25/5 *unlevered* trend+LETF 위성 = core 대비 수익 못 보탬 (Phase 1: 풀사이클 −41%p·MDD −3%p·Sharpe 0.95→0.98).
- **C2** **risk-matched(동일 vol·동일 −35%MDD)로 *공정* 재검증해도 위성 기여 = +0.15%p/yr ≈ 노이즈** (Phase 1.5). → 드래그도 엣지도 아님. *양쪽 테스트 = false-negative 아님.*
- **C3** v3 풀북 = SPY를 어느 horizon(3M/6M/1Y/풀)도 위험조정으로 못 이김 (풀사이클 3x +699% vs SPY +307%는 레버지 엣지 아님·Sharpe 0.82<0.90).
- **C4** 단순 횡단면 팩터(value/momentum/lowvol) net 엣지 없음(IC≈0). quality는 broad서 보였다(IC-IR 0.22) 최근 절반 식음(0.046)·long-only<cap-weight.
- **C5** 파이프라인 정확 — self-built S&P500 PIT cap-weight vs 실제 SPY **corr 0.998.**

> **근거:** 전부 phase1a 코드 측정(phase1_core_satellite·phase1_5_risk_matched·multi_anchor_sim·B2B5/B3·B0broad). **측정됐으므로 가장 강한 락. 단 "그래서 알파 영영 없다"로 일반화 금지 — 그건 E(prior).**

---

## D. RESEARCH OPEN — 자본권한 0으로 살아있음 (네 "알파 놓칠라" 걱정의 안전장치)
**원칙: 높은 기대치 = 연구 금지 아님 = production *승격 기준*이 높다는 뜻.**

**Alpha Candidate Registry 파이프 (모든 후보 동일 경로):**
`등록 → 싸고 빠른 1차 스크린 → Paper Sandbox(자본 0) → Attribution(core 대비 한계기여) → OOS·비용후 → Promotion Review → Production Candidate`

**열어두는 후보(우선순위순):** ① quality 레짐 retest · ② **mean-reversion**(미탐색·Parker 전향 방향·chop장서 trend 보완) · ③ trend/LETF overlay variant(C1/C2는 *고정 70/25/5*만 부정) · ④ adaptive allocator(고정비중 OOS 못 이기면 폐기) · ⑤ 기관 slow-tilt(13F 45일 지연=느린 bias) · ⑥ intraday lab(paper-only·capital 침범 금지) · ⑦ TSFM/DL/LLM 보조(meta-labeler/scanner/sentiment).

**거버넌스 게이트(Research→Production):** 사전등록 kill · 비용후 · OOS · attribution · risk-veto 통과 → *Production Candidate*, 그 다음에야 사람 자본 게이트.

> **Claude refine (합의):** ① **순차·예산제한** — research도 한 번에 한 스레드(production forward 도는 동안). 5개 병렬 = V1 paralysis가 연구 옷 입고 복귀. *시간·집중이 솔로의 최희소 자원.* ② **TSFM/DL은 열되 저우선·고바**(증거가 강하게 불리 — 단순법보다 높은 바, 우선순위 맨 뒤). ③ **fair-reframe(risk-matched 등)는 OK, config-mining(변형 N개 난사)은 사전등록으로 차단.**

> **근거(false-negative 해소):** 진짜 신호 놓침의 치료약은 *바 낮추기가 아니라 결정과 증거축적 분리* — 후보를 paper로 살려 데이터·forward 증거 쌓으면 진짜-작은/레짐의존은 드러나고 가짜는 평평. research 트랙 = anti-false-negative 기계. (Phase 1.5가 위성을 *공정히* 살려 재검증한 게 그 실증.)

---

## E. OPERATING PRIORS — 락 아님 = *기대치*(모든 후보가 싸울 높은 바)
- **E1** *지금까지 검증한* 단순팩터·v3 풀북·고정 trend/LETF엔 비용후 강건 알파 미확인 → 신규 후보는 강한 회의 prior와 싸움. 단 "영영 없다"는 *닫는 결론 금지.*
- **E2** trend/momentum = 쇠퇴·레짐의존·대부분 크래시보험(CTA 잃어버린 10년·McLean-Pontiff 발표후 −58%) → 추세 = *리스크 도구*로 기대.
- **E3** 레퍼 = 부품 창고지 전략 쇼핑몰 아님 — 역할당 검증된 부품 하나, baseline 이겨야. 레퍼는 V4 *리스크 구조*는 지지하나 *알파*는 검증 못 함(시대·스케일 의존).
- **E4** 알파는 책·레퍼에 없다(있었으면 차익거래로 소멸) → 남은 오라클 = 시장(forward paper).

> **근거:** E를 C(Evidence)와 분리하는 게 v0.2→v0.3 핵심. v0.1은 prior를 LOCK으로 박아 연구를 닫음 = V1 과폐기를 반대 방향 반복. prior는 기대치를 높이지(가짜 차단), 탐색을 금지하지 않는다.

---

## F. 판정 라벨 & VETO (거버넌스 기계 · 신규 명시)
**모든 전략·후보에 라벨 하나:** `LOCK` · `RESEARCH_ONLY` · `REJECT` · `NEEDS_EVIDENCE` · `PRODUCTION_SAFE` · `PRODUCTION_UNSAFE`
- **capital-veto ≠ research-veto 분리** — `PRODUCTION_UNSAFE`라도 `RESEARCH_ONLY`로 살릴 수 있음 (예: VRP short-vol = MDD −92%라 PRODUCTION_UNSAFE지만 tail-hedge 변형 *연구*는 허용).
- **기본값 = PRODUCTION_UNSAFE** (증거 불완전 시). "죽은 전략 살리기"가 아니라 *죽은 이유 분류*(비용 전에도 음수인 reversal류 = REJECT, 식은 quality = NEEDS_EVIDENCE).

> **근거:** V1의 이진(통과/폐기)이 너무 경직 → 좋은 후보까지 죽임. 6라벨 = 융통성의 *구조적* 형태(바 낮추기 아님).

---

## G. DATA SOURCES (v0.1 충돌 해소)
- **Research/backtest primary = Sharadar**(유료·PIT·survivorship·CA).
- **Forward paper = yfinance 무료 EOD**(임시·무인 데모·sanity. Sharadar lapse 대비).
- **실자본 전 = 2 독립 피드 + 브로커 대조**(무료 단일은 레버 실자본 부적합 — 조정오류 1건이 신호 뒤집음).

---

## H. 공유 기억 & 운영 (신규)
- **Codex/Claude 공유 기억:** `AGENTS.md`(Codex)·`CLAUDE.md`(Claude)가 `docs/context/{PROJECT_STATE,LOCKS,ADVERSARIAL_COUNSEL,DECISION_LOG}.md`를 매번 읽음. 대화 기억 의존 X.
- **적대 카운슬:** `./council.sh "질문"` — 현재 STATE+LOCKS 자동 주입(붙여넣기 불필요)·web_search·결과 저장.
- **갱신 규율(staleness 방지·유일한 실패점):** 상태 바뀌면 `PROJECT_STATE.md` + `DECISION_LOG.md`만. **rationale는 이 락시트 한 곳에만**(중복 금지). PROJECT_STATE 날짜 오래되면 Codex가 먼저 경고.
- **forward 운영:** `forward_runner.py` 무인 일1회(미국 장마감 후)·fail-closed·append-only·look-ahead 없음. GPU/클라우드 불필요(CPU·ML 미사용).

---

## I. BUILD STATUS & 다음
- ✅ Phase 1(Core+trend+LETF+고정 allocator+attribution) — 위성=알파 아님(C1).
- ✅ Phase 1.5(risk-matched) — 위성 +0.15%/yr=노이즈(C2), *공정 확인.*
- ✅ 공유 기억 체계(AGENTS/CLAUDE/docs-context/council.sh) — 커밋·푸시 완료.
- ▶ **다음 = A1(−35%)로 Production 결정 → forward:** Phase 1.5서 −35%에 Core 20.25%·CoreSat 20.40%(거의 동일·위성 노이즈) → **Production = Core(SPY/QQQ) 중심 + 위성은 *선택적* 가벼운 오버레이.** forward 투입.
- ▶ **Research 첫 스레드 1개** = mean-reversion 또는 quality 레짐 retest (한 개·forward 도는 동안).

> **한 줄:** V4 = **유연한 연구 + 엄격한 자본권한.** Production 단순·단단(Core forward), Research 격리·개방(후보 살려 증거축적), 승격 천천히, 비중 연속, 변경은 attribution 근거로.

---
*정본 코드: phase1a/engine/ · 산출물 PRAMANA_V4/ · 근거 원본 PRAMANA_MASTER_DOSSIER.docx + phase1a/reports/ · 공유기억 docs/context/. v0.1·v0.2 superseded(git).*
