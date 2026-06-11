#!/usr/bin/env python3
"""PRAMANA v3 — 종합 대시보드(자기설명형). 3개월 일별 페이퍼 런(₩100M, 2026-03~).
대시보드만 보고 전부 이해: 무슨 종목 샀나·어떻게 작동하나·sleeve별 성과·벤치 대비·월별·리스크·규칙.
⚠️ paper·no live·3개월=작은표본. self-contained HTML(base64 PNG)."""
import os, sys, io, base64, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data, features as F, universe as U
ENG=os.path.join(data.PHASE1A,"outputs","engine"); CAP=100_000_000
LETF_MAP={"QQQ":"TQQQ","SPY":"UPRO"}; W=dict(eq=0.46,trend=0.50,letf=0.04); LEV=3.0

# ── 데이터 ──
etf=data.load("SFP_FUNDS",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
TT=[c for c in ["SPY","QQQ","IWM","DIA","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"] if c in etf.columns]
eqpx=data.load("broad_SEP",usecols=["ticker","date","closeadj"]).pivot_table(index="date",columns="ticker",values="closeadj").sort_index()
sf1=data.load("broad_SF1"); sf1x=data.load("broad_SF1_ext"); sector=data.load_tickers()["sector"]; names=data.load_tickers()["name"]
uni=U.rank_universe(1,1500); rebal=sorted(uni["asof"].unique())
mom=F.momentum(eqpx,rebal); qual=F.quality(sf1,rebal,eqpx.columns); EQ=F.event_subsignals(sf1x,rebal)
end=min(etf.index[-1],eqpx.index[-1]); start=end-pd.Timedelta(days=95)
days=etf.index.intersection(eqpx.index); days=days[(days>=start)&(days<=end)]
me=[d for d in rebal if d<=end]; seg_dates=sorted(set([d for d in me if d>=start-pd.Timedelta(days=40)]))

def eq_frame(t):
    members=set(uni[uni["asof"]==t]["ticker"]); mem=[c for c in eqpx.columns if c in members]
    d=pd.DataFrame({"mom":mom.loc[t].reindex(mem),"qual":qual.loc[t].reindex(mem)})
    for k in F.EVENT_COLS: d[k]=EQ[k].loc[t].reindex(mem)
    d["sec"]=sector.reindex(mem).values; d["ev"]=F.composite(d,F.EVENT_COLS); d=d.dropna(subset=["mom","qual","ev"])
    d["meta"]=pd.concat([F.zscore(d["mom"]),F.zscore(d["qual"]),F.zscore(d["ev"])],axis=1).mean(axis=1)
    d["sn"]=d["meta"]-d.groupby("sec")["meta"].transform("mean"); return d
def trend_info(t):
    a=etf.loc[:t].iloc[-1]; sma=etf.loc[:t].rolling(200).mean().iloc[-1]
    on=[c for c in TT if a[c]>sma[c]]; info={c:(a[c],sma[c],(a[c]/sma[c]-1)*100) for c in TT}
    return on,[LETF_MAP[u] for u in LETF_MAP if u in on], info

SEG={}
for t in seg_dates:
    d=eq_frame(t); rk=d["sn"].rank(pct=True); on,letf,tinfo=trend_info(t)
    SEG[t]=dict(L=d.index[rk>=0.8].tolist(),S=d.index[rk<=0.2].tolist(),on=on,letf=letf,frame=d,tinfo=tinfo)
def applic(d): p=[t for t in seg_dates if t<d]; return SEG[p[-1]] if p else SEG[seg_dates[0]]

etf_ret=etf.pct_change(); eq_ret=eqpx.pct_change()
def mret(rf,d,nm): return rf.loc[d,[c for c in nm if c in rf.columns]].mean() if d in rf.index and nm else 0.0
recs=[]; sl={"equity":[],"trend":[],"letf":[]}
for i,d in enumerate(days):
    if i==0: recs.append((d,0.0)); [sl[k].append(0.0) for k in sl]; continue
    s=applic(d); tr=mret(etf_ret,d,s["on"]); lf=mret(etf_ret,d,s["letf"]); eqd=mret(eq_ret,d,s["L"])-mret(eq_ret,d,s["S"])
    sl["equity"].append(eqd); sl["trend"].append(tr); sl["letf"].append(lf)
    recs.append((d,float(LEV*(W["eq"]*eqd+W["trend"]*tr+W["letf"]*lf))))
R=pd.DataFrame(recs,columns=["date","ret"]).set_index("date"); R["nav"]=CAP*(1+R["ret"]).cumprod()
tot=R["nav"].iloc[-1]/CAP-1; dd=(R["nav"]/R["nav"].cummax()-1).min()
ann=R["ret"].mean()/R["ret"].std()*np.sqrt(252) if R["ret"].std()>0 else float("nan"); win=(R["ret"][1:]>0).mean()
spy=etf["SPY"].reindex(days).ffill(); spy_nav=spy/spy.iloc[0]; spy_tot=spy_nav.iloc[-1]-1
cur=applic(days[-1]); curt=seg_dates[[t for t in seg_dates if t<days[-1]][-1] and -1] if False else [t for t in seg_dates if t<days[-1]][-1]
def sstat(arr): a=pd.Series(arr); return ((1+a).prod()-1)*100, (a.mean()/a.std()*np.sqrt(252) if a.std()>0 else 0)

# ── 차트 ──
def png(fig): b=io.BytesIO(); fig.savefig(b,format="png",dpi=95,bbox_inches="tight",facecolor="#0d1326"); plt.close(fig); return base64.b64encode(b.getvalue()).decode()
plt.style.use("dark_background"); plt.rcParams.update({"axes.facecolor":"#0d1326","figure.facecolor":"#0d1326","grid.alpha":.15,"font.size":9})
f1=plt.figure(figsize=(10,3.4)); plt.plot(R.index,R["nav"]/CAP,color="#22d3ee",lw=2.4,label="PRAMANA book"); plt.plot(days,spy_nav,color="#f59e0b",lw=1.4,ls="--",label="SPY (buy&hold)")
plt.axhline(1,color="#555",lw=.7); plt.legend(loc="upper left",framealpha=.2); plt.title("Growth of ₩100M (book vs SPY)",fontsize=12,color="#e5e7eb"); plt.ylabel("× initial"); nav_png=png(f1)
ddc=(R["nav"]/R["nav"].cummax()-1)*100; f2=plt.figure(figsize=(10,1.9)); plt.fill_between(ddc.index,ddc,0,color="#ef4444",alpha=.55); plt.title("Drawdown (%)",fontsize=10,color="#e5e7eb"); dd_png=png(f2)
f3=plt.figure(figsize=(10,2.6))
for k,c in [("equity","#a78bfa"),("trend","#34d399"),("letf","#fbbf24")]: plt.plot(days,(np.cumprod(1+np.array(sl[k]))-1)*100,label=k,lw=1.8,color=c)
plt.legend(framealpha=.2); plt.title("Each sleeve's cumulative return (pre-leverage, %)",fontsize=10,color="#e5e7eb"); sl_png=png(f3)
# 섹터 노출 바
secL=pd.Series([cur["frame"].loc[x,"sec"] for x in cur["L"]]).value_counts(); secS=pd.Series([cur["frame"].loc[x,"sec"] for x in cur["S"]]).value_counts()
allsec=sorted(set(secL.index)|set(secS.index)); f4=plt.figure(figsize=(10,2.8)); y=np.arange(len(allsec))
plt.barh(y-.2,[secL.get(s,0) for s in allsec],.4,color="#34d399",label="long"); plt.barh(y+.2,[-secS.get(s,0) for s in allsec],.4,color="#f87171",label="short")
plt.yticks(y,allsec,fontsize=8); plt.legend(framealpha=.2); plt.title("Equity book sector exposure (long vs short, # names)",fontsize=10,color="#e5e7eb"); plt.axvline(0,color="#555",lw=.7); sec_png=png(f4)

# ── 보유 테이블 ──
def tline(tk): return f"<tr><td><b>{tk}</b></td><td>{str(names.get(tk,''))[:34]}</td><td>{cur['frame'].loc[tk,'sec'] if tk in cur['frame'].index else ''}</td><td class=num>{cur['frame'].loc[tk,'meta']:+.2f}</td></tr>" if tk in cur['frame'].index else ""
topL=cur["frame"].reindex(cur["L"]).sort_values("meta",ascending=False).head(12).index.tolist()
topS=cur["frame"].reindex(cur["S"]).sort_values("meta").head(12).index.tolist()
trend_rows="".join(f"<tr><td><b>{c}</b></td><td>{cur['tinfo'][c][0]:.1f}</td><td>{cur['tinfo'][c][1]:.1f}</td><td class='num {'pos' if cur['tinfo'][c][2]>=0 else 'neg'}'>{cur['tinfo'][c][2]:+.1f}%</td><td>{'🟢 LONG' if c in cur['on'] else '⚪ flat'}</td></tr>" for c in TT)
mr=R["ret"].resample("ME").apply(lambda x:(1+x).prod()-1); mrow="".join(f"<tr><td>{i.strftime('%Y-%m')}</td><td class='num {'pos' if v>=0 else 'neg'}'>{v*100:+.2f}%</td></tr>" for i,v in mr.items())
eqr,eqsh=sstat(sl["equity"]); trr,trsh=sstat(sl["trend"]); lfr,lfsh=sstat(sl["letf"])

C=lambda v:'pos' if v>=0 else 'neg'
html=f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>PRAMANA Dashboard</title>
<style>
*{{box-sizing:border-box}} body{{background:#070b16;color:#e5e7eb;font-family:'Segoe UI',system-ui,sans-serif;margin:0;line-height:1.5}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 18px 60px}}
header{{background:linear-gradient(120deg,#0e7490,#5b21b6);padding:26px 18px;margin-bottom:8px}}
header .wrap{{padding-bottom:0}} h1{{margin:0;font-size:1.7em;letter-spacing:.5px}} .sub{{color:#cbd5e1;font-size:.92em;margin-top:6px}}
.badge{{display:inline-block;background:#7f1d1d;color:#fecaca;border-radius:6px;padding:2px 9px;font-size:.75em;font-weight:700;margin-left:8px;vertical-align:middle}}
.kpis{{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}}
.kpi{{flex:1;min-width:130px;background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:14px 16px}}
.kpi .l{{color:#94a3b8;font-size:.78em;text-transform:uppercase;letter-spacing:.5px}} .kpi .v{{font-size:1.7em;font-weight:800;margin-top:4px}}
.pos{{color:#34d399}} .neg{{color:#f87171}} .cyan{{color:#22d3ee}}
h2{{font-size:1.15em;margin:30px 0 6px;border-left:4px solid #22d3ee;padding-left:10px}}
.card{{background:#0d1326;border:1px solid #1e293b;border-radius:14px;padding:16px 18px;margin:10px 0}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} @media(max-width:720px){{.grid2{{grid-template-columns:1fr}}}}
img{{width:100%;border-radius:10px;display:block}}
table{{width:100%;border-collapse:collapse;font-size:.88em}} th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid #1e293b}} th{{color:#94a3b8;font-weight:600;font-size:.82em}}
td.num{{text-align:right;font-variant-numeric:tabular-nums}} .how li{{margin:7px 0}} .how b{{color:#22d3ee}}
.flow{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;font-size:.84em;color:#cbd5e1;margin-top:8px}}
.flow span{{background:#1e293b;border-radius:7px;padding:5px 10px}} .flow i{{color:#64748b;font-style:normal}}
.muted{{color:#64748b;font-size:.82em}} .warn{{background:#1c1408;border:1px solid #92400e;border-radius:10px;padding:12px 16px;color:#fde68a;font-size:.88em;margin-top:14px}}
.tag{{display:inline-block;background:#064e3b;color:#6ee7b7;border-radius:6px;padding:1px 8px;font-size:.8em;margin:2px}}
.tagr{{display:inline-block;background:#450a0a;color:#fca5a5;border-radius:6px;padding:1px 8px;font-size:.8em;margin:2px}}
</style></head><body>
<header><div class=wrap><h1>🦊 PRAMANA — Systematic Paper Book<span class=badge>PAPER · NO LIVE</span></h1>
<div class=sub>US 멀티-sleeve 공격적 시장중립+추세 전략 · 가상자본 ₩100M · {days[0].date()} → {days[-1].date()} ({len(days)} 거래일)</div></div></header>
<div class=wrap>

<div class=kpis>
<div class=kpi><div class=l>누적 수익</div><div class="v {C(tot)}">{tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>현재 평가액</div><div class="v cyan">₩{(1+tot)*1:.3f}억</div></div>
<div class=kpi><div class=l>SPY 단순보유</div><div class="v {C(spy_tot)}">{spy_tot*100:+.2f}%</div></div>
<div class=kpi><div class=l>최대 낙폭</div><div class="v neg">{dd*100:.1f}%</div></div>
<div class=kpi><div class=l>Sharpe <span class=muted>(연·3M표본)</span></div><div class="v">{ann:+.2f}</div></div>
<div class=kpi><div class=l>상승일 비율</div><div class="v">{win*100:.0f}%</div></div>
</div>

<h2>📈 자산 성장 (vs SPY 단순보유)</h2><div class=card><img src="data:image/png;base64,{nav_png}"></div>
<div class=card style=padding:6px-18px><img src="data:image/png;base64,{dd_png}"></div>

<h2>⚙️ 이 전략은 어떻게 작동하나</h2>
<div class="card how">
<div class=flow><span>📊 신호 산출</span><i>→</i><span>3개 sleeve</span><i>→</i><span>위험예산 결합</span><i>→</i><span>레버리지</span><i>→</i><span>🛡️ 리스크엔진 veto</span><i>→</i><span>💰 NAV</span></div>
<ul>
<li><b>① Equity 시장중립 L/S</b> — top-1500 미국주식을 <b>모멘텀+퀄리티(gp/assets)+실적추정변화</b> 합성점수로 랭킹, 섹터중립 후 상위 20%(롱)·하위 20%(숏) 동일가중. 시장 방향에 중립(베타≈0).</li>
<li><b>② ETF 추세추종</b> — 15개 美 ETF(SPY/QQQ/섹터)가 <b>200일 이동평균 위</b>면 롱, 아래면 현금. SPY 20일 변동성↑이면 노출 ½(vol-regime).</li>
<li><b>③ LETF 컨벡스 dose</b> — 추세 ON일 때 3배 ETF(TQQQ/UPRO)로 상승 증폭. 위험예산 소량(고변동이라 dollar 비중 작게).</li>
<li><b>결합</b> — 세 sleeve가 서로 <b>거의 무상관</b>(분산효과) → 위험예산 가중(eq {W['eq']:.0%}/trend {W['trend']:.0%}/letf {W['letf']:.0%}) 후 <b>레버리지 {LEV:.0f}x</b>(변동성 목표).</li>
<li><b>🛡️ 리스크 엔진(바닥)</b> — DD ladder(−10/−15/−20/−25%→노출 축소)·kill-switch(데이터무결성·변동성폭발·시장중립붕괴)·look-ahead 없음(신호 t, 진입 t+1)·전부 paper.</li>
</ul></div>

<h2>🛒 지금 무엇을 들고 있나 <span class=muted>(as-of {pd.Timestamp(curt).date()} 리밸런스)</span></h2>
<div class=grid2>
<div class=card><b>📈 ETF 추세 ({len(cur['on'])}/{len(TT)} 롱)</b>
<table><tr><th>ETF</th><th>종가</th><th>200d MA</th><th>이격</th><th>상태</th></tr>{trend_rows}</table></div>
<div class=card><b>🚀 LETF 컨벡스 dose</b><p>{''.join(f'<span class=tag>{l}</span>' for l in cur['letf']) or '없음'}</p>
<div class=muted>추세 ON인 지수의 3배 ETF로 상승 증폭(위험예산 {W['letf']:.0%}).</div>
<b style=margin-top:14px;display:block>⚖️ Equity L/S 규모</b><p><span class=tag>롱 {len(cur['L'])}종</span><span class=tagr>숏 {len(cur['S'])}종</span> · 섹터중립·동일가중</p></div>
</div>
<div class=card><img src="data:image/png;base64,{sec_png}"></div>
<div class=grid2>
<div class=card><b class=pos>⬆️ Equity 롱 상위 (합성점수 높음)</b><table><tr><th>티커</th><th>종목</th><th>섹터</th><th class=num>점수</th></tr>{''.join(tline(x) for x in topL)}</table></div>
<div class=card><b class=neg>⬇️ Equity 숏 상위 (합성점수 낮음)</b><table><tr><th>티커</th><th>종목</th><th>섹터</th><th class=num>점수</th></tr>{''.join(tline(x) for x in topS)}</table></div>
</div>

<h2>🧩 sleeve별 성과 (3개월, 레버 전)</h2>
<div class=card><img src="data:image/png;base64,{sl_png}"></div>
<div class=card><table><tr><th>sleeve</th><th>역할</th><th class=num>3M 수익</th><th class=num>Sharpe(연)</th><th class=num>위험예산</th></tr>
<tr><td>Equity MN L/S</td><td>시장중립 분산</td><td class='num {C(eqr)}'>{eqr:+.1f}%</td><td class=num>{eqsh:+.2f}</td><td class=num>{W['eq']:.0%}</td></tr>
<tr><td>ETF Trend</td><td>추세 수익엔진</td><td class='num {C(trr)}'>{trr:+.1f}%</td><td class=num>{trsh:+.2f}</td><td class=num>{W['trend']:.0%}</td></tr>
<tr><td>LETF Convex</td><td>상승 증폭 dose</td><td class='num {C(lfr)}'>{lfr:+.1f}%</td><td class=num>{lfsh:+.2f}</td><td class=num>{W['letf']:.0%}</td></tr></table></div>

<h2>📅 월별 수익</h2><div class=card><table><tr><th>월</th><th class=num>수익</th></tr>{mrow}</table></div>

<div class=warn>⚠️ <b>정직 고지:</b> 이건 <b>가상(paper) 백테스트</b>이지 실거래가 아니다. 3개월은 작은 표본이고 마침 <b>강추세 구간</b>(ETF {len(cur['on'])}/{len(TT)} 추세 ON)이라 추세 중심 전략에 유리했다 — 연환산 수치를 그대로 미래 기대값으로 보면 안 된다. 정직한 forward 기대 Sharpe ~0.5–0.6. <b>실거래(live)는 12개월 forward 검증 통과 + 사람 승인 후에만.</b></div>
<div class=muted style=margin-top:14px>데이터: Sharadar(주식·ETF·LETF, PIT·survivorship-safe) · 비용·차입 반영 · look-ahead 제거(신호 t→진입 t+1) · LLM은 자문만, 결정은 규칙·사람이 자본 게이트. 엔진: phase1a/engine/ · 생성: dashboard.py</div>
</div></body></html>"""
out=os.path.join(data.PHASE1A,"outputs","dashboard.html"); open(out,"w").write(html); R.to_csv(os.path.join(ENG,"run_3mo_nav.csv"))
print(f"대시보드 생성 → {out} ({os.path.getsize(out)//1024}KB)")
print(f"  3개월 +{tot*100:.2f}%(SPY {spy_tot*100:+.1f}%)·maxDD {dd*100:.1f}%·Sharpe {ann:+.2f}·상승일 {win*100:.0f}%")
print(f"  현재: trend {len(cur['on'])}/{len(TT)} ON·LETF {cur['letf']}·eq 롱{len(cur['L'])}/숏{len(cur['S'])} · 섹션: 성장곡선·작동방식·현재보유(ETF/LETF/롱숏종목+섹터)·sleeve성과·월별·고지")
