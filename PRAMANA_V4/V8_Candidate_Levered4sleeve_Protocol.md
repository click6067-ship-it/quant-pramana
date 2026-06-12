# V8 Candidate — Levered 4-sleeve · crash-pack 사전등록 프로토콜 v0.1

> **가설:** V7 4-sleeve(분산북)를 *조심스럽게* 레버(1.25~1.5x)하면 — 상승 참여↑ 유지하며 비대칭(낙폭 방어) 유지. 용하 니즈("상승 더 먹고 하락 덜 맞기")에 가장 가까운 *비알파* 해법.
> **명확히(불변):** 이건 **알파 아님 = 분산 프리미엄을 레버한 것 = 목적함수 이동**(V7 '크래시 생존' → V8 '상승 참여 + 하락 방어'). QQQ를 레버하는 게(V5) 아니라 *분산 구조*를 레버.
> 상태: **V8 Candidate(확정 아님)·PAPER·RESEARCH_ONLY.** 결과 보기 **전** 작성(goalpost 고정). 2026-06-12.

## 1. grid (단일값 금지)
4-sleeve(Eq50/MF25/Gold15/Bond10) × **L ∈ {1.0(V7 baseline), 1.25, 1.35, 1.5}**. 레버 = `L·four_ret − (L−1)·RF/252`(financing). 1.5 초과 안 봄(그 이상은 "덜 맞기" 목적 훼손).

## 2. crash-pack (proxy·stress — V5 교훈: cap은 crash-loss budget으로 정한다, CAGR 아님)
| 윈도우 | 데이터 | 비고 |
|---|---|---|
| 2020 COVID·2022 bear | 실 ETF(SPY/QQQ/DBMF/GLD/IEF) | 실증 |
| 2008 GFC | VFINX·RYMFX·GC=F·VFITX | 4-sleeve 전부 proxy(핵심·긴 약세장) |
| 2000 닷컴 | VFINX·cash(MF)·GC=F·VFITX | MF proxy 없음→cash |
| 1987 | VFINX·VUSTX·cash | Black Monday 실데이터 |
측정: 각 L × 각 윈도우 → MDD·누적·회복일(UW). + 2019~ 풀 upside/downside capture(상승참여 확인).
**정정(Codex #2·방법론 버그 수정):** 2000/2008 equity는 VFINX 단일이 아니라 **실 SPY/QQQ 50/50**(QQQ 닷컴 −78% 반영·둘 다 1999~ 존재). VFINX는 1987만. 이 수정으로 레버 전부 worst MDD −49~−57% = **V8 전면 기각**(초기 VFINX proxy는 equity tail 과소평가였음).

## 3. 사전등록 통과/실패 기준 (kill = crash-loss budget)
A1 시나리오: MDD Conservative −20% / **Aggressive −35%(기본)** / Max −50%.
- **통과(그 L 감당 가능):** worst-crash MDD ≤ **−35%**(Aggressive) **AND** 상승참여(2019~) > V7 1.0x(53%).
- **승격:** 통과한 L 중 최고가 **V8 Paper Core Candidate**로 승격(상승참여 최대화하되 −35% 이내).
- **실패:** 모든 L>1.0이 worst-crash MDD > −35% → **레버 실패 → V7 1.0x 유지**(V8 기각).
- **레버 꼬리 경고:** 2008 proxy에서 어떤 L이 −35% 넘으면 그 L은 자동 reject(긴 약세장이 레버를 죽이는지가 핵심).

## 4. 한계 (사전 명시)
- proxy·in-sample(2019~ benign·2008도 proxy)·forward MDD는 더 클 수 있음(V5 −70%+ 꼬리 교훈).
- RF=5% 고정·financing 근사·일 리밸런스 가정(실제 레버 비용/슬리피지 더).
- **통과해도 paper·자본권한 0·Promotion Gates(forward 12mo·2-feed·사람 게이트) 전 실자본 금지.**
- 옵션 컨벡시티(★에 더 가까울 수 있음)는 데이터·프리미엄·과최적화 문제로 **이 crash-pack 이후로 미룸**(용하).

> **한 줄:** 알파 못 찾은 상태의 현실적 다음 수 = QQQ 레버(V5)가 아니라 V7 분산 구조를 *조심스럽게* 레버. crash-pack이 cap을 정한다(CAGR 아님). 통과=V8 Candidate 승격·실패=V7 1.0x.
