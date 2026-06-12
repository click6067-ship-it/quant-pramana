#!/usr/bin/env python3
"""PRAMANA — '상승 참여 vs 하락 방어' 프론티어. 용하 니즈(상승 다 먹고+하락 방어)가 데이터상 가능한가?
upside/downside capture(QQQ 월수익 기준)로 여러 북 배치. 우상단(상승 100+하락 낮음)에 아무도 없으면=공짜점심 없음.
free yfinance·비용후·in-sample. PNG(채팅). python engine/upside_downside_frontier.py"""
import os, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, yfinance as yf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); PNG=os.path.join(ROOT,"outputs","frontier.png")
RF=0.05
px=yf.download(["SPY","QQQ","DBMF","GLD","IEF","TLT"],period="max",interval="1d",auto_adjust=True,progress=False)
px=(px["Close"] if isinstance(px.columns,pd.MultiIndex) else px).dropna()
ret=px.pct_change(); days=ret.dropna().index   # DBMF 제약(2019~)
W7={"SPY":0.25,"QQQ":0.25,"DBMF":0.25,"GLD":0.15,"IEF":0.10}
four=sum(W7[t]*ret[t] for t in W7)
def lev(series,L): return L*series-(L-1)*RF/252
BOOKS={
 "QQQ (100% 성장)":ret["QQQ"],
 "SPY":ret["SPY"],
 "60/40 (SPY/IEF)":0.6*ret["SPY"]+0.4*ret["IEF"],
 "V7 4-sleeve 1.0x":four,
 "4-sleeve 1.25x":lev(four,1.25),
 "4-sleeve 1.5x":lev(four,1.5),
 "QQQ60/4sleeve40":0.6*ret["QQQ"]+0.4*four,
 "QQQ70/4sleeve30":0.7*ret["QQQ"]+0.3*four,
}
# 월별 수익 → QQQ up/down months capture
mret=(1+ret).resample("ME").prod()-1
mb={k:(1+v).resample("ME").prod()-1 for k,v in BOOKS.items()}
q=mret["QQQ"]; up=q>0; dn=q<=0
def cap(bk):
    u=bk[up].mean()/q[up].mean()*100; d=bk[dn].mean()/q[dn].mean()*100
    cum=(1+bk).prod()-1; mdd=((1+bk).cumprod()/(1+bk).cumprod().cummax()-1).min()
    return u,d,cum,mdd
print(f"{'북':<22}{'상승참여%':>9}{'하락참여%':>9}{'누적%':>8}{'MDD%':>7}  (QQQ 기준·월별·2019~)")
R={}
for k,v in mb.items():
    u,d,cum,mdd=cap(v); R[k]=(u,d,cum,mdd)
    print(f"  {k:<20}{u:>9.0f}{d:>9.0f}{cum*100:>8.0f}{mdd*100:>7.0f}")
# 산점도: x=하락참여(낮을수록 방어좋음), y=상승참여(높을수록 좋음)
plt.style.use("dark_background"); plt.rcParams.update({"figure.facecolor":"#070b16","axes.facecolor":"#0d1326","grid.alpha":.2,"font.size":10})
fig,ax=plt.subplots(figsize=(10,7.5))
for k,(u,d,cum,mdd) in R.items():
    col="#22d3ee" if "4-sleeve 1.0" in k else "#a78bfa" if k.startswith("QQQ (") else "#f59e0b" if "1.25" in k or "1.5" in k else "#94a3b8"
    ax.scatter(d,u,s=140,color=col,zorder=3,edgecolors="white",linewidths=0.5)
    ax.annotate(k,(d,u),fontsize=8.5,color="#e5e7eb",xytext=(6,5),textcoords="offset points")
ax.axhline(100,color="#475569",ls=":",lw=1); ax.axvline(100,color="#475569",ls=":",lw=1)
ax.scatter(60,100,s=300,marker="*",color="#34d399",zorder=4,edgecolors="white"); ax.annotate("용하 니즈\n(상승 100·하락 60)",(60,100),fontsize=9,color="#34d399",xytext=(8,-28),textcoords="offset points",fontweight="bold")
ax.set_xlabel("하락장 참여율 % (낮을수록 방어 좋음 ←)",fontsize=11); ax.set_ylabel("상승장 참여율 % (높을수록 좋음 ↑)",fontsize=11)
ax.set_title("상승 참여 vs 하락 방어 프론티어 — '둘 다(우상+좌)' 영역에 자산배분은 없다\n(QQQ 월수익 기준·2019~·비용후·in-sample)",color="#22d3ee",fontsize=12)
ax.grid(True,zorder=0)
# 대각선(참여=방어, 단순 베타 라인) 안내
ax.plot([0,140],[0,140],color="#334155",ls="--",lw=1,zorder=1); ax.annotate("베타 라인(상승=하락)",(120,120),fontsize=8,color="#64748b",rotation=33)
fig.tight_layout(); fig.savefig(PNG,dpi=115,bbox_inches="tight",facecolor="#070b16"); plt.close(fig)
print(f"\n핵심: 자산배분 북들은 전부 '베타 라인' 근처(상승 깎으면 하락도 깎임). 용하 니즈(★ 상승 100·하락 60)는 라인 *위/왼쪽*=알파/컨벡시티 영역=자산배분으론 도달 불가.")
print(f"✅ PNG: {PNG}")
if __name__=="__main__": pass
