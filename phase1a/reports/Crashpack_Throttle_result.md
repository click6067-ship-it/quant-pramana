# Crash-Pack × Brake-Only Throttle — 결과 (사전등록 대조)

> 사전등록: `PRAMANA_V4/Crashpack_Throttle_Protocol_v0.1.md` · 코드: `phase1a/engine/crash_pack_throttle.py`
> 질문(딱 하나): *4-sleeve 고정 코어 + 공격 overlay(3x LETF)에 brake-only throttle*이 crash-pack서 값어치 있나?
> 데이터: proxy=**stress 신호지 실증 아님**(VFINX·RYMFX·GC=F·VFITX·2000-02 MF=cash·1987 eq+bond). PAPER·RESEARCH_ONLY. 2026-06-12.

## 판정 한 줄
**throttle = 사전등록 PASS 실패 → 대시보드/정보용 유지(risk-engine 승격 ❌).** 그리고 더 큰 발견: **LETF overlay를 코어에 붙이는 것 자체가 위험조정 손해** — static 4-sleeve가 overlay 붙인 모든 북을 crash마다 이긴다.

## 핵심 수치 (overlay w=20% 대표 · crash 윈도우)
| crash | 북 | tot% | MDD% | Sharpe | UW일 |
|---|---|---|---|---|---|
| **2008 GFC** (4-sleeve 전부 proxy) | static 4-sleeve | +0.9 | **−27** | **0.11** | 409 |
| | 4sl+overlay 고정 | −20.4 | −53 | −0.14 | 546 |
| | 4sl+overlay+THROTTLE | −13.3 | −32 | −0.37 | 546 |
| **2000 닷컴** (MF=cash) | static 4-sleeve | −12.0 | **−22** | **−0.32** | 582 |
| | 4sl+overlay 고정 | −35.0 | −46 | −0.52 | 695 |
| | 4sl+overlay+THROTTLE | −20.9 | −26 | −0.62 | 742 |
| **2022 bear** (트랙 A 실 ETF) | static 4-sleeve | −9.9 | **−12** | **−0.70** | 191 |
| | 4sl+overlay 고정 | −29.8 | −31 | −1.04 | 250 |
| | 4sl+overlay+THROTTLE | −14.7 | −16 | −1.25 | 250 |
| **1987** (eq+bond·단일샘플) | static 4-sleeve | +9.5 | −18 | 0.49 | 215 |
| | 4sl+overlay 고정 | +12.0 | −34 | 0.41 | 215 |
| | 4sl+overlay+THROTTLE | **+21.2** | −20 | **0.89** | 215 |

## 사전등록 5조건 대조
| # | PASS 조건 (vs overlay-고정·vs static 4-sleeve) | 결과 |
|---|---|---|
| 1 | crash MDD 감소 | ✅ **충족**(모든 crash·w↑일수록 큼: w20% +13.9~21.2%p) |
| 3 | crash 손실 감소 | ✅ **충족**(일관) |
| 2 | 회복기간(UW) 단축 | ❌ **실패** — UW 미개선/증가. throttle이 200일선 아래서 overlay 끄면 **반등도 놓침**(2008/2000 발동 506/633일=거의 내내 off→회복 지연) |
| 4 | 비위기 수익 훼손 과하지 않음 | △ overlay-고정 대비는 +지만, **static 4-sleeve 대비론 throttle도 음수**(overlay 붙인 순간 진다) |
| 5 | thr Sharpe > static 4-sleeve (복잡도 정당화) | ❌ **실패** — 거의 전 구간 −0.11~−0.55. **1987만 예외**(+0.12~0.40·단일 379일·MF/gold=cash 40%=노이즈 의심) |

→ **#2·#5 실패 → throttle 기각.**

## 무엇이 진짜 드러났나
1. **throttle은 반창고지 알파 아님.** crash 손실은 확실히 줄인다(LETF가 daily-reset으로 박살나기 전에 끔). 하지만 ① 후행 신호라 gap(1987 Black Monday) 못 피하고 ② 200일선 아래 장기 체류시 반등 놓쳐 회복 지연.
2. **이 형태의 overlay가 가치 파괴.** static 4-sleeve가 overlay 붙인 어떤 북보다 crash Sharpe 높고 MDD 낮음. throttle로도 static 4-sleeve 이상으로 복구 못 함. → **코어에 *이 형태로*(core-attached LETF + binary brake) 레버드 공격을 섞지 말 것.** *(Codex no-echo 교정: "overlay의 *모든* 형태가 무용"은 과잉일반화. 죽은 건 정확히 **사전등록 brake-only binary throttle + core-attached LETF**다. static 4-sleeve 우월 결론만 robust.)*
3. **V7 구조가 데이터로 재확인:** 코어 = 순수 4-sleeve(레버/overlay 없음), 공격 알파는 **Alpha Lab(paper·격리)**에서 별도 사냥. 코어-부착 하이브리드(overlay+throttle)는 폐기.
4. **정직한 양면(no-echo):** throttle을 *옹호*할 유일한 조건 = "어떤 이유로 LETF overlay를 *반드시* 들어야 한다면, throttle로 끄는 게 안 끄는 것보다 낫다"(crash MDD 일관 감소는 진짜). 그러나 그 전제(LETF를 들어야 함)가 기각되므로 moot.

## 한계 (proxy)
VFINX(QQQ 성장틸트 제거)·RYMFX(DBMF와 운용 다름)·GC=F(GLD 추적오차)·2000-02 MF=cash(25% 무수익=4-sleeve에 유리하게 편향)·1987 단일이벤트. **방향성 stress 신호지 backtest 진실 아님.** 단 결론(static 4-sleeve 우월·overlay 무용)은 4개 독립 crash + 3개 w에서 일관 → robust.

## Codex 적대검증 VERDICT (no-echo·2026-06-12)
**"throttle = 기각, 대시보드 전용. risk-engine 승격 ❌."** — 내 판정에 동의. 6지적:
1. **DD<−10%가 recovery서 throttle 영구 OFF** — 2008/2000 발동 506/633일은 *불리한 설계가 아니라 brake-only 규칙의 본질적 실패*. re-entry/hysteresis는 새 실험(현재 패배 못 되돌림).
2. **LETF 합성 비용은 결론 못 뒤집음** — RF=5% 고정·0.95% expense(실 TQQQ 0.84%)는 약간 불리하나, Sharpe 열위 −0.11~−0.55·MDD 수십%p를 10~100bp 보정으론 못 구함.
3. **overlay-off=cash는 brake-only 정의 그대로** — 코어 재배분하면 "tactical reallocation"=새 자유도=사전등록 없이 살리면 config-mining.
4. **proxy 한계는 결론을 *강화*** — VFINX는 QQQ 성장틸트 제거→실제 dot-com overlay 손상 *더* 컸을 것·2000-02 MF=cash는 static에 불리한데도 static이 이김.
5. **1987 예외는 신호 아님** — 단일 379일·MF/gold=cash. + **프로토콜-코드 불일치**(프로토콜 "synthetic −20% gap" 적었으나 코드는 실데이터 Black Monday 사용·gap 삽입 없음). → 정정함(아래).
6. **핵심은 throttle이 아니라 overlay 자체의 음의 한계기여** — 이미 LOCK된 *trend+LETF 위성 +0.15%/yr 노이즈*와 같은 방향. throttle은 나쁜 overlay의 왼쪽 꼬리만 자른 것.
- **교정 수용:** "overlay 모든 형태 무용"은 과잉일반화 → 죽은 건 **사전등록 brake-only binary throttle + core-attached LETF**. static 4-sleeve 우월만 robust 결론.
- **1987 불일치 정정:** 코드는 1987 **실데이터**(VFINX에 Black Monday −20% 이미 포함) 사용 → synthetic gap 불필요·미구현이 맞음. 프로토콜 v0.1 문구를 실데이터로 정정. **판정 불변**(1987 빼도 2020·2022·2008·2000서 #2·#5 실패 남음).

## 결론 / 다음
- **throttle:** risk-engine 승격 **기각 확정** → **대시보드/정보용 유지**(Risk Monitor 표시만·라벨 NEEDS_EVIDENCE→REJECTED-for-promotion).
- **코어:** 순수 4-sleeve paper forward 유지(이 형태 overlay 안 붙임).
- **알파:** 급등주/단타는 Alpha Lab(paper·자본권한 0)에서 별도. 코어와 안 섞음.
- **재실험 금지:** re-entry/hysteresis/단계적 throttle/overlay-재배분은 *전부 새 자유도* → 사전등록 없이 돌리면 config-mining. 현재 결과의 패배는 확정.
