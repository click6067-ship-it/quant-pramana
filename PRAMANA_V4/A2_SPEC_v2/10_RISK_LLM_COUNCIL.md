# 10 — Risk Dashboard & LLM Council

## 1. 원칙

LLM은 정보참모다. 매수/매도 결정자가 아니다.

```text
LLM = 상태 판정, narrative 요약, bull/bear case
Rule engine = 비중 변경
Ledger = 실제 회계
Human = 최종 override
```

## 2. LLM 입력

```text
QQQ/TQQQ 상태
Leadership basket 상태
VIX/VXN
realized volatility
QQQ drawdown
EDGAR filings
NEG Gate candidates
뉴스/공시/실적/테마 narrative
Attack/Moonshot open positions
Vault trigger status
TQ-DH dip classification candidates
```

## 3. LLM 출력

```json
{
  "market_state": "GREEN|YELLOW|RED",
  "leadership_state": "GREEN|YELLOW|RED",
  "tqqq_state": "GREEN|YELLOW|RED",
  "attack_state": "GREEN|YELLOW|RED",
  "moonshot_state": "OPEN|HOLD_ONLY|LOCKED",
  "vault_state": "ACCUMULATE|HOLD|RELOAD_ALLOWED",
  "narrative_state": "GREEN|YELLOW|RED",
  "top_risks": [],
  "top_attack_candidates": [],
  "top_moonshot_candidates": [],
  "forbidden_actions_today": [],
  "human_review_required": []
}
```

## 4. 금지

```text
LLM이 TQQQ 45% 같은 비중 숫자 제안 금지
LLM이 NVDA 매수 같은 주문 결정 금지
LLM이 성공확률 확정 금지
LLM 점수로 자동 진입 금지
```

## 5. Leadership Risk

감시 대상:

```text
NVDA, MSFT, AAPL, AMZN, GOOGL, META, AVGO, TSLA, AMD, NFLX/COST
```

종목별 1점:

```text
20일선 이탈
50일선 이탈
high-volume down day
earnings gap-down
VWAP 아래 마감
QQQ 대비 상대약세
negative filing/news
```

해석:

```text
0~10 = GREEN
11~25 = YELLOW
26+ = RED
```

## 6. Market Stress

체크:

```text
QQQ 20/50/200일선
VIX/VXN
20일 realized vol
QQQ drawdown
gap-down 연속
HYG/IEF credit stress
Treasury yield shock
```

## 7. TQQQ Decay

체크:

```text
QQQ 20일 수익률 ±3% 이내
realized vol 상승
20일 high-low range 확대
TQQQ realized multiple < 2.3 × QQQ
```

## 8. Narrative Risk

LLM이 판정:

```text
AI/반도체 narrative 약화
빅테크 capex 우려
금리/인플레 narrative 악화
규제/반독점 리스크
earnings call tone 악화
```

출력:

```text
GREEN/YELLOW/RED
근거 3~5줄
어떤 sleeve에 영향 있는지
```

## 9. Daily War Plan

매일 장 시작 전 생성:

```text
reports/A2_daily_war_plan.md
outputs/a2_live/war_plan.json
```

내용:

```text
1. 오늘의 market state
2. leadership state
3. tqqq permission
4. attack permission
5. moonshot permission
6. vault state
7. top risks
8. top candidates
9. forbidden actions
10. human review items
```
