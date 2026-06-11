# DECISION_LOG — PRAMANA V4 (왜 이렇게 정했나 · append-only)
> 결정의 *이유 + 시점.* 무엇=LOCKS.md, 이유=여기. 신규 결정은 맨 위에 추가.

## 2026-06-12
- **V6 Diversified Aggressive 빌드 (용하 'v6 ㄱㄱ'·결정은 Codex 회의).** 동기: V5가 SPY/QQQ와 같이 낙폭(레버 증폭)·용하 "같이 안 맞기·현금으로 빼기(숏 아님)". 파훼법 회의 → managed-futures 분산이 답(DBMF 2022 +21.5%). Codex v6 스펙 council 확정: **vol_target·cap 1.5·DBMF 15%·추가 gate OFF**(v6A: 풀 +257%/−27%MDD/Sh0.99 > V5 +344%/−32%/0.95·고정레버 −39%MDD보다 나음; 6mo −6.3%p는 보험료지 결함 아님; DBMF 20%는 과함; gate=config-mining). **정직 트레이드오프: 낙폭↓·Sharpe↑ 대신 수익↓(+257 vs +344)·2023 bull 드래그 = "보험료"(Codex). alpha 아님·검증은 forward.** RESEARCH_ONLY. forward_runner_v6.py 가동(라이브 2026-06-11)·PRAMANA_V6_Problem_Frame_v0.1.md. caveat: DBMF 짧음(2019~·2008없음)·MF lost-decade(2011-20)·샘플의존. + Codex 전체검수 fix(판정표 라이브-only·no-ruin 제거·대시보드 프레이밍).
- **Production / Research 분리 확정 (LOCK SHEET v0.2).** 왜: v0.1이 Phase 1 실망 때문에 *연구 가능성까지* 닫음 = V1의 과폐기를 반대 방향으로 반복. → 자본권한 엄격 / 연구 개방. "쉬운 알파 없다"·"DL reject"를 LOCK에서 prior(높은 바)로 강등.
- **임시 A1 = ₩100M · 1~3년 · MDD −35%.** 왜: 임시값 없으면 모든 후속 선택(위성 채택·레버·승격)이 계속 흔들림.
- **Phase 1.5 risk-matched 측정.** 왜: Phase 1(equal-notional)이 위성 과소평가 의심 → 동일 vol·동일 −35%MDD로 *공정* 재검증 → +0.15%/yr 노이즈 확인 = false-negative 아님(공정히 봐도 안 보탬).
- **Codex 기억 = repo 컨텍스트 파일로 고정** (AGENTS.md + docs/context/*). 왜: Codex stateless → 대화 붙여넣기 비효율. AGENTS.md가 매번 강제 읽기.
- **LOCK SHEET v0.3 통합(정본).** 왜: v0.1/v0.2 거치며 쌓인 의견 전체 합침 — 신규: 6 판정라벨+capital/research veto 명시(F), V1 정밀교정(연구성공/포트실패), 공유기억 운영층(H). 과하게 닫힌 표현은 prior로 강등 유지. 포인터 전부 v0.3로.
- **v4 BUILD COMPLETE (autonomous·Codex 2회 REVISE 수용).** Production=Core Beta 1.0x(production_book.py): Codex가 "−35% MDD에 레버 맞추기=과거낙폭에 수익 끼워맞추는 backward knob=PRODUCTION_UNSAFE(forward 낙폭 더 클 수 있음·2008 미포함)" 지적→**레버를 격리 sleeve로 빼고 기본 1.0x**, overlay OFF(−0.14%=노이즈). Research thread1 mean-reversion=**REJECT**(net −4%·turnover 3660%·IC-IR 0.002·Core 한계기여 −0.027; 사전등록 4/5 kill·Codex가 kill 6개 추가 권고). forward reconcile 프레임(stooq 404→2nd피드 wiring TODO·0체크=UNKNOWN 정직). 공유기억 시스템 실작동 검증(Codex가 AGENTS.md+락시트 스스로 읽음). "마무리" 표현 교정(Codex): **"v4 build complete; alpha research open & capital-isolated"** — 알파 검증은 안 끝남, forward 운영상태 전환일뿐.
- **3개월 sim → v5 재정의 트리거.** Core Beta 1.0x 3M +10.9% > SPY +7.6%, but **QQQ +14.3%엔 짐**. 사용자 directive("SPY·QQQ 둘 다 못넘으면 v1→v4처럼 재정의")대로 → **v5 문제 재정의 Codex 회의 발사**(bk67xo7b5): QQQ까지 넘기가 솔로에 가능한가 / 목표 재정의 / 무한루프 회피. 정직: 베타북은 자기 벤치(QQQ)를 못 넘음=설계상 — 넘는 길은 레버(리스크) or 미발견 알파뿐. 가짜 승리 안 만듦.
- **v5 = Aggressive Leveraged Core Beta Book 확정(용하: 공격·리스크수용·유연 / Codex 3회 REVISE 수용 → SHIP-as-paper).** v0.1 risk-control 프레임 대신 용하가 raw 공격 선택=레버 수용 명시. aggressive_book.py(vol-target 28%·캡2.0x·DD ladder). in-sample 2016-26: +625%>QQQ +539%>SPY +301%·MDD −32%·Sharpe 0.95(≈QQQ). **Codex 최종평가: "이긴 게 아니라 benign 샘플서 QQQ보다 조금 더 잘 맞은 레버드 베타지 알파 아님(Sharpe≈QQQ)·forward −70%+ 가능(2008/dot-com 미포함)·vol-target은 no-ruin 아니라 손실속도 완화(gap 무력)." 라벨 RESEARCH_ONLY/PRODUCTION_UNSAFE·2.0x=paper max·live cap 1.25~1.5x(crash-pack 후)·cap은 crash-loss budget로 정함(CAGR 아님).** 빠졌던 forward 정량 판정표(상방참여/MDD/ulcer/회복/레버breach/체결오차/funding/reconciliation/missed-run·수익-only 합격금지) 박아서 SHIP-as-paper. behavior kill(12mo 전 목표변경·−30%서 override 금지). 왜: 용하 "이번엔 이겨보자"에 정직하게 — in-sample 승리는 레버지 엣지 아님, 진짜 승패는 다음 crash·12개월 규율.
- **v5 reframe 제안(Codex 회의 결과·Claude 동의) = PRAMANA_V5_Problem_Frame_v0.2.md(v0.1 대체).** Codex VERDICT: "SPY+QQQ raw 둘 다 넘기 = STOP"(50/50으론 수학적 불가·QQQ raw 추격=고농도 성장베타 chase=v1→v4 역행·SPIVA 79%/Morningstar 1%로 솔로가 QQQ 비용후 초과 base-rate≈UNKNOWN·레버=알파 아닌 risk budget 재명명). → **v5 = QQQ-Participation Risk-Control Book**: SPY raw 초과(floor) + QQQ엔 raw 아니라 80-100% upside capture·낮은 MDD/ulcer·빠른 회복. **무한루프 차단 STOP 기준: 12개월 forward(or OOS블록) 못 맞추면 목표 또 바꾸지 말고 "쉬운 알파 없음·Core Beta만 production-safe" 수용. 레버=별도 book만.** 왜: 벤치마크가 목적함수를 훔치는 것(QQQ 이겨라→성장베타chase) 차단 + 정직한 종착점 사전등록.
- **LOCK SHEET v0.4 (정본·v0.1~v0.3 대체).** 왜: GPT 추가 refine 5개 수용 — ① A1 단일 −35%가 결정을 끌고 가는 위험 → 3 시나리오(−20/−35/−50) 병기 ② Production을 **"Core Beta Forward Book"**으로 정직 명명(Core>SPY=QQQ 틸트=레짐이지 알파 아님, 자기기만 방지·C6) ③ Research 1순위 = mean-reversion(trend가 알파 아니면 반대 성격을 봐야·quality는 식어서 2순위) ④ forward reconciliation(stooq 상시 sanity + Sharadar 윈도우 주기 대조) ⑤ 연구 active(1개)/passive data collection(병렬) 분리. v0.1~v0.3 git rm.

## 2026-06-11
- **명명 V2→V4.** 왜: 내부 v1/v2/v3와 혼동 방지.
- **core-satellite 피벗.** 왜: 멀티시점서 풀북이 SPY를 위험조정으로 못 이김 → SPY와 싸우지 말고 *깔고 얹기.*
- **NO ML/TSFM as alpha (off-path 보조만).** 왜: DR-4 + bake-off(ridge/GBM이 선형 합성 못 넘음) + GKX(ML OOS R² 0.4%·마이크로캡·비용전) + 자유도/비정상성/SNR 논리. *영구금지 아니라* research 허용·고바·저우선.
- **레퍼 = 부품창고 (전략 통째 베끼기 금지) · Parker = 평균회귀로 교정.** 왜: 풀파워 회의(Codex+Claude×3) — Frankenstein 순환논법·생존편향·trend decay. 레퍼는 *리스크 구조*는 지지하나 *알파*는 검증 못 함.
- **리스크엔진 판정 언어 세분화 + capital/research veto 분리.** 왜: V1 이진 폐기가 너무 경직(좋은 후보까지 죽임).

## 이전 (v1~v3 요약)
데이터·검증·리스크 파이프 구축 = 자산(PIT cap-weight corr 0.998). 단순팩터 6 family 전멸 = 정직한 negative. Codex 리뷰 = REVISE("인-샘플 베타 타이밍을 분산북으로 포장"·same-close 누수→next-bar 수정). → core-satellite(V4)로 전환.
