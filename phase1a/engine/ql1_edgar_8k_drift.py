#!/usr/bin/env python3
"""PRAMANA Alpha Lab QL-1 (baseline) — EDGAR 8-K event drift (LLM 前·정성 알파의 전제조건 확인).
사전등록 가설: 8-K 공시(이벤트) 후 daily drift가 있나? Item 타입별 차이? = LLM 정성 얹기 *전*에 'event 자체가 신호 있나' 확인.
설계: 8-K acceptance timestamp → *다음 거래일 종가* 진입(look-ahead 차단) → 5/10/20일 forward excess(vs SPY). Item별·SPY방향별.
kill: 전체 excess≈0 AND 모든 Item excess≈0 → 8-K event drift 없음 → LLM 얹어도 의미 적음(단 LLM이 event 선택 개선 여지는 2단계). 결과 후 종목/기간/Item 튜닝 금지.
무료(EDGAR+yfinance)·PIT·백테스트. python engine/ql1_edgar_8k_drift.py"""
import os, json, time, warnings; warnings.filterwarnings("ignore")
import urllib.request, numpy as np, pandas as pd, yfinance as yf
UA={"User-Agent":"pramana research click6067@gmail.com"}
def jget(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=20))
# universe: S&P100 대형 + 변동성/중형 섞어 (다양 섹터·표본 확보)
UNIV=["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AVGO","AMD","NFLX","CRM","ADBE","INTC","QCOM","TXN","MU","AMAT","ARM","SMCI","PLTR",
"JPM","BAC","WFC","GS","MS","C","V","MA","AXP","BLK","SCHW","COIN","HOOD","SOFI","PYPL",
"UNH","JNJ","LLY","PFE","MRK","ABBV","TMO","ABT","BMY","AMGN","GILD","CVS","MRNA","VRTX","REGN",
"XOM","CVX","COP","SLB","OXY","WMT","COST","HD","NKE","MCD","SBUX","TGT","LOW","DIS","CMCSA","T","VZ",
"BA","CAT","GE","HON","UPS","RTX","LMT","DE","MMM","F","GM","RIVN","UBER","ABNB","DAL",
"PG","KO","PEP","CL","MDLZ","MO","ORCL","IBM","CSCO","NOW","SNOW","NET","CRWD","DDOG","PANW","ZS","SHOP","SQ","ROKU","DKNG",
"MSTR","IONQ","RGTI","SMR","OKLO","AI","ENPH","FSLR","CCJ","LULU","CMG","WBD","RBLX","U","TTD","MDB","ANET","DELL","WDC","ON"]
print(f"=== QL-1: EDGAR 8-K event drift (universe {len(UNIV)}종목·LLM 前 baseline) ===")
t2c={v["ticker"]:str(v["cik_str"]).zfill(10) for v in jget("https://www.sec.gov/files/company_tickers.json").values()}
ev=[]
for i,tk in enumerate(UNIV):
    cik=t2c.get(tk);
    if not cik: continue
    try:
        r=jget(f"https://data.sec.gov/submissions/CIK{cik}.json")["filings"]["recent"]
        for j in range(len(r["form"])):
            if r["form"][j]=="8-K":
                ev.append({"tk":tk,"date":r["filingDate"][j],"accept":r["acceptanceDateTime"][j],"items":r.get("items",[""]*len(r["form"]))[j]})
    except Exception: pass
    time.sleep(0.12)
ed=pd.DataFrame(ev); ed["date"]=pd.to_datetime(ed["date"])
ed=ed[ed["date"]>="2021-01-01"]   # 표본 기간(고정)
print(f"수집 8-K: {len(ed)}건 ({ed['date'].min().date()}~{ed['date'].max().date()})")
# 가격
px=yf.download(UNIV+["SPY"],period="6y",interval="1d",auto_adjust=True,progress=False)["Close"]
spy=px["SPY"]; cal=px.index
def fwd_excess(tk,d,h):  # d=8-K date·다음 거래일 진입·h일 forward excess vs SPY
    if tk not in px: return np.nan
    after=cal[cal>d]
    if len(after)<h+1: return np.nan
    e=after[0]; ex=after[h] if len(after)>h else after[-1]
    p=px[tk]
    if pd.isna(p.get(e)) or pd.isna(p.get(ex)) or p.get(e,0)<=0: return np.nan
    r=p[ex]/p[e]-1; sr=spy[ex]/spy[e]-1
    return r-sr   # 시장조정 초과
for h in [5,10,20]:
    ed[f"ex{h}"]=ed.apply(lambda x:fwd_excess(x["tk"],x["date"],h),axis=1)
ed["spy_up"]=ed["date"].map(lambda d:(spy[cal[cal<=d][-1]]/spy[cal[cal<=d][-2]]-1>0) if len(cal[cal<=d])>=2 else np.nan)
ed["item1"]=ed["items"].map(lambda s:str(s).split(",")[0] if s else "none")
def summ(df,lbl,h=10):
    v=df[f"ex{h}"].dropna()
    if len(v)<10: print(f"  {lbl:<26} n={len(v):>4} (소표본)"); return
    print(f"  {lbl:<26} n={len(v):>4}  평균excess {v.mean()*100:>6.2f}%  중앙 {v.median()*100:>6.2f}%  승률 {(v>0).mean()*100:>3.0f}%")
print(f"\n[전체 8-K · {len(ed)}건 · forward excess vs SPY (10일)]")
summ(ed,"all 8-K")
print(f"\n[SPY 방향별 — 강세장 의존?]")
summ(ed[ed["spy_up"]==True],"발표일 SPY up"); summ(ed[ed["spy_up"]==False],"발표일 SPY down ★")
print(f"\n[Item 타입별 (주요·10일 excess)] — 어떤 event가 drift 있나")
ITEMNAME={"2.02":"실적발표","1.01":"계약체결","5.02":"경영진변경","8.01":"기타이벤트","7.01":"Reg-FD","1.05":"사이버","2.01":"인수완료","3.01":"상폐통지","5.07":"주총투표"}
for it,n in ed["item1"].value_counts().head(10).items():
    summ(ed[ed["item1"]==it],f"{it} {ITEMNAME.get(it,'')}")
print(f"\n[Horizon별 전체]")
for h in [5,10,20]: summ(ed,f"전체 {h}일",h)
# 판정
a=ed["ex10"].dropna();
print(f"\n{'='*70}\n사전등록 판정 (kill=전체·모든 Item excess≈0):")
best_item=max([(it,ed[ed['item1']==it]['ex10'].dropna().mean()) for it in ed['item1'].value_counts().head(8).index if len(ed[ed['item1']==it]['ex10'].dropna())>=20],key=lambda x:x[1],default=("none",0))
print(f"  전체 8-K 평균 excess(10일): {a.mean()*100:+.2f}% (승률 {(a>0).mean()*100:.0f}%)")
print(f"  최고 Item: {best_item[0]} {ITEMNAME.get(best_item[0],'')} = {best_item[1]*100:+.2f}%")
sig = abs(a.mean())>0.003 or best_item[1]>0.005
print(f"  → {'신호 흔적 有 → LLM grade 2단계 진행 가치' if sig else 'event drift≈0 → 8-K 자체는 신호 없음(단 LLM이 event 선택 개선 여지는 별도)'}")
ed.to_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"outputs","ql1_8k_events.csv"),index=False)
print(f"\n정직: LLM 前 baseline·시장조정 excess·소형주 적음(대형 위주=효율적이라 drift 불리)·PIT(다음거래일 진입). 신호 있어도 비용/표본/다중검정 後. 적재 outputs/ql1_8k_events.csv")
if __name__=="__main__": pass
