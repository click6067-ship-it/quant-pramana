#!/usr/bin/env python3
"""PRAMANA forward paper runner — 무인 24/7(일 1회) 페이퍼 북. Sharadar 구독 없이 돈다.
- free EOD(yfinance, ~17개 ETF만) → CPU·초단위 (ML/GPU 전혀 불필요).
- sleeve: ETF 200d-SMA 추세 + SPY 20d-vol 디리스킹 + LETF 컨벡스 dose (= 백테스트의 수익엔진).
  · equity 시장중립 sleeve는 유료 펀더멘털(Sharadar SF1) 필요 → forward(무료)에선 일시정지(대시보드 표기).
- look-ahead 없음: 가중치는 종가 t에 결정, 수익은 t+1에 실현(W.shift(1)).
- 가격캐시 append-only(과거값 동결=재현성) · 라이브 트랙 인셉션 기록 · 멱등(하루 중복실행 OK).
사용: python engine/forward_runner.py [--dry](네트워크 없이 캐시만)"""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FWD=os.path.join(ROOT,"outputs","forward"); os.makedirs(FWD,exist_ok=True)
PRICES=os.path.join(FWD,"prices.csv"); LOG=os.path.join(FWD,"forward_log.csv"); STATE=os.path.join(FWD,"state.json")
DASH=os.path.join(ROOT,"outputs","forward_dashboard.html"); CAP=100_000_000
ETFS=["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"]
LETF_MAP={"QQQ":"TQQQ","SPY":"UPRO"}; ALL=ETFS+list(LETF_MAP.values())
TREND_BUDGET,LETF_BUDGET,LEV,VOL_GATE = 0.50,0.04,3.0,0.22

def pull():
    import yfinance as yf
    df=yf.download(ALL,period="400d",interval="1d",auto_adjust=True,progress=False,threads=True)
    df=df["Close"] if isinstance(df.columns,pd.MultiIndex) else df
    return df.dropna(how="all")

def main():
    dry="--dry" in sys.argv
    hist=pd.read_csv(PRICES,index_col=0,parse_dates=True) if os.path.exists(PRICES) else None
    if dry:
        if hist is None: print("no cache for --dry"); return
        px=hist
    else:
        new=pull()
        # append-only: 기존 날짜값 동결, 새 날짜만 추가 → NAV 재현성
        px = new if hist is None else pd.concat([hist,new[~new.index.isin(hist.index)]]).sort_index()
        px=px[~px.index.duplicated(keep="last")]; px.to_csv(PRICES)
    avail=[c for c in ETFS if c in px.columns]
    # ── 무결성 invariants (Codex red-team #3: 조용한 오염 차단 · fail-closed) ──
    # "무인 페이퍼는 멀쩡해 보이면서 틀릴 수 있다 → 깨끗한 대시보드 + 오염된 기록." 치명 invariant면 업데이트 안 함.
    health=[]; fatal=False; latest=px.index[-1]
    age=(pd.Timestamp(dt.date.today())-latest).days if not dry else 0
    if age>5: health.append(f"STALE feed {age}d"); fatal=True
    if len(avail)<12: health.append(f"ETF {len(avail)}/15"); fatal=True
    nanr=float(px[avail].iloc[-1].isna().mean())
    if nanr>0.2: health.append(f"NaN {nanr:.0%}"); fatal=True
    if not px.index.is_monotonic_increasing: health.append("dates non-monotonic"); fatal=True
    bad=int((px[avail].pct_change().abs()>0.6).sum().sum())
    if bad>0: health.append(f"bad-tick {bad}")
    if fatal:
        json.dump({"ok":False,"issues":health,"asof":str(latest.date())},open(os.path.join(FWD,"health.json"),"w"),indent=2)
        print(f"⛔ FAIL-CLOSED: {'; '.join(health)} — 기존 로그/대시보드 보존(업데이트 안 함)"); return
    json.dump({"ok":True,"issues":health,"asof":str(latest.date())},open(os.path.join(FWD,"health.json"),"w"),indent=2)
    sma=px[avail].rolling(200).mean()
    spyvol=px["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
    regime=pd.Series([0.5 if (d in spyvol.index and pd.notna(spyvol[d]) and spyvol[d]>VOL_GATE) else 1.0 for d in px.index],index=px.index)
    on=(px[avail]>sma).astype(float)                    # 종가>200dMA → 1
    w_etf=on.div(on.sum(axis=1).replace(0,np.nan),axis=0).fillna(0.0).mul(regime,axis=0)*TREND_BUDGET
    letf=pd.DataFrame(0.0,index=px.index,columns=list(LETF_MAP.values()))
    for u,l in LETF_MAP.items():
        if u in on.columns: letf[l]=on[u]
    w_letf=letf.div(letf.sum(axis=1).replace(0,np.nan),axis=0).fillna(0.0).mul(regime,axis=0)*LETF_BUDGET
    W=(pd.concat([w_etf,w_letf],axis=1).fillna(0.0))*LEV
    rets=px[W.columns].pct_change().fillna(0.0)
    port=(W.shift(1)*rets).sum(axis=1)                  # next-bar: t-1 종가 가중치 × t 수익
    first=sma.dropna(how="all").index
    if len(first)==0: print("⚠️ 200일 history 부족 — 더 누적 필요"); return
    port=port[port.index>=first[0]]; nav=CAP*(1+port).cumprod()

    # 라이브 인셉션 기록(첫 실행일=진짜 forward 시작점)
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    today=str(px.index[-1].date())
    if "inception_live" not in state: state["inception_live"]=today
    state["last_run"]=today; state["last_nav"]=float(nav.iloc[-1]); state["bad_ticks"]=int(bad)
    json.dump(state,open(STATE,"w"),indent=2)
    incep=pd.Timestamp(state["inception_live"])

    # 로그(append-only by date)
    cur_on=[c for c in avail if on.iloc[-1][c]>0]; cur_reg=float(regime.iloc[-1])
    logdf=pd.DataFrame({"date":nav.index,"nav":nav.values,"port_ret":port.values})
    logdf.to_csv(LOG,index=False)

    # ── 라이브 대시보드 ──
    spy=px["SPY"].reindex(nav.index).ffill(); spy_nav=CAP*spy/spy.iloc[0]
    tot=nav.iloc[-1]/CAP-1; spytot=spy_nav.iloc[-1]/CAP-1; dd=(nav/nav.cummax()-1).min()
    r=port.dropna(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float("nan")
    live=nav[nav.index>=incep]; live_tot=(live.iloc[-1]/live.iloc[0]-1) if len(live)>1 else 0.0
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.8)); plt.plot(nav.index,nav/CAP,color="#22d3ee",lw=2.2,label="forward book (trend+LETF)")
    plt.plot(spy_nav.index,spy_nav/CAP,color="#f59e0b",lw=1.4,ls="--",label="SPY")
    plt.axvline(incep,color="#34d399",lw=1.2,ls=":"); plt.text(incep,plt.ylim()[1],"  live start",color="#34d399",fontsize=8,va="top")
    plt.legend(framealpha=.2); plt.title("Forward paper NAV vs SPY (left of dotted = warm-start backtest)",color="#e5e7eb"); plt.ylabel("× ₩100M")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); chart=base64.b64encode(b.getvalue()).decode()
    Wn=W.iloc[-1]/LEV; trows="".join(f"<tr><td><b>{t}</b></td><td class=num>{px.iloc[-1][t]:.2f}</td><td class=num>{(sma.iloc[-1][t] if t in sma.columns else float('nan')):.2f}</td><td>{'🟢 LONG' if t in cur_on else '⚪ flat'}</td><td class=num>{Wn[t]*100:.1f}%</td></tr>" for t in avail)
    ltags="".join(f"<span class=tag>{l} {Wn[l]*100:.1f}%</span>" for l in LETF_MAP.values() if Wn.get(l,0)>0) or "없음"
    C=lambda v:'pos' if v>=0 else 'neg'; hstr=("✅ 무결성 OK" if not health else "⚠️ "+"; ".join(health))
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA Forward (LIVE paper)</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:980px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.4em}}
.badge{{background:#064e3b;color:#6ee7b7;border-radius:6px;padding:2px 9px;font-size:.72em;font-weight:700}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}} .kpi{{flex:1;min-width:120px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:12px 14px}}
.kpi .l{{color:#94a3b8;font-size:.74em;text-transform:uppercase}} .kpi .v{{font-size:1.5em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:16px;margin:10px 0}} img{{width:100%;border-radius:10px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 8px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:.8em}} td.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#34d399}} .neg{{color:#f87171}}
.tag{{display:inline-block;background:#064e3b;color:#6ee7b7;border-radius:6px;padding:1px 8px;margin:2px;font-size:.85em}}
h2{{font-size:1.1em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:24px}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.86em}}</style></head><body>
<div class=wrap><h1>🟢 PRAMANA Forward — LIVE paper book <span class=badge>AUTO · 일1회 · free EOD</span></h1>
<p style='color:#94a3b8'>업데이트 {today} · 라이브 인셉션 {state['inception_live']} · 매시간 자동 새로고침 · trend+LETF sleeve (무인 무료데이터)</p>
<div class=kpis>
<div class=kpi><div class=l>전체 누적</div><div class="v {C(tot)}">{tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>라이브 이후</div><div class="v {C(live_tot)}">{live_tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>SPY</div><div class="v {C(spytot)}">{spytot*100:+.2f}%</div></div>
<div class=kpi><div class=l>MaxDD</div><div class="v neg">{dd*100:.1f}%</div></div>
<div class=kpi><div class=l>Sharpe</div><div class="v">{sh:+.2f}</div></div>
<div class=kpi><div class=l>vol regime</div><div class="v">{'½ derisk' if cur_reg<1 else 'full'}</div></div></div>
<div class=card><img src="data:image/png;base64,{chart}"></div>
<h2>🛒 현재 타깃 (종가 {today} 기준 · 내일 적용)</h2>
<div class=card><table><tr><th>ETF</th><th class=num>종가</th><th class=num>200d MA</th><th>상태</th><th class=num>비중</th></tr>{trows}</table>
<p style='margin-top:10px'><b>LETF dose:</b> {ltags} · <b>레버:</b> {LEV:.0f}x · <b>추세 ON:</b> {len(cur_on)}/{len(avail)} · <b>vol regime:</b> {'½ 디리스킹' if cur_reg<1 else 'full'}</p></div>
<div class=warn>⚠️ <b>PAPER·무료데이터.</b> 이 forward 트랙은 <b>trend+LETF sleeve만</b> 돈다(equity 시장중립 sleeve는 유료 Sharadar 펀더멘털 필요 → 구독중 월간 갱신, 현재 일시정지). 점선 왼쪽=가격history 워밍(백테스트), 오른쪽=진짜 라이브 forward. 무결성 체크: {hstr} · 데이터 단일소스(무료)=실자본 부적합(Codex: 2개 독립피드 필요). <b>실거래 아님</b> — 12개월 라이브 트랙 + 사람 승인 게이트 통과 전 실자본 금지.</div>
<p style='color:#64748b;font-size:.8em;margin-top:12px'>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/forward_runner.py >> outputs/forward/cron.log 2>&1</code> · 생성 forward_runner.py</p>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ forward 업데이트 {today} · 누적{tot*100:+.2f}%(SPY{spytot*100:+.1f}%)·MDD{dd*100:.1f}%·Sharpe{sh:+.2f}·추세ON {len(cur_on)}/{len(avail)}·badtick {bad}")
    print(f"   라이브 인셉션 {state['inception_live']} · LETF {[l for l in LETF_MAP.values() if Wn.get(l,0)>0]} · 대시보드 → outputs/forward_dashboard.html")

if __name__=="__main__": main()
