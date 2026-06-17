# Claude Execution Prompt — PRAMANA A2 Full Module Implementation

아래를 Claude에게 그대로 붙여넣는다.

---

## Prompt

PRAMANA A2 구현을 다시 정리한다. 지금부터 이 폴더의 문서만 보고 구현한다고 가정한다.

반드시 먼저 읽을 파일:

1. `00_INDEX.md`
2. `01_MASTER_SPEC.md`
3. `02_EIGHT_LAYER_ARCHITECTURE.md`
4. `03_STATE_AND_CONFIG_CONTRACT.md`
5. `14_IMPLEMENTATION_SEQUENCE.md`
6. `15_CODEX_QA_STOP_CHECKLIST.md`

그 다음 모듈별 문서를 읽어라:

- `05_QQQ_MODULE.md`
- `06_TQQQ_BOOSTER_MODULE.md`
- `07_ATTACK_MODULE.md`
- `08_MOONSHOT_MODULE.md`
- `09_VAULT_MODULE.md`
- `10_RISK_DASHBOARD_AND_LLM_COUNCIL.md`
- `11_DYNAMIC_ALLOCATOR_MAPPING.md`
- `12_LEDGER_ACCOUNTING_AND_BENCHMARKS.md`
- `13_DASHBOARD_REPORTS_AND_CRON.md`

핵심 지시:

```text
A2는 PAPER only.
SPY는 A2 portfolio에서 퇴출, benchmark로만 유지.
Base allocation은 QQQ 35 / TQQQ 35 / Attack 10 / Moonshot 10 / Vault 10.
TQQQ는 Core가 아니라 Booster.
LLM은 상태 판정만 한다. 비중 변경은 사전 정의 mapping으로 한다.
Attack은 분봉 day strategy다.
Moonshot은 thesis/판정일 기반이다.
Vault는 진짜 ledger로 구현한다.
```

구현 순서:

### Phase 0 — Codex STOP 무결성 패치

```text
- allocator next-bar 적용: all states shift(1)
- live/backtest 분리
- to_won 시작값 수정
- capital accounting 통일
- naive beta benchmark 생성
```

Phase 0 완료 전 성과 해석 금지.

### Phase A — Vault 진짜 ledger

```text
- positions/vault.json
- outputs/a2_live/vault_ledger.csv
- Hard/Reload 분리
- HWM trigger
- 주1회/월10% 제한
- active NAV에서 실제 차감
```

### Phase B — Attack/Moonshot 연료

```text
- Graveyard Revival Board 판정
- Attack ledger/token
- Moonshot draft/thesis ledger
- NEG Gate 차등 적용
- R sizing/EV 기록
```

### Phase C — LLM War Plan / Mapping / Minute Provider

```text
- LLM War Plan 생성
- state_mapping.yaml
- dynamic allocator
- intraday provider interface
- yfinance PROXY provider
- Attack scanner ORB/VWAP/RVOL/Bollinger
```

### Phase D — Dashboard / Reports / MiniPC routine

```text
- A2 dashboard
- daily war plan report
- weekly vault review
- codex QA report
- cron/systemd guide
```

보고 형식:

```text
1. 먼저 전체 구조를 쉬운 말로 요약
2. 변경 파일 목록
3. 구현한 Phase
4. 아직 미구현인 것
5. Codex STOP checklist 잔여
6. 현재 NAV/weights/mode
7. dashboard path
8. 다음 필요한 사용자 입력
```

금지:

```text
새로운 검증 엔진 만들기 금지
A2 수치를 live 성과처럼 과장 금지
Vault를 표시용으로만 구현 금지
LLM에게 비중 결정시키기 금지
TQQQ를 알파라고 부르기 금지
```
