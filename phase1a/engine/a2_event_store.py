#!/usr/bin/env python3
"""PRAMANA A2 — Event Store (EDGAR 공시 PIT·catalyst/NEG·blind backtest용).

설계 정본: pramana_a2_delta_patch_pack/02_ATTACK_MOONSHOT_BLIND_BACKTEST.md §3·§6.2.
EDGAR submissions API = 공시 acceptanceDateTime(PIT) → available_at 정확. data.sec.gov 무료·10req/s.

available_at 규율(02 §3):
  - acceptance가 장중(09:30~16:00 ET)·장마감 후 → 그 이후 첫 사용가능 bar.
  - 단순화(daily backtest): acceptance(ET) >= 16:00 또는 비거래일 → 다음 거래일, else 당일. → blind backtest는 available_at 다음 bar 진입.

catalyst(POS) vs NEG 분류 (form + 8-K item code):
  POS  = 8-K 2.02(실적)·1.01(중요계약)·7.01(RegFD)·8.01(기타호재)·1.02 / 425·DEFM14A(M&A)
  NEG  = 8-K 1.03(파산)·4.02(재무제표 non-reliance=회계문제)·3.01(상폐통지)·3.02(희석발행) / S-3·424B(증자/shelf)·reverse split
EDGAR 전종목 10년 크롤 = rate-limit상 비현실 → 표본(leadership+attack 빈출 종목) 실측 + zacks earnings(캐시) 광역 catalyst proxy.
커버리지는 정직 라벨. PAPER·자본권한 0.
"""
import os, sys, json, time, hashlib, datetime as dt
import urllib.request, urllib.error
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_data

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "outputs", "a2_events"); CACHE = os.path.join(OUTDIR, "edgar_cache")
os.makedirs(CACHE, exist_ok=True)
STORE = os.path.join(OUTDIR, "event_store.csv")
UA = "PRAMANA academic research (paper, zero-capital) contact: research@pramana.local"

POS_ITEMS = {"2.02", "1.01", "7.01", "8.01", "1.02"}
NEG_ITEMS = {"1.03", "4.02", "3.01", "3.02"}
NEG_FORMS = {"S-3", "S-3/A", "424B5", "424B3", "424B4", "424B2"}
POS_FORMS = {"425", "DEFM14A", "SC TO-T", "SC 14D9"}


def _label(form, items):
    its = set(str(items).replace(" ", "").split(",")) if items else set()
    if form.startswith("8-K"):
        if its & NEG_ITEMS: return "NEG", sorted(its & NEG_ITEMS)
        if its & POS_ITEMS: return "POS", sorted(its & POS_ITEMS)
        return "NEUTRAL", sorted(its)
    if form in NEG_FORMS: return "NEG", [form]
    if form in POS_FORMS: return "POS", [form]
    return "NEUTRAL", [form]


def fetch_submissions(cik, throttle=0.13, refresh=False):
    """EDGAR submissions JSON (캐시). cik=숫자 문자열. 반환 dict or None(실패)."""
    cik10 = str(int(cik)).zfill(10); cf = os.path.join(CACHE, f"CIK{cik10}.json")
    if os.path.exists(cf) and not refresh:
        try: return json.load(open(cf))
        except Exception: pass
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    try:
        import gzip, io
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            d = json.loads(raw)
        json.dump(d, open(cf, "w"))
        time.sleep(throttle)
        return d
    except Exception as e:
        time.sleep(throttle)
        return None


def _avail_date(accept_iso):
    """acceptanceDateTime → available 거래일(date).
    ★ Codex fix: EDGAR acceptanceDateTime은 'Z' suffix가 붙어도 실제 **US Eastern wall-clock**이다(legacy 표기).
    pandas가 UTC로 파싱하면 4~5h 시프트로 16:00 경계가 틀어짐 → tz 제거 후 wall-clock을 ET로 취급."""
    try:
        ts = pd.Timestamp(accept_iso)
        if ts.tz is not None:
            ts = ts.tz_localize(None)   # 'Z' 무시·wall-clock = ET로 간주(EDGAR 규약)
    except Exception:
        return None
    d = ts.normalize()
    # 16:00 이후(또는 새벽 접수=전일 장후) → 다음 거래일로 미룸. 주말은 월요일.
    after_close = ts.hour >= 16 or ts.hour < 4
    nd = d + pd.Timedelta(days=1) if after_close else d
    while nd.weekday() >= 5:  # 토/일 → 월
        nd += pd.Timedelta(days=1)
    return nd.normalize()


def events_for_ticker(ticker, cik, forms=("8-K",), max_events=400):
    """한 종목의 EDGAR 이벤트 행 리스트 (02 §6.2 schema)."""
    d = fetch_submissions(cik)
    if not d: return []
    rec = d.get("filings", {}).get("recent", {})
    n = len(rec.get("form", []))
    items_col = rec.get("items", [""] * n); acc = rec.get("accessionNumber", [])
    out = []
    for i in range(n):
        form = rec["form"][i]
        if forms and not any(form.startswith(f) for f in forms) and form not in NEG_FORMS and form not in POS_FORMS:
            continue
        adt = rec.get("acceptanceDateTime", [None] * n)[i]
        if not adt: continue
        avail = _avail_date(adt)
        if avail is None: continue
        lab, codes = _label(form, items_col[i] if i < len(items_col) else "")
        accession = acc[i] if i < len(acc) else ""
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}"
        rawhash = hashlib.sha256(f"{accession}|{form}|{items_col[i] if i<len(items_col) else ''}".encode()).hexdigest()[:16]
        out.append({"ticker": ticker, "event_type": f"{form}:{lab}", "label": lab, "codes": ",".join(codes),
                    "event_time": adt, "available_at": str(avail.date()), "form_type": form,
                    "item_code": items_col[i] if i < len(items_col) else "", "source_url": url,
                    "raw_text_hash": rawhash, "llm_label": "", "source": "edgar"})
        if len(out) >= max_events: break
    return out


def zacks_events():
    """zacks earnings 관찰 → catalyst proxy 이벤트 (obs_date=available_at 근사·추정치 카운트만=약한 proxy)."""
    z = a2_data.zacks_earnings()
    if z.empty: return []
    out = []
    for _, r in z.dropna(subset=["obs_date"]).iterrows():
        out.append({"ticker": r["ticker"], "event_type": "earnings_window:CATALYST", "label": "CATALYST",
                    "codes": "earnings", "event_time": str(r["obs_date"]), "available_at": str(pd.Timestamp(r["obs_date"]).date()),
                    "form_type": "ZACKS_EEH", "item_code": "", "source_url": "zacks_eeh_2018.csv",
                    "raw_text_hash": "", "llm_label": "", "source": "zacks"})
    return out


def neg_tickers_asof(event_df, decision_date, lookback_days=90):
    """decision_date 기준 직전 lookback_days 내 NEG 공시가 있는 종목 set (war_plan/scanner NEG gate용·PIT)."""
    dd = pd.Timestamp(decision_date); lo = dd - pd.Timedelta(days=lookback_days)
    av = pd.to_datetime(event_df["available_at"])
    m = (event_df["label"] == "NEG") & (av <= dd) & (av > lo)
    return set(event_df.loc[m, "ticker"].unique())


def sample_tickers(n=180):
    """EDGAR 실측 표본 = leadership 메가캡 + feature_store strong-candidate 빈출 종목 top-N (catalyst/NEG 실측)."""
    leaders = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "AMD", "NFLX",
               "SMCI", "PLTR", "CRWD", "MRVL", "SNOW", "ARM", "COIN", "MSTR", "MARA", "RIOT"]
    fs = os.path.join(ROOT, "outputs", "a2_features", "feature_store.csv")
    extra = []
    if os.path.exists(fs):
        freq = pd.read_csv(fs, usecols=["ticker"])["ticker"].value_counts()
        extra = [t for t in freq.index.tolist() if t not in leaders][:n]
    return leaders + extra


def main():
    refresh = "--refresh" in sys.argv
    cap = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 180
    meta = a2_data.tickers_meta()
    tks = sample_tickers(cap)
    rows = []; ok = 0; nocik = 0; fail = 0
    print(f"EDGAR 표본 fetch: {len(tks)}종 (leadership + attack 빈출)…")
    for i, t in enumerate(tks):
        if t not in meta.index: nocik += 1; continue
        cik = meta.loc[t, "cik"]
        if cik is None or (isinstance(cik, float) and np.isnan(cik)): nocik += 1; continue
        ev = events_for_ticker(t, cik)
        if ev: ok += 1; rows.extend(ev)
        else: fail += 1
        if (i + 1) % 40 == 0: print(f"  …{i+1}/{len(tks)} (events {len(rows):,})")
    edf = pd.DataFrame(rows)
    zdf = pd.DataFrame(zacks_events())
    allev = pd.concat([edf, zdf], ignore_index=True) if len(zdf) else edf
    allev.to_csv(STORE, index=False)
    np_, nn = (int((edf["label"] == "POS").sum()), int((edf["label"] == "NEG").sum())) if len(edf) else (0, 0)
    print(f"✅ event_store: EDGAR {len(edf):,}건/{ok}종(POS {np_}·NEG {nn}·NEUTRAL {len(edf)-np_-nn if len(edf) else 0}) + "
          f"zacks {len(zdf):,}건 → {STORE}")
    print(f"   coverage: EDGAR 실측 {ok}종(CIK없음 {nocik}·fetch실패 {fail}) · zacks {zdf['ticker'].nunique() if len(zdf) else 0}종 · "
          f"전종목 EDGAR 크롤=rate-limit상 표본(인프라 완비·확장은 시간문제)")
    if len(edf):
        print(f"   EDGAR date range: {pd.to_datetime(edf['event_time']).min().date()}~{pd.to_datetime(edf['event_time']).max().date()}")


if __name__ == "__main__":
    main()
