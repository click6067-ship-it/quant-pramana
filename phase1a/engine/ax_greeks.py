#!/usr/bin/env python3
"""PRAMANA AX — Black-Scholes price + Greeks (옵션 모델링 + attribution residual 분해용).

scipy 의존 없음(math.erf로 정규 CDF). European call/put. 옵션 *과거 데이터 없음* → BS 모델 = 가정(IV proxy).
attribution(AX0_Protocol §4): P&L = Δ·dS + vega·dIV + theta·dt + 0.5·gamma·dS² + residual.
PAPER·검증된 알파 아님(이 모듈은 가격 모델만).
"""
import math

SQRT2 = math.sqrt(2.0); SQRT2PI = math.sqrt(2.0 * math.pi)
def _N(x): return 0.5 * (1.0 + math.erf(x / SQRT2))          # 표준정규 CDF
def _n(x): return math.exp(-0.5 * x * x) / SQRT2PI            # 표준정규 PDF

def _d1d2(S, K, T, sigma, r=0.04, q=0.0):
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0: return None, None
    v = sigma * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / v
    return d1, d1 - v

def price(S, K, T, sigma, r=0.04, q=0.0, kind="call"):
    """BS 가격. T=잔존(년)·sigma=연율 IV. 만기/IV 0이면 intrinsic."""
    if T <= 0 or sigma <= 0:
        intr = max(0.0, (S - K) if kind == "call" else (K - S)); return intr
    d1, d2 = _d1d2(S, K, T, sigma, r, q)
    if kind == "call":
        return S * math.exp(-q * T) * _N(d1) - K * math.exp(-r * T) * _N(d2)
    return K * math.exp(-r * T) * _N(-d2) - S * math.exp(-q * T) * _N(-d1)

def greeks(S, K, T, sigma, r=0.04, q=0.0, kind="call"):
    """delta·gamma·vega(per 1.0 vol)·theta(per year)·rho. 만기/IV 0이면 0(intrinsic)."""
    if T <= 0 or sigma <= 0:
        d = (1.0 if S > K else 0.0) if kind == "call" else (-1.0 if S < K else 0.0)
        return {"delta": d, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}
    d1, d2 = _d1d2(S, K, T, sigma, r, q); v = sigma * math.sqrt(T)
    disc_q = math.exp(-q * T); disc_r = math.exp(-r * T)
    gamma = disc_q * _n(d1) / (S * v)
    vega = S * disc_q * _n(d1) * math.sqrt(T)                 # per 1.0 vol (1%=vega/100)
    if kind == "call":
        delta = disc_q * _N(d1)
        theta = (-S * disc_q * _n(d1) * sigma / (2 * math.sqrt(T))
                 - r * K * disc_r * _N(d2) + q * S * disc_q * _N(d1))
        rho = K * T * disc_r * _N(d2)
    else:
        delta = -disc_q * _N(-d1)
        theta = (-S * disc_q * _n(d1) * sigma / (2 * math.sqrt(T))
                 + r * K * disc_r * _N(-d2) - q * S * disc_q * _N(-d1))
        rho = -K * T * disc_r * _N(-d2)
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}

def attribute(S0, S1, K, T0, dt_years, iv0, iv1, r=0.04, kind="call"):
    """entry→exit 옵션 P&L을 Greeks로 분해. 반환: total·delta·gamma·vega·theta·residual (per 1 contract·×100 안 함)."""
    p0 = price(S0, K, T0, iv0, r, kind=kind); p1 = price(S1, K, max(1e-6, T0 - dt_years), iv1, r, kind=kind)
    g = greeks(S0, K, T0, iv0, r, kind=kind)
    dS = S1 - S0
    delta_pnl = g["delta"] * dS
    gamma_pnl = 0.5 * g["gamma"] * dS * dS
    vega_pnl = g["vega"] * (iv1 - iv0)
    theta_pnl = g["theta"] * dt_years
    total = p1 - p0
    residual = total - delta_pnl - gamma_pnl - vega_pnl - theta_pnl
    return {"total": total, "entry_px": p0, "exit_px": p1, "delta_pnl": delta_pnl, "gamma_pnl": gamma_pnl,
            "vega_pnl": vega_pnl, "theta_pnl": theta_pnl, "residual": residual}

if __name__ == "__main__":
    # sanity: 5% OTM call·35DTE·IV 40%
    S = 100; K = 105; T = 35 / 365; iv = 0.40
    print("price", round(price(S, K, T, iv), 3), "greeks", {k: round(v, 4) for k, v in greeks(S, K, T, iv).items()})
    a = attribute(100, 108, 105, T, 10 / 365, 0.40, 0.30)   # +8% spot, IV crush 40→30, 10일 경과
    print("attribute(+8% spot·IV 40→30·10d):", {k: round(v, 3) for k, v in a.items()})
