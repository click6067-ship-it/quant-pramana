# V3 — VOL-RISK-PREMIUM (short-vol carry) sleeve + HARD CRASH KILL

**VERDICT: FAIL (loudly).** The crash kill does NOT save it. Worst month **-62.3%** (kill ON), maxDD **-92.3%**. This is paper/sandbox only — **do not paper-trade, do not live-trade, do not add to the book.**

`engine/sleeve_vrp.py` · output `outputs/engine/sleeve_vrp_nav.csv` · ⚠️ paper (가상)·single backtest·no live.

---

## Pre-registered kills (locked BEFORE results)

| # | Kill condition | Result | Hit? |
|---|---|---|---|
| 1 | net Sharpe ≤ 0 → FAIL | net Sharpe **+0.28** | no |
| 2 | **single worst month < -25%** (tail not controlled by crash kill) → FAIL (ruin) | worst month **-62.3%** | **YES → FAIL** |
| 3 | dies at 2x cost (net Sharpe ≤ 0) → FAIL | 2x Sharpe +0.23 | no |
| 4 | max drawdown < -40% → FAIL | maxDD **-92.3%** | **YES → FAIL** |

**Two independent ruin-risk kills tripped (worst-month and maxDD).** The deliverable was crash protection; the crash protection failed. Verdict is unambiguous FAIL.

---

## ONE definition (no tuning, pre-registered)

- **Position:** SHORT UVXY (1.5x VIX short-term futures ETF). Daily position return = **-1 × UVXY closeadj daily return**. Monthly mark, compounded from **daily** returns (the kill and the tail are daily-resolution phenomena — monthly-only would hide the blowups). UVXY chosen as primary because it covers the full window incl. Feb-2018; VXX (starts 2018-01) run as a secondary robustness check.
- **HARD CRASH KILL** (mandatory, deterministic, 3-trigger **OR**, evaluated at close → applied **next bar**): FLAT the short if ANY of:
  1. SPY 20d realized vol ≥ **25%/yr**, OR
  2. SPY < 50d MA **OR** SPY < 200d MA (trend break), OR
  3. VIX-proxy spike: UVXY 1-day return ≥ **+20%** (vol spiking — the in-data VIX-short-term proxy).
- **Next-bar execution:** signal at close(t) → position effective (t+1). `position[t] = target.shift(1)`. **Look-ahead = 0** (verified, see integrity checks).
- **Cost:** ETF tier **5bp** one-way (UVXY ultra-liquid → top tier, frozen `cost` convention) on turnover (|Δposition|) + **borrow 5%/yr** for shorting UVXY (modest because UVXY is liquid/easy-to-borrow, but real and accrued daily on the short notional). Stressed at 2×.

Window: **2016-01-05 → 2026-06-10, 2623 trading days, 126 months.** Crash kill is ON 31.2% of days → short exposure only 68.8% of days.

---

## Results (UVXY short-vol carry, monthly returns)

| Variant | Sharpe | CAGR | vol | maxDD | **worst month** | 2021-26 Sh |
|---|---|---|---|---|---|---|
| gross (no cost, kill ON) | +0.33 | -8.56% | 85.6% | -89.7% | -62.1% | +0.26 |
| **net 1x cost, kill ON [PRIMARY]** | **+0.28** | **-12.37%** | **85.2%** | **-92.3%** | **-62.3%** | +0.20 |
| net 2x cost, kill ON (stress) | +0.23 | -16.02% | 84.8% | -94.2% | -62.6% | +0.15 |
| net 1x cost, **kill OFF (naked)** | +0.56 | -7.36% | 104.1% | **-99.0%** | **-87.0%** | +0.50 |

Note the perverse outcome: **the naked (no-kill) version has a HIGHER Sharpe (+0.56) than the kill version (+0.28)** — because the kill, by going flat after spikes, misses the violent mean-reversion *rebounds* that follow vol spikes (the days UVXY collapses -20%/-26%, which a naked short would harvest). The kill cuts the left tail somewhat but at a large carry cost, and **still leaves a -62% month and -92% drawdown.** Neither version is remotely investable; both fail catastrophically.

### Worst months (kill ON net) — tail check (FAIL if < -25%)

| Month | Net return |
|---|---|
| 2016-06 (Brexit) | **-62.3%** |
| 2017-08 | -52.1% |
| 2021-11 | -49.0% |
| 2020-06 | -46.0% |
| 2024-08 (Aug vol spike) | -41.6% |

Five separate months worse than -40%, even with the crash kill active.

### Annual net returns (kill ON) — 2018 / 2020 highlighted

```
2016: -23.2%   2017: +202.6%   2018: -64.2%   2019:  +6.4%   2020: -42.2%
2021: -42.6%   2022:  -0.8%    2023: +171.1%  2024: -72.3%   2025: +55.7%   2026: -26.4%
```

The blow-out positive years (2017 +203%, 2023 +171%) are exactly the seductive carry that lures people in; they are wiped out by -64%/-72%/-42% years. The path is unsurvivable: ₩100M → **₩0.25억 (-75% over 10y)** net of cost, kill ON.

---

## Crash-kill effectiveness — THE deliverable (Feb-2018 / Mar-2020)

| Window | kill ON | kill OFF (naked) | First kill fire (close) |
|---|---|---|---|
| **Feb-2018 (XIV blowup)** | **-35.4%** | -84.4% | 2018-02-02 |
| **Mar-2020 (COVID)** | **-37.7%** | -94.9% | 2020-02-24 |
| naked worst month | — | **-87.0%** | — |
| kill-ON worst month | **-62.3%** | — | — |

**What the kill DOES do:** it materially cuts the *multi-day* blow-ups. Mar-2020 went from -94.9% (naked) to -37.7% (kill) because the MA50/spike triggers fired on Feb-24, putting the book flat well before the worst of the COVID crash. Feb-2018 went from -84.4% to -35.4%.

**What the kill CANNOT do — and why it fails:** it cannot prevent **single-day gap spikes**, because next-bar execution means the trigger fires at the *close* of the spike day — too late for that day's loss. Three concrete failures (verified daily):

- **Brexit, Jun-24 2016:** Jun-23 was a *calm* pre-vote day (UVXY -19.5%), so NO trigger fired at the Jun-23 close → we were SHORT into Jun-24. Jun-24 (result day) UVXY **+44.1% → -44.2% in one day.** The spike trigger fired at Jun-24 close — after the damage. → -62.3% month.
- **Aug 2017 whipsaw:** UVXY +26.7% Aug-10 (kill fires, flat Aug-11), market calms (kill OFF Aug-14 close), we **re-enter short Aug-15**, then UVXY +33.3% Aug-17 → -33.3% in one day. The kill whipsawed us back in right before the next spike.
- **Feb-5 2018:** the MA50 trigger fired Feb-5 close, so we were flat Feb-6 — but only *after* eating part of the Feb-2 (-27.4%) and being short into the regime. (The spike trigger did fire Feb-2, which is what cut Mar-2020-style multi-day damage, but the one-day hits still compounded the month to -35%.)

Counted across the window: **6 times** the kill went flat and then re-entered the short within 3 days, directly into another ≥+20% UVXY spike. **Daily-signal + next-bar execution is structurally incapable of dodging the one-day vol gap that defines short-vol tail risk.** That is the core, honest reason the deliverable fails.

> Bottom line on the deliverable: naked worst month -87.0% → kill-ON worst month -62.3%. **The kill improves it but does NOT bring it inside the -25% ruin bound. The crash protection does not save the strategy.** ❌

---

## Correlations to the existing book

Common 109 months (2017-05 → 2026-05) vs `outputs/engine/combined_book_nav.csv`:

- corr(VRP, **eq**) = **+0.002** (essentially uncorrelated to the equity MN L/S sleeve — as advertised).
- corr(VRP, **ov**) = **+0.520** (materially correlated to the ETF trend+vol overlay — *not* the clean diversifier the pitch claims; both are short-vol/trend-flavored and crash together).
- (existing corr(eq, ov) = +0.061.)

The +0.52 correlation to `ov` is itself a red flag: the VRP sleeve's "uncorrelated, high-return" pitch is half false — it is correlated with the book's existing risk-on/trend exposure, so it adds tail in the same regimes the book is already exposed to.

---

## Does adding it (small weight) to the combined book help?

2-sleeve base = 0.5·eq + 0.5·ov, cost after, unlevered. Add VRP at small weights:

| Mix | Sharpe | CAGR | vol | maxDD | worst month | 2021-26 Sh |
|---|---|---|---|---|---|---|
| base (eq+ov 50/50) | **+0.82** | +6.38% | 7.9% | -10.4% | -6.0% | +1.11 |
| + VRP 5% | +0.71 | +6.50% | 9.6% | -11.8% | -7.0% | +0.97 |
| + VRP 10% | +0.58 | +6.49% | 12.1% | -15.7% | -8.5% | +0.79 |
| + VRP 20% | +0.42 | +6.07% | 18.1% | -23.8% | -11.5% | +0.57 |

**No.** Even at a 5% weight: CAGR barely moves (+6.38% → +6.50%, ~+0.1pp) while **Sharpe drops +0.82 → +0.71, maxDD worsens -10.4% → -11.8%, worst month -6.0% → -7.0%.** Every increment of VRP **lowers Sharpe and deepens the tail** for negligible return. It does the *opposite* of the goal (return up without exploding tail): it explodes the tail without adding return. Recent-regime Sharpe (2021-26) degrades hardest (+1.11 → +0.97 → +0.79).

---

## Robustness — VXX (2018-01→), same definition

VXX net (1x, kill ON): Sharpe **-0.09**, CAGR -16.3%, maxDD -80.7%, worst month -46.0%. Confirms the failure is not UVXY-specific — the short-vol carry net of its own crash risk is a losing trade on the unleveraged 1× ETN too (and starting after Feb-2018, so it even *skips* the worst event and still loses).

---

## Integrity checks (verified, no bug behind the FAIL)

- **No look-ahead:** `position[t] == target.shift(1)[t]` exactly (max diff < 1e-12). ✅
- **Flat = zero P&L:** when position == 0, gross P&L == 0 exactly. ✅
- **Monthly compounding:** hand-recompute of Aug-2017 (-52.1%) matches report. ✅
- **Naked = pure short:** kill-OFF holds position == 1 every day after day 1. ✅

The -62% month and -92% drawdown are real properties of the strategy, not artifacts.

---

## Verdict & recommendation

**FAIL — and the crash kill does NOT save it.** Both ruin-risk kills (worst month < -25%, maxDD < -40%) tripped by a wide margin. The fundamental, structural reason is honest and unavoidable: **short-vol tail risk is a single-day gap risk (Brexit +44%, Aug-2017 +33%, Feb-2018 +66%), and a daily-close signal with next-bar execution physically cannot exit before that day's loss.** The kill helps multi-day crashes (Mar-2020 -95%→-38%) but leaves the one-day gaps intact, and its whipsaw re-entries (6×) feed the short straight back into the next spike. On top of that, the sleeve is +0.52 correlated to the book's existing `ov` overlay, so it is not even the clean diversifier claimed, and adding any weight lowers Sharpe while deepening drawdown.

- **Do NOT promote, do NOT paper-trade, do NOT add to the combined book.** This is sandbox research output only.
- This is the system working correctly: a pre-registered, deterministic test caught a tail-deadly strategy *before* any capital (even paper) touched it, instead of being seduced by the +203%/+171% carry years.
- If short-vol were ever revisited (it should not be at this sizing), the only structurally sound forms are **defined-risk** (long-put / put-spread collar so the max single-day loss is *capped by contract*, not by a reactive signal) — which is a different instrument and a different project, not this short-ETF sleeve.
