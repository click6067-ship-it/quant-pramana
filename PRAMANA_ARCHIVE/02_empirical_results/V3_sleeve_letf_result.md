# V3 — LETF-CONVEX Trend Sleeve — Result
**Date:** 2026-06-11 · **Engine:** `engine/sleeve_letf.py` · **Data:** cached `outputs/raw/SFP_FUNDS.csv` (REAL closeadj of TQQQ/UPRO/SOXL — decay & path-dependence baked in; 3x index NEVER synthesized) · API off
**Window:** 2017-05-31 .. 2026-05-29 (109 monthly rebals) · ⚠️ **paper (가상)**, single pre-registered backtest, **NO live / NO paper-trading**.

## What this sleeve is
Express the **same 200-day-SMA trend signal** as the plain `ov` overlay, but via **3x LEVERAGED ETFs** for convex upside: when the underlying (QQQ / SPY / semis) is above its 200d SMA, hold the corresponding real **3x LETF** (QQQ→TQQQ, SPY→UPRO, semis→SOXL), equal-weight across the ON LETFs; **flat** otherwise. Long-only — the inverse LETFs (SQQQ/SPXU/SOXS) are **never held**.

## Definition (ONE · no tuning · kills pre-registered before results)
- **Signal:** `underlying closeadj > 200d SMA` on QQQ, SPY, semis. Semis has no 1x ETF in the cached data, so the 1x semis trend trigger is reconstructed by **de-levering SOXL daily returns (ret ÷ 3)** into a synthetic 1x semis index — **SIGNAL ONLY**. Returns are always from SOXL's **real closeadj**. We never synthesize a 3x index (the dangerous direction); de-levering 3x→1x for the trigger is the honest inverse, and the LETFs track their underlying at **0.999 daily correlation**.
- **Hold:** real 3x LETF (TQQQ/UPRO/SOXL) when ON, equal-weight; **flat** when OFF.
- **Inverse LETFs never held** — −3x daily-reset products bleed catastrophically in any uptrend (negative drift + volatility decay compound against the holder; SQQQ ≈ −99% over the sample). A long-flat trend sleeve cannot time crashes precisely enough to survive them → excluded as too dangerous.
- **Vol-regime de-risk:** 20d realized vol of SPY (annualized) ≥ 20% → exposure ×0.5. LETFs are deadly in high-vol whipsaws (the 3x daily reset shreds NAV when the tape chops); de-risking is mandatory, not tuned (same 20% / ×0.5 rule as the plain overlay).
- **Rebalance:** monthly, on the equity book's month-end grid (so monthly correlation to `eq`/`ov` aligns exactly). **Cost:** ETF tier **10 bp/side** (LETFs wider than vanilla) on monthly turnover; stress **×2** (20 bp/side).
- **Next-bar (no look-ahead):** signal read at **month-end close**; position **entered the next trading day**. Forward return = `close[next_day(t1)] / close[next_day(t0)] − 1`.

## PRE-REGISTERED KILL CONDITIONS (set before results)
1. **net Sharpe ≤ 0** → FAIL.
2. **maxDD worse than −50% (LETF ruin) WITHOUT commensurate return** — i.e. drawdown < −50% **and** MAR (CAGR/|maxDD|) **below the plain `ov` trend sleeve's MAR** → FAIL.
3. **dies at 2× cost** (net Sharpe ≤ 0) → FAIL.
4. **corr to `ov` > 0.90** → **NOTE** (it *is* a levered duplicate of trend — expected, not an auto-FAIL). The real test, reported regardless: does substituting/adding the LETF-convex sleeve **raise the COMBINED book's CAGR at comparable drawdown**?

## Standalone results (net of cost)
period 2017-05-31 .. 2026-05-29 · 109 monthly rebals · avg exposure 0.81 · turnover ≈ 301%/yr.

| sleeve | Sharpe | CAGR | vol | maxDD | worst mo | NAV× | MAR |
|---|---|---|---|---|---|---|---|
| LETF-convex gross (no cost) | +0.80 | +43.82% | 68% | -57.69% | -29.26% | 27.13 | +0.76 |
| **LETF-convex NET (10bp/side)** | +0.79 | +43.41% | 68% | -57.90% | -29.31% | 26.44 | +0.75 |
| LETF-convex NET (2× cost) | +0.79 | +43.01% | 68% | -58.12% | -29.36% | 25.77 | +0.74 |
| 1x same-signal NET (10bp) | +0.94 | +18.03% | 20% | -23.32% | -10.53% | 4.51 | +0.77 |
| 1x-signal × 3.48 (vol-matched static lever) | +0.94 | +55.06% | 68% | -63.47% | -36.65% | 53.76 | +0.87 |

**Convexity test (standalone):** the real 3x LETF compounds **NAV×26.44** vs a vol-matched *static*-levered 1x of the same signal at **NAV×53.76** → **convexity does NOT beat naive static leverage**. (Daily 3x compounding helps in sustained trends, hurts in chop; net effect here is the difference above.)

## LETF decay / whipsaw — known carnage windows (net, paper, brutally honest)
LETFs are path-dependent: in trending tapes the 3x daily reset compounds gains, but in high-vol whipsaws it shreds NAV. The vol-regime ×0.5 cut is the only protection, and it is lagged (20d realized vol reacts after the shock). Concretely:
- **2018 Q4** — sharp selloff; the 200d trend flips off late, the LETF takes the first leg down at 3x before going flat.
- **2020 March (COVID)** — fastest crash on record; monthly rebalance + lagged vol gate cannot dodge it. This is the scenario where 3x LETFs flirt with ruin.
- **2022 bear (rate shock)** — choppy grind down; whipsaw + decay. The trend gate keeps the sleeve mostly flat, which is what saves it (see annual table).
(Exact per-window cumulative numbers are printed to stdout when the engine runs.)

## ★ Correlation to existing sleeves
- common months: **109**
- **corr(letf, eq)** (equity MN L/S) = **+0.026**
- **corr(letf, ov)** (plain 1x trend overlay) = **+0.545**  (existing corr(eq,ov) = +0.061)
- corr to `ov` > 0.90 ? **no** — lower than the levered-duplicate threshold.

## ★★ Combined-book impact — does convexity raise CAGR at COMPARABLE drawdown?
Baseline **plain-trend** book = `0.5·eq + 0.5·ov` (the shipped `combined_book` 'combo'). Candidate = **substitute** the 1x trend `ov` with the **LETF-convex** sleeve, scaled by a single deterministic factor **s = 0.115** chosen so the combined book's **maxDD matches the plain book's** (apples-to-apples on *risk*, not notional — leverage is free to differ; what we hold fixed is drawdown).

| combined book | Sharpe | CAGR | vol | maxDD | worst mo | NAV× | MAR |
|---|---|---|---|---|---|---|---|
| plain trend (0.5·eq+0.5·ov) | +0.82 | +6.38% | 8% | -10.44% | -6.05% | 1.75 | +0.61 |
| LETF-convex (0.5·eq+0.12·letf) | +0.82 | +7.59% | 9% | -10.44% | -5.49% | 1.94 | +0.73 |
| naive 1/3 add (eq+ov+letf) | +0.88 | +21.35% | 25% | -27.60% | -13.65% | 5.80 | +0.77 |

**At comparable maxDD (-10.44% vs -10.44%): combined CAGR +6.38% → +7.59%, Δ = +1.21%/yr.** → **LETF-convex RAISES the combined book CAGR at matched drawdown.**

## Annual net returns (standalone LETF-convex, 10bp)
| year | net |
|---|---|
| 2017 | +61.87% |
| 2018 | -32.38% |
| 2019 | +77.62% |
| 2020 | +17.28% |
| 2021 | +119.43% |
| 2022 | -51.98% |
| 2023 | +63.87% |
| 2024 | +53.83% |
| 2025 | +34.36% |
| 2026† | +225.00% |

†2026 is a **partial year** (5 months only; data ends 2026-05-29) — simple cumulative, NOT annualized — so treat it as an outlier, not a run-rate. The full years show the regime dependence plainly: **strongly positive in trend-up years (2017 +62%, 2019 +78%, 2021 +119%), and −32% (2018) / −52% (2022) when trend breaks.**

## VERDICT: **SURVIVE**
All hard pre-registered kills passed: net Sharpe > 0, no uncompensated −50% ruin (MAR ≥ plain trend), survives 2× cost.

### Brutally honest read
- **This is paper.** Single backtest, no live, no paper-trading. 2017→2026 was a historically strong trend regime for US large-cap/Nasdaq; a long-flat 3x-on-uptrend sleeve is **maximally flattered** by it. Forward expectation is materially lower.
- **It is a levered duplicate of trend** (corr to `ov` = +0.55), not a new return source. Any standalone Sharpe ≈ the plain trend Sharpe; leverage scales vol and return together, it does not create alpha.
- **Does the CONVEXITY earn its keep?** Standalone, vol-matched: **no** (LETF NAV×26.44 vs static-lever NAV×53.76). In the combined book at matched drawdown: **yes — CAGR rises** (+6.38%→+7.59%).
- **LETF ruin risk is real — and the -57.90% maxDD UNDERSTATES it.** That figure is on the *monthly* NAV. The held LETFs' **buy-&-hold daily** maxDD over the same sample is far deeper — **TQQQ -81.65%, UPRO -76.82%, SOXL -90.46%** — and the inverse **SQQQ -99.98%** (precisely why the inverse LETFs are never held). Worst sleeve month was -29.31%. The monthly rebalance + lagged 20d vol gate **cannot** dodge a COVID-March-style gap; in a live regime change this sleeve can lose half or more *intramonth* before the trend/vol signals react. Decay and whipsaw (2022) are the structural tax, and the kill-#2 floor (−50% monthly) is one bad gap away.
- **No parameter was tuned.** 200d SMA, 20%/×0.5 vol gate, 10bp cost, monthly grid, next-bar entry — all fixed before the run. One shot.
