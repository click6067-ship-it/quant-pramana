#!/usr/bin/env python3
"""PRAMANA V7 — Paper Core Candidate = 4-sleeve forward runner + Risk Monitor (정보용·자동전환 금지).
4-sleeve = Equity 50%(SPY/QQQ) + Managed-Futures 25%(DBMF) + Gold 15%(GLD) + Bonds 10%(IEF). 기본 1.0x.
'회피기동=구조적 분산'(코어 전환 없음). Risk Monitor = 200일선/vol/DD 점수→모드 표시(자본 안 옮김).
'Production'은 Promotion Gates(crash-pack+12mo forward+2-feed+attribution+사람 게이트) 통과 후만 — 그 전엔 Paper Candidate.
free yfinance·next-bar·append-only·fail-closed. RESEARCH_ONLY/PRODUCTION_UNSAFE/PAPER. 사용: python engine/forward_runner_v7.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FWD=os.path.join(ROOT,"outputs","forward_v7"); os.makedirs(FWD,exist_ok=True)
PRICES=os.path.join(FWD,"prices.csv"); STATE=os.path.join(FWD,"state.json"); LOG=os.path.join(FWD,"forward_log.csv")
DASH=os.path.join(ROOT,"outputs","v7_forward_dashboard.html"); CAP=100_000_000; RF=0.05; LEV=1.0
TICK=["SPY","QQQ","DBMF","GLD","IEF"]
W={"SPY":0.25,"QQQ":0.25,"DBMF":0.25,"GLD":0.15,"IEF":0.10}   # 4-sleeve(Equity50=SPY/QQQ·MF25·Gold15·Bond10)
def pull():
    import yfinance as yf
    df=yf.download(TICK,period="600d",interval="1d",auto_adjust=True,progress=False)
    return (df["Close"] if isinstance(df.columns,pd.MultiIndex) else df).dropna(how="all")
def risk_mode(spy,sma,vol,dd):  # Market Risk Score (정보용)
    s=0
    if pd.notna(sma) and spy<sma: s+=1
    if pd.notna(vol) and vol>0.22: s+=1
    if pd.notna(dd) and dd<-0.10: s+=1
    return s, {0:"Growth",1:"Caution",2:"Defense"}.get(s,"Crash")
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
    if health: json.dump({"ok":False,"issues":health},open(os.path.join(FWD,"health.json"),"w")); print(f"⛔ FAIL-CLOSED: {health}"); return
    ret=px[TICK].pct_change()
    book=sum(W[t]*ret[t] for t in TICK)
    days=book.dropna().index
    nav=CAP*(1+(LEV*book.reindex(days).fillna(0)-(LEV-1)*RF/252)).cumprod()
    # Risk Monitor (현재)
    sma200=px["SPY"].rolling(200).mean(); svol=px["SPY"].pct_change().rolling(20).std()*np.sqrt(252)
    spydd=(px["SPY"]/px["SPY"].cummax()-1)
    p=px.index[-1]; score,mode=risk_mode(px["SPY"].get(p),sma200.get(p),svol.get(p),spydd.get(p))
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}; today=str(latest.date())
    if "inception_live" not in state: state["inception_live"]=today
    state.update({"last_run":today,"nav":float(nav.iloc[-1]),"risk_score":score,"mode":mode,"book":"4-sleeve 1.0x"}); json.dump(state,open(STATE,"w"),indent=2)
    pd.DataFrame({"date":nav.index,"nav":nav.values}).to_csv(LOG,index=False)
    spy=CAP*(1+ret["SPY"].reindex(days).fillna(0)).cumprod(); qqq=CAP*(1+ret["QQQ"].reindex(days).fillna(0)).cumprod()
    def mdd(s): return (s/s.cummax()-1).min()
    tot=nav.iloc[-1]/nav.iloc[0]-1; qup=qqq.iloc[-1]/qqq.iloc[0]-1; r=nav.pct_change().dropna(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float('nan')
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.6))
    for k,s,c in [("V7 4-sleeve",nav,"#22d3ee"),("QQQ",qqq,"#a78bfa"),("SPY",spy,"#f59e0b")]:
        plt.plot(s.index,s/CAP,label=k,lw=2.2 if "V7" in k else 1.4,color=c,ls=("-" if "V7" in k else "--"))
    plt.legend(framealpha=.2); plt.title("V7 Paper Core Candidate (4-sleeve) vs QQQ·SPY",color="#e5e7eb"); plt.ylabel("×")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    modecolor={"Growth":"#34d399","Caution":"#fbbf24","Defense":"#fb923c","Crash":"#f87171"}[mode]
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>V7 Forward</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:960px;margin:0 auto;padding:22px 18px 50px}} h1{{font-size:1.3em}}
.badge{{background:#064e3b;color:#6ee7b7;border-radius:6px;padding:2px 9px;font-size:.7em;font-weight:700}} .b2{{background:#1e3a8a;color:#bfdbfe}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}} .kpi{{flex:1;min-width:108px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.72em}} .kpi .v{{font-size:1.35em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.05em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:18px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 15px;color:#fde68a;font-size:.85em}}</style></head><body>
<div class=wrap><h1>🟢 PRAMANA V7 — Paper Core Candidate: 4-sleeve<span class=badge>AUTO·일1회</span><span class="badge b2">PAPER</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·라이브 인셉션 {state['inception_live']}·<b>Equity 50%(SPY/QQQ)+MF 25%(DBMF)+Gold 15%(GLD)+Bonds 10%(IEF)·{LEV:.2f}x</b>. 회피기동=구조적 분산(코어 전환 없음). QQQ=benchmark.</p>
<div class=kpis><div class=kpi><div class=l>누적</div><div class="v {'pos' if tot>=0 else 'neg'}">{tot*100:+.1f}%</div></div>
<div class=kpi><div class=l>QQQ</div><div class="v">{qup*100:+.1f}%</div></div>
<div class=kpi><div class=l>MDD</div><div class="v neg">{mdd(nav)*100:.0f}%</div></div>
<div class=kpi><div class=l>Sharpe</div><div class="v">{sh:.2f}</div></div>
<div class=kpi><div class=l>Risk Monitor</div><div class="v" style="color:{modecolor}">{mode}</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<h2>🚦 Risk Monitor (정보용·자본 자동전환 금지)</h2>
<div class=card>현재 모드 <b style="color:{modecolor}">{mode}</b> (score {score}/3: SPY 200일선·20일 변동성·낙폭). <span style='color:#64748b'>이 신호는 *공격 파트*(LETF·급등주 Alpha Lab) throttle용이지 코어(4-sleeve)를 갈아타지 않는다(코어 대전환은 데이터로 휩쏘). 현재 공격 파트 없음→정보 표시만.</span></div>
<div class=warn>⚠️ paper·NO LIVE·<b>Paper Core Candidate</b>(Production 아님). V7 코어 = <b>구조적 분산</b>(알파 아님). QQQ bull엔 수익 ~절반 포기(= 크래시 생존 사는 보험료). DBMF/GLD 짧은 역사(2019~·2008 없음)·crash-pack 미실시.<br><b>🔒 Promotion Gates(실자본 전 전부):</b> crash-pack pass + 12mo forward 판정표 + 2-feed reconciliation + attribution + 사람 자본 게이트. <b>게이트 전 차단:</b> 실자본·1.25x·throttle risk-engine 편입.</div>
<div style='color:#64748b;font-size:.78em;margin-top:8px'>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/forward_runner_v7.py</code> · 스펙 PRAMANA_V4/PRAMANA_V7_Plan_v0.2.md</div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ v7 forward {today}·4-sleeve 누적{tot*100:+.1f}%(QQQ{qup*100:+.1f}%)·MDD{mdd(nav)*100:.0f}%·Sharpe{sh:.2f}·Risk Monitor={mode}({score}/3)·라이브{state['inception_live']}")
if __name__=="__main__": main()
