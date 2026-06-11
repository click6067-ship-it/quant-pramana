# PROJECT_STATE — PRAMANA V4
> 현재 상태 스냅샷. **갱신일: 2026-06-12.** 상태가 바뀌면 이 파일부터 갱신. *Codex: 이 날짜가 오늘과 많이 떨어졌으면 먼저 "stale 가능" 경고하고 시작.*
> 정본 locks+근거 = `PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v0.4.md` · 전체 히스토리 = `PRAMANA_ARCHIVE/PRAMANA_MASTER_DOSSIER.docx`

## 한 줄
core-satellite 재설계(V4). **v4 build complete; alpha research open & capital-isolated**(Codex 표현). Production = Core Beta Forward Book(SPY/QQQ 1.0x·*베타*지 알파 아님). 확인된 알파 위성 *없음*(MR thread1 REJECT).
**⚠️ 3개월 sim: Core Beta +10.9% > SPY +7.6%, but QQQ +14.3%엔 짐 → 사용자 directive(SPY·QQQ 둘 다 못넘으면 재정의)대로 v5 재정의 진행중.**

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

## 다음 행동
1. **cron 등록 → forward 12개월 무인 가동.** 판정표 통과해야 'win'(수익-only 합격 금지).
2. **reconciliation 2nd 무료소스 wiring**(stooq 404 → 대체) — 판정표 reconcile 항목 UNKNOWN 해소.
3. 알파 research(유료 Sharadar 사용): thread1 MR=REJECT(turnover 3660%)·thread2 quality 레짐=**NEEDS_EVIDENCE → 사실상 not-candidate**(IC-IR 0.22·chop +36.9% 방어적이나 Core 대비 한계기여 최고 +0.03%p « 50bp 경제적 최소치 → 승격 후보 아님). 다음 후보: event/revision 또는 quality×다른팩터. *알파는 베타를 못 넘는 패턴 재확인.*
4. **behavior 규율(Codex kill): 12mo 전 목표 변경·−30%서 수동 override 금지.**
2. (보류) Research 후보: quality 레짐 retest / MR 변형(longer-horizon·no-trade band) — v5 방향 정해진 뒤.
3. (TODO) forward reconciliation 2nd 무료소스 wiring(stooq 대체).
