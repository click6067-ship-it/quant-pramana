# DR-4 Final Model Candidate Map v0.1
## GPT DR-4 Primary + Claude DR-4 Red-team 병합본

**Project:** Pramana systematic equity research / validation / trading operating system  
**Date:** 2026-06-09  
**Scope:** Layer-by-layer model candidate map  
**Non-scope:** final model adoption, stock recommendation, live trading strategy, performance forecast, company ranking

---

## 0. One-page Briefing

DR-4의 결론은 단순하다.

> **Phase 1은 멋진 모델부터 시작하지 않는다.**
> **먼저 지루하고 검증 가능한 baseline을 만든 뒤, challenger가 그 baseline을 실제로 이기는지만 본다.**

최종 모델군 위치는 아래처럼 정리한다.

| 구분 | 쉽게 말하면 | 대표 후보 |
|---|---|---|
| **Baseline candidate** | 가장 지루한 기준선. 먼저 만들어야 함 | simple factor, cross-sectional rank, equal-weight blend, 1/N, monotone rank-to-weight, basic risk cap, simple cost haircut |
| **Low-DoF challenger** | 조금 더 똑똑하지만 자유도 낮은 도전자 | penalized regression, deterministic event/calendar feature, constrained linear ranker |
| **Challenger candidate** | 성능 가능성은 있지만 과최적화 위험이 큰 도전자 | tree ensemble, constrained optimizer, HRP/robust optimizer, factor/shrinkage risk model, nonlinear cost model |
| **Exploratory / quarantine** | 연구 가치는 있지만 Phase 1 core에는 못 올림 | event/NLP alpha, alternative data, LLM weak signal, regime model, deep/TSFM/foundation overlay |
| **Reject for Phase 1** | 지금 하면 안 됨 | raw MVO, free-form LLM trading, direct HFT/MM, RL trading agent, autonomous retraining, black-box meta-allocator, deep/TSFM/foundation as core alpha |

핵심 패치:

1. GPT DR-4의 큰 방향은 유지한다.
2. Claude DR-4가 지적한 대로 **baseline을 더 낮춘다**.
3. `penalized regression`, `learned blending`, `optimizer 고도화`는 baseline이 아니라 challenger다.
4. `tree ensemble`은 challenger로 유지하되, DSR/PBO/trial registry gate를 더 강하게 적용한다.
5. `deep sequence`, `TSFM`, `financial foundation model`은 Phase 1 core alpha로는 reject, 연구 overlay로만 quarantine이다.
6. LLM은 off-path advisory/critic/parser만 허용한다.
7. 다음 단계는 **Phase 1 Experiment Design**이며, 구현이 아니라 실험 설계다.

---

## 1. Final Verdict

| Item | Final Status |
|---|---|
| GPT DR-4 Primary | GO |
| Claude DR-4 Audit | PASS |
| DR-4 final status | **PATCHED-LOCK** |
| Final model adoption | **NO-GO** |
| Phase 1 experiment design | **GO** |
| Production / paper trading | **NO-GO** |
| Next step | **Phase 1 Experiment Design** |

### Final Decision

DR-4는 모델 채택 문서가 아니라 **후보 지도(candidate map)** 이다.  
이 문서가 잠그는 것은 “무엇을 먼저 실험할지”이지, “무엇을 최종 사용할지”가 아니다.

---

## 2. Merge Summary: What Changed After Claude

| Area | GPT DR-4 Primary | Claude DR-4 Audit | Final Merge |
|---|---|---|---|
| Baseline | factor/rank 중심, 일부 residualization/linear 포함 | baseline이 아직 덜 boring함 | baseline을 1/N, rank, equal-weight, simple factor로 축소 |
| Penalized regression | challenger 후보 | low-DoF 도구이나 tuning 자유도 존재 | **Low-DoF challenger** |
| Tree ensemble | challenger | challenger 맞음, 단 high-DoF라 gate 강화 필요 | **Challenger with heavier DSR/PBO** |
| Raw MVO | reject | reject 강하게 확인 | **Reject for Phase 1** |
| Robust optimizer / HRP | challenger | low-vol tilt attribution 필요 | **Challenger with attribution gate** |
| Deep / TSFM / foundation | quarantine | alpha 용도는 reject에 가까움 | **Reject as Phase 1 core alpha; quarantine as overlay research** |
| Event/NLP | challenger | 직접 검증 근거 얇음 | **Challenger only if deterministic/timestamped; otherwise quarantine** |
| LLM | off-path | empirical edge 근거로 쓰면 안 됨 | **Off-path only** |
| Multiple testing | gate 연결 | 더 강한 N/trial-count gate 필요 | **Mandatory trial registry + DSR/PBO where relevant** |

---

## 3. Final Classification Rules

### 3.1 Baseline candidate

Baseline은 “최소 자유도, 최대 감사 가능성”이 기준이다.

A model family can be baseline only if:

- rules are simple
- degrees of freedom are low
- tuning is minimal
- output is interpretable
- failure is easy to diagnose
- after-cost OOS test can be run cleanly

### 3.2 Low-DoF challenger

Low-DoF challenger는 baseline보다 조금 더 똑똑하지만, 아직 통제 가능한 후보이다.

Examples:

- penalized regression
- constrained linear ranker
- deterministic event/calendar features

### 3.3 Challenger candidate

Challenger는 baseline을 이길 수 있지만, 과최적화 위험이 크다.

Must include:

- explicit trial registry
- search budget
- OOS + walk-forward
- cost stress
- DSR/PBO or equivalent multiple-testing control when search/tuning is material

### 3.4 Exploratory / quarantine

Research is allowed, but Phase 1 core is blocked.

Quarantine candidates require:

- independent replication
- stronger data rights check
- longer paper/shadow gate
- governance review
- no direct production path

### 3.5 Reject for Phase 1

Reject means “do not spend Phase 1 core resources on this.”

Reject does not necessarily mean “forever impossible.”  
It means “not compatible with the current data, validation, governance, and small-team constraints.”

---

## 4. Final Layer Taxonomy

| Layer | Name | Purpose | Main output |
|---|---|---|---|
| L0 | Research Objective / Benchmark / Universe | target, market sleeve, benchmark, universe boundary | locked experiment scope |
| L1 | Data Source / Data Contract | source, license, version, PIT availability | raw data contract |
| L2 | Data Engineering / PIT / Versioning | cleaning, point-in-time, transformations | research-ready panel |
| L3 | Feature / Representation | characteristics, residuals, event features | feature matrix |
| L4 | Alpha Model | forecast or rank signal | alpha score |
| L5 | Alpha Ensemble / Signal Aggregation | combine approved signals | combined forecast |
| L6 | Portfolio Construction / Optimizer | convert score into weights | target portfolio |
| L7 | Risk Model / Risk Engine | exposure, drawdown, liquidity, veto | approved/rejected portfolio |
| L8 | Cost / Slippage / Tax Model | after-cost realism | cost-adjusted forecast/return |
| L9 | Execution Support | order slicing, participation, handoff | executable order plan |
| L10 | Validation / Experiment Factory | OOS, WF, DSR/PBO, registry | promotion decision |
| L11 | Monitoring / Drift / Decay | live/paper performance and drift | alert/quarantine signal |
| L12 | Governance / Human / LLM Advisory | approval, audit, critic, documentation | human-controlled decision log |

---

## 5. Final Model Family Classification Table

| Model family | Candidate layer | Final treatment | Why |
|---|---|---|---|
| PIT core characteristics library | L3 | **Baseline candidate** | core feature substrate |
| Simple factor sleeves | L3/L4 | **Baseline candidate** | low-DoF, interpretable, auditable |
| Cross-sectional rank composite | L4 | **Baseline candidate** | simple and transparent |
| Equal-weight alpha blend | L5 | **Baseline candidate** | low parameter risk |
| 1/N portfolio | L6 | **Baseline candidate** | genuine boring portfolio baseline |
| Equal-weight top-N | L6 | **Baseline candidate** | easy to audit |
| Monotone rank-to-weight | L6 | **Baseline candidate** | simple score-to-weight conversion |
| Basic hard risk cap | L7 | **Baseline candidate** | deterministic risk containment |
| Simple cost haircut | L8 | **Baseline candidate** | prevents paper-alpha illusion |
| Basic execution support | L9 | **Baseline candidate** | no-trade buffer, participation cap, VWAP/TWAP handoff |
| Basic monitoring / shadow book | L11 | **Baseline candidate** | required operational control |
| Sector / beta residualization | L3/L7 | **Baseline-adjacent diagnostic** | useful but can erase alpha; compare raw vs residualized |
| Penalized regression: ridge/lasso/elastic net | L4 | **Low-DoF challenger** | useful DoF control but requires tuning |
| Constrained linear ranker | L4 | **Low-DoF challenger** | transparent but still learned |
| Deterministic event/calendar features | L3/L4 | **Low-DoF challenger** | timestamp discipline required |
| Shrinkage-weighted alpha blender | L5 | **Challenger candidate** | can meta-overfit |
| Tree ensemble: XGBoost/LightGBM/CatBoost | L4 | **Challenger candidate** | strong tabular challenger but high-DoF |
| Constrained optimizer | L6 | **Challenger candidate** | must beat 1/N after attribution |
| HRP / robust optimizer | L6 | **Challenger candidate** | must pass low-vol/factor attribution |
| Factor + shrinkage covariance risk model | L7 | **Challenger candidate** | useful but mapping risk exists |
| Nonlinear impact model | L8 | **Challenger candidate** | capacity realism, parameter instability |
| Predictive execution timing | L9 | **Challenger candidate** | broker/data-dependent |
| Drift / decay alerting | L11 | **Challenger candidate** | useful if alert-only |
| Event/NLP alpha | L3/L4 | **Exploratory / quarantine unless deterministic and timestamped** | evidence and leakage risks |
| Alternative data model | L3/L4 | **Exploratory / quarantine** | rights, PIT, mapping, cost risk |
| Regime model | L5/L7/L11 | **Exploratory / quarantine** | regime overfit risk |
| LLM-derived weak signal | L3/L4/L12 | **Exploratory / quarantine** | schema-locked only, no direct action |
| Deep sequence model | L4 | **Reject as Phase 1 core alpha / quarantine as overlay** | small data, low SNR, high compute/opacity |
| TSFM | L3/L4 | **Reject as Phase 1 core alpha / quarantine as overlay** | not Phase 1 core |
| Financial foundation model | L3/L4/L12 | **Reject as Phase 1 core alpha / quarantine as overlay** | fast-moving, governance and contamination risks |
| Raw plug-in MVO | L6 | **Reject for Phase 1** | estimation-error maximizer |
| Black-box meta-allocator | L5/L6 | **Reject for Phase 1** | layered overfitting and opacity |
| RL trading / execution agent | L6/L9 | **Reject for Phase 1** | simulator mismatch, reward hacking |
| Autonomous online retraining / self-promotion | L10/L11 | **Reject for Phase 1** | governance and reproducibility failure |
| Free-form LLM order/sizing/veto/regime switch | L12/control | **Reject for Phase 1** | violates authority topology |
| Direct HFT / market making | L9 | **Reject for Phase 1** | excluded scope |
| Naked options / high-leverage tail-risk strategy | outside scope | **Reject for Phase 1** | excluded and high-risk |

---

## 6. Validation Gate by Treatment

| Treatment | Required gate |
|---|---|
| Baseline candidate | Data gate + OOS + cost stress + paper/shadow |
| Baseline-adjacent diagnostic | Baseline gates + raw vs adjusted comparison |
| Low-DoF challenger | Data gate + OOS + walk-forward + cost stress + trial registry + paper/shadow |
| Challenger candidate | Data gate + OOS + walk-forward + cost stress + DSR/PBO or equivalent + paper/shadow |
| High-DoF challenger | Challenger gates + search budget cap + feature registry + independent holdout |
| Exploratory / quarantine | Challenger gates + independent replication + longer paper/shadow + governance review |
| Reject for Phase 1 | No Phase 1 experiment unless classification is reopened by later evidence |

---

## 7. Phase 1 Research Queue

### Phase 1A — Boring Baseline

**Goal:** prove data pipeline, benchmark, cost, and validation factory before testing complex models.

Included:

- PIT core characteristics
- simple factor sleeves
- cross-sectional rank composite
- equal-weight alpha blend
- 1/N or equal-weight top-N
- monotone rank-to-weight
- basic hard risk cap
- simple cost haircut
- basic execution support
- paper/shadow monitoring

Excluded:

- tree ensemble
- NLP/event ML
- optimizer sophistication
- TSFM/foundation/deep
- LLM-derived alpha
- RL
- black-box allocation

Promotion condition:

- baseline survives OOS, cost stress, and paper/shadow pipeline checks
- data acceptance gate passes
- benchmark sanity passes
- results are reproducible from versioned configs

---

### Phase 1B — Low-DoF Simple Challenger

**Goal:** test whether small, interpretable improvements add value over baseline.

Included:

- penalized regression
- constrained linear ranker
- deterministic event/calendar features
- sector/beta residualization variant
- simple shrinkage or nonnegative alpha blending

Promotion condition:

- incremental value over baseline survives walk-forward
- search budget is documented
- cost/turnover do not explode
- alpha is not just hidden exposure or low-vol tilt

---

### Phase 1C — Controlled ML Challenger

**Goal:** test high-DoF but manageable ML.

Included:

- shallow tree ensemble
- constrained XGBoost/LightGBM/CatBoost
- conservative NLP/event score only if timestamped and rights-cleared
- constrained optimizer / HRP / robust optimizer
- factor + shrinkage risk model
- nonlinear cost/impact model
- drift/decay alerting

Promotion condition:

- heavier DSR/PBO or equivalent multiple-testing control
- feature/model/trial registry complete
- independent holdout not tuned on
- after-cost advantage remains after turnover/capacity constraints
- factor/low-vol attribution explains whether improvement is real alpha or disguised risk tilt

---

### Phase 1D — Quarantined Exploratory Research

**Goal:** study future candidates without letting them enter the production path.

Included:

- alternative data
- LLM-derived weak signal
- deep sequence overlay
- TSFM overlay
- financial foundation model overlay
- regime model
- black-box/meta allocation research only
- RL research only

Promotion condition:

- not promotable in Phase 1 core
- requires independent replication
- requires stronger governance
- requires data rights and PIT proof
- requires longer paper/shadow gate
- must be reclassified in a later DR or audit

---

## 8. U.S.-core / KR-addon Treatment

| Model group | U.S. Phase 1 treatment | KR-addon treatment |
|---|---|---|
| Simple factor / rank | Phase 1A core | revalidate with KR data/PIT/cost |
| Equal-weight / monotone rank-to-weight | Phase 1A core | portable, but liquidity/cost constraints differ |
| Penalized regression | Phase 1B | revalidate with shorter KR PIT panel and accounting lag |
| Tree ensemble | Phase 1C | likely harder due to data depth and microstructure |
| Event/NLP | timestamped SEC/EDGAR first | DART/KRX/KIND timing and field mapping must be rebuilt |
| Optimizer / HRP / robust | only after baseline | must re-run cost/liquidity constraints |
| Cost/slippage | U.S. adapter first | KR requires KRX-only vs SOR-enabled distinction |
| LLM advisory | off-path allowed | off-path allowed; Korean language parsing needs separate validation |
| Deep/TSFM/foundation | no Phase 1 core alpha | no KR core alpha |

Do not transfer U.S. results to KR without retesting.

---

## 9. LLM Role Map

| LLM use case | Final treatment | Controls |
|---|---|---|
| Research assistant | Allowed | human review |
| Paper summarizer | Allowed | source citations required |
| Filing/news parser | Conditional challenger | schema-locked output + timestamp test |
| Event extraction | Conditional challenger | deterministic schema + replay test |
| Hypothesis generator | Allowed off-path | hypothesis registry only |
| Adversarial critic | Allowed off-path | no direct model promotion |
| Post-trade explanation | Allowed | no trading authority |
| Feature generator | Quarantine | requires full validation as weak signal |
| Direct alpha score | Quarantine / reject unless schema-locked and validated | no free-form score |
| Direct order decision | Reject | forbidden |
| Direct risk veto | Reject | forbidden |
| Direct position sizing | Reject | forbidden |
| Direct regime switch | Reject | forbidden |

---

## 10. Failure Mode Register

| Failure mode | Affected families | Detection | Treatment |
|---|---|---|---|
| Look-ahead bias | all alpha/event/NLP | timestamp replay | block |
| Survivorship bias | universe/alpha | inactive/delisted inclusion test | block |
| Delisting omission | returns/universe | delisting casebook | block |
| Corporate-action error | price/features | split/dividend reconciliation | block |
| Stale fundamentals | factor/linear/tree | filing lag test | block |
| Restatement leakage | fundamentals | as-filed vs restated comparison | block |
| Benchmark mismatch | portfolio/optimizer | self-built benchmark sanity | quarantine |
| Cost underestimation | all trading path | 2x/3x stress or calibrated stress | quarantine/reject |
| Turnover explosion | ML/optimizer | turnover and ADV cap | quarantine |
| Feature mining | ML/NLP/alt data | feature registry and MTC | quarantine |
| Hyperparameter overfitting | tree/deep/optimizer | search budget + DSR/PBO | quarantine |
| Regime overfit | regime/allocator | regime-split OOS | quarantine |
| Vendor artifact | alt data/NLP | vendor version comparison | quarantine |
| LLM hallucinated signal | LLM features | schema + replay + human review | reject if free-form |
| Low-vol disguised optimizer alpha | optimizer/HRP | factor attribution | quarantine unless explained |

---

## 11. Phase 1 Experiment Design Handoff

The next stage is **Phase 1 Experiment Design**.

Phase 1 must not begin with all model families.  
It should begin with **Phase 1A boring baseline experiment design only**.

Required next deliverables:

1. Experiment registry schema
2. Data snapshot / universe / benchmark config schema
3. Phase 1A baseline experiment design
4. OOS / walk-forward split definition
5. Cost stress configuration
6. Basic promotion / quarantine / reject rule
7. Trial budget policy
8. Report template
9. Failure log template
10. Phase 1B/1C queue gating rule

### Recommended Phase 1 Entry Order

```text
Phase 1A:
Data acceptance + boring baseline

Phase 1B:
Low-DoF challenger only after Phase 1A passes

Phase 1C:
Controlled ML challenger only after Phase 1B passes

Phase 1D:
Quarantined exploratory research, never production path in Phase 1
```

---

## 12. Final Locked Summary

| Decision | Status |
|---|---|
| Start with boring baseline | LOCK |
| Treat penalized regression as challenger | LOCK |
| Treat tree ensemble as controlled challenger | LOCK |
| Reject raw MVO | LOCK |
| Require factor attribution before optimizer promotion | LOCK |
| Reject deep/TSFM/foundation as Phase 1 core alpha | LOCK |
| Keep deep/TSFM/foundation as quarantine overlay research | PROVISIONAL |
| Keep event/NLP as conditional challenger only if timestamped/schema-locked | PROVISIONAL |
| Keep LLM off-path | LOCK |
| Require DSR/PBO/trial registry for high-DoF challengers | LOCK |
| Move next to Phase 1 Experiment Design | GO |

---

## 13. Short Mental Model

Think of the system like this:

```text
1. First, build the boring yardstick.
2. Then test small challengers.
3. Then test controlled ML.
4. Keep shiny models in quarantine.
5. Never let LLM or black-box models touch orders.
```

That is DR-4.
