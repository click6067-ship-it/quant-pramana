#!/usr/bin/env python3
"""PRAMANA A1 — Catalyst Confirmed Attack Book · 라이브 paper ledger 러너 (가상 ₩100M·24/7).
4 sleeve: Base Core 40%(V7 4-sleeve 자동·일봉) + Attack 30% + Moonshot 15% + Cash 15%.
정직 v0: Base Core=자동 실데이터 / Attack·Moonshot=포지션 JSON 평가(비면 현금 대기·스캐너/사람이 채움).
  intraday(ORB/VWAP/RVOL) 자동집행은 분봉 벤더(Polygon/Alpaca) 연동 후 승급 — v0은 일봉 EOD 평가.
forward 가격 = yfinance EOD(forward 정본·무료·매일) / Sharadar=backtest·universe 스캔용(별도).
append-only·fail-closed·next-bar·PAPER·NO LIVE. 사용: python engine/a1_live_runner.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
A1=os.path.join(ROOT,"outputs","a1_live"); POS=os.path.join(A1,"positions"); os.makedirs(POS,exist_ok=True)
PRICES=os.path.join(A1,"prices.csv"); STATE=os.path.join(A1,"state.json"); LOG=os.path.join(A1,"nav_log.csv")
ATTACK_F=os.path.join(POS,"attack.json"); MOON_F=os.path.join(POS,"moonshot.json")
DASH=os.path.join(ROOT,"outputs","a1_live_dashboard.html")
CAP=100_000_000; RF=0.05
ALLOC={"core":0.40,"attack":0.30,"moonshot":0.15,"cash":0.15}     # A1 자본배분 (용하 확정)
CORE_W={"SPY":0.25,"QQQ":0.25,"DBMF":0.25,"GLD":0.15,"IEF":0.10}  # Base Core 내부 = V7 4-sleeve
CORE_TICK=list(CORE_W)
def loadj(p,d):
    if os.path.exists(p):
        try: return json.load(open(p))
        except: return d
    json.dump(d,open(p,"w"),indent=2); return d
def pull(tickers):
    """Sharadar(유료·PIT) 우선 — ETF=SFP·개별주=SEP·closeadj / 실패 시 yfinance fallback. (출처, df) 반환."""
    KEY=os.path.join(ROOT,".ndl_key")
    try:
        import nasdaqdatalink as ndl
        ndl.ApiConfig.api_key=open(KEY).read().strip()
        frames=[]; etfs=[t for t in tickers if t in CORE_TICK]; stocks=[t for t in tickers if t not in CORE_TICK]
        if etfs:
            d=ndl.get_table("SHARADAR/SFP",ticker=etfs,paginate=True)
            if len(d): frames.append(d.pivot(index="date",columns="ticker",values="closeadj"))
        if stocks:
            d=ndl.get_table("SHARADAR/SEP",ticker=stocks,paginate=True)
            if len(d): frames.append(d.pivot(index="date",columns="ticker",values="closeadj"))
        if frames:
            px=pd.concat(frames,axis=1).sort_index(); px.index=pd.to_datetime(px.index)
            if all(t in px.columns for t in CORE_TICK): return px.dropna(how="all"),"Sharadar(유료·PIT)"
    except Exception: pass
    import yfinance as yf
    df=yf.download(tickers,period="600d",interval="1d",auto_adjust=True,progress=False)
    c=df["Close"] if isinstance(df.columns,pd.MultiIndex) else df
    if isinstance(c,pd.Series): c=c.to_frame(tickers[0])
    return c.dropna(how="all"),"yfinance(fallback)"
def main():
    dry="--dry" in sys.argv; DATASRC="cache/dry"
    attack=loadj(ATTACK_F,[]); moon=loadj(MOON_F,[])
    pos_tk=sorted({p["ticker"] for p in attack+moon if p.get("ticker")})
    alltk=CORE_TICK+[t for t in pos_tk if t not in CORE_TICK]
    hist=pd.read_csv(PRICES,index_col=0,parse_dates=True) if os.path.exists(PRICES) else None
    if dry and hist is not None: px=hist
    elif dry: print("no cache — run live once first"); return
    else:
        new,DATASRC=pull(alltk)
        if isinstance(new,pd.Series): new=new.to_frame(alltk[0])
        px=new if hist is None else pd.concat([hist,new[~new.index.isin(hist.index)]]).sort_index()
        px=px[~px.index.duplicated(keep="last")]; px.to_csv(PRICES)
    # ── fail-closed 무결성 가드 ──
    health=[]; latest=px.index[-1]
    if not dry and (pd.Timestamp(dt.date.today())-latest).days>5: health.append("STALE>5d")
    if any(t not in px.columns for t in CORE_TICK): health.append("core ticker missing")
    if float(px[CORE_TICK].iloc[-1].isna().mean())>0: health.append("NaN core latest")
    if health:
        json.dump({"ok":False,"issues":health},open(os.path.join(A1,"health.json"),"w"))
        print(f"⛔ FAIL-CLOSED: {health}"); return
    json.dump({"ok":True,"as_of":str(latest.date())},open(os.path.join(A1,"health.json"),"w"))
    state=loadj(STATE,{}); today=str(latest.date())
    if "inception" not in state: state["inception"]=today; json.dump(state,open(STATE,"w"),indent=2)
    incep=pd.Timestamp(state["inception"])
    # ── Base Core 40% = V7 4-sleeve 자동 (오늘 진입 = inception 이후만 누적·forward 정직) ──
    cret=sum(CORE_W[t]*px[t].pct_change() for t in CORE_TICK); adays=cret.dropna().index
    days=adays[adays>=incep]
    if len(days)==0: days=adays[-1:]
    core_budget=CAP*ALLOC["core"]; core_nav=core_budget*(1+cret.reindex(days).fillna(0)).cumprod()
    core_val=float(core_nav.iloc[-1]); core_ret=core_val/core_budget-1
    def cur(t):
        try: return float(px[t].dropna().iloc[-1])
        except: return float("nan")
    # ── Attack 30% = 포지션 평가 (비면 현금 대기) ──
    a_budget=CAP*ALLOC["attack"]; a_deployed=sum(p["shares"]*p["entry"] for p in attack); a_mkt=sum(p["shares"]*cur(p["ticker"]) for p in attack)
    a_cash=a_budget-a_deployed; a_val=a_cash+a_mkt; a_pnl=a_mkt-a_deployed
    # ── Moonshot 15% = 수동 thesis 슬롯 평가 ──
    m_budget=CAP*ALLOC["moonshot"]; m_deployed=sum(p["shares"]*p["entry"] for p in moon); m_mkt=sum(p["shares"]*cur(p["ticker"]) for p in moon)
    m_cash=m_budget-m_deployed; m_val=m_cash+m_mkt; m_pnl=m_mkt-m_deployed
    # ── Cash 15% (RF 무시·paper) ──
    cash_val=CAP*ALLOC["cash"]
    nav=core_val+a_val+m_val+cash_val; tot=nav/CAP-1
    # ── 벤치 (QQQ·SPY 같은 인셉션) ──
    qqq=CAP*(1+px["QQQ"].pct_change().reindex(days).fillna(0)).cumprod(); spy=CAP*(1+px["SPY"].pct_change().reindex(days).fillna(0)).cumprod()
    qup=qqq.iloc[-1]/CAP-1; sup=spy.iloc[-1]/CAP-1
    # ── state·log (append-only) ──
    state.update({"last_run":today,"nav":nav,"total_ret":tot,"core_val":core_val,"attack_val":a_val,"moonshot_val":m_val,"cash_val":cash_val,
                  "n_attack":len(attack),"n_moonshot":len(moon),"data_source":DATASRC}); json.dump(state,open(STATE,"w"),indent=2)
    row=pd.DataFrame([{"date":today,"nav":nav,"core":core_val,"attack":a_val,"moonshot":m_val,"cash":cash_val,"qqq":float(qqq.iloc[-1]),"spy":float(spy.iloc[-1])}])
    if os.path.exists(LOG):
        old=pd.read_csv(LOG); old=old[old["date"]!=today]; pd.concat([old,row]).to_csv(LOG,index=False)
    else: row.to_csv(LOG,index=False)
    # ── 대시보드 ──
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.4))
    for k,s,c,w in [("A1 NAV",core_nav+a_val+m_val+cash_val,"#22d3ee",2.4),("QQQ",qqq,"#a78bfa",1.3),("SPY",spy,"#f59e0b",1.3)]:
        plt.plot(s.index,s/CAP,label=k,lw=w,color=c,ls=("-" if "A1" in k else "--"))
    plt.legend(framealpha=.2); plt.title("PRAMANA A1 Attack Book — paper NAV vs QQQ·SPY",color="#e5e7eb"); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    def won(x): return f"₩{x/1e8:.3f}억" if abs(x)>=1e7 else f"₩{x:,.0f}"
    def sleeve_row(name,budget,val,pnl,n,note,color):
        return f'<tr><td style="color:{color};font-weight:700">{name}</td><td>{ALLOC[name.split()[0].lower() if name.split()[0].lower() in ALLOC else "cash"]*100:.0f}%</td><td>{won(val)}</td><td class="{"pos" if pnl>=0 else "neg"}">{("+" if pnl>=0 else "")+won(pnl) if pnl else "—"}</td><td>{n}</td><td style="color:#94a3b8;font-size:.85em">{note}</td></tr>'
    arows="".join(f'<tr><td>{p["ticker"]}</td><td>{p.get("catalyst","")[:40]}</td><td>{p["shares"]}</td><td>{p["entry"]}</td><td>{cur(p["ticker"]):.2f}</td><td class="{"pos" if cur(p["ticker"])>=p["entry"] else "neg"}">{(cur(p["ticker"])/p["entry"]-1)*100:+.1f}%</td></tr>' for p in attack) or '<tr><td colspan=6 style="color:#64748b;text-align:center">— 포지션 없음 (Attack 예산 ₩0.30억 현금 대기·스캐너 후보 관찰 중) —</td></tr>'
    mrows="".join(f'<tr><td>{p["ticker"]}</td><td>{p.get("thesis","")[:50]}</td><td>{p["shares"]}</td><td>{p["entry"]}</td><td>{cur(p["ticker"]):.2f}</td><td>최대손실 {won(p.get("maxloss",0))}</td></tr>' for p in moon) or '<tr><td colspan=6 style="color:#64748b;text-align:center">— thesis 없음 (Moonshot 예산 ₩0.15억 현금 대기·수동 thesis 입력 슬롯) —</td></tr>'
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A1 Live</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.3em}}
.badge{{background:#7f1d1d;color:#fca5a5;border-radius:6px;padding:2px 9px;font-size:.68em;font-weight:700}} .b2{{background:#1e3a8a;color:#bfdbfe}} .b3{{background:#064e3b;color:#6ee7b7}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}} .kpi{{flex:1;min-width:104px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.72em}} .kpi .v{{font-size:1.3em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.05em;border-left:4px solid #ef4444;padding-left:10px;margin-top:20px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
table{{width:100%;border-collapse:collapse;font-size:.85em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:7px 9px}} td{{padding:6px 9px;border-top:1px solid #1a2540}}
.bar{{display:flex;height:30px;border-radius:8px;overflow:hidden;margin:6px 0}} .bar div{{display:flex;align-items:center;justify-content:center;font-size:.7em;font-weight:700}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.84em}}</style></head><body>
<div class=wrap><h1>📝 PRAMANA A1 — Catalyst Attack Book<span class=badge>ATTACK</span><span class="badge b2">PAPER FORWARD</span><span class="badge b3">실자본 0</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·인셉션 {state['inception']}·배분 <b>Core 40 / Attack 30 / Moonshot 15 / Cash 15</b>·데이터={DATASRC}. 목표=레버 ETF 없이 QQQ 초과 <i>시도</i>(검증된 알파 아님).</p>
<div class=kpis>
<div class=kpi><div class=l>Paper NAV (시뮬)</div><div class="v {'pos' if tot>=0 else 'neg'}">{won(nav)}</div></div>
<div class=kpi><div class=l>Paper 수익</div><div class="v {'pos' if tot>=0 else 'neg'}">{tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>실투입 자본</div><div class="v">₩0 · NO BROKER</div></div>
<div class=kpi><div class=l>QQQ(동기간)</div><div class="v">{qup*100:+.2f}%</div></div>
<div class=kpi><div class=l>SPY(동기간)</div><div class="v">{sup*100:+.2f}%</div></div>
<div class=kpi><div class=l>vs QQQ</div><div class="v {'pos' if tot-qup>=0 else 'neg'}">{(tot-qup)*100:+.2f}%p</div></div></div>
<div class=card><b style='font-size:.85em;color:#94a3b8'>Sleeve 자본 배분</b>
<div class=bar><div style="width:40%;background:#2563eb">Core 40</div><div style="width:30%;background:#dc2626">Attack 30</div><div style="width:15%;background:#d97706">Moon 15</div><div style="width:15%;background:#475569">Cash 15</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<h2>📊 Sleeve 현황</h2>
<div class=card><table><tr><th>Sleeve</th><th>배분</th><th>평가액</th><th>손익</th><th>포지션</th><th>비고</th></tr>
<tr><td style="color:#2563eb;font-weight:700">Base Core</td><td>40%</td><td>{won(core_val)}</td><td class="{'pos' if core_ret>=0 else 'neg'}">{core_ret*100:+.2f}%</td><td>4-sleeve</td><td style="color:#94a3b8;font-size:.85em">V7 자동(SPY/QQQ/DBMF/GLD/IEF)·backtest 생존 후보·prod-unsafe</td></tr>
<tr><td style="color:#dc2626;font-weight:700">Attack</td><td>30%</td><td>{won(a_val)}</td><td class="{'pos' if a_pnl>=0 else 'neg'}">{('+'+won(a_pnl)) if a_pnl>=0 else won(a_pnl)}</td><td>{len(attack)}</td><td style="color:#94a3b8;font-size:.85em">catalyst+수급(일봉 v0·intraday는 분봉 후)</td></tr>
<tr><td style="color:#d97706;font-weight:700">Moonshot</td><td>15%</td><td>{won(m_val)}</td><td class="{'pos' if m_pnl>=0 else 'neg'}">{('+'+won(m_pnl)) if m_pnl>=0 else won(m_pnl)}</td><td>{len(moon)}</td><td style="color:#94a3b8;font-size:.85em">수동 thesis·−100% 인정/upside 3~10x</td></tr>
<tr><td style="color:#64748b;font-weight:700">Cash</td><td>15%</td><td>{won(cash_val)}</td><td>—</td><td>—</td><td style="color:#94a3b8;font-size:.85em">버퍼</td></tr></table></div>
<h2>⚔️ Attack 포지션 <span style="color:#64748b;font-size:.7em">(positions/attack.json)</span></h2>
<div class=card><table><tr><th>티커</th><th>catalyst</th><th>수량</th><th>진입</th><th>현재</th><th>손익</th></tr>{arows}</table></div>
<h2>🚀 Moonshot thesis <span style="color:#64748b;font-size:.7em">(positions/moonshot.json)</span></h2>
<div class=card><table><tr><th>티커</th><th>thesis</th><th>수량</th><th>진입</th><th>현재</th><th>리스크</th></tr>{mrows}</table></div>
<div class=warn>⚠️ PAPER·NO LIVE·가상 ₩1억. <b>검증된 알파가 아니라 위험을 정직하게 인정한 공격 베팅.</b> Base Core만 자동 실데이터·Attack/Moonshot은 포지션 JSON 평가(intraday 자동집행=분봉 벤더 후 승급). <b>나쁜공시(3.02/3.01/4.01/4.02 등) 회피 필수·catalyst=총알/ORB·VWAP·RVOL=방아쇠.</b> 실자본 게이트=사람.<br>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/a1_live_runner.py</code></div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ A1 live {today}·NAV {won(nav)}({tot*100:+.2f}%)·Core {won(core_val)}({core_ret*100:+.1f}%)·Attack {won(a_val)}({len(attack)})·Moon {won(m_val)}({len(moon)})·Cash {won(cash_val)}·QQQ{qup*100:+.1f}%/SPY{sup*100:+.1f}%·인셉션{state['inception']}")
if __name__=="__main__": main()
