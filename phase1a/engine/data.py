#!/usr/bin/env python3
"""Phase 2 M1 — Research Engine data module.
책임: snapshot 로딩 · 파일 해시 · manifest 생성/검증 *만*. (feature/signal/portfolio/cost 로직 없음.)
규율: API 기본 off. live pull은 명시 플래그(snapshot_tickers)에서만. 숫자 안 바뀜(read-only + byte-hash).
사용: python engine/data.py validate | manifest | snapshot-tickers"""
import os, sys, json, hashlib
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE1A = os.path.dirname(HERE)
RAW = os.path.join(PHASE1A, "outputs", "raw")
HASHES_TXT = os.path.join(RAW, "HASHES.txt")
MANIFEST_JSON = os.path.join(RAW, "manifest.json")
PROVENANCE_JSON = os.path.join(RAW, "provenance.json")     # {file: {generated_at, source}}
ALLOW_PULL = False                      # 기본 off — live API 금지
DATE_COLS = ("date", "datekey", "asof", "calendardate", "reportperiod", "lastupdated")

# ── 핵심: 로딩 ──────────────────────────────────────────────────────────────
def path_of(name):
    """name('broad_SEP' 또는 'broad_SEP.csv') → outputs/raw/<name>.csv 절대경로."""
    fn = name if name.endswith(".csv") else name + ".csv"
    return os.path.join(RAW, fn)

def load(name, usecols=None):
    """raw snapshot을 long-form DataFrame으로 로드(날짜 파싱). pivot/feature 수학 안 함."""
    import pandas as pd
    p = path_of(name)
    if not os.path.exists(p):
        raise FileNotFoundError(f"snapshot 없음: {p}")
    head = pd.read_csv(p, nrows=0).columns
    parse = [c for c in DATE_COLS if c in head and (usecols is None or c in usecols)]
    return pd.read_csv(p, usecols=usecols, parse_dates=parse or None)

def load_tickers(usecols=None):
    """동결된 TICKERS snapshot 로드(ticker 인덱스). API-free — downstream의 live TICKERS 호출 대체."""
    import pandas as pd
    p = path_of("TICKERS")
    if not os.path.exists(p):
        raise FileNotFoundError("TICKERS snapshot 없음 — `python engine/data.py snapshot-tickers` 먼저 실행")
    return pd.read_csv(p, usecols=usecols).drop_duplicates("ticker").set_index("ticker")

# ── 핵심: 해시 ──────────────────────────────────────────────────────────────
def file_sha256(name, _chunk=1 << 20):
    h = hashlib.sha256()
    with open(path_of(name), "rb") as f:
        for blk in iter(lambda: f.read(_chunk), b""):
            h.update(blk)
    return h.hexdigest()

# ── 핵심: manifest ──────────────────────────────────────────────────────────
def _list_raw_csvs():
    return sorted(f for f in os.listdir(RAW) if f.endswith(".csv"))

def _meta(fn):
    """파일 메타(행수·티커수·날짜범위·컬럼) — 최소 컬럼만 읽어 메모리 절약."""
    import pandas as pd
    p = os.path.join(RAW, fn)
    cols = list(pd.read_csv(p, nrows=0).columns)
    m = {"sha256": file_sha256(fn), "size_bytes": os.path.getsize(p), "columns": cols}
    key = "ticker" if "ticker" in cols else (cols[0] if cols else None)
    if key:
        s = pd.read_csv(p, usecols=[key])[key]
        m["rows"] = int(len(s))
        if key == "ticker":
            m["tickers"] = int(s.nunique())
    dcol = next((c for c in DATE_COLS if c in cols), None)
    if dcol:
        d = pd.to_datetime(pd.read_csv(p, usecols=[dcol])[dcol], errors="coerce").dropna()
        if len(d):
            m["date_col"], m["date_min"], m["date_max"] = dcol, str(d.min().date()), str(d.max().date())
    return m

def _provenance():
    return json.load(open(PROVENANCE_JSON)) if os.path.exists(PROVENANCE_JSON) else {}

def build_manifest():
    prov = _provenance()
    files = {}
    for fn in _list_raw_csvs():
        m = _meta(fn)
        if fn in prov:                              # generated_at/source 병합(있으면)
            m.update(prov[fn])
        files[fn] = m
    return {"raw_dir": "outputs/raw", "note": "Phase2 M1 authoritative snapshot manifest (HASHES.txt 상위집합)",
            "files": files}

def write_manifest(path=MANIFEST_JSON):
    man = build_manifest()
    with open(path, "w") as f:
        json.dump(man, f, indent=2, sort_keys=True)
    return man

# ── 핵심: 검증 (기존 HASHES.txt 1:1 대조) ──────────────────────────────────
def _read_hashes_txt():
    out = {}
    if not os.path.exists(HASHES_TXT):
        return out
    with open(HASHES_TXT) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split()
            if len(parts) >= 2:
                out[parts[-1]] = parts[0]      # <sha>  <file>
    return out

def validate():
    """기존 HASHES.txt의 해시를 재계산해 1:1 대조 + 디스크 신규파일 카탈로그."""
    expected = _read_hashes_txt()
    on_disk = set(_list_raw_csvs())
    matched, mismatched, missing_on_disk, new_on_disk = [], [], [], []
    for fn in sorted(on_disk):
        h = file_sha256(fn)
        if fn in expected:
            (matched if expected[fn] == h else mismatched).append(fn)
        else:
            new_on_disk.append(fn)
    for fn in expected:
        if fn not in on_disk:
            missing_on_disk.append(fn)              # HASHES엔 있으나 raw/엔 없음(파생/이동)
    rep = {"matched": matched, "mismatched": mismatched,
           "in_hashes_not_in_raw": missing_on_disk, "new_files_not_in_hashes": new_on_disk}
    print("=" * 74); print("Phase 2 M1 — data.py snapshot 검증 (read-only, API off)"); print("=" * 74)
    print(f"raw/ csv 파일: {len(on_disk)} · HASHES.txt 엔트리: {len(expected)}")
    known_on_disk = sum(1 for fn in on_disk if fn in expected)
    print(f"\n[MATCH] 기존 해시 1:1 일치: {len(matched)}/{known_on_disk} (재계산 동일 = 데이터 무손상)")
    for fn in matched: print(f"  ✅ {fn}")
    if mismatched:
        print(f"\n[MISMATCH] ❌ 해시 불일치(CRITICAL — 데이터 변형): {mismatched}")
    else:
        print("\n[MISMATCH] 없음 — 기존 잠긴 데이터 전부 무손상 ✅")
    if missing_on_disk:
        print(f"\n[HASHES엔 있으나 raw/에 없음] (파생/이동 파일): {missing_on_disk}")
    if new_on_disk:
        print(f"\n[신규 — HASHES 미등록] manifest에 추가됨: {new_on_disk}")
    ok = (not mismatched)
    print("\n" + "=" * 74)
    print(f"판정: {'PASS — 기존 숫자 안 바뀜(해시 무손상)' if ok else 'FAIL — 해시 불일치!'} · 신규 {len(new_on_disk)}개 manifest 편입")
    return rep, ok

# ── 명시 플래그 전용: TICKERS 동결(재현성용 1회 pull) ──────────────────────
def snapshot_tickers(allow_pull=False):
    """live SHARADAR/TICKERS를 outputs/raw/TICKERS.csv로 동결. 명시 플래그 필수."""
    if not (allow_pull or ALLOW_PULL):
        raise PermissionError("snapshot_tickers: live pull은 allow_pull=True(명시 플래그) 필요. (API 기본 off)")
    import pandas as pd, nasdaqdatalink as ndl
    ndl.ApiConfig.api_key = open(os.path.join(PHASE1A, ".ndl_key")).read().strip()
    tk = ndl.get_table("SHARADAR/TICKERS", table="SEP", paginate=True).drop_duplicates("ticker")
    out = os.path.join(RAW, "TICKERS.csv")
    tk.to_csv(out, index=False)
    prov = _provenance()
    prov["TICKERS.csv"] = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           "source": "SHARADAR/TICKERS table=SEP (drop_duplicates ticker)"}
    json.dump(prov, open(PROVENANCE_JSON, "w"), indent=2, sort_keys=True)
    write_manifest()                                # manifest 갱신(TICKERS + generated_at 편입)
    print(f"[snapshot_tickers] {len(tk)} tickers · {len(tk.columns)} cols → {out}")
    print(f"  sha256 {file_sha256('TICKERS')} · columns: {list(tk.columns)}")
    return out

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        rep, ok = validate(); sys.exit(0 if ok else 1)
    elif cmd == "manifest":
        m = write_manifest(); print(f"manifest → {MANIFEST_JSON} ({len(m['files'])} files)")
    elif cmd == "snapshot-tickers":
        snapshot_tickers(allow_pull=True)
    else:
        print(__doc__); sys.exit(2)
