# V8 Candidate — Levered 4-sleeve crash-pack 결과 → **기각 (V7 1.0x 유지)**

> 사전등록: `PRAMANA_V4/V8_Candidate_Levered4sleeve_Protocol.md` · 코드: `phase1a/engine/v8_levered_crashpack.py`
> 가설: V7 분산북을 레버(1.25~1.5x)하면 상승참여↑ 유지하며 crash MDD가 A1 Aggressive(−35%) 이내인가?
> **명확히: 알파 아님 = 분산 프리미엄 레버 = 목적함수 이동.** proxy·in-sample·PAPER. 2026-06-12.

## 판정 한 줄 (보정·UNKNOWN nuance)
**V8 (Levered 4-sleeve) = 보수적 기각(닷컴 equity tail·Codex fail-close) · V7 1.0x 유지.** 단 **기각 신뢰도는 제한적 = UNKNOWN 잔존**: worst를 지배하는 2000 닷컴이 **MF=cash(DBMF proxy 부재·4-sleeve에 불리)**다. **2008(완전 proxy)만 보면 1.25x −32%로 통과**·1.35x+는 2008서도 −35%라 명확 폐기. = 1.25x는 "2008 통과·2000 불확실"이지 단정적 전멸 아님.

## 1.10~1.25 grid 대조 (GPT 요청·실 SPY/QQQ) — 판정은 2000 MF 부재에 달림
| 레버 | 2008 GFC (MF=RYMFX) | 2000 닷컴 (MF=cash) | 상승참여 |
|---|---|---|---|
| 1.0x | −26% | −39% | 53% |
| 1.10x | −29% | −43% | 57% |
| 1.20x | −31% | −47% | 62% |
| **1.25x** | **−32% ✅** | **−49% ❌** | 64% |
| 1.35x | −35% | −52% | 68% |
| 1.5x | −38% | −57% | 75% |
→ **2008 기준 cap=1.25x · 2000(MF부재) 기준 cap=0(무레버도 실패).** 진짜 4-sleeve(DBMF 포함)가 닷컴류에 어떻게 방어하나 = 무료로 확인 불가 = **핵심 미해결.**

## ★ Codex가 잡은 결함 — equity proxy 누락 (verify-before-done 승리)
- **초기 실수:** 장기 crash-pack의 equity sleeve를 `VFINX`(S&P500) 단일로 씀. 그런데 V7 equity는 **SPY/QQQ 50/50**이고 **QQQ는 닷컴 −78%**. → VFINX(−49%)만 쓰면 equity tail을 과소평가.
- **수정:** 2000·2008 equity를 **실 SPY/QQQ 50/50**(둘 다 1999~ 존재)로 재실행.
- **결과 반전:**

| crash | 지표 | VFINX proxy(틀림) | **실 SPY/QQQ(맞음)** |
|---|---|---|---|
| 2000 닷컴 | 1.0x MDD | −22% | **−39%** |
| 2000 닷컴 | 1.25x MDD | −29% | **−49%** |

## crash-pack 재판정 (실 SPY/QQQ·worst MDD per 레버)
| crash 윈도우 | 1.0x(V7) | 1.25x | 1.35x | 1.5x |
|---|---|---|---|---|
| 2020 COVID | −18% | −22% | −24% | −26% |
| 2022 bear | −12% | −16% | −17% | −19% |
| 2008 GFC (실 SPY/QQQ) | −26% | −32% | −35% | −38% |
| **2000 닷컴 (실 SPY/QQQ)** | **−39%** | **−49%** | **−52%** | **−57%** |
| 1987 | −18% | −23% | −24% | −27% |
| **worst-crash MDD** | **−39%** | **−49%** | **−52%** | **−57%** |

## 사전등록 판정 (kill = worst-crash MDD ≤ −35%)
| 레버 | worst MDD | ≤ −35%? | 판정 |
|---|---|---|---|
| 1.0x | −39% | ❌ | (V7·아래 단서) |
| 1.25x | −49% | ❌ | **FAIL** |
| 1.35x | −52% | ❌ | FAIL |
| 1.5x | −57% | ❌ | FAIL |

→ **모든 레버 FAIL → V8 기각 → V7 1.0x 유지.**

## Codex 적대검증 VERDICT (no-echo)
**"더 보수적 cap. V8 1.25x 승격 반대 — borderline, proxy-error-adjusted FAIL/UNKNOWN."** 6지적(전부 수용):
1. 1.25x −34%(초기)는 −35% 한계에 1%p 마진 + A1 −35% 자체가 "임시·미확정" → 미확정 임계에 1%p로 붙으면 **threshold fitting**. risk budget은 fail-close.
2. **equity proxy(VFINX 단일)가 레버 위험 과소평가** — V7은 SPY/QQQ 50/50·QQQ 닷컴 −78%. → 수정함(위·판정 뒤집힘).
3. 2008 MF proxy(RYMFX≠DBMF) 대표성 부족 — proxy 오차 1~3%p면 탈락.
4. 비용 관대 — financing만·차입스프레드/expense/rebalance/crash liquidity 0 → 현실화하면 더 깊음.
5. +11%p 상승참여는 개선 아니라 **위험예산 재배치**(frontier 이동)·crash budget 거의 소진.
6. V5와 구조는 다르나 **ruin operator(gap·correlation break·margin·forced deleveraging) 동일** → in-sample −34%를 "생존"으로 읽으면 안 됨.

## 무엇이 드러났나
1. **레버는 닷컴류(QQQ 중심 폭락)에서 죽는다.** 1.25x도 2000 닷컴 −49%. 분산북 레버라도 equity tail이 QQQ면 레버가 증폭. V8 = 명확히 기각.
2. **★ 더 중요: V7 1.0x조차 2000 닷컴 proxy에서 −39%** (A1 Aggressive −35% 초과). 멀티앵커의 "V7 MDD −18%"는 *2019~ benign 샘플*(닷컴 없음)이었음. **진짜 닷컴류 QQQ 폭락엔 V7도 −39%** — V7의 "낙폭 방어"도 샘플 의존(단 2000 proxy는 MF=cash 보수적·진짜 DBMF 있었으면 덜했을 수도).
3. **verify-before-done의 승리.** 안 고쳤으면 1.25x를 V8로 잘못 승격할 뻔. Codex의 proxy 결함 지적 → 수정 → 정직한 기각.

## 결론 (보정)
- **V8 (Levered 4-sleeve) = 보수적 기각(Codex fail-close)·V7 1.0x core 유지.** 단 단정적 전멸 아님 = **UNKNOWN 잔존**: 2008(완전 proxy) 1.25x −32% 통과·2000(MF=cash 부재) 1.0x도 −39% 실패. 판정이 2000 MF proxy 부재에 달림.
- **1.35x/1.5x = 명확 폐기**(2008서도 −35/−38%).
- **1.25x = 상한 후보·UNKNOWN.** GPT/용하 권고대로 **V7 1.0x core + V8 1.25x를 자본권한 0 shadow forward로 "UNKNOWN 추적"**은 합리적(단 "안전 통과"라 라벨 금지). 1.10~1.20도 shadow에 병기.
- **V7 1.0x도 닷컴류 −39%**(2019~ −18%는 benign)·"낙폭 방어"는 *상대적*(QQQ −78% vs V7 −39%)이지 절대 안전 아님.
- 핵심 미해결: **2000 닷컴류에 진짜 4-sleeve(DBMF 포함) 방어력 = 무료로 확인 불가**(MF 장기 proxy 부재). 옵션 컨벡시티는 보류.
- 용하 니즈("상승 다 먹고 하락 방어")는 레버로도 단정 불가 — 알파 없이 프론티어 못 밀어냄은 유지되나, V8은 *전멸*이 아니라 *UNKNOWN*이 정직한 라벨.
