# Alpha Lab MT-1 — Daily Re-entry Ladder 결과 → **DEAD (마켓타이밍 4번째 negative·종료)**

> 사전등록: `PRAMANA_V4/MT1_Daily_Reentry_Ladder_Protocol.md` · 코드: `phase1a/engine/mt1_daily_ladder.py`
> 질문: 4-sleeve 코어 + QQQ overlay를 *단계적 ladder*로 조절하면 binary throttle보다·static보다 나은가?
> 비용후·proxy·in-sample·PAPER·자본권한 0. 2026-06-12.

## 판정 한 줄
**MT-1 ladder = DEAD.** static 4-sleeve(Sharpe 1.20)를 못 이김(ladder 1.08). 단계적이 binary(1.06)보다 미세 우위(+0.02)지만 **둘 다 static 못 이김.** → **느린 일봉 risk-score 기반 코어/overlay 마켓타이밍 종료(4번째 negative)·V7 생존코어 *후보* 확정.**
> *Codex 정밀화: "마켓타이밍 *전체* 사망"이 아니라 "*느린 일봉 risk-score 기반* 코어/overlay timing 사망"(빠른/선행 신호는 미검증·단 prior 낮음). V7은 생존코어 *후보*지 production-safe 아님(PAPER/forward 12mo/2-feed/crash-pack 남음).*

## 결과 (풀 2019~·비용후)
| 북 | 누적% | MDD% | Sharpe | turn/yr |
|---|---|---|---|---|
| static QQQ | +305 | −35 | 0.94 | 0.1 |
| **static 4-sleeve** | +175 | **−18** | **1.20** | 0.0 |
| binary throttle | +185 | −21 | 1.06 | 2.9 |
| **MT-1 ladder** | +202 | −22 | **1.08** | 2.5 |

## 사전등록 kill 대조
| # | 조건 | 결과 |
|---|---|---|
| 1 | ladder가 static 4-sleeve Sharpe 못 이김 | ❌ **FAIL** (1.08 < 1.20·MDD −22% vs −18%) |
| 2 | binary보다 나은 게 없음 | △ ladder +0.02 미세 우위(하지만 #1로 무의미) |
| 4 | crash-pack 방어 의미 없음 | ❌ 전 crash서 static에 짐 |

→ **kill #1 발동 → DEAD.**

## crash 윈도우 (전부 static 4-sleeve에 짐)
| crash | static 4-sleeve | MT-1 ladder |
|---|---|---|
| 2020 COVID | +6.4 / −18 / 0.64 | +5.3 / −22 / 0.53 |
| 2022 bear | −9.9 / −12 / −0.70 | −20.6 / −22 / −1.36 |
| 2008 GFC (proxy) | +0.9 / −27 | −2.9 / −32 |
| **2000 닷컴 (proxy)** | **−12 / −22** | **−41.5 / −50** |

## ★ 결정타 — 2000 닷컴 (두 원인이 섞임·Codex #3)
overlay(QQQ)가 닷컴서 **−83%** 박살나는데, risk_score(200dMA·vol·DD)는 **후행 신호**라 ladder가 단계적으로 빼봤자 **MDD −50%**(static 4-sleeve −22%보다 2배 이상). **두 원인이 섞임:** ① QQQ overlay 독성(닷컴 −83% 직접 노출) ② 느린 SPY 신호 후행(급락 초반 못 피함). = "모든 마켓타이밍이 폭락 못 피함"의 증명이 아니라 **"QQQ overlay를 느린 SPY 위험신호로 조절하는 설계는 닷컴형 crash에 부적합"**의 증명. 단계적이든 binary든 *느린 신호*로는 "늦게 빼는" 본질이 같다.

## 마켓타이밍 4전 4패 (종료 근거)
| # | 실험 | 형태 | 결과 |
|---|---|---|---|
| 1 | regime_switch_test | 단계적 코어전환(growth↔survival) | static 못 이김(0.91<1.07) |
| 2 | crash_pack_throttle | binary overlay | static 못 이김·반등 놓침 |
| 3 | derisk_test | 추세→현금 | 휩쏘·full −50%p |
| 4 | **MT-1** | **단계적 overlay(안 본 조합)** | **static 못 이김(1.08<1.20)·닷컴 −50%** |

**코어/overlay × binary/단계적 × 전환/현금 — 모든 조합이 static 4-sleeve를 못 이긴다.** 공통 killer = **후행 신호의 본질**(늦게 팔고 늦게 사서 휩쏘·폭락 못 피함).

## 결론
- **MT-1 = DEAD. 느린 일봉 risk-score 기반 코어/overlay 마켓타이밍 종료(4번째 negative).**
- **ORB/VWAP/RVOL 2단계 = 안 감** — 1단계(일봉 ladder) DEAD인데 분봉 센서 추가는 *실패한 daily timing에 intraday 자유도를 얹는 구제책*(Codex #5). v2 event-driven은 별도 research로만.
- **V7 4-sleeve = 생존코어 *후보* 확정**(current survivor·단 PAPER/forward 12mo/2-feed/crash-pack 남음·production-safe 아님). "상승 먹고 하락 피하기"는 *느린 일봉 신호로는* 솔로가 못 한다.
- 옵션 컨벡시티(선행적 보호)만 이론상 다르나(비용·과최적화) 별도·후순위.
- **구현 caveat(Codex #6):** proxy 구간(2008/2000) risk_score가 실 SPY 기준인데 book은 VFINX proxy → "SPY signal vs VFINX signal" 민감도 1회 확인 권고(치명 아님·결론 불변·재튜닝 금지).

## Codex 적대검증 VERDICT (no-echo)
**"DEAD 확정·코어 마켓타이밍 종료·2단계로 구제 금지."** ① 불리 설계 아님(고정 파라미터·lower OV_MAX는 static 수렴·higher는 손실↑·결과 후 만지면 config-mining) ② ladder +0.02는 존재이유 아님(kill #1은 static 초과) ③ 2000 닷컴 = overlay 독성 + 후행 섞임(전체 timing 사망 아니라 느린 SPY 신호 부적합) ④ V7=생존코어 후보지 production-safe 아님 ⑤ 2단계 센서는 실패한 timing 구제책=금지·v2는 별도 research ⑥ proxy signal 민감도 1회 확인. **가장 먼저 볼 1개: MT-1 파라미터가 아니라 Alpha Lab v2 catalyst forward log — 코어 timing 닫고, 남은 질문은 "검증된 공격 알파가 있나".**
