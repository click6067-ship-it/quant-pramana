#!/usr/bin/env python3
"""PRAMANA A2 Phase C4 — 분봉 provider interface (Attack scanner ORB/VWAP/RVOL/Bollinger용).
Stage 0: yfinance 5m/15m = PROXY(IEX/지연·full-market VWAP/RVOL 부정확·Codex: QA only).
Stage 1: Polygon Starter($29)/Databento/Alpaca SIP = FULL_MARKET(키 .env 후).
DATA_QUALITY 라벨 필수 — paper signal은 PROXY로 축적, 성과 판정은 FULL_MARKET만. PAPER·자본권한 0."""
import os

class IntradayProvider:
    name = "base"; quality = "UNKNOWN"
    def get_intraday_bars(self, ticker, interval="5m", lookback_days=5): raise NotImplementedError
    def get_quote(self, ticker): raise NotImplementedError

class YFinanceProvider(IntradayProvider):
    """Stage 0 — 무료·PROXY. full-market VWAP/RVOL 부정확(Codex): 파이프라인/축적 QA용만, 성과 증거 불가."""
    name = "yfinance"; quality = "PROXY"
    def get_intraday_bars(self, ticker, interval="5m", lookback_days=5):
        import yfinance as yf
        return yf.download(ticker, period=f"{min(lookback_days,59)}d", interval=interval, progress=False, auto_adjust=False)
    def get_quote(self, ticker):
        import yfinance as yf
        h = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(h["Close"].iloc[-1]) if len(h) else float("nan")

class PolygonProvider(IntradayProvider):
    """Stage 1 — Polygon Starter($29/mo)·SIP full-market. 키=.env POLYGON_KEY(없으면 사용 금지)."""
    name = "polygon"; quality = "FULL_MARKET"
    def __init__(self): self.key = os.environ.get("POLYGON_KEY")
    def get_intraday_bars(self, ticker, interval="5m", lookback_days=5):
        if not self.key: raise RuntimeError("POLYGON_KEY 없음(.env) — 키 발급 후 활성")
        raise NotImplementedError("Polygon REST aggregates는 키 발급 후 구현(현재 stub)")
    def get_quote(self, ticker):
        if not self.key: raise RuntimeError("POLYGON_KEY 없음")
        raise NotImplementedError("stub")

class AlpacaProvider(IntradayProvider):
    """Stage 1 — Alpaca. 무료=IEX(SIP의 ~2%·VWAP/RVOL 부정확·Codex STOP)→paper execution 연결용만. SIP=Algo Trader Plus($99)."""
    name = "alpaca"; quality = "IEX_or_SIP"
    def __init__(self): self.key = os.environ.get("ALPACA_KEY"); self.secret = os.environ.get("ALPACA_SECRET")
    def get_intraday_bars(self, ticker, interval="5m", lookback_days=5):
        if not (self.key and self.secret): raise RuntimeError("ALPACA_KEY/SECRET 없음(.env)")
        raise NotImplementedError("alpaca-py는 키 발급 후 구현(현재 stub)")
    def get_quote(self, ticker): raise NotImplementedError("stub")

def get_provider(name="yfinance"):
    """기본 yfinance(PROXY). 키 생기면 polygon/alpaca. 반환 객체의 .quality로 DATA_QUALITY 라벨."""
    return {"yfinance": YFinanceProvider, "polygon": PolygonProvider, "alpaca": AlpacaProvider}.get(name, YFinanceProvider)()
