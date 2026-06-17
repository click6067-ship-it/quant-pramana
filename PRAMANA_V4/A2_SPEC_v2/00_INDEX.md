# PRAMANA A2 — Claude 구현용 최종 통합 스펙 v2.0

**상태:** PAPER only · NO LIVE · 자본권한 0  
**이 문서팩의 목적:** Claude가 더 이상 이전 문서/구현을 임의 해석하지 않고, 이 문서만 보고 A2를 A→Z로 구현하도록 하는 단일 source of truth.

## 이 문서가 이전 문서보다 우선한다

충돌 시 우선순위:

1. `PRAMANA_A2_SINGLE_SOURCE_OF_TRUTH_v2.md` / 이 모듈팩
2. `pramana_a2_delta_patch_pack`
3. `pramana_a2_implementation_pack`
4. `PRAMANA_A2_Convex_Raider_Book_FINAL_v1.md`
5. 과거 A1/V7 문서

이전 A2 v1의 `QQQ30/TQQQ40/Attack12/Moon8/Vault10`은 **legacy**다.  
최신 A2 v2 기본 비중은 **QQQ35/TQQQ35/Attack10/Moonshot10/Vault10**이다.

## 구현 순서

Claude는 반드시 아래 순서대로만 구현한다.

1. **Phase 0 — 무결성 패치**  
   next-bar, live/backtest 분리, 회계 통일, Vault display-only 제거.
2. **Phase A — Vault 진짜 ledger**  
   Hard/Reload Vault, NAV 차감, Vault In/Out, weekly/monthly limit.
3. **Phase B — 모듈별 book 회계**  
   QQQ, TQQQ, Attack, Moonshot, Vault sleeve를 독립 ledger로 구현.
4. **Phase C — Attack/Moonshot 연료**  
   Attack scanner, Moonshot thesis board, NEG Gate, Token/Draft/Decay.
5. **Phase D — LLM Council + Mapping Engine**  
   LLM은 상태만 판정, 비중 변경은 사전정의 mapping.
6. **Phase E — TQ-DH**  
   TQQQ Dip Harvester, Reload Vault 기반 dip 분류/재투입.
7. **Phase F — 대시보드/운영**  
   3년/12/6/3/live comparison, mini PC cron, health check.

## 파일 목록

| 파일 | 역할 |
|---|---|
| `01_A2_MASTER_SPEC.md` | A2 v2 전체 목적·원칙·금지사항 |
| `02_EIGHT_LAYER_ARCHITECTURE.md` | 기존 8레이어에 A2 모듈 매핑 |
| `03_DATA_AND_TIME_CONTRACT.md` | 데이터/API·PIT·blind backtest·분봉 데이터 계약 |
| `04_ALLOCATION_AND_MAPPING.md` | 35/35/10/10/10·동적 비중·LLM state mapping |
| `05_QQQ_MODULE.md` | QQQ Core 구현 |
| `06_TQQQ_MODULE.md` | TQQQ Booster·Decay·Booster Rent |
| `07_ATTACK_MODULE.md` | 급등주·ORB/VWAP/RVOL·Bollinger·day trade |
| `08_MOONSHOT_MODULE.md` | Moonshot thesis·EV·Draft Board |
| `09_VAULT_MODULE.md` | Profit Vault 진짜 ledger·Vault In/Out |
| `10_RISK_LLM_COUNCIL.md` | Risk Dashboard·LLM Council 역할 |
| `11_TQ_DH_DIP_HARVESTER.md` | TQQQ Dip Harvester |
| `12_BENCHMARKS_AND_DASHBOARD.md` | QQQ/SPY/TQQQ/naive/A2-Q/A2-T/TQ-DH 비교 |
| `13_IMPLEMENTATION_SEQUENCE.md` | 구현 단계·파일·완료조건 |
| `14_CODEX_STOP_CHECKLIST.md` | Codex STOP 방지 체크리스트 |
| `15_CLAUDE_EXECUTION_PROMPT.md` | Claude에게 그대로 넣을 실행 프롬프트 |

## Claude에게 전달 방법

1. 압축을 풀어 repo의 `PRAMANA_V4/A2_SPEC_v2/`에 넣는다.
2. Claude에게 먼저 `15_CLAUDE_EXECUTION_PROMPT.md`를 붙여넣는다.
3. Claude가 구현 전 `00_INDEX.md → 01 → 02 → 03 → 04 → 모듈별 문서 → 13 → 14` 순서로 읽었는지 확인한다.
4. Claude가 구현 완료를 말하면 `14_CODEX_STOP_CHECKLIST.md` 기준으로 자체검사 결과를 보고하게 한다.

## 한 줄 요약

A2는 알파가 검증된 전략이 아니다. **QQQ/TQQQ 성장 베타를 사고, Attack/Moonshot으로 비대칭을 붙이고, Profit Vault로 번 돈을 잠그며, Risk/LLM Dashboard로 자멸을 줄이는 고위험 paper book**이다.
