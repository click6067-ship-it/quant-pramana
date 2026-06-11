#!/usr/bin/env python3
"""트레이더 렌즈 재측정 — 버렸던 market-neutral long-short를 *전략으로* 측정.
kill 바(cap-weight 이기기·IC-IR0.20) 말고: net Sharpe·CAGR·maxDD·시장상관(중립성)·2021-26 robustness.
엔진 재사용(캐시·API 0). 새 알파 0·튜닝 0 — 기존 신호의 long-short 위험조정 성과만."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
import run as RUN, configs

def ls_stats(R):
    net = (R["spread"] - (R["to5"]*R["c5"] + R["to1"]*R["c1"])).dropna()   # 월 net long-short
    m = 12
    sharpe = net.mean()/net.std()*np.sqrt(m) if net.std() > 0 else np.nan
    cagr = (1+net).prod()**(m/len(net)) - 1
    nav = (1+net).cumprod(); dd = (nav/nav.cummax()-1).min()
    corr = net.corr(R["bcw"])                                              # 시장(cap-weight)과 상관
    rec = net[net.index >= "2021-01-01"]
    rs = rec.mean()/rec.std()*np.sqrt(m) if rec.std() > 0 else np.nan
    return dict(n=len(net), ann_net=net.mean()*m, sharpe=sharpe, cagr=cagr, maxdd=dd,
                mktcorr=corr, rec_sharpe=rs, rec_ann=rec.mean()*m)

print("="*86); print("트레이더 렌즈: market-neutral LONG-SHORT 재측정 (기존 신호, 비용후)"); print("="*86)
print(f"{'config':22s} {'net%/yr':>8s} {'Sharpe':>7s} {'CAGR%':>7s} {'maxDD%':>7s} {'mktcorr':>8s} {'21-26 Sh':>9s}")
for name in ["B3_quality", "B4_momentum", "phase1b_blend", "sm_blend", "broad_event"]:
    try:
        R = RUN.run_named(name)["R"]; s = ls_stats(R)
        print(f"{name:22s} {s['ann_net']*100:+8.2f} {s['sharpe']:+7.2f} {s['cagr']*100:+7.2f} "
              f"{s['maxdd']*100:7.1f} {s['mktcorr']:+8.2f} {s['rec_sharpe']:+9.2f}")
    except Exception as e:
        print(f"{name:22s} ERR {str(e)[:50]}")
print("\n해석: Sharpe>0·낮은 mktcorr=시장중립 분산수익 / 2021-26 Sharpe=최근 생존 여부.")
print("⚠️ long-short 추가비용(차입/숏보로) 미반영·gross exposure 가정 단순 — *측정*이지 라이브 아님.")
