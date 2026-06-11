# 11 · DR-3 Claude Red-Team Audit (Validation Protocol)

> **적대 레드팀 대상:** ChatGPT DR-3 (`GPT DR-3 Primary.md`) — 모델 승격 전 검증 프로토콜(게이트·OOS·다중검정·비용·paper/shadow).
> **방법:** deep-research 하니스 (fan-out 검색 → 소스 fetch → 3-vote 적대 검증 → 종합). 통계 원전(López de Prado·Bailey·Harvey-Liu-Zhu·Lo) + 공식 데이터문서 한정.
> **생성:** 2026-06-08. runId `wf_54846d39-1c8`.
> **규모:** 108 agent calls · sources fetched 25 · claims extracted 116 · verified 25 · confirmed 23 · killed 2 · findings 12.

---

## VERDICT — PATCH-BEFORE-MODELS

The red-team audit of ChatGPT DR-3's validation protocol confirms three core attacks against its statistical "house rules." First, the t-statistic > 3.0 multiple-testing hurdle is correctly attributable to Harvey, Liu & Zhu (RFS 2016) — NOT Chen-Zimmermann (who are skeptics arguing the hurdle is too high), and HLZ's own framework shows the hurdle is NOT a flat constant but time-varying and N-dependent (≈1.96 → 3.78 by 2012 → 4.00 forecast 2032, differing by error-control target: ~3.9 for FWER@5%, ~3.0 for FDR@1%). Second, both the "DSR at 95%" and "PBO < 0.20" gates are under-specified or unsourced: DSR's threshold SR* is an explicit increasing function of the trial count N and cross-trial Sharpe variance (a flat 95% without N is incomputable, and the same SR=2.5 strategy flips reject→pass purely by lowering N to 46), while the PBO paper's ONLY endorsed cutoff is 0.05 (Neyman-Pearson) — so 0.20 is an unsourced house-rule strictly MORE lenient than the primary source. Third, DSR, family-t, and PBO are NOT interchangeable (they penalize different axes: trial multiplicity/dispersion vs. rank-consistency vs. a scalar threshold), and the necessity of purging/CPCV is driven by horizon-based OVERLAPPING labels — weak/absent for a monthly-rebalanced non-overlapping cross-sectional strategy — meaning full CPCV is computationally over-engineered (a genuine practical limit for a solo book lacking substantial compute), while walk-forward alone is empirically weak at false-discovery prevention. The over-arching verdict supports PATCH-BEFORE-MODELS: the protocol's frame is sound but every numeric threshold must either cite its primary source with the load-bearing parameter (N, error-rate target, S) attached, or be relabeled an explicit house-rule.

---

## Findings (적대 검증 통과)

### [1] The t-statistic > 3.0 multiple-testing hurdle for a new cross-sectional return factor is canonically Harvey, Liu & Zhu (RFS 2016), NOT Chen-Zimmermann. ChatGPT DR-3's 'family-level t-stat > 3' is correctly attributable to HLZ; a citation to Chen-Zimmermann would be a mis-attribution because they are SKEPTICS of the raised hurdle (arguing FDR is ~1% and most findings are likely TRUE), not its originators.
**confidence:** high · **vote:** 3-0 (across 4 merged claims [0,3,6,9])

Verbatim from HLZ abstract: 'A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0. We argue that most claimed research findings in financial economics are likely false.' Verified across four independent primary-source hosts (Duke author PDF, Oxford RFS, SSRN, NBER w20592). Authors = Campbell Harvey (Duke/NBER), Yan Liu (Texas A&M), Heqing Zhu (Oklahoma); RFS 29(1):5-68, Editor's Choice. Chen-Zimmermann POSTDATE HLZ by 5-6 years and argue AGAINST raising the hurdle (~98% of clearly-significant factors hold at t>1.96; FDR ~1%), so crediting them with t>3 is wrong on both date and stance. Implication: DR-3's t>3 should cite HLZ and be treated as a defensible-but-debated house rule, not a settled constant.

**Sources:**
- https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF
- https://academic.oup.com/rfs/article-abstract/29/1/5/1843824
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314
- https://www.nber.org/papers/w20592


### [2] The t>3.0 hurdle is NOT a flat static constant: it is TIME-VARYING, scales with the cumulative number of factors/trials tested (N), and differs by which multiple-testing error rate is controlled and at what level. A bare 'family t-stat > 3' is therefore under-specified unless it names the error rate (FWER vs FDR), the level, and the trial count.
**confidence:** high · **vote:** 3-0 (across 5 merged claims [1,2,4,5,7,8])

Verbatim HLZ: 'For Bonferroni, the benchmark t-statistic starts at 1.96 and increases to 3.78 by 2012. It reaches 4.00 in 2032.' And: 'a t-statistic of 3.9 and 3.0 is needed to control FWER at 5% and FDR at 1%, respectively... not far away from our previous estimates of 3.78 (Holm adjustment, FWER 5%) and 3.38 (BHY adjustment, FDR 1%).' The hurdle is explicitly monotonic in N: 'The Bonferroni adjusted t-ratio is monotonically increasing in the number of trials.' HLZ catalogue 316 factors and state 'our count of 316 tested factors is surely too low, this means the t-ratio cutoff is likely even higher.' INTERNAL MISMATCH in DR-3: it says 'family-level' (evokes FWER, which needs ~3.9) but uses the value 3.0 (which is HLZ's FDR-1% number) — the exact under-specification the red-team flagged. Note BHY (FDR) is non-monotonic, stabilizing ~3.39; the time-varying claim is correctly scoped to Bonferroni/Holm. Chen (arXiv 2204.10275) disputes the LEVEL but reinforces the under-specification point.

**Sources:**
- https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF
- https://academic.oup.com/rfs/article-abstract/29/1/5/1843824
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314


### [3] The Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) requires five inputs beyond the observed Sharpe — number of independent trials N, variance across trials' Sharpe estimates, sample length T, skewness, and kurtosis. The rejection benchmark SR* is an explicit INCREASING function of N and trial-Sharpe variance, so a flat 'DSR at 95%' stated without N and the trial moments is incomputable and under-specified by the paper's own definition.
**confidence:** high · **vote:** 3-0 (across 3 merged claims [11,13,21])

Verbatim: 'DSR deflates SR by taking into consideration five additional variables: The non-Normality of the returns (gamma3, gamma4), the length of the returns series (T), the variance of the SRs tested (V[{SR_n}]), as well as the number of independent trials involved in the selection (N).' SR* formula (False Strategy Theorem): SR* = sqrt(V[{SR_n}]) * ((1-gamma)*Z^-1[1-1/N] + gamma*Z^-1[1-1/(Ne)]), and 'SR* increases quickly as more independent trials are attempted (N), or the trials involve a greater variance.' The 95% is a separate probability target evaluated AGAINST this N/variance-dependent SR*, so omitting N omits the load-bearing parameter. Wikipedia and quant docs corroborate the same formula and N-dependence. PATCH: DR-3 must record N and the trial-return moments, not assert a bare 95%.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf


### [4] DSR's pass/fail verdict flips entirely with N at a fixed confidence level: the paper's own worked example shows the SAME strategy (annualized SR 2.5, T=1250) is REJECTED at the realized trial count but would PASS the 95% bar if found after only N=46 independent trials (DSR=0.9505), rising to N=88 under Normal returns. A flat numeric DSR threshold without declaring N is therefore not a coherent stand-alone gate.
**confidence:** high · **vote:** 3-0 (claim [12])

Verbatim: 'Should the strategist have made his discovery after running only N=46 independent trials, the investor may have allocated some funds, as [DSR] would have been 0.9505, above the 95% confidence level... If the strategy had exhibited Normal returns... [DSR]≈0.95 after N=88 independent trials.' Monotonicity confirmed: 'as the number of independent trials (N) grows, so will grow the expected maximum of {SR}.' The same SR=2.5 strategy flips reject→pass purely by lowering N. The paper's 'WHEN SHOULD WE STOP TESTING?' section warns N must be planned and disclosed. This is direct primary-source proof that DR-3's flat DSR-95% gate is incoherent without a declared/logged trial count.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf


### [5] DSR, family-level t-stat, and PBO are NOT interchangeable measures and can conflict by construction — they penalize different axes. DSR penalizes trial multiplicity AND cross-trial Sharpe dispersion (V[{SR_n}]), which a scalar t-hurdle does not capture; PBO measures rank-consistency between in-sample and out-of-sample via CSCV; family-t is a single threshold. A strategy can pass one and fail another.
**confidence:** high · **vote:** 3-0 (claim [13], corroborated by [14],[16],[22])

Verbatim DSR: 'Given a set of SR estimates, its expected maximum is greater than zero, even if the true SR is zero... SR* increases as more independent trials are attempted (N), or the trials involve a greater variance (V[{SR_n}]).' A family-t hurdle (HLZ) is a single scalar that does NOT take cross-trial Sharpe dispersion as an input, so DSR penalizes an axis (trial dispersion) the t-hurdle cannot. PBO is structurally separate (CSCV rank-based overfitting probability). The red-team's redundancy/conflict concern is therefore real but reversed: the three gates are NOT redundant — they are complementary, and DR-3 should not treat passing one as substituting for another.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf


### [6] PBO is formally the probability that an in-sample-optimal strategy ranks BELOW THE MEDIAN out-of-sample, computed via CSCV (Combinatorially Symmetric Cross-Validation): partition the TxN matrix into S row-blocks, form all C(S,S/2) symmetric train/test splits, compute per-split logits lambda_c = ln(omega_c/(1-omega_c)), and PBO = phi = integral from -inf to 0 of f(lambda). Its natural neutral value is 0.5 (a coin flip). A flat 'PBO<0.20' without specifying S, N, and the logit distribution is under-specified relative to this procedure.
**confidence:** high · **vote:** 3-0 (across 2 merged claims [14,16])

Verbatim Definition 2.2: 'the probability of backtest overfit (PBO). More precisely, PBO = SUM(n=1..N) Prob[rn < N/2 | r in Omega*_n]Prob[r in Omega*_n].' CSCV procedure verbatim: 'partition M across rows, into an even number S of disjoint submatrices... form all combinations CS taken in groups of size S/2... if S=16, we will form 12,780 combinations... logit lambda_c = ln omega_c/(1-omega_c)... PBO ... phi = integral_{-inf}^{0} f(lambda)dlambda.' The N/2 median threshold inside the formula confirms 0.5 as the coin-flip baseline. The paper ties phi's resolution to N and the logit distribution: 'if the investor is sensitive to values of phi < 1/10... N >> 10 is required.' So PBO<0.20 is under-specified without S, N, and f(lambda).

**Sources:**
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf


### [7] The ONLY numerical PBO rejection threshold endorsed by the primary source is PBO > 0.05 (Neyman-Pearson framing). There is NO 0.20 cutoff and NO 0.20-0.35 quarantine band anywhere in the paper. ChatGPT DR-3's 'PBO < 0.20' is an unsourced house-rule that is strictly MORE LENIENT than the only number the authors offer, and cannot be attributed to this primary paper.
**confidence:** high · **vote:** 3-0 (claim [15])

Verbatim: 'In accordance with standard applications of the Neyman-Pearson framework, a customary approach would be to reject models for which PBO is estimated to be greater than 0.05.' Exhaustive regex search of the full extracted PDF returned ZERO hits for '0.20', '0.35', '20%', '35%', or 'quarantine'. A strategy with PBO=0.15 PASSES DR-3's rule but FAILS the authors' customary 0.05 rule. PATCH: relabel PBO<0.20 as an explicit house-rule (and justify the relaxation), or tighten toward the paper's 0.05. Note the paper calls 0.05 'customary,' not a hard derivation, so 0.05 is itself trial-count-dependent — but that does not rescue 0.20's attributability.

**Sources:**
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf


### [8] Controlling for the number of trials (I/N) is MANDATORY and is the prerequisite for ANY multiple-testing statistic — FWER, FDR, and PBO cannot even be computed without it. Under a true-zero-Sharpe martingale the expected maximum Sharpe across I trials is strictly positive (order sqrt(2 log I)), so selecting the max-Sharpe backtest is a false discovery by construction. DR-3 must therefore log a program-level trial/experiment count, not merely apply flat thresholds.
**confidence:** high · **vote:** 3-0 (claim [22], corroborated by [11],[12],[21])

Verbatim Lopez de Prado: 'researchers will select the backtest with the maximum estimated Sharpe ratio, even if the true Sharpe ratio is zero. That is the reason why it is imperative to control for the number of trials (I)... Without this information, it is not possible to determine the Family-Wise Error Rate (FWER), False Discovery Rate (FDR), Probability of Backtest Overfitting (PBO) or similar.' This grounds a CRITICAL MISSING GATE the red-team flagged: program-level (not just family-level) multiple-testing accounting requires a logged experiment count I across the whole research history. The sqrt(2 log I) is the correct asymptotic growth of the max of I Gaussians (the paper uses the Gauss extreme-value approximation).

**Sources:**
- https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf


### [9] Cross-validation leakage in finance is CONDITIONAL on two mechanisms — serial correlation in features AND labels formed on OVERLAPPING data. The purging/CPCV remedy is mechanically triggered by label-window overlap, which is weak or absent for a monthly-rebalanced cross-sectional strategy with non-overlapping holding periods. Therefore the necessity of full CPCV is driven by horizon-based overlapping labels, not by cross-sectional ranking per se — bearing directly on whether DR-3's monthly strategy needs full CPCV.
**confidence:** high · **vote:** 2-1 (claim [19])

Verbatim Lopez de Prado: 'Consider a serially correlated feature X that is associated with labels Y that are formed on overlapping data: (1) Because of the serial correlation, X_t ≈ X_{t+1}; (2) because labels are derived from overlapping data points, Y_t ≈ Y_{t+1}. Then, placing t and t+1 in different sets leaks information.' The leakage and purging remedy key off label time-spans overlapping. CAVEAT (the 2-1 split / one minor over-statement): LdP treats serial correlation as a partially independent second channel that embargo guards against even absent direct label overlap, so the claim's 'only' is slightly strong; but the core conclusion — full CPCV's necessity is driven by overlapping labels, weak for non-overlapping monthly rebalancing — survives. Conclusion is correctly confined to 'full CPCV' (does not claim zero purging needed).

**Sources:**
- https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf


### [10] Purging removes training observations whose label-spanning intervals [t_j,0, t_j,1] overlap the test labels; embargo removes only the training observations IMMEDIATELY FOLLOWING the test set (asymmetric, post-test only), with a small h ≈ 0.01T typically sufficing. This is the precise sourced definition the protocol must match — and where purging/embargo IS essential (overlapping multi-day holding returns, feature windows spanning the label).
**confidence:** high · **vote:** 3-0 (claim [20])

Verbatim: 'eliminate from the training set all observations whose labels overlapped in time with those labels included in the testing set. I call this process purging... eliminate from the training set observations that immediately follow an observation in the testing set. I call this process embargo. The embargo does not need to affect training observations prior to a test... A small value h ≈ .01T... often suffices.' CITATION-HYGIENE PATCH: the verbatim detailed passage is from the BOOK Advances in Financial Machine Learning (2018, Ch. 7), not the GARP whitepaper — cite AFML Ch.7. Substance verified independently (Wikipedia Purged_cross-validation confirms purging removes observations whose timestamp falls within a test label's formation range, and embargo can only occur after the test set).

**Sources:**
- https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf


### [11] Walk-forward — which DR-3 designates as its PRIMARY OOS layer — has notable shortcomings in false-discovery prevention relative to CPCV (higher temporal variability, weaker stationarity), undercutting reliance on walk-forward ALONE as the primary leakage/overfitting control. This supports DR-3's choice to NOT rely on walk-forward alone, while flagging that walk-forward should not be the sole gate.
**confidence:** medium · **vote:** 3-0 (claim [17])

Verbatim peer-reviewed (Arian, Norouzi M. & Seco, Knowledge-Based Systems Vol. 305, Dec 2024): 'Walk-Forward, by contrast, exhibits notable shortcomings in false discovery prevention, characterized by increased temporal variability and weaker stationarity.' CONFIDENCE CAPPED AT MEDIUM because evidence is from a SYNTHETIC controlled environment the authors explicitly flag may not generalize ('might not generalize across all market conditions'), and it is one study. QUALIFICATION (not contradiction): walk-forward is uniquely realistic for live-deployment simulation (chronological, no look-ahead at decision time) — a realism virtue, not a false-discovery virtue. Note: two STRONGER claims that 'CPCV empirically outperforms WF/K-Fold' were REFUTED (votes 1-2 and 0-3) in verification, so the comparative ranking of CPCV is NOT established — only walk-forward's standalone weakness is.

**Sources:**
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376
- https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110


### [12] CPCV's computational intensity is a genuine practical limitation that can preclude real-time/large-scale use without substantial compute — directly supporting the red-team's 'scale-inappropriate for a solo book' concern. The authors rely on parallelization to make CPCV feasible, which a tiny solo ~₩100M book lacking substantial compute does not have. This justifies trimming/optional-izing full CPCV at solo scale.
**confidence:** medium · **vote:** 3-0 (claim [18])

Verbatim (Arian, Norouzi M. & Seco): 'the computational intensity of advanced cross-validation methods, especially CPCV, could limit their practical application in real-time trading systems without substantial computational resources' and 'parallelization significantly improves efficiency, making them feasible for large-scale financial datasets.' Corroborated by multiple practitioner sources (CPCV 'orders of magnitude more intensive than a simple backtest'). CONFIDENCE MEDIUM: this is an academic limitations statement plus operational evidence, not a statistical-correctness result. Combined with the overlapping-label finding (full CPCV's necessity is driven by overlapping labels, weak for monthly non-overlapping rebalancing), this is the strongest sourced basis for the scale-appropriateness verdict: keep purging+embargo around the rebalance horizon, make full CPCV OPTIONAL/diagnostic for a solo book, reserve it for model-family comparison.

**Sources:**
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376
- https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110


---

## Caveats / 미커버 영역

SCOPE: These 23 confirmed claims cover ONLY the statistical-method targets of the brief (the multiple-testing/DSR/PBO/purging/CPCV/walk-forward block — brief items 1-3). The verified evidence does NOT independently substantiate the brief's other house-rule attacks: IR>0.25 false-precision on a 1-year holdout (Lo 2002 sampling-error argument), the drawdown -10pp/-5pp veto, 2x/3x cost stress, 5%/10% ADV capacity, ≤5bp/≤30bp benchmark replication error, or the 8wk+8wk paper/shadow duration. Those remain ASSERTED-BUT-UNVERIFIED in this synthesis — treat the red-team's critiques of them as plausible house-rule flags pending primary grounding (Lo 'The Statistics of Sharpe Ratios' 2002 was named in the brief but no confirmed claim retrieved it). SOURCE QUALITY: the statistical core rests on PRIMARY sources (HLZ RFS 2016 verified across 4 hosts; Bailey-LdP DSR 2014 and PBO 2016 author PDFs text-extracted verbatim; LdP GARP whitepaper / AFML 2018) — these are high-strength. The walk-forward/CPCV comparative findings rest on a SINGLE 2024 study (Arian-Norouzi-Seco) in a SYNTHETIC environment the authors flag may not generalize — hence medium confidence, and the stronger 'CPCV beats all' claims were explicitly REFUTED in verification. CITATION HYGIENE: one purging/embargo claim mis-cited the GARP whitepaper for text that is actually from AFML 2018 Ch.7 (same author, substance correct). TIME-SENSITIVITY: the HLZ hurdle is dated (3.0 ≈ 2012 snapshot, projected 4.00 by 2032) — any flat application is already stale; and the Chen-Zimmermann counter-literature (FDR ~1%, hurdle contested) means t>3 should be labeled defensible-but-debated, not settled. NOT EVALUATED: per the brief, no alpha models, rankings, or strategy recommendations were assessed; data-gate items (EDGAR/OpenDART/CRSP) inherit from prior DR-2A/DR-2B locks and were not re-verified here.

---

## Open Questions

- Is the red-team's Lo-2002 sampling-error attack on the hard IR>0.25 gate (and Sharpe-type gates on a ~252-day holdout) supported by the primary source? No confirmed claim retrieved Lo 'The Statistics of Sharpe Ratios' (2002), so whether a hard single-number IR cutoff on a 1-year holdout is statistically indefensible vs. should be confidence-interval/sign-based remains unverified.
- What primary justification, if any, exists for the operational house-rules left unaudited here — the drawdown veto (-10pp/-5pp), 2x/3x cost stress multipliers, 5%/10% ADV participation caps, ≤5bp/≤30bp benchmark replication error, and 8wk+8wk paper/shadow durations? These appear to be unsourced round numbers but none were independently checked against a primary source in this verification round.
- Given the overlapping-label finding makes full CPCV optional for monthly non-overlapping rebalancing, what is the minimal sufficient purging/embargo configuration (h value, embargo window relative to the ~monthly rebalance horizon) for THIS cross-sectional strategy — and does any feature window spanning the label re-introduce overlap that would make purging mandatory after all?
- Should the program-level trial-count (I) accounting that the LdP source mandates be reconciled with HLZ's program-vs-family distinction — i.e., does DR-3 need BOTH a per-family correction AND a whole-research-history N registry, and how is N estimated (effective/independent trials via clustering) for a solo operator's in-house search rather than a cross-literature factor census?

---

## Refuted claims (적대 검증서 탈락 — 투명성)

- "Empirically, CPCV (Combinatorial Purged Cross-Validation) is superior to Walk-Forward, K-Fold, and Purged K-Fold at mitigating backtest overfitting, evidenced by a lower Probability of Backtest Overfitting (PBO) and a superior Deflated Sharpe Ratio (DSR) test statistic. This is the primary empirical support for DR-3's choice to include CPCV in the OOS stack." — vote 1-2 · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376
- "Combinatorial Purged Cross-Validation (CPCV) empirically outperforms Walk-Forward and K-Fold methods, showing lower Probability of Backtest Overfitting (PBO) and a superior Deflated Sharpe Ratio (DSR) test statistic — i.e., the three-layer OOS design ChatGPT proposes (walk-forward + purged CV + CPCV) is ranked by this peer-reviewed study with CPCV as the strongest, not as redundant theater." — vote 0-3 · https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110

---

## Sources (25)

- https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF — primary · academic/primary — multiple-testing t-hurdle attribution · 5 claims
- https://academic.oup.com/rfs/article-abstract/29/1/5/1843824 — primary · academic/primary — multiple-testing t-hurdle attribution · 5 claims
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314 — primary · academic/primary — multiple-testing t-hurdle attribution · 5 claims
- https://www.nber.org/papers/w20592 — primary · academic/primary — multiple-testing t-hurdle attribution · 4 claims
- https://foxholm.com/q/research/harvey-liu-zhu-cross-section/ — secondary · academic/primary — multiple-testing t-hurdle attribution · 5 claims
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf — primary · academic/primary — DSR & PBO exact definitions · 5 claims
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf — primary · academic/primary — DSR & PBO exact definitions · 5 claims
- https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio — secondary · academic/primary — DSR & PBO exact definitions · 5 claims
- https://medium.com/balaena-quant-insights/the-probability-of-backtest-overfitting-pbo-9ba0ac7fb456 — blog · academic/primary — DSR & PBO exact definitions · 5 claims
- https://en.wikipedia.org/wiki/Purged_cross-validation — secondary · technical/scope — purged CV & CPCV necessity for cross-sectional · 5 claims
- https://blog.quantinsti.com/cross-validation-embargo-purging-combinatorial/ — blog · technical/scope — purged CV & CPCV necessity for cross-sectional · 5 claims
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376 — primary · technical/scope — purged CV & CPCV necessity for cross-sectional · 5 claims
- https://www.mlfinlab.com/en/latest/cross_validation/cpcv.html — unreliable · technical/scope — purged CV & CPCV necessity for cross-sectional · 0 claims
- https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf — primary · technical/scope — purged CV & CPCV necessity for cross-sectional · 5 claims
- https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110 — primary · technical/scope — purged CV & CPCV necessity for cross-sectional · 5 claims
- https://traders.studentorg.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf — primary · statistical-robustness — Sharpe/IR sampling error on short holdout · 5 claims
- https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios — primary · statistical-robustness — Sharpe/IR sampling error on short holdout · 4 claims
- http://www.sharperat.io/sharpe-symmetric-ci-one.html — secondary · statistical-robustness — Sharpe/IR sampling error on short holdout · 4 claims
- https://www.twosigma.com/wp-content/uploads/sharpe-tr-1.pdf — primary · statistical-robustness — Sharpe/IR sampling error on short holdout · 5 claims
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces — primary · practitioner/implementation — data gates, capacity, shadow duration at small scale · 5 claims
- https://www.sec.gov/about/webmaster-frequently-asked-questions — primary · practitioner/implementation — data gates, capacity, shadow duration at small scale · 5 claims
- https://www.tylergshumway.org/Shumway-DelistingBiasCRSP-1997.pdf — primary · practitioner/implementation — data gates, capacity, shadow duration at small scale · 5 claims
- https://tylergshumway.org/Shumway-DelistingBiasCRSPs-1999.pdf — primary · practitioner/implementation — data gates, capacity, shadow duration at small scale · 5 claims
- https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001 — primary · practitioner/implementation — data gates, capacity, shadow duration at small scale · 4 claims
- https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf — primary · contrarian/scale — backtest validation for solo/small book proportionality · 5 claims

---

## Stats

```json
{
  "angles": 6,
  "sourcesFetched": 25,
  "claimsExtracted": 116,
  "claimsVerified": 25,
  "confirmed": 23,
  "killed": 2,
  "afterSynthesis": 12,
  "urlDupes": 4,
  "budgetDropped": 6,
  "agentCalls": 108
}
```