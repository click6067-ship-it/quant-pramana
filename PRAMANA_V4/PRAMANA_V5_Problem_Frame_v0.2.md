# PRAMANA V5 — Problem Frame v0.2 (용하 승인 + Codex REVISE 반영 · v0.1 대체)

> **용하 결정(2026-06-12): #1 공격적 수익극대화·리스크 수용 · #2 유연하게(v4 핵심) · #3 12mo STOP 동의.**
> → v5 = **Aggressive Leveraged Core Beta Book.** 단 Codex 2회 REVISE 전부 반영(정직 라벨·crash-pack 가드레일).
> 상태: 방향 승인됨 + 빌드 완료(aggressive_book.py) + Codex 3회 REVISE 수용 + **forward 정량 판정표 박음 → Codex "SHIP-as-paper".** paper RESEARCH_ONLY로 가동. 실자본은 crash-pack 통과 + cap 하향(1.25~1.5x) 전 금지.
> in-sample 결과: V5 Aggressive 2016-26 +625% > QQQ +539% > SPY +301%·MDD −32%·Sharpe 0.95(≈QQQ) — **정직: 알파 아닌 레버, benign 샘플, forward −70%+ 가능.** Codex 한 문장: "이긴 게 아니라 benign 샘플서 QQQ보다 조금 더 잘 맞은 레버드 베타 북을 찾은 것, 진짜 승패는 다음 crash와 12개월 규율."

## v5 정체 (정직 — Codex 라벨 그대로)
**"crash-loss를 줄이려는 procyclical-risk-aware LEVERED BETA experiment."** 알파 아님·no-ruin 아님.
- 수익극대화 = 시장노출(레버)↑. **beat = 리스크로 산 것이지 엣지 아님**(Sharpe ≈ QQQ면 알파 0).
- 유연 = vol-target(변동성 따라 레버 조절) + DD ladder(낙폭 깊을수록 디레버). **단 이건 손실*속도* 완화지 floor 아님 — gap엔 무력**(procyclical).

## 측정 결과 (2016-26, paper, 비용후)
V5 Aggressive(vol-target 28%·캡 2.0x·ladder): 누적 **+625% > QQQ +539% > SPY +301%**, MDD **−32%**, Sharpe 0.95(≈QQQ 0.97), 평균레버 1.59x.
→ **QQQ raw를 in-sample서 넘음 + MDD도 낮음.** 단 정직: ① Sharpe≈QQQ=알파 아님(레버+vol타이밍이 COVID vol스파이크에 유리했던 샘플운). ② 2022 슬로우베어선 −31%로 SPY(−24%)보다 *나빴음.* ③ **−32%는 2016-26 conditional** — 2008/dot-com 없음.

## ⚠️ Codex REVISE 반영 (실자본 전 필수 라벨·게이트)
- **라벨: RESEARCH_ONLY / PRODUCTION_UNSAFE.** target vol 28% = 목표 아니라 tuning hypothesis. expected MDD −45~50% = *2016-26 conditional.* **forward capital-risk = possible −70%+** (레버×2008류). 2.0x = *paper max*, live candidate cap 아님.
- **가장 중요한 가드레일: cap은 crash-loss budget으로 정한다, vol-target CAGR로 정하지 않는다.** 사전등록 crash-pack(1987 −20% 1일갭·2000-02 Nasdaq·2008 GFC·2020 limit-down·2022 bear) + next-bar 디레버 지연 + 실제 차입/LETF compounding/비용. 어떤 구간서도 account DD가 사전 kill line 넘으면 → **레버 cap 자동 하향.** 통과 전 2.0x는 "상한 후보"일 뿐. **live cap 1.25~1.5x 시작.**
- **vol-target은 no-ruin floor 아님**(Moreira-Muir는 평균 위험조정 개선이지 crash-proof 아님·gap엔 추정·리밸 둘 다 늦음).
- **유연 레버 = config-mining 표면↑**(lookback·estimator·smoothing·DD rung·re-entry·rebal freq). fixed vs vol-target 판정은 CAGR 아니라 *사전등록 OOS crash-adjusted utility*로.
- **LETF/QQQ-tilt = 별도 instrument-risk sleeve**(daily-reset path dependency·SEC/FINRA 경고), core 레버와 분리 평가. "더 공격"이 아니라 "instrument risk 추가된 레버".

## ★ 12mo STOP 기준 (무한루프 차단 · 용하 동의)
- 3개월 raw로 목표 또 안 바꿈(레짐 표본).
- **12개월 forward에서: 수익만 좋고 DD/ulcer/recovery 가드레일 깨지면 → 성공 처리 금지(FAIL).** 수익-only 합격 허용하면 v5가 베타-추격으로 붕괴.
- 12mo forward에서 SPY-floor도 risk 가드레일도 못 맞추면 → **목표 또 바꾸지 말고 "쉬운 알파 없음·Core Beta 1.0x만 production-safe" 수용.** 레버는 별도 book만.

## ★ Forward 사전등록 정량 판정표 (Codex 최종: 이게 있어야 SHIP-as-paper)
사후해석 여지 = 자기기만. 12개월 forward는 아래를 *숫자로* 통과해야 'win'. **수익-only 합격 금지 — 하나라도 깨지면 FAIL.**

| 항목 | 통과 기준 | 위반 시 |
|---|---|---|
| 상방 참여(vs QQQ) | upside capture ≥ 80% | FAIL |
| MDD | ≤ −40% (account) · 하드 kill −50% | kill→레버 cap 자동 하향 |
| Ulcer index | ≤ QQQ × 1.2 | FAIL |
| 회복일수 | ≤ QQQ recovery × 1.5 | FAIL |
| 레버 cap breach | = 0 (paper 2.0x 절대초과 금지) | 즉시 FAIL |
| next-bar 체결오차 | 모델 budget 내(스프레드+슬리피지) | FAIL |
| funding/borrow | 비용 반영(미반영=UNKNOWN) | FAIL |
| 데이터 reconciliation | 미해결 UNKNOWN day = 0 (2nd 피드 필수 wiring) | FAIL |
| missed-run | fail-closed(stale 데이터에 거래 금지) | FAIL |

- **crash-pack(1987갭·2000-02·2008·2020·2022) 사전등록** — 어떤 구간서도 kill line 넘으면 레버 cap 하향. 이게 cap을 정한다(CAGR 아님).
- **behavior kill(Codex 지적): 용하가 12개월 전 목표 또 바꾸거나 −30% 근처서 수동 override = 규율 위반 = 실험 무효.**


- **알파 위성 research-OPEN 유지**(Active 1개) — 알파 찾으면 같은 수익에 *레버 덜* 써도 됨(리스크↓). MR thread1 REJECT 후 다음: quality 레짐 / MR 변형(no-trade band).
- Production 기본은 여전히 **Core Beta 1.0x(PRODUCTION_SAFE 후보)**. Aggressive는 그 위 *연구/paper* 레이어.

> **한 줄:** 네 선택(공격·리스크수용·유연)대로 **레버드 베타 북을 paper로 가동** — in-sample QQQ도 넘었다. 단 정직히: 알파 아니라 레버(Sharpe≈QQQ), −32%는 benign 샘플치고 **forward는 −70%+ 가능**, 실자본은 crash-pack로 cap 정하고 1.25~1.5x부터. 12mo guardrail 못 지키면 수익 좋아도 FAIL. 가짜 승리 거부.
