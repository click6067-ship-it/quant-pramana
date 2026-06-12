# Alpha Lab v2 — Event-Driven Momentum 가설 사전등록 v0.1

> **v1과 다른 점: 숫자 튜닝이 아니라 *가설 구조*를 바꿈.** v1=단순 ORB(누구나 봄·"왜 움직이나" 없음·false breakout 56%=DEAD). v2 = **catalyst 있는 종목만**(실적/뉴스/gap)에서 momentum.
> **방법: backtest 아님 → forward paper 로그부터(4~8주).** entry-time only·사후수정 금지·append-only. 후보 품질 형편없으면 유료데이터 살 필요 없음.
> 상태: **PAPER · 자본권한 0 · RESEARCH_ONLY.** 코어(4-sleeve) 면역. 2026-06-12. 근거: 용하 로드맵(2026-06-12).

## 0. 죽은 것 / 산 것 (v1 정산) — 용하: "실패는 기록·폐기는 마·좀 더 지켜보자"
| | 판정 |
|---|---|
| Alpha Lab v0 데이터 인프라 | **유지** |
| v1 단순 ORB/VWAP/RVOL setup | **DEAD 기록**(backtest: false breakout 56%·강세장 베타·RVOL 누수). **단 완전폐기/종결 아님 → forward 관찰 보류**(원형 그대로·튜닝 없이 매일 로그해 진짜 죽었나 더 본다) |
| RVOL 계산(entry-time 누적) | **수정 유지** |
| v1 setup 튜닝(stop/target/RVOL/ORB) | **금지**(=data-mining 부활). *관찰은 튜닝 아님 — 숫자 안 바꾸고 원형 forward 기록만* |
| Production 자본 투입 | **금지** |

## 1. v2 가설 (구조가 다름)
**Event-Driven Momentum** = *catalyst가 있어 움직이는* 종목의 momentum만 본다. "왜 움직이는가"가 있는 돌파.
- **catalyst proxy(무료 가용):** ① 실적발표 근접(±1거래일·yfinance earnings date) ② 큰 overnight gap(뉴스 대리·>+3%) ③ entry-time RVOL 비정상(장초반 누적/과거 평균 ≥ 2). → 셋 중 하나라도 = "이유 있는 움직임" 후보.
- **진입 신호(entry-time only):** catalyst + ORB15 돌파 + VWAP 위 (v0 인프라 재사용).
- **단순 ORB와 차이:** catalyst 필터로 "이유 없는 돌파"(false breakout 다수)를 *진입 전* 걸러냄.
- *진짜 뉴스/8-K/가이던스 catalyst = 유료(다음). 지금은 earnings-date + gap + RVOL proxy.*

## 2. 방법: forward paper 로그 먼저 (backtest ❌)
용하 핵심: "무작정 유료데이터 사지 말고, 무료/임시로 *실시간 후보 생성·기록*이 안정적인지 먼저."
- `alpha_lab_v2_scanner.py` = 매일 1회 후보 scan → **append-only 로그**(`outputs/alpha_lab/v2_forward_log.csv`).
- 기록: 날짜·종목·**왜 뽑혔나**(earnings/gap/RVOL)·entry-time RVOL·진입가(실시간 기준)·진입/청산 신호. **사후수정 금지.**
- **entry-time only**(09:45 시점까지 정보만·look-ahead 차단·v1 RVOL 누수 재발 방지).
- 4~8주 축적 후 평가 — *backtest 성과가 아니라 로그 품질*(후보 남발 안 하나·catalyst 실재하나·forward에서 신호가 의미있나).
- **v1 setup도 같이 forward 관찰(폐기 안 함)**: scanner가 v1 단순 setup을 *원형 그대로*(튜닝 없이) 매일 로그 → backtest서 DEAD였던 게 forward에서도 죽나 확인. v1·v2 후보를 한 로그에 나란히(catalyst 유무 비교). 용하: "좀 더 지켜보자."

## 3. 유료 intraday 데이터 — 보류·조건부
지금 바로 안 산다(첫 setup DEAD·base-rate 낮음·돈/시간↑). 아래 *전부* 충족 시에만 Polygon/Alpaca/QuantRocket 검토:
1. forward paper 로그 4~8주 안정 기록
2. scanner가 후보를 과도하게 남발하지 않음(하루 N개 이내)
3. event/news/catalyst 필터 필요성이 *명확*(proxy로 부족함이 드러남)
4. bid-ask/체결가정 없이는 더 판단 불가한 병목 확인

## 4. 사전등록 kill (forward 로그 평가)
- 하루 후보 남발(평균 > 운영 가능 수) → 필터 무의미
- catalyst 없는 후보가 대부분(gap/RVOL만이고 실재 이벤트 0) → proxy 실패
- forward 로그상 진입 후보의 방향성이 시장 베타와 분리 안 됨(SPY 따라감) → v1과 동일 실패
- **하나라도면 v2 = DEAD 기록**(또 정직한 negative). **단 완전종결 아님 → forward 관찰 보류**(용하: 폐기는 마·좀 더 지켜보자). 튜닝으로 살리기는 여전히 금지(원형 관찰만).

## 5. 한계 (사전 명시)
- catalyst proxy(earnings date + gap + RVOL)는 *진짜* 뉴스/이벤트 아님 → false catalyst 가능. 진짜=유료.
- yfinance earnings date 불안정 가능·5m 60일 한도.
- forward 로그 4~8주 = 짧음·시장 레짐 의존. brutal prior(day-trader <1% 순수익) 유지.
- **이 문서는 가설 등록 + 로그 수집 시작이지 "검증된 엣지" 주장 아님.**

## 6. 로드맵 (용하)
Core: 순수 4-sleeve forward 12개월(코어 그만 만짐) ‖ Alpha Lab: v0 유지·v1 DEAD 기록·**v2 event-driven forward 로그 4~8주 → 그 후 유료 결정.** 금지: v1 튜닝·Production 자본.
