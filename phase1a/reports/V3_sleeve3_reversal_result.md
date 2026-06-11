# V3 — Candidate Sleeve3: Short-Term (1-Month) Reversal — RESULT

**Question.** Does a 3rd alpha sleeve — classic cross-sectional **short-term reversal** — add a THIRD near-uncorrelated diversifying return stream to the existing 2-sleeve US book?
Existing book: **sleeve1 `eq`** = equity sector-neutral market-neutral L/S (momentum+quality+earnings-revision); **sleeve2 `ov`** = ETF trend+vol overlay. The two are near-zero correlated (+0.06).

**Status: paper / virtual / single backtest — NO live, NO paper-trade.** One definition, no tuning, no window hunting.
**Run:** `./.venv/bin/python engine/sleeve3_reversal.py` → `outputs/engine/sleeve3_reversal_nav.csv`. Cached data only (no API).

---

## PRE-REGISTERED KILLS (written BEFORE results)

| # | Kill condition | Rationale |
|---|----------------|-----------|
| K1 | **net Sharpe ≤ 0 → FAIL** | a diversifier must at least earn its own keep net-of-cost |
| K2 | **\|corr\| > 0.5 to EITHER `eq` or `ov` → NOT diversifying** | must be near-uncorrelated to add a 3rd stream |
| K3 | **dies at 2× cost → FAIL** | must be cost-robust; ST reversal is high-turnover |
| K4 | **turnover so high net is negative → FAIL** | turnover must not eat the entire gross edge |

ST reversal is well known to be largely an **illiquidity / microstructure premium** that typically **DIES after cost in liquid large-caps**. This test reports the truth either way.

---

## Candidate definition (ONE, frozen — no tuning)

- **Universe:** top-1500 PIT membership (`broad_universe_top1500.csv`), survivorship-safe, common stock only. Avg 1,484 members/month.
- **Signal:** `−(prior 1-month return)` = `−(mpx.shift(1)/mpx.shift(2) − 1)` on the monthly grid → high score = prior loser.
- **Sector-neutral:** demean signal within `sector` (same convention as `ls_book.py`).
- **Portfolio:** **LONG bottom-prior-return quintile (losers), SHORT top quintile (winners)**, equal-weight, dollar-neutral. (Quintile = primary ONE definition; decile reported for reference.)
- **Forward return:** next month (`mpx.shift(-1)/mpx − 1`).
- **Costs (CRITICAL — high turnover):**
  - `cost.tier_marketcap_bps` (marketcap tercile 5 / 10 / 15 bp one-way) applied **round-trip (×2) on turnover, both legs**.
  - **Short borrow ~0.5%/yr** flat on the short leg.
  - `cost.turnover_oneway` (frozen) on the membership set, both legs.
- **Metrics:** monthly, Sharpe = mean/std·√12 (`combined_book.perf` / `ls_book.st`, frozen). Period **2016-03 → 2026-05, 123 months**; correlation/combo on the **109-month** overlap with `eq`/`ov`.

---

## RESULTS (actual numbers)

**Turnover ≈ 937%/yr** (one-way, two-leg average) — i.e. the book turns over ~9×/yr. Decile ≈ 1035%/yr. Honestly reported: this is brutal turnover, exactly the ST-reversal signature.

### Quintile (primary)

| Variant | Sharpe | CAGR | vol | maxDD | 2021–26 Sharpe |
|---|---:|---:|---:|---:|---:|
| gross (no cost) | **−0.52** | −4.27% | 7.8% | −40.3% | −0.91 |
| **net (1× cost)** | **−1.07** | **−8.27%** | 7.8% | −60.7% | −1.44 |
| net (2× cost — stress) | **−1.62** | −12.11% | 7.8% | −74.2% | −1.97 |

### Decile (reference only)

| Variant | Sharpe | CAGR | vol | maxDD |
|---|---:|---:|---:|---:|
| net (1× cost) | −1.02 | −10.50% | 10.3% | −70.8% |
| net (2× cost) | −1.47 | −14.59% | 10.3% | −81.6% |

**The gross signal is already negative (Sharpe −0.52) over this sample.** In top-1500 liquid large-caps over 2016–2026, "buy the 1-month loser / short the 1-month winner" did **not** even work before costs — the classic ST-reversal premium has decayed/inverted in this liquid universe (a continuation/crowding-into-winners regime), and cost then drives it deep negative. ₩100M → **₩0.41억 (−59%)** over 10y at 1× net.

---

## CORRELATIONS (109-month overlap)

| pair | corr |
|---|---:|
| **corr(reversal, eq)** | **−0.28** |
| **corr(reversal, ov)** | **−0.09** |
| corr(eq, ov) (existing, for reference) | +0.06 |

Correlations ARE low (both \|corr\| < 0.5 → **K2 passes**). The reversal stream is genuinely near-uncorrelated (even mildly negatively correlated to `eq`). **But low correlation to a money-LOSING stream does not help** — a diversifier must also earn a non-negative net return.

---

## 3-SLEEVE COMBO vs 2-SLEEVE COMBO (equal-weight, net, no leverage)

| Combo | Sharpe | CAGR | vol | maxDD | 2021–26 Sharpe |
|---|---:|---:|---:|---:|---:|
| 2-sleeve (eq+ov, 50/50) | **+0.82** | +6.38% | 7.9% | −10.4% | +1.11 |
| 3-sleeve (eq+ov+rev, 1/3) | **+0.25** | +1.18% | 5.3% | −9.7% | +0.27 |
| **Δ (adding reversal)** | **−0.57** | — | — | — | **−0.84** |

**Adding the reversal sleeve HURTS** — combo Sharpe drops from +0.82 to +0.25 (Δ −0.57; recent Δ −0.84). It cuts vol (5.3% vs 7.9%) only because it is a negative-mean, mildly-anticorrelated drag, not because it adds return. It does NOT add a useful third stream.

---

## KILL-CONDITION CHECK → VERDICT

| Kill | Result | Triggered? |
|---|---|:--:|
| K1 net Sharpe ≤ 0 | net Sharpe = **−1.07** | **YES** |
| K2 \|corr\| > 0.5 to eq or ov | eq −0.28 / ov −0.09 | no |
| K3 dies at 2× cost | 2× Sharpe = **−1.62** | **YES** |
| K4 turnover so high net negative | net CAGR = **−8.27%**, turnover ≈ 937%/yr | **YES** |

# VERDICT: **FAIL** (3 of 4 kills triggered)

Short-term 1-month reversal **does NOT add a third diversifying return stream** to this book. It is **near-uncorrelated (K2 passes)** but **loses money even gross**, has **~937%/yr turnover**, and gets worse at 2× cost. Adding it to the equal-weight combo **lowers Sharpe from +0.82 to +0.25**.

This is the textbook, expected outcome: **ST reversal is a liquidity/microstructure premium that does not survive — indeed is negative even gross — in liquid top-1500 large-caps.** Honest result. **Do not promote. Do not paper-trade. No tuning / no smaller-cap re-hunt** (that would be window-hunting; out of scope for this single pre-registered test, and would carry the small-cap cost penalty already documented elsewhere in Phase 1A).

**Files:** `engine/sleeve3_reversal.py` (runnable) · `outputs/engine/sleeve3_reversal_nav.csv` (gross / net / net_2x / turnover per month).
