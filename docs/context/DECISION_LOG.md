# DECISION_LOG — PRAMANA V4 (왜 이렇게 정했나 · append-only)
> 결정의 *이유 + 시점.* 무엇=LOCKS.md, 이유=여기. 신규 결정은 맨 위에 추가.

## 2026-06-12
- **Production / Research 분리 확정 (LOCK SHEET v0.2).** 왜: v0.1이 Phase 1 실망 때문에 *연구 가능성까지* 닫음 = V1의 과폐기를 반대 방향으로 반복. → 자본권한 엄격 / 연구 개방. "쉬운 알파 없다"·"DL reject"를 LOCK에서 prior(높은 바)로 강등.
- **임시 A1 = ₩100M · 1~3년 · MDD −35%.** 왜: 임시값 없으면 모든 후속 선택(위성 채택·레버·승격)이 계속 흔들림.
- **Phase 1.5 risk-matched 측정.** 왜: Phase 1(equal-notional)이 위성 과소평가 의심 → 동일 vol·동일 −35%MDD로 *공정* 재검증 → +0.15%/yr 노이즈 확인 = false-negative 아님(공정히 봐도 안 보탬).
- **Codex 기억 = repo 컨텍스트 파일로 고정** (AGENTS.md + docs/context/*). 왜: Codex stateless → 대화 붙여넣기 비효율. AGENTS.md가 매번 강제 읽기.
- **LOCK SHEET v0.3 통합(정본).** 왜: v0.1/v0.2 거치며 쌓인 의견 전체 합침 — 신규: 6 판정라벨+capital/research veto 명시(F), V1 정밀교정(연구성공/포트실패), 공유기억 운영층(H). 과하게 닫힌 표현은 prior로 강등 유지. 포인터 전부 v0.3로.
- **LOCK SHEET v0.4 (정본·v0.1~v0.3 대체).** 왜: GPT 추가 refine 5개 수용 — ① A1 단일 −35%가 결정을 끌고 가는 위험 → 3 시나리오(−20/−35/−50) 병기 ② Production을 **"Core Beta Forward Book"**으로 정직 명명(Core>SPY=QQQ 틸트=레짐이지 알파 아님, 자기기만 방지·C6) ③ Research 1순위 = mean-reversion(trend가 알파 아니면 반대 성격을 봐야·quality는 식어서 2순위) ④ forward reconciliation(stooq 상시 sanity + Sharadar 윈도우 주기 대조) ⑤ 연구 active(1개)/passive data collection(병렬) 분리. v0.1~v0.3 git rm.

## 2026-06-11
- **명명 V2→V4.** 왜: 내부 v1/v2/v3와 혼동 방지.
- **core-satellite 피벗.** 왜: 멀티시점서 풀북이 SPY를 위험조정으로 못 이김 → SPY와 싸우지 말고 *깔고 얹기.*
- **NO ML/TSFM as alpha (off-path 보조만).** 왜: DR-4 + bake-off(ridge/GBM이 선형 합성 못 넘음) + GKX(ML OOS R² 0.4%·마이크로캡·비용전) + 자유도/비정상성/SNR 논리. *영구금지 아니라* research 허용·고바·저우선.
- **레퍼 = 부품창고 (전략 통째 베끼기 금지) · Parker = 평균회귀로 교정.** 왜: 풀파워 회의(Codex+Claude×3) — Frankenstein 순환논법·생존편향·trend decay. 레퍼는 *리스크 구조*는 지지하나 *알파*는 검증 못 함.
- **리스크엔진 판정 언어 세분화 + capital/research veto 분리.** 왜: V1 이진 폐기가 너무 경직(좋은 후보까지 죽임).

## 이전 (v1~v3 요약)
데이터·검증·리스크 파이프 구축 = 자산(PIT cap-weight corr 0.998). 단순팩터 6 family 전멸 = 정직한 negative. Codex 리뷰 = REVISE("인-샘플 베타 타이밍을 분산북으로 포장"·same-close 누수→next-bar 수정). → core-satellite(V4)로 전환.
