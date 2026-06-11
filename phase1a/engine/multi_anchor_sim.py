#!/usr/bin/env python3
"""PRAMANA — 멀티시점 백테스트(3M/6M/1Y/풀사이클) × 레버 유무, SPY 단순보유 비교.
'왜 SPY보다 낮나'의 데이터 답: 단기 강세장에선 시장중립+디리스킹이 SPY에 짐(설계상).
풀사이클·위험조정(Sharpe)·낙폭(MDD)·레버로 보면 그림이 다르다 — 숫자가 말하게.
paper·gross + turnover기반 net추정(라벨 명시). dashboard.py와 동일 로직(재현)."""
import os, sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, universe as U
ENG=os.path.join(data.PHASE1A,"outputs","engine"); os.makedirs(ENG,exist_ok=True); CAP=100_000_000
LETF_MAP={"QQQ":"TQQQ","SPY":"UPRO"}; W=dict(eq=0.46,trend=0.50,letf=0.04)
BPS=dict(eq=30,trend=10)  # 단위 turnover당 비용(bp): equity 30bp·ETF 10bp(왕복), ×LEV 적용

# ── 데이터 (dashboard.py와 동일) ──
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
eqpx=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]
uni=U.rank_universe(1,1500); rebal=sorted(uni["asof"].unique())
mom=F.momentum(eqpx,rebal); qual=F.quality(sf1,rebal,eqpx.columns); EQ=F.event_subsignals(sf1x,rebal)
sma200=etf.rolling(200).mean()

def eq_frame(t):
    members=set(uni[uni["asof"]==t]["ticker"]); mem=[c for c in eqpx.columns if c in members]
    d=pd.DataFrame({"mom":mom.loc[t].reindex(mem),"qual":qual.loc[t].reindex(mem)})
    for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
    d["sec"]=sector.reindex(mem).values; d["ev"]=F.composite(d,F.EVENT_COLS); d=d.dropna(subset=["mom","qual","ev"])
    d["meta"]=pd.concat([F.zscore(d["mom"]),F.zscore(d["qual"]),F.zscore(d["ev"])],axis=1).mean(axis=1)
    d["sn"]=d["meta"]-d.groupby("sec")["meta"].transform("mean"); return d
def trend_on(t):
    a=etf.loc[:t].iloc[-1]; s=sma200.loc[:t].iloc[-1]
    on=[c for c in TT if pd.notna(s[c]) and a[c]>s[c]]; return set(on), {LETF_MAP[u] for u in LETF_MAP if u in on}

# ── SEG over all valid rebal dates ──
seg_dates=[t for t in rebal if t in mom.index and t>=etf.index[200]]
SEG={}
for t in seg_dates:
    d=eq_frame(t); rk=d["sn"].rank(pct=True); on,letf=trend_on(t)
    SEG[t]=dict(L=set(d.index[rk>=0.8]),S=set(d.index[rk<=0.2]),on=on,letf=letf)
sd=sorted(SEG)
turn={}
for i,t in enumerate(sd):
    if i==0: turn[t]=dict(eq=1.0,trend=1.0); continue
    A,B=SEG[sd[i-1]],SEG[t]
    turn[t]=dict(eq=(len(A["L"]^B["L"])+len(A["S"]^B["S"]))/max(1,len(B["L"])+len(B["S"])),
                 trend=len(A["on"]^B["on"])/max(1,len(TT)))
def applic(d):
    p=[t for t in sd if t<d]; return SEG[p[-1]] if p else None

etf_ret=etf.pct_change(); eq_ret=eqpx.pct_change(); days_all=etf.index.intersection(eqpx.index)
turn_set=set(turn)
def mret(rf,d,nm):
    nm=[c for c in nm if c in rf.columns]; return rf.loc[d,nm].mean() if (d in rf.index and nm) else 0.0

def run(start,end,LEV,cost=True):
    days=days_all[(days_all>=start)&(days_all<=end)]; nav=[CAP]; idx=[days[0]]
    for i in range(1,len(days)):
        d=days[i]; s=applic(d); r=0.0
        if s is not None:
            tr=mret(etf_ret,d,s["on"]); lf=mret(etf_ret,d,s["letf"]); eqd=mret(eq_ret,d,s["L"])-mret(eq_ret,d,s["S"])
            r=LEV*(W["eq"]*eqd+W["trend"]*tr+W["letf"]*lf)
            if cost and d in turn_set:
                r-=LEV*(turn[d]["eq"]*W["eq"]*BPS["eq"]+turn[d]["trend"]*W["trend"]*BPS["trend"])/1e4
        nav.append(nav[-1]*(1+r)); idx.append(d)
    return pd.Series(nav,index=idx)
def spy_nav(start,end):
    days=days_all[(days_all>=start)&(days_all<=end)]; s=etf["SPY"].reindex(days).ffill(); return CAP*s/s.iloc[0]
def stats(nav):
    r=nav.pct_change().dropna(); yrs=(nav.index[-1]-nav.index[0]).days/365.25
    tot=nav.iloc[-1]/nav.iloc[0]-1; cagr=(1+tot)**(1/yrs)-1 if yrs>0 and tot>-1 else float("nan")
    mdd=(nav/nav.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else float("nan")
    return dict(tot=tot,cagr=cagr,mdd=mdd,sh=sh,yrs=yrs)

end=days_all[-1]; full_start=days_all[days_all>=etf.index[210]][0]
ANCHORS=[("3M",end-pd.Timedelta(days=95)),("6M",end-pd.Timedelta(days=190)),
         ("1Y",end-pd.Timedelta(days=370)),("FULL",full_start)]
rows=[]
print(f"\n{'='*78}\nPRAMANA 멀티시점 vs SPY 단순보유 — 끝점 {end.date()} · 비용후(net,turnover기반)\n{'='*78}")
print(f"{'기간':<6}{'전략':<14}{'누적%':>9}{'CAGR%':>8}{'MDD%':>8}{'Sharpe':>8}   {'vs SPY(누적)':>12}")
for nm,start in ANCHORS:
    sp=spy_nav(start,end); ss=stats(sp)
    for lev,lab in [(1.0,"book 1x(무레버)"),(3.0,"book 3x(공격)")]:
        nav=run(start,end,lev,cost=True); st=stats(nav)
        rows.append(dict(anchor=nm,strat=lab,**{f"b_{k}":v for k,v in st.items()}))
        diff=(st["tot"]-ss["tot"])*100
        print(f"{nm:<6}{lab:<14}{st['tot']*100:>8.2f}{st['cagr']*100:>8.2f}{st['mdd']*100:>8.1f}{st['sh']:>8.2f}   {diff:>+11.2f}%p")
    print(f"{'':<6}{'SPY 단순보유':<14}{ss['tot']*100:>8.2f}{ss['cagr']*100:>8.2f}{ss['mdd']*100:>8.1f}{ss['sh']:>8.2f}   {'—':>12}")
    print(f"{'-'*78}")
pd.DataFrame(rows).to_csv(os.path.join(ENG,"multi_anchor.csv"),index=False)

# ── HTML (풀사이클 NAV + 표 + 정직 결론) ──
fs=full_start; navs={"book 3x":run(fs,end,3.0),"book 1x":run(fs,end,1.0),"SPY":spy_nav(fs,end)}
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
f=plt.figure(figsize=(11,4));
for k,c,w in [("book 3x","#22d3ee",2.4),("book 1x","#a78bfa",1.6),("SPY","#f59e0b",1.6)]:
    plt.plot(navs[k].index,navs[k]/CAP,label=k,color=c,lw=w,ls=("--" if k=="SPY" else "-"))
plt.legend(framealpha=.2); plt.yscale("log"); plt.title(f"Growth of ₩100M — full cycle {fs.date()}→{end.date()} (log)",color="#e5e7eb"); plt.ylabel("× initial")
b=io.BytesIO(); f.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(f); chart=base64.b64encode(b.getvalue()).decode()
def tr(nm,lab,st,ss):
    C=lambda v:'pos' if v>=0 else 'neg'; d=st['tot']-ss['tot']
    return f"<tr><td>{nm}</td><td>{lab}</td><td class='num {C(st['tot'])}'>{st['tot']*100:+.2f}%</td><td class='num'>{st['cagr']*100:+.2f}%</td><td class='num neg'>{st['mdd']*100:.1f}%</td><td class='num'>{st['sh']:+.2f}</td><td class='num {C(d)}'>{d*100:+.2f}%p</td></tr>"
trows=""
for nm,start in ANCHORS:
    sp=spy_nav(start,end); ss=stats(sp)
    for lev,lab in [(3.0,"book 3x"),(1.0,"book 1x")]:
        trows+=tr(nm,lab,stats(run(start,end,lev)),ss)
    C=lambda v:'pos' if v>=0 else 'neg'
    trows+=f"<tr style='background:#1a1206'><td>{nm}</td><td><b>SPY 단순보유</b></td><td class='num {C(ss['tot'])}'>{ss['tot']*100:+.2f}%</td><td class='num'>{ss['cagr']*100:+.2f}%</td><td class='num neg'>{ss['mdd']*100:.1f}%</td><td class='num'>{ss['sh']:+.2f}</td><td class='num'>—</td></tr>"
F3=stats(run(fs,end,3.0)); FS=stats(spy_nav(fs,end))
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PRAMANA 멀티시점 vs SPY</title><style>
body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.55}}
.wrap{{max-width:1000px;margin:0 auto;padding:24px 18px 60px}}
h1{{font-size:1.5em}} h2{{font-size:1.12em;border-left:4px solid #22d3ee;padding-left:10px;margin-top:28px}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:16px 18px;margin:10px 0}}
img{{width:100%;border-radius:10px}} table{{width:100%;border-collapse:collapse;font-size:.9em}}
th,td{{padding:7px 9px;border-bottom:1px solid #1e293b;text-align:left}} th{{color:#94a3b8;font-size:.82em}}
td.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#34d399}} .neg{{color:#f87171}}
.warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:14px 16px;color:#fde68a;font-size:.9em}}
.badge{{background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.72em;font-weight:700}}</style></head><body>
<div class=wrap><h1>📐 PRAMANA — 멀티시점 vs SPY 단순보유 <span class=badge>PAPER · 비용후(net)</span></h1>
<p style='color:#94a3b8'>같은 전략을 3개월·6개월·1년·풀사이클({fs.date()}~{end.date()}) 시점부터 돌려 SPY 단순보유와 비교. "왜 SPY보다 낮나"의 정직한 답.</p>
<h2>📈 풀사이클 성장곡선 (log)</h2><div class=card><img src="data:image/png;base64,{chart}"></div>
<h2>📊 시점별 비교 (전부 비용후)</h2><div class=card><table>
<tr><th>기간</th><th>전략</th><th class=num>누적</th><th class=num>CAGR</th><th class=num>MDD</th><th class=num>Sharpe</th><th class=num>vs SPY</th></tr>{trows}</table></div>
<div class=warn><b>정직한 결론:</b><br>
• <b>단기(3M·6M·강세장)에선 book이 SPY에 진다 — 설계상 당연하다.</b> equity sleeve가 시장중립(베타≈0)이고 추세 sleeve는 변동성↑때 디리스킹하니, 조용한 상승장에선 "그냥 SPY 100% 보유"를 못 이긴다.<br>
• <b>book의 값어치는 풀사이클·위험조정·낙폭에 있다.</b> 풀사이클 book 3x: 누적 {F3['tot']*100:+.0f}%·MDD {F3['mdd']*100:.0f}%·Sharpe {F3['sh']:+.2f} vs SPY 누적 {FS['tot']*100:+.0f}%·MDD {FS['mdd']*100:.0f}%·Sharpe {FS['sh']:+.2f}.<br>
• <b>레버는 양날.</b> 3x는 조용한 상승장에서 SPY를 앞지를 수 있지만 MDD도 키운다. "SPY를 이기려" 레버를 올리면 낙폭 한도와 충돌(승격 게이트 MDD≤15%).<br>
• <b>결론: 단기 강세장만 보면 SPY 단순보유가 낫다.</b> 이 전략은 "강세장 베팅"이 아니라 "전 구간 위험조정 + 하락 방어 + 레버 여력"을 사는 것이다. 둘 중 무엇을 원하는지가 먼저다.</div>
<p style='color:#64748b;font-size:.82em;margin-top:14px'>비용가정: 리밸런스시 turnover×(equity 30bp·ETF 10bp)×레버. 데이터 Sharadar(PIT·survivorship-safe·배당조정). 생성 multi_anchor_sim.py.</p>
</div></body></html>"""
open(os.path.join(data.PHASE1A,"outputs","multi_anchor.html"),"w").write(html)
print(f"\n✅ HTML → outputs/multi_anchor.html · CSV → outputs/engine/multi_anchor.csv")
print(f"   풀사이클({F3['yrs']:.1f}년) book3x: 누적{F3['tot']*100:+.0f}%·MDD{F3['mdd']*100:.0f}%·Sharpe{F3['sh']:+.2f}  |  SPY: 누적{FS['tot']*100:+.0f}%·MDD{FS['mdd']*100:.0f}%·Sharpe{FS['sh']:+.2f}")
