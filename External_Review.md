# External Review — 외부 적대 검증 기록

> PRAMANA를 public으로 공개한 뒤 받은 외부 리뷰 중, **내부 적대검수(Codex)와 독립적으로 동일한 결론**에 도달한 평가를 기록한다. 검증 프레임의 robustness가 외부에서 교차 확인된 사례다. (리뷰어는 익명화 — 코드 비공개 상태에서 README만으로 평가.)

## 외부 리뷰 요지 (공개 포럼, 2026-06)

**강점 (인정):**
- 검증 하니스 — next-bar fill(signal t → fill t+1) · OOS + 최종 holdout · after-cost·turnover · 사전등록 kill · self-built survivorship-free S&P 500(실제 SPY corr **0.998**) — 가 대다수 retail 및 일부 published quant보다 엄격.
- 적대검수가 look-ahead 버그를 **2회 적발**했고, intraday ORB/VWAP/RVOL "alpha"가 누수 수정 즉시 사망한 것 = 하니스가 실제로 *문다*는 tell.
- TQQQ(raw-return foil) vs SPY/QQQ(risk-adjusted benchmark) 분리 = correct이며 드묾.

**약점 (지적 — 내부 Codex 채점과 일치):**
1. **"verifiable해지면 알파가 아니다(정보이론)" 슬로건 = as-stated 과장.** 본인 OOS에서 verifiable ≠ 공개적으로 arbitraged. 방어 가능한 건 좁은 버전("솔로가 free/cheap 데이터 + 표준 팩터·트렌드로 만든 신호는 이미 priced").
2. **"8세대 robust negative" = 상관된 한 regime**(2016–26 bull · 닷컴/2008 없음). scoped 강증거 / universal 약증거 → README headline이 footer(scope-conditional)보다 더 주장하는 내부 긴장.
3. **마켓타이밍 4전4패 = regime-conditional.** 저변동 grinding bull에서 방어 overlay는 구조상 lag. "후행신호 wall"은 부분적으로 regime 탓이다.
4. **8-K "bad-filing avoidance" survivor = 숫자 부재.** OOS effect size·t-stat·after-cost·turnover, 그리고 저품질/숏사이드 스크린(=베타) 변장 여부 미검증.

**리뷰어 결론:** "epistemics가 conclusions보다 낫다. validation OS·negative-results record로 credible. 'no easy solo alpha'는 scoped 버전을 벌었고 universal을 빌리고 있다."

## 우리 응답 (수용/반영)

| 지적 | 응답 |
|---|---|
| #1 슬로건 과장 | **수용.** 본문은 이미 scope-conditional로 교정(초록·결론·Evidence Ledger). headline은 TQQQ raw-return foil vs risk-adjusted alpha를 분리. |
| #2 한 regime | **수용.** 8세대는 scoped negative로 명시(보편 주장 아님). |
| #3 regime-conditional 타이밍 | **수용·한계로 기록.** "이 저변동 bull 샘플에서 *느린 일봉* 신호가 static 분산을 못 이김"으로 좁혀 읽어야 함. |
| #4 8-K 통계 부재 | **정확한 지적 — 제일 약한 주장.** 현재 정성·방향성 신호로만 라벨(OOS t-stat·after-cost·베타 변장 체크 미완). production 신호 아님으로 격하 유지. |

## 메타

외부 독립 리뷰어가 *코드 없이 README만으로* 내부 Codex 적대검수와 **동일한 강점·약점**을 짚었다는 사실 자체가, 본 검증 프레임이 reviewer-orthogonal하게 robust함을 시사한다. 점수가 아니라 이 교차확인이 본 프로젝트의 핵심 수확이다.
