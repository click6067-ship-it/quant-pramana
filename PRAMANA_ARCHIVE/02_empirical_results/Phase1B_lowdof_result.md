# Phase 1B — Low-DoF Challenger 결과 (사전등록 1회 테스트)

**날짜:** 2026-06-11 · **데이터:** broad top-1500 PIT, 2016–2026, 122개월 · **프로토콜:** `integrated/Phase1B_LowDoF_Challenger_Protocol_v0.1.md` (결과 보기 전 박음) · **튜닝 0.**
**전제:** 어떤 결과든 live/paper 자동승격 없음. PASS는 Phase 1C 검토 후보까지만.

## 한 줄 결론

**3개 저DoF 모델(simple blend / constrained rank / ridge OOS) 전부 FAIL → US simple/linear factor family 종료(TERMINATE).**
단순 결합도, OOS 선형 회귀도 cap-weight 벤치를 못 이긴다. Phase 1A("single factor 안 됨")의 결론이 **결합/선형 단계까지 확장 확인.**

## 결과

| 모델 | Rank IC / IC-IR | net active vs CW | vs 1/N EW | 2016–20 net | 2021–26 net (IC-IR) | turnover | 판정 |
|---|---|---|---|---|---|---|---|
| A simple blend (z 동일가중) | +0.0256 / **+0.200** | **−2.44%/yr** | +1.13% | −4.50% | −0.92% (+0.306) | 238% | ❌ FAIL |
| B constrained rank (percentile) | +0.0291 / +0.190 | **−3.55%/yr** | +0.03% | −7.00% | −1.00% (+0.297) | 248% | ❌ FAIL |
| C ridge OOS (expanding, λ=5) | +0.0021 / **+0.014** | **−0.69%/yr** | +2.86% | +10.53% | **−4.83% (−0.099)** | 229% | ❌ FAIL |

## 읽는 법 (스핀 없이)

1. **cross-sectional 정보는 약하게 있다** — blend/rank의 IC-IR ~0.19–0.20, vs 1/N EW로는 미세 양수(+1.13%, ridge +2.86%). Phase 1A의 "noise는 아님"과 정합.
2. **그런데 셋 다 cap-weight 벤치를 못 이긴다** — net active vs CW가 전부 음수(−0.7 ~ −3.6%/yr). long-only는 인덱스만 드는 것보다 나쁨. 결합이 long-leg를 살리지 못함(quality 단독 +1.79% → blend +1.13%로 오히려 약화 = 죽은 팩터를 섞으면 희석).
3. **OOS ridge가 결정타** — 가중을 실제로 데이터에 적합해 *미래*를 예측하면 IC-IR **0.014**(완전 0). 2016–20 +10.53% → 2021–26 **−4.83%(IC-IR −0.099)**. 초기 레짐 과적합이 OOS에서 반전 = 교과서적 in-sample 환상. **정직하게 fit하면 edge 없음.**
4. **최근 절반(2021–26) 전 모델 net 음수** — decay가 결합으로도 복구 안 됨.

## 판정 (사전등록 규칙 적용 — goalpost 불변)

- 6개 kill 조건 중 각 모델이 다수 발동(net vs CW≤0 · long-only 음수 · 2021–26 net≤0 · ridge는 recent IC-IR<0.10·sector중립화후 음수).
- **3/3 FAIL → US simple/linear factor family TERMINATE.**
- **no live / no paper. no tuning to rescue.**
- → 다음: **KR arena 또는 다른 edge source 검토** (단순·선형·결합 패러다임은 미국 중대형에서 닫힘).

## 의미

Phase 1A + 1B = **미국 중대형(top-1500, 2016–2026)에서 공개된 단순 팩터를, 단독으로도 저DoF 결합으로도, 거래 가능한 standalone edge로 만들 수 없다.** 정보는 약하게 있으나(IC>0, vs EW 미세 양수) cap-weight를 못 이기고 최근 소멸. factor-decay / Alpha Illusion prior-art와 강하게 정합. 검증 시스템이 의도대로 작동 — **가짜 알파를 두 단계에서 죽였다.**
