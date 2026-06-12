# Alpha Lab v0 — Intraday Data Infra 설계 (전략 아님·데이터부터)

> **정체:** Alpha Lab v0 = *intraday 데이터 인프라*다. **전략/돈벌기 아님.** 첫 목표 = **"내가 보고 싶은 setup(VWAP/ORB/급등주)이 데이터로 잡히는지"** 확인.
> 상태: **PAPER · 자본권한 0 · RESEARCH_ONLY.** 코어(4-sleeve)와 완전 분리·별도 NAV. 2026-06-12.
> 근거: 용하 지시(2026-06-12) — "LETF core overlay 폐기. 다음은 Alpha Lab v0 intraday data infra 설계 하나. 처음부터 전략 만들지 말고 데이터부터."

## 0. 두 개의 초점 (용하) — 코어 아님, *공격 파트 허용/중지*용
1. **브레이크** = 위험할 때 공격을 끈다 (예측 아님·이미 위험해진 시장서 *덜 맞게*).
2. **반등 감지** = 다시 좋아질 때 공격을 *천천히* 연다 (바닥예측 아님·재진입 절차).
- **건드리는 대상(공격 파트만):** 급등주 신규진입·VWAP/ORB 단타·position size·하루 손실 한도·overnight 보유. **순수 4-sleeve 코어는 영구 면역**(갈아타기 ❌).
- **★ 계좌 기준 브레이크 > 시장 신호** (더 확실): 하루 −1%→당일 신규금지·계좌 DD −3/−5%→Alpha Lab 중지.

## 1. 데이터 스키마 (정규 컬럼 — 모든 intraday 벤더 공통 타겟)
| 컬럼 | 의미 | yfinance 0단계 | 비고 |
|---|---|---|---|
| ticker | 종목 | ✓ | universe는 일봉 Sharadar서 PIT |
| timestamp (tz=America/New_York) | 봉 시각 | ✓ | tz-aware 필수 |
| open/high/low/close | OHLC | ✓ | |
| volume | 거래량 | ✓ | |
| is_premarket | 장전 여부 | ✓ (prepost=True) | <09:30 |
| is_regular | 정규장 여부 | ✓ | 09:30–16:00 |
| vwap | 세션 VWAP | 계산 (Σpv/Σv·세션리셋) | "오늘 수급 평균선" |
| rvol | 상대거래량 | 계산 (당일/20일평균) | 급등주 1차 필터 |
| split/adj | 분할조정 | △ (Adj Close) | 벤더별 확인 |
| event_ts | 뉴스/실적 timestamp | ✗ (0단계 없음) | 1단계 별도 소스 |

## 2. 데이터 전략 (3단계 — 처음부터 고가 데이터 X·Sharadar는 일봉 유지)
| 단계 | 목적 | 데이터 | 상태 |
|---|---|---|---|
| **0** | 패턴 감 잡기·setup 검출 검증 | **yfinance 5m/15m**(60일 한도·premarket ✓) | ← **지금** |
| 1 | 제대로 된 paper lab | Polygon / Alpaca / QuantRocket intraday(1분 2007~) | 데이터 확보 후 |
| 2 | 실거래 전 검증 | broker 체결로그 + 유료 intraday + 2-feed reconciliation | Promotion Gate |
- **Sharadar 역할 불변:** 일봉 core / universe / fundamentals / survivorship-safe 백테스트. **분봉은 별도 벤더**(Sharadar는 EOD 상품·분봉 아님 — 확인됨).
- yfinance 한계 명시: 5m=60일 rolling·1m=8일 → **장기 백테스트 불가**. 0단계는 *append-only 일별 적재*로 forward 축적 + setup 검출 검증용.

## 3. setup 파이프라인 (급등주/VWAP/ORB — paper lab·production 아님)
```
pre-market scan (RVOL·gap·뉴스/실적/테마)
  → 장시작 ORB 박스 형성(첫 5/15/30분 high·low)
  → VWAP 위 유지 확인(매수세 우위)
  → ORB 상단 돌파 진입
  → 익절 +3/+5/+7 또는 trailing stop
  → 청산: VWAP 이탈 / ORB 저점 이탈 / time stop
```
- **ORB caveat:** 최근 OHLCV intraday 연구서 ORB류가 비용후 안정적으로 살아남기 어렵다는 부정적 결과 → **production 아니라 paper lab.** brutal prior(day-trader ~5%만 수익).

## 4. 브레이크 / 반등 (측정만·자본권한 0 — v0은 *데이터로 잡히나*까지)
**브레이크 신호(공격 축소·끄기):** 20/50일선 이탈→신규 축소 · 200일선 이탈→LETF/overnight 금지 · VIX 급등→size 축소 · breadth 급락→돌파 신뢰도↓ · gap-down 연속→장초반 진입금지 · **계좌 DD −3/−5%→중지 · 하루 −1%→당일 신규금지(계좌 브레이크 최우선).**
**반등 신호(단계적 재개·한 번에 다 켜지 말기):** 5/20일선 회복 · VWAP 위 회복·유지 · ORB 상단 돌파·유지 · VIX 하락 · breadth 회복 · gap-up 유지 · 3일 연속 higher-low.
**재개 사다리:** ① paper scan만 → ② intraday만(overnight 금지) → ③ size 50% → ④ 정상.

## 5. v0 산출물 / kill
- **산출물:** `engine/alpha_lab_v0.py` — yfinance 5m 정규화 적재(append-only) + VWAP/ORB/RVOL/premarket 계산 + **setup 스캐너**(오늘 "ORB돌파 & VWAP유지" 종목 리스트). `outputs/alpha_lab/` 적재.
- **v0 합격 = "돈"이 아니라 "setup이 데이터로 잡힘"** (검증됨: NVDA 2026-06-11 ORB돌파+VWAP setup 19 bar 검출).
- **kill(사전):** paper 사전등록 net(비용후) 못 넘으면 전략 폐기 = 또 하나의 정직한 negative 수용. 변형 난사 금지(가설당 1개). 자본권한 0 유지 — 실계좌 주문/margin 붙는 순간 V7 원칙 위반.
