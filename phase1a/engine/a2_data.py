#!/usr/bin/env python3
"""PRAMANA A2 — shared PIT-safe daily data loader (blind backtest backbone).

모든 A2 backtest 모듈(feature store·event store·blind backtest·TQ-DH·benchmarks)이 import하는 단일 데이터 소스.
캐시 = phase1a/outputs/raw/ (2026-06-10/11 Sharadar bulk pull·HASHES.txt sha256 동결·구독중 완료). API 불필요.

PIT 규율 (이 로더가 강제):
  - 가격: 그날 close는 그날 장마감 후에야 available → decision_time 규율은 backtest 엔진이 적용(여기선 raw 패널 제공).
  - 펀더멘털(SF1): datekey = 공시 가용일 = available_at. datekey<=decision_time만 사용(blind backtest가 강제).
  - OHLC adjust: SEP의 open/high/low는 raw(unadjusted), closeadj만 조정 → factor=closeadj/close로 OHLV 동시 조정(split/배당 일관).
PAPER·자본권한 0. 검증된 알파 아님(이 로더는 데이터만 제공).
"""
import os, functools
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # phase1a/
RAW  = os.path.join(ROOT, "outputs", "raw")

# 캐시 파일 (manifest.json·HASHES.txt 동결)
F_SEP_SP500   = os.path.join(RAW, "SHARADAR_SEP.csv")    # S&P500 ever-member·OHLCV+closeadj (712종·1.6M행)
F_SEP_SMALLMID= os.path.join(RAW, "smallmid_SEP.csv")    # small/mid·closeadj+volume (4504종·7.4M행)
F_SEP_BROAD   = os.path.join(RAW, "broad_SEP.csv")       # top-1500·closeadj only
F_VOL_BROAD   = os.path.join(RAW, "broad_volume.csv")    # top-1500 volume
F_FUNDS       = os.path.join(RAW, "SFP_FUNDS.csv")       # ETF (QQQ/TQQQ/SPY/SQQQ/...)·closeadj+volume
F_SPY         = os.path.join(RAW, "SFP_SPY.csv")         # SPY OHLCV
F_SF1_BROAD   = os.path.join(RAW, "broad_SF1_ext.csv")   # 펀더멘털 PIT (datekey·gp·assets·roe·grossmargin)
F_SF1_SP500   = os.path.join(RAW, "SHARADAR_SF1_ARQ.csv")
F_TICKERS     = os.path.join(RAW, "TICKERS.csv")         # 메타 (isdelisted·CIK·sector·scalemarketcap)
F_DAILY_MCAP  = os.path.join(RAW, "DAILY_all.csv")       # marketcap (5797종·9.3M행)
F_ZACKS_EEH   = os.path.join(RAW, "zacks_eeh_2018.csv")  # earnings estimate 관찰일 (catalyst context)

BENCH_TICKERS = ["QQQ", "TQQQ", "SPY", "SQQQ", "SOXL", "IWM"]


def _exists(p):
    if not os.path.exists(p):
        raise FileNotFoundError(f"A2 캐시 없음: {p} (phase1a/outputs/raw — Sharadar bulk pull 필요)")
    return p


@functools.lru_cache(maxsize=1)
def benchmarks():
    """ETF 벤치마크 wide DataFrame (index=date, cols=ticker, value=closeadj). QQQ/TQQQ/SPY 등."""
    df = pd.read_csv(_exists(F_FUNDS), usecols=["ticker", "date", "closeadj"])
    w = df.pivot_table(index="date", columns="ticker", values="closeadj", aggfunc="last")
    w.index = pd.to_datetime(w.index)
    return w.sort_index()


@functools.lru_cache(maxsize=1)
def bench_volume():
    """ETF 거래량 wide (index=date, cols=ticker)."""
    df = pd.read_csv(_exists(F_FUNDS), usecols=["ticker", "date", "volume"])
    w = df.pivot_table(index="date", columns="ticker", values="volume", aggfunc="last")
    w.index = pd.to_datetime(w.index)
    return w.sort_index()


def _adjust_ohlc(df):
    """SEP raw OHLC를 closeadj 기준으로 조정. factor=closeadj/close (split/배당 일관)."""
    df = df.copy()
    factor = (df["closeadj"] / df["close"]).replace([np.inf, -np.inf], np.nan)
    for c in ("open", "high", "low"):
        if c in df.columns:
            df[c + "_adj"] = df[c] * factor
    df = df.rename(columns={"closeadj": "close_adj"})
    return df


def price_panel(universe="sp500", min_date=None, max_date=None):
    """long-format 가격 패널.
    universe='sp500'  → SHARADAR_SEP: ticker,date,open_adj,high_adj,low_adj,close_adj,volume (OHLCV 완비 → gap=open/prev_close 가능)
    universe='smallmid' → smallmid_SEP: ticker,date,close_adj,volume (OHLC 없음 → gap=close/prev_close 근사·라벨 PROXY)
    반환 컬럼: ticker,date(datetime),close_adj,volume[,open_adj,high_adj,low_adj]
    """
    if universe == "sp500":
        df = pd.read_csv(_exists(F_SEP_SP500),
                         usecols=["ticker", "date", "open", "high", "low", "close", "volume", "closeadj"])
        df = _adjust_ohlc(df)
        df = df[["ticker", "date", "open_adj", "high_adj", "low_adj", "close_adj", "volume"]]
    elif universe == "smallmid":
        df = pd.read_csv(_exists(F_SEP_SMALLMID), usecols=["ticker", "date", "closeadj", "volume"])
        df = df.rename(columns={"closeadj": "close_adj"})
    else:
        raise ValueError(f"unknown universe {universe!r} (sp500|smallmid)")
    df["date"] = pd.to_datetime(df["date"])
    if min_date is not None:
        df = df[df["date"] >= pd.Timestamp(min_date)]
    if max_date is not None:
        df = df[df["date"] <= pd.Timestamp(max_date)]
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


@functools.lru_cache(maxsize=1)
def fundamentals():
    """SF1 펀더멘털 (PIT). datekey = 공시 가용일 = available_at. 컬럼: ticker,datekey,gp,assets,roe,grossmargin,revenue,epsusd.
    blind backtest는 datekey<=decision_time만 사용(가장 최근 1건 forward-fill)."""
    frames = []
    for f in (F_SF1_BROAD, F_SF1_SP500):
        if os.path.exists(f):
            cols = pd.read_csv(f, nrows=0).columns.tolist()
            keep = [c for c in ["ticker", "datekey", "gp", "assets", "roe", "grossmargin", "revenue", "epsusd"] if c in cols]
            frames.append(pd.read_csv(f, usecols=keep))
    if not frames:
        raise FileNotFoundError("SF1 캐시 없음")
    df = pd.concat(frames, ignore_index=True)
    df["datekey"] = pd.to_datetime(df["datekey"])
    df = df.dropna(subset=["datekey"]).sort_values(["ticker", "datekey"])
    return df.drop_duplicates(["ticker", "datekey"]).reset_index(drop=True)


@functools.lru_cache(maxsize=1)
def tickers_meta():
    """TICKERS 메타: ticker→{isdelisted,cik,sector,scalemarketcap,sicsector}. CIK는 secfilings URL에서 추출."""
    df = pd.read_csv(_exists(F_TICKERS),
                     usecols=lambda c: c in ("ticker", "isdelisted", "sector", "sicsector",
                                             "scalemarketcap", "secfilings", "name", "category"))
    df = df.drop_duplicates("ticker", keep="last")
    def _cik(u):
        if isinstance(u, str) and "CIK=" in u:
            try:    return str(int(u.split("CIK=")[1].split("&")[0]))
            except Exception: return None
        return None
    df["cik"] = df["secfilings"].map(_cik)
    return df.set_index("ticker")


@functools.lru_cache(maxsize=1)
def zacks_earnings():
    """zacks earnings 관찰(obs_date·per_end_date·estimate counts). catalyst context = '실적 시즌 근접' 신호.
    obs_date = 추정치 관찰일 = available_at 근사. 실제 EPS surprise 아님(추정치 카운트만)→약한 catalyst proxy."""
    if not os.path.exists(F_ZACKS_EEH):
        return pd.DataFrame(columns=["ticker", "obs_date", "per_end_date"])
    df = pd.read_csv(F_ZACKS_EEH)
    for c in ("obs_date", "per_end_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def pit_fundamental(funds_df, ticker, decision_time, col="gp_over_assets"):
    """decision_time 기준 PIT 펀더멘털 (datekey<=decision_time 최신). col='gp_over_assets'면 gp/assets."""
    sub = funds_df[(funds_df["ticker"] == ticker) & (funds_df["datekey"] <= pd.Timestamp(decision_time))]
    if sub.empty:
        return np.nan
    row = sub.iloc[-1]
    if col == "gp_over_assets":
        return float(row["gp"] / row["assets"]) if row.get("assets") else np.nan
    return float(row.get(col, np.nan))


def summary():
    """sanity 요약 (CLI)."""
    b = benchmarks()
    print(f"benchmarks: {list(b.columns)}  {b.index.min().date()}~{b.index.max().date()}  ({len(b)}일)")
    for u in ("sp500", "smallmid"):
        p = price_panel(u, min_date="2016-01-01")
        print(f"{u:9s}: {p['ticker'].nunique()}종·{len(p):,}행·{p['date'].min().date()}~{p['date'].max().date()}·cols={[c for c in p.columns if c not in ('ticker','date')]}")
    f = fundamentals(); print(f"fundamentals: {f['ticker'].nunique()}종·{len(f):,}행 (datekey PIT)")
    m = tickers_meta(); print(f"tickers_meta: {len(m)}종·CIK 있는 종목 {m['cik'].notna().sum()}")
    z = zacks_earnings(); print(f"zacks_earnings: {len(z):,}행 ({z['ticker'].nunique() if len(z) else 0}종)")


if __name__ == "__main__":
    summary()
