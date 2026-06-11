# PRAMANA V5 — Problem Frame v0.1 (PROPOSED · 용하 승인 대기)

> **상태: 제안.** v4 Production(Core Beta 1.0x)이 3M서 SPY는 넘고 QQQ엔 짐 → 용하 directive("SPY·QQQ 둘 다 못 넘으면 v1→v4처럼 재정의")로 발동. Codex 회의 결과 + Claude 동의. **목표 변경이라 용하 승인 전 LOCK 아님.**
> 작성 2026-06-12 · 근거: docs/context/DECISION_LOG.md, Codex v5 council.

## 트리거 (측정 사실)
3개월: Core Beta 1.0x +10.9% > SPY +7.6%, **QQQ +14.3%엔 짐.** → "SPY·QQQ 둘 다 raw로 넘기" 미달.

## 정직한 진단 (왜 "QQQ raw 넘기"가 잘못된 목표인가 — Codex+Claude)
1. **50/50 Core가 QQQ raw 초과 = 수학적 기본 불가.** `0.5·SPY+0.5·QQQ`는 QQQ>SPY 구간서 항상 QQQ 아래. 3M 결과는 실패가 아니라 *정의상 예상값.*
2. **QQQ는 "쉬운 벤치"가 아니라 고농도 성장주 생존자 클러스터.** 10년 QQQ 18.97% vs S&P 14.15%·최근10년 중 7년 S&P 초과(Invesco). "QQQ raw 초과" = 시장초과가 아니라 *고농도 성장베타 초과* 요구.
3. **레버로 QQQ 넘기 = 알파 아니라 risk budget 재명명.** 더 큰 손실분포를 사는 것(SEC 레버ETF 경고). → 레버는 PRODUCTION_UNSAFE 기본·"합의된 레버 절대수익 book"으로만 별도 평가, QQQ-초과 알파라 부르지 않음.
4. **진짜 알파 위성 = 열되 base rate 처참.** SPIVA: active large-cap 79%가 당해 S&P 패배(장기 더↓)·Morningstar: active large-growth 20년 생존군 1%만 인덱스 초과·passive가 10년 연 2.2%p 앞섬. 솔로 systematic이 비용후 QQQ 지속초과한 공개·재현 사례 ≈ UNKNOWN.
5. **벤치마크가 목적함수를 훔친다.** "QQQ 이겨라" 순간 목적이 `max 초과수익 s.t. MDD≤X` → `tech-heavy 성장베타 chase`로 변질 = v1→v4 교정의 *역행.*

## 제안 v5 목적 = **QQQ-Participation Risk-Control Book**
- **SPY = floor 벤치:** raw return 초과 (1.0x Core가 이미 QQQ틸트로 달성).
- **QQQ = risk-control 벤치(raw 아님):** **80-100% upside capture + 더 낮은 MDD / 더 낮은 ulcer / 더 빠른 회복.** (= 규율 시스템이 raw QQQ 대비 *실제로* 줄 수 있는 효용. "QQQ만큼 먹되 덜 다치고 빨리 회복".)
- **제약:** A1 `MDD ≤ −35%`(현 기본) · next-bar · attribution · NO LIVE.
- **알파 위성:** RESEARCH_ONLY 계속 개방. production 승격 = core 대비 비용후 한계기여 + OOS + forward + attribution 통과 시만.
- **레버:** 별도 "합의 레버 절대수익 book"으로만, shock-stress 후. v5 알파라 부르지 않음.

## ★ 무한 재정의 루프 차단 기준 (Codex — 가장 중요)
- **3개월 raw로 목표 또 바꾸지 않는다.** 3M은 레짐 표본이지 목표-실패 판정 표본 아님. 목표 변경 트리거는 "raw QQQ 초과가 core-satellite lock과 충돌"이지 3M 패배가 아님.
- **STOP 기준:** 이 v5 정의로 **12개월 forward(또는 사전등록 OOS 블록)**에서 `SPY-floor 초과`와 `QQQ risk-control 지표(upside capture/MDD/회복)` 중 **하나도 못 맞추면 → 목표 또 바꾸지 말고 "쉬운 알파 없음, Core Beta만 production-safe" 수용.** 레버는 별도 book으로만.
- = "동기부여용 motion이 아니라 실제 수렴." 정직한 종착점을 미리 박음.

## 용하가 정할 것 (승인/조정)
1. 이 v5 reframe(QQQ raw 추격 버리고 risk-control 효용) 채택? — 아니면 "그래도 raw로 넘고 싶다"면 = 레버(리스크) 명시 수용한다는 뜻.
2. QQQ risk-control 지표 임계값(예: upside capture ≥85% & MDD ≤ QQQ의 0.8배) — 제안값, 조정 가능.
3. STOP 기준(12개월) 동의?

> **한 줄:** v5 = "QQQ를 raw로 이기려는 헛된 베타 추격"이 아니라 **"QQQ만큼 참여하되 덜 다치고 빨리 회복하는 규율 북" + 알파는 research에서 정직하게 계속 찾되, 12개월 못 넘으면 '쉬운 알파 없음'을 수용.** 가짜 승리도, 무한 루프도 거부.
