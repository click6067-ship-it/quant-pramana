#!/usr/bin/env python3
"""PRAMANA A2 — Convex Raider Book 라이브 paper 러너 (가상 ₩1억).
Beta Engine(QQQ30+TQQQ40 자동·일봉) + Attack12/Moonshot8 슬롯 + Vault10 + Risk Dashboard(Leadership Score·TQQQ Decay·regime).
설계=PRAMANA_V4/PRAMANA_A2_Convex_Raider_Book.md. 데이터=Sharadar SFP(ETF)/SEP(메가캡)·yfinance fallback.
PAPER·자본권한0·V7/A1과 독립. v0: Vault=excess HWM 계산·권고 표시(실제 ledger 차감은 v0.1·forward 초기엔 0).
Risk Dashboard=정보용(자동매도 금지·신규/증액 게이트만). 사용: python engine/a2_live_runner.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
A2=os.path.join(ROOT,"outputs","a2_live"); POS=os.path.join(A2,"positions"); os.makedirs(POS,exist_ok=True)
PRICES=os.path.join(A2,"prices.csv"); STATE=os.path.join(A2,"state.json"); LOG=os.path.join(A2,"nav_log.csv")
ATTACK_F=os.path.join(POS,"attack.json"); MOON_F=os.path.join(POS,"moonshot.json")
DASH=os.path.join(ROOT,"outputs","a2_live_dashboard.html"); KEY=os.path.join(ROOT,".ndl_key")
CAP=100_000_000; INCEP_DEFAULT="2026-05-12"
ALLOC={"qqq":0.30,"tqqq":0.40,"attack":0.12,"moonshot":0.08,"vault":0.10}
BETA=["QQQ","TQQQ"]; LEADERS=["NVDA","MSFT","AAPL","AMZN","GOOGL","META","AVGO","TSLA","AMD","NFLX"]
def loadj(p,d):
    if os.path.exists(p):
        try: return json.load(open(p))
        except: return d
    json.dump(d,open(p,"w"),indent=2); return d
def pull(sfp_tk, sep_tk):
    try:
        import nasdaqdatalink as ndl; ndl.ApiConfig.api_key=open(KEY).read().strip()
        fr=[]
        if sfp_tk:
            d=ndl.get_table("SHARADAR/SFP",ticker=sfp_tk,paginate=True)
            if len(d): fr.append(d.pivot(index="date",columns="ticker",values="closeadj"))
        if sep_tk:
            d=ndl.get_table("SHARADAR/SEP",ticker=sep_tk,paginate=True)
            if len(d): fr.append(d.pivot(index="date",columns="ticker",values="closeadj"))
        if fr:
            px=pd.concat(fr,axis=1).sort_index(); px.index=pd.to_datetime(px.index)
            px=px.loc[:,~px.columns.duplicated()]
            if "QQQ" in px.columns and "TQQQ" in px.columns: return px.dropna(how="all"),"Sharadar(유료·PIT)"
    except Exception: pass
    import yfinance as yf
    tk=list(dict.fromkeys(sfp_tk+sep_tk)); df=yf.download(tk,period="800d",interval="1d",auto_adjust=True,progress=False)
    c=df["Close"] if isinstance(df.columns,pd.MultiIndex) else df
    return c.dropna(how="all"),"yfinance(fallback)"
def main():
    dry="--dry" in sys.argv; DATASRC="cache/dry"
    attack=loadj(ATTACK_F,[]); moon=loadj(MOON_F,[])
    pos_tk=sorted({p["ticker"] for p in attack+moon if p.get("ticker")})
    hist=pd.read_csv(PRICES,index_col=0,parse_dates=True) if os.path.exists(PRICES) else None
    if dry and hist is not None: px=hist
    elif dry: print("no cache — run live once first"); return
    else:
        new,DATASRC=pull(list(dict.fromkeys(BETA+pos_tk)),list(dict.fromkeys(LEADERS+pos_tk)))
        px=new if hist is None else pd.concat([hist,new[~new.index.isin(hist.index)]]).sort_index()
        px=px[~px.index.duplicated(keep="last")]; px.to_csv(PRICES)
    health=[]; latest=px.index[-1]
    if not dry and (pd.Timestamp(dt.date.today())-latest).days>5: health.append("STALE>5d")
    if any(t not in px.columns for t in BETA): health.append("QQQ/TQQQ missing")
    if health: json.dump({"ok":False,"issues":health},open(os.path.join(A2,"health.json"),"w")); print(f"⛔ FAIL-CLOSED: {health}"); return
    json.dump({"ok":True,"as_of":str(latest.date())},open(os.path.join(A2,"health.json"),"w"))
    state=loadj(STATE,{}); today=str(latest.date())
    if "inception" not in state: state["inception"]=INCEP_DEFAULT
    incep=pd.Timestamp(state["inception"])
    # ── Beta Engine (QQQ30 + TQQQ40 자동·inception부터) ──
    def navser(t,w):
        r=px[t].pct_change(); adays=r.dropna().index; days=adays[adays>=incep]
        if len(days)==0: days=adays[-1:]
        return CAP*w*(1+r.reindex(days).fillna(0)).cumprod(), days
    qqq_nav,days=navser("QQQ",ALLOC["qqq"]); tqqq_nav,_=navser("TQQQ",ALLOC["tqqq"])
    qqq_val=float(qqq_nav.iloc[-1]); tqqq_val=float(tqqq_nav.iloc[-1])
    def cur(t):
        try: return float(px[t].dropna().iloc[-1])
        except: return float("nan")
    # ── Attack / Moonshot (positions JSON·비면 현금) ──
    a_bud=CAP*ALLOC["attack"]; a_dep=sum(p["shares"]*p["entry"] for p in attack); a_mkt=sum(p["shares"]*cur(p["ticker"]) for p in attack); a_val=a_bud-a_dep+a_mkt
    m_bud=CAP*ALLOC["moonshot"]; m_dep=sum(p["shares"]*p["entry"] for p in moon); m_mkt=sum(p["shares"]*cur(p["ticker"]) for p in moon); m_val=m_bud-m_dep+m_mkt
    vault_base=CAP*ALLOC["vault"]
    # ── 벤치 QQQ (since incep) ──
    qb=(1+px["QQQ"].pct_change().reindex(days).fillna(0)).cumprod(); qqq_ret=float(qb.iloc[-1]-1)
    spy_ret=None
    # ── Risk Dashboard: Leadership Score (메가캡 10종·정보용) ──
    score=0; q1m=px["QQQ"].pct_change(21)
    for t in LEADERS:
        if t not in px.columns: continue
        s=px[t].dropna()
        if len(s)<50: continue
        p=s.iloc[-1]; ma20=s.rolling(20).mean().iloc[-1]; ma50=s.rolling(50).mean().iloc[-1]; t1m=s.pct_change(21).iloc[-1]
        score+=(1 if p<ma20 else 0)+(1 if p<ma50 else 0)+(1 if (pd.notna(t1m) and pd.notna(q1m.iloc[-1]) and t1m<q1m.iloc[-1]) else 0)
    lead=("RED" if score>=21 else "YELLOW" if score>=11 else "GREEN")
    # ── TQQQ Decay Meter (횡보 고변동) ──
    q20ret=px["QQQ"].pct_change(20).iloc[-1]; q20vol=px["QQQ"].pct_change().rolling(20).std().iloc[-1]*np.sqrt(252)
    decay=bool(abs(q20ret)<0.03 and q20vol>0.25)
    regime=("Risk-Off" if lead=="RED" else "Red King" if (lead=="YELLOW" or decay) else "Base")
    beta_expo=ALLOC["qqq"]*1+ALLOC["tqqq"]*3  # ≈ QQQ 1.5x
    # ── Vault excess HWM (v0 계산·권고 표시·실제 차감 v0.1) ──
    active_bud=CAP*(ALLOC["qqq"]+ALLOC["tqqq"]+ALLOC["attack"]+ALLOC["moonshot"]); active_nav=qqq_val+tqqq_val+a_val+m_val
    active_ret=active_nav/active_bud-1; excess=active_ret-qqq_ret
    hwm=state.get("excess_hwm",0.0); hard=state.get("hard_vault",0.0); rel=state.get("reload_vault",0.0)
    if excess>hwm and excess>=0.04:
        rate=0.50 if excess>=0.12 else (0.50 if excess>=0.08 else 0.25)
        mv=(excess-hwm)*active_bud*rate; hard+=mv*0.7; rel+=mv*0.3
    if excess>hwm: state["excess_hwm"]=excess
    state["hard_vault"]=hard; state["reload_vault"]=rel
    nav=active_nav+vault_base; tot=nav/CAP-1
    state.update({"last_run":today,"nav":nav,"total_ret":tot,"qqq_val":qqq_val,"tqqq_val":tqqq_val,"attack_val":a_val,"moonshot_val":m_val,"vault_base":vault_base,
                  "excess_vs_qqq":excess,"lead_score":int(score),"lead":lead,"decay":decay,"regime":regime,"data_source":DATASRC,"beta_expo":beta_expo,
                  "hard_vault":hard,"reload_vault":rel,"n_attack":len(attack),"n_moonshot":len(moon)})
    json.dump(state,open(STATE,"w"),indent=2)
    # ── log ──
    row=pd.DataFrame([{"date":today,"nav":nav,"qqq_val":qqq_val,"tqqq_val":tqqq_val,"excess":excess,"lead":lead,"regime":regime}])
    if os.path.exists(LOG): old=pd.read_csv(LOG); old=old[old["date"]!=today]; pd.concat([old,row]).to_csv(LOG,index=False)
    else: row.to_csv(LOG,index=False)
    # ── 대시보드 ──
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    a2ser=qqq_nav+tqqq_nav+(a_val+m_val+vault_base)
    qqqbench=CAP*qb
    f=plt.figure(figsize=(11,3.4))
    plt.plot(a2ser.index,a2ser/CAP,label="A2 Convex Raider",lw=2.4,color="#22d3ee")
    plt.plot(qqqbench.index,qqqbench/CAP,label="QQQ",lw=1.3,color="#a78bfa",ls="--")
    plt.legend(framealpha=.2); plt.title("PRAMANA A2 Convex Raider — paper NAV vs QQQ",color="#e5e7eb"); plt.ylabel("배수(×)")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    def won(x): return f"₩{x/1e8:.3f}억"
    rc={"GREEN":"#34d399","YELLOW":"#fbbf24","RED":"#f87171"}[lead]
    rgc={"Base":"#34d399","Red King":"#fbbf24","Risk-Off":"#f87171"}[regime]
    arows="".join(f'<tr><td>{p["ticker"]}</td><td>{p.get("catalyst","")[:36]}</td><td>{p["shares"]}</td><td>{p["entry"]}</td><td>{cur(p["ticker"]):.2f}</td><td class="{"pos" if cur(p["ticker"])>=p["entry"] else "neg"}">{(cur(p["ticker"])/p["entry"]-1)*100:+.1f}%</td></tr>' for p in attack) or '<tr><td colspan=6 style="color:#64748b;text-align:center">— 포지션 없음 (Attack ₩0.12억 현금 대기) —</td></tr>'
    mrows="".join(f'<tr><td>{p["ticker"]}</td><td>{p.get("thesis","")[:46]}</td><td>{p["shares"]}</td><td>{p["entry"]}</td><td>{cur(p["ticker"]):.2f}</td></tr>' for p in moon) or '<tr><td colspan=5 style="color:#64748b;text-align:center">— thesis 없음 (Moonshot ₩0.08억 현금 대기) —</td></tr>'
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A2 Live</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.3em}}
.badge{{border-radius:6px;padding:2px 9px;font-size:.66em;font-weight:700}} .bm{{background:#5b21b6;color:#ddd6fe}} .bp{{background:#1e3a8a;color:#bfdbfe}} .bw{{background:#064e3b;color:#6ee7b7}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}} .kpi{{flex:1;min-width:100px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.7em}} .kpi .v{{font-size:1.25em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.03em;border-left:4px solid #a78bfa;padding-left:10px;margin-top:18px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
table{{width:100%;border-collapse:collapse;font-size:.84em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 9px}} td{{padding:5px 9px;border-top:1px solid #1a2540}}
.bar{{display:flex;height:28px;border-radius:8px;overflow:hidden;margin:6px 0}} .bar div{{display:flex;align-items:center;justify-content:center;font-size:.66em;font-weight:700}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:11px 14px;color:#fde68a;font-size:.82em}}</style></head><body>
<div class=wrap><h1>🟣 PRAMANA A2 — Convex Raider Book<span class="badge bm">CONVEX</span><span class="badge bp">PAPER</span><span class="badge bw">가상 ₩1억</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·인셉션 {state['inception']}(1달 백필)·데이터={DATASRC}·배분 <b>QQQ30/TQQQ40/Attack12/Moonshot8/Vault10</b>·실질 QQQ beta ≈ {beta_expo:.1f}x. 검증된 알파 아님 — QQQ를 *크게 이길 확률*을 사는 book.</p>
<div class=kpis>
<div class=kpi><div class=l>총 NAV</div><div class="v {'pos' if tot>=0 else 'neg'}">{won(nav)}</div></div>
<div class=kpi><div class=l>총수익</div><div class="v {'pos' if tot>=0 else 'neg'}">{tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>QQQ(동기간)</div><div class="v">{qqq_ret*100:+.2f}%</div></div>
<div class=kpi><div class=l>vs QQQ(excess)</div><div class="v {'pos' if excess>=0 else 'neg'}">{excess*100:+.2f}%p</div></div>
<div class=kpi><div class=l>regime</div><div class="v" style="color:{rgc}">{regime}</div></div></div>
<div class=card><b style='font-size:.82em;color:#94a3b8'>Sleeve 배분</b>
<div class=bar><div style="width:30%;background:#2563eb">QQQ 30</div><div style="width:40%;background:#7c3aed">TQQQ 40</div><div style="width:12%;background:#dc2626">Atk 12</div><div style="width:8%;background:#d97706">Moon 8</div><div style="width:10%;background:#475569">Vault 10</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<h2>📊 Sleeve 현황</h2>
<div class=card><table><tr><th>Sleeve</th><th>배분</th><th>평가액</th><th>비고</th></tr>
<tr><td style="color:#2563eb;font-weight:700">QQQ Core</td><td>30%</td><td>{won(qqq_val)}</td><td style="color:#94a3b8">성장 베타·자동</td></tr>
<tr><td style="color:#7c3aed;font-weight:700">TQQQ Booster</td><td>40%</td><td>{won(tqqq_val)}</td><td style="color:#94a3b8">레버(알파 아님·Booster)·자동</td></tr>
<tr><td style="color:#dc2626;font-weight:700">Attack</td><td>12%</td><td>{won(a_val)}</td><td style="color:#94a3b8">catalyst+수급({len(attack)}건·분봉 후 자동집행)</td></tr>
<tr><td style="color:#d97706;font-weight:700">Moonshot</td><td>8%</td><td>{won(m_val)}</td><td style="color:#94a3b8">비대칭({len(moon)}건·thesis 수동)</td></tr>
<tr><td style="color:#64748b;font-weight:700">Vault</td><td>10%</td><td>{won(vault_base)}</td><td style="color:#94a3b8">+ 권고 잠금 Hard {won(hard)}/Reload {won(rel)}</td></tr></table></div>
<h2>🚦 Risk Dashboard <span style="color:#64748b;font-size:.7em">(정보용·자동매도 금지·신규/증액 게이트)</span></h2>
<div class=card>
<b>Leadership Risk:</b> <span style="color:{rc};font-weight:700">{lead}</span> (score {score}/30·메가캡 10종 20/50일선·QQQ 상대) →
{'TQQQ 유지·Attack 허용' if lead=='GREEN' else 'TQQQ 증액 금지·Attack size 50%' if lead=='YELLOW' else 'TQQQ 신규 금지·Attack/Moonshot 신규 금지'}<br>
<b>TQQQ Decay Meter:</b> <span style="color:{'#f87171' if decay else '#34d399'};font-weight:700">{'DECAY ZONE(횡보 고변동)' if decay else 'OK'}</span> (QQQ 20일 {q20ret*100:+.1f}%·vol {q20vol*100:.0f}%)<br>
<b>Beta Governor:</b> 실질 QQQ beta ≈ <b>{beta_expo:.1f}x</b> (QQQ 1× + TQQQ 3×)<br>
<b>regime:</b> <span style="color:{rgc};font-weight:700">{regime}</span></div>
<h2>⚔️ Attack 포지션 <span style="color:#64748b;font-size:.7em">(positions/attack.json)</span></h2>
<div class=card><table><tr><th>티커</th><th>catalyst</th><th>수량</th><th>진입</th><th>현재</th><th>손익</th></tr>{arows}</table></div>
<h2>🚀 Moonshot thesis <span style="color:#64748b;font-size:.7em">(positions/moonshot.json)</span></h2>
<div class=card><table><tr><th>티커</th><th>thesis</th><th>수량</th><th>진입</th><th>현재</th></tr>{mrows}</table></div>
<div class=warn>⚠️ PAPER·NO LIVE·가상 ₩1억. <b>검증된 알파 아님 — 고위험 convex book.</b> TQQQ=Booster(Core 아님). Attack 분봉 자동집행은 분봉 벤더 후·Moonshot은 수동 thesis. Vault=excess HWM 권고(v0 표시·실제 ledger 차감 v0.1·forward 초기엔 0). NEG Filing Gate 필수·물타기 금지·이길 때만 피라미딩. V7/A1과 독립 평가.<br>cron: <code>0 6 * * 2-6 cd {ROOT}/phase1a && .venv/bin/python engine/a2_live_runner.py</code></div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ A2 live {today}·NAV {won(nav)}({tot*100:+.2f}%)·QQQ{qqq_ret*100:+.1f}%·excess{excess*100:+.1f}%p·QQQ{won(qqq_val)}/TQQQ{won(tqqq_val)}·Lead {lead}({score}/30)·Decay{'Y' if decay else 'N'}·regime {regime}·{DATASRC}·인셉션{state['inception']}")
if __name__=="__main__": main()
