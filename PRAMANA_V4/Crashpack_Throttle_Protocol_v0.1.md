# Crash-Pack × Brake-Only Throttle — 사전등록 프로토콜 v0.1

> **목적(딱 하나):** *4-sleeve 고정 코어 + 공격 overlay에 brake-only throttle*이 **crash-pack에서 값어치가 있나?**
> **금지:** QQQ↔4-sleeve 코어 대전환 재실험(이미 데이터로 짐). 이번엔 **코어는 고정, 공격 overlay(LETF)만 끈다.**
> 상태: PAPER · RESEARCH_ONLY · 결과 보기 **전** 작성(goalpost 고정). 2026-06-12.

## 1. 비교 대상 (4개 북)
1. **Static QQQ** (트랙 B = VFINX·S&P500 TR) — benchmark
2. **Static 4-sleeve** — Eq50(SPY/QQQ→VFINX) · MF25(DBMF→RYMFX, 없으면 cash) · Gold15(GLD→GC=F) · Bond10(IEF→VFITX)
3. **4-sleeve + 공격 overlay 고정** — 자본 w%를 합성 LETF(3x equity, daily-reset·financing·expense), (1−w)%를 4-sleeve. w ∈ {5%, 10%, 20%}
4. **4-sleeve + overlay + Risk Throttle** — 위험신호 뜨면 **overlay만 cash로**(코어 4-sleeve 불변). next-bar(score t → weight t+1)

## 2. Throttle 규칙 (brake-only · 코어 안 건드림)
score = (equity < 200dMA) + (20d vol > 22%) + (drawdown < −10%) — 사전정의·후행지표
- **주 버전:** score ≥ 1 → overlay = 0 (cash). score 0 → overlay = w.
- 변형(보고만): 단계적 overlay = w·{0:1, 1:0.5, 2:0, 3:0}[score].
- look-ahead 차단: 신호 t → overlay t+1.

## 3. 데이터 트랙 (전부 "stress proxy, NOT 실증" 라벨)
| 트랙 | 기간 | sleeve 데이터 | 비고 |
|---|---|---|---|
| **A 실증** | 2019~2026 | DBMF/GLD/IEF/SPY/QQQ 실 ETF | 2020·2022 실데이터 |
| **B-2008** | 2007-10~2009-12 | VFINX·RYMFX·GC=F·VFITX | 4-sleeve 전부 proxy(핵심) |
| **B-2000** | 2000-01~2002-12 | VFINX·**cash**·GC=F·VFITX | MF proxy 없음→25% cash(보수적·라벨) |
| **B-1987** | 1987 실데이터 | VFINX·VUSTX | gold/MF 없음→cash. **Black Monday(−20%)는 VFINX 실데이터에 이미 포함→synthetic gap 불필요·미사용**(v0.1 초안의 "synthetic gap" 문구는 코드와 불일치였어 정정·Codex #5) |

overlay underlying: 트랙 A=3x QQQ, 트랙 B=3x VFINX(S&P500). LETF = 3·u_ret − 2·RF/252 − 0.95%/252 (daily reset→누적 곱이 vol-decay 자동 반영).

## 4. 측정 (각 북 × 풀기간 + 각 crash 윈도우)
누적 · CAGR · MDD · Sharpe · 회복일수(peak 복귀) · crash 윈도우 peak-to-trough 손실 · **throttle drag**(비위기 구간 overlay-고정 대비 누적차) · **throttle false-positive**(overlay 끈 직후 overlay가 오른 놓친 수익).

## 5. 사전등록 PASS 조건 (throttle 승격 — 전부 만족해야)
throttle이 **공격 overlay-고정(북3) 대비** 아래를 *crash-pack에서* 보여야 함:
1. **crash MDD 감소** (각 crash 윈도우)
2. **회복기간 감소**
3. **crash 손실 감소**
4. **비위기 수익 훼손 과하지 않음** — throttle drag로 인한 풀기간 net이 음수면 실패(끈 손실 > 구한 손실)
5. **복잡도 정당화** — 4-sleeve+overlay+throttle 풀 위험조정(Sharpe)이 *static 4-sleeve*를 넘어야(안 넘으면 그냥 static 4-sleeve가 정답)

**하나라도 실패 → throttle = 대시보드/정보용 유지(risk-engine 승격 ❌).** 못 보여주면: 코어는 4-sleeve paper forward, 알파는 Alpha Lab(급등주)서 별도 사냥.

## 6. 한계 (사전 명시)
- proxy ≠ 실증: VFINX(QQQ 성장틸트 제거)·RYMFX(DBMF와 운용 다름)·GC=F(GLD 추적오차)·2000-02 MF=cash·1987 합성. **결과는 방향성 stress 신호지 backtest 진실 아님.**
- LETF 합성은 실 LETF의 차입비용/추적오차 근사(보수적이려 시도).
- 단일 실험: 통과해도 forward·실 LETF·2-feed 전엔 paper 고정(Promotion Gates 불변).
