# Alpha Lab v1 — 단일 setup paper sim 결과 → **DEAD (backtest) · forward 관찰 보류**

> **용하(2026-06-12): "실패는 기록·폐기는 마·좀 더 지켜보자."** → backtest DEAD는 기록하되 *완전폐기/종결 아님*. v1 setup을 **원형 그대로(튜닝 없이)** `alpha_lab_v2_scanner.py`가 매일 forward 로그로 관찰(진짜 죽나 더 본다). 튜닝(stop/target/RVOL/ORB)은 여전히 금지.

> 사전등록: `PRAMANA_V4/AlphaLab_v1_Protocol.md` · 코드: `phase1a/engine/alpha_lab_v1_sim.py`
> setup: Gap-up(+1%) + RVOL≥1.5(진입시점 누적) + ORB15 돌파 + VWAP 위 · 진입=next-bar 시가 · 청산 +5%target/VWAP·ORB stop/장마감 · 비용 20bp.
> 데이터: yfinance 5m·60일·watchlist 30종목(2026 변동성주). **PAPER·자본권한 0·RESEARCH_ONLY.** 2026-06-12.

## 판정 한 줄
**이 등록된 setup = DEAD(폐기).** RVOL look-ahead 누수(Codex가 발견) 수정 후 재실행하니 **사전등록 kill ③(false breakout 과반) 직접 발동** + 중앙값 음수 + 강세장 베타 의존. Codex VERDICT="폐기" 확정. 튜닝 금지(config-mining).

## ★ RVOL look-ahead 버그 (Codex #1 — verify-before-done 위반·인정)
- **버그:** 가격은 next-bar로 차단했으나 **RVOL을 당일 *전체* 거래량(09:45 진입인데 15:50까지 미래 거래량)으로 계산**했음. RVOL 필터가 미래를 봄 → 결과 부풀림.
- **수정(튜닝 아닌 버그픽스·Codex 승인):** RVOL = **신호 bar 시점까지 누적 거래량 / 과거 20일 *같은 경과분* 누적 평균**. 그 후 unchanged 재실행.

## 결과 — RVOL 누수 수정 전 → 후
| 지표 | 누수 버전(무효) | **수정 후(정직)** |
|---|---|---|
| 전체 평균 net | +1.06% | **+0.73%** |
| 전체 중앙 net | +0.10% | **−0.41% (음수)** |
| 승률 | 51% | **41%** |
| SPY down/flat 날 | −0.90% | **−0.99%·승률 10%** |
| false breakout(stop) | 49% | **56% (과반)** |
| 손절 vs hold-to-close | −0.28%p | −0.23%p (여전히 깎음) |

→ 평균 +0.73%는 소수 큰 승리(target+5% 21%)에 끌린 것·**중앙값 음수·승률 41% = 대부분 트레이드는 진다.**

## 사전등록 kill 대조 (수정 후)
| # | 조건 | 결과 |
|---|---|---|
| ① | after-cost 평균 net > 0 | △ +0.73%(평균만·중앙 음수) |
| ② | 강세장에서만 양수? | ⚠️ 우려 — SPY down −0.99%·승률 10% |
| ③ | **false breakout 과반?** | ❌ **FAIL (56% > 과반)** |
| ④ | VWAP/ORB 손절이 손실 줄이나? | ⚠️ 우려 — 손절이 수익 −0.23%p 깎음 |

→ **③ 직접 위반 + ②④ 우려 = setup DEAD.**

## Codex 적대검증 VERDICT (no-echo·2026-06-12)
**"폐기 (DEAD) for this registered setup/config. 약한 엣지 후보 아님."** broader phenomenon만 `RESEARCH_ONLY/NEEDS_EVIDENCE`. 6지적:
1. **RVOL look-ahead** — 당일 전체 거래량을 진입 전 사용. *이것만으로 +1.06% 무효 가능.* → 수정함(위).
2. **Watchlist selection = 최대 비코드 편향** — 2026 핫종목 고정 = "최근 중요했던 이름"이지 거래가능 과거 유니버스 아님. PIT 유니버스면 결론 뒤집힐 수 있음(setup이 사실상 "시장 오르는 날 현재 승자 매수").
3. **사전등록 kill 위반 = DEAD** — SPY down −0.90% + 손절이 hold보다 나쁨. "mixed" 아님. 결과 보고 프로토콜 고치면 config-mining.
4. **비용 20bp는 clean kill 아니나 execution modeling이 문제** — gross +1.26%라 40-50bp도 기계적으론 +0.86/0.76%. 단 market/stop 주문은 immediacy cost(bid-ask·빠른 종목 슬리피지) 지불 → flat bp 아니라 quote 기반 replay 필요.
5. **시장 베타는 SPY gate로 안 풀림** — gate 끼면 엣지 주장이 "selected hot stocks의 bull-day momentum"으로 바뀜 = setup 알파 아님. + SPY day return은 마감후만 known → gate는 prior-close state만 써야.
6. **n=70은 hidden trials 후 부족** — 30종목·60일 bull·gap/RVOL/ORB/target 선택·인간 사전탐색. deflated Sharpe/PBO. day-trader <1%만 순수익(Barber).

**가장 먼저 볼 1개:** PIT 유니버스 replay + entry-time-only RVOL + 현실적 execution cost. 그 전엔 해석 가치 낮음.

## 결론 / 다음
- **이 setup = DEAD 기록 (backtest).** 단 **완전폐기 아님 → forward 관찰 보류**(용하: 좀 더 지켜보자). `alpha_lab_v2_scanner.py`가 원형 그대로 매일 로그. **튜닝 금지**(stop/target/RVOL/ORB/SPY gate 만지면 실패한 사전등록 테스트를 mined strategy로 변환).
- **v0 데이터 infra(setup 검출)는 유지** — 죽은 건 *이 단일 setup의 수익성*이지 인프라 아님.
- **broader phenomenon(급등주 intraday momentum)** = `NEEDS_EVIDENCE`. 진짜 검증 = ① PIT 유니버스(그날 실제 gap-up·미래정보 없이) ② entry-time-only RVOL(고침) ③ quote-level execution(bid-ask) — **전부 1단계 유료 intraday(Polygon/Alpaca/QuantRocket) 필요.** 그 인프라 전엔 yfinance로 결론 못 냄.
- 정직: Alpha Lab 첫 전략이 죽음 = 또 하나의 negative. 시스템이 RVOL 누수까지 잡아 가짜 알파를 안 만듦(자산).
