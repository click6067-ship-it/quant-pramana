# Claude 구현 프롬프트 — A2 Delta Patch v0.1

아래 지시를 그대로 수행해줘. 기존 `PRAMANA_A2_Convex_Raider_Book_FINAL_v1.md`를 전면 재작성하지 말고, delta patch 문서와 구현 파일을 추가/수정한다.

## 0. 목적

최근 대화에서 확정된 다음 네 가지를 A2에 반영한다.

```text
1. Attack/Moonshot blind/PIT backtest 설계.
2. TQ-DH — TQQQ Dip Harvester 추가.
3. 벤치마크 확장 및 실행.
4. 동적 매도/Vault timing 알고리즘 추가.
```

상태는 유지한다.

```text
PAPER only.
NO LIVE.
자본권한 0.
LLM은 상태판정만.
비중 변경은 mapping engine만.
```

---

## 1. 문서 추가

아래 문서를 repo에 추가해.

```text
PRAMANA_V4/A2_DELTA/00_INDEX.md
PRAMANA_V4/A2_DELTA/01_A2_DELTA_MASTER_PATCH.md
PRAMANA_V4/A2_DELTA/02_ATTACK_MOONSHOT_BLIND_BACKTEST.md
PRAMANA_V4/A2_DELTA/03_TQ_DH_TQQQ_DIP_HARVESTER.md
PRAMANA_V4/A2_DELTA/04_BENCHMARKS_AND_METRICS.md
PRAMANA_V4/A2_DELTA/05_DYNAMIC_SELL_AND_VAULT_TIMING.md
```

각 문서에는 사용자가 요구한 세부사항을 모두 넣는다.

---

## 2. A2 기본 비중 업데이트

기본값을 35/35/10/10/10으로 변경한다.

```text
QQQ 35
TQQQ 35
Attack 10
Moonshot 10
Vault 10
```

허용 범위:

```text
QQQ 25~45
TQQQ 15~45
Attack 0~20
Moonshot 0~15
Vault 5~30
```

변경 단위:

```text
1회 5%p
일일 최대 5%p
주간 최대 10%p
```

---

## 3. Blind/PIT backtest 구현

Attack/Moonshot 과거 시뮬레이션은 반드시 blind/PIT로 구현한다.

핵심:

```text
decision_time 기준 available_at <= decision_time 데이터만 사용.
signal_time < execution_time.
same-bar execution 금지.
```

구현 파일:

```text
engine/a2_feature_store.py
engine/a2_event_store.py
engine/a2_blind_backtest.py
```

출력:

```text
outputs/a2_features/feature_store.parquet
outputs/a2_events/event_store.parquet
outputs/a2_decisions/decision_log.csv
```

Sharadar는 daily/PIT backbone으로만 사용한다.  
분봉/VWAP/ORB 과거검증은 Sharadar로 불가능하므로 yfinance recent proxy 또는 provider minute data로 별도 라벨링한다.

---

## 4. TQ-DH 구현

TQQQ Dip Harvester를 추가한다.

파일:

```text
engine/a2_tq_dh.py
config/a2_tq_dh.yaml
outputs/a2_live/tq_dh_decisions.csv
reports/A2_tq_dh_weekly_review.md
```

Dip type:

```text
Type A: Liquidity Air Pocket
Type B: Growth Reset
Type C: Structural Break
Type D: Capitulation + Repair
```

Hard Vault 사용 금지.  
Reload Vault만 25%씩 사용.

비교:

```text
TQQQ buy-and-hold
TQQQ monthly DCA
TQQQ drawdown DCA
A2 with/without TQ-DH
```

---

## 5. 벤치마크 구현

파일:

```text
engine/a2_benchmarks.py
outputs/a2_live/benchmark_panel.csv
outputs/a2_live/a2_benchmark_dashboard.html
reports/A2_monthly_benchmark_review.md
```

벤치마크:

```text
SPY
QQQ
TQQQ
A2-Q
A2-T
A2 base fixed
A2 dynamic
naive QQQ35/TQQQ35/Cash30
synthetic QQQ 1.4x
TQQQ monthly DCA
TQQQ drawdown DCA
V7
TQ-DH
```

성과표 기간:

```text
3년
12개월
6개월
3개월
inception-to-date
live-only
```

---

## 6. Dynamic Sell / Vault Timing 구현

파일:

```text
engine/a2_dynamic_sell.py
engine/a2_profit_vault.py
config/a2_vault_rules.yaml
outputs/a2_live/vault_events.csv
outputs/a2_live/sleeve_adjustments.csv
reports/A2_weekly_vault_review.md
```

Vault In:

```text
A2 excess HWM 갱신
AND A2 절대 NAV 수익 상태
AND 위험 신호 YELLOW/RED일수록 더 강하게 Vault
```

Vault Out:

```text
Reload Vault만 사용.
Hard Vault 사용 금지.
Leadership GREEN, Decay GREEN, Market Stress not RED, A급 후보 또는 TQ-DH Type A/D일 때만.
```

Sell/Trim:

```text
TQQQ trim = -5%p
Attack trim = -5%p
Moonshot trim = -5%p
```

Add:

```text
TQQQ add = +5%p
Attack add = +5%p
Moonshot add = +5%p
```

LLM은 상태만 제공. 실제 변경은 mapping engine.

---

## 7. 기존 구현 주의

Codex STOP 사항을 다시 위반하지 말 것.

```text
same-day look-ahead 금지
backtest/live 혼동 금지
Vault 표시용 금지
Attack/Moonshot 빈 슬롯 cash accounting 명확화
```

---

## 8. 완료 보고 형식

구현 후 다음을 보고해.

```text
1. 추가/수정 파일 목록
2. 문서 링크/경로
3. 구현된 기능
4. 아직 미구현
5. 대시보드 경로
6. 벤치마크 표
7. Codex STOP 잔여 리스크
8. 다음 사용자 입력 필요사항
```
