#!/usr/bin/env bash
# PRAMANA A2 v2 — daily chain (SSOT v2 §13 phase order). PAPER·자본권한 0.
# 순서 중요: risk_dashboard(state factory) → sleeve/lockout/allocator → war_plan → scanner/executor → tq_dh → book(NAV·Vault) → dashboard.
# cron: 화~토 06:00 한 줄로 호출. 로그 = outputs/a2_live/cron.log
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY=".venv/bin/python"
LOG="outputs/a2_live/cron.log"
run(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; $PY engine/$* >> "$LOG" 2>&1 || echo "[$(date '+%F %T')] WARN $* exit $?" >> "$LOG"; }

run a2_risk_dashboard.py        # L2 state factory (FIRST)
run a2_book.py                  # L3/L7 accountable NAV + 실제 Vault 차감 (drawdown_rules가 current dd 읽으려면 먼저·Codex fix)
run a2_q_module.py              # L3 QQQ state
run a2_tqqq_module.py           # L3 TQQQ Booster·Decay·Booster Rent
run a2_drawdown_rules.py        # L5 Crash/Attack Lockout (book의 LIVE current drawdown 기준)
run a2_dynamic_allocator.py     # L4 state→target weight (next-bar·5%p·clamp)
run a2_daily_war_plan.py        # L2 통합 war plan (SSOT §10 schema)
run a2_attack_scanner.py        # L2 attack candidates (분봉 PROXY)
run a2_attack_executor_paper.py # L6 paper entry (token·NEG gate·grade A/B)
run "a2_tq_dh.py --forward"     # L5/E TQ-DH LIVE forward 신호(backtest 아님·real Reload Vault·Codex fix)
run a2_dashboard.py             # L7 unified dashboard (마지막)
echo "[$(date '+%F %T')] A2 daily chain done" >> "$LOG"
