# 15 — Claude Execution Prompt

아래 지시를 그대로 실행하라.

```text
너는 PRAMANA A2 구현 담당 Claude다.
과거 구현에서 look-ahead, live/backtest 혼동, Vault display-only, TQ-DH 누락, Attack/Moonshot 미회계 문제가 반복되었다.
이번에는 이 문서팩만 source of truth로 사용한다.

읽을 순서:
00_INDEX.md
01_A2_MASTER_SPEC.md
02_EIGHT_LAYER_ARCHITECTURE.md
03_DATA_AND_TIME_CONTRACT.md
04_ALLOCATION_AND_MAPPING.md
05~11 모듈 문서
12_BENCHMARKS_AND_DASHBOARD.md
13_IMPLEMENTATION_SEQUENCE.md
14_CODEX_STOP_CHECKLIST.md

우선 구현 순서:
1. Phase 0 Codex STOP 무결성 패치
2. Phase A Vault 진짜 ledger
3. Phase B 모듈별 book 회계
4. Phase C Attack/Moonshot 연료
5. Phase D LLM War Plan + Mapping
6. Phase E TQ-DH
7. Phase F 분봉 provider
8. Phase G Dashboard/cron

핵심 설정:
QQQ 35
TQQQ 35
Attack 10
Moonshot 10
Vault 10

절대 조건:
- LLM은 상태만 판정한다.
- 비중 변경은 mapping engine만 한다.
- 1회 변경 단위 5%p.
- same-day 신호로 same-day 수익 먹지 않는다.
- Vault는 반드시 active capital에서 실제 차감한다.
- Hard Vault는 재투입 금지다.
- TQ-DH는 반드시 구현한다.
- Attack과 Moonshot은 반드시 별도 ledger다.
- A2는 QQQ뿐 아니라 naive beta book과 비교한다.

구현 후 보고:
1. 변경 파일 목록
2. 구현 완료 phase
3. 남은 미구현
4. Codex STOP checklist 자체검사 결과
5. 현재 live/backtest 분리 상태
6. Vault가 진짜 ledger인지 증명
7. A2-Q/A2-T/naive 비교표
8. TQ-DH 모듈 존재 확인
9. Attack/Moonshot ledger 상태
10. 다음 필요한 사용자 입력
```
