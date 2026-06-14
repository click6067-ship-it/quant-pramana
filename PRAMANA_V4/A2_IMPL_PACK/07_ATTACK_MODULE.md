# PRAMANA A2 — Attack Module

## 0. 정의

Attack Sleeve는 분봉 기반 단기 급등주·모멘텀 공격 자금이다.

```text
목표: 하루 또는 짧은 기간 안에 수급이 붙은 종목에서 빠르게 수익
기본 보유: 당일
원칙: 오래 보유하지 않음
```

---

## 1. 비중

```text
Base: 10%
Range: 0~20%
```

---

## 2. Attack과 Moonshot 차이

| 구분 | Attack | Moonshot |
|---|---|---|
| 시간축 | 장중~수일 | 수일~수개월 |
| 핵심 | 수급/모멘텀/분봉 확인 | thesis / catalyst / 비대칭 |
| 진입 | ORB/VWAP/RVOL/Bollinger | thesis와 판정일 |
| 청산 | 빠름, 당일 우선 | thesis 깨질 때 또는 목표 달성 |
| NEG 처리 | size 축소/overnight 금지 가능 | Hard NEG 금지 |

---

## 3. Attack 후보 유형

```text
1. Catalyst Confirmed Momentum
2. Delayed Recognition
3. Leadership Rotation
4. Bollinger Squeeze Breakout
5. Gap + RVOL + ORB + VWAP day trade
```

---

## 4. Entry Conditions

### 필수

```text
A/B catalyst or strong momentum trigger
RVOL entry-time 통과
VWAP 위
ORB15 돌파 or 전일 고점 돌파
Leadership RED 아님
Market Stress RED 아님
```

### Bollinger 조건

```text
Bollinger squeeze 이후 상단 확장
또는 상단 밴드 breakout + RVOL
```

### catalyst 없는 경우

```text
C급 paper only
실제 Attack ledger 진입 금지 또는 0.25R 이하
```

---

## 5. Negative Filing 처리

사용자 의도 반영: 급등주 단타에서는 위험공시가 있어도 당일 수급으로 먹고 빠질 수 있음.

```text
Hard NEG + 급등주:
- paper-only 또는 0.25R~0.5R
- overnight 금지
- VWAP 이탈 즉시 청산
- 물타기 금지
```

단, Hard NEG가 있는 종목을 Moonshot으로 승격 금지.

---

## 6. Sizing

```text
1R = A2 NAV의 0.5% 손실
GREEN 환경에서 1R = 1.0%까지 가능
```

```text
A급 = 1R
B급 = 0.5R
C급 = paper only
Hard NEG 단타 = 0.25R~0.5R
```

---

## 7. Intraday Execution Rules

```text
ORB 15분 기본
VWAP regular session 기준
RVOL entry-time only
same-bar execution 금지
bar close 기준 신호 → 다음 bar 진입
```

---

## 8. Exit Rules

```text
-1R 손절
VWAP 이탈
ORB low 이탈
time stop
장마감 전 청산 기본
```

Profit waterfall:

```text
+1R → stop breakeven
+2R → 1/3 익절
+3R → 1/3 Vault
나머지 → trailing stop
```

---

## 9. Attack Token

```text
매주 3 token
A급 진입 = 1 token
B급 진입 = 0.5 token
손실 trade = 다음 주 token -1
+2R 이상 승리 = 다음 주 token +1
Leadership RED = token 0
```

---

## 10. Ledger Schema

`positions/attack.json`

```json
{
  "weekly_tokens": 3,
  "positions": [
    {
      "ticker": "",
      "grade": "A|B|C",
      "catalyst": "",
      "entry_time": "",
      "entry_price": 0,
      "size_r": 0.5,
      "stop_price": 0,
      "take_profit_rules": [],
      "overnight_allowed": false,
      "data_quality": "PROXY|SIP|QUOTE_LEVEL",
      "status": "OPEN|CLOSED"
    }
  ],
  "closed_trades": []
}
```

---

## 11. Outputs

```text
outputs/a2_live/attack_candidates.csv
outputs/a2_live/attack_ledger.csv
outputs/a2_live/attack_closed_trades.csv
```

---

## 12. Implementation Files

```text
engine/a2_attack_scanner.py
engine/a2_attack_ledger.py
engine/a2_attack_tokens.py
engine/a2_intraday_scanner.py
```
