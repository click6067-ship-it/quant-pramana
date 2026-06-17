# PRAMANA A2 — Implementation Sequence

Claude는 이 순서대로만 구현한다. 순서 건너뛰기 금지.

---

## Phase 0 — Codex STOP 무결성 패치

### 목표

기존 A2-T가 제대로 된 수치가 되도록 회계/룩어헤드/라벨 문제를 먼저 해결.

### 작업

```text
0.1 allocator next-bar: all daily states shift(1)
0.2 live/backtest 분리
0.3 to_won 시작값 s.iloc[0] 기준
0.4 QQQ/TQQQ/Attack/Moonshot/Vault/Cash accounting 통일
0.5 naive beta benchmark 생성
0.6 dashboard에서 오염 수치 숨기거나 라벨 수정
```

### 산출물

```text
outputs/a2_backtest/backtest_panel_clean.csv
outputs/a2_live/nav_log.csv
reports/A2_codex_check.md
```

### 완료 기준

```text
Codex STOP #1~#5 모두 CLOSED or 명확한 TODO
```

---

## Phase A — Vault 진짜 ledger

### 목표

Vault를 표시용이 아니라 실제 active capital에서 빠지는 ledger로 구현.

### 작업

```text
A.1 positions/vault.json 생성
A.2 vault_ledger.csv append-only
A.3 HWM trigger 계산
A.4 Hard/Reload 분리
A.5 주1회/월10% 제한
A.6 Vault-adjusted NAV 계산
A.7 Dashboard 표시
```

### 완료 기준

```text
Vault 이동 시 active capital 감소
Hard Vault 재투입 불가
dashboard에 Hard/Reload/trigger 표시
```

---

## Phase B — Attack/Moonshot 연료

### 목표

A2가 beta-only가 아니라 Attack/Moonshot이 실제 ledger를 갖는 book이 되게 함.

### 작업

```text
B.1 Graveyard Revival Board 판정 파일 작성
B.2 config/a2_revived_components.yaml
B.3 Attack ledger + token system
B.4 Moonshot ledger + draft board
B.5 NEG Gate 차등 적용
B.6 Thesis template 생성
B.7 sample paper candidate 1개까지는 수동 입력 가능
```

### 완료 기준

```text
Attack 후보가 ledger에 들어갈 수 있음
Moonshot thesis가 등록될 수 있음
Token과 R sizing이 작동
NEG Gate가 Attack/Moonshot에 다르게 적용
```

---

## Phase C — LLM War Plan / Mapping / Minute Provider

### 목표

LLM 상태 판정과 rule-based dynamic allocation 구현.

### 작업

```text
C.1 LLM War Plan JSON/MD 생성
C.2 state_mapping.yaml 작성
C.3 a2_dynamic_allocator.py 구현
C.4 intraday provider interface 구현
C.5 yfinance provider = PROXY
C.6 Attack scanner에 ORB/VWAP/RVOL/Bollinger 추가
C.7 DATA_QUALITY 표시
```

### 완료 기준

```text
LLM이 숫자 비중을 정하지 않음
mapping engine이 target weights 생성
Minute provider가 바 데이터를 반환
Attack candidates 생성
```

---

## Phase D — Dashboard / Cron / Reports

### 목표

운영 가능하게 보이도록 통합.

### 작업

```text
D.1 dashboard.html 업데이트
D.2 Daily War Plan 링크
D.3 Vault review 링크
D.4 cron/systemd 설정 문서
D.5 health log
D.6 3년/12/6/3개월 표
```

### 완료 기준

```text
A2 live dashboard에서 모든 주요 상태 확인 가능
cron status 표시
ledger append-only 확인
```

---

## 절대 금지

```text
Phase A 전에 새로운 전략 성과 해석 금지
Phase B 전에 A2가 공격형이라고 주장 금지
Phase C 전에 LLM이 비중 숫자 결정 금지
Vault 미구현 상태에서 Vaulted Profit 성공 조건 표시 금지
```
