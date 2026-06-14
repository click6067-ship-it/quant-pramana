# PRAMANA AX-0 — Pre-Registration Protocol (kill/gate를 결과 *前* 잠금)

> 정본 = `~/main/council/2026-06-14_aggressive-pivot/plan.md`(Codex 3R → APPROVED). 이 문서 = 결과 보기 *전* 박는 사전등록.
> **판정 라벨: RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 자본권한 0 · 검증된 알파 아님.**
> 작성 2026-06-14. **이 파일은 첫 trade 전 동결.** 결과 보고 임계값·정의·attribution 식 바꾸면 = config-mining = 무효.

## 0. 한 줄
공격적 전환의 첫 sleeve = **AX-0 = S1 Long-Convex Catalyst (옵션 long·defined-risk·forward-paper)**. 알파 발견이 아니라 **catalyst 둘레의 비대칭 payoff를 *산다*** (convexity 구매·검증불가 인정). 가상 ₩1억 PAPER·매수권 0·사람 게이트.

## 1. 왜 (8세대 + kickoff 결론)
- 8세대 = 솔로·공개데이터 robust alpha 미발견·"검증된 순간 베타". A2 Attack(spot daily-proxy) DEAD·Moonshot 표본 edge 없음·AlphaLab v1 DEAD.
- 용하 지시 = "안전·검증 바이어스 버리고 공격적·유연." 단 PAPER·no-ruin(완화)·사람게이트 레일 유지.
- Codex 3R 핵심: **PAPER는 자본 피해만 제거·*인식론적 피해(운→엣지 착각)*는 안 제거** → 전략은 공격적, **게이트는 더 단단히**.

## 2. AX-0 정의 (1 sleeve만·단계적 롤아웃 1단계)
- **수단:** long premium·debit call/put spread만. **금지(AX-0): naked write·margin·숏·LETF·short-vol("VRP")·재량 size-up·옵션 백테스트 claim.** (다음 단계 sleeve에서 게이트 통과 후.)
- **소스:** Feeder A 후보(catalyst = 8-K item 2.02 실적/1.01 중요계약 + 추정치 리비전 + gap/momentum). 후보 ≠ 매수 — defined-risk 옵션으로만 표현.
- **데이터:** 옵션 = yfinance 체인(forward·현재 스냅샷만·이력 없음) = **FORWARD_PAPER_ONLY_UNVERIFIED**. 주식/이벤트 = Sharadar 캐시 + EDGAR.

## 3. 사전등록 graduation gate (S2/S3 열기 *전* AX-0이 통과해야·net>0만으론 절대 통과 X)
전부 AND:
1. **독립 trade N ≥ 30** — 독립 = (event·underlying·date·expiry-cluster) 고유. row-count 아님(같은 catalyst 다리는 1개).
2. **median trade P&L > 0** (after 보수 fill+cost) — fat-tail 1방 대박 금지.
3. **잔차 하한 CI > 0** — §4 attribution 차감 후 residual의 bootstrap 하한 신뢰구간 > 0 (PSR/DSR류·다중검정 보정 정신).
4. **process compliance = 100%** (사전등록 위반·thesis hash 변경·cherry-pick 0).
**하나라도 깨짐 → AX-0 sleeve DEAD → graveyard 기록 → trial registry 다음 칸**(또는 "쉬운 공격 엣지도 없음" 수용·무한루프 차단).

## 4. Attribution-kill (사전등록 *방정식*·factor·임계 동결)
- **P&L = Σ(Δ·ΔS) + vega·ΔIV + theta·dt + carry + cost + residual.**
- factor = SPY/QQQ/IWM beta + LETF leverage proxy + vol-regime(VIXY/20d realized).
- 데이터 소스·계산식 = 첫 trade 전 동결.
- **kill:** cost·Greeks·beta·short-vol 차감 후 **residual 하한 CI ≤ 0** → "beta/vol lottery" 라벨 → sleeve 폐기. ("mostly" 같은 사후 이동 금지.)

## 5. Heat rails (hard veto·PAPER·−70%와 독립·−70%는 sandbox 외벽이지 sizing input 아님)
- max premium-at-risk / trade = NAV의 1.0%
- max open premium(전체 동시) = NAV의 8%
- max same-expiry 노출 = NAV의 3%
- max 상관 catalyst 동시 = 동일 sector/theme 3건
- max monthly theta burn = NAV의 2%/월
- daily process stop: 하루 −1% → 당일 신규 금지 / 위반 발생 시 강제 cool-down 5거래일
- (위반은 경고 아니라 **진입 거부**.)

## 6. Master trial registry (family-wise·R2#4)
- sleeve 고정 순서: **S1(AX-0) → S2 Conviction-calibration → S3 Directional(broker-valid) → S4 Short-Vol.**
- 최대 시도 수 = 4 sleeve(각 1회)·global error budget. "S1 죽으면 S2" = family search → 나중 sleeve 성공은 **global hurdle 통과 전엔 family-adjusted exploratory로만 보고.**
- registry append-only(폐기 variant 포함). sleeve 내 no-replacement.

## 7. Graveyard 상속 (R2#5)
모든 Feeder 후보에 `graveyard_overlap` 필드 필수(candidate 생성 시점·사후 아님). A2 Attack/Moonshot·AlphaLab v1/v2·LETF trend과 겹치면 `revival` 태그 + **새 메커니즘/데이터 증거 전엔 거래 금지.**
- AX-0의 catalyst-momentum 표면은 A2 Attack(spot daily-proxy DEAD)과 겹침 → revival. **새 메커니즘 = spot 추격이 아니라 defined-risk *옵션 convexity*(다른 payoff/risk)** = 거래 허용 근거(단 forward-paper·UNVERIFIED).

## 8. 측정/산출
- `outputs/ax0/candidates.csv`(feeder 전수·append-only) · `option_ledger.csv`(signal_quality + tradable_pnl 분리) · `trial_registry.json` · `attribution.csv` · `health.json`.
- 리포트 `reports/AX0_status.md`(N·median·residual CI·compliance·gate 상태 — N<30이면 INSUFFICIENT).

## 9. 금지 (LOCK)
실자본 · naked/숏/margin/LETF/short-vol을 AX-0에 · 옵션 midpoint mark · 결과 보고 catalyst/임계 튜닝 · stress-only를 book NAV 합산 · attribution/다중검정 보정 없이 paper net을 "edge"로 · feeder standalone 알파 주장. PAPER·자본권한 0·사람=자본 게이트.
