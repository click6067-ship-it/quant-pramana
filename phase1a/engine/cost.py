#!/usr/bin/env python3
"""Phase 2 M4 — Research Engine cost module. 동결 비용 tier + turnover *만*.
규율: 새 비용모델 0 · spread/impact 새 추정 0 · tier 변경 0 · universe/feature/portfolio/evaluate 0 · API 0.
정의 출처(verbatim): b2b5_broad.cost_bps / quality_quarantine.ctier (marketcap 5/10/15bp) · b_smallmid.cost_oneway (ADV 25/45/75bp).
1x/2x/3x stress = 호출측에서 cost term × mult."""
import numpy as np, pandas as pd

BPS = 1e4

def tier_marketcap_bps(mc_series, default=10.0):
    """marketcap tercile one-way bps: 상위33%=5 · 중=10 · 하=15. (b2b5_broad/quality_quarantine 동결)
    입력: 그룹 ticker로 인덱스된 marketcap series(결측 허용; 결측=default). 그룹 내 rank로 tier."""
    s = pd.Series(mc_series)
    m = s.dropna()
    if not len(m):
        return pd.Series(default, index=s.index)
    q = m.rank(pct=True)
    c = pd.Series(15.0, index=m.index); c[q >= 1/3] = 10.0; c[q >= 2/3] = 5.0
    return c.reindex(s.index).fillna(default)

def tier_adv_bps(adv_series):
    """ADV(dollar-volume) tercile one-way bps: 상위33%=25 · 중=45 · 하=75 (보수적). (b_smallmid 동결)
    입력: 그룹 ticker로 인덱스된 ADV series(결측 없음 전제). 그룹 내 rank로 tier."""
    s = pd.Series(adv_series)
    q = s.rank(pct=True)
    c = pd.Series(75.0, index=s.index); c[q >= 1/3] = 45.0; c[q >= 2/3] = 25.0
    return c

def to_fraction(bps):
    return bps / BPS

def turnover_oneway(cur, prev):
    """one-way turnover: |cur △ prev| / (2·max(|cur|,1)). 최초(prev 없음)=1.0. (전 스크립트 동결)"""
    cur, prev = set(cur), set(prev)
    if not prev:
        return 1.0
    return len(cur ^ prev) / (2 * max(len(cur), 1))

# 편의: per-rebal cost term (mult 적용은 호출측에서 — 1x/2x/3x stress)
def longshort_cost(to5, c5_frac, to1, c1_frac, mult=1.0):
    """net Q5-Q1 비용항: (to5·c5 + to1·c1)·mult. (b2b5_broad/quality_quarantine)"""
    return (to5 * c5_frac + to1 * c1_frac) * mult

def longonly_cost(to5, c5_frac, mult=1.0):
    """net long-only 비용항: to5·c5·mult. (b_smallmid)"""
    return to5 * c5_frac * mult

REGISTRY = {
    "broad":     {"tier": "marketcap 5/10/15bp", "fn": "tier_marketcap_bps"},
    "small_mid": {"tier": "ADV 25/45/75bp (보수적)", "fn": "tier_adv_bps"},
    "stress":    "1x/2x/3x (cost term × mult)",
}
