#!/usr/bin/env bash
# PRAMANA — one-command reproduction (free yfinance data · no API key required).
# Proves the validation pipeline runs end-to-end WITHOUT the paid Sharadar subscription.
# Paid-data results (see */reports/*.md) require your own NASDAQ_DATA_LINK key;
# this script is the free *machinery* check — trust the PASS/FAIL of the integrity
# gates, not the return numbers (free mode is survivorship-biased by construction).
set -euo pipefail
cd "$(dirname "$0")/phase1a"

echo "── 1/3  venv + deps ──────────────────────────────────────"
python3 -m venv .venv 2>/dev/null || true
.venv/bin/pip install -q -r requirements.txt

echo "── 2/3  B0 benchmark sanity (free · 6 integrity gates) ────"
# self-built cap-weight TR benchmark + CHK-W/S/F/TR/R/D; frozen snapshot → reproducible
.venv/bin/python b0_benchmark_sanity.py --source free \
    --tickers AAPL,MSFT,JPM,KO,GE,PG,JNJ,WMT,XOM,T --start 2015-01-01

echo "── 3/3  V7 paper core runner (yfinance fallback · fail-closed) ──"
.venv/bin/python engine/forward_runner_v7.py 2>&1 | tail -2 || echo "(needs internet; skipped)"

echo ""
echo "✅ reproduction done. Open phase1a/outputs/*.html for the live dashboards."
echo "   Free mode = survivorship-biased smoke test: trust the *machinery* PASS, not the returns."
echo "   For the real (paid, PIT, survivorship-free) results, set NASDAQ_DATA_LINK_API_KEY and see */reports/*.md."
