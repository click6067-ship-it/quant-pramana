#!/usr/bin/env python3
"""PRAMANA risk engine — deterministic veto (사이징·한도·4 kill-type·gap추정). 순수 함수, 데이터 의존 0.
원칙: 결정적 규칙이 사이징/veto/kill을 트리거, LLM/AI는 off-path. 공격적이어도 hard cap + 청산로직 명시."""
import numpy as np, pandas as pd

# ── 사이징: vol-target + hard leverage cap + fractional-Kelly guard ──
def target_leverage(trailing_vol, target_vol=0.25, max_lev=4.0, kelly_frac=0.5):
    """fractional-Kelly(0.5) × vol-target, hard cap. trailing_vol=과거 실현변동성(연). 추정오차 큰 풀켈리 회피."""
    if not trailing_vol or trailing_vol <= 0 or np.isnan(trailing_vol):
        return 1.0
    return float(min(max_lev, kelly_frac * target_vol / trailing_vol))

# ── 한도(weights veto): per-name·gross ──
def apply_limits(w, max_name=0.03):
    w = w.clip(upper=max_name)
    return w / w.sum() if w.sum() > 0 else w

# ── 4 kill-type (always-on) → (kill, lev_mult, reason) ──
def kill_check(*, data_ok=True, trailing_dd=0.0, realized_vol=None, target_vol=0.25,
               mkt_beta=0.0, trailing_ret=None, dd_cut=-0.15, vol_mult=2.0, beta_lim=0.4):
    """correlation_breakdown은 *안정적 rolling beta*로 판정(짧은창 corr 노이즈 회피). model_decay는 12m trailing."""
    if not data_ok:
        return ("data_integrity", 0.0, "데이터 무결성 실패 → 즉시 거래중단")          # ① 즉시 halt
    if trailing_dd < dd_cut:
        return ("risk_breach", 0.4, f"DD {trailing_dd:+.1%}<{dd_cut:.0%} → gross 40%+cooldown")  # ② 축소
    if realized_vol is not None and realized_vol > vol_mult * target_vol:
        return ("vol_explosion", 0.5, f"실현변동성 {realized_vol:.0%}>{vol_mult}×target → 50% 축소")  # (②계열)
    if abs(mkt_beta) > beta_lim:
        return ("correlation_breakdown", 0.5, f"시장 beta |{mkt_beta:+.2f}|>{beta_lim} → 시장중립 깨짐, 축소")  # ④
    if trailing_ret is not None and trailing_ret < 0:
        return ("model_decay", 0.6, "trailing 12m 수익 음수 → 신규리스크 60% 동결")    # ③ decay
    return (None, 1.0, "정상")

# ── pre-trade gap/crash 손실 추정 ──
def gap_estimate(beta, leverage, shock=-0.07):
    """시장 -7% gap 시 book 손익 ≈ beta×shock×leverage (시장중립이면 작음)."""
    return float(beta * shock * leverage)

# ── 청산/재진입(명시) ──
def reentry_ok(cooldown_left):
    """kill 후 즉시 재가동 금지: cooldown 동안 de-risk 유지."""
    return cooldown_left <= 0

LIMITS = dict(target_vol=0.25, max_lev=4.0, kelly_frac=0.5, max_name=0.03, dd_cut=-0.15,
              vol_mult=2.0, beta_lim=0.4, cooldown=2)
