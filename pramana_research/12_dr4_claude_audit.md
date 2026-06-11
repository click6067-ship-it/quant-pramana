# 12 · DR-4 Claude Red-Team Audit (Layer-by-layer Model Candidate Map)

> **적대 레드팀 대상:** ChatGPT DR-4 (`GPT DR-4 Primary.md`, terse 계획/아웃라인) — 모델 패밀리 분류(baseline/challenger/quarantine/reject)·레이어 L0–L12·검증 게이트 매핑.
> **방법:** deep-research 하니스 (fan-out 검색 → 소스 fetch → 3-vote 적대 검증 → 종합). 1차 학술원전(DeMiguel-Garlappi-Uppal·Gu-Kelly-Xiu·Grinsztajn·Bailey-LdP·Michaud·Zakamulin) 중심.
> **생성:** 2026-06-09. runId `wf_0f26b279-5be`.
> **규모:** 104 agent calls · sources fetched 22 · claims extracted 100 · verified 25 · confirmed 21 · killed 4 · findings 12.

---

## VERDICT — PATCH-BEFORE-FINAL-MAP

The verified primary-source evidence strongly supports a PATCH-BEFORE-FINAL-MAP verdict on ChatGPT DR-4: the "boring baseline" set is secretly a challenger set, and the multiple-testing gating is under-specified relative to what the literature demands. Three evidence pillars dominate. (1) PORTFOLIO LAYER (L6): raw mean-variance optimization is an estimation-error maximizer that no realistic sample can rescue (DeMiguel-Garlappi-Uppal 2009: >3,000-6,000 months needed for 25-50 assets vs ~120 used; Yuan-Zhou 2024: estimated rules cannot reach the optimal Sharpe when N>>T; Zakamulin 2017: even apparent optimizer wins are a low-vol-tilt artifact), so the genuinely boring baseline optimizer is 1/N / monotone rank-to-weight, NOT estimated/shrinkage MVO — confirming raw MVO=reject (Target 6) and demanding factor-attributed gating before any "robust optimizer/HRP" promotion (Target 7). (2) ALPHA LAYER (L4): on the canonical US panel (~30k stocks × 60 yrs) the best ML (trees/NN) achieve only 0.33-0.40% monthly OOS R², shallow beats deep (NN peaks at 3 layers then declines; trees avg <6 leaves) explicitly because of small data and tiny signal-to-noise — direct primary evidence for "right shape, wrong scale" and against deep-sequence/TSFM/foundation models as alpha; Grinsztajn 2022 confirms GBDT remains state-of-the-art on medium (~10k-sample) tabular data, validating tree ensembles as a legitimate CHALLENGER (not baseline, not above trees) but one whose edge is interaction-capturing high-DoF that earns its place only conditional on demonstrated OOS profitability (Yuan-Zhou 2024). (3) VALIDATION LAYER (L10): the Bailey-Borwein-López de Prado-Zhu PBO/DSR literature shows a gate chain ending in plain OOS/holdout is INSUFFICIENT (repeated holdout ~20× makes false positives expected), that even few-parameter searches over a few hundred trials overfit pseudorandom data, that overfit backtests actively MINIMIZE future performance (negative IS→OOS slope), and that DSR raises the required Sharpe threshold with both trial count N and SR-dispersion — so DR-4 MUST attach an explicit multiple-testing stage (DSR/DSR-N + PBO) with HEAVIER gating on high-DoF challengers (tuned tree ensembles) than on low-DoF baselines, and any promotion before DR-3's thresholds are locked (still PATCH-BEFORE-MODELS) is premature.

---

## Findings (적대 검증 통과)

### [1] The genuinely boring baseline optimizer is 1/N (equal-weight) / monotone rank-to-weight, NOT estimated or shrinkage mean-variance: across 14 optimized models on 7 datasets none consistently beat 1/N out-of-sample, and 1/N is theoretically optimal in a 1-factor model with diversifiable risk as dimensionality rises (the project's high-N-low-T regime). DR-4's baseline set, if it contains penalized regression and multi-factor cross-sectional ranking, is therefore secretly a CHALLENGER set (Target 1).
**confidence:** high · **vote:** 3-0 (merged from unanimous DGU-2009 and Yuan-Zhou-2024 claims)

DeMiguel-Garlappi-Uppal (2009, RFS 22:1915-1953): 'Of the fourteen models of optimal portfolio choice that we evaluate across seven empirical datasets, we find that none is consistently better than the 1/N rule in terms of Sharpe ratio, certainty-equivalent return, or turnover.' Yuan-Zhou (2024, JFQA 59(8):3601-3632, Sharpe Best-Paper Award): 'the 1/N rule is optimal in a 1-factor model with diversifiable risks as dimensionality increases' and estimated strategies 'will not achieve the optimal Sharpe ratio when the dimensionality is high relative to sample size.' This is precisely the project's tens-of-months × hundreds-of-names regime (N>>T).

**Sources:**
- https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901
- https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/why-naive-1n-diversification-is-not-so-naive-and-how-to-beat-it/4969319F5B1F3E350FB7FC8A73BA9F65


### [2] Raw mean-variance optimization is correctly REJECTED: it is an estimation-error maximizer, and the estimation window required for sample MVO to beat 1/N is enormous (>3,000 months for 25 assets, >6,000 for 50, vs ~120 used in practice), so estimation noise dominates any theoretical optimization gain at realistic sample sizes. Confirms Target 6.
**confidence:** high · **vote:** 3-0 (merged DGU-2009 estimation-error + window-length claims)

DGU (2009): 'the gain from optimal diversification is more than offset by estimation error.' Calibration: 'for a portfolio with only 25 assets, the estimation window needed is more than 3,000 months, and for a portfolio with 50 assets, it is more than 6,000 months, although in practice these parameters are estimated using 120 months of data.' Counter-literature (Tu-Zhou 2011, Kritzman et al 2010) does NOT refute this — it concedes raw/sample MVO is dominated and engineers around it with shrinkage/constraints/combination, which routes to CHALLENGER not baseline.

**Sources:**
- https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901


### [3] Apparent wins of optimized portfolios over 1/N are largely a LOW-VOLATILITY-TILT artifact, not optimization skill: after controlling for the low-vol effect there is no evidence of superior OOS performance. Therefore any 'robust optimizer / HRP / constrained-MVO' challenger gain must be factor-attributed (controlled for low-vol) before promotion over a 1/N or constrained-inverse-vol baseline (Target 7).
**confidence:** high · **vote:** 3-0 (merged; one component was 2-1 but both Zakamulin claims survived)

Zakamulin (2017, Finance Research Letters 22:122-128): optimized portfolios beating 1/N 'are tilted towards assets with lowest volatilities and, after controlling for the low-volatility effect, there is absolutely no evidence of superior performance'; 'the low-volatility effect is present in virtually all datasets in the Kenneth French online data library.' Implication: DR-4 should split the optimizer family — constrained inverse-vol / simple risk-parity as the boring baseline optimizer, HRP/robust-MVO as challengers requiring factor-attributed OOS evidence vs 1/N, not one lumped 'robust optimizer' box.

**Sources:**
- https://www.sciencedirect.com/science/article/abs/pii/S1544612316303555


### [4] Penalized regression (ridge/lasso/elastic-net, PCR/PLS) is a legitimate LOW-DoF tool whose value comes precisely from degrees-of-freedom reduction — NOT a free-running challenger and NOT the same as raw high-DoF linear regression. Raw full-predictor OLS is an estimation-error liability (OOS R² goes deeply negative), while shrinkage/dimension-reduction rescues it. This nuances Target 1: penalized regression sits between baseline and challenger and must be classed by its DoF-control discipline, not auto-demoted or auto-promoted.
**confidence:** high · **vote:** 3-0 (merged Gu-Kelly-Xiu OLS-collapse + elastic-net-rescue claims)

Gu-Kelly-Xiu (2020, RFS 33(5):2223-2274): 'When we expand the OLS panel model to include our set of 900+ predictors, predictability vanishes immediately—the R2 drops deeply into negative territory... efficiency of OLS regression deteriorates precipitously.' Conversely elastic net 'uses parameter shrinkage and variable selection to limit the regression's degrees of freedom... pulls the out-of-sample R2 into positive territory at 0.11% per month'; PCR/PLS reach 0.26%/0.27%. Low-DoF benchmark OLS-3 (size/value/momentum) yields ~0.16%/month. So the DoF-controlled penalized linear model is a defensible floor, not the offender — but its tuning (λ/α) means it is NOT as low-DoF as 1/N or a single-factor sort.

**Sources:**
- https://academic.oup.com/rfs/article/33/5/2223/5758276


### [5] Tree ensembles (GBDT: XGBoost/LightGBM/CatBoost) are correctly placed as CHALLENGER (not baseline, not quarantine, not above trees as a strawman): GBDT remains state-of-the-art on medium-sized (~10K-sample) tabular data, and on financial panels trees/NN are the best performers via nonlinear PREDICTOR INTERACTIONS (GLM with splines but no interactions fails to beat linear). Their edge is high-DoF interaction-capturing, distinct from low-DoF baselines (Target 2).
**confidence:** high · **vote:** 3-0 (merged Grinsztajn-2022 tabular + Gu-Kelly-Xiu interaction claims)

Grinsztajn-Oyallon-Varoquaux (2022, NeurIPS D&B, arXiv:2207.08815): 'tree-based models remain state-of-the-art on medium-sized data (~10K samples) even without accounting for their superior speed' — the project's tens-of-months × hundreds-of-names panel is exactly this medium/small regime. Gu-Kelly-Xiu (2020): 'trees and neural networks unambiguously improve return prediction with monthly stock-level R2's between 0.33% and 0.40%. But the generalized linear model... (but with no predictor interactions), fails to robustly outperform the linear specification' — the entire ML edge is interaction-capture. This validates 'challenger' but flags that the edge is high-DoF.

**Sources:**
- https://arxiv.org/abs/2207.08815
- https://academic.oup.com/rfs/article/33/5/2223/5758276


### [6] Tree ensembles must carry HEAVIER DSR/PBO gating than a generic challenger, because (a) ML/anomaly portfolios beat 1/N only CONDITIONAL on demonstrated profitability, and (b) on the canonical US panel the best ML achieves only 0.33-0.40% monthly OOS R² — an extremely low signal-to-noise ceiling even with ~30,000 stocks over 60 years. At the project's tiny scale the multiple-testing/overfitting hazard is far worse, so 'challenger' is right only with reinforced gating (Target 2).
**confidence:** high · **vote:** 3-0 (merged Yuan-Zhou conditional-profitability + Gu-Kelly-Xiu R²-ceiling claims)

Yuan-Zhou (2024): one can beat 1/N 'by combining it with anomalies or machine learning portfolios, conditional on the profitability of the latter, when N is large' — ML earns its place only after proving genuine profitability. Gu-Kelly-Xiu (2020): best ML monthly stock-level OOS R² = 0.33-0.40% on 'nearly 30,000 individual stocks over 60 years' — a low ceiling at maximal scale; the solo book has orders of magnitude less data, so the deflation/PBO burden is heavier.

**Sources:**
- https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/why-naive-1n-diversification-is-not-so-naive-and-how-to-beat-it/4969319F5B1F3E350FB7FC8A73BA9F65
- https://dachxiu.chicagobooth.edu/download/ML.pdf


### [7] TSFM / financial-foundation / deep-sequence models are DISFAVORED for alpha at financial scale by primary evidence — quarantine is too generous for them AS ALPHA: shallow beats deep specifically because of small data and tiny signal-to-noise. NN performance peaks at three hidden layers then DECLINES; boosted trees/random forests select trees averaging fewer than six leaves, explicitly attributed to return prediction's small data and low SNR versus settings where deep learning thrives. This is direct support for REJECT-for-alpha (overlay-only at most) rather than quarantine (Target 5), and 'right shape, wrong scale' (Target underlying premise).
**confidence:** high · **vote:** 3-0 (merged two Gu-Kelly-Xiu shallow-beats-deep claims, corroborated by European/Tidy-Finance replications)

Gu-Kelly-Xiu (2020): 'Shallow learning outperforms deeper learning... neural network performance peaks at three hidden layers then declines as more layers are added... boosted tree and random forest algorithms tend to select trees with few leaves (on average less than six leaves)... This is likely an artifact of the relatively small amount of data and tiny signal-to-noise ratio for our return prediction problem, in comparison to the kinds of non-financial settings in which deep learning thrives.' The mechanism applies a fortiori to the tiny solo book. (NOTE: later transformer/decomposition papers winning at NN4/NN5 use different architectures/larger data, which is CONSISTENT with the small-data attribution, not a refutation.)

**Sources:**
- https://academic.oup.com/rfs/article/33/5/2223/5758276
- https://dachxiu.chicagobooth.edu/download/ML.pdf


### [8] GBDT/trees should NOT be promoted below deep-sequence/foundation models, and deep/foundation models should not be promoted above trees for tabular financial alpha. Tree-based models remain state-of-the-art on medium tabular data, undercutting any DR-4 placement that treats TSFM/foundation models as a near-baseline-quality alpha candidate (Targets 2 and 5).
**confidence:** high · **vote:** 3-0

Grinsztajn-Oyallon-Varoquaux (2022, arXiv:2207.08815): 45 datasets, ~20,000 compute-hours: 'tree-based models remain state-of-the-art on medium-sized data (~10K samples) even without accounting for their superior speed.' Caveats (TabPFN/foundation models at >50K samples) do not reach the project's small/medium regime. Combined with the shallow-beats-deep finding, this orders the alpha layer: low-DoF linear/factor baselines < penalized linear < GBDT challenger << deep-sequence/TSFM (reject-for-alpha or overlay-only).

**Sources:**
- https://arxiv.org/abs/2207.08815


### [9] DR-4's validation gate chain ending in plain OOS / walk-forward / holdout is INSUFFICIENT — it must include an explicit MULTIPLE-TESTING stage. The holdout/OOS method does not control for backtest overfitting; applying holdout ~20 times (for 95% confidence) makes false positives EXPECTED, because each pass is treated as a single trial and ignores the rising false-positive rate (Target 9).
**confidence:** high · **vote:** 3-0

Bailey & López de Prado, 'The Deflated Sharpe Ratio' (JPM 2014): 'the holdout method can not prevent backtest overfitting: Holdout assesses the generality of a model as if a single trial had taken place... If we apply the holdout method enough times (say 20 times for a 95% confidence level), false positives are no longer unlikely: They are expected.' DR-4's gate chain (data → OOS → walk-forward → cost stress → multiple-testing → paper/shadow) is only sound if the multiple-testing stage is mandatory and load-bearing, not appended.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf


### [10] Multiple testing makes false positives near-certain even at SMALL scale and with FEW parameters: a few-parameter strategy searched over a few hundred iterations on purely pseudorandom (zero-signal) returns trivially yields profitable in-sample strategies whose OOS performance is 'utterly disappointing'; after enough trials a false positive is GUARANTEED, so any backtest omitting the number of trials N is 'worthless.' This directly mandates that every promotable family report DoF/configurations searched and minimize them — reinforcing the project's 'minimize degrees of freedom' constraint and the brutality of multiple-testing at solo scale.
**confidence:** high · **vote:** 3-0 (merged PBO-pseudorandom + DSR-guaranteed-false-positive claims)

Bailey-Borwein-López de Prado-Zhu, 'The Probability of Backtest Overfitting' (J. Computational Finance 2015/2017): 'After a few hundred iterations, it is trivial to find highly profitable strategies in-sample, despite the small number of parameters involved. Performance out-of-sample is, of course, utterly disappointing.' Bailey & López de Prado DSR paper: 'After a sufficient number of trials, it is guaranteed that a researcher will always find a misleadingly profitable strategy... a backtest where the researcher has not controlled for the extent of the search... is worthless, regardless of how excellent the reported performance might be.' Low parameter count does NOT immunize against overfitting once N (trials) is uncontrolled.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf


### [11] Overfit backtests do not merely fail to generalize — they actively MINIMIZE future performance (negative IS→OOS slope in most practical cases), so a higher in-sample Sharpe from an aggressive search predicts a LOWER (often negative) OOS Sharpe. This justifies HEAVIER DSR/PBO gating for high-DoF searches (tuned tree ensembles) than for low-DoF boring baselines (Targets 2, 9).
**confidence:** high · **vote:** 2-1 (survived; corroborated by companion PNAS 2014 paper)

Bailey et al., 'The Probability of Backtest Overfitting': 'the β will be negative in most practical cases... overfit backtests minimize future performance: The model is so fit to past noise that it is often rendered unfit for future signal.' Companion PNAS (2014): 'backtest overfitting leads to negative expected returns out-of-sample.' The caveat 'in most practical cases' (slope magnitude scales with degree of overfitting) is preserved — the claim is normative, not deterministic, and supports proportional gating.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf


### [12] The Deflated Sharpe Ratio gives a concrete, sourced mechanism for differential gating: it deflates the observed Sharpe by the variance of Sharpe ratios ACROSS trials AND the number of independent trials N, so more configurations searched and more dispersed results raise the required Sharpe threshold even when the true Sharpe is zero. PBO is the conditional probability that the IS-best configuration underperforms the MEDIAN of the N candidates OOS — a model-free selection-overfitting metric that scales with N. DR-4 should impose DSR-with-N and PBO per promotable family, heavier for high-DoF challengers (Target 9).
**confidence:** high · **vote:** 3-0 (merged DSR-mechanism + PBO-definition claims)

Bailey & López de Prado DSR: benchmark SR0 = sqrt(V[SR_hat]) × ((1−γ)Φ⁻¹[1−1/N] + γΦ⁻¹[1−1/(N·e)]); increases monotonically in both sqrt(V[SR]) and N. PBO (Bailey et al. 2015): 'The probability that the model configuration selected as optimal IS will underperform the median of the N model configurations OOS' — estimated by the model-free CSCV procedure. CRITICAL: these verifications validate only the DEFINITIONS/mechanisms, NOT any numeric cutoff — DR-3's PBO<0.20 / t>3 / DSR-95% thresholds remain separately flagged as unsourced/under-specified (N-dependent), so promoting any family before DR-3 thresholds are locked is premature.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf


---

## Caveats / 미커버 영역

SCOPE OF VERIFICATION: The 21 confirmed claims establish the EVIDENCE BASE for the DR-4 audit but do not by themselves resolve every one of the 12 required output sections. Specifically, the evidence is dense and unanimous on: baseline composition (Target 1), raw-MVO reject (6), optimizer altitude/factor-attribution (7), tree-ensemble challenger status + heavier gating (2), TSFM/deep-sequence reject-for-alpha (5), and the multiple-testing-gate insufficiency / DR-3-threshold-not-locked problem (9). The evidence is THIN-TO-ABSENT in the verified set for: Target 3 (event/NLP alpha decay — NO event/news-alpha-decay primary source survived verification, so the claim that event/NLP is over-promoted to challenger is NOT yet evidence-backed here and should be treated as an open verification gap, not a settled finding); Target 4 (LLM on-path leakage — no LLM-discipline or schema-locking primary evidence in the verified set; this is a design/governance argument, not an empirically-verified claim); Target 8 (US-first/KR-later per-family split — no KR-microstructure or day-granular-disclosure primary evidence verified); Target 10 (Phase 1A/B/C/D queue ordering — supported indirectly by the 'minimize DoF / boring-baseline-first' logic but not by a dedicated source).

THRESHOLD vs DEFINITION: Every PBO/DSR claim that survived validates only the DEFINITION and MECHANISM of the metric, NOT any specific numeric cutoff. The project's prior red-team finding that DR-3's thresholds (PBO<0.20, t>3, DSR-95%) are unsourced/N-dependent is REINFORCED, not resolved — the literature confirms thresholds must be a function of trial count N and SR-dispersion, which DR-3 has not specified.

NON-REFUTING NUANCES carried by the evidence: (1) DGU-2009 (1/N hard to beat) and Yuan-Zhou-2024 (theory + conditional how-to-beat) are DISTINCT papers and must not be conflated; the prompt occasionally cites DGU where Yuan-Zhou is the actual source. (2) 1/N optimality is REGIME-CONDITIONAL (1-factor model, diversifiable risk, high N/T) — it is the boring baseline IN THE PROJECT'S regime, not a universal law. (3) Zakamulin's low-vol-tilt result is demonstrated on Kenneth-French factor-sorted datasets, so it is a strong cautionary attribution requirement, not proof that ALL optimizer outperformance is purely low-vol. (4) Gu-Kelly-Xiu's shallow-beats-deep is a finding about THAT panel attributed to small-data/low-SNR; later transformer wins use different architectures/larger data and are consistent with (not contradictory to) the attribution. (5) The estimation of the EFFECTIVE number of independent trials N is itself hard (requires clustering correlated configs) — a practical burden that strengthens, not weakens, the mandate to minimize DoF.

REFUTED-FOR-TRANSPARENCY: Three claims arguing properly-designed/low-turnover constrained MVO (VT/RRT) beats 1/N were REJECTED (0-3 / 1-2), and the claim that DGU's result is merely a research-design artifact was REJECTED (0-3). Net effect: the pro-optimizer rebuttal did NOT survive adversarial verification, so the reject-raw-MVO and demote-estimated-optimizer-from-baseline positions stand unweakened. One mechanistic Grinsztajn claim (three inductive biases) was also rejected (0-3) — but the headline 'trees state-of-the-art on medium tabular data' survived, so the conclusion is unaffected even though that particular causal explanation is not verified.

TIME-SENSITIVITY: All load-bearing sources are foundational/canonical (2009-2024) and current for their structural findings. The only genuinely fast-moving area is tabular foundation models (TabPFN/TabDPT 2025), which remain confined to large-data regimes outside the project's small/medium scope as of the knowledge cutoff.

---

## Refuted claims (적대 검증서 탈락 — 투명성)

- "DeMiguel, Garlappi & Uppal (2009)'s finding that naive 1/N diversification dominates mean-variance optimization out-of-sample is attributable largely to research design that focuses on portfolios subject to high estimation risk and extreme turnover, not to an inherent superiority of 1/N." — vote 0-3 · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1571351
- "Properly designed mean-variance optimization often outperforms naive 1/N diversification out-of-sample, but transaction-cost-driven turnover can erode that advantage." — vote 1-2 · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1571351
- "Two low-turnover, constrained variants of mean-variance selection — volatility timing (VT) and reward-to-risk timing (RRT) — outperform naive 1/N diversification even under high transaction costs, i.e. a disciplined optimizer with reduced degrees of freedom can beat the 1/N baseline." — vote 0-3 · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1571351
- "Trees outperform deep nets because of three inductive biases that neural nets lack: robustness to uninformative features, preservation of data orientation (rotation non-invariance), and ability to learn irregular/non-smooth target functions. These mechanisms are precisely the features of noisy financial tabular data (many uninformative features, non-smooth cross-sectional signal), explaining why GBDT is the appropriate tabular workhorse and why deep-sequence models are not a strong alpha source on small panels." — vote 0-3 · https://arxiv.org/abs/2207.08815

---

## Sources (22)

- https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901 — primary · baseline degrees-of-freedom / 1-over-N · 5 claims
- https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/why-naive-1n-diversification-is-not-so-naive-and-how-to-beat-it/4969319F5B1F3E350FB7FC8A73BA9F65 — primary · baseline degrees-of-freedom / 1-over-N · 4 claims
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1571351 — primary · baseline degrees-of-freedom / 1-over-N · 4 claims
- https://academic.oup.com/rfs/article/33/5/2223/5758276 — primary · baseline degrees-of-freedom / 1-over-N · 5 claims
- https://www.sciencedirect.com/science/article/abs/pii/S1544612316303555 — primary · baseline degrees-of-freedom / 1-over-N · 4 claims
- https://scientificportfolio.com/external-research-anthology/victor-demiguel-lorenzo-garlappi-raman-uppal-2009/optimal-versus-naive-diversification-how-inefficient-is-the-1-n-portfolio-strategy/ — secondary · baseline degrees-of-freedom / 1-over-N · 5 claims
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf — primary · tree-ensemble overfitting at small scale · 5 claims
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf — primary · tree-ensemble overfitting at small scale · 5 claims
- https://dachxiu.chicagobooth.edu/download/ML.pdf — primary · tree-ensemble overfitting at small scale · 5 claims
- https://arxiv.org/abs/2207.08815 — primary · tree-ensemble overfitting at small scale · 4 claims
- https://www.nber.org/system/files/working_papers/w20592/w20592.pdf — primary · tree-ensemble overfitting at small scale · 5 claims
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 — primary · tree-ensemble overfitting at small scale · 5 claims
- https://arxiv.org/pdf/2511.18578 — primary · TSFM / deep-sequence vs trees evaluation · 5 claims
- https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html — primary · TSFM / deep-sequence vs trees evaluation · 3 claims
- https://openreview.net/forum?id=kQDzqIkXLO — primary · TSFM / deep-sequence vs trees evaluation · 3 claims
- https://rpc.cfainstitute.org/research/financial-analysts-journal/1989/the-markowitz-optimization-enigma-is-optimized-optimal — primary · portfolio optimization: MVO error vs HRP/shrinkage/risk-parity · 4 claims
- https://jpm.pm-research.com/content/42/4/59.short — primary · portfolio optimization: MVO error vs HRP/shrinkage/risk-parity · 5 claims
- https://www.sciencedirect.com/science/article/abs/pii/S0167739X25000391 — primary · portfolio optimization: MVO error vs HRP/shrinkage/risk-parity · 4 claims
- http://www.ledoit.net/Goldilocks_RFS_2017.pdf — primary · portfolio optimization: MVO error vs HRP/shrinkage/risk-parity · 5 claims
- https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf — primary · event/news alpha decay + PIT timestamp discipline · 5 claims
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2080900 — primary · event/news alpha decay + PIT timestamp discipline · 5 claims
- http://www.econ.yale.edu/~shiller/behfin/2007-12/tetlock.pdf — primary · event/news alpha decay + PIT timestamp discipline · 5 claims

---

## Stats

```json
{
  "angles": 5,
  "sourcesFetched": 22,
  "claimsExtracted": 100,
  "claimsVerified": 25,
  "confirmed": 21,
  "killed": 4,
  "afterSynthesis": 12,
  "urlDupes": 3,
  "budgetDropped": 5,
  "agentCalls": 104
}
```