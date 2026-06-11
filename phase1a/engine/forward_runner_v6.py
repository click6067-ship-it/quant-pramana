#!/usr/bin/env python3
"""PRAMANA V6 — Diversified Aggressive forward runner (Codex 확정 스펙: vol_target·cap1.5·15%DBMF·no extra gate).
V6 = 85% 레버드 Core(SPY/QQQ·vol-target 28%·캡 1.5x·DD ladder) + 15% managed-futures(DBMF).
'같이 안 맞기'(2022 DBMF +21.5% 주식+채권 동반하락때 상승)·낮은 레버. 정직: 레버드 베타+구조적 분산, alpha 아님·no-ruin 아님.
free yfinance·look-ahead無(W t→수익 t+1)·append-only·fail-closed. 판정표 LIVE-only. RESEARCH_ONLY/PAPER_ONLY.
사용: python engine/forward_runner_v6.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FWD=os.path.join(ROOT,"outputs","forward_v6"); os.makedirs(FWD,exist_ok=True)
PRICES=os.path.join(FWD,"prices.csv"); STATE=os.path.join(FWD,"state.json"); LOG=os.path.join(FWD,"forward_log.csv")
DASH=os.path.join(ROOT,"outputs","v6_forward_dashboard.html"); CAP=100_000_000
RF=0.05; TVOL=0.28; LMAX=1.5; MF=0.15; TICK=["SPY","QQQ","DBMF"]
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
    health=[]; latest=px.index[-1]
    if not dry and (pd.Timestamp(dt.date.today())-latest).days>5: health.append("STALE")
    if any(t not in px.columns for t in TICK): health.append("missing ticker")
    if float(px[TICK].iloc[-1].isna().mean())>0: health.append("NaN latest")
    if health:
        json.dump({"ok":False,"issues":health},open(os.path.join(FWD,"health.json"),"w"))
        print(f"⛔ FAIL-CLOSED: {health}"); return
    ret=px[TICK].pct_change(); core=0.5*ret["SPY"]+0.5*ret["QQQ"]; rvol=core.rolling(20).std()*np.sqrt(252)
    days=core.dropna().index; days=days[days>=rvol.dropna().index[0]]
    nav=[CAP]; peak=CAP; levs=[]; core_nav=[CAP]
    for i in range(1,len(days)):
        d=days[i]; p=days[i-1]; rv=rvol.get(p,np.nan)
        L=min(LMAX,TVOL/rv) if (pd.notna(rv) and rv>0) else 1.0; L*=ddscale(nav[-1]/peak-1)
        core_r=L*core.get(d,0)-(L-1)*RF/252
        nav.append(nav[-1]*(1+(1-MF)*core_r+MF*ret["DBMF"].get(d,0))); peak=max(peak,nav[-1]); levs.append(L)
    NAV=pd.Series(nav,index=days); curL=levs[-1] if levs else 1.0
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    today=str(latest.date())
    if "inception_live" not in state: state["inception_live"]=today
    state.update({"last_run":today,"nav":float(NAV.iloc[-1]),"cur_lever":round(curL,2),"spec":"v6 voltarget cap1.5 15%DBMF"}); json.dump(state,open(STATE,"w"),indent=2)
    pd.DataFrame({"date":NAV.index,"nav":NAV.values}).to_csv(LOG,index=False)
    spy=CAP*(1+ret["SPY"].reindex(days).fillna(0)).cumprod(); qqq=CAP*(1+ret["QQQ"].reindex(days).fillna(0)).cumprod()
    def mdd(s): return (s/s.cummax()-1).min()
    vup=NAV.iloc[-1]/NAV.iloc[0]-1; qup=qqq.iloc[-1]/qqq.iloc[0]-1   # 전체(워밍) KPI 맥락
    ls=pd.Timestamp(state["inception_live"]); livei=NAV.index[NAV.index>=ls]; nlive=len(livei); SHORT=nlive<20
    pend=lambda v:(f"PENDING(live {nlive}일)" if SHORT else v); pok=lambda ok:(None if SHORT else ok)
    if not SHORT:
        nv=NAV.reindex(livei); nq=qqq.reindex(livei); lq=nq.iloc[-1]/nq.iloc[0]-1
        lup=((nv.iloc[-1]/nv.iloc[0]-1)/lq) if lq>0 else float('nan'); lmd=mdd(nv)
    else: lup=lmd=float('nan')
    card=[("상방참여 vs QQQ(live)","≥80%",pend(f"{lup*100:.0f}%"),pok(lup>=0.80)),
          ("MDD(live)","≤−40%(kill −50%)",pend(f"{lmd*100:.0f}%"),pok(lmd>=-0.40)),
          ("레버 cap breach","=0(≤1.5x)",f"max {max(levs) if levs else 1:.2f}x",(max(levs) if levs else 1)<=1.5001),
          ("DBMF sleeve","=15%",f"{MF*100:.0f}%",abs(MF-0.15)<1e-6),
          ("Ulcer/회복/체결/funding","사전등록","NOT_IMPLEMENTED→UNKNOWN",None),
          ("reconciliation","2nd 피드","UNKNOWN(무료 독립소스 막힘·실자본전 유료)",None),
          ("missed-run/무결성","fail-closed","OK" if not health else "FAIL",not health)]
    r=NAV.pct_change().dropna(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan')
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.6))
    for k,s,c in [("V6 (Core+15%DBMF)",NAV,"#22d3ee"),("QQQ",qqq,"#a78bfa"),("SPY",spy,"#f59e0b")]:
        plt.plot(s.index,s/CAP,label=k,lw=2.2 if "V6" in k else 1.4,color=c,ls=("-" if "V6" in k else "--"))
    plt.axvline(ls,color="#34d399",lw=1,ls=":"); plt.legend(framealpha=.2); plt.title("V6 Diversified forward (점선=live start)",color="#e5e7eb"); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    rows="".join(f"<tr><td>{a}</td><td>{b2}</td><td class=num>{c}</td><td>{'✅' if ok else ('⚠️' if ok is None else '❌')}</td></tr>" for a,b2,c,ok in card)
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>V6 Forward</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:960px;margin:0 auto;padding:22px 18px 50px}} h1{{font-size:1.3em}}
.badge{{background:#064e3b;color:#6ee7b7;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700}}
.b2{{background:#7f1d1d;color:#fecaca}} .kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}}
.kpi{{flex:1;min-width:108px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.72em}} .kpi .v{{font-size:1.35em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:.9em}} th,td{{padding:6px 9px;border-bottom:1px solid #1e293b;text-align:left}} td.num{{text-align:right}}
h2{{font-size:1.05em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:18px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.85em}}</style></head><body>
<div class=wrap><h1>🟢 PRAMANA V6 — Diversified Aggressive (live paper)<span class=badge>AUTO·일1회</span><span class="badge b2">RESEARCH_ONLY</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·라이브 인셉션 {state['inception_live']}·레버 {curL:.2f}x(캡1.5)·<b>85% 레버드 Core(SPY/QQQ) + 15% managed-futures(DBMF)</b>. '같이 안 맞기' 구조. 정직: 레버드 베타+분산, alpha 아님.</p>
<div class=kpis><div class=kpi><div class=l>누적(전체)</div><div class="v {'pos' if vup>=0 else 'neg'}">{vup*100:+.1f}%</div></div>
<div class=kpi><div class=l>QQQ</div><div class="v">{qup*100:+.1f}%</div></div>
<div class=kpi><div class=l>MDD</div><div class="v neg">{mdd(NAV)*100:.0f}%</div></div>
<div class=kpi><div class=l>Sharpe</div><div class="v">{sh:.2f}</div></div>
<div class=kpi><div class=l>레버</div><div class="v">{curL:.2f}x</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<h2>📋 forward 판정표 (LIVE-only·수익-only 합격 금지)</h2>
<div class=card><table><tr><th>항목</th><th>기준</th><th class=num>현재</th><th>판정</th></tr>{rows}</table>
<p style='color:#64748b;font-size:.8em;margin-top:8px'>워밍(점선 좌측)은 backtest 맥락·판정은 라이브 12개월. NOT_IMPLEMENTED/UNKNOWN = 불합격(완전 자동채점 아님).</p></div>
<div class=warn>⚠️ paper·NO LIVE. V6 = 레버드 베타 + managed-futures 분산('같이 안 맞기'는 2022형 동반하락에 유효·2023 bull엔 드래그=보험료). alpha 아님·no-ruin 아님. DBMF 역사 짧음(2019~). live cap·crash-pack·12mo forward·사람 게이트 전 실거래 금지.</div>
<div style='color:#64748b;font-size:.78em;margin-top:8px'>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/forward_runner_v6.py</code> · 생성 forward_runner_v6.py · 스펙 PRAMANA_V4/PRAMANA_V6_Problem_Frame_v0.1.md</div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ v6 forward {today}·누적{vup*100:+.1f}%(QQQ{qup*100:+.1f}%)·MDD{mdd(NAV)*100:.0f}%·레버{curL:.2f}x·DBMF15%·라이브{state['inception_live']}")
    print(f"   판정표(LIVE): {('PENDING %d일'%nlive) if SHORT else '상방참여%.0f%%'%(lup*100)}·레버max{max(levs) if levs else 1:.2f}x·미구현=UNKNOWN → {DASH}")
if __name__=="__main__": main()
