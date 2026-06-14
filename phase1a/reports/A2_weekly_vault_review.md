# A2 Weekly Vault Review — 2026-06-12

> PAPER·자본권한 0. 아래는 **제안(SUGGESTION)**·실제 적용은 사람 게이트. LLM=상태만·숫자=rule engine.

## Vault 상태 (forward live ledger·positions/vault.json)

- **Hard Vault** (영구 잠금·재투입 불가): 0.000% NAV ≈ ₩0.0000억
- **Reload Vault** (재장전 가능·25%/회·월1회): 0.000% NAV ≈ ₩0.0000억
- **A2 excess HWM**: 0.329%p
- **Vault 이벤트 누적**: 0건 (last_date=None)

## 이번 평가 제안 (SUGGESTION)

### 5%p Dynamic Sell/Add

- 🔻 **TRIM tqqq -5%p** — Leadership RED
- 🔻 **TRIM attack -5%p** — Leadership RED

### Vault In/Out

- (없음 — excess HWM 미돌파 또는 Vault Out 게이트 불충족)

## §9 구현 체크리스트

- ✅ Vault In은 실제 ledger에 기록 — positions/vault.json + vault_events.csv append-only
- ✅ Vault Out은 Reload Vault에서만 — apply_reload()는 reload만 차감·Hard 불변 assert
- ✅ Hard Vault는 코드상 재투입 불가 — reinvest_hard()=PermissionError·assert_hard_locked·save 거부
- ✅ 5%p trim/add는 target weights에 반영 — suggest_delta() ±5%p·sleeve_ranges clamp (SUGGESTION·사람 게이트)
- ✅ LLM은 상태만 제공 — state.json risk 라벨만 입력·숫자 산출 0
- ✅ mapping engine이 실제 변경 — classify_vault_in/eval_trim/eval_add = rule engine
- ✅ 매도/trim과 Vault 이동은 별도 이벤트로 기록 — sleeve_adjustments.csv vs vault_events.csv 분리
- 🟡 대시보드에 Vault In/Out/Trim/Add 구분 표시 — a2_live_runner 대시보드 Vault 섹션 존재·Trim/Add 표시 = runner 채택 시
