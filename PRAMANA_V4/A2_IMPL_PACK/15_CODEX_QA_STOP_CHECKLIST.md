# PRAMANA A2 — Codex QA / STOP Checklist

이 문서는 구현 후 Codex 검수 전에 Claude가 스스로 확인해야 하는 체크리스트다.

---

## 1. Look-ahead

- [ ] 모든 daily state는 shift(1) 되었는가?
- [ ] close(t)로 계산한 신호가 return(t)에 적용되지 않는가?
- [ ] RVOL은 entry-time cumulative volume 기준인가?
- [ ] EDGAR filing은 acceptance timestamp 이후에만 사용되는가?
- [ ] 월평균/미래 평균 가격으로 시작값을 만들지 않았는가?

---

## 2. Live / Backtest 분리

- [ ] live ledger는 inception 이후만 포함하는가?
- [ ] 2016~ backtest를 live ₩1억으로 라벨링하지 않았는가?
- [ ] dashboard에 Historical Backtest와 Live Paper가 분리되어 있는가?

---

## 3. Vault 회계

- [ ] Vault 이동 시 active capital에서 실제 차감되는가?
- [ ] Hard Vault / Reload Vault 분리되는가?
- [ ] Hard Vault는 재투입 불가능한가?
- [ ] 주1회/월10% 제한이 코드로 enforced 되는가?
- [ ] Vaulted Profit이 표시용 장식이 아닌가?

---

## 4. Capital Accounting

- [ ] TOTAL_NAV = sleeve values + cash + vault인가?
- [ ] Attack/Moonshot empty slot이 cash로 반영되는가?
- [ ] target_weights와 actual_weights가 분리되어 있는가?
- [ ] weights sum ≈ 1.0인가?
- [ ] 음수 cash가 발생하지 않는가?

---

## 5. Benchmarks

- [ ] QQQ benchmark 생성됨?
- [ ] SPY benchmark 생성됨?
- [ ] TQQQ reference 생성됨?
- [ ] A2-Q 생성됨?
- [ ] A2-T 생성됨?
- [ ] naive beta book 생성됨?
- [ ] A2가 naive를 못 이기면 이를 명확히 표시하는가?

---

## 6. LLM Governance

- [ ] LLM이 직접 매수/매도 명령을 내리지 않는가?
- [ ] LLM이 비중 숫자를 직접 결정하지 않는가?
- [ ] LLM이 성공확률을 확정하지 않는가?
- [ ] LLM output은 GREEN/YELLOW/RED와 근거로 제한되는가?

---

## 7. Attack / Moonshot

- [ ] Attack과 Moonshot이 다른 schema를 갖는가?
- [ ] Attack은 day strategy로 설계되었는가?
- [ ] Moonshot은 thesis와 판정일이 필수인가?
- [ ] NEG Gate가 Attack/Moonshot에 다르게 적용되는가?
- [ ] R sizing이 기록되는가?
- [ ] thesis decay timer가 있는가?

---

## 8. Secrets / Security

- [ ] API key가 repo에 커밋되지 않았는가?
- [ ] .env는 gitignore에 있는가?
- [ ] dashboard에 secrets가 노출되지 않는가?

---

## 9. Verdict Labels

구현 결과는 반드시 라벨을 가진다.

```text
PASS
REVISE
STOP
UNKNOWN
PAPER_ONLY
PROXY_DATA
```

A2는 기본적으로 PAPER_ONLY.
