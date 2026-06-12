# Alpha Lab v1 — 단일 setup 사전등록 프로토콜 v0.1

> **정체:** v1 = *검증 가능한 protocol*(돈 버는 전략 아님). 단일 setup 하나만·사전등록 kill·결과 보기 **전** 작성(goalpost 고정).
> **목표:** v0가 "setup이 데이터로 잡히나"(PASS)였다면, v1 = **"이 setup이 *비용후* 돈 되나"**의 첫 정직한 측정. 안 되면 폐기 = 또 하나의 정직한 negative.
> 상태: **PAPER · 자본권한 0 · RESEARCH_ONLY.** 코어(4-sleeve)와 완전 분리. 2026-06-12. 근거: 용하 지시(2026-06-12).

## 1. 단일 setup (하나만 — 변형 난사 금지)
**Gap-up + RVOL + ORB15 breakout + VWAP hold**
- **진입 조건(전부 충족):**
  - 장초반 **gap-up**(당일 시가 > 전일 종가·임계 사전등록 +1%)
  - **RVOL 상위**(당일 RVOL ≥ 1.5·급등주 1차 필터)
  - 첫 15분 **ORB 상단 돌파**(close > ORB15 high)
  - 돌파 시점 가격이 **VWAP 위**
- **★ look-ahead 차단:** entry = **돌파 확인된 bar의 *종가* 기준 → 다음 bar 시가 체결**(같은 봉 내부 체결 금지). v3서 잡은 same-bar 누수 재발 방지.
- **청산:** +3% 1차 익절 · +5% 2차 · +7% or trailing stop · VWAP 이탈 · ORB 저점 이탈 · time stop(미정의시 장마감). **장마감 전 청산 여부=별도 테스트(overnight 보유는 브레이크 게이트).**

## 2. 리스크 한도 (사전등록)
- paper notional **2~5%** / 트레이드 (자본권한 0)
- 한 종목 손실 한도 **0.25~0.5%**
- 하루 최대 손실 **1%**
- **금지:** 저유동성·넓은 스프레드·무뉴스 잡주(첫 버전은 유동성 필터로 근사)

## 3. 브레이크 (공격 허용/중지 — 코어 4-sleeve 면역·계좌 > 시장)
**계좌 기준(최우선):** 하루 −1%→당일 신규금지 · Alpha Lab DD −3%→size 50% · DD −5%→일시중지 · 연속손실 3회→당일중지.
**시장 기준(보조):** SPY/QQQ 200일선 아래→overnight 금지 · VIX/20일 vol 급등→size 축소 · breadth 급락→breakout 제한 · gap-down 연속→장초반 진입금지.

## 4. 반등 (단계적 사다리 — 한 번에 안 켬)
① scanner만 허용 → ② paper entry 기록만 → ③ size 50% paper → ④ 정상 paper size.
복구 신호: SPY/QQQ 5·20일선 회복 · VWAP 위 회복·유지 · ORB 상단 돌파·유지 · RVOL 상승 · breadth 회복 · gap-up 갭 안 메움 · VIX 하락 전환. **바닥 맞히기 아님 = 재개 조건 단계화.**

## 5. 검증 지표 + 사전등록 kill (숫자 없으면 합격 없음)
setup 진입들에 대해 측정:
| 지표 | 합격 방향 |
|---|---|
| ORB 돌파 후 평균 수익(after-cost) | > 0 (스프레드/슬리피지/수수료 후) |
| false breakout 비율 | 과반이면 위험 |
| VWAP 이탈 손절이 손실을 *실제로* 줄이나 | 손절 有 vs 無 비교 |
| +3/+5/+7 익절이 기대값 높이나 | 익절 有 vs hold 비교 |
| **강세장 의존성** | SPY/QQQ 강한 날만 되면 = 시장 베타지 setup 엣지 아님 |
| 하락/횡보장 생존 | down/chop 구간서도 양수? |
| 표본 수 | 너무 적으면 무효(deflated) |

**사전등록 kill:** ① after-cost 평균수익 ≤ 0 ② 강세장에서만 양수(SPY 음수날 음수) ③ false breakout 과반 ④ VWAP 손절이 손실 못 줄임 — **하나라도면 setup DEAD**(폐기·튜닝 금지). 통과해도 자본권한 0 유지·60일+ forward paper·attribution·2-feed 전 Production Candidate 아님.

## 6. 한계 (사전 명시)
- **데이터:** yfinance 5m·60일 rolling·watchlist 고정(유니버스 전체 PIT 스캔 아님→survivorship/selection 편향)·소표본. **방향성 신호지 검증된 엣지 아님.**
- 진짜 검증 = 1단계 유료 intraday(Polygon/Alpaca/QuantRocket)·뉴스/이벤트 timestamp·체결로그.
- ORB류는 비용후 살아남기 어렵다는 선행 부정결과 → **brutal prior**(day-trader ~5%만 수익).

## 7. 추천 순서 (용하)
데이터 QA → universe scanner 확장(상대강도/RVOL) → **단일 setup 프로토콜 고정(이 문서)** → paper trade simulator → 비용/슬리피지 → 60일+ forward paper → *그 후에만* 유료 intraday 검토.
