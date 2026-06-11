# PRAMANA V6 — 설계도 (외부 검수용 · 레이어별 핵심)

> **용도: GPT/외부 리뷰어가 개선점을 찾도록 만든 단일 설계 문서.** 코드 전체가 아니라 *레이어별로 뭘 썼나 + 정확한 파라미터 + 근거 + 실증 결과 + 미해결*. 끝의 **§9 검수 요청**을 우선 봐달라.
> 상태: **PAPER only / NO LIVE · RESEARCH_ONLY / PRODUCTION_UNSAFE.** 솔로 + AI · US 주식/ETF · 가상자본 ₩100M. 2026-06-12.

---

## 1. 정체 (한 문단)
PRAMANA는 "종목 찍는 AI"가 **아니다.** 데이터·비용 정직성으로 **솔로에게 쉬운 알파가 없음을 실증한 뒤**, **레버드 분산 베타**(SPY/QQQ + managed-futures)를 **변동성-반응 리스크 통제**로 굴리는 페이퍼 *검증* 시스템이다. **예측·종목선택·익절 로직이 없다.** 학습된 ML 모델 0개 — 전부 규칙·산술.

## 2. 계보 (왜 여기까지 왔나 = 무엇이 죽었나)
- **v1~v3:** 단순/선형 횡단면 팩터(value·momentum·quality·lowvol·event)·결합·ridge/GBM → **전부 비용후 SPY/QQQ 못 이김**(IC≈0·decay). 정직한 negative(가짜알파 안 만든 게 자산). Codex 리뷰=REVISE("인-샘플 베타타이밍 포장").
- **v4:** Core Beta Forward Book(SPY/QQQ 1.0x) — 정직한 베타북, 알파 아님.
- **v5:** Aggressive Leveraged Core Beta(vol-target·캡2.0x) — in-sample QQQ raw 넘김(+625% vs +539%) **but 레버지 알파 아님(Sharpe≈QQQ)·SPY/QQQ와 *같이* 낙폭(6mo −20%)**.
- **v6(현재):** v5 + **managed-futures(DBMF) 분산 + 낮은 레버(1.5x)** = "같이 안 맞기"를 구조적으로 완화.

## 3. 목적함수 · 제약 · 잠금 원칙
- **목적:** max 초과수익 over benchmark, **s.t. MDD ≤ X**(공격적 수익극대화 + 리스크 수용, 단 파산 회피). A1 임시: 가상 ₩100M·1~3년·MDD 시나리오 −20/−35/−50%.
- **잠금(불변):** PAPER/NO LIVE · US only · **next-bar 실행**(look-ahead 차단) · **attribution 필수** · **결정적 risk engine veto** · **LLM/TSFM 직접 트레이딩 금지**(off-path 보조만) · **단순 baseline 우선**(복잡 모델은 1/N·고정비중 OOS 비용후 이겨야) · 사람 자본 게이트 · 사전등록 kill.
- **operating prior(락 아님):** 쉬운 알파 없음(높은 바) · 추세=리스크 도구지 엔진 아님 · 레퍼=부품창고.

## 4. 레이어별 설계 (핵심)

| 레이어 | 무엇을 썼나 | 모델/규칙 | 정확한 파라미터 | 근거 |
|---|---|---|---|---|
| **L1 데이터** | Sharadar(유료·backtest)·yfinance(무료·forward) | — | PIT·survivorship-safe·가격만(V6는 펀더멘털 미사용) | 미래누수 차단; cap-weight PIT가 실제 SPY와 corr 0.998 검증 |
| **L2 신호/레짐** | 20일 실현변동성 + 현재 낙폭 | **모델 없음 = 공식** | realized vol = 20d rolling std × √252 | *예측 아님*, 후행 지표; ML은 알파無라 제외 |
| **L3 북(sleeve)** | 85% 레버드 Core(SPY/QQQ 50/50) + 15% managed-futures(DBMF) | vol-target 공식 + DD-ladder 테이블 + 고정 85/15 | (§5) | DBMF=주식 추세하락때 상승(2022 +21.5%)→분산 |
| **L4 배분(allocator)** | 고정 85/15 | **고정비중**(적응형 X) | core 85% / DBMF 15% | DeMiguel 2009: 적응형이 고정비중 OOS 못 이김 |
| **L5 리스크엔진** | vol-target + DD-ladder + 레버캡 | 결정적 규칙 | target_vol=28%·cap=1.5x·DD ladder(아래) | 변동성↑→노출↓·낙폭↑→디레버·캡으로 ruin 둔화 |
| **L6 실행** | next-bar | 비용 모델 | 진입 t+1·financing=5%/yr on (L−1)·ETF 스프레드 | same-close 누수 차단(v3서 발견·수정) |
| **L7 귀속/모니터** | core vs DBMF 기여·forward 판정표 | — | 판정표 LIVE-only·미구현=UNKNOWN=불합격 | 자기기만 방지·수익-only 합격 금지 |
| **L8 거버넌스** | paper·사람 자본게이트·LLM off-path·12mo STOP | — | crash-pack+12mo forward 전 자본 금지 | 무한 재정의 루프 차단 |

## 5. V6 북 정확한 메커니즘 (매일·결정적)
```
매일(장마감 후 1회):
1. SPY·QQQ·DBMF 종가 수신(append-only 캐시)
2. core_ret_t = 0.5·SPY_ret + 0.5·QQQ_ret
3. realized_vol = std(core_ret, 20d) × √252
4. L_vt = min(1.5, 0.28 / realized_vol)          # vol-target, 캡 1.5x
5. L = L_vt × DD_ladder(current_drawdown)         # 낙폭 깊을수록 디레버
      DD_ladder:  dd≤−40% →0.2 · ≤−30% →0.4 · ≤−20% →0.7 · else 1.0
6. book_ret_t+1 = 0.85·(L·core_ret − (L−1)·5%/252) + 0.15·DBMF_ret   # next-bar·financing
7. NAV 갱신 → 판정표 채점 → 대시보드
```
- 리밸런스 = 매일(레버는 vol-target으로 일별 변동). DBMF 비중 고정 15%.
- **숏·헷지·익절·종목선택·예측 없음.** "변동성 따라 레버 조절한 분산 베타"가 전부.

## 6. 실증 결과 (paper·비용후)
**풀사이클 (2019-06~2026·DBMF 제약):**
| 북 | 누적 | MDD | Sharpe |
|---|---|---|---|
| **V6 (85%lev·15%DBMF·cap1.5)** | **+257%** | **−27%** | **0.99** |
| V5 (cap2.0·DBMF無) | +344% | −32% | 0.95 |
| v6C (고정1.5·DBMF無) | +380% | −44% | 0.85 |
| QQQ | +316% | −35% | ~0.96 |
| SPY | +성장기준 낮음 | −34% | 0.89 |

**멀티시점 진입 (vs QQQ):** 3개월 V6 +17.6%/−9%MDD (QQQ +19.8%) · 6개월 +12.2%/−13% (QQQ +13.5%·**V5는 +7.5%/−20%였음→개선**) · 12개월 +37.5%/−13% (**QQQ +34.1% 넘김**).
**2022 동반하락:** V6 −26%/−27%MDD vs V5 −31%/−32% vs QQQ −33%/−35% (DBMF가 올라 방어).
**DBMF 15% 기여(고정1.5 기준):** Sharpe 0.85→0.89·MDD −44→−39%·수익 +380→+336%.
**Research(유료 Sharadar):** mean-reversion thread1=**REJECT**(turnover 3660%)·quality 레짐 retest=**not-candidate**(Core 대비 한계기여 +0.03%p«50bp).

## 7. 정직한 평가 / 한계
- **Sharpe ≈ QQQ** → 위험조정 우위 0 = **알파 아님.** 수익=레버(리스크)·낙폭통제=분산(보험료).
- **레버 꼬리위험:** 2.0x/1.5x 레버 + 2016-26/2019-26 benign 샘플(2008·닷컴 없음) → **forward MDD −70%+ 가능.** vol-target은 손실속도 완화지 no-ruin 아님(gap 무력).
- **DBMF 짧은 역사**(2019~)·managed futures 2011-20 'lost decade'·+0.05~0.14 Sharpe 개선 **샘플 의존.**
- **forward 검증 0개월** — in-sample/backtest일 뿐. 판정표(ulcer/회복/체결/funding) 다수 NOT_IMPLEMENTED.

## 8. 미해결 / 개선 후보 (용하 지적 + 알려진 TODO)
1. **[큰 낙폭 상관]** V6도 큰 크래시서 SPY/QQQ와 *같이* 떨어짐(85% 주식 베타 지배·DBMF 15%뿐). → 더 강한 decorrelation 필요?
2. **[85/15 vs 4-sleeve]** Codex 판정: **85/15는 너무 equity-dominant라 큰 크래시 decorrelation엔 부족 → 별도 mandate인 4-sleeve가 답.** 추천(research-only): **Equity 50%(SPY/QQQ) + Managed Futures 25%(DBMF/KMLM) + Gold 15%(GLDM/IAU) + Bonds 10%(IEF/SGOV)**, 레버 0x~총 1.25x cap(그 이상이면 "덜 같이 맞기" 목적 훼손). 채권보다 managed futures가 핵심 hedge(2022 채권 깨짐·DBMF +21.5%). 비용: QQQ bull엔 거의 확실히 짐(decorrelation↑=QQQ capture↓·"다른 고통 선택"이지 알파 아님).
3. **[일봉 vs 분봉]** Codex 판정: **거의 무관(직교).** "큰 낙폭서 같이 맞기"는 *자산 노출* 문제지 *타이밍 빈도* 문제 아님 — equity beta 70~85%면 분봉 붙여도 crash correlation 안 사라짐. 분봉=운영 품질 과제지 핵심 결함 해결책 아님.
4. **[왜 QQQ 대신 V6?]** Codex 판정: **기본값 = '그냥 QQQ' 수용.** V6는 QQQ 이긴 상품 아니라 *QQQ 수익 일부 팔아 −8%p MDD 산 보험북*(Sharpe≈QQQ). **목적함수 문제:** raw wealth → QQQ / crash-survival(계좌+멘탈 같이 안 부서지기) → QQQ 단독 금지·4-sleeve. → **용하가 정할 것: 최대 복리(QQQ) vs 크래시 생존(4-sleeve).**
5. **[vol-target procyclical]** 6mo chop서 고정레버 대비 −6.3%p 손해(저점 디레버·반등 놓침). 풀사이클은 도움. 유지/제거?
6. **[레버캡/target-vol]** cap 1.5x·target-vol 28% — 적정? crash-loss budget로 재산정 필요(현재 미실시).
7. **[forward 판정표 미완]** ulcer/회복일수/체결오차/funding 자동채점 NOT_IMPLEMENTED.
8. **[reconciliation]** 무료 독립 2nd 피드 막힘(stooq) → 실자본 전 유료 필요.
9. **[crash-pack 미실시]** 1987갭·2000-02·2008·2020·2022 사전등록 스트레스로 cap 결정해야(미완).

## 9. 검수 요청 (리뷰어에게)
다음을 *우선* 공격해 달라:
- **A. 존재 이유:** 무알파 조건서 V6가 QQQ를 들 가치가 있나, 아니면 '그냥 QQQ/SPY'가 정직한 답인가? (가장 중요)
- **B. 큰 낙폭 decorrelation:** 4-sleeve/risk-parity가 큰 크래시 상관을 *진짜* 줄이나, 2022처럼 또 깨지나? 비-알파로 가능한 최선은?
- **C. 레버 정책:** vol-target 유지 vs 고정레버? cap 1.5x 적정? forward −70%+ 꼬리를 어떻게 정직 처리?
- **D. 자기기만 잔존:** in-sample/benign-sample/DBMF-짧은역사 위에 세운 결론에 남은 과신은? look-ahead/overfit?
- **E. 파라미터 과적합:** target-vol 28%·DD-ladder 임계·85/15·15% DBMF — config-mining 표면인가? 단순화할 곳은?
- **F. 분봉:** 낙폭 상관 문제에 무관한가, 아니면 의미 있나?

> 리뷰 원칙: 칭찬 금지·문제만·`[발견]/왜/수정`. 새 반박은 새 데이터/논리로. 정직성 > 정중함.
