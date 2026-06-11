# Broad-Universe Cost-Aware Factor Retest — Protocol v0.1 (PRE-REGISTERED)
**Date:** 2026-06-11 · **Status:** pre-registered BEFORE results (overfit 방지) · **구독 29일 윈도우 내 실행**
**목적:** S&P500 대형주에서 죽은 단순팩터(B2~B5)가 **broad universe에서 *비용 후*에도 살아나는지** 확인.
**이건 알파 사냥 아님 — 단순팩터를 *종료시키기 위한* 확정 검증.** kill 조건을 먼저 박는다.

## 1. Universe (PIT, survivorship-aware)
- 모집단: US **Domestic Common Stock** (TICKERS category), ~13,488 ever (active 3,239 + delisted 10,249).
- 각 월말(실제 거래일): **marketcap 상위 N** 선택. **N = 1500** (1차; 견고성용으로 1000·3000도 부차 확인).
- 유동성 필터(사전): price ≥ $5, 그리고 ADV(거래대금) 하위 제외(예: dollar-volume 하위 20% 컷) — 소형·저유동성 집중 방지.
- 상장폐지 종목: 폐지 전까지 포함(survivorship). firstpricedate 이전 편입 금지(no-future).
- **현재 리스트 소급 금지** — marketcap은 그 시점 DAILY 값으로 PIT 랭킹.

## 2. Factors — **S&P500 run과 *완전히 동일* (튜닝·신규팩터 금지)**
| Sleeve | 정의(고정) |
|---|---|
| B2 value | 1/pb (DAILY pb) |
| B3 quality | gp/assets (SF1 ARQ, datekey PIT) |
| B4 momentum | 12-1 (t-12→t-1 monthly return) |
| B5 low-vol | −trailing 126d daily-return vol |
- value 계산식·momentum window·quality 정의 **변경 금지**. broad는 *유니버스만* 바꾸는 통제 실험.

## 3. Cost model (provisional house, 사전고정)
- one-way cost = half-spread proxy + turnover penalty. 1차값(provisional): **대형주 5bp / 중소형 15bp** one-way(시총분위로 차등), + 시장충격 근사(participation 기반).
- net return = gross − Σ(|Δweight| × one-way cost). turnover 보고 필수.
- base / 2x cost 스트레스.

## 4. Metrics
gross & **net** Q5-Q1 spread(연), Rank IC mean·IC-IR·IC>0%, turnover(연), 시총분위별 기여(소형주 집중 점검), 하위기간(연도별) 부호 일관성.

## 5. ★ PRE-REGISTERED KILL CONDITIONS (결과 보기 전 확정)
한 sleeve는 아래 중 **하나라도** 해당하면 **DEAD(채택불가)**:
1. **net Q5-Q1 spread ≤ 0** (비용 후 프리미엄 소멸)
2. **IC-IR < 0.20** (provisional; 노이즈 수준)
3. **turnover 과도** → net이 gross의 절반 미만으로 깎임
4. **신호가 소형·저유동성/특정 시총분위에 집중** (대형주선 0인데 소형주만 → 비용·capacity로 실현불가 의심)
5. **기간 의존**: 절반 이상 연도에서 부호 뒤집힘

**종합 판정:**
- 모든 sleeve DEAD → **단순팩터 경로 종료** → Phase 1B(저-DoF challenger: penalized regression·constrained linear ranker·simple blend). *XGBoost/LLM/TSFM 여전히 금지.*
- 1개 이상 survive → 그 sleeve만 Phase 1B에서 challenger 비교 대상으로(여전히 채택 아님, DSR/PBO 게이트 후).

## 6. 정직한 사전확률
대형주에서 IC≈0이었고, 소형주는 IC가 높아도 **비용이 프리미엄을 잡아먹음**(Novy-Marx–Velikov). → **비용 후 robust 엣지 없을 가능성 높음.** 이 검증의 가치 = "안 살아나면 단순팩터를 *깨끗이 닫는다*". 살아나길 바라는 게 아니라 *닫기 위한* 테스트.

## 7. 실행 순서 (29일 윈도우)
1. 전체 Domestic Common Stock **DAILY(marketcap) bulk pull** (랭킹용) — 진행 중(resumable).
2. 월별 top-1500 PIT 유니버스 구성.
3. 그 union 종목 **SEP(closeadj) + SF1(gp/assets)** pull.
4. 동일 B2~B5 + 비용 → gross/net 지표.
5. §5 kill 조건 대조 → 판정(survive/dead) → 결과 리포트.
6. 그 후 Phase 1B 설계 or 단순팩터 종료.

> 데이터는 구독 중 확보(로컬 snapshot+hash). 해지는 이 윈도우 다 쓴 뒤.
