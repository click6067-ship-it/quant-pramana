# 08 — Moonshot Module

## 1. 역할

Moonshot은 **큰 비대칭 thesis 베팅**이다.

```text
기본 비중: 10%
허용 범위: 0~15%
목표: 2x~5x 이상 가능성이 있는 event/thesis를 작은 손실 한도로 포착
```

Moonshot은 분봉매매가 아니다. Moonshot은 thesis와 판정일이 핵심이다.

## 2. 후보 유형

```text
FDA/임상 결과
소송 판결
M&A 가능성
규제 승인
대형 계약
파산 회생
구조조정
숏스퀴즈
AI/전력/반도체/바이오 핵심 테마
복잡한 8-K/10-Q/10-K mispricing
```

## 3. 필수 thesis 필드

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

## 4. 진입 조건

```text
thesis 명확
판정일 있음
Reward/Risk ≥ 3:1
EV > +0.5R
최대손실 사전확정
Hard NEG 없음
LLM bull/bear case 작성
Moonshot Draft Board 상위 후보
```

## 5. 금지

```text
판정일 없는 Moonshot
Hard NEG 있는 Moonshot
그냥 꿈
P_up 근거 없는 진입
Reward/Risk < 3:1
최대손실 불명확
손실 중 물타기
```

## 6. 사이징

```text
기본 = 1R
강한 thesis = 2R
최대 = 3R
1R = A2 NAV의 0.5% 손실
공격모드 1R = A2 NAV의 1.0% 손실
Moonshot sleeve 전체를 한 번에 사용 금지
```

## 7. P_up 과대평가 방지

```text
LLM은 P_up 확률을 결정하지 않음
LLM은 bull/bear case만 작성
사람의 P_up 입력 기본 상한 40%
P_up 60% 이상은 특별 사유 없으면 금지
```

## 8. Moonshot Draft Board

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

## 9. Optionality Queue

```text
Queue 1: 판정일 30일 이내
Queue 2: 판정일 90일 이내
Queue 3: 장기 thesis
```

가장 가까운 catalyst부터 배정.

## 10. Moonshot Vault

```text
2배 → 원금 회수
3배 → 절반 Vault
thesis 깨짐 → 즉시 종료
판정일 경과 → 강제 리뷰
```

## 11. Thesis Decay Timer

```text
판정일 경과 후 업데이트 없음 → 강제 리뷰
catalyst 지연 → thesis decay
negative filing 발생 → 즉시 재평가
```
