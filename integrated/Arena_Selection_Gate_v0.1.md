# Arena Selection Gate v0.1 (Phase 0 Reframe — 짧게)
**Date:** 2026-06-11 · **Status:** US 단순/선형/결합 패러다임 TERMINATE 후 다음 arena 선택 · **결정:** 3(reframe) → 2(US signal type 변경), KR 보류
**교훈(정정):** "미국이 안 됨"이 아니라 **"공개 단순팩터는 대형/중대형에서 단독·결합 모두 standalone edge가 아님"**. → *시장*이 아니라 *edge source*(level → event/surprise)를 바꾼다. KR로 바로 점프 = 작동하는 실험장 버리고 새 경기장 공사 = 비약·위험.

## 후보 arena 3개 × 7축

### 🥇 A. US event / earnings drift  ← **1순위 (다음 실험)**
1. **edge hypothesis:** 공개 *레벨* 팩터는 차익거래로 소멸했지만, **공시 이벤트 주변의 변화·드리프트**(fundamental acceleration, post-filing drift)는 정보처리 지연·관심 제약으로 덜 차익거래됨.
2. **required data:** 공시일(PIT) + 펀더멘털 시계열(revenue/gp/eps/margin) + 가격. (진짜 surprise엔 analyst estimate.)
3. **current availability:** **HIGH** — Sharadar SF1 `datekey`(PIT 공시일)·revenue/gp/netinc/eps/grossmargin/roe 全 보유, pull 인프라 검증됨. *단 analyst estimate=없음 → surprise는 proxy(fundamental acceleration)로만.* (정직한 한계.)
4. **cost/liquidity risk:** **LOW** — top-1500 중대형 그대로 사용(유동성 OK), 비용 모델 이미 있음. 회전율만 관리.
5. **impl difficulty:** **LOW** — 기존 파이프(universe·benchmark·cost·IC) 재사용, 신호만 event 기반으로 교체.
6. **kill condition:** 2021–26 IC-IR<0.10 / net active vs CW≤0 / 비용 후 사망 / 2016–20에만 집중 / long-only 음수 → 하나라도면 arena 종료.
7. **next 1-week experiment:** SF1 datekey 기반 fundamental acceleration + filing freshness 신호, top-1500 long-only Q5 + rank-IC diagnostic, cost 포함, 2021–26 kill. → `US_Event_Earnings_Drift_Experiment_Protocol_v0.1.md`.

### 🥈 B. US micro / small-cap (cost-first)
1. **edge hypothesis:** top-1500 밖 소형주는 덜 효율적 → 단순팩터가 *거기선* 살 수도. (단 Phase 1A가 시사: 대형선 죽음 = 소형 프리미엄 가설.)
2. **required data:** 소형주 가격·시총·펀더멘털(이미 DAILY_all에 5797종)·**거래대금(volume, 미pull)**.
3. **current availability:** **MEDIUM** — 시총/가격 있음, **volume·spread 미보유**(비용 추정 핵심인데 빠짐).
4. **cost/liquidity risk:** **HIGH** — spread/impact가 알파를 죽일 가능성 큼. "탐색"이 아니라 **비용 후 죽는지 kill-test로만**.
5. **impl difficulty:** MEDIUM — volume pull + 현실적 비용 모델 필요.
6. **kill condition:** 현실적 비용(소형 spread) 적용 시 net≤0 → 즉시 종료.
7. **next experiment:** (A 실패 시) volume pull → 소형 단순팩터 비용-우선 kill test.

### 🥉 C. KR small/mid + event (보류)
1. **edge hypothesis:** KR 비효율 코너(소형·공시이벤트·구조적 데이터우위). **KR 대형주 단순팩터 포팅은 금지**(미국과 동일 벽 예상).
2. **required data:** KR PIT 구성종목·공시(KIND/DART I002)·무료 종목마스터·가격.
3. **current availability:** **LOW(미구축)** — DR-2 시퀀스에 스코핑됐으나 PIT 멤버십·거래세·체결(NXT/SOR) 난도 재상승. 데이터 feasibility 재점검 필요.
4. **cost/liquidity risk:** 거래세 30bp·유동성·체결구조 = US보다 높음.
5. **impl difficulty:** **HIGH** — 새 데이터 파이프 처음부터.
6. **kill condition:** PIT/data feasibility 재점검 통과 못 하면 진입 안 함.
7. **next experiment:** (A·B 실패 시) KR PIT/data feasibility 재점검 → small/mid/event 중심.

## 결정 (박음)
- **A(US event/earnings drift) = 다음 실험.** 살아있는 Sharadar 구독 + 이미 받은 데이터 + 검증된 US 인프라 활용. 작동하는 실험장 유지.
- A 죽으면 → B(US 소형 cost-first kill-test). B도 죽으면 → C(KR, data feasibility 먼저).
- **불변:** KR 즉시점프 금지 · XGBoost/LLM/TSFM/deep 금지 · 기존 4팩터(value/quality/momentum/lowvol) 정의·튜닝 변경 금지 · **kill 조건 먼저 박기.**

## 실행 결과 (2026-06-11)
- **A (US event) = FAIL** — event/surprise 신호 decay 안 하나 large-cap에선 cap-weight 벽. `reports/US_event_drift_result.md`.
- **B (US small/mid cost-first) = FAIL** — small/mid는 cap-weight 벽 약해 신호 더 살지만(value 부활·셋다 base서 CW 이김), edge가 *최저유동성 버킷에 집중*+IC-IR<0.20 바+turnover로 종료. event만 잔여(2021–26 IC-IR +0.301·고유동성 +1.69%)나 바 미달 FAIL(goalpost 불변). `reports/US_smallmid_costfirst_result.md`.
- **→ US public-data cross-sectional arena CLOSED.** 4 arena 전부 종료.
- **~~다음 = C (KR feasibility)~~ → SUPERSEDED (2026-06-11).** 프로젝트 scope를 **US-only로 고정**, KR은 **Future Market Adapter (Deferred)**. 다음은 KR이 아니라 **US-Only Completion Roadmap**(`US_Only_Completion_Roadmap_v0.1.md`). 방향신호 2개(신호는 small/mid서 더 산다·event는 decay 안 함)는 P3.3 US next-edge protocol의 입력으로 보관(KR 즉시 점프 아님).
