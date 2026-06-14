# A2 Monthly Benchmark Review

> ⚠️ **백테스트(2016~·강세장 편향·닷컴/2008 crash 없음) · PAPER · 검증된 알파 아님.**
> 데이터 2016-01-04~2026-06-10 (2624 거래일, Sharadar closeadj 캐시). 라이브 ₩1억 ledger 아님(a2_live_runner 소관). 자본권한 0.
> 생성 2026-06-14 · engine/a2_benchmarks.py · spec: 04_BENCHMARKS_AND_METRICS.md

## Inception-to-date 패널 (full 2016~)

| 벤치마크 | 총수익 | 연율 | MDD | 회복 | 위험비율(ann/\|MDD\|) | Sharpe(rf=0) | vs QQQ 최대열위 |
|---|---|---|---|---|---|---|---|
| SPY | +327.3% | +14.9% | -33.7% | 97td | 0.44 | 0.87 | -288.5% |
| QQQ | +583.0% | +20.2% | -35.1% | 278td | 0.58 | 0.94 | +0.0% |
| TQQQ | +3155.2% | +39.6% | -81.7% | 486td | 0.49 | 0.84 | -22.1% |
| Naive Beta (QQQ35/TQQQ35/Cash30) | +882.1% | +24.5% | -48.4% | 278td | 0.51 | 0.87 | -4.8% |
| Synthetic QQQ 1.4x (proxy) | +934.6% | +25.1% | -48.2% | 267td | 0.52 | 0.88 | -4.8% |
| TQQQ monthly DCA | +794.7% | +23.4% | -83.6% | 836td | 0.28 | 0.65 | -132.1% |
| TQQQ drawdown DCA (-15%) | +703.9% | +22.1% | -84.2% | 840td | 0.26 | 0.64 | -164.0% |
| A2 base fixed (=A2 dynamic·동적 OFF) | +882.1% | +24.5% | -48.4% | 278td | 0.51 | 0.87 | -4.8% |
| V7 survival core (Eq50/DBMF25/GLD15/IEF10) | +169.9% | +15.0% | -17.9% | 55td | 0.84 | 1.18 | -136.6% |

## 판정 (§4 성공 정의)

- **성공** = A2 > QQQ **AND** A2 > naive **AND** Vaulted Profit > 0
- **부분 성공** = A2 > QQQ but A2 < naive (TQQQ beta는 효과·운영규칙 부가가치 미확정)
- **실패** = A2 < QQQ 또는 A2 < naive 또는 Vaulted=0 또는 Attack/Moonshot 기여 ≤ 0

**A2 base fixed (inception-to-date): +882.1% · QQQ +583.0% · naive +882.1%**

→ **부분 성공 (A2>QQQ but A2≤naive → TQQQ beta는 효과·운영규칙 부가가치 미확정)**

### 정직한 해석

- **A2 base fixed = naive(QQQ35/TQQQ35/Cash30)와 구성이 동일** (동적 allocator는 `dynamic_mode_enabled: false` = REJECT·동적기여 음수라 OFF 확정). 따라서 이 backtest 패널에서 **A2 base fixed ≈ naive (동률)**. 둘의 부가가치 차이는 이 패널로 측정 불가 — 운영규칙(Attack/Moonshot/Vault)은 forward live ledger(a2_live_runner)에서만 산다.
- A2 base fixed가 QQQ를 이김: QQQ35/TQQQ35/Cash30은 실효 beta ≈ 1.40x → 강세장(2016~)에선 QQQ buy-and-hold 대비 초과. 단 이건 **레버일 뿐 알파 아님** (synthetic 1.4x·TQQQ buy-and-hold와 같이 봐야 함).
- **Vaulted Profit = 0 (backtest 패널에선 미측정)**: §4 성공의 세 번째 조건은 forward live Vault ledger(a2_live_runner positions/vault.json) 소관. backtest 2016~ 누적 excess로 Vault를 돌리면 단위 부적합(live_runner 주석 참조)이라 OFF. → 이 패널만으로는 **"성공" 판정 불가**, beta-book 비교까지만.
- TQQQ buy-and-hold MDD=-81.7%·회복=486td = 3x decay/낙폭의 실증. A2가 "큰 낙폭 후 게임 계속" 조건을 보려면 TQQQ MDD 대비 A2 MDD가 얕아야 함(현재 A2 fixed MDD=-48.4% vs TQQQ -81.7%).

### TQ-DH 비교 (§5)

| | 총수익 | MDD | 회복 |
|---|---|---|---|
| TQQQ buy-and-hold | +3155.2% | -81.7% | 486td |
| TQQQ monthly DCA | +794.7% | -83.6% | 836td |
| TQQQ drawdown DCA (-15%) | +703.9% | -84.2% | 840td |

DCA는 **contribution-weighted capital multiple**(최종 시장가치/총투입 → buy-and-hold와 비교 가능·엄밀 IRR/MWRR는 아님). 매수일 미세 sawtooth(투입 희석)는 MDD에 보수적.

### caveats

- 강세장 편향: 2016~ 표본에 닷컴(-49% QQQ)·2008 없음 → TQQQ/synthetic 1.4x·A2 fixed 모두 **하방 미검증**. V8(분산북 레버) 기각 근거와 동일 caveat.
- Synthetic QQQ 1.4x = `QQQ일수익×1.4 − 2.0%/yr 금융비용 proxy` (가정·실제 펀딩비 아님).
- V7 OK: DBMF/GLD/IEF=yfinance(auto_adjust) · 공통 2019-05-08~2026-06-10 (1783td) · DBMF 상장 2019-05 → 2016-19 미커버(부분기간 caveat)
- 동적 allocator OFF = A2 dynamic == A2 base fixed (이 패널 표기는 동일 곡선).
