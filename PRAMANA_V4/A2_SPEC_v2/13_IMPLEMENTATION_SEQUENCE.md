# 13 — Implementation Sequence

## Phase 0 — Codex STOP 무결성 패치

목적: 수치 신뢰성 회복.

해야 할 일:

```text
0.1 allocator next-bar 적용
0.2 live ledger와 historical backtest 분리
0.3 to_won 기준 s.iloc[0] 또는 inception NAV로 수정
0.4 QQQ/TQQQ/Attack/Moonshot/Vault/Cash capital accounting 통일
0.5 naive beta benchmark 추가
0.6 old contaminated A2 숫자는 deprecated 처리
```

완료 기준:

```text
same-day look-ahead 없음
live/backtest 라벨 분리
NAV = QQQ + TQQQ + Attack + Moonshot + Vault + Cash
```

## Phase A — Vault 진짜 ledger

파일:

```text
engine/a2_profit_vault.py
positions/vault.json
outputs/a2_live/vault_ledger.csv
reports/A2_weekly_vault_review.md
```

완료 기준:

```text
Vault가 active capital에서 실제 차감
Hard/Reload 분리
주1회/월10% 제한
Vault-adjusted NAV 표시
```

## Phase B — 모듈별 book 회계

파일:

```text
engine/a2_book.py
engine/a2_q_module.py
engine/a2_tqqq_module.py
engine/a2_attack_ledger.py
engine/a2_moonshot_ledger.py
```

완료 기준:

```text
각 sleeve가 별도 ledger 보유
빈 Attack/Moonshot은 cash로 회계
Attack/Moonshot contribution 계산 가능
```

## Phase C — Attack/Moonshot 연료

파일:

```text
engine/a2_attack_scanner.py
engine/a2_attack_tokens.py
engine/a2_moonshot_draft.py
engine/a2_neg_gate.py
reports/moonshot_thesis/*.md
```

완료 기준:

```text
Attack 후보 발생
Attack token 소모/회복
Moonshot draft board 표시
NEG Gate 적용
```

## Phase D — LLM War Plan + Mapping

파일:

```text
engine/a2_daily_war_plan.py
engine/a2_dynamic_allocator.py
config/a2_state_mapping.yaml
outputs/a2_live/war_plan.json
```

완료 기준:

```text
LLM은 state만 출력
mapping engine이 target_weights 생성
5%p 변경 제한 적용
next-bar 적용
```

## Phase E — TQ-DH

파일:

```text
engine/a2_tq_dh.py
outputs/a2_live/tq_dh_signals.csv
reports/A2_tq_dh_report.md
```

완료 기준:

```text
dip type A/B/C/D 분류
Reload Vault만 사용
TQQQ DCA 벤치마크와 비교
```

## Phase F — 분봉 provider

파일:

```text
engine/a2_intraday_provider.py
engine/providers/yfinance_provider.py
engine/providers/polygon_provider.py
engine/providers/alpaca_provider.py
```

완료 기준:

```text
yfinance PROXY 작동
provider interface 통일
DATA_QUALITY 표시
자동집행 전 paper signal만
```

## Phase G — Dashboard/cron

파일:

```text
engine/a2_dashboard.py
outputs/a2_live_dashboard.html
reports/A2_daily_dashboard.md
reports/A2_weekly_review.md
```

완료 기준:

```text
A2 vs QQQ/SPY/TQQQ/naive/V7/A2-Q/A2-T/TQ-DH 표시
Vault 실제 표시
Attack/Moonshot 표시
mini PC cron/systemd 문서화
```
