# Moonshot Thesis — TEMPLATE

> 정본: `pramana_a2_implementation_pack/08_MOONSHOT_MODULE.md` §5.
> 규율: thesis·판정일 없으면 진입 금지(신앙 베팅 차단). LLM = bull/bear case만. **P_up_human = 사람이 입력**(LLM이 확률 결정 ❌·상한 40%·≥60%는 특별사유). Hard NEG = 절대 금지. PAPER·자본권한 0.
> 이 파일을 `TICKER.md`로 복사해 채운다. `a2_moonshot_draft.py`가 draft_board에서 점수·순위(상위 1~2개만 진입 자격).

| 필드 | 값 |
|---|---|
| **Ticker** | |
| **Grade (M1/M2/M3)** | M1=판정일+R/R≥3+NEG없음 / M2=narrative만→Attack격하 / M3=금지 |
| **Thesis (한 줄)** | 왜 이게 비대칭 베팅인가 |
| **Catalyst** | 무엇이 재평가를 촉발하나 |
| **판정일 (verdict_date)** | YYYY-MM-DD (이 날까지 catalyst 없으면 강제 리뷰) |
| **왜 시장이 틀렸는가** | mispricing의 출처 |
| **성공 조건** | 데이터로 평가 가능한 조건 |
| **실패 조건** | |
| **무효화 조건 (invalidation)** | thesis가 깨졌다고 인정하는 선 |
| **최대손실 (max_loss)** | 절대 금액/비율 |
| **Reward/Risk** | ≥ 3:1 필수 |
| **P_up_human** | 사람 입력·상한 0.40 |
| **Tail risk** | 희석/유증/상폐/회계/going-concern 점검 |
| **Exit plan** | 2배→원금회수 / 3배→절반 Vault / thesis깨짐→즉시종료 / 판정일경과→강제리뷰 |

## LLM bull case (사실+timestamp 출처만·미래결과 금지)
- 

## LLM bear case (severity 평가 포함)
- 

## Hard NEG 체크 (하나라도 YES면 Moonshot 금지 → Attack 0.25R로만)
- [ ] 희석/반복 ATM offering
- [ ] 상장폐지 위험 / reverse split
- [ ] 회계 문제 / 재무제표 신뢰 불가 / going concern

## Draft board 점수 (0~3 각 축·`a2_moonshot_draft.py`)
catalyst_clarity · time_to_catalyst · reward_risk_score · neg_risk_low · dilution_risk_low · liquidity · narrative_strength · llm_bear_low · theme_concentration_low · tail_risk_low
