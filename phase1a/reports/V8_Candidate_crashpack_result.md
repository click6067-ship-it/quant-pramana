# V8 Candidate — Levered 4-sleeve crash-pack 결과 → **기각 (V7 1.0x 유지)**

> 사전등록: `PRAMANA_V4/V8_Candidate_Levered4sleeve_Protocol.md` · 코드: `phase1a/engine/v8_levered_crashpack.py`
> 가설: V7 분산북을 레버(1.25~1.5x)하면 상승참여↑ 유지하며 crash MDD가 A1 Aggressive(−35%) 이내인가?
> **명확히: 알파 아님 = 분산 프리미엄 레버 = 목적함수 이동.** proxy·in-sample·PAPER. 2026-06-12.

## 판정 한 줄
**V8 (Levered 4-sleeve) = 기각. V7 1.0x 유지.** equity proxy를 실 SPY/QQQ(QQQ 닷컴 −78%)로 고치니 **레버 전부 2000 닷컴에서 −49~−57%** = A1 Aggressive(−35%) 대폭 초과. Codex 적대검증이 proxy 결함을 잡았고, 수정 후 판정 뒤집힘.

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

## 결론
- **V8 (Levered 4-sleeve) 기각.** 레버는 닷컴류 tail을 못 견딤(1.25x −49%).
- **V7 1.0x 유지** — 단 정직 보정: V7도 닷컴류 −39%까지 가능(2019~ −18%는 benign). "낙폭 방어"는 *상대적*(QQQ −78% vs V7 −39%)이지 절대 안전 아님.
- 옵션 컨벡시티(★ 진짜 둘 다)는 데이터·프리미엄·과최적화 문제로 보류(용하). 
- 용하 니즈("상승 다 먹고 하락 방어")는 **레버로도 안 됨** — 알파 없이는 프론티어를 못 밀어낸다는 또 하나의 실증.
