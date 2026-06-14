# PRAMANA A2 — Risk Dashboard and LLM Council

## 0. 핵심 원칙

LLM은 상태 판정만 한다. 비중변경은 사전 정의된 mapping engine이 한다.

```text
LLM = 정보참모
Mapping Engine = 비중 결정자
Ledger = 실제 반영자
```

---

## 1. Leadership Risk Score

감시 대상:

```text
NVDA, MSFT, AAPL, AMZN, GOOGL, META, AVGO, TSLA, AMD, NFLX/COST
```

각 종목 체크:

```text
20일선 이탈
50일선 이탈
high-volume down day
earnings gap-down
VWAP 아래 마감
QQQ 대비 상대약세
negative filing/news
```

점수:

```text
0~10 = GREEN
11~25 = YELLOW
26+ = RED
```

행동:

```text
GREEN: TQQQ 유지/증액 가능, Attack 허용
YELLOW: TQQQ 증액 금지, Attack half
RED: TQQQ 신규매수 금지, Attack/Moonshot 신규 금지
```

---

## 2. Market Stress

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

상태:

```text
GREEN/YELLOW/RED
```

---

## 3. TQQQ Decay State

정의는 `06_TQQQ_BOOSTER_MODULE.md` 참조.

상태:

```text
GREEN: 추세 좋고 변동성 감당 가능
YELLOW: 조심
RED/ZONE: 횡보 고변동, 증액 금지
```

---

## 4. LLM Narrative Risk

LLM 입력:

```text
AI/반도체 narrative
빅테크 capex 우려
금리/인플레
규제/반독점
earnings call tone
주요 뉴스
EDGAR/8-K/10-Q/10-K 변화
```

LLM 출력:

```json
{
  "narrative_state": "GREEN|YELLOW|RED",
  "reasons": ["", "", ""],
  "affected_sleeves": ["QQQ", "TQQQ", "Attack", "Moonshot"],
  "forbidden_actions": [],
  "human_review": []
}
```

금지:

```text
LLM 매수/매도 결정 금지
LLM 비중 숫자 제안 금지
LLM 성공확률 확정 금지
```

---

## 5. Daily War Plan

매일 장 전 생성.

파일:

```text
reports/A2_daily_war_plan.md
outputs/a2_live/war_plan.json
```

섹션:

```text
1. Market state
2. Leadership state
3. TQQQ state
4. Attack permission
5. Moonshot permission
6. Vault state
7. Top risks
8. Attack candidates
9. Moonshot draft candidates
10. Forbidden actions today
11. Human review items
```

---

## 6. LLM Council Roles

초기에는 단일 LLM judge로 가능. 확장 시 역할 분리.

```text
Bull analyst: 왜 오를 수 있는가
Bear analyst: 왜 깨질 수 있는가
Forensic analyst: 회계/희석/공시 위험
Judge: GREEN/YELLOW/RED와 요약만
```

---

## 7. Implementation Files

```text
engine/a2_risk_dashboard.py
engine/a2_llm_council.py
engine/a2_daily_war_plan.py
reports/A2_daily_war_plan.md
outputs/a2_live/war_plan.json
```
