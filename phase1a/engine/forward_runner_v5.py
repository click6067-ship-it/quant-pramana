#!/usr/bin/env python3
"""PRAMANA V5 — forward runner (무인 일1회). v5 Aggressive Leveraged Core Beta를 *실제* forward로.
Core(SPY/QQQ 50/50) × vol-target(28%·캡 2.0x) × DD ladder. free yfinance EOD만. CPU·초.
look-ahead 없음(가중치 t→수익 t+1). 가격캐시 append-only. fail-closed 무결성. + forward 판정표 자동채점.
reconciliation 2nd 피드 = stooq 404 → UNKNOWN 정직표기(TODO). 사용: python engine/forward_runner_v5.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FWD=os.path.join(ROOT,"outputs","forward_v5"); os.makedirs(FWD,exist_ok=True)
PRICES=os.path.join(FWD,"prices.csv"); STATE=os.path.join(FWD,"state.json"); LOG=os.path.join(FWD,"forward_log.csv")
DASH=os.path.join(ROOT,"outputs","v5_forward_dashboard.html"); CAP=100_000_000
RF=0.05; TVOL=0.28; LMAX=2.0; TICK=["SPY","QQQ"]
def ddscale(dd): return 0.2 if dd<=-0.40 else 0.4 if dd<=-0.30 else 0.7 if dd<=-0.20 else 1.0
def pull():
    import yfinance as yf
    df=yf.download(TICK,period="400d",interval="1d",auto_adjust=True,progress=False)
    return (df["Close"] if isinstance(df.columns,pd.MultiIndex) else df).dropna(how="all")
def main():
    dry="--dry" in sys.argv
    hist=pd.read_csv(PRICES,index_col=0,parse_dates=True) if os.path.exists(PRICES) else None
    if dry and hist is not None: px=hist
    elif dry: print("no cache"); return
    else:
        new=pull(); px=new if hist is None else pd.concat([hist,new[~new.index.isin(hist.index)]]).sort_index()
        px=px[~px.index.duplicated(keep="last")]; px.to_csv(PRICES)
    # fail-closed 무결성
    health=[]; latest=px.index[-1]
    if not dry and (pd.Timestamp(dt.date.today())-latest).days>5: health.append("STALE")
    if any(t not in px.columns for t in TICK): health.append("missing ticker")
    if float(px[TICK].iloc[-1].isna().mean())>0: health.append("NaN latest")
    if health:
        json.dump({"ok":False,"issues":health},open(os.path.join(FWD,"health.json"),"w"))
        print(f"⛔ FAIL-CLOSED: {health} — 업데이트 안 함"); return
    # v5 북 (vol-target 레버드 Core)
    ret=px[TICK].pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]
    rvol=core.rolling(20).std()*np.sqrt(252)
    days=core.dropna().index; days=days[days>=rvol.dropna().index[0]]
    nav=[CAP]; peak=CAP; levs=[]
    for i in range(1,len(days)):
        d=days[i]; p=days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0
        L*=ddscale(nav[-1]/peak-1)
        nav.append(nav[-1]*(1+L*core.get(d,0)-(L-1)*RF/252)); peak=max(peak,nav[-1]); levs.append(L)
    NAV=pd.Series(nav,index=days); curL=levs[-1] if levs else 1.0
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    today=str(latest.date())
    if "inception_live" not in state: state["inception_live"]=today
    state.update({"last_run":today,"nav":float(NAV.iloc[-1]),"cur_lever":round(curL,2)}); json.dump(state,open(STATE,"w"),indent=2)
    pd.DataFrame({"date":NAV.index,"nav":NAV.values}).to_csv(LOG,index=False)
    # ── 판정표 자동채점 (forward) ──
    spy=CAP*(1+ret["SPY"].reindex(days).fillna(0)).cumprod(); qqq=CAP*(1+ret["QQQ"].reindex(days).fillna(0)).cumprod()
    def mdd(s): return (s/s.cummax()-1).min()
    qup=(qqq.iloc[-1]/qqq.iloc[0]-1); vup=(NAV.iloc[-1]/NAV.iloc[0]-1)   # 전체(워밍 포함) = KPI 맥락용
    # 판정표 = LIVE-only (inception_live 이후). live 짧으면 PENDING. 미구현=UNKNOWN=불합격 (Codex audit fix)
    ls=pd.Timestamp(state["inception_live"]); live=NAV.index[NAV.index>=ls]; nlive=len(live); SHORT=nlive<20
    pend=lambda v:(f"PENDING(live {nlive}일·12mo 필요)" if SHORT else v); pok=lambda ok:(None if SHORT else ok)
    if not SHORT:
        nv=NAV.reindex(live); nq=qqq.reindex(live); lq=nq.iloc[-1]/nq.iloc[0]-1
        lupcap=((nv.iloc[-1]/nv.iloc[0]-1)/lq) if lq>0 else float('nan'); lmdd=mdd(nv)
    else: lupcap=lmdd=float('nan')
    upcap=lupcap
    card=[("상방참여 vs QQQ(live)","≥80%",pend(f"{lupcap*100:.0f}%"),pok(lupcap>=0.80)),
          ("MDD(live)","≤−40%(kill −50%)",pend(f"{lmdd*100:.0f}%"),pok(lmdd>=-0.40)),
          ("레버 cap breach","=0(≤2.0x)",f"max {max(levs) if levs else 1:.2f}x",(max(levs) if levs else 1)<=2.0001),
          ("Ulcer index","≤QQQ×1.2","NOT_IMPLEMENTED→UNKNOWN",None),
          ("회복일수","≤QQQ×1.5","NOT_IMPLEMENTED→UNKNOWN",None),
          ("체결오차/슬리피지","budget 내","NOT_IMPLEMENTED→UNKNOWN",None),
          ("funding/borrow","반영","NOT_IMPLEMENTED→UNKNOWN",None),
          ("reconciliation","2nd 피드","UNKNOWN(stooq 404·TODO)",None),
          ("missed-run/무결성","fail-closed",f"{'OK' if not health else 'FAIL'}",not health)]
    # ── 대시보드 ──
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.6))
    for k,s,c in [("V5 forward",NAV,"#22d3ee"),("QQQ",qqq,"#a78bfa"),("SPY",spy,"#f59e0b")]:
        plt.plot(s.index,s/CAP,label=k,lw=2.2 if k=="V5 forward" else 1.4,color=c,ls=("-" if "V5" in k else "--"))
    plt.axvline(pd.Timestamp(state["inception_live"]),color="#34d399",lw=1,ls=":")
    plt.legend(framealpha=.2); plt.title("V5 forward (점선=live start·좌측은 워밍 backtest)",color="#e5e7eb"); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    r=NAV.pct_change().dropna(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan')
    rows="".join(f"<tr><td>{a}</td><td>{b2}</td><td class=num>{c}</td><td>{'✅' if ok else ('⚠️' if ok is None else '❌')}</td></tr>" for a,b2,c,ok in card)
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>V5 Forward</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:960px;margin:0 auto;padding:22px 18px 50px}} h1{{font-size:1.35em}}
.badge{{background:#064e3b;color:#6ee7b7;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}} .kpi{{flex:1;min-width:110px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.72em}} .kpi .v{{font-size:1.4em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}} td.num{{text-align:right}}
h2{{font-size:1.05em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:20px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.85em}}</style></head><body>
<div class=wrap><h1>🟢 PRAMANA V5 Forward (live paper)<span class=badge>AUTO·일1회·free EOD</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·라이브 인셉션 {state['inception_live']}·현재 레버 {curL:.2f}x · vol-target 레버드 Core(SPY/QQQ). 정직: 레버드 베타.</p>
<div class=kpis><div class=kpi><div class=l>누적</div><div class="v {'pos' if vup>=0 else 'neg'}">{vup*100:+.1f}%</div></div>
<div class=kpi><div class=l>QQQ</div><div class="v">{qup*100:+.1f}%</div></div>
<div class=kpi><div class=l>MDD</div><div class="v neg">{mdd(NAV)*100:.0f}%</div></div>
<div class=kpi><div class=l>Sharpe</div><div class="v">{sh:.2f}</div></div>
<div class=kpi><div class=l>레버</div><div class="v">{curL:.2f}x</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<h2>📋 forward 판정표 (사전등록·수익-only 합격 금지)</h2>
<div class=card><table><tr><th>항목</th><th>기준</th><th class=num>현재</th><th>판정</th></tr>{rows}</table>
<p style='color:#64748b;font-size:.8em;margin-top:8px'>⚠️ 좌측 워밍은 backtest·라이브는 점선 우측. 12개월 forward로 판정. reconciliation은 2nd 피드 wiring 전까지 UNKNOWN.</p></div>
<div class=warn>⚠️ paper·NO LIVE. vol-target 레버드 베타지 알파 아님·no-ruin 아님(gap 무력). forward −70%+ 가능. live cap 1.25~1.5x(crash-pack 후)·사람 게이트 전 실거래 금지.</div>
<div style='color:#64748b;font-size:.78em;margin-top:8px'>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/forward_runner_v5.py</code> · 생성 forward_runner_v5.py</div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ v5 forward {today}·누적{vup*100:+.1f}%(QQQ{qup*100:+.1f}%)·MDD{mdd(NAV)*100:.0f}%·레버{curL:.2f}x·라이브인셉션{state['inception_live']}")
    print(f"   판정표(LIVE-only): {('PENDING(live %d일)'%nlive) if SHORT else ('상방참여%.0f%%'%(upcap*100))}·레버max{max(levs) if levs else 1:.2f}x·ulcer/회복/체결/funding=NOT_IMPLEMENTED·reconcile=UNKNOWN → {DASH}")
if __name__=="__main__": main()
