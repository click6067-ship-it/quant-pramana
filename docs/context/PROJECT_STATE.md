# PROJECT_STATE — PRAMANA V4
> 현재 상태 스냅샷. **갱신일: 2026-06-12.** 상태가 바뀌면 이 파일부터 갱신. *Codex: 이 날짜가 오늘과 많이 떨어졌으면 먼저 "stale 가능" 경고하고 시작.*
> 정본 locks+근거 = `PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v0.4.md` · 전체 히스토리 = `PRAMANA_ARCHIVE/PRAMANA_MASTER_DOSSIER.docx`

## 한 줄
core-satellite 재설계(V4). **Production = Core(SPY/QQQ) 중심·일봉·paper forward. Research = 자본권한 0으로 개방.** 확인된 알파 위성은 *아직 없음.*

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

## 다음 행동
1. A1(현 −35%)로 **Production = "Core Beta Forward Book"(알파북 아님 — SPY/QQQ 베타 + 선택적 약한 낙폭 오버레이; Core>SPY는 QQQ 틸트=레짐, 알파 아님) → forward.**
2. **Research Active 1개 = mean-reversion(★1순위·trend 약한 chop장 공략)** — forward 도는 동안. (quality는 2순위.) 동시에 sentiment/기관/intraday 데이터는 *passive 수집* 가능.
