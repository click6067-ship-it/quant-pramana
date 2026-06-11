# PRAMANA v3 — COMPLETION v0.1
**Date:** 2026-06-11 · **Status:** v3 profit-max paper book = **BUILT & RUNNABLE.** · **paper(₩100M 가상)·no live.**
**한 줄:** "굴러가고 수익내는" US 멀티-sleeve 공격적 paper book 완성. 백테스트 aggressive **Sharpe 1.12 / CAGR +14% / maxDD −17% / ₩100M→3.37억** — *단 regime-flattered, forward 보수(~0.6-0.8), live는 forward paper 통과 후 human gate.*

## 1. 무엇이 완성됐나 (8레이어 전부 구현·작동)
| 레이어 | 구현 |
|---|---|
| 1 데이터 | `engine/data.py` Sharadar 주식+ETF/LETF/vol(SFP_FUNDS)·PIT·manifest/hash·API-free |
| 2 신호 | `features.py` 동결(value/quality/momentum/lowvol/event)+trend+vol regime · 모델 CONSTRAINED(council) |
| 3 앙상블 | `portfolio_max.py`·`book_final.py` — 무상관 sleeve risk-budget 결합 |
| 4 사이징 | vol-target + max-lev + **DD ladder(−10/−15/−20/−25)** + cooldown |
| 5 리스크엔진 | `risk_engine.py` 결정적 veto·fractional-Kelly·4 kill·gap추정 (acceptance 4/4) |
| 6 실행 | `execution.py` per-name 체결(spread/impact/borrow/부분체결) smoke 4/4 |
| 7 모니터/kill | `monitor.py` K1~6·daily 메트릭·heartbeat·promotion gate smoke 8/8 |
| 8 거버넌스 | promotion gate가 backtest 차단·LLM off-path·human capital gate |
| **forward 운용** | `forward_book.py` — *현재 목표 포트폴리오* 산출 + forward_log(promotion gate 시계) |

## 2. 최종 book (book_final.py)
- **sleeve(next-bar, look-ahead 제거):** equity MN(Sharpe 0.25·corr to trend −0.25) + ETF trend(0.86) + LETF convex 소량 dose(0.80·vol68%→risk-budget 4% dollar). **VRP short-vol = REJECT**(worst month −62%·crash kill이 single-day gap 못막음).
- **결합 무레버: Sharpe 1.18·CAGR +8.2%·maxDD −10.3%**(분산). 공격(vol40·4x): **Sharpe 1.12·CAGR +14.3%·maxDD −17%·2021-26 Sh 1.27·₩100M→3.37억·연 8/10 양수.**

## 3. ★ 정직한 평가 (Codex 리뷰 반영 — no echo)
- **헤드라인(1.12-1.18)은 backtest·regime-flattered.** trend sleeve가 견인(2017-26 강추세·저금리), corr −0.25는 benign 샘플(스트레스 시 +0.25~+0.60 가능). **forward 정직 기대 = Sharpe ~0.6-0.8·CAGR 한자리~10%대 초반.**
- equity MN sleeve는 약함(0.25), 분산용. LETF는 convexity가 naive 레버 못이김(결합서 소량만 +).
- **= "되는 전략 발견"이 아니라 "유망 후보 + 굴러가는 시스템." live 아님.**

## 4. 바닥 규율 (유지) vs 천장 (paper엔 미적용)
- **바닥(절대):** look-ahead 제거(next-bar)·blow-up 방지(DD ladder/kill/cooldown)·날조 0·paper·LLM off-path·human이 capital gate. (수익최대화 모드여도 이건 안 푼다.)
- **천장(paper엔 미적용):** promotion gate(live Sharpe≥0.8·12mo OOS·maxDD≤15%) = *실제 돈* 기준. paper 수익최대화엔 족쇄라 미적용. → live 검토 시에만 게이트.

## 5. 어떻게 굴리나 (forward)
```bash
python engine/data.py validate        # 무결성
python engine/forward_book.py         # 매월: 현재 목표 포트폴리오 + forward_log 적재
python engine/book_final.py           # 백테스트 재현
```
- `forward_book.py` 매월 실행 → 현재 트렌드 ON ETF·LETF dose·equity L/S·목표 레버·리스크 상태 + 로그(promotion gate 12mo 시계 시작, 2026-06부터).
- 실제 체결 = next-bar·broker 연동은 **human 승인 후**(promotion gate 통과 시).

## 6. 남은 것 / forward가 결정할 것
- **forward paper 12mo+ 추적** = trend sleeve가 *친화 레짐 밖*에서도 사나, corr가 forward에 유지되나, 비용/세금 현실(broker fills)이 견디나 — **이게 candidate를 진짜로 만들거나 죽인다.**
- 개선 여지(council 우선순위): equity sleeve 알파 품질↑(그냥 레버 금지)·broker-grade 비용/세금·regime-conditioned 레버.
- **live 승격 = forward paper 통과 + DD 규율(≤15%→저레버) + human 더블사인오프.** 그 전엔 절대 실거래 0.

## 결론
v1(검증 negative)·v2(데이터축)·v3(빌드) 거쳐 **굴러가고 (paper)수익내는 공격적 멀티-sleeve 시스템 완성.** 숫자는 정직히 깎아서 봐도 *유망*하고, 시스템·규율·forward 추적이 갖춰졌다. 다음 진짜 진전은 *백테스트가 아니라 forward paper 시간*이다.
