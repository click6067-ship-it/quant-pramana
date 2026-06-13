# PRAMANA Graveyard Revival Board — 폐기 전략 부활 검토

> **목적:** 8세대에서 폐기된 전략을 *전부* 다시 펼쳐 — 용하가 직접 **부활(역할)/영구 격리**를 판정한다.
> 각 전략: **실험 의도 · 상황/설계 · 결과(수치) · 죽은 이유 · A2 부활 가능성 · [판정란]**.
> **정렬: "수치상 아쉽게 죽은 것"부터.** 원자료 = `PRAMANA_All_Experiments_Ledger.md` · `PRAMANA_Conclusions_OneLine.md` · `phase1a/reports/*.md`. 작성 2026-06-13.
> **핵심 원칙(8세대 결론):** standalone *알파*로 부활할 건 없다. 단 **역할을 바꾸면**(매수신호→confirmation·숏→Gate·코어타이밍→dashboard) A2의 부품으로 재활용 가능.

---

## A. 부활 1순위 — 수치상 아쉽게 죽은 것 (수익은 보였으나 규칙/구조에 막힘)

### A-1. Momentum (broad 12-1) — *가장 아쉬움(net 양수)*
- **의도:** 최근 12개월−1개월 수익 상위 종목이 broad 유니버스(top-1500)에서 추세 지속하나.
- **상황/설계:** top-1500 PIT(시총·유동성 필터)·비용 tier 5/10/15bp·turnover 측정·net Q5−Q1·size-bucket IC·**사전등록 kill조건**(IC-IR<0.2 or turnover 과도 or 소형집중 → DEAD).
- **결과:** **net +7.6%/yr (양수!)** · 단 **IC-IR 0.10**(임계 0.2의 절반) · **turnover 301%**(과도).
- **죽은 이유:** 사전등록 규칙 위반 — 수익은 났으나 *신호 불안정 + 회전비용 과다*. goalpost 안 옮김(규율).
- **A2 부활 가능성:** Attack sleeve의 **단기 모멘텀 confirmation**(catalyst 종목의 추세 확인) 또는 후보 랭킹 보조. ⚠️ standalone 알파 아님.
- **[판정: ⬜ 부활(역할: ____) / ⬜ 격리]**

### A-2. Quality (broad, gross profitability gp/assets)
- **의도:** Novy-Marx 총수익성(매출총이익/자산)이 broad에서 프리미엄 주나.
- **상황/설계:** PIT-by-datekey(미래정보 차단)·비용후·대형/소형 size-bucket IC·quarantine 추가검증(다중검정·DSR/PBO·subperiod·2x cost).
- **결과:** Rank IC-IR **0.22**(임계 0.2 *간신히* 통과) · net **+4.4%/yr** · 대형/소형 일관 · Novy-Marx 정합 → quarantine서 **decay 발각: 2021-26 IC-IR 0.046** · long-only vs cap-weight **−1.15%**.
- **죽은 이유:** 최근 5년 신호 식음(decay) + long-only는 메가캡 cap-weight 못 이김.
- **A2 부활 가능성:** Attack/Moonshot 종목 **품질 필터**(쓰레기 거르기·NEG Gate 보완). standalone 아님.
- **[판정: ⬜ 부활(역할: ____) / ⬜ 격리]**

### A-3. Event / Earnings drift (PEAD)
- **의도:** 실적 surprise 후 drift(post-earnings-announcement drift) 포착.
- **상황/설계:** 숫자 surprise 기반·next-bar 진입·비용후·long-short vs long-only 분리.
- **결과:** **long-short +4.4%**(양수) · 단 **long-only net vs CW −0.90%** · 공매도 솔로 불가 · *decay는 안 함(정보는 있음)*.
- **죽은 이유:** 알파가 short 다리에 있는데 **공매도 솔로 불가** + long-only는 메가캡 벽.
- **A2 부활 가능성:** Attack **catalyst 트리거**(실적 서프라이즈 종목 = catalyst 후보·long-only 진입 타이밍). EDGAR 8-K Item 2.02와 연결.
- **[판정: ⬜ 부활(역할: ____) / ⬜ 격리]**

### A-4. LETF convex (long-vol convexity)
- **의도:** 레버 ETF의 볼록성(상승 가속)을 소량 dose로 활용.
- **상황/설계:** trend+LETF 위성(70/25/5)·convexity vs naive 레버 비교·결합 dose 측정.
- **결과:** **SURVIVE(약)** — convexity가 naive 레버를 못 넘으나 결합서 *소량 dose*는 의미.
- **죽은 이유:** 약하게 살아있으나 standalone 부족.
- **A2 부활 가능성:** **A2 TQQQ 사이징 보조**(convex dose 관리·Beta Governor와 연동). A2 핵심과 이미 정합.
- **[판정: ⬜ 부활(역할: ____) / ⬜ 격리]**

### A-5. V5 Leveraged Core (cap 2.0x)
- **의도:** Core Beta에 레버를 걸어 절대수익 증폭.
- **상황/설계:** vol-target 28%·캡 2.0x·DD ladder·in-sample 2016-26.
- **결과:** in-sample **+625% > QQQ +539% > SPY +301%** · 단 **Sharpe 0.95 ≈ QQQ**(레버일 뿐 알파 아님) · 같이 −32% 낙폭 · forward −70% 가능.
- **죽은 이유:** 누적은 이겼으나 위험조정 동급 = 레버드 베타(알파 아님)·benign 샘플.
- **A2 부활 가능성:** **이미 A2 TQQQ Booster로 부활**(의식적 리스크 베타로 정직 라벨·Vault/ladder로 관리). 부활 아니라 *재정의 채택*.
- **[판정: ✅ A2 TQQQ로 채택됨]**

---

## B. 역할 변경 부활 후보 (예전 역할 ❌ → 새 역할 ⭕)

### B-1. ORB/VWAP/RVOL (Alpha Lab v1 — DEAD)
- **의도(원래):** 급등주 intraday *매수 신호*(gap-up+RVOL+ORB15+VWAP).
- **결과:** **DEAD** — RVOL look-ahead 누수 수정 후 중앙 **−0.41%**·승률 41%·**false breakout 56%**(과반)·SPY 하락일 −0.99%.
- **죽은 이유:** 매수 *신호*로는 강세장 베타 + 누수. (Codex: watchlist selection 편향·flat-bp 비용 비현실.)
- **역할 변경:** 매수 신호 ❌ → **Attack confirmation sensor ⭕**(catalyst가 총알·이건 "시장이 그 catalyst를 인정하는지" 확인). **A2 §6.3 이미 반영.**
- **[판정: ⬜ 부활(confirmation sensor) / ⬜ 격리]**

### B-2. NEG 8-K (QL-1B)
- **결과:** NEG 공시(희석/회계/상폐) 후 **−0.75% 일관**·승률 42% — **8세대 유일 일관 directional 신호.**
- **역할 변경:** 숏 신호 ❌ → **매수 금지 필터(NEG Gate) ⭕**. **A2 §4.6 이미 승격 채택.**
- **[판정: ✅ NEG Gate로 채택됨]**

### B-3. Trend (마켓타이밍 4전4패)
- **결과:** regime_switch(Sharpe 0.91<1.07)·throttle(REJECT)·derisk(휩쏘)·MT-1 ladder(1.08<1.20) — 전부 static 4-sleeve 못 이김. **공통 killer = 후행 신호.**
- **역할 변경:** 코어 전환 신호 ❌ → **Risk Dashboard 입력 ⭕**(Leadership Risk·Market Stress의 한 요소·*자동매도 아님*·신규/증액 게이트만). A2 §4 반영. ⚠️ Codex: 느린 일봉 timing만 죽음·빠른/선행 신호는 미검증.
- **[판정: ⬜ 부활(dashboard 입력) / ⬜ 격리]**

### B-4. v2 Event-driven momentum
- **결과:** 약함 — catalyst 없는 순수 momentum·**테마 88% 집중·SPY 상승일 80%** = 강세장/테마 베타. forward 관찰 중.
- **역할 변경:** standalone ❌ → **Attack catalyst 후보 generator ⭕**(forward 로그 + LLM A/B 분류). A2 Attack 입력단.
- **[판정: ⬜ 부활(catalyst generator) / ⬜ 격리]**

### B-5. Delayed Recognition (미검증)
- **의도:** 좋은 공시인데 당일 반응 약함 → 3~10일 후 거래량/가격 붙음.
- **상태:** **미검증(안 해봄)** — 아쉽게 죽은 게 아니라 *미탐색*. "남들이 덜 본 것"에 가장 가까움(해석 지연 게임 = 솔로+LLM 덜 불리).
- **역할:** **A2 Attack 'B' 후보**(§6.3).
- **[판정: ⬜ 부활(Attack B) / ⬜ 보류]**

---

## C. 영구 격리 (부활 금지 — 구조적으로 위험/무용)
| 전략 | 결과(수치) | 격리 이유 |
|---|---|---|
| **VRP short-vol** | worst month −62% · maxDD **−92%** | 꼬리가 계좌를 죽임 · A2 convex(롱 볼)와 정반대 |
| **Short-term reversal** | net −4% · **turnover 3660%** | 회전비용이 알파 초과 |
| **V8 Levered 4-sleeve** | 닷컴 proxy **−49%** · 전부 −35% 초과 | 레버 분산북 꼬리 (A2는 TQQQ로 레버하되 분산북 레버는 ❌·Vault/ladder로 관리) |
| **v1 look-ahead 오염 수치** | (RVOL 누수 전 원래 수치) | 오염 = 증거 불가(수정 후 DEAD) |
| **Raw MVO** | DR-4 reject·1/N 못 이김 | 추정오차 증폭(DeMiguel 2009) |
| **단순팩터 standalone**(value/lowvol) | Rank IC ≈ 0 | 신호 자체 없음 |

---

## D. 미탐색 (부활이 아니라 *안 해본 것* — A2의 새 연료)
- **정성 텍스트 + LLM** (8-K 본문·실적콜·뉴스): 유일하게 안 본 진짜 축. A2 catalyst 분류·Moonshot thesis의 LLM bull/bear로 *부분* 진입(확률은 사람).
- **옵션 컨벡시티:** 상승참여+하락보호. 비용(프리미엄 드래그)·과최적화로 후순위.
- **KR small/mid:** 덜 효율적이나 세금/체결/구조 새 리스크.

---

## E. 판정 요약 (용하 기입란)
| # | 전략 | 죽은 핵심 수치 | Claude 제안 역할 | 용하 판정 |
|---|---|---|---|---|
| A-1 | momentum broad | net +7.6%·IC-IR 0.10·turnover 301% | Attack 모멘텀 confirm | ⬜ |
| A-2 | quality broad | IC-IR 0.22→0.046 decay·net +4.4% | 종목 품질 필터 | ⬜ |
| A-3 | event drift | long-short +4.4%·공매도 불가 | Attack catalyst 트리거 | ⬜ |
| A-4 | LETF convex | SURVIVE 약·소량 dose | TQQQ 사이징 보조 | ⬜ |
| A-5 | V5 Leveraged | +625%·Sharpe≈QQQ | A2 TQQQ로 채택 | ✅ |
| B-1 | ORB/VWAP/RVOL | 중앙 −0.41%·false 56% | Attack confirmation sensor | ⬜ |
| B-2 | NEG 8-K | −0.75% 일관 | NEG Gate | ✅ |
| B-3 | trend | 4전4패·후행 벽 | Risk Dashboard 입력 | ⬜ |
| B-4 | v2 event momentum | 테마 88%·SPY 80% | Attack catalyst generator | ⬜ |
| B-5 | delayed recognition | 미검증 | Attack 'B' 후보 | ⬜ |
| C | VRP·reversal·V8·MVO·단순팩터 | −92%·3660%·−49% 등 | 영구 격리 | ⬜ |

---
> **한 줄:** 8세대 폐기 전략 중 *standalone 알파로 부활할 것은 없다*(momentum +7.6%·quality +4.4%·event long-short +4.4%도 전부 공매도불가·회전비용·decay·메가캡 벽에 막힘). 단 **역할을 바꾸면** A2의 부품(confirmation·Gate·dashboard·catalyst generator)으로 재활용 가능. *진짜 새 연료는 폐기 부활이 아니라 미탐색 축(정성 LLM)이다.*
