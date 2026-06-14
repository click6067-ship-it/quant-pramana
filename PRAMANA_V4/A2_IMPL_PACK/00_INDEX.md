# PRAMANA A2 Implementation Pack — Claude Navigation Index

**목적:** Claude가 이 폴더만 보고 PRAMANA A2-T / A2-Q / Attack / Moonshot / Vault를 처음부터 끝까지 구현할 수 있게 만든 구현 지시 패키지.

**상태:** PAPER only · NO LIVE · 가상자본 ₩100,000,000 · A2는 검증된 알파가 아니라 고위험 Convex Raider Book.

**핵심:** SPY는 A2 포트폴리오에서 퇴출. QQQ/TQQQ 중심. TQQQ는 Core가 아니라 Booster. Attack/Moonshot은 별도 엔진. Vault는 장식이 아니라 실제 ledger. LLM은 상태 판정만, 비중 변경은 사전 정의 mapping.

---

## 문서 목록과 읽는 순서

1. [`01_MASTER_SPEC.md`](01_MASTER_SPEC.md)  
   전체 목표, 금지어, 기본 비중, 구현 철학, 성공 정의.

2. [`02_EIGHT_LAYER_ARCHITECTURE.md`](02_EIGHT_LAYER_ARCHITECTURE.md)  
   기존 8레이어 아키텍처로 A2를 재구조화.

3. [`03_STATE_AND_CONFIG_CONTRACT.md`](03_STATE_AND_CONFIG_CONTRACT.md)  
   모든 config/state/ledger의 단일 소스 규칙. Claude 구현 실수를 막는 계약서.

4. [`04_DATA_AND_INTEGRITY_LAYER.md`](04_DATA_AND_INTEGRITY_LAYER.md)  
   Sharadar, EDGAR, yfinance, minute provider, next-bar, PIT, live/backtest 분리.

5. [`05_QQQ_MODULE.md`](05_QQQ_MODULE.md)  
   QQQ Core 모듈. SPY 퇴출, QQQ benchmark, A2-Q 구조.

6. [`06_TQQQ_BOOSTER_MODULE.md`](06_TQQQ_BOOSTER_MODULE.md)  
   TQQQ Booster 모듈. 35% 기본, 15~45% 범위, Decay Meter, Booster Rent, 증액/축소 조건.

7. [`07_ATTACK_MODULE.md`](07_ATTACK_MODULE.md)  
   Attack Sleeve. 급등주·모멘텀·Bollinger·ORB/VWAP/RVOL·당일 청산.

8. [`08_MOONSHOT_MODULE.md`](08_MOONSHOT_MODULE.md)  
   Moonshot Sleeve. thesis 기반, 판정일, Reward/Risk, draft board.

9. [`09_VAULT_MODULE.md`](09_VAULT_MODULE.md)  
   Profit Vault. 실제 ledger, NAV 차감, Hard/Reload, HWM, weekly/monthly 제한.

10. [`10_RISK_DASHBOARD_AND_LLM_COUNCIL.md`](10_RISK_DASHBOARD_AND_LLM_COUNCIL.md)  
    Leadership Risk, Market Stress, LLM Narrative, 상태 판정만 하는 LLM Council.

11. [`11_DYNAMIC_ALLOCATOR_MAPPING.md`](11_DYNAMIC_ALLOCATOR_MAPPING.md)  
    35/35/10/10/10 기본 비중과 ±5%p mapping. LLM 상태 → rule engine target weights.

12. [`12_LEDGER_ACCOUNTING_AND_BENCHMARKS.md`](12_LEDGER_ACCOUNTING_AND_BENCHMARKS.md)  
    live/backtest 분리, A2-T/A2-Q/naive/QQQ/SPY/TQQQ 비교, 회계 불변식.

13. [`13_DASHBOARD_REPORTS_AND_CRON.md`](13_DASHBOARD_REPORTS_AND_CRON.md)  
    대시보드, 미니PC cron/systemd, 장전/장중/장후 루틴.

14. [`14_IMPLEMENTATION_SEQUENCE.md`](14_IMPLEMENTATION_SEQUENCE.md)  
    실제 구현 순서. Phase 0 → A → B → C → D. 한 번에 다 하지 말 것.

15. [`15_CODEX_QA_STOP_CHECKLIST.md`](15_CODEX_QA_STOP_CHECKLIST.md)  
    Codex 검수 체크리스트. look-ahead, Vault 장식화, live/backtest 혼동 방지.

16. [`16_CLAUDE_PROMPT_EXECUTION_ORDER.md`](16_CLAUDE_PROMPT_EXECUTION_ORDER.md)  
    Claude에게 바로 넣을 수 있는 실행 프롬프트.

---

## 절대 원칙

```text
1. A2는 PAPER only. 실거래 금지.
2. TQQQ는 Core가 아니라 Booster.
3. SPY는 A2 포트폴리오에서 퇴출하지만 benchmark로는 유지.
4. LLM은 상태 판정만 한다. 비중 변경은 mapping engine.
5. 모든 신호는 next-bar. same-day look-ahead 금지.
6. live ledger와 historical backtest는 절대 섞지 않는다.
7. Vault는 실제 ledger다. 표시용이면 실패.
8. Attack/Moonshot이 비어 있으면 A2는 미완성 beta book이다.
9. A2-T가 QQQ를 이겨도 naive beta book을 못 이기면 전략 부가가치는 미확정.
10. 구현 전 이 폴더를 끝까지 읽고, Phase 순서대로 진행한다.
```
