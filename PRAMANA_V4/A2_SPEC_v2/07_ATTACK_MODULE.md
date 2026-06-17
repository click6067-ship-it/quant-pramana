# 07 — Attack Module

## 1. 역할

Attack은 **당일/초단기 급등주·모멘텀 공격 sleeve**다.

```text
기본 비중: 10%
허용 범위: 0~20%
보유 기간: 기본 당일, 강한 경우 1~3일
목표: 작은 손실로 빠르게 진입하고, 수익은 Vault/익절로 회수
```

## 2. Attack 후보 유형

```text
A. Catalyst Confirmed Momentum
B. Delayed Recognition
C. Leadership Rotation
D. Bollinger Squeeze Breakout
E. Gap + RVOL + ORB + VWAP day trade
```

## 3. 데이터

```text
Sharadar: 일봉 필터/유동성/PIT/fundamental
EDGAR: NEG/Catalyst
yfinance 5m/15m: PROXY 분봉
Polygon/Databento/Alpaca SIP: 실전급 분봉 option
LLM: catalyst/narrative 요약
```

## 4. 진입 조건

A/B catalyst 또는 강한 momentum trigger 중 하나 필요.

그리고 아래 확인:

```text
RVOL entry-time 통과
VWAP 위
ORB15 돌파 또는 전일 고점 돌파
Bollinger squeeze breakout 또는 upper band expansion
Leadership RED 아님
Market Stress RED 아님
Attack token 있음
```

## 5. Bollinger 전략

Bollinger는 단독 매수 신호가 아니다.

사용:

```text
volatility squeeze 후 상단 확장
급등주 모멘텀 confirmation
ORB/VWAP/RVOL과 결합
```

금지:

```text
Bollinger 상단 터치만 보고 매수
횡보장에서 반복 매수
```

## 6. NEG 처리

Attack은 Moonshot과 다르게 Hard NEG를 완전 금지로만 쓰지 않는다.

```text
Hard NEG + 급등주:
- paper-only 또는 0.25R~0.5R
- overnight 금지
- VWAP 이탈 즉시 청산
- 물타기 금지
- high-risk flag 표시
```

하지만 아래는 매우 주의:

```text
상폐 위험
재무제표 신뢰 불가
회계 문제
반복 유증
```

이 경우 실전 승격 금지, paper-only.

## 7. Attack 등급

| 등급 | 조건 | 사이즈 |
|---|---|---|
| A | strong catalyst + clean filing + RVOL/VWAP/ORB | 1R |
| B | catalyst 있음 + 일부 confirmation | 0.5R |
| C | momentum only | paper watch |
| D | reject | 금지 |

## 8. Attack Token

```text
매주 3 token
A급 attack = 1 token
B급 attack = 0.5 token
손실 trade = 다음 주 token -1
+2R 이상 승리 = 다음 주 token +1
Leadership RED = token 0
```

## 9. 청산

```text
-1R 손절
+1R → stop breakeven
+2R → 1/3 익절
+3R → 1/3 Vault
VWAP 이탈
ORB low 이탈
time stop
장마감 전 청산 기본
```

## 10. Overnight

기본 금지.

허용 조건:

```text
A급 catalyst
종가 VWAP 위
strong close
Market not RED
NEG 없음
```

## 11. blind/PIT backtest

분봉 과거 데이터가 없는 경우:

```text
daily approximation만 사용
DATA_QUALITY=DAILY_PROXY
```

분봉 결과는 유료 provider 전까지 실전 검증으로 부르지 않는다.
