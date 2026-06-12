# PRAMANA 실험 결론 — 한 줄 압축 (자동 취합)

> 각 실험을 **한 줄 결론**으로. 새 실험은 맨 아래 카테고리에 1줄 추가(규율: CLAUDE.md/AGENTS.md NOW에 명시).
> 상세 = `PRAMANA_All_Experiments_Ledger.md` · 원자료 = `phase1a/registry/phase1a_milestones.csv`. 갱신 2026-06-13.

## 정량 cross-sectional (v1 · Phase 1A/1B)
- **B0/B1 데이터 sanity** → PASS. 파이프라인 정확(PIT cap-weight vs SPY corr 0.998) = 자산.
- **B2~B5 단순팩터**(value/mom/quality/lowvol) → 신호 없음(Rank IC ≈ 0).
- **B3 quality quarantine** → FAIL(IC-IR 0.22→0.046 식음·long-only vs CW −1.15%).
- **Phase 1B 결합**(ridge/blend/GBM) → FAIL(OOS net vs CW 음수·결합도 cap-weight 못 이김).
- **US event/earnings drift**(숫자 surprise) → FAIL(net vs CW −0.90%).
- **US small/mid·True PEAD·revision** → FAIL/미완.
- **→ US 공개 cross-sectional CLOSED**: 6 family 전멸·killer = 메가캡 cap-weight 벽(신호 무관).

## 풀북 / Trend / 레버 (v3)
- **trend+LETF 위성** → 알파 아님(+0.15%/yr 노이즈).
- **VRP short-vol** → REJECT(tail −92%).
- **LETF convex** → SURVIVE(약·결합서 소량만).
- **단기 reversal** → FAIL(turnover 3660%).
- **v3 풀북** → SPY를 위험조정으로 못 이김(3x는 레버지 엣지 아님).
- **bake-off(ridge/GBM)** → ML이 선형 못 넘음(GKX ML OOS R² 0.4%와 일치).

## Core-satellite / 분산 / 레버 (V4~V8)
- **V4 Core Beta 1.0x** → 베타북·알파 아님·QQQ 못 넘음(설계상).
- **V5 Leveraged** → in-sample QQQ 넘김 but Sharpe≈QQQ = 레버지 알파 아님·같이 낙폭.
- **V6 Diversified(+DBMF)** → 낙폭 완화·but 보험료(상승장 수익↓).
- **V7 4-sleeve(현 코어)** → 생존코어(Sharpe 1.21·MDD −18% 최선·단 누적 절반·닷컴 proxy −39%).
- **V8 Levered 4-sleeve** → REJECT/UNKNOWN(실 SPY/QQQ crash-pack 닷컴 −49%·1.35x+ 폐기).

## 마켓타이밍 (4전 4패)
- **regime_switch**(코어 전환) → 휩쏘(Sharpe 0.91 < static 1.07).
- **throttle**(binary overlay) → REJECT(static 못 이김·반등 놓침).
- **derisk**(현금화) → 휩쏘(full −50%p).
- **MT-1 ladder**(단계적 overlay) → DEAD(1.08 < static 1.20·닷컴 −50%). **공통: 후행 신호 벽.**

## Alpha Lab (intraday / event / 정성)
- **v0 intraday infra** → BUILT(setup 검출 PASS).
- **v1 단순 setup**(ORB/VWAP/RVOL) → DEAD(RVOL 누수·중앙 −0.41%·강세장 베타).
- **v2 event-driven momentum** → 약함(테마 88%·SPY 상승일 80% = 베타).
- **QL-1 8-K event drift**(LLM 前) → 약한 흔적·거래 알파 아님(중앙 −0.32%·승률 48%·비용 전).
- **QL-1B 8-K Item bucket(OOS)** → **POS(좋은 공시 사기) OOS FAIL** · **NEG(나쁜 공시 피하기) 일관 신호**(−0.75%·승률 42%) = *사는 알파 없음·피하는 필터는 있음*.

## 구조/프론티어
- **upside/downside frontier** → "상승 다 먹고 하락 방어"는 자산배분으로 불가(프론티어 위 이동뿐).

---
## 메타 결론 (한 줄)
**솔로가 공개 데이터로 SPY/QQQ를 *위험조정 초과*하는 "사는" 알파 = 8세대+QL-1로 거의 없음(robust negative). 건진 것: V7 생존코어 · 나쁜-공시 회피 필터 · 가짜-알파 면역.**

<!-- 새 실험 1줄 추가 지점 (날짜·실험명 → 결론) -->
