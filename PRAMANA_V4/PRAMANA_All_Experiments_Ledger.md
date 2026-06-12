# PRAMANA 전체 실험 원장 (Experiment Ledger) — 면밀 검토용

> **목적:** 지금까지의 *모든* 실험·판정·핵심 수치·근거를 한 파일에. "정말 알파가 힘든가"를 데이터로 직접 검토하기 위함.
> **작성:** 2026-06-12 (Claude·용하 요청). 정본 계보 = `PRAMANA_Lineage_Dossier.docx` · 원자료 = `phase1a/registry/phase1a_milestones.csv` + `phase1a/reports/*.md`.
> 판정 라벨: PASS/MEASURED(중립)·FAIL/DEAD/REJECT/CLOSED(부정)·SURVIVE/UNKNOWN(조건부)·BUILT(인프라).

---

## 0. 한눈에 — 메타 결론

**검증된(거래 가능한) 알파 = 0.** 단 *무엇을 시도했고 무엇을 안 했나*가 핵심:

| 데이터/접근 축 | 시도? | 결과 |
|---|---|---|
| 정량 cross-sectional (가격·펀더멘털·일봉) | ✅ 6+ family | **전멸 (cap-weight 메가캡 벽)** |
| 정량 결합/ML (ridge·GBM·tree) | ✅ bake-off | **선형 못 넘음·ML OOS R² 0.4%** |
| event/earnings drift (숫자 surprise) | ✅ | **net vs CW −0.90%** |
| analyst revision (Zacks) | △ 프로토콜만 | 데이터 없어 미완 |
| 풀북/trend/LETF | ✅ | **알파 아님·+0.15%/yr 노이즈** |
| 레버 (V5/V8) | ✅ | **알파 아님·닷컴 −49% 꼬리** |
| 마켓타이밍 (4종) | ✅ | **4전4패 (후행 신호 벽)** |
| 분산 (V7 4-sleeve) | ✅ | **생존코어·알파 아님 (분산 프리미엄)** |
| intraday 급등주 (ORB/VWAP/RVOL) | ✅ v1 | **DEAD (강세장 베타·누수)** |
| event-driven momentum (catalyst proxy) | ✅ v2 | 약함 (테마 88%·SPY 80%) |
| **정성 텍스트 + LLM (공시·실적콜·뉴스)** | ❌ **안 봄** | **미개척 (유일하게 열린 진짜 새 축)** |
| 옵션 컨벡시티 | ❌ 보류 | 비용·과최적화 |

→ **"정량·정형 데이터로 솔로가 SPY/QQQ 위험조정 초과 = 매우 어렵다"는 정확히 가리킴.** 단 *정성 LLM*과 *옵션*은 미검증.

---

## 1. 정량 Cross-sectional (Phase 1A/1B·v1·v2.x) — US 공개데이터

| 실험 | 판정 | 핵심 수치 | 근거 |
|---|---|---|---|
| B0 데이터 sanity | **PASS** | self-built PIT cap-weight vs 실 SPY **corr 0.998** | 파이프라인 정확 (자산) |
| B1 1/N baseline | PASS | — | boring baseline |
| B2~B5 단순팩터(value/mom/quality/lowvol) | **MEASURED** | **Rank IC ≈ 0** (|IC|<0.01·IC-IR<0.05) | 비용 전인데 신호 無 |
| B2~B5 broad retest (비용후) | MEASURED | value/mom/lowvol DEAD·quality만 IC-IR 0.22(간신히) | 3/4 DEAD |
| B3 quality quarantine | **FAIL** | IC-IR 0.22→**0.046 decay**(2021-26)·long-only vs CW **−1.15%** | 식음·벽 |
| Phase 1B 결합(ridge/blend/GBM) | **FAIL** | ridge OOS IC-IR **0.014**·net vs CW 음수 | 결합도 cap-weight 못 이김 |
| US event/earnings drift | **FAIL** | net vs CW **−0.90%**·long-short +4.4%(공매도 솔로불가) | kill 4개 |
| US small/mid cost-first | **FAIL** | 비용/유동성에 죽음 | |
| True PEAD (반전) | **FAIL** | — | |
| v2.1 Zacks revision 2018 | **FAIL-sample** | 샘플 부족·데이터 게이트 | 진짜 revision 미완 |
| **US cross-sectional arena** | **CLOSED** | 6 family 전멸 = robust negative | |

**★ 메타 패턴 (가장 중요):** 모든 신호군이 **1/N은 이기나 cap-weight long-only는 못 이긴다.** killer = **2016-26 메가캡 지배 레짐.** cross-sectional EW 틸트는 *신호 무관하게* cap-weight에 구조적으로 진다. (event/surprise는 decay 안 함=정보는 있으나 long-only 벽+비용이 먹음.)

---

## 2. 풀북 / Trend / 레버 (v3)

| 실험 | 판정 | 핵심 수치 |
|---|---|---|
| trend+LETF 위성(70/25/5) | SURVIVE(약) | unlevered & risk-matched 둘 다 **+0.15%/yr = 노이즈** |
| v3 풀북 | — | **SPY를 어느 horizon도 위험조정 못 이김**(3x +699%는 레버지 엣지 아님·Sharpe 0.82<0.90) |
| VRP short-vol | **REJECT** | worst month −62%·maxDD −92%·tail-deadly |
| LETF convex | SURVIVE(약) | convexity가 naive레버 못 이김·결합서 소량 dose만 |
| short-term reversal | **FAIL** | net −4%·turnover 3660% |
| model bake-off (ridge/GBM) | MEASURED | **ML이 선형 합성 못 넘음** → GKX2020(ML OOS R² 0.33-0.40%)과 일치 |

---

## 3. Core-satellite / 분산 / 레버 (V4~V8)

| 세대 | 판정 | 핵심 수치 |
|---|---|---|
| V4 Core Beta 1.0x | 베타북 | 알파 아님·QQQ 못 넘음(설계상) |
| V5 Leveraged (cap2.0) | SHIP-paper | in-sample +625% > QQQ +539% **but Sharpe 0.95≈QQQ = 레버지 알파 아님**·같이 낙폭 |
| V6 Diversified (+DBMF) | SHIP-paper | 낙폭 완화·**보험료**(상승장 수익↓)·alpha 아님 |
| **V7 4-sleeve (현재 코어)** | 생존코어 후보 | **풀 +175%/MDD −18%/Sharpe 1.21**(최선) vs QQQ +305%/−35%/0.94·**단 누적 절반·닷컴 proxy −39%** |
| V8 Levered 4-sleeve | **REJECT/UNKNOWN** | 실 SPY/QQQ crash-pack **닷컴 −49%**·전부 −35% 초과·1.35x+ 폐기 |

---

## 4. 마켓타이밍 — **4전 4패** (용하 핵심 관심)

| # | 실험 | 형태 | 판정 | 핵심 수치 |
|---|---|---|---|---|
| 1 | regime_switch_test | 단계적 코어전환(growth↔survival) | 죽음 | switch Sharpe **0.91 < static 1.07**·2022 −24% vs −10% |
| 2 | crash_pack throttle | binary overlay 끄기 | **REJECT** | static 4-sleeve 못 이김·반등 놓침 |
| 3 | derisk_test | 추세→현금 | 휩쏘 | V회복/chop 휩쏘·full −50%p |
| 4 | **MT-1 ladder** | **단계적 overlay(확률→포지션)** | **DEAD** | ladder Sharpe **1.08 < static 1.20**·닷컴 ladder MDD −50% vs static −22% |

**공통 killer = 후행 신호 본질** (늦게 팔고 늦게 사 휩쏘·폭락 후행으로 못 피함). **코어/overlay × binary/단계적 × 전환/현금 *모든 조합*이 static 4-sleeve를 못 이긴다.**
*(Codex 정밀화: "느린 일봉 risk-score 기반" timing 사망·빠른/선행 신호는 미검증.)*

---

## 5. Alpha Lab (intraday / event-driven)

| 실험 | 판정 | 핵심 수치 |
|---|---|---|
| v0 intraday DATA INFRA | **BUILT** | setup 검출 PASS(VWAP/ORB/RVOL 계산·적재) |
| v1 단순 setup(Gap+RVOL+ORB+VWAP) | **DEAD** | RVOL look-ahead 누수 수정후 **중앙 −0.41%·승률 41%·false breakout 56%**·SPY 하락일 −0.99% |
| v2 event-driven momentum | 약함(관찰中) | catalyst 없는 순수 momentum·**테마 88% 집중·SPY 상승일 80%** = 강세장/테마 베타 |

---

## 6. "딥러닝·분봉·개인단위 써도 알파 힘들다"가 정확히 가리키나?

**정량/정형 = YES, 정확히 가리킴:**
- 가격·거래량·펀더멘털·분봉·cross-sectional·timing·레버 — *모든 정량 각도*에서 막힘(위 1~5).
- **딥러닝/TSFM:** DR-4가 "reject-as-core-alpha"·우리 bake-off에서 ridge/GBM이 선형 못 넘음·GKX2020 ML OOS R² 0.4%(거의 0)·shallow>deep. → *모델을 고급화해도 정량 데이터엔 신호가 없다.*
- **분봉:** v1 DEAD·day-trader <1% 순수익·HFT 속도 벽.
- **개인 단위:** 기관 대비 데이터·속도·비용·공매도·자본 전부 불리(XTX/Jane Street = 미세구조·유동성공급·실행인프라 게임 = 솔로가 복제 불가).

**정성/텍스트 = NO, 안 가리킴 (미검증):**
- 공시·실적콜·뉴스 텍스트 + LLM = **한 번도 안 봄.** 정량과 *다른 축*이고, LLM(2023~)이 새로워서 *상대적으로* 덜 효율적일 *가능성.*
- 단 함정: 기관 NLP 10년+·정보≠알파·PIT look-ahead·cross-sectional 벽 그대로.

→ **결론: "정량으로 솔로 알파 ≈ 0"은 데이터가 정확히 가리킴. "정성 LLM"은 유일하게 열린 진짜 프론티어.**

---

## 7. 미검증 / 열린 것 (남은 후보)

1. **정성 텍스트 + LLM** — EDGAR 공시(무료·PIT timestamp)·실적콜·catalyst quality. *유일하게 안 본 진짜 새 축.* PIT 백테스트 가능(EDGAR).
2. **옵션 컨벡시티** — 상승 참여 + 하락 보호. 비용(프리미엄 드래그)·과최적화. 후순위.
3. **KR small/mid** — 덜 효율적이나 데이터/세금/체결/구조 새 리스크. 2순위.

---

## 8. 마켓타이밍 "확률값으로 완화" 재검토 (용하 재주장)

**용하 주장:** "정확히 맞추는 게 아니라, 하락장/반등을 *확률값*으로 바꿔 포지션 비율 조절 → *완화* 정도는 가능."

**검토 — 이게 정확히 MT-1이었다:**
- MT-1 = risk_score(0~3)를 **확률값처럼** 써서 overlay를 **단계적 비율(100→66→33→0%)**로 조절 = "확률→포지션 완화" 그 자체.
- 결과: **완화해도 static 4-sleeve보다 나쁨** (Sharpe 1.08<1.20·MDD −22% vs −18%). 즉 *완화가 휩쏘 비용을 추가로 냄.*
- 닷컴: 단계적으로 빼도 MDD −50%(static −22%) — *완화가 폭락을 못 막음*(후행).

→ **"완화 정도는 가능"은 직관이지만, MT-1이 그 직관을 정확히 테스트했고 *완화할수록 위험효율이 나빠졌다.*** 후행 신호로는 "조금 줄이기"도 비용이 이득을 넘는다. *(단 Codex: 느린 일봉 신호만 죽음·더 빠른/다른 신호는 미검증.)*

---

> **한 줄:** 정량(가격·펀더멘털·분봉·ML·레버·타이밍)으로 솔로가 SPY/QQQ 위험조정 초과 = 데이터가 7+세대로 "거의 불가"를 가리킴(정확). 마켓타이밍 "확률 완화"도 MT-1로 죽음(완화=비용↑). **유일하게 안 본 = 정성 텍스트+LLM.** 그게 다음 정직한 프론티어.
