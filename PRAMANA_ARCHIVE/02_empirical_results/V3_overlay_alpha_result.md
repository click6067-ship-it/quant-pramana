# V3 — TREND + VOL-REGIME Overlay Alpha (US ETFs) — Result
**Date:** 2026-06-11 · **Engine:** `engine/overlay_alpha.py` · **Data:** cached `outputs/raw/SFP_FUNDS.csv` (23 ETFs, REAL closeadj incl. LETF decay) · API off
**Window:** 2017-05-31 .. 2026-05-29 (109 monthly rebals) · paper only, no live

## Goal
Build a NEW, ideally LOW-CORRELATION net-of-cost return stream to *add* to the existing market-neutral (MN) equity book (`outputs/engine/book_ledger.csv` `applied_ret` = the realized 1x book return after its leverage/kill risk-engine). The whole point: does it *diversify*? (Verdict is robust: re-running against raw `net_1x` gives corr +0.061 and against leveraged `net_agg` gives corr +0.034 — all far under the kill, all with positive combo uplift.)

## Signal definitions (ONE each, fixed — no tuning, no window hunting)
- **Trend:** `closeadj > 200-day SMA` on the **15 unlevered ETFs** (SPY QQQ IWM DIA + 11 sector SPDRs). Monthly: hold (long) the uptrend ETFs, **flat** the rest, **equal-weight** the on-set. Long-FLAT (the MN book already supplies a short side). LETF/vol products are **never held** (real-decay assets used as context only).
- **Vol regime:** 20-day realized vol of SPY, annualized. **Fixed** rule: risk-ON (x1.0) when ann.vol < 20%, risk-OFF (x0.5) when >= 20%. Scalar on the whole sleeve.
- **Cost:** flat **5 bp/side** (commission+spread) on monthly turnover. Stress = **x2**.
- Rebalanced on the equity book's month-end dates so monthly correlation aligns exactly. Returns from real prices at those dates.

## PRE-REGISTERED KILL CONDITIONS (set before results)
1. **net Sharpe <= 0** -> FAIL.
2. **correlation to equity book > +0.60** (not diversifying) -> FAIL.
3. **dies at 2x cost** (net Sharpe <= 0) -> FAIL.
4. **50/50 combo Sharpe NOT > equity-only Sharpe** (overlay adds nothing) -> FAIL.

## Results (net of cost)
| metric | value |
|---|---|
| gross Sharpe | +0.87 |
| **NET Sharpe (5bp/side)** | **+0.85** |
| NET Sharpe (2x cost) | +0.83 |
| CAGR (net) | +9.69% |
| maxDD (net) | -16.16% |
| avg exposure | 0.89 |
| avg turnover/mo | 0.38 |
| cost drag/yr | +0.23% |

## ★ Correlation to equity MN book (the whole point)
- overlapping months: **109**
- **corr(overlay net, equity `applied_ret`) = +0.018**  (FAIL threshold +0.60)

| sleeve (overlap window) | Sharpe |
|---|---|
| equity MN book only | +0.33 |
| overlay only | +0.85 |
| **50/50 combo** | **+0.85** |
| combo uplift vs equity-only | +0.51 |

## Annual net returns
| year | overlay | equity book |
|---|---|---|
| 2017 | +12.8% | +7.6% |
| 2018 | -4.9% | +5.8% |
| 2019 | +18.3% | -0.3% |
| 2020 | +4.4% | -7.8% |
| 2021 | +28.0% | +13.5% |
| 2022 | -15.0% | -8.4% |
| 2023 | +15.3% | +2.2% |
| 2024 | +16.7% | +17.1% |
| 2025 | +12.1% | +0.1% |
| 2026 | +6.6% | +0.0% |

## VERDICT: SURVIVE (all pre-registered kills passed)

### Honest read
- Standalone net edge (5bp & 2x): **yes** (net Sharpe +0.85 / 2x +0.83).
- Diversifying vs equity book: **yes** (corr +0.018).
- Raises combined Sharpe: **yes** (+0.33 -> +0.85).
- A long-flat trend overlay is **net-long beta**, so positive correlation to a broad equity book is expected; the test is whether it stays under +0.60 and still lifts the combined Sharpe. Paper only. No parameter was tuned; this is a single pre-registered shot.
