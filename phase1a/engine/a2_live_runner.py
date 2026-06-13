#!/usr/bin/env python3
"""PRAMANA A2 v2 — Convex Raider 라이브 (가상 ₩1억). config 기반 동적 allocator + Profit Vault + naive beta 판정선.
1단계 뼈대: Beta Engine(QQQ/TQQQ 동적 모드) + Risk Dashboard(Leadership/Decay/모드) + Vault(excess HWM) + 비교(QQQ/SPY/TQQQ/A2/naive).
Attack/Moonshot = positions ledger(2단계 연료·현재 cash). SPY=벤치만(A2 퇴출). 데이터=Sharadar SFP/SEP·yfinance fallback.
대시보드: y=계좌금액(₩1억 스타트)·x=기간·시작점=시작월 평균 정규화(특정일 노이즈 제거). PAPER·자본0. 사용: python engine/a2_live_runner.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); REPO=os.path.dirname(ROOT)
A2=os.path.join(ROOT,"outputs","a2_live"); POS=os.path.join(A2,"positions"); os.makedirs(POS,exist_ok=True)
PRICES=os.path.join(A2,"prices.csv"); STATE=os.path.join(A2,"state.json"); LOG=os.path.join(A2,"nav_log.csv")
DASH=os.path.join(ROOT,"outputs","a2_live_dashboard.html"); KEY=os.path.join(ROOT,".ndl_key")
CFG_PATH=os.path.join(REPO,"config","a2_convex_raider.yaml")
DEFAULT_CFG={"capital":100_000_000,"inception":"2026-05-12","dynamic_mode_enabled":True,
 "allocation":{"base":{"qqq":.35,"tqqq":.35},"berserker":{"qqq":.30,"tqqq":.45},"red_king":{"qqq":.40,"tqqq":.25},
   "attack_lockout":{"qqq":.35,"tqqq":.35},"crash_lockout":{"qqq":.35,"tqqq":.10}},
 "daily_max_shift_pp":.10,"leadership":{"green_max":10,"yellow_max":20},"tqqq_decay":{"qqq_20d_range":.03,"vol_threshold":.25},
 "vault":{"base_pct":.10,"thresholds":[{"excess":.04,"rate":.25},{"excess":.08,"rate":.25},{"excess":.12,"rate":.50}],"hard_ratio":.70,"reload_ratio":.30},
 "naive_benchmark":{"qqq":.35,"tqqq":.35},"verdict":{"horizon_months":12,"must_beat":["naive","qqq"]}}
def load_cfg():
    try:
        import yaml; c=yaml.safe_load(open(CFG_PATH)); return c if c else DEFAULT_CFG
    except Exception: return DEFAULT_CFG
CFG=load_cfg(); CAP=CFG["capital"]
BETA=["QQQ","TQQQ","SPY"]; LEADERS=["NVDA","MSFT","AAPL","AMZN","GOOGL","META","AVGO","TSLA","AMD","NFLX"]
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
            px=pd.concat(fr,axis=1).sort_index(); px.index=pd.to_datetime(px.index); px=px.loc[:,~px.columns.duplicated()]
            if all(t in px.columns for t in ["QQQ","TQQQ"]): return px.dropna(how="all"),"Sharadar(유료·PIT)"
    except Exception: pass
    import yfinance as yf
    tk=list(dict.fromkeys(sfp_tk+sep_tk)); df=yf.download(tk,period="2600d",interval="1d",auto_adjust=True,progress=False)
    c=df["Close"] if isinstance(df.columns,pd.MultiIndex) else df
    return c.dropna(how="all"),"yfinance(fallback)"
def main():
    dry="--dry" in sys.argv; DATASRC="cache/dry"
    attack=loadj(os.path.join(POS,"attack.json"),[]); moon=loadj(os.path.join(POS,"moonshot.json"),[])
    pos_tk=sorted({p["ticker"] for p in attack+moon if p.get("ticker")})
    hist=pd.read_csv(PRICES,index_col=0,parse_dates=True) if os.path.exists(PRICES) else None
    if dry and hist is not None: px=hist
    elif dry: print("no cache"); return
    else:
        new,DATASRC=pull(list(dict.fromkeys(BETA+pos_tk)),list(dict.fromkeys(LEADERS+pos_tk)))
        px=new if hist is None else pd.concat([hist,new[~new.index.isin(hist.index)]]).sort_index()
        px=px[~px.index.duplicated(keep="last")]; px.to_csv(PRICES)
    health=[]; latest=px.index[-1]
    if not dry and (pd.Timestamp(dt.date.today())-latest).days>5: health.append("STALE>5d")
    if any(t not in px.columns for t in ["QQQ","TQQQ"]): health.append("QQQ/TQQQ missing")
    if health: json.dump({"ok":False,"issues":health},open(os.path.join(A2,"health.json"),"w")); print(f"⛔ FAIL-CLOSED: {health}"); return
    json.dump({"ok":True,"as_of":str(latest.date())},open(os.path.join(A2,"health.json"),"w"))
    px=px[[c for c in (BETA+LEADERS) if c in px.columns]].dropna()   # 공통기간(메가캡·QQQ·TQQQ·SPY)
    qr=px["QQQ"].pct_change().fillna(0); tr=px["TQQQ"].pct_change().fillna(0)
    # ── Risk Dashboard 시계열: Leadership Score · Decay ──
    qmom=px["QQQ"].pct_change(21); lead=pd.Series(0.0,index=px.index)
    for t in LEADERS:
        if t not in px.columns: continue
        ma20=px[t].rolling(20).mean(); ma50=px[t].rolling(50).mean()
        lead=lead+(px[t]<ma20).astype(int)+(px[t]<ma50).astype(int)+(px[t].pct_change(21)<qmom).astype(int)
    gmax=CFG["leadership"]["green_max"]; ymax=CFG["leadership"]["yellow_max"]
    q20ret=px["QQQ"].pct_change(20); q20vol=px["QQQ"].pct_change().rolling(20).std()*np.sqrt(252)
    decay=(q20ret.abs()<CFG["tqqq_decay"]["qqq_20d_range"])&(q20vol>CFG["tqqq_decay"]["vol_threshold"])
    def mode_of(l,d):
        if l>ymax: return "attack_lockout"
        if l>gmax or d: return "red_king"
        return "base"
    modes=pd.Series([mode_of(lead.iloc[i],bool(decay.iloc[i])) for i in range(len(px))],index=px.index)
    # ── 동적 allocator (모드별 QQQ/TQQQ 목표·일일 10%p 천이) / dynamic OFF면 base 고정 ──
    AW=CFG["allocation"]; shift=CFG["daily_max_shift_pp"]; dyn=CFG.get("dynamic_mode_enabled",True)
    cur=np.array([AW["base"]["qqq"],AW["base"]["tqqq"]]); a2=1.0; navs=[]
    qa=qr.values; ta=tr.values; mds=modes.values
    for i in range(len(px)):
        m=mds[i] if dyn else "base"; tw=np.array([AW[m]["qqq"],AW[m]["tqqq"]])
        cur=cur+np.clip(tw-cur,-shift,shift)
        a2*=(1+cur[0]*qa[i]+cur[1]*ta[i]); navs.append(a2)
    a2ratio=pd.Series(navs,index=px.index)            # A2 동적 배수(시작 1)
    nb=CFG["naive_benchmark"]; naive=(1+nb["qqq"]*qr+nb["tqqq"]*tr).cumprod()   # naive 고정
    # ── 시작월 평균 정규화 → 계좌금액(₩1억 스타트) ──
    def to_won(s):
        s=s.dropna(); m0=s.index[0].to_period("M"); base=s[s.index.to_period("M")==m0].mean()
        return CAP*s/base
    series={"PRAMANA-A2":to_won(a2ratio),"QQQ":to_won(px["QQQ"]),"SPY":to_won(px["SPY"]),"TQQQ":to_won(px["TQQQ"])}
    naive_won=to_won(naive)
    # ── 멀티앵커 (3년/12/6/3개월/풀) — 누적%·시작월평균 기준 ──
    def cum(s,n):
        s=s.dropna(); seg=s.iloc[-min(n,len(s)):]; return (seg.iloc[-1]/seg.iloc[0]-1)*100
    ANCH=[("3년",756),("12개월",252),("6개월",126),("3개월",63)]
    rows=[]
    for lbl,n in ANCH:
        rows.append((lbl, cum(series["PRAMANA-A2"],n), cum(series["QQQ"],n), cum(series["SPY"],n), cum(series["TQQQ"],n), cum(naive_won,n)))
    # ── Vault (excess HWM·A2 vs QQQ·전체) ──
    a2ret=series["PRAMANA-A2"]/CAP-1; qqqret=series["QQQ"]/CAP-1; excess=float((a2ret-qqqret).iloc[-1])
    state=loadj(STATE,{});
    if "inception" not in state: state["inception"]=CFG["inception"]
    hwm=state.get("excess_hwm",0.0); hard=state.get("hard_vault",0.0); rel=state.get("reload_vault",0.0)
    if excess>hwm and excess>=0.04:
        rate=0.50 if excess>=0.12 else 0.25
        mv=(excess-hwm)*CAP*rate; hard+=mv*CFG["vault"]["hard_ratio"]; rel+=mv*CFG["vault"]["reload_ratio"]
    if excess>hwm: state["excess_hwm"]=excess
    state["hard_vault"]=hard; state["reload_vault"]=rel
    # ── 현재 상태 ──
    cur_mode=modes.iloc[-1] if dyn else "base"; cur_lead=int(lead.iloc[-1]); cur_decay=bool(decay.iloc[-1])
    leadlbl=("RED" if cur_lead>ymax else "YELLOW" if cur_lead>gmax else "GREEN")
    beta_expo=cur[0]*1+cur[1]*3; a2_won=float(series["PRAMANA-A2"].iloc[-1]); tot=a2_won/CAP-1
    qqq_full=float(series["QQQ"].iloc[-1]/CAP-1); naive_full=float(naive_won.iloc[-1]/CAP-1)
    beat_qqq=tot>qqq_full; beat_naive=tot>naive_full
    today=str(latest.date())
    state.update({"last_run":today,"a2_won":a2_won,"total_ret":tot,"excess_vs_qqq":excess,"mode":cur_mode,"lead_score":cur_lead,"lead":leadlbl,
                  "decay":cur_decay,"qqq_w":round(float(cur[0]),3),"tqqq_w":round(float(cur[1]),3),"beta_expo":round(float(beta_expo),2),
                  "data_source":DATASRC,"beat_qqq":beat_qqq,"beat_naive":beat_naive,"dynamic":dyn}); json.dump(state,open(STATE,"w"),indent=2)
    pd.DataFrame([{"date":today,"a2_won":a2_won,"excess":excess,"mode":cur_mode,"lead":leadlbl}]).to_csv(LOG,mode="a",header=not os.path.exists(LOG),index=False)
    # ── 대시보드 ──
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,3.9)); COL={"PRAMANA-A2":"#22d3ee","QQQ":"#a78bfa","SPY":"#f59e0b","TQQQ":"#ec4899"}
    for k in ["TQQQ","QQQ","SPY","PRAMANA-A2"]:
        plt.plot(series[k].index,series[k]/1e8,label=k,lw=2.6 if k=="PRAMANA-A2" else 1.3,color=COL[k],ls="-" if k=="PRAMANA-A2" else "--")
    try: plt.axvline(pd.Timestamp(state["inception"]),color="#475569",ls=":",lw=1); plt.text(pd.Timestamp(state["inception"]),plt.ylim()[1]*0.95,"라이브 시작",color="#94a3b8",fontsize=7)
    except: pass
    plt.legend(framealpha=.2); plt.title("PRAMANA A2 vs QQQ·SPY·TQQQ — 계좌금액(₩1억 시작·시작월 평균 정규화)",color="#e5e7eb"); plt.ylabel("계좌금액(억원)")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    def won(x): return f"₩{x/1e8:.3f}억"
    rc={"GREEN":"#34d399","YELLOW":"#fbbf24","RED":"#f87171"}[leadlbl]; mc={"base":"#34d399","red_king":"#fbbf24","attack_lockout":"#fb923c","crash_lockout":"#f87171","berserker":"#22d3ee"}.get(cur_mode,"#94a3b8")
    arows="".join(f'<tr><td>{l}</td><td class=cyan>{a:+.1f}%</td><td class=viol>{q:+.1f}%</td><td class=amber>{s:+.1f}%</td><td class=pink>{t:+.1f}%</td><td>{nv:+.1f}%</td></tr>' for l,a,q,s,t,nv in rows)
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A2 v2 Live</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.3em}}
.badge{{border-radius:6px;padding:2px 9px;font-size:.66em;font-weight:700}} .bm{{background:#5b21b6;color:#ddd6fe}} .bp{{background:#1e3a8a;color:#bfdbfe}} .bw{{background:#064e3b;color:#6ee7b7}}
.kpis{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}} .kpi{{flex:1;min-width:100px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:11px 13px}}
.kpi .l{{color:#94a3b8;font-size:.7em}} .kpi .v{{font-size:1.22em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.03em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:18px}} .pos{{color:#34d399}} .neg{{color:#f87171}}
table{{width:100%;border-collapse:collapse;font-size:.84em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 9px}} td{{padding:5px 9px;border-top:1px solid #1a2540}}
.cyan{{color:#22d3ee}}.viol{{color:#a78bfa}}.amber{{color:#f59e0b}}.pink{{color:#ec4899}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:11px 14px;color:#fde68a;font-size:.82em}}
.verdict{{padding:10px 14px;border-radius:10px;font-weight:700;margin:8px 0}}</style></head><body>
<div class=wrap><h1>🟣 PRAMANA A2 v2 — Convex Raider<span class="badge bm">CONVEX</span><span class="badge bp">PAPER</span><span class="badge bw">가상 ₩1억</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·데이터={DATASRC}·동적모드 {'ON' if dyn else 'OFF'}·현재 <b style="color:{mc}">{cur_mode}</b>(QQQ {cur[0]*100:.0f}%/TQQQ {cur[1]*100:.0f}%)·실질 beta ≈ {beta_expo:.2f}x. 검증된 알파 아님 — QQQ를 *크게 이길 확률*을 사는 book.</p>
<div class=kpis>
<div class=kpi><div class=l>A2 계좌</div><div class="v {'pos' if tot>=0 else 'neg'}">{won(a2_won)}</div></div>
<div class=kpi><div class=l>총수익</div><div class="v {'pos' if tot>=0 else 'neg'}">{tot*100:+.1f}%</div></div>
<div class=kpi><div class=l>QQQ(풀)</div><div class="v">{qqq_full*100:+.1f}%</div></div>
<div class=kpi><div class=l>vs QQQ</div><div class="v {'pos' if excess>=0 else 'neg'}">{excess*100:+.1f}%p</div></div>
<div class=kpi><div class=l>regime</div><div class="v" style="color:{mc}">{cur_mode}</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<div class="verdict" style="background:{'#0a1f17' if (beat_qqq and beat_naive) else '#1a0e0e'};border:1px solid {'#16a34a' if (beat_qqq and beat_naive) else '#7f1d1d'}">
{'✅' if beat_qqq else '❌'} vs QQQ ({tot*100:+.1f}% vs {qqq_full*100:+.1f}%) · {'✅' if beat_naive else '❌'} vs naive beta book ({naive_full*100:+.1f}%) — <b>판정선: 둘 다 이겨야 A2가 의미. 12개월 내 못 이기면 종료(무한루프 방지).</b></div>
<h2>📈 진입 시점별 성과 (3년/12/6/3개월·계좌금액 기준)</h2>
<div class=card><table><tr><th>진입</th><th class=cyan>A2</th><th class=viol>QQQ</th><th class=amber>SPY</th><th class=pink>TQQQ</th><th>naive</th></tr>{arows}</table></div>
<h2>🚦 Risk Dashboard <span style="color:#64748b;font-size:.7em">(정보용·자동매도 금지·신규/증액 게이트)</span></h2>
<div class=card><b>현재 모드:</b> <span style="color:{mc};font-weight:700">{cur_mode}</span> → QQQ {cur[0]*100:.0f}% / TQQQ {cur[1]*100:.0f}% (나머지 cash·Attack/Moonshot 비어있음)<br>
<b>Leadership:</b> <span style="color:{rc};font-weight:700">{leadlbl}</span> ({cur_lead}/30·메가캡 10종)·<b>TQQQ Decay:</b> <span style="color:{'#f87171' if cur_decay else '#34d399'}">{'DECAY ZONE' if cur_decay else 'OK'}</span>·<b>Beta Governor:</b> {beta_expo:.2f}x<br>
<b>Profit Vault:</b> excess HWM {state['excess_hwm']*100:.1f}%p · Hard {won(hard)} / Reload {won(rel)} (excess +4/+8/+12%p에서 25/25/50% 잠금·forward 초기엔 0)</div>
<h2>⚔️ Attack / 🚀 Moonshot <span style="color:#64748b;font-size:.7em">(2단계 연료·현재 비어있음=cash)</span></h2>
<div class=card style="color:#94a3b8;font-size:.85em">Attack {len(attack)}건 / Moonshot {len(moon)}건. <b style="color:#fbbf24">⚠️ 둘 다 비면 A2는 사실상 QQQ/TQQQ beta book</b> — 연료(폐기표 부활 판정·thesis)가 들어가야 진짜 convex.</div>
<div class=warn>⚠️ PAPER·NO LIVE·가상 ₩1억. 검증된 알파 아님·고위험 convex book. TQQQ=Booster(Core 아님). 동적모드=마켓타이밍 실험(config로 ON/OFF). 기존 TQQQ 자동매도 안 함(폭락 시 사람 게이트). 물타기 금지·이길 때만 피라미딩·NEG Gate 필수. V7/A1과 독립 평가.<br>설계=PRAMANA_V4/PRAMANA_A2_Convex_Raider_Book_FINAL_v2.md · cron: <code>10 6 * * 2-6 ... a2_live_runner.py</code></div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ A2 v2 {today}·계좌 {won(a2_won)}({tot*100:+.1f}%)·QQQ{qqq_full*100:+.1f}%·excess{excess*100:+.1f}%p·mode {cur_mode}(QQQ{cur[0]*100:.0f}/TQQQ{cur[1]*100:.0f})·Lead {leadlbl}({cur_lead}/30)·beat QQQ:{beat_qqq} naive:{beat_naive}·{DATASRC}")
if __name__=="__main__": main()
