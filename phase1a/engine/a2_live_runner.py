#!/usr/bin/env python3
"""PRAMANA A2 v3 — Convex Raider (discretionary-systematic hybrid·가상 ₩1억).
듀얼 추적: A2-T(QQQ/TQQQ 동적) vs A2-Q(TQQQ 없음·QQQ 중심) → TQQQ가 횡보 decay 넘는 값을 하나 데이터 판정.
동적 allocator(Leadership/Decay→모드→비중 천이 10%p/일·position-sizing alpha) + Profit Vault(alpha-timing·In/Out) + naive 판정선.
Attack/Moonshot = positions ledger(2단계 연료·현재 cash). 대시보드: y=계좌금액(₩1억·첫 거래일 종가 기준·Codex #6)·비교 A2-T/A2-Q/QQQ/SPY/TQQQ.
PAPER·자본0·V7/A1 독립. 사용: python engine/a2_live_runner.py [--dry]"""
import os, sys, json, datetime as dt, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kfont import set_korean_font; set_korean_font()
import a2_attack_ledger as AL, a2_moonshot_ledger as ML   # Phase B #4: forward sleeve 회계
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); REPO=os.path.dirname(ROOT)
A2=os.path.join(ROOT,"outputs","a2_live"); POS=os.path.join(A2,"positions"); os.makedirs(POS,exist_ok=True)
PRICES=os.path.join(A2,"prices.csv"); STATE=os.path.join(A2,"state.json"); LOG=os.path.join(A2,"nav_log.csv")
DASH=os.path.join(ROOT,"outputs","a2_live_dashboard.html"); KEY=os.path.join(ROOT,".ndl_key")
CFG_PATH=os.path.join(REPO,"config","a2_convex_raider.yaml")
DEFAULT_CFG={"capital":100_000_000,"inception":"2026-05-12","dynamic_mode_enabled":True,
 "allocation_a2t":{"base":{"qqq":.35,"tqqq":.35},"berserker":{"qqq":.30,"tqqq":.45},"red_king":{"qqq":.40,"tqqq":.25},"attack_lockout":{"qqq":.35,"tqqq":.35},"crash_lockout":{"qqq":.35,"tqqq":.10}},
 "allocation_a2q":{"base":{"qqq":.55,"tqqq":0.0},"berserker":{"qqq":.60,"tqqq":0.0},"red_king":{"qqq":.40,"tqqq":0.0},"attack_lockout":{"qqq":.55,"tqqq":0.0},"crash_lockout":{"qqq":.30,"tqqq":0.0}},
 "daily_max_shift_pp":.10,"leadership":{"green_max":10,"yellow_max":20},"tqqq_decay":{"qqq_20d_range":.03,"vol_threshold":.25},
 "vault":{"base_pct":.10,"vault_in":{"excess_pp":.04},"thresholds":[{"excess":.04,"rate":.25},{"excess":.08,"rate":.25},{"excess":.12,"rate":.50}],"hard_ratio":.70,"reload_ratio":.30},
 "naive_benchmark":{"qqq":.35,"tqqq":.35},"verdict":{"horizon_months":12,"must_beat":["naive","qqq","a2q"]}}
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
    px=px[[c for c in (BETA+LEADERS) if c in px.columns]].dropna()
    qr=px["QQQ"].pct_change().fillna(0); tr=px["TQQQ"].pct_change().fillna(0)
    # ── Risk Dashboard 시계열 ──
    qmom=px["QQQ"].pct_change(21); lead=pd.Series(0.0,index=px.index)
    for t in LEADERS:
        if t not in px.columns: continue
        lead=lead+(px[t]<px[t].rolling(20).mean()).astype(int)+(px[t]<px[t].rolling(50).mean()).astype(int)+(px[t].pct_change(21)<qmom).astype(int)
    gmax=CFG["leadership"]["green_max"]; ymax=CFG["leadership"]["yellow_max"]
    q20ret=px["QQQ"].pct_change(20); q20vol=px["QQQ"].pct_change().rolling(20).std()*np.sqrt(252)
    decay=(q20ret.abs()<CFG["tqqq_decay"]["qqq_20d_range"])&(q20vol>CFG["tqqq_decay"]["vol_threshold"])
    def mode_of(l,d): return "attack_lockout" if l>ymax else ("red_king" if (l>gmax or d) else "base")
    mds=[mode_of(lead.iloc[i],bool(decay.iloc[i])) for i in range(len(px))]
    dyn=CFG.get("dynamic_mode_enabled",True); shift=CFG["daily_max_shift_pp"]; qa=qr.values; ta=tr.values
    # ── 듀얼 동적 allocator ──
    qqq_cum_s=(1+qr).cumprod(); qma20=px["QQQ"].rolling(20).mean()   # excess HWM·Vault Out 조건용
    def run_book(aw, vault_on=False, use_dyn=None):   # next-bar(shift1) + Vault ledger(In: 노출 차감 / Out: Reload 재투입) + weekly 제한 + dynamic ablation
        udyn=(dyn if use_dyn is None else use_dyn); wcap=CFG.get("weekly_max_shift_pp",0.10)
        qw=aw["base"]["qqq"]; tw=aw["base"].get("tqqq",0.0); vlt=CFG["vault"]["base_pct"]; hard=0.0; rel=0.0
        nav=1.0; out=[]; hwm=0.0; last_v=-99; m_moved=0.0; w_moved=0.0; cur_mo=None; cur_wk=None
        for i in range(len(qa)):
            mo=px.index[i].to_period("M"); wk=int(px.index[i].isocalendar()[1])
            if mo!=cur_mo: cur_mo=mo; m_moved=0.0
            if wk!=cur_wk: cur_wk=wk; w_moved=0.0
            m=(mds[i-2] if (udyn and i>1) else "base"); mw=aw.get(m,aw["base"])   # close-only 보수적 next-bar(Codex #1): 신호 close_{t-2} → close_{t-1}→close_t 적용 = same-close 제거
            dq=float(np.clip(mw["qqq"]-qw,-shift,shift)); dt=float(np.clip(mw.get("tqqq",0.0)-tw,-shift,shift))
            mag=abs(dq)+abs(dt); room=max(0.0,wcap-w_moved)
            if mag>room and mag>1e-12: dq*=room/mag; dt*=room/mag   # weekly 10%p 제한
            qw+=dq; tw+=dt; w_moved+=abs(dq)+abs(dt)
            nav*=(1+qw*qa[i]+tw*ta[i]); out.append(nav)   # Vault·cash = 0 수익(노출 밖)
            if vault_on:
                excess=(nav-1)-(float(qqq_cum_s.iloc[i])-1)
                if excess>hwm and excess>=0.04 and nav>1.0 and (i-last_v>=5) and m_moved<0.10:   # Vault In
                    rate=0.50 if excess>=0.12 else 0.25; mv=min((excess-hwm)*rate,0.10-m_moved)
                    tot=qw+tw
                    if tot>1e-9: qw-=mv*qw/tot; tw-=mv*tw/tot   # 노출에서 Vault로 차감
                    vlt+=mv; hard+=mv*0.70; rel+=mv*0.30; hwm=excess; last_v=i; m_moved+=mv
                elif rel>1e-9 and i>0 and lead.iloc[i-1]<=CFG["leadership"]["green_max"] and (not bool(decay.iloc[i-1])) and px["QQQ"].iloc[i-1]>qma20.iloc[i-1]:   # Vault Out: Reload 25%씩 재투입(위험↓+기회)
                    ow=rel*0.25; tq=mw["qqq"]; tt=mw.get("tqqq",0.0); s2=tq+tt
                    if s2>0: qw+=ow*tq/s2; tw+=ow*tt/s2
                    rel-=ow; vlt-=ow   # Reload만 재투입·Hard는 영구 잠금
        return pd.Series(out,index=px.index),(qw,tw),{"vlt":vlt,"hard":hard,"rel":rel,"hwm":hwm}
    a2t,a2t_cur,a2t_v=run_book(CFG["allocation_a2t"],False); a2q,a2q_cur,a2q_v=run_book(CFG["allocation_a2q"],False)   # 백테스트 Vault OFF(장기 누적 excess→비중 과다=단위 부적합·Vault는 forward live ledger=Phase A로 분리)
    a2t_off,_,_=run_book(CFG["allocation_a2t"],False,use_dyn=False)   # ablation: dynamic OFF
    nb=CFG["naive_benchmark"]; naive=(1+nb["qqq"]*qr+nb["tqqq"]*tr).cumprod()
    def to_won(s):   # ★ Codex #3: 첫 거래일 종가 기준(look-ahead 없음). 차트 시작=₩1억. (월평균 정규화는 미래 월중가 참조라 폐기)
        s=s.dropna(); return CAP*s/s.iloc[0]
    S={"A2-T":to_won(a2t),"A2-Q":to_won(a2q),"QQQ":to_won(px["QQQ"]),"SPY":to_won(px["SPY"]),"TQQQ":to_won(px["TQQQ"])}; naive_won=to_won(naive)
    def fullret(s): return float(s.iloc[-1]/CAP-1)
    a2t_r=fullret(S["A2-T"]); a2q_r=fullret(S["A2-Q"]); qqq_r=fullret(S["QQQ"]); naive_r=fullret(naive_won)
    excess=a2t_r-qqq_r; decay_drag=a2t_r-a2q_r; a2t_off_r=fullret(to_won(a2t_off)); dyn_contrib=a2t_r-a2t_off_r   # 동적 allocator 순수 기여(ON−OFF)   # TQQQ 순기여(+면 TQQQ 값함·−면 decay가 잡아먹음)
    # ── 멀티앵커 ──
    def cum(s,n): s=s.dropna(); seg=s.iloc[-min(n,len(s)):]; return (seg.iloc[-1]/seg.iloc[0]-1)*100
    ANCH=[("3년",756),("12개월",252),("6개월",126),("3개월",63)]
    rows=[(l,cum(S["A2-T"],n),cum(S["A2-Q"],n),cum(S["QQQ"],n),cum(S["SPY"],n),cum(S["TQQQ"],n),cum(naive_won,n)) for l,n in ANCH]
    # ── Vault alpha-timing (In/Out 판정) ──
    state=loadj(STATE,{})
    if "inception" not in state: state["inception"]=CFG["inception"]
    incep=pd.Timestamp(state["inception"])
    def live_r(s):   # ★ Codex #2: live ledger = inception 이후만(백테스트 2016~와 분리)
        sl=s[s.index>=incep]; return float(sl.iloc[-1]/sl.iloc[0]-1) if len(sl)>1 else 0.0
    live_a2t=live_r(a2t); live_a2q=live_r(a2q); live_qqq=live_r(px["QQQ"]); live_days=int((px.index>=incep).sum())
    # ★ Phase A: forward Vault ledger (live excess HWM·vault.json append-only·Codex #2#3 — 백테스트 아닌 live만)
    VJ=os.path.join(POS,"vault.json"); vj=loadj(VJ,{"hard":0.0,"reload":0.0,"hwm":0.0,"last_date":None,"events":[]})
    live_excess=live_a2t-live_qqq
    if live_excess>vj["hwm"] and live_excess>=0.04 and live_a2t>0.0 and vj.get("last_date")!=today:   # HWM 갱신·절대수익(QQQ보다 덜잃은 것만으론 금지)·임계·일1회
        rate=0.50 if live_excess>=0.12 else 0.25; mvw=(live_excess-vj["hwm"])*rate
        vj["hard"]+=mvw*0.70; vj["reload"]+=mvw*0.30; vj["events"].append({"date":today,"live_excess":round(live_excess,4),"moved_w":round(mvw,4)}); vj["hwm"]=live_excess; vj["last_date"]=today
        json.dump(vj,open(VJ,"w"),indent=2)
    elif live_excess>vj["hwm"]: vj["hwm"]=live_excess; json.dump(vj,open(VJ,"w"),indent=2)
    hard=vj["hard"]*CAP; rel=vj["reload"]*CAP; vlt_w=vj["hard"]+vj["reload"]; state["excess_hwm"]=vj["hwm"]   # forward live Vault(백테스트 a2t_v는 OFF)
    # ★ Phase B #4: forward NAV sleeve 회계 (QQQ35+TQQQ35+Attack10+Moonshot10+Cash10·positions 차도 정확·빈슬롯=cash)
    def s_ret(t):
        sl=px[t][px.index>=incep]; return float(sl.iloc[-1]/sl.iloc[0]-1) if len(sl)>1 else 0.0
    fwd_qqq=CAP*0.35*(1+s_ret("QQQ")); fwd_tqqq=CAP*0.35*(1+s_ret("TQQQ"))
    _cur=lambda t: (float(px[t].dropna().iloc[-1]) if (t in px.columns and len(px[t].dropna())>0) else float("nan"))
    ae=AL.evaluate(attack,_cur,CAP*0.10); me=ML.evaluate(moon,_cur,CAP*0.10); fwd_cash=CAP*0.10
    fwd_nav=fwd_qqq+fwd_tqqq+ae["value"]+me["value"]+fwd_cash; fwd_ret=fwd_nav/CAP-1
    cur_lead=int(lead.iloc[-1]); cur_decay=bool(decay.iloc[-1]); cur_mode=mds[-1] if dyn else "base"
    leadlbl=("RED" if cur_lead>ymax else "YELLOW" if cur_lead>gmax else "GREEN")
    qqq_above_ma20=bool(px["QQQ"].iloc[-1]>px["QQQ"].rolling(20).mean().iloc[-1])
    vin=[]
    if excess>=CFG["vault"]["vault_in"].get("excess_pp",0.04): vin.append(f"A2-T가 QQQ +{excess*100:.0f}%p")
    if leadlbl!="GREEN": vin.append(f"Leadership {leadlbl}")
    if cur_decay: vin.append("TQQQ Decay")
    vout_ok = (leadlbl=="GREEN" and not cur_decay and qqq_above_ma20)
    beta_expo=a2t_cur[0]*1+a2t_cur[1]*3
    beat_qqq=a2t_r>qqq_r; beat_naive=a2t_r>naive_r; beat_a2q=a2t_r>a2q_r; today=str(latest.date())
    state.update({"last_run":today,"a2t_ret":a2t_r,"a2q_ret":a2q_r,"qqq_ret":qqq_r,"excess":excess,"decay_drag":decay_drag,"mode":cur_mode,
                  "lead":leadlbl,"decay":cur_decay,"beta_expo":round(float(beta_expo),2),"beat_qqq":beat_qqq,"beat_naive":beat_naive,"beat_a2q":beat_a2q,
                  "vault_in_signals":vin,"vault_out_ok":vout_ok,"data_source":DATASRC,"dynamic":dyn}); json.dump(state,open(STATE,"w"),indent=2)
    pd.DataFrame([{"date":today,"a2t":float(S["A2-T"].iloc[-1]),"a2q":float(S["A2-Q"].iloc[-1]),"excess":excess,"decay_drag":decay_drag,"mode":cur_mode}]).to_csv(LOG,mode="a",header=not os.path.exists(LOG),index=False)
    # ── 대시보드 ──
    plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
    f=plt.figure(figsize=(11,4.0)); COL={"A2-T":"#22d3ee","A2-Q":"#34d399","QQQ":"#a78bfa","SPY":"#f59e0b","TQQQ":"#ec4899"}
    for k in ["TQQQ","QQQ","SPY","A2-Q","A2-T"]:
        plt.plot(S[k].index,S[k]/1e8,label=k,lw=2.6 if k=="A2-T" else (2.0 if k=="A2-Q" else 1.2),color=COL[k],ls="-" if k.startswith("A2") else "--")
    try: plt.axvline(pd.Timestamp(state["inception"]),color="#475569",ls=":",lw=1)
    except: pass
    plt.legend(framealpha=.2,ncol=5,fontsize=8); plt.title("PRAMANA A2 — A2-T(TQQQ) vs A2-Q(no TQQQ) vs QQQ·SPY·TQQQ · 계좌금액(₩1억·첫거래일 기준)",color="#e5e7eb"); plt.ylabel("계좌금액(억원)")
    b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); ch=base64.b64encode(b.getvalue()).decode()
    def won(x): return f"₩{x/1e8:.3f}억"
    rc={"GREEN":"#34d399","YELLOW":"#fbbf24","RED":"#f87171"}[leadlbl]; mc={"base":"#34d399","red_king":"#fbbf24","attack_lockout":"#fb923c","crash_lockout":"#f87171","berserker":"#22d3ee"}.get(cur_mode,"#94a3b8")
    arows="".join(f'<tr><td>{l}</td><td class=cyan>{a:+.0f}%</td><td class=grn>{q:+.0f}%</td><td class=viol>{qq:+.0f}%</td><td class=amber>{s:+.0f}%</td><td class=pink>{t:+.0f}%</td><td>{nv:+.0f}%</td></tr>' for l,a,q,qq,s,t,nv in rows)
    dd_c="#34d399" if decay_drag>=0 else "#f87171"
    html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<meta http-equiv=refresh content=3600><title>PRAMANA A2 v3 Live</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI','Malgun Gothic',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1020px;margin:0 auto;padding:22px 18px 60px}} h1{{font-size:1.28em}}
.badge{{border-radius:6px;padding:2px 9px;font-size:.64em;font-weight:700}} .bm{{background:#5b21b6;color:#ddd6fe}} .bp{{background:#1e3a8a;color:#bfdbfe}} .bw{{background:#064e3b;color:#6ee7b7}}
.kpis{{display:flex;flex-wrap:wrap;gap:9px;margin:14px 0}} .kpi{{flex:1;min-width:95px;background:#0d1326;border:1px solid #1e293b;border-radius:12px;padding:10px 12px}}
.kpi .l{{color:#94a3b8;font-size:.68em}} .kpi .v{{font-size:1.18em;font-weight:800}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:15px;margin:10px 0}} img{{width:100%;border-radius:8px}}
h2{{font-size:1.02em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:18px}}
table{{width:100%;border-collapse:collapse;font-size:.82em}} th{{background:#111a30;color:#94a3b8;text-align:left;padding:6px 8px}} td{{padding:5px 8px;border-top:1px solid #1a2540}}
.cyan{{color:#22d3ee}}.grn{{color:#34d399}}.viol{{color:#a78bfa}}.amber{{color:#f59e0b}}.pink{{color:#ec4899}}.pos{{color:#34d399}}.neg{{color:#f87171}}
.verdict{{padding:10px 14px;border-radius:10px;font-weight:700;margin:8px 0}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:11px 14px;color:#fde68a;font-size:.8em}}</style></head><body>
<div class=wrap><h1>🟣 PRAMANA A2 v3 — Convex Raider<span class="badge bm">HYBRID</span><span class="badge bp">PAPER</span><span class="badge bw">가상 ₩1억</span></h1>
<p style='color:#94a3b8'>업데이트 {today}·데이터={DATASRC}·discretionary-systematic hybrid·동적 {'ON' if dyn else 'OFF'}·<b style="color:{mc}">{cur_mode}</b>·beta ≈ {beta_expo:.2f}x. 검증된 알파 아님.<br>
<b style="color:#fbbf24">⚠️ 아래 큰 수치 = 백테스트(2016~·강세장 편향·닷컴/2008 없음·next-bar 적용).</b> 라이브 paper(인셉션 {state['inception']}~·{live_days}거래일·sleeve 회계 #4): <b class=cyan>A2-T NAV ₩{fwd_nav/1e8:.3f}억({fwd_ret*100:+.1f}%)</b> [QQQ35+TQQQ35+Attack {ae['n']}건+Moon {me['n']}건+Cash10] · QQQ {live_qqq*100:+.1f}%.</p>
<div class=kpis>
<div class=kpi><div class=l>A2-T (TQQQ)</div><div class="v cyan">{a2t_r*100:+.0f}%</div></div>
<div class=kpi><div class=l>A2-Q (no TQQQ)</div><div class="v grn">{a2q_r*100:+.0f}%</div></div>
<div class=kpi><div class=l>QQQ</div><div class="v viol">{qqq_r*100:+.0f}%</div></div>
<div class=kpi><div class=l>TQQQ 순기여</div><div class="v" style="color:{dd_c}">{decay_drag*100:+.0f}%p</div></div>
<div class=kpi><div class=l>regime</div><div class="v" style="color:{mc};font-size:.95em">{cur_mode}</div></div></div>
<div class=card><img src="data:image/png;base64,{ch}"></div>
<div class="verdict" style="background:{'#0a1f17' if (beat_qqq and beat_naive and beat_a2q) else '#1a0e0e'};border:1px solid {'#16a34a' if (beat_qqq and beat_naive and beat_a2q) else '#7f1d1d'}">
{'✅' if beat_qqq else '❌'} vs QQQ · {'✅' if beat_naive else '❌'} vs naive · {'✅' if beat_a2q else '❌'} vs A2-Q(no TQQQ) — <b style="color:#f87171">동적 allocator v3 = REJECT</b> (2016~ benign·무비용서도 fixed 대비 {dyn_contrib*100:+.0f}%p) · TQQQ 순기여 {decay_drag*100:+.0f}%p · <span style="color:#94a3b8">"동적 마켓타이밍 일반 사망"까지 확장 금지(Codex #5)</span></div>
<h2>📈 진입 시점별 (3년/12/6/3개월·계좌금액 기준)</h2>
<div class=card><table><tr><th>진입</th><th class=cyan>A2-T</th><th class=grn>A2-Q</th><th class=viol>QQQ</th><th class=amber>SPY</th><th class=pink>TQQQ</th><th>naive</th></tr>{arows}</table></div>
<h2>🚦 Risk Dashboard <span style="color:#64748b;font-size:.7em">(정보용·신규/증액 게이트·LLM Council=2단계)</span></h2>
<div class=card><b>모드:</b> <span style="color:{mc};font-weight:700">{cur_mode}</span> (A2-T: QQQ {a2t_cur[0]*100:.0f}%/TQQQ {a2t_cur[1]*100:.0f}%)·<b>Leadership:</b> <span style="color:{rc};font-weight:700">{leadlbl}</span> ({cur_lead}/30)·<b>TQQQ Decay:</b> <span style="color:{'#f87171' if cur_decay else '#34d399'}">{'ZONE' if cur_decay else 'OK'}</span>·<b>Beta:</b> {beta_expo:.2f}x·<b>QQQ&gt;20일선:</b> {'예' if qqq_above_ma20 else '아니오'}</div>
<h2>💰 Profit Vault <span style="color:#64748b;font-size:.7em">(alpha-timing·표시용)</span></h2>
<div class=card>✅ <b style="color:#34d399">forward live Vault ledger</b>(Codex #2#3·positions/vault.json append-only): live excess(inception~) HWM·절대수익일 때만·Hard70/Reload30·Hard 재투입 금지. 백테스트(2016~)는 Vault OFF(장기 excess 단위 부적합). 노출차감/주1회/월10% run_book 로직 완성.<br>live excess HWM <b>{vj['hwm']*100:.2f}%p</b> · Hard {won(hard)} / Reload {won(rel)} · 이동 {len(vj['events'])}건 <span style="color:#64748b">(forward {live_days}거래일·excess 작아 현재 거의 0=정상)</span><br>
<b>Vault IN 신호:</b> {' · '.join(vin) if vin else '없음(아직 안 뺌)'}<br>
<b>Vault OUT(Reload) 가능:</b> <span style="color:{'#34d399' if vout_ok else '#94a3b8'}">{'예 (Leadership GREEN+Decay OK+QQQ&gt;20일선)' if vout_ok else '아니오 (위험 신호 잔존)'}</span> · Hard Vault는 영구 재투입 금지</div>
<h2>⚔️ Attack / 🚀 Moonshot <span style="color:#64748b;font-size:.7em">(2단계 연료·현재 cash)</span></h2>
<div class=card style="color:#94a3b8;font-size:.84em">Attack {len(attack)}건(분봉 day strategy·NEG는 size 축소/overnight 금지) / Moonshot {len(moon)}건(thesis+판정일 필수·NEG 금지). <b style="color:#fbbf24">⚠️ 비면 A2는 QQQ/TQQQ beta book</b></div>
<div class=warn>⚠️ PAPER·NO LIVE·₩1억. 검증 알파 아님·고위험 hybrid. TQQQ=Booster. 동적=position-sizing 실험(config ON/OFF). 폭락 시 기존 TQQQ 자동매도 안 함(사람 게이트). 물타기 금지. V7/A1 독립.<br>설계=PRAMANA_A2_Convex_Raider_Book_FINAL_v2.md · cron <code>10 6 * * 2-6 a2_live_runner.py</code></div>
</div></body></html>"""
    open(DASH,"w").write(html)
    print(f"✅ A2 v3 {today}·A2-T {a2t_r*100:+.0f}%(동적기여 {dyn_contrib*100:+.0f}%p)·A2-Q {a2q_r*100:+.0f}%·QQQ {qqq_r*100:+.0f}%·Vault잠김 {vlt_w*100:.1f}%·beat QQQ:{beat_qqq}/naive:{beat_naive}/A2-Q:{beat_a2q}·{DATASRC}")
if __name__=="__main__": main()
