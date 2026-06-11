# PROJECT_STATE — PRAMANA V4
> 현재 상태 스냅샷. **갱신일: 2026-06-12.** 상태가 바뀌면 이 파일부터 갱신. *Codex: 이 날짜가 오늘과 많이 떨어졌으면 먼저 "stale 가능" 경고하고 시작.*
> 정본 locks+근거 = `PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v0.4.md` · 전체 히스토리 = `PRAMANA_ARCHIVE/PRAMANA_MASTER_DOSSIER.docx`

## 한 줄
**최신 = V7 Paper Core Candidate = 4-sleeve** (GPT+Claude 수렴·Codex 검수 SHIP-as-paper/REVISE 반영·RESEARCH_ONLY/PRODUCTION_UNSAFE): Equity 50%(SPY/QQQ) + Managed-Futures 25%(DBMF) + Gold 15%(GLD) + Bonds 10%(IEF)·기본 1.0x. **회피기동 = 코어 대전환(QQQ↔4-sleeve 마켓타이밍·데이터로 짐)이 아니라 구조적 분산(4-sleeve)을 깔고 위험신호 뜨면 *공격 파트만* 끄기(throttle·NEEDS_EVIDENCE).** "Production"은 Promotion Gates(crash-pack+12mo forward+2-feed+attribution+사람 게이트) 통과 후만.
계보: v4(Core Beta) → v5(레버드 베타·QQQ넘김 but 레버지 알파아님·6mo 같이 낙폭) → v6(+managed-futures 분산·낮은 레버) → **v7(4-sleeve 구조분산 코어 + throttle 공격파트만 + Alpha Lab paper + Risk Monitor)**. forward_runner_v7 가동(라이브 2026-06-11·4-sleeve 1.0x). 스펙 PRAMANA_V4/PRAMANA_V7_Plan_v0.2.md. **부정됨(데이터): 코어 regime-switch(switch Sharpe 0.91<static 4-sleeve 1.07·2022 −24% vs −10% 휩쏘).**

## 지금까지 측정된 것 (Evidence)
- 단순 횡단면 팩터(value/momentum/lowvol) = 비용후 net 엣지 없음. quality = 식음(IC-IR 0.22→0.046).
- v3 풀북 = SPY를 어느 horizon도 위험조정으로 못 이김.
- **trend+LETF 위성(고정 70/25/5): unlevered & risk-matched(동일 vol·−35%MDD) 둘 다 기여 ≈ +0.15%/yr = 노이즈** → 알파 아닌 약한 낙폭 도구.
- 파이프라인 검증됨: self-built S&P500 PIT cap-weight vs 실제 SPY corr 0.998.

## 현재 빌드/운영
- `forward_runner.py` 무인 일1회(yfinance·fail-closed·append-only) · 라이브 인셉션 2026-06-09 · `outputs/forward_dashboard.html` live.
- Phase 1(core-satellite) · Phase 1.5(risk-matched) 완료. (`phase1a/engine/phase1_core_satellite.py`, `phase1_5_risk_matched.py`)

## 임시 A1 (확정 아님 — 3 시나리오)
가상 **₩100M · 1~3년 · MDD: Conservative −20% / Aggressive −35%(현 기본값) / Max −50%.**

## v4 빌드 현황 (2026-06-12 완료)
- Production = Core Beta 1.0x(production_book.py·target JSON). **레버는 격리 sleeve·PRODUCTION_UNSAFE**(Codex: −35% 레버=backward knob, shock-replay 전 자본금지). overlay OFF(−0.14%=노이즈).
- Research thread1 mean-reversion = **REJECT**(net −4%·turnover 3660%·Core 한계기여 −0.027). research_meanrev.py.
- forward reconciliation 프레임 = research_meanrev/forward_reconcile.py(stooq 2nd-feed 404→**다른 무료소스 wiring TODO**, 0체크=UNKNOWN 정직보고).
- 대시보드 production_dashboard.html. Codex 2회 REVISE 수용.

## v5 현황 (용하 승인 = 공격적·리스크수용·유연 / Codex 3회 REVISE 수용 → SHIP-as-paper)
- **v5 = Aggressive Leveraged Core Beta Book**(aggressive_book.py·vol-target 28%·캡 2.0x·DD ladder). 정직: 레버드 베타지 알파 아님(no-ruin 아님=손실속도 완화·gap 무력).
- **in-sample(2016-26): +625% > QQQ +539% > SPY +301%·MDD −32%·Sharpe 0.95(≈QQQ)** → 네 공격 바로는 in-sample "이김". 단 알파 아닌 레버·benign 샘플·**forward −70%+ 가능**.
- 정본 = `PRAMANA_V4/PRAMANA_V5_Problem_Frame_v0.2.md`(+ forward 정량 판정표). 대시보드 production_dashboard.html.
- 라벨: RESEARCH_ONLY/PRODUCTION_UNSAFE. live cap 1.25~1.5x(crash-pack 후). 2.0x=paper max.

## v5 forward 배선 완료 (2026-06-12)
- **forward_runner_v5.py = v5 북 실제 무인 forward** (free yfinance·fail-closed·append-only·라이브 인셉션 2026-06-11). cron `0 6 * * 2-6`면 일1회 자동.
- **판정표 자동채점** 내장(상방참여/MDD/레버breach/reconcile/무결성). 워밍 윈도우 현재 상방참여 60%=❌(아직 미달·QQQ에 짐) → 정직히 표기. **라이브 12개월 트랙으로 판정.**
- 대시보드: v5_forward_dashboard.html(라이브)·production_dashboard.html(백테스트)·multi_anchor_v5.html(12/6/3개월 진입).
- multi-anchor: V5가 12mo 진입 QQQ 넘음(+38% vs +31%)·3mo ~동률·6mo 짐(+7.5% vs +11.3%)·세 구간 다 MDD↑·Sharpe<QQQ = 레버드 베타 양면.

## v7 빌드 현황 (2026-06-12 · 최신 · GPT+Claude 수렴 → Codex SHIP-as-paper/REVISE 반영)
- **V7 = Paper Core Candidate(4-sleeve) + Risk Throttle(공격파트만) + Alpha Lab(paper) + Risk Monitor.** 스펙 `PRAMANA_V4/PRAMANA_V7_Plan_v0.2.md`.
- **부정됨(데이터·no-echo):** 코어 regime-switch(QQQ↔4-sleeve 대전환)=마켓타이밍·휩쏘. `regime_switch_test.py`: switch 풀 Sharpe 0.91 < static 4-sleeve 1.07·2022 −24% vs −10%. → **코어는 안 갈아탄다.**
- **4-sleeve 측정(`test_4sleeve.py`·2019-26 비용후):** 풀 +174%/MDD −18%/**Sharpe 1.21**(BEST)·2022 −10%/−12%(vs QQQ −35%)·2023 +18.9%(vs QQQ +55.9%=bull 드래그=보험료). 정직: QQQ bull 수익 ~절반 포기=알파 아니라 *목적함수(크래시생존) 선택*.
- **빌드:** `forward_runner_v7.py`(4-sleeve 1.0x·free yfinance SPY/QQQ/DBMF/GLD/IEF·fail-closed·라이브 인셉션 2026-06-11)+Risk Monitor 점수(200일선/20일vol/DD→Growth/Caution/Defense/Crash·**정보용·자본 자동전환 금지**)·`outputs/v7_forward_dashboard.html`.
- **Codex 검수 VERDICT: SHIP-as-paper plan, REVISE label/gate**(STOP 아님). 6지적 전부 반영: ①"Production"→"Paper Core Candidate"+Promotion Gates ②4-sleeve 수치는 crash-pack 전 ③throttle=NEEDS_EVIDENCE ④paper notional 2~5% ⑤게이트 전 차단(실자본·1.25x·throttle 편입) ⑥승격 판정표 §5b.
- **🔒 Promotion Gates(실자본 전 전부):** crash-pack pass + 12mo forward 판정표 + 2-feed reconciliation + attribution + 사람 자본 게이트.

## 다음 행동
1. **cron 등록 → forward_runner_v7 12개월 무인 가동.** 판정표(§5b) 통과해야 'win'(수익-only 합격 금지).
2. **crash-pack(2000-02·2008·2020·2022·1987 gap):** ① 4-sleeve robustness ② throttle이 static을 *crash-pack서* 이기나 → 이기면 승격, 못 이기면 대시보드 전용. DBMF/GLD/IEF 짧은 역사 → 장기 proxy 필요.
3. **reconciliation 2nd 무료소스 wiring**(stooq 404 → 대체) — 판정표 reconcile 항목 UNKNOWN 해소.
4. (Research·자본권한 0) Alpha Lab(급등주/VWAP/ORB·intraday infra 필요)·brake-only smoothing·event/revision 팩터. *알파는 베타를 못 넘는 패턴 재확인 위.*
5. **behavior 규율(Codex kill): 12mo 전 목표 변경·−30%서 수동 override 금지.**
