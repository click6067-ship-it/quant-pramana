# Alpha Lab MT-1 — Daily Re-entry Ladder · 사전등록 프로토콜 v0.1

> **가설:** 4-sleeve 코어 유지 + QQQ *공격 overlay*를 위험신호에 따라 **단계적(0→25→50→75→100)**으로 조절하면, **binary on/off throttle보다 휩쏘↓·회복지연↓**.
> **단 prior 낮음:** regime_switch_test=단계적 전환(growth↔survival) 죽음(Sharpe 0.91<static 1.07)·crash_pack_throttle=binary overlay 죽음. **MT-1=둘의 조합(단계적×overlay·코어유지)=안 본 변형 하나만.**
> 상태: **PAPER · 자본권한 0 · RESEARCH_ONLY.** 코어(4-sleeve) 전환 아님(overlay만). 결과 보기 **전** 작성. 2026-06-12.

## 1. 비교 대상 (4개·일봉만)
- **static QQQ** (100%·타이밍 없음·상한 벤치)
- **static V7 4-sleeve** (overlay 0·하한 벤치)
- **binary throttle** — risk-on이면 overlay=OV_MAX, risk-off면 0 (crash_pack_throttle 형태)
- **MT-1 daily ladder** — overlay = OV_MAX × scale(risk_score) 단계적

book_ret = (1−ov)·four_ret + ov·QQQ_ret − turnover_cost · |Δov|. **next-bar**(score t → ov t+1).

## 2. 고정 파라미터 (자유도 최소 — 새 자유도 = "단계적 vs binary" 하나뿐)
- **OV_MAX = 0.50** (공격 overlay 상한·고정·"절반까지만 QQQ")
- **risk_score** = 기존 3-factor 재사용: SPY<200dMA(+1)·20일 vol>22%(+1)·drawdown<−10%(+1) → 0~3
- **ladder scale** = {0:1.0, 1:0.66, 2:0.33, ≥3:0} (regime_switch 재사용·고정)
- **binary scale** = {0:1.0, else:0}
- **turnover cost** = 10bp × |Δov| (휩쏘 비용·매일)

## 3. 금지 (config-mining 차단)
- ORB/VWAP/RVOL 분봉 센서 추가 **금지** (2단계로 보류)
- threshold(200dMA·22%·−10%·OV_MAX·scale) 여러 개 만지기 **금지**
- 결과 본 뒤 ladder 단계 변경 **금지** (=vNext 분리)
- 코어(4-sleeve) 전환 **금지** (overlay만 조절)
- LETF/레버 **금지**

## 4. 측정 (풀 + crash 윈도우 · 비용후)
누적 · MDD · Sharpe · 회복일수(UW) · 전환 turnover · 휩쏘 비용 · crash별 손실.
crash-pack: 2020 COVID · 2022 bear (실 ETF) + 2008 GFC · 2000 닷컴 (proxy·VFINX overlay·crash_pack 인프라 재사용).

## 5. 사전등록 kill (goalpost 고정)
**MT-1 ladder가 아래 중 하나라도면 DEAD:**
1. **static 4-sleeve를 위험조정(Sharpe)으로 못 이김** (regime_switch·throttle 죽인 그 기준)
2. **binary throttle보다 나은 게 없음** (단계적의 *유일한 존재이유*)
3. **휩쏘 비용 후 net이 static보다 열위**
4. **crash-pack(2008/2020/2022)에서 static 4-sleeve 대비 방어 의미 없음**
5. QQQ 대비 회복/수익 매력 없음

→ **DEAD면 마켓타이밍 코어 실험 *닫음*(4번째 negative·정직 종착).** SURVIVE면 2단계로 ORB/VWAP/RVOL 반등 센서 추가.

## 6. 한계 / 정직
- prior 낮음: 단계적(regime_switch)·overlay(throttle) 각각 이미 죽음. 조합만 미검증.
- proxy(2008/2000 VFINX overlay)·in-sample(2019~ benign)·forward 0개월.
- 후행 신호의 본질(늦음·휩쏘)은 ladder로도 안 풀릴 수 있음 — 그게 kill이면 정직히 닫는다.

> **한 줄:** "단계적 ladder가 binary throttle보다 나은가" 하나만. static 4-sleeve 못 이기면 DEAD → 마켓타이밍 닫고 V7 생존코어 확정. 올인 아님.
