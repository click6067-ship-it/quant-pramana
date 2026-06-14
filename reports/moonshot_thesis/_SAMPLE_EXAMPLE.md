# Moonshot Thesis — SAMPLE (예시·실제 포지션 아님·PAPER)

> ⚠️ 이것은 thesis 양식이 어떻게 채워지는지 보여주는 **가공 예시**다. 실제 추천/포지션이 아니다. 매수권 0.
> 실제 후보는 `TICKER.md`로 작성하고 `a2_moonshot_draft.py`로 점수화한다.

| 필드 | 값 |
|---|---|
| **Ticker** | EXMPL (가상) |
| **Grade** | M1 (판정일 명확 + R/R 4:1 + Hard NEG 없음) |
| **Thesis** | Phase 3 임상 1차 판독 — 시장은 실패를 ~80% 가격에 반영했으나 mechanism/선행 데이터상 성공 확률이 그보다 높다고 판단 |
| **Catalyst** | Phase 3 topline 판독 (PDUFA 아님·임상 결과) |
| **판정일** | 2026-09-30 (topline 발표 예정 분기) |
| **왜 시장이 틀렸는가** | 소형주·기관 커버리지 부재로 선행 Phase 2 효능 신호가 과소반영 |
| **성공 조건** | 1차 endpoint 통계적 유의(p<0.05) → 재평가 |
| **실패 조건** | endpoint miss 또는 안전성 hold |
| **무효화 조건** | 판정일 전 임상 중단(clinical hold) 공시 |
| **최대손실** | 포지션의 −60% (자본의 1.5R = A2 NAV의 0.75%) |
| **Reward/Risk** | 4:1 (성공 시 +250%, 실패 시 −60%) |
| **P_up_human** | 0.35 (사람 입력·상한 0.40 준수·LLM 아님) |
| **Tail risk** | 임상 실패 시 going-concern·후속 유증 위험 → 즉시 종료 룰로 제한 |
| **Exit plan** | 2배→원금회수 / 3배→절반 Vault / clinical hold 공시→즉시 종료 / 9-30 경과 시 강제 리뷰 |

## EV 계산 (a2_moonshot_ledger.ev)
- P_up 0.35 × upside +250% − P_down 0.65 × downside −60% − tail − cost
- = 0.875 − 0.39 = **+0.485 (양의 EV·R/R 4:1)** → M1 자격. 단 P_up은 사람 추정(불확실)·소표본 1회 베팅.

## LLM bull case (사실+출처 timestamp만)
- Phase 2 (가상 NCTxxxx, 2025-06 발표) 1차 endpoint 충족 사례 인용 — *미래 주가/사후 분석 금지*.

## LLM bear case (severity)
- 소형 바이오 Phase 3 단독 자산 실패율 역사적으로 높음(severity HIGH) → sizing 1.5R 상한·물타기 금지.

## Hard NEG 체크
- [ ] 희석/ATM — 현재 없음(현금 12개월 runway 가정)
- [ ] 상폐/reverse split — 없음
- [ ] 회계/going concern — 임상 실패 *후*에만 발생 → 진입 시점엔 없음

## Draft board 점수 (예시)
catalyst_clarity 3 · time_to_catalyst 2 · reward_risk_score 3 · neg_risk_low 2 · dilution_risk_low 2 · liquidity 1 · narrative_strength 3 · llm_bear_low 1 · theme_concentration_low 2 · tail_risk_low 1 → **20/30 (67%)**
