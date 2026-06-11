# PRAMANA — Review Handoff v0.1
**Date:** 2026-06-11 · **For:** 외부 리뷰어(사람/AI) · **Scope:** US-only systematic equity *paper* trading OS (₩100M 가상, **no live**). · **이 문서 하나로 전체 파악 + 공격 지점까지.**

> **검증 방법(clone 후 2커맨드, API/인터넷 불필요 — 모든 데이터 캐시 동결):**
> `cd phase1a && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
> `python engine/data.py validate` (스냅샷 무결성) · `python engine/_smoke_run.py` (과거 실험 config로 동결 재현)
> 핵심 book 재현: `python engine/combined_book.py`

---

## 0. TL;DR
1. **목표는 종목추천 AI가 아니라 검증·실행 OS.** "데이터 정직 → 비용 정직 → 검증 통과 → 그다음 모델."
2. **v1(검증): US 공개 cross-sectional 단순/결합/event/PEAD/revision-게이트 = 6개 가설 사전등록 kill로 전멸.** 정직한 negative + 재사용 검증엔진 완성.
3. **v3(빌드): 진짜 lever는 모델복잡도가 아니라 *분산*.** equity 시장중립 L/S(Sharpe 0.31) + ETF trend+vol overlay(0.85, 상관 +0.06) **결합 → Sharpe 0.82·vol↓·maxDD↓**, 레버리지 → CAGR +11.9%/Sharpe 0.87/maxDD −18% (paper).
4. **★ 정직: combo Sharpe는 trend sleeve가 견인 = 2017–25 강추세 레짐 flattered. 독립 적대 리뷰(Codex)는 forward Sharpe를 ~0.45로 더 낮게 보고, "equity beta timing 백테스트를 다변화 book으로 분장한 것일 수 있다"고 판정. 전부 backtest·paper·forward 0개월.**
5. ML(deep 포함)은 deep-research(105에이전트)+자체 bake-off로 **증분 없음** 확정 → 모델공간 CONSTRAIN.
6. **★ 독립 적대 리뷰(Codex) 평결 = REVISE, 현 상태로 fundable 아님**(§8). 확인된 누수: **same-close 실행**(next-bar 필요). → **결론: "되는 전략 발견"이 아니라 "유망한 후보 + 검증해야 할 약점 다수." live 절대 아님.**

## 1. LOCKED 결정 (사용자 확정)
| 항목 | 값 |
|---|---|
| 시장 / 자본 | US only / ₩100M **가상(paper)** · no live |
| 목적함수 | 공격적 절대수익 (고변동·레버리지 허용) |
| 모델공간 | **CONSTRAINED**(council 결정): 정규화선형+GBM challenger only·trial ledger·**deep/비제약 ML 금지** |
| 데이터 | Sharadar 고정(~$69/mo)·주식+ETF+LETF+vol(SFP)·**native 선물 없음→proxy** |
| 규율 | 사전등록 kill·walk-forward/OOS·정직(no echo)·동결 재현·**risk engine 결정적 veto·LLM off-path·human이 capital gate** |

## 2. 실증 결과 (전부 비용후·OOS·paper)
| sleeve / book | Sharpe | CAGR | maxDD | 비고 |
|---|---|---|---|---|
| equity MN L/S (mom+qual+rev) | 0.31 | +2.6% | −21% | modest·**5x비용 사망** |
| ETF trend+vol overlay | 0.85 | +9.7% | −16% | **regime-flattered**·long-flat=net-long beta |
| short-term reversal (3번째 후보) | **−1.07** | −8.3% | −61% | **FAIL**(gross도 음수·턴오버 937%) = 가짜알파 거부 |
| **50/50 combo (eq+ov)** | **0.82** | +6.4% | **−10.4%** | corr(eq,ov)=+0.06 → 분산: vol 7.9%·DD↓·2021-26 Sh 1.11 |
| combo + leverage (1.8x avg) | 0.87 | +11.9% | −18% | ₩100M→2.77억(9년)·연 8/10 양수 |
| **combo 비용 스트레스** | 1x **0.82** / 2x **0.70** / 3x 0.59 / **5x 0.35** | | | equity 단독 5x 사망 vs **결합 5x 생존**(분산이 cost도 완충) |
| ML bake-off (ridge/GBM, OOS) | ridge +0.15·GBM +0.02 | | | **선형 0.33 못 넘음** = ML 무증분 |

## 3. 아키텍처 (8레이어) + 상태
```
1 데이터인프라    ✅ Sharadar 주식+ETF/LETF/vol·PIT·survivorship·manifest/hash (API-free)
2 신호/모델팩토리  ✅ 동결 feature(value/quality/momentum/lowvol/event)+trend/vol · 모델 CONSTRAINED
3 alpha ensemble  ✅ 무상관 sleeve 결합(equity MN + ETF trend) = 핵심 lever
4 portfolio opt.  △ 단순(quintile-EW·50/50) — 정교화 DEFER(Codex: 효과<위험)
5 risk engine     ✅ 결정적 veto: fractional-Kelly 사이징·4 kill·gap추정 (acceptance 4/4)
6 execution       ✅ per-name 체결(spread/impact/borrow/부분체결) smoke 4/4 — book 통합 남음
7 monitoring/kill ✅ K1~6 kill·daily 메트릭·heartbeat·promotion gate smoke 8/8 — book 통합 남음
8 거버넌스         ✅ promotion gate가 backtest 차단(forward 0개월·DD>15%)·LLM off-path·human capital gate
```

## 4. ★ 정직한 자체 평가 (리뷰어가 알아야 할 약점)
1. **combo Sharpe(0.82/0.87)는 trend sleeve(0.85)가 견인 → 2017–2025 강추세·저금리·불장 레짐 flattered.** trend long-run Sharpe는 보통 0.4–0.6. 2022 −13%가 tail. **forward 기대는 Sharpe ~0.6, CAGR 한 자리수로 깎아서 봐야.**
2. **전부 backtest·single 사전등록 shot·paper. forward/live track 0개월.** promotion gate(live Sharpe≥0.8·12mo OOS·DD≤15%)는 *의도적으로* 미충족.
3. **ETF trend overlay는 long-flat = net-long 주식 beta**(진짜 시장중립 아님). vol-regime de-risk만이 crash 방어. 2008류 미테스트(데이터 2016~).
4. **equity sleeve는 modest(0.31)+cost-fragile**(단독 5x 사망). 결합이 가려주지만 standalone 약함.
5. **레버리지는 Sharpe 안 올림**(vol만 키움). "공격적"(−18% DD) vs "promotable"(DD≤15%) 상충 — 승격하려면 저레버.
6. 데이터창 2016–2026(한 레짐·COVID/2022 포함, 2008 제외)·단일 유니버스(top-1500 중대형).

## 5. ★ 리뷰어가 공격/검증해줬으면 하는 것
- **trend overlay 0.85가 레짐 아티팩트인가?** 다른 기간/OOS·turnover·진짜 net beta·2008류 스트레스.
- **corr +0.06이 forward에 유지되나?**(분산 전제의 핵심) rolling 상관·레짐별.
- **비용 가정 현실성**(tier 5/10/15·25/45/75bp·sqrt impact·borrow 0.5%) — 너무 낙관?
- **PIT/look-ahead 무결성**: SF1 datekey PIT·closeadj·SP500 멤버십 역재생·survivorship — 누수 없나.
- **leverage/vol-target procyclicality·gap 리스크**·kill-switch 설계 적정성.
- **trial/multiple-testing**: 여러 사전등록 테스트 누적 → 결합 book에 DSR/PBO·trial ledger 정식 적용 필요(아직 미적용).

## 6. Artifacts (어디 보면 되나)
- **정본 결정/설계:** `integrated/` — `V3_Locked_Decisions_and_Master_Plan`(+v0.2 Codex반영)·`V3_Model_Selection_Council_Decision`(모델공간)·`V3_Design_Specs`(데이터/리스크/모니터링)·`US_Public_Data_CrossSectional_Chapter_Final_Lock`(v1 negative)·`PROJECT_MAP`.
- **코드:** `phase1a/engine/` — `data·universe·features·cost·evaluate·kills·report·run·configs`(검증엔진) + `risk_engine·book_runner·execution·monitor`(OS 척추) + `overlay_alpha·combined_book·aggr_book·model_bakeoff`(전략). `legacy/`=원본 보존.
- **결과:** `phase1a/reports/` (B0~B5·quarantine·event·PEAD·overlay·sleeve3·model-selection deep-research) · `outputs/engine/*.csv`(NAV/ledger/regression).
- **데이터:** `phase1a/outputs/raw/`(동결 snapshot + `manifest.json` + `HASHES.txt`) · **재현 검증:** `python engine/data.py validate`.
- **이력:** `phase1a/registry/phase1a_milestones.csv`(44 milestone, 시간순 전 결정).

## 7. 현재 위치 / 남은 일
- **계획·설계 100% LOCKED**(모델선택 council이 마지막 열린 질문 닫음). 큰 결정 0.
- **남은 = 구현/통합:** sleeve+execution+monitor → **하나의 standing 자율 루프** + **forward paper 추적 시작**(promotion gate 12mo 시계). 모델 정교화엔 시간 안 씀(council).
- **핵심 질문(리뷰 포인트): trend sleeve의 forward 생존 + combo 무상관 지속 + 비용/PIT 현실성.** 이게 견디면 book은 진짜, 아니면 equity sleeve만 남는 modest book.

---

## 8. 독립 적대 리뷰 (Codex) — 평결: REVISE, 현 상태 fundable 아님
*(이 프로젝트의 standing 적대 리뷰 도구 Codex가 §0–7을 공격. 웹검색 on. 우리가 자초한 검토 — 정직히 전재.)*

1. **"전략"의 실체는 대부분 ETF beta timing.** 0.85 trend sleeve가 전부고 equity L/S(0.31)는 "noise with branding." 2016–2026 = 후-GFC·저금리·QE·미국주식 지배 = equity 추세추종이 *깨끗해 보이도록 고른 바로 그 기간*. **정직 forward: trend sleeve net 0.35–0.55(고르면 0.45)·combo 0.35–0.55(0.6도 후함).** 로버스트한 trend는 *자산군 분산 선물*(Hurst/Ooi/Pedersen·Moskowitz)이지 15개 주식연계 ETF의 200d 룰이 아님.
2. **"무상관 sleeve"는 과장.** +0.06은 benign 샘플 아티팩트, 구조적 아님. L/S엔 숨은 노출(size·liquidity·momentum-crash·quality·financing). trend은 추세 양일 때 net-long beta. **스트레스 시 forward 상관 +0.25~+0.60**(분산이 필요한 바로 그때 함께 손실). 2018Q4·2022·2008류.
3. **비용 여전히 sanitized.** $75k선 impact 아니라 *운영+세금* drag가 문제: same-close 체결·de-risk일 spread/auction·**borrow locate/recall·Reg SHO·margin/rebate·corp action·ETF 분배·미국 단기차익 ordinary-income 세금·wash-sale**. flat borrow 0.5%는 *easy-to-borrow 대형주만* 아니면 fantasy. "5x 생존"은 누락비용이 선형 bps가 아니라 *강제 미체결·recall·gap·세금*이면 약함.
4. **누수는 타이밍에 숨는다(우선 점검).** ★**ETF 신호 same-close 실행=오염**(우리 코드 확인: a0 종가신호로 a0 종가 진입 → next-open/close 필요) · SF1 datekey(calendardate 아님) · SP500 멤버십 역재생 · 폐지종목 잔존+delisting return · ETF survivorship(15개 ex-ante 선택?) · adjusted price future-artifact · 리밸런스 캘린더(주문 전 모든 값 known). **가장 위험 = same-day close 신호 실행 / 펀더 as-of 오용.**
5. **레버리지 framing 자기모순.** 1.8x/−18% DD가 이미 15% 게이트 위반 → 승격제품이 자기 리스크 제약 불충족. vol-target/kill은 procyclical(급등후 컷·잔잔할때 재진입=난도질). gap 리스크는 일별로 못 막음(룰 깬 종가 *후* 청산).
6. **이게 가짜일 단 하나의 가장 큰 이유:** *in-sample equity beta timing 백테스트를 다변화 multi-sleeve book으로 분장*한 것일 수 있음. 반복가능 edge를 증명 못 함 — 200d equity trend가 친화적 2016–2026 레짐서 잘 보였고 약한 L/S를 구제했음을 증명할 뿐.
- **"$75k 네 돈 지금 넣겠나? NO."** 바꿀 단 하나: **잠긴·timestamp된 6–12개월 paper→live forward run**(broker-grade fills·**next-bar 실행**·borrow/locate 로그·세금인식 회계·사전선언 룰), 거기서 ETF sleeve가 same-close/유니버스 누수 없이도 양의 위험조정수익 유지.

### → 우리 대응 (LOCKED next)
Codex 평결 수용. **현 결과 = 후보지 결론 아님.** 다음 필수: ① **next-bar 실행으로 전 sleeve 재측정**(same-close 누수 제거, Sharpe 하향 예상) ② 비용/세금/borrow 현실화 + 진짜 net-beta 측정 ③ 스트레스 상관 재측정 ④ trial ledger + DSR/PBO ⑤ **6–12mo forward paper(promotion gate 시계)**. live는 그 후에만, human gate.
