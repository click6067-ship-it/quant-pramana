#!/usr/bin/env python3
"""
B0 — Data-only Benchmark Sanity (Phase 1A, MINIMAL)
=====================================================
목적: "깨끗한(survivorship-aware, PIT-safe) 데이터로 self-built cap-weight total-return
벤치마크를 재구성할 수 있는가?" — 이것만 본다.

B0는 alpha 실험이 아니다. 수익 예측이 아니다. 종목 추천이 아니다.
B0의 성공 = 높은 수익이 아니라 "데이터/벤치 파이프라인이 정직하게 작동함".

두 모드
-------
  --source free      : yfinance. EQUAL-WEIGHT TR index. **survivorship-biased** (상장폐지 종목 없음),
                       historical market cap 없음 → CAP-WEIGHT 불가. 기계 smoke test 전용.
                       **이 모드 숫자는 절대 신뢰 금지.** 키 없이 오늘 당장 파이프라인이 도는지만 확인.
  --source sharadar  : Sharadar(Nasdaq Data Link). CAP-WEIGHT TR + 상장폐지 포함 = 진짜 B0.
                       환경변수 NASDAQ_DATA_LINK_API_KEY 필요.

사용 예
-------
  pip install -r requirements.txt

  # (A) 무료 dry-run — 키 불필요, 오늘 가능:
  python b0_benchmark_sanity.py --source free \
      --tickers AAPL,MSFT,JPM,XOM,KO,PG,JNJ,WMT,GE,T --start 2015-01-01

  # (B) Sharadar 스키마 capture — 키 필요(실제 컬럼을 라이브로 출력):
  export NASDAQ_DATA_LINK_API_KEY=YOUR_KEY
  python b0_benchmark_sanity.py --source sharadar --inspect-schema

  # (C) Sharadar 진짜 B0 — 키 필요:
  python b0_benchmark_sanity.py --source sharadar \
      --tickers AAPL,MSFT,JPM,XOM,KO,PG,JNJ,WMT,GE,T --start 2015-01-01

핵심 체크(6개) — 14게이트 전체가 아니라, 막히는 것만 나중에 추가한다:
  CHK-W   weights sum ≈ 1 at every rebalance
  CHK-S   survivorship: 상장폐지 종목이 (있다면) 폐지 전까지 보유됨 (sharadar only)
  CHK-F   no-future: 상장(첫 거래일) 전에는 절대 편입 안 됨
  CHK-TR  total-return: TR index ≥ price-return index (배당이 더해짐)
  CHK-R   reproducibility: 입력 data_hash + 출력 series_hash 기록
  CHK-D   drift(diagnostic): SPY 대비 상관/연환산차 — 자동 실패 아님, 설명용
"""
import argparse, os, sys, json, hashlib, datetime as dt

def die(msg):
    print(f"[FATAL] {msg}", file=sys.stderr); sys.exit(2)

try:
    import numpy as np
    import pandas as pd
except ImportError:
    die("pandas/numpy 필요. `pip install -r requirements.txt` 먼저.")

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP_DIR = os.path.join(HERE, "outputs", "snapshots")


# ---------------------------------------------------------------------------
# Snapshot freeze/thaw — 라이브 데이터를 한 번 받아 동결(byte-stable)해야 재현 가능.
# (이 프로젝트가 설계에 박아둔 data_snapshot + data_hash 게이트의 실제 구현.)
# ---------------------------------------------------------------------------
def _snap_key(source, tickers, start, end):
    raw = f"{source}|{','.join(sorted(tickers))}|{start}|{end}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def _df_to_csv(df, path):
    if df is not None:
        df.to_csv(path)

def freeze_or_thaw(loader, source, tickers, start, end, refresh=False):
    """스냅샷 없으면 다운로드→동결, 있으면 동결본 로드. 항상 동결본(CSV)에서 다시 읽어
    1차/2차 실행이 byte-identical 데이터를 쓰게 만든다 → 재현성 보장."""
    sdir = os.path.join(SNAP_DIR, f"{source}_{_snap_key(source, tickers, start, end)}")
    keys = ["px_tr", "px_unadj", "divs", "mktcap", "spy", "meta"]
    fresh = (not os.path.isdir(sdir)) or refresh
    if fresh:
        data = loader()                       # 라이브 다운로드
        os.makedirs(sdir, exist_ok=True)
        for k in keys:
            v = data.get(k)
            if v is None:
                continue
            _df_to_csv(v if isinstance(v, (pd.DataFrame, pd.Series)) else pd.DataFrame(v),
                       os.path.join(sdir, f"{k}.csv"))
        note = data.get("note", "")
    else:
        note = "(frozen snapshot 재사용)"
    # 항상 동결본에서 다시 읽음
    def _read(name, is_series=False):
        p = os.path.join(sdir, f"{name}.csv")
        if not os.path.exists(p):
            return None
        if name == "meta":
            return pd.read_csv(p)
        df = pd.read_csv(p, index_col=0, parse_dates=True)
        return df.iloc[:, 0] if is_series else df
    out = {"px_tr": _read("px_tr"), "px_unadj": _read("px_unadj"), "divs": _read("divs"),
           "mktcap": _read("mktcap"), "spy": _read("spy", is_series=True), "meta": _read("meta"),
           "note": note, "snapshot_dir": sdir, "frozen": (not fresh)}
    # data_hash = 동결 파일 바이트 해시 (byte-stable → 재현 가능)
    h = hashlib.sha256()
    for k in keys:
        p = os.path.join(sdir, f"{k}.csv")
        if os.path.exists(p):
            with open(p, "rb") as f:
                h.update(f.read())
    out["data_hash"] = h.hexdigest()[:16]
    return out


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------
def load_free(tickers, start, end):
    """yfinance: adjusted close(=split+dividend 조정, TR 근사). survivorship-biased."""
    try:
        import yfinance as yf
    except ImportError:
        die("yfinance 필요. `pip install yfinance`.")
    syms = tickers + ["SPY"]
    raw = yf.download(syms, start=start, end=end, auto_adjust=True, progress=False)
    # auto_adjust=True → 'Close'가 split+dividend 조정가 = total-return 가격
    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    close = close.dropna(how="all")
    spy = close["SPY"].dropna() if "SPY" in close else None
    px = close[[c for c in tickers if c in close.columns]].copy()
    # market cap 없음 → None (cap-weight 불가, equal-weight로 폴백)
    return {"px_tr": px, "mktcap": None, "spy": spy, "meta": None,
            "note": "FREE mode: EQUAL-WEIGHT, survivorship-biased, NUMBERS NOT TRUSTWORTHY"}


def load_sharadar(tickers, start, end, inspect=False):
    """Sharadar: SEP.closeadj(=TR price), DAILY.marketcap(=cap weight), TICKERS(meta)."""
    try:
        import nasdaqdatalink as ndl
    except ImportError:
        die("nasdaq-data-link 필요. `pip install Nasdaq-Data-Link`.")
    key = os.environ.get("NASDAQ_DATA_LINK_API_KEY")
    if not key:
        keyfile = os.path.join(HERE, ".ndl_key")   # 채팅에 키 노출 안 하려고 파일에서 읽음(.gitignore됨)
        if os.path.exists(keyfile):
            key = open(keyfile).read().strip()
    if not key:
        die("키 없음: 환경변수 NASDAQ_DATA_LINK_API_KEY 또는 phase1a/.ndl_key 파일에 키를 넣어.")
    ndl.ApiConfig.api_key = key

    if inspect:
        # === 진짜 schema capture: 라이브 API가 돌려주는 실제 컬럼을 찍는다 ===
        for tbl, kw in [("SHARADAR/SEP", dict(ticker="AAPL")),
                        ("SHARADAR/DAILY", dict(ticker="AAPL")),
                        ("SHARADAR/TICKERS", dict(ticker="AAPL")),
                        ("SHARADAR/ACTIONS", dict(ticker="AAPL"))]:
            try:
                df = ndl.get_table(tbl, paginate=True, **kw)
                print(f"\n## {tbl} columns:\n  {list(df.columns)}")
                print(df.head(3).to_string())
            except Exception as e:
                print(f"\n## {tbl}: ERROR {e}")
        sys.exit(0)

    # 메타: 상장/폐지일·delisting flag (survivorship/no-future 판정에 필요)
    meta = ndl.get_table("SHARADAR/TICKERS", ticker=tickers, paginate=True)
    # TICKERS는 티커당 여러 행(table=SF1/SEP...). SEP 행 우선, 티커별 1행으로 정리.
    if "table" in meta.columns and (meta["table"] == "SEP").any():
        meta = meta[meta["table"] == "SEP"]
    meta = meta.drop_duplicates(subset="ticker", keep="first")
    # SEP: 조정종가(closeadj=TR) + 미조정(closeunadj)
    sep = ndl.get_table("SHARADAR/SEP", ticker=tickers,
                        date={"gte": start, "lte": end or "2100-01-01"}, paginate=True)
    sep["date"] = pd.to_datetime(sep["date"])
    px_tr = sep.pivot_table(index="date", columns="ticker", values="closeadj")    # TR(split+div 조정)
    px_unadj = sep.pivot_table(index="date", columns="ticker", values="closeunadj")  # as-traded
    # ACTIONS: 배당(per-share) → 배당수익률로 PR 도출에 사용. SEP엔 배당 컬럼이 없음.
    try:
        act = ndl.get_table("SHARADAR/ACTIONS", ticker=tickers,
                            date={"gte": start, "lte": end or "2100-01-01"}, paginate=True)
        act = act[act["action"].astype(str).str.contains("div", case=False, na=False)]
        act["date"] = pd.to_datetime(act["date"])
        divs = act.pivot_table(index="date", columns="ticker", values="value", aggfunc="sum")
    except Exception:
        divs = None
    # DAILY: 일별 marketcap (cap weight 입력)
    daily = ndl.get_table("SHARADAR/DAILY", ticker=tickers,
                          date={"gte": start, "lte": end or "2100-01-01"}, paginate=True)
    daily["date"] = pd.to_datetime(daily["date"])
    mktcap = daily.pivot_table(index="date", columns="ticker", values="marketcap")
    # SPY 외부 comparator: SPY는 ETF라 SFP(Fund Prices)에 있음. SFP→SEP 순으로 시도.
    spy = None
    for tbl in ("SHARADAR/SFP", "SHARADAR/SEP"):
        try:
            spyd = ndl.get_table(tbl, ticker="SPY",
                                 date={"gte": start, "lte": end or "2100-01-01"}, paginate=True)
            if len(spyd):
                spyd["date"] = pd.to_datetime(spyd["date"])
                spy = spyd.set_index("date")["closeadj"].sort_index()
                break
        except Exception:
            continue
    return {"px_tr": px_tr.sort_index(), "px_unadj": px_unadj.sort_index(),
            "divs": (divs.sort_index() if divs is not None else None),
            "mktcap": mktcap.sort_index(), "spy": spy, "meta": meta,
            "note": "SHARADAR mode: cap-weight TR, survivorship-aware (delisted retained)"}


# ---------------------------------------------------------------------------
# Benchmark reconstruction: 월말 리밸런스, 보유기간 TR
# ---------------------------------------------------------------------------
def build_index(px_tr, mktcap, start_value=100.0):
    """월말 as-of 가중 → 다음 달 보유. mktcap 있으면 cap-weight, 없으면 equal-weight."""
    px_tr = px_tr.sort_index()
    rets = px_tr.pct_change()                       # 일별 TR (조정가 기준)
    rebal_dates = px_tr.resample("ME").last().index # 월말
    weights_log = {}
    idx = pd.Series(index=px_tr.index, dtype=float)
    idx.iloc[0] = start_value
    cur_w = None
    for i in range(1, len(px_tr)):
        d = px_tr.index[i]
        # 직전 월말에 가중치 재설정
        prev_month_end = px_tr.index[i-1]
        if (cur_w is None) or (px_tr.index[i-1] in rebal_dates):
            asof = px_tr.index[i-1]
            live = px_tr.loc[asof].dropna().index     # 그날 가격 있는 종목 = 그날 살아있는 종목(survivorship-aware)
            if mktcap is not None and asof in mktcap.index:
                w = mktcap.loc[asof, live].reindex(live).fillna(0.0)
            else:
                w = pd.Series(1.0, index=live)         # equal-weight 폴백
            w = w[w > 0]
            if w.sum() > 0:
                cur_w = (w / w.sum())
                weights_log[asof] = cur_w
        # 당일 수익 = 보유 종목 가중 평균(그날 수익 없는 종목=폐지/결측은 제외, 직전까지 반영됨)
        r = rets.loc[d, cur_w.index].fillna(0.0)
        idx.iloc[i] = idx.iloc[i-1] * (1.0 + float((cur_w * r).sum()))
    return idx.dropna(), weights_log


def index_from_weights(rets, weights_log, ref_index, start_value=100.0):
    """build_index와 *동일한* weights_log로 임의 returns 행렬을 재구성(like-for-like 비교용)."""
    rets = rets.reindex(ref_index)
    idx = pd.Series(index=ref_index, dtype=float); idx.iloc[0] = start_value
    asofs = sorted(weights_log.keys()); cur = None; ai = 0
    for i in range(1, len(ref_index)):
        d_prev = ref_index[i - 1]
        while ai < len(asofs) and asofs[ai] <= d_prev:
            cur = weights_log[asofs[ai]]; ai += 1
        if cur is None:
            idx.iloc[i] = idx.iloc[i - 1]; continue
        r = rets.loc[ref_index[i], cur.index].fillna(0.0)
        idx.iloc[i] = idx.iloc[i - 1] * (1 + float((cur * r).sum()))
    return idx.dropna()


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def run_checks(data, idx, weights_log):
    res = []
    def add(cid, name, status, detail): res.append((cid, name, status, detail))

    # CHK-W weights sum ≈ 1
    bad = [str(d.date()) for d, w in weights_log.items() if abs(w.sum() - 1.0) > 1e-6]
    add("CHK-W", "weights sum≈1", "PASS" if not bad else "FAIL",
        f"{len(weights_log)} rebalances, {len(bad)} bad")

    # CHK-S survivorship (sharadar only)
    meta = data.get("meta")
    if meta is not None and "ticker" in getattr(meta, "columns", []):
        meta = meta.drop_duplicates(subset="ticker", keep="first")  # 방어적 dedup
    if meta is not None and "isdelisted" in getattr(meta, "columns", []):
        n_del = int((meta["isdelisted"].astype(str).str.upper() == "Y").sum())
        add("CHK-S", "survivorship (delisted retained)",
            "PASS" if n_del > 0 else "WARN",
            f"{n_del} delisted names in universe meta "
            f"({'있음→survivorship-aware' if n_del>0 else '없음: 표본에 폐지종목 0 — 더 넓은 유니버스 필요'})")
    else:
        add("CHK-S", "survivorship", "N/A", "free mode = survivorship-biased (delisted 없음)")

    # CHK-F no-future (sharadar: firstpricedate 이전 편입 금지)
    if meta is not None and "firstpricedate" in getattr(meta, "columns", []):
        fp = pd.to_datetime(meta.set_index("ticker")["firstpricedate"], errors="coerce")
        fp = fp[~fp.index.duplicated(keep="first")]   # 유니크 인덱스 보장(스칼라 조회)
        viol = 0
        for asof, w in weights_log.items():
            for t in w.index:
                v = fp.get(t)
                if v is not None and pd.notna(v) and asof < v:
                    viol += 1
        add("CHK-F", "no-future (편입≥상장일)", "PASS" if viol == 0 else "FAIL", f"{viol} violations")
    else:
        add("CHK-F", "no-future", "N/A", "free mode: 첫 가격일=데이터 시작, 근사만")

    # CHK-TR  TR ≥ PR — *같은 가중*으로 비교(가짜경보 제거). PR = TR수익 − 배당수익률.
    px_unadj = data.get("px_unadj"); divs = data.get("divs")
    if px_unadj is not None and divs is not None and len(weights_log) > 0:
        px_tr = data["px_tr"]
        tr_rets = px_tr.pct_change()
        # 배당수익률: 배당(per-share) / 직전 as-traded 종가, 비-ex일은 0
        dy = (divs.reindex(index=px_tr.index, columns=px_tr.columns)
                  .div(px_unadj.shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0.0))
        pr_rets = tr_rets - dy                     # 배당 제외 = price return (분할은 closeadj가 처리)
        idx_pr = index_from_weights(pr_rets, weights_log, idx.index)
        tr_g = idx.iloc[-1] / idx.iloc[0]; pr_g = idx_pr.iloc[-1] / idx_pr.iloc[0]
        add("CHK-TR", "TR≥PR (same weighting)", "PASS" if tr_g >= pr_g - 1e-9 else "FAIL",
            f"TR×{tr_g:.4f} ≥ PR×{pr_g:.4f} (배당기여 {(tr_g-pr_g)*100:+.2f}%p)")
    else:
        add("CHK-TR", "TR≥PR", "N/A", "free 모드: 조정 semantics 불신/배당 미사용 → sharadar에서 검증")

    # CHK-D drift vs SPY (diagnostic)
    spy = data.get("spy")
    if spy is not None and len(spy) > 10:
        j = pd.concat([idx.pct_change(), spy.pct_change()], axis=1, join="inner").dropna()
        j.columns = ["bm", "spy"]
        corr = j["bm"].corr(j["spy"])
        ann = (j["bm"].mean() - j["spy"].mean()) * 252
        add("CHK-D", "drift vs SPY (diagnostic)", "INFO",
            f"corr={corr:.3f}, 연환산차={ann*100:+.2f}%p (설명용, 자동실패 아님)")
    else:
        add("CHK-D", "drift vs SPY", "N/A", "SPY 미확보")
    return res


# ---------------------------------------------------------------------------
def sha(obj):
    return hashlib.sha256(str(obj).encode()).hexdigest()[:16]

def main():
    ap = argparse.ArgumentParser(description="B0 data-only benchmark sanity (minimal)")
    ap.add_argument("--source", choices=["free", "sharadar"], required=True)
    ap.add_argument("--tickers", default="AAPL,MSFT,JPM,XOM,KO,PG,JNJ,WMT,GE,T")
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--inspect-schema", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="스냅샷 무시하고 새로 다운로드(동결 갱신)")
    a = ap.parse_args()
    tickers = [t.strip().upper() for t in a.tickers.split(",") if t.strip()]

    if a.inspect_schema:
        if a.source != "sharadar":
            die("--inspect-schema는 sharadar 모드 전용")
        load_sharadar(tickers, a.start, a.end, inspect=True)   # 출력 후 종료

    loader = ((lambda: load_sharadar(tickers, a.start, a.end)) if a.source == "sharadar"
              else (lambda: load_free(tickers, a.start, a.end)))
    data = freeze_or_thaw(loader, a.source, tickers, a.start, a.end, refresh=a.refresh)
    data_hash = data["data_hash"]

    print("=" * 70)
    print("B0 — Data-only Benchmark Sanity")
    print(f"source={a.source} | tickers={len(tickers)} | start={a.start}"
          f" | snapshot={'재사용(frozen)' if data['frozen'] else '신규동결'}")
    print(f"NOTE: {data['note']}")
    print("=" * 70)

    px_tr = data["px_tr"].dropna(how="all")
    if px_tr.shape[0] < 30:
        die(f"가격 데이터 부족({px_tr.shape}). 티커/기간 확인.")

    idx, wlog = build_index(px_tr, data["mktcap"])
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    series_path = os.path.join(out_dir, f"b0_benchmark_{a.source}.csv")
    idx.to_csv(series_path, header=["benchmark_index"])
    series_hash = sha(idx.round(8).to_json())

    ann = (idx.iloc[-1] / idx.iloc[0]) ** (252 / len(idx)) - 1
    print(f"\n기간: {idx.index[0].date()} ~ {idx.index[-1].date()}  ({len(idx)} days)")
    print(f"index: {idx.iloc[0]:.1f} → {idx.iloc[-1]:.1f}  (연환산 {ann*100:+.1f}%, *신뢰판단 금지*)")
    print(f"weight scheme: {'CAP-weight' if data['mktcap'] is not None else 'EQUAL-weight(폴백)'}")
    print(f"data_hash={data_hash}  series_hash={series_hash}")

    print("\n--- CHECKS ---")
    checks = run_checks(data, idx, wlog)
    # CHK-R reproducibility (스냅샷 동결 기반)
    repro = "PASS" if data["frozen"] else "FROZEN"
    repro_detail = ("동결본 재사용 → data_hash 재현됨" if data["frozen"]
                    else f"1차 동결 완료(다음 실행부터 재현) snapshot={os.path.basename(data['snapshot_dir'])}")
    checks.append(("CHK-R", "reproducibility (snapshot)", repro, f"{repro_detail} | data_hash={data_hash}"))
    for cid, name, status, detail in checks:
        print(f"  [{status:4}] {cid:7} {name:32} | {detail}")

    # 최소 registry (5필드 + 체크요약) — 60필드 관료제 아님
    reg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registry")
    os.makedirs(reg_dir, exist_ok=True)
    reg_path = os.path.join(reg_dir, "b0_runs.csv")
    row = {
        "run_id": f"B0-{a.source}-{dt.datetime.now():%Y%m%d-%H%M%S}",
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "source": a.source, "tickers": ";".join(tickers), "start": a.start,
        "data_hash": data_hash, "series_hash": series_hash,
        "checks": ";".join(f"{c}:{s}" for c, _, s, _ in checks),
    }
    hdr = not os.path.exists(reg_path)
    pd.DataFrame([row]).to_csv(reg_path, mode="a", header=hdr, index=False)

    crit_fail = [c for c, _, s, _ in checks if s == "FAIL"]
    verdict = "FAIL" if crit_fail else "PASS(machinery)"
    print(f"\nB0 verdict: {verdict}"
          + (f"  (failed: {crit_fail})" if crit_fail else "")
          + ("\n  ⚠️ free 모드 = survivorship-biased. 숫자/통과를 '진짜 B0 통과'로 신뢰하지 말 것."
             if a.source == "free" else ""))
    print(f"  series → {series_path}\n  registry → {reg_path}")

if __name__ == "__main__":
    main()
