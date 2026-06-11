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

## 다음 행동
1. **v5 reframe 제안 완료(Codex 회의 done) → 용하 승인 대기.** = `PRAMANA_V4/PRAMANA_V5_Problem_Frame_v0.1.md`. 핵심: "QQQ raw 넘기"(불가·베타chase) 버리고 **v5 = QQQ-Participation Risk-Control Book**(SPY는 raw 초과·QQQ엔 80-100% 상방참여+낮은 낙폭/빠른 회복). **STOP 기준: 12개월 forward 못 맞추면 재정의 중단·"쉬운 알파 없음" 수용**(무한루프 차단). 용하 결정: 채택? 지표 임계? 아니면 raw 고집=레버(리스크) 수용?
2. (보류) Research 후보: quality 레짐 retest / MR 변형(longer-horizon·no-trade band) — v5 방향 정해진 뒤.
3. (TODO) forward reconciliation 2nd 무료소스 wiring(stooq 대체).
