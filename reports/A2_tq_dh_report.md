# A2 TQ-DH (TQQQ Dip Harvester) — Report (Phase E)
> 생성 2026-06-14 · backtest 2016-01~2026-06 · PAPER only · 자본권한 0 · **검증된 알파 아님**.
> spec: `PRAMANA_V4/A2_SPEC_v2/11_TQ_DH_DIP_HARVESTER.md` (+09 Vault·13 §E)
> **REAL Reload Vault** = `engine/a2_profit_vault.py` ledger(`outputs/a2_live/positions/vault.json`). 이전 버전의 가짜 'reserve' 변수 제거. **Hard Vault 절대 미사용**(apply_reload만, Hard assert 불변).

## 0. 사전등록 (Pre-registered) 성공·실패 조건 — 결과 보기 전에 박음 (spec §2)
**성공조건 — A2 *with* TQ-DH가 A2 *without* TQ-DH 대비:**
1. final NAV ≥ (같거나 높음)
2. MDD 더 낮음(덜 깊음)
3. 회복기간 더 짧음
4. Vaulted Profit > 0

→ spec §2가 명시: TQQQ buy-and-hold보다 최종 NAV가 *낮아도 평가 가능* (MDD·회복·Vaulted Profit으로 본다).

**실패조건 — 하나라도 해당 시:**
- TQ-DH가 TQQQ drawdown DCA보다 final NAV·MDD **둘 다** 열위
- Reload가 대부분 Type C(구조붕괴)에서 발생 (spec §5: Type C=Reload 금지 → 0이어야 정상)
- Hard Vault를 써야만 성과가 남 (spec §8: Hard 절대 금지 → 코드상 불가)

## 1. 방법론·치환 (정직 라벨)
- **REAL Reload Vault closed-loop**: Vault In(이긴 돈=A2 excess HWM·abs profit)으로 `a2_profit_vault.apply_vault_in`이 NAV에서 차감하며 Hard(70%)/Reload(30%) 적립. dip 분류 시 `can_reload` 게이트 통과하면 `apply_reload`로 **Reload Vault의 25%만** active book(QQQ/TQQQ)에 환원. Hard Vault는 호출조차 안 함(불변 assert).
- **VIX/VXN proxy**: 캐시에 VIX/VXN 없음 → **QQQ 20일 realized volatility(연율화)**로 치환. 라벨 `GREEN/YELLOW/RED-proxy`(calm<20%·elevated<35%). 진짜 term-structure/skew 아님.
- **Leadership/risk_state**: sp500 패널 대형주 10종 vs 50/20일선 비율 (실데이터). forward 모드는 `a2_risk_dashboard.compute()`의 per-name leadership score 사용.
- **Narrative/Earnings/Credit**: LLM·HYG/IEF 미구현 → `narrative_state = N/A-proxy` (정직 공백).
- **NO LOOK-AHEAD**: close_t 분류 → close_{t+1} 체결·수익. 회복확인(10일 고점·follow-through)도 과거 데이터만.
- **Reload 규칙(spec §8)**: 1 reload = Reload Vault 25%, 최소 간격 3거래일, TQQQ sleeve MDD -15% 초과 시 추가 금지, Type C=Reload 금지, Hard Vault 절대 미사용.

## 2. 백테스트 비교 (₩1억 기준·log 차트 = `outputs/a2_live/tq_dh_backtest.png`)

| 전략 | 최종 NAV(배) | 최종 평가액 | MDD | 회복(거래일) |
|---|---:|---:|---:|---:|
| TQQQ_BH | 32.552 | ₩32.552억 | -81.7% | 486 |
| TQQQ_DCA_monthly | 8.947 | ₩8.947억 | -75.7% | 380 |
| TQQQ_DCA_drawdown | 6.765 | ₩6.765억 | -65.4% | 268 |
| QQQ_BH | 6.830 | ₩6.830억 | -35.1% | 278 |
| A2_base | 9.821 | ₩9.821억 | -48.4% | 278 |
| A2_with_TQ-DH | 10.502 | ₩10.502억 | -57.0% | 280 |

## 3. TQ-DH 동작 통계 (REAL Reload Vault)
- 총 reload 횟수: **134** · Type C에서 발생: **0** (0% — spec §5상 0이어야 함)
- reload 자산 분포: {'TQQQ': 106, 'QQQ': 28}
- **REAL Vault 잔액(기말)**: Hard ₩0.907억 · Reload ₩0.092억 · ledger events 347건
- **Hard Vault 단조 비감소(절대 미사용) 증명**: **True** (reload는 apply_reload만 호출 → Hard 불변 assert; Vault In만 Hard 적립)
- **Vaulted Profit** (reload 자산의 체결→최종 누적 이득): **₩0.655억** (+65.45% of 자본)
- dip type 분류 일수: {'NONE': 1687, 'D': 360, 'B': 320, 'A': 137, 'C': 120}
- reload 후 평균 수익: 5일 +0.89% (n=134) · 20일 +4.90% (n=134)
- 신호 로그: `outputs/a2_live/tq_dh_signals.csv` (date·qqq_drawdown·vix_vxn_state·leadership_state·narrative_state·dip_type·action·reload_amount·asset_used·post_reload_return_5d/20d·reload_vault_bal·hard_vault_bal)

## 4. 판정 (Verdict) — 사전등록 조건 대조
**성공조건 (vs A2 without TQ-DH):**

| 조건 | A2 base | A2 with TQ-DH | 통과 |
|---|---:|---:|:--:|
| 최종 NAV(배) | 9.821 | 10.502 | ✅ |
| MDD | -48.4% | -57.0% | ❌ |
| 회복기간(거래일) | 278 | 280 | ❌ |
| Vaulted Profit > 0 | — | ₩0.655억 | ✅ |

**성공조건 종합: ❌ NOT MET (일부 미충족)**

**실패조건:**
- vs drawdown-DCA NAV·MDD 둘 다 열위: 아니오
- reload 대부분 Type C: 아니오
- Hard Vault 의존: 아니오 (Hard 단조 비감소=True·코드상 재투입 불가)

**실패조건 종합: ✅ 실패조건 없음**

## 5. 정직한 결론 (Honest Verdict)
**NOT MET (성공조건 일부 미충족, 명시적 FAIL 트리거 없음).** A2 with TQ-DH NAV=10.50배 vs A2 base 9.82배. spec §2가 예고했듯 최종 NAV에서 TQQQ buy-and-hold(32.6배)를 못 이기는 것은 정상 — 평가는 MDD/회복/Vaulted Profit으로 한다.

핵심 정직 메모: (a) **REAL Reload Vault**만 쓰므로(이긴 돈의 30% 중 25%씩) TQ-DH의 NAV 기여 *상한*이 작다 — 구조적으로 TQQQ buy-and-hold를 NAV로 이길 수 없게 설계됨(의도된 보수성). (b) 강세장 편향 표본에선 'dip을 가려 사는' 절제가 '아무 dip이나 사는' 단순 DCA보다 NAV를 깎을 수 있다. TQ-DH의 진짜 효용은 *긴 하락장 자본 보존*인데 이 표본엔 그 구간이 없어 측정 불가. (c) **Hard Vault 잔액 ₩90.7M은 전 기간 한 번도 빠지지 않았다(단조 비감소)** — 이 결과는 '기계가 약속대로 작동하고 look-ahead 없이 dip을 분류·절제하며 **Reload Vault만** 쓴다'는 **machinery 검증**이지 '수익 알파 입증'이 아니다.

## 6. Caveats (한계 — 결과 해석 시 필수)
- **VIX-proxy 치환**: 실 VIX/VXN 아닌 QQQ 20일 realized vol. spike-then-ease·term-structure 신호 손실.
- **표본 편향**: 2016~2026 = 닷컴(-49%)·2008(-55%) **없음**. TQQQ는 그런 장기 하락장에서 daily-rebalance decay로 -90%+ 가능. 이 구간은 *강세장 편향*이라 TQQQ 계열이 구조적으로 유리 → TQ-DH의 진짜 가치(긴 하락장 자본 보존)는 **검증 불가**.
- **Vault closed-loop 단순화**: Vault In은 A2 excess vs QQQ HWM·abs profit 게이트로 적립(spec §09 룰 엔진). Vaulted Profit 상한이 작아(Reload는 적립분의 25%씩) NAV로 TQQQ B&H를 못 이기게 설계됨(의도된 보수성).
- **Narrative/Credit 공백**: LLM narrative·HYG/IEF credit stress 미구현 → Type C 식별이 가격+200dma+leadership에만 의존.
- **체결 단순화**: reload 다음 종가 1회 체결 근사(슬리피지·부분체결·비용 미반영).
- PAPER only · NO LIVE · 자본권한 0 · TQQQ는 Core/알파가 아니라 Booster.
