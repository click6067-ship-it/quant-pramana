# PRAMANA V4 — LOCK SHEET v0.4 (정본)

> **v0.1~v0.3 대체** (git 보존·이유는 docs/context/DECISION_LOG.md). v0.4 = v0.3 + GPT 추가 refine 5개:
> ① A1 3시나리오화 ② Production = "Core Beta Forward Book"(알파북 아님 명시) ③ Research 1순위 = mean-reversion ④ forward reconciliation ⑤ active/passive 연구 분리.
> **핵심 원칙:** 자본권한은 **엄격**, 연구는 **개방하되 격리.** 융통성 = 바를 낮추는 게 아니라 *상태를 여러 개로 + 비중을 연속적으로.*
> **V1 정밀 교정:** V1은 *연구로선 성공*(가짜 알파 죽임=자산), *수익 포트폴리오로선 실패*(core 부재·기관잣대·이진폐기). → V4는 검증 *약화*가 아니라 **자본권한 엄격 + 연구 개방.**
> 작성 2026-06-12 · **PAPER only / NO LIVE** · V4 = core-satellite 재설계, 내부 v1·v2·v3 = 이전 작업.
> 구성: **A 임시 · B Hard LOCK · C Evidence LOCK · D Research OPEN · E Operating Priors · F 판정라벨/veto · G 데이터 · H 공유기억·운영 · I 빌드현황.**

---

## A. PROVISIONAL — 임시 (3 시나리오 병기, 실제 자본 정해지면 행 선택)
자본 = 가상 ₩100M (이미 hard) · 시계 = **1~3년.** 감내 MDD는 **하나로 박지 않고 3개로** 둔다(GPT) — 단일 −35%가 이미 Production 결정을 끌고 가는 위험 방지:

| 시나리오 | MDD 한도 | 함의 |
|---|---|---|
| Conservative | −20% | Core 비중↓·레버 거의 無·위성=방어 only |
| **Aggressive (현 기본값)** | **−35%** | Core 중심·소폭 레버 허용·위성 선택적 |
| Max Aggressive | −50% | 레버↑·LETF dose↑·큰 변동 감내 |

> 현재 작업 기준 = **Aggressive(−35%).** 실제 운용 규모/성향 정해지면 *락시트 안 뒤엎고* 행만 선택. → 잣대로 "core만 vs core+오버레이"·레버 한도·승격 판정 결정.
> **근거:** 단일 임시값이 전략 선택을 크게 바꾸고 이미 −35%로 흐름. 3행 병기 = 나중에 바로 선택 가능(GPT). Phase 1.5도 −35% 예산으로 측정.

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
- **B12** 거버넌스 = **판정 라벨 + capital/research veto 분리**(F). 모든 전략·후보에 라벨 하나.
- **B13** 기억은 **repo 파일에 고정**(AGENTS.md/CLAUDE.md → docs/context/*). 대화 기억 의존 금지(H).

> **근거:** B4=Codex가 v3 same-close 누수 발견. B5=v3서 trend가 벌고 equity 희석을 전체성과론 못 잡음→자기기만 방지. B6/B7=LEAN/Nautilus 권한골격+LLM 트레이딩 벤치(직접매매 비용후 알파 0). B8=DeMiguel 2009. B11=SEC market-access·FINRA 15-09.

---

## C. EVIDENCE LOCK — 측정된 사실만 (좁게, 재논쟁은 새 데이터로만)
- **C1** 고정 70/25/5 *unlevered* trend+LETF 위성 = core 대비 수익 못 보탬 (Phase 1: 풀사이클 −41%p·MDD −3%p·Sharpe 0.95→0.98).
- **C2** **risk-matched(동일 vol·동일 −35%MDD) *공정* 재검증해도 위성 기여 = +0.15%p/yr ≈ 노이즈** (Phase 1.5). → 드래그도 엣지도 아님. *양쪽 테스트=false-negative 아님.*
- **C3** v3 풀북 = SPY를 어느 horizon도 위험조정으로 못 이김 (풀사이클 3x +699% vs SPY +307%는 레버지 엣지 아님·Sharpe 0.82<0.90).
- **C4** 단순 횡단면 팩터(value/momentum/lowvol) net 엣지 없음(IC≈0). quality는 보였다(IC-IR 0.22) 최근 절반 식음(0.046)·long-only<cap-weight.
- **C5** 파이프라인 정확 — self-built S&P500 PIT cap-weight vs 실제 SPY **corr 0.998.**
- **C6 (신규 명시)** **Core(SPY/QQQ)가 SPY를 이긴 건 QQQ/기술주 틸트(레짐)지 알파 아님** — 2016-26 메가캡·기술주 우위 구간 산물. → Production을 "알파"로 착각 금지(B2·I 참조).

> **근거:** 전부 phase1a 코드 측정. **측정됐으므로 가장 강한 락. 단 "그래서 알파 영영 없다"로 일반화 금지 — 그건 E(prior).**

---

## D. RESEARCH OPEN — 자본권한 0으로 살아있음 (알파 놓칠라 걱정의 안전장치)
**원칙: 높은 기대치 = 연구 금지 아님 = production *승격 기준*이 높다는 뜻.**

**Alpha Candidate Registry 파이프:** `등록 → 싸고 빠른 1차 스크린 → Paper Sandbox(자본 0) → Attribution(core 대비 한계기여) → OOS·비용후 → Promotion Review → Production Candidate`

**열어두는 후보(우선순위순):**
1. **mean-reversion ★1순위** — 미탐색·Parker 전향 방향. *trend/LETF가 알파가 아니라면(C1·C2), 다음은 같은 방향 trend 변형이 아니라 trend 약한 chop장(2011-21)에서 먹힐 *반대 성격* 전략이다.* (단 같은 brutal 바·게이트 적용 — 1순위지 "통과 보장" 아님.)
2. **quality 레짐 retest** — 이미 식은 흔적(C4)→1순위보다 뒤. 어느 레짐서 core와 무상관 기여했나.
3. trend/LETF overlay variant (C1/C2는 *고정 70/25/5*만 부정).
4. adaptive allocator(고정비중 OOS 못 이기면 폐기).
5. 기관 slow-tilt(13F 45일 지연=느린 bias).
6. intraday lab(paper-only·capital 침범 금지).
7. TSFM/DL/LLM 보조(meta-labeler/scanner/sentiment).

**거버넌스 게이트(Research→Production):** 사전등록 kill · 비용후 · OOS · attribution · risk-veto 통과 → *Production Candidate*, 그 다음에야 사람 자본 게이트.

> **refine (합의):**
> ① **2층 구조** — **Active Research = 1개만**(분석·판단 = 과적합 위험 지점, 한 스레드씩) + **Passive Data Collection = 병렬 OK**(sentiment·기관·intraday 데이터를 *수집만*, 판단 X). 분석 5개 병렬 = V1 paralysis 복귀지만, *데이터 축적*은 병렬 무해. **단 수집 데이터를 몰래 마이닝 금지 — 분석은 active 스레드에서만.**
> ② **TSFM/DL은 열되 저우선·고바**(증거 강하게 불리 — 단순법보다 높은 바, 우선순위 맨 뒤).
> ③ **fair-reframe(risk-matched 등)는 OK, config-mining(변형 N개 난사)은 사전등록으로 차단.**

> **근거(false-negative 해소):** 신호 놓침의 치료약은 *바 낮추기가 아니라 결정과 증거축적 분리* — 후보를 paper로 살려 데이터·forward 증거 쌓으면 진짜-작은/레짐의존은 드러나고 가짜는 평평. Phase 1.5가 위성을 *공정히* 재검증한 게 실증.

---

## E. OPERATING PRIORS — 락 아님 = *기대치*(모든 후보가 싸울 높은 바)
- **E1** *지금까지 검증한* 단순팩터·v3 풀북·고정 trend/LETF엔 비용후 강건 알파 미확인 → 신규 후보는 강한 회의 prior와 싸움. 단 "영영 없다"는 *닫는 결론 금지.*
- **E2** trend/momentum = 쇠퇴·레짐의존·대부분 크래시보험(CTA 잃어버린 10년·McLean-Pontiff 발표후 −58%) → 추세 = *리스크 도구.*
- **E3** 레퍼 = 부품 창고지 전략 쇼핑몰 아님. 레퍼는 V4 *리스크 구조*는 지지하나 *알파*는 검증 못 함(시대·스케일 의존).
- **E4** 알파는 책·레퍼에 없다(있었으면 차익거래로 소멸) → 남은 오라클 = 시장(forward paper).

> **근거:** E를 C와 분리하는 게 핵심. v0.1은 prior를 LOCK으로 박아 연구를 닫음 = V1 과폐기 반대방향 반복. prior는 기대치를 높이지 탐색을 금지하지 않는다.

---

## F. 판정 라벨 & VETO (거버넌스 기계)
**모든 전략·후보에 라벨 하나:** `LOCK` · `RESEARCH_ONLY` · `REJECT` · `NEEDS_EVIDENCE` · `PRODUCTION_SAFE` · `PRODUCTION_UNSAFE`
- **capital-veto ≠ research-veto 분리** — `PRODUCTION_UNSAFE`라도 `RESEARCH_ONLY`로 살릴 수 있음(VRP = MDD −92%라 PRODUCTION_UNSAFE지만 tail-hedge 변형 *연구*는 허용).
- **기본값 = PRODUCTION_UNSAFE**(증거 불완전 시). "죽은 전략 살리기"가 아니라 *죽은 이유 분류*(비용 전에도 음수 reversal류 = REJECT, 식은 quality = NEEDS_EVIDENCE).

> **근거:** V1 이진(통과/폐기)이 너무 경직→좋은 후보까지 죽임. 6라벨 = 융통성의 *구조적* 형태(바 낮추기 아님).

---

## G. DATA SOURCES & FORWARD 신뢰도
- **Research/backtest primary = Sharadar**(유료·PIT·survivorship·CA).
- **Forward paper = yfinance 무료 EOD**(임시·무인 데모. Sharadar lapse 대비).
- **실자본 전 = 2 독립 피드 + 브로커 대조**(무료 단일은 레버 실자본 부적합 — 조정오류 1건이 신호 뒤집음).
- **Forward reconciliation 필수 (신규)** — forward가 곧 미래 판단 근거가 되므로 단일 무료피드는 약함. forward_runner는: ① yfinance NAV ② **2번째 무료소스(stooq) sanity diff = 상시 cross-check**(데이터 오류 즉시 감지) ③ **Sharadar 구독 윈도우 때 같은 기간 EOD 재계산 NAV + diff reconciliation log**(주기적). → 실거래 아니어도 "forward 좋았나/나빴나" 판단의 데이터 무결성 확보.

> **근거(GPT):** forward track이 판단 근거면 데이터 오류 논란 방지 필요. *Claude 실무 단서: Sharadar는 lapse하므로 상시 reconciliation은 2번째 무료소스로, Sharadar 대조는 구독 윈도우 때 주기적으로.*

---

## H. 공유 기억 & 운영
- **Codex/Claude 공유 기억:** `AGENTS.md`(Codex)·`CLAUDE.md`(Claude)가 `docs/context/{PROJECT_STATE,LOCKS,ADVERSARIAL_COUNSEL,DECISION_LOG}.md`를 매번 읽음. 대화 기억 의존 X.
- **적대 카운슬:** `./council.sh "질문"` — 현재 STATE+LOCKS 자동 주입·web_search·결과 저장.
- **갱신 규율(staleness 방지·유일한 실패점):** 상태 바뀌면 `PROJECT_STATE.md` + `DECISION_LOG.md`만. **rationale는 이 락시트 한 곳에만**. PROJECT_STATE 날짜 오래되면 Codex가 먼저 경고.
- **forward 운영:** `forward_runner.py` 무인 일1회·fail-closed·append-only·look-ahead 없음. GPU/클라우드 불필요(CPU·ML 미사용).

---

## I. BUILD STATUS & 다음 (2026-06-12 — "v4 build complete; alpha research open & capital-isolated")
- ✅ Phase 1·1.5 · 공유 기억 체계 · Codex 2회 REVISE 수용.
- ✅ **Production = Core Beta 1.0x** (production_book.py·target JSON). 정직 명명: 베타북, NOT 알파(Core>SPY=QQQ 틸트, C6). **레버는 격리 sleeve·PRODUCTION_UNSAFE**(Codex: −35% 레버=backward knob지 risk cap 아님 → shock-replay[2018Q4/2020/2022]+gross-lev cap+financing+gap stress+fail-closed 고정 전 자본 금지). overlay OFF(−0.14%=노이즈).
- ✅ **Research thread1 mean-reversion = REJECT** (research_meanrev.py·net −4%·turnover 3660%·IC-IR 0.002·Core 한계기여 −0.027). 리서치 기계 정상작동(사전등록 kill·정직 negative). Codex가 kill 6개 추가 권고(net≤레버없는Core·tail집중·chop사후·half-life·2x비용·episode집중) → MR 변형 재시도 시 적용.
- ✅ forward reconciliation 프레임(forward_reconcile.py) — stooq 404 → **2nd 무료소스 wiring TODO**, 0체크=UNKNOWN 정직보고. ✅ 대시보드 production_dashboard.html.
- ⚠️ **3개월 sim: Core Beta +10.9% > SPY +7.6%, QQQ +14.3%엔 짐** → 사용자 directive(SPY·QQQ 둘 다 못넘으면 재정의)대로 **v5 재정의 트리거.**
- ▶ **v5 = Aggressive Leveraged Core Beta Book** (용하 승인: 공격·리스크수용·유연 / Codex 3회 REVISE → SHIP-as-paper) → `PRAMANA_V4/PRAMANA_V5_Problem_Frame_v0.2.md`. in-sample 2016-26 +625% > QQQ +539%(beat!) but **레버지 알파 아님(Sharpe≈QQQ)·MDD −32% benign-conditional·forward −70%+ 가능.** RESEARCH_ONLY·live cap 1.25~1.5x(crash-pack 후). **다음 = forward 12개월 사전등록 판정표**(수익-only 합격 금지). 베타북은 QQQ를 알파로 못 넘음=설계상; 레버로 넘긴 것.

> **한 줄:** V4 = **유연한 연구 + 엄격한 자본권한.** Production = 정직한 Core Beta Forward Book(단순·단단), Research = 격리·개방(후보 살려 증거축적), 승격 천천히, 비중 연속, 변경은 attribution 근거로.

---
*정본 코드: phase1a/engine/ · 산출물 PRAMANA_V4/ · 근거 PRAMANA_MASTER_DOSSIER.docx + phase1a/reports/ · 공유기억 docs/context/. v0.1~v0.3 superseded(git).*
