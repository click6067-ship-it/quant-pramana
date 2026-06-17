# A2 TQ-DH (TQQQ Dip Harvester) — Weekly/Backtest Review
> 생성 2026-06-14 · backtest 2016-01~2026-06 · PAPER only · 자본권한 0 · **검증된 알파 아님**.
> spec: `pramana_a2_delta_patch_pack/03_TQ_DH_TQQQ_DIP_HARVESTER.md` (+05 §5 reload rules)

## 0. 사전등록 (Pre-registered) 성공·실패 조건 — 결과 보기 전에 박음
**성공조건 (spec §8) — A2 *with* TQ-DH가 A2 *without* TQ-DH 대비:**
1. final NAV ≥ (같거나 높음)
2. MDD 더 낮음(덜 깊음)
3. 회복기간 더 짧음
4. Vaulted Profit > 0

→ TQQQ buy-and-hold보다 최종 NAV가 *낮아도 괜찮다* (대신 MDD·Vaulted Profit에서 보상).

**실패조건 (spec §9) — 하나라도 해당 시:**
- TQ-DH가 TQQQ drawdown DCA보다 final NAV·MDD **둘 다** 열위
- Reload가 대부분 Type C(구조붕괴)에서 발생
- Hard Vault를 써야만 성과가 남 (설계상 Hard Vault 재투입 금지 → 구조적으로 불가)
- Reload 후 손실 반복 / A2가 QQQ 대비 언더퍼폼을 크게 확대

## 1. 방법론·치환 (정직 라벨)
- **VIX/VXN proxy**: 캐시에 VIX/VXN 없음 → **QQQ 20일 realized volatility(연율화)**로 치환. 라벨 = `GREEN/YELLOW/RED-proxy` (calm<20%·elevated<35%·이상 RED). 진짜 VIX term-structure·skew 아님.
- **Leadership**: sp500 패널의 대형주 10종(NVDA·MSFT·AAPL·AMZN·GOOGL·META·AVGO·TSLA·AMD·NFLX) vs 50일선 비율 (실데이터).
- **Narrative/Earnings/Credit**: LLM·HYG/IEF 미구현 → `narrative_state = N/A-proxy` (정직 공백).
- **NO LOOK-AHEAD**: close_t로 분류한 dip은 close_{t+1}부터만 reload 체결·수익 계산. 회복확인(10일고점·follow-through)도 과거 데이터만.
- **Reload Vault**: 자본의 10%를 reserve로 분리, 1 reload = Reload Vault의 25%, 최소 간격 3거래일, Type C=reload 금지, **Hard Vault는 절대 사용 안 함**.

## 2. 백테스트 비교 (₩1억 기준·log 차트 = `outputs/a2_live/tq_dh_backtest.png`)

| 전략 | 최종 NAV(배) | 최종 평가액 | MDD | 회복(거래일) |
|---|---:|---:|---:|---:|
| TQQQ_BH | 32.552 | ₩32.552억 | -81.7% | 486 |
| TQQQ_DCA_monthly | 8.947 | ₩8.947억 | -75.7% | 380 |
| TQQQ_DCA_drawdown | 6.765 | ₩6.765억 | -65.4% | 268 |
| QQQ_BH | 6.830 | ₩6.830억 | -35.1% | 278 |
| A2_base | 9.821 | ₩9.821억 | -48.4% | 278 |
| A2_with_TQ-DH | 12.264 | ₩12.264억 | -53.6% | 293 |

## 3. TQ-DH 동작 통계
- 총 reload 횟수: **41** · Type C에서 발생: **0** (0% — 설계상 0이어야 함)
- reload 자산 분포: {'TQQQ': 21, 'QQQ': 20}
- **Vaulted Profit** (reload 자산의 체결→최종 누적 이득): **₩1.551억** (+155.09% of 자본)
- dip type 분류 일수: {'NONE': 1687, 'D': 360, 'B': 320, 'A': 137, 'C': 120}
- reload 후 평균 수익: 5일 +2.23% (n=41) · 20일 +6.75% (n=41)
- 결정 로그: `outputs/a2_live/tq_dh_decisions.csv` (date·qqq_drawdown·vix_vxn_state·leadership_state·narrative_state·dip_type·action·reload_amount·asset_used·post_reload_return_5d/20d)

## 4. 판정 (Verdict) — 사전등록 조건 대조
**성공조건 (vs A2 without TQ-DH):**

| 조건 | A2 base | A2 with TQ-DH | 통과 |
|---|---:|---:|:--:|
| 최종 NAV(배) | 9.821 | 12.264 | ✅ |
| MDD | -48.4% | -53.6% | ❌ |
| 회복기간(거래일) | 278 | 293 | ❌ |
| Vaulted Profit > 0 | — | ₩1.551억 | ✅ |

**성공조건 종합: ❌ NOT MET (일부 미충족)**

**실패조건:**
- vs drawdown-DCA NAV·MDD 둘 다 열위: 아니오
- reload 대부분 Type C: 아니오
- Hard Vault 의존: 아니오 (설계상 Hard Vault 재투입 코드상 불가)

**실패조건 종합: ✅ 실패조건 없음**

## 5. 정직한 결론 (Honest Verdict)
**NOT MET (성공조건 일부 미충족, 그러나 명시적 FAIL 트리거는 없음).** A2 with TQ-DH NAV=12.26배 vs A2 base 9.82배. spec이 예고했듯 최종 NAV에서 TQQQ buy-and-hold(32.6배)를 못 이기는 것은 정상 — 평가는 MDD/회복/Vaulted Profit으로 한다.

핵심 정직 메모: (a) Reload Vault(자본 10%)만 쓰므로 TQ-DH의 NAV 기여 *상한*이 작다 — 구조적으로 TQQQ buy-and-hold를 NAV로 이길 수 없게 설계됨(의도된 보수성). (b) 강세장 편향 표본에서는 'dip을 가려 사는' 절제가 '아무 dip이나 사는' 단순 DCA보다 NAV를 깎을 수 있다(상승장에선 더 많이 살수록 유리). TQ-DH의 진짜 효용은 *긴 하락장 자본 보존*인데 이 표본엔 그런 구간이 없어 측정 불가. (c) 따라서 이 결과는 '기계가 약속대로 작동하고 look-ahead 없이 dip을 분류·절제한다'는 **machinery 검증**이지, '수익 알파 입증'이 아니다.

## 6. Caveats (한계 — 결과 해석 시 필수)
- **VIX-proxy 치환**: 실 VIX/VXN 아닌 QQQ 20일 realized vol. spike-then-ease·term-structure 신호 손실.
- **표본 편향**: 2016~2026 = 닷컴(-49%)·2008(-55%) **없음**. TQQQ는 그런 장기 하락장에서 daily-rebalance decay로 -90%+ 가능. 이 백테스트는 *강세장 편향* 구간이라 TQQQ 계열이 구조적으로 유리 → TQ-DH의 진짜 가치(긴 하락장 자본 보존)는 **검증 불가**.
- **Narrative/Credit 공백**: LLM narrative·HYG/IEF credit stress 미구현 → Type C 식별이 가격+200일선+leadership에만 의존(과소·과대 가능).
- **체결 단순화**: reload를 다음 종가 1회 체결로 근사(슬리피지·부분체결 무시). 비용(수수료/스프레드) 미반영.
- PAPER only · NO LIVE · 자본권한 0 · TQQQ는 Core/알파가 아니라 Booster.
