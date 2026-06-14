# PRAMANA A2 — Moonshot Module

## 0. 정의

Moonshot Sleeve는 맞으면 크게 먹고 틀리면 손실을 감수하는 비대칭 베팅이다.

```text
Moonshot = 백테스트 알파가 아니라 thesis 기반 high-risk event bet
```

---

## 1. 비중

```text
Base: 10%
Range: 0~15%
```

---

## 2. Moonshot 후보 유형

```text
1. FDA/임상 결과
2. 소송 판결
3. M&A 가능성
4. 규제 승인
5. 대형 계약
6. 파산 회생
7. 구조조정
8. 숏스퀴즈 가능성
9. AI/전력/반도체/로봇/바이오 등 큰 테마 핵심 후보
10. 복잡한 8-K/10-Q/10-K mispricing
```

---

## 3. 진입 필수 조건

```text
thesis 명확
판정일 있음
Reward/Risk ≥ 3:1
최대손실 명시
Hard NEG 없음
LLM bull/bear case 작성
P_up_human 기록
Tail risk 기록
```

---

## 4. Moonshot 등급

```text
M1 = 판정일 명확 + Reward/Risk ≥ 3:1 + NEG 없음
M2 = narrative 강하지만 catalyst 약함 → Attack으로 격하
M3 = 그냥 꿈 → 금지
```

---

## 5. Thesis Template

```text
Ticker:
Thesis:
Catalyst:
판정일:
왜 시장이 틀렸는가:
성공 조건:
실패 조건:
무효화 조건:
최대손실:
Reward/Risk:
P_up_human:
LLM bull case:
LLM bear case:
Tail risk:
Exit plan:
```

---

## 6. P_up Rule

LLM은 확률을 결정하지 않는다.

```text
LLM = bull/bear case 작성
Human = P_up_human 입력
기본 P_up 상한 = 40%
P_up ≥ 60%는 특별 사유 없으면 금지
```

---

## 7. Sizing

```text
기본 = 1R
강한 thesis = 2R
최대 = 3R
Moonshot sleeve 전체 10%를 한 번에 쓰지 말 것
```

---

## 8. Hard NEG Rule

Moonshot에서 Hard NEG는 금지.

```text
희석/유증
상장폐지 위험
회계 문제
going concern
재무제표 신뢰 불가
반복 ATM offering
reverse split risk
```

---

## 9. Moonshot Vault Rule

```text
Moonshot 2배 → 원금 회수
Moonshot 3배 → 절반 Vault
Moonshot thesis 깨짐 → 즉시 종료
판정일 경과 → 강제 리뷰
```

---

## 10. Thesis Decay Timer

```text
판정일 지나도 catalyst 없음 → review
thesis 관련 뉴스 반대 방향 → review
가격이 -1R 근접 → review
Hard NEG 발생 → immediate review/exit
```

---

## 11. Draft Board

후보를 바로 사지 않는다. draft board에서 순위를 매긴다.

점수:

```text
Catalyst clarity
Time to catalyst
Reward/Risk
NEG filing risk
Dilution risk
Liquidity
Narrative strength
LLM bear case severity
Theme concentration
Tail risk
```

상위 1~2개만 실제 진입 가능.

---

## 12. Ledger Schema

`positions/moonshot.json`

```json
{
  "draft_board": [],
  "positions": [
    {
      "ticker": "",
      "grade": "M1|M2|M3",
      "thesis_file": "reports/moonshot_thesis/TICKER.md",
      "entry_date": "",
      "entry_price": 0,
      "size_r": 1,
      "max_loss": 0,
      "judgement_date": "",
      "status": "OPEN|REVIEW|CLOSED"
    }
  ],
  "closed_theses": []
}
```

---

## 13. Implementation Files

```text
engine/a2_moonshot_ledger.py
engine/a2_moonshot_draft.py
reports/moonshot_thesis/*.md
```
