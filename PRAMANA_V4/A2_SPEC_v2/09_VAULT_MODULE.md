# 09 — Profit Vault Module

## 1. 목적

Vault는 평가익을 실제로 잠그는 회계 장치다.

```text
A2가 QQQ를 이겼을 때 수익 일부를 전장에서 빼낸다.
Vault는 표시용이 아니다.
Vault 이동 시 active capital에서 실제 차감된다.
```

## 2. 핵심 ledger

파일:

```text
positions/vault.json
outputs/a2_live/vault_ledger.csv
reports/A2_weekly_vault_review.md
```

스키마:

```json
{
  "hard_vault": 0,
  "reload_vault": 0,
  "last_vault_date": null,
  "month_vault_total": 0,
  "a2_excess_hwm": 0,
  "vault_events": []
}
```

## 3. Vault In 조건

```text
A2_excess = A2_total_return - QQQ_total_return
A2_excess_HWM = max(previous_HWM, A2_excess)
```

발동 조건:

```text
1. 새로운 excess HWM 갱신
2. A2 absolute NAV가 수익 상태
3. QQQ보다 덜 잃은 것만으로는 발동 금지
4. 주 1회 제한 통과
5. 월간 Vault 이동 ≤ 전체 NAV 10%
```

## 4. Vault In 비율

```text
A2 excess HWM ≥ +4%p  → 신규 초과수익분 25% Vault
A2 excess HWM ≥ +8%p  → 신규 초과수익분 추가 25% Vault
A2 excess HWM ≥ +12%p → 신규 초과수익분 50% Vault
```

## 5. Vault source

수익 난 sleeve에서만 이동.

우선순위:

```text
1. TQQQ realized profit
2. Attack realized profit
3. Moonshot realized profit
4. QQQ profit
```

손실 중 sleeve에서 Vault 이동 금지.

## 6. Hard / Reload Vault

```text
Vault inflow 70% → Hard Vault
Vault inflow 30% → Reload Vault
```

Hard Vault:

```text
절대 재투입 금지
공격자금에서 제외
가능하면 별도 계좌/별도 ETF/별도 브로커
```

Reload Vault:

```text
조건부 재투입 가능
한 번에 Reload Vault 25%만 사용
월 1회 이하
```

## 7. Vault Out 조건

Reload Vault만 사용 가능.

```text
Leadership GREEN
TQQQ Decay GREEN
Market Stress not RED
QQQ 20일선 회복
A2 drawdown 회복 중
Attack A급 후보 존재
```

Hard Vault 사용 금지.

## 8. Dynamic Sell / Vault Timing

Vault In은 단순 수익률만이 아니라 위험 신호도 본다.

Vault In 강화 조건:

```text
A2 excess HWM 갱신
AND Leadership YELLOW/RED
OR TQQQ Decay YELLOW/RED
OR LLM Narrative YELLOW/RED
```

즉, 이겼고 위험이 커질 때 더 강하게 잠근다.

Vault Out은 위험이 줄고 기회가 확인될 때만.

## 9. Moonshot Vault

```text
Moonshot 2배 → 원금 회수
Moonshot 3배 → 절반 Vault
Moonshot thesis 깨짐 → 즉시 종료
```

## 10. 완료 기준

```text
Vault 이동이 active NAV에서 실제 차감됨
Hard/Reload balance가 dashboard에 표시됨
Vault-adjusted NAV와 active NAV가 분리됨
주1회/월10% 제한이 코드로 enforce됨
Vaulted Profit이 성공지표로 사용 가능
```
