# PRAMANA A2 — Delta Patch Pack v0.1

작성일: 2026-06-13  
상태: PAPER only · NO LIVE · 자본권한 0  
목적: 기존 `PRAMANA_A2_Convex_Raider_Book_FINAL_v1.md`를 전면 재작성하지 않고, 최근 대화에서 확정/수정된 부분만 별도 설계 문서로 분리한다.

---

## 읽는 순서

1. `01_A2_DELTA_MASTER_PATCH.md`  
   전체 변경 요약. 기존 A2 v1에서 무엇을 바꾸는지 한눈에.

2. `02_ATTACK_MOONSHOT_BLIND_BACKTEST.md`  
   Attack/Moonshot을 과거데이터로 볼 때 blind/PIT 처리 방법. Sharadar로 가능한 것과 불가능한 것. 무료 데이터 한계.

3. `03_TQ_DH_TQQQ_DIP_HARVESTER.md`  
   TQ-DH — TQQQ Dip Harvester. 단순 낙폭매수와 다른 방식으로 dip을 분류하고 Reload Vault를 사용하는 공격형 모듈.

4. `04_BENCHMARKS_AND_METRICS.md`  
   비교 벤치마크. QQQ, SPY, TQQQ, naive beta book, TQQQ DCA, TQQQ drawdown DCA, A2-Q, A2-T, TQ-DH 등.

5. `05_DYNAMIC_SELL_AND_VAULT_TIMING.md`  
   매도 타이밍, Vault In/Out, 5%p 단위 동적 비중 조절. Vault를 단순 고정 규칙이 아니라 alpha-timing engine으로 쓰는 설계.

6. `06_CLAUDE_IMPLEMENTATION_PROMPT_DELTA.md`  
   Claude에게 그대로 붙여넣을 구현 지시 프롬프트.

---

## 핵심 변경 한 줄

기존 A2는 QQQ/TQQQ 성장 베타 + Attack/Moonshot + Vault 구조였지만, 이번 delta는 다음 네 가지를 추가/수정한다.

```text
1. Attack/Moonshot 과거 시뮬레이션은 반드시 blind/PIT로 구현한다.
2. TQ-DH: TQQQ dip을 무작정 사지 않고 dip의 종류를 분류한다.
3. 모든 결과는 QQQ/TQQQ/naive/DCA 계열 벤치마크와 비교한다.
4. Vault와 매도 타이밍도 5%p 단위의 동적 alpha-timing mapping으로 관리한다.
```

---

## 강제 원칙

```text
PAPER only.
NO LIVE.
자본권한 0.
LLM은 상태판정만.
비중 변경은 사전정의된 mapping만.
Hard Vault 재투입 금지.
look-ahead 금지.
Sharadar는 daily/PIT backbone.
분봉 과거검증은 무료로는 제한적이며, 신뢰 판정에는 별도 라벨 필요.
```
