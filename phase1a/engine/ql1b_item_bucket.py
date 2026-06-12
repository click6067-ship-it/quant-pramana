#!/usr/bin/env python3
"""PRAMANA QL-1B — 8-K Item bucket triage (정직 OOS·비용후). "event 종류 구분이 거래 가능한가?"
의미 기반 사전 bucket(결과로 고른 거 최소화)·비용 20bp·OOS(2021-23 정의 → 2024-26 검증).
kill: positive bucket이 비용후·OOS 중앙값 양수 못 내면 → event 종류 구분도 거래 알파 아님 → LLM 보류.
이건 승격 아니라 triage/feasibility(GPT). ql1_8k_events.csv 재사용. python engine/ql1b_item_bucket.py"""
import os, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ed=pd.read_csv(os.path.join(ROOT,"outputs","ql1_8k_events.csv")); ed["date"]=pd.to_datetime(ed["date"])
ed["item1"]=ed["items"].map(lambda s:str(s).split(",")[0] if pd.notna(s) and s else "none")
# 의미 기반 사전 bucket (공시 *종류*의 통상적 방향·결과 무관)
POS={"1.01":"계약","2.01":"인수완료","5.02":"경영진","5.07":"주총"}
NEG={"3.02":"희석/유증","3.01":"상폐위험","4.02":"재무신뢰불가","5.03":"정관변경","2.05":"구조조정","2.06":"손상","4.01":"회계법인변경"}
def buck(it): return "POS" if it in POS else ("NEG" if it in NEG else "NEU")
ed["bucket"]=ed["item1"].map(buck)
COST=0.002  # round-trip 20bp
ed["net10"]=ed["ex10"]-COST   # excess(SPY차감) - 거래비용
ed["oos"]=ed["date"]>="2024-01-01"
def summ(df,lbl):
    v=df["net10"].dropna()
    if len(v)<15: print(f"  {lbl:<30} n={len(v):>4} (소표본)"); return None
    print(f"  {lbl:<30} n={len(v):>4}  평균net {v.mean()*100:>6.2f}%  중앙 {v.median()*100:>6.2f}%  승률 {(v>0).mean()*100:>3.0f}%")
    return (v.mean(),v.median(),(v>0).mean())
print(f"=== QL-1B: 8-K Item bucket triage (비용 {COST*1e4:.0f}bp후·SPY차감·10일) ===")
print(f"\n[bucket별 — 전체기간]")
for b in ["POS","NEG","NEU"]: summ(ed[ed["bucket"]==b],f"{b} ({'/'.join(list(POS.values())[:2]) if b=='POS' else '/'.join(list(NEG.values())[:2]) if b=='NEG' else '실적/기타'})")
summ(ed,"ALL 8-K")
print(f"\n[★ OOS 정직 검증 — POS bucket]")
print(f"  In-sample (2021-23):"); a_in=summ(ed[(ed['bucket']=='POS')&(~ed['oos'])],"  POS in-sample")
print(f"  OOS (2024-26):"); a_oos=summ(ed[(ed['bucket']=='POS')&(ed['oos'])],"  POS OOS")
print(f"\n[NEG 회피 가치 — long-only 필터(GPT 아이디어1)]")
neg=ed[ed["bucket"]=="NEG"]["net10"].dropna(); allv=ed["net10"].dropna()
print(f"  NEG bucket net {neg.mean()*100:+.2f}%(중앙 {neg.median()*100:+.2f}%) — *회피하면* 이만큼 손실 안 봄(drawdown 방지)")
print(f"\n[POS − NEG spread (long-short proxy·공매도 솔로불가)]")
pos=ed[ed["bucket"]=="POS"]["net10"].dropna()
print(f"  POS {pos.mean()*100:+.2f}% − NEG {neg.mean()*100:+.2f}% = spread {(pos.mean()-neg.mean())*100:+.2f}%p")
# 판정
print(f"\n{'='*72}\n사전등록 판정 (kill: POS가 비용후 OOS 중앙값 양수 못 내면 → LLM 보류):")
if a_oos:
    ok = a_oos[1]>0 and a_oos[2]>0.50
    print(f"  POS OOS: 중앙 {a_oos[1]*100:+.2f}% · 승률 {a_oos[2]*100:.0f}% → {'PASS(거래 가능성·LLM 2단계 가치)' if ok else 'FAIL(event 종류 구분도 비용후 OOS 거래 알파 아님 → LLM 보류)'}")
    print(f"  단 NEG 회피({neg.mean()*100:+.2f}%)는 long-only 필터로 별도 가치(손실방지)·POS−NEG spread는 공매도 전제")
print(f"\n정직: 의미 bucket도 결과 본 후라 약한 mining·OOS로 통제 시도·비용 20bp는 낙관·대형주 위주(효율적). triage지 승격 아님.")
if __name__=="__main__": pass
