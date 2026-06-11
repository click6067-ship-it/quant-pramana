# pythia 작동방식 — 세부 설명서 (읽기용)

> "이게 *어떻게* 도는가"를 데이터 흐름 → 각 부품 → 실행까지 구체적으로. 파일·함수·실제 숫자로.

---

## 0. 전체 흐름 한눈에
```
KRX/DART  ──소싱──▶  PIT 캐시(parquet)  ──as_of(D 종가)──▶  ① 팩터/카운슬
                                                                  │  TargetWeights
                                                                  ▼
                                              leak-gate ◀── 백테스트(비용후) ──▶ walk-forward
                                              (진짜인가?)                              │
                                                  │ 통과한 것만                         │
                                                  ▼                                    ▼
                          ② Session 스파인 ──▶ ExecutionEngine ──▶ KIS 모의투자
                          (ledger에서 상태복원,                     (주문·체결)
                           리스크 게이트 작동)                          │
                                                                  ▼
                                              Phase-1 verdict 표 (매일)
```

## 1. 데이터 레이어 — PIT(point-in-time)가 핵심
**문제:** 백테스트가 "미래를 보면" 가짜 수익. **해법:** 모든 레코드에 `available_at` 타임스탬프, 읽을 땐 `available_at <= asof`만.
- `ParquetStore.read_prices_as_of(ticker, asof)` — 가격 PIT. (성능: 인스턴스당 parquet 1회 캐시 → 리플레이 >90s→2s.)
- `read_disclosures_as_of` — 공시(available_at = 공시일 09:00). 이벤트 팩터는 **rcept_dt < asof**(전일 이전)만 → 장후공시 누수 차단.
- `read_investor_flow_as_of` — 투자자별 순매수(available_at = **18:00 장후**) → 15:40 종가 결정 view엔 *전일까지만* 보임.
- `index_members_as_of` — 과거 시점 KOSPI200/KOSDAQ150 구성종목 → 생존편향 제거.
- `data.as_of(D 종가)` → `PointInTimeView`(`.prices` `.disclosures` `.investor_flow`). **전략은 오직 이 view만 본다 — 미래 불가.**

## 2. ① 리서치 — 팩터 + 카운슬
- **팩터**(`pythia/factors/`): `compute(view, universe, asof) → {종목: 점수}`. momentum(252/21)·low_volatility(60)·short_reversal(21)·**disclosure_reaction**(공시후 표류)·**investor_flow**(외국인+기관 순매수/거래대금, 사이즈중립).
- **파이프라인**: 각 팩터 winsorize→z-score→**동일가중 결합** → top-N 동일가중(long-only). 다팩터 = 자동 앙상블.
- **카운슬**: 멀티-LLM 병렬 비평(결함·누수·환각 적발). **주문권 0**(불변원칙 4). nof1: LLM 직접매매=전멸.

## 3. leak-gate — "이게 진짜인가?" 관문
**왜:** LLM/팩터 백테스트는 *사후지식 암송*으로 가짜로 좋을 수 있다(Profit Mirage). 집행 전에 강제로 검증.
`run_gate(prereg, in_sample, oos, baseline_oos)` — 순서대로 독립 판정:
1. **in_sample_edge**: 연환산 Sharpe ≥ 0.5? (없으면 시작도 안 함)
2. **cutoff_decay**: `1 − oos_Sharpe/in_Sharpe ≤ 0.5`? (LLM cutoff 2026-01 전후 50%↑ 붕괴 = 누수, 기각)
3. **baseline_excess**: OOS에서 baseline을 paired-t로 이김?
→ 단계별 verdict + 사유. **단일 pass/fail 배지 금지**(실패 유형 숨김 방지).

**walk-forward**(`walk_forward_folds`): 전체기간을 5 fold(각 ~10개월)로 쪼개 *각 fold에서* baseline을 이기나. **≥⅔(4/5) 이겨야 robust.** 단일 짧은 OOS 창의 운을 거른다. (momentum/monthly: 4/5 통과·평균 OOS Sharpe 0.83 — 진짜지만 모뎀.)

**prereg lockbox**: 전략·파라미터공간·trial_count·kill 규칙을 *결과 보기 전* 동결(해시). → 과적합·p-hacking 회계.

## 4. ② Session 스파인 — 리스크 게이트를 *살리는* 척추
**문제:** 일일서킷·max-DD·quit-line 같은 *시간/PnL 게이트*는 "어제 대비"가 필요한데, 매 sync는 무상태라 게이트가 *죽어 있었다*(조용히 PROCEED).
**해법:** `Session`이 append-only ledger를 *재생*해 상태 복원:
- `reconstruct_positions` · `cash_from_ledger` · `equity_marks` · `realized_pnl`(평균원가).
- `state(prices, today)` → equity·**economic_nav**(정지종목 0마크)·economic_loss·peak(고점)·day_start(당일 첫 mark).
- `step(engine, target, prices, today, limits)`: ① 당일 opening mark 먼저 append → day_start 고정 ② state 복원 → ③ `engine.sync(..., day_start_equity, peak_equity, economic_loss, strict=True)` → **게이트가 실제 입력으로 작동.** crash-safe(재시작해도 ledger에서 복원).
- **fail-closed strict**: limits 있는데 상태 없으면 거래 거부(죽은 게이트로 거래 금지).

## 5. 리스크 게이트 (결정론 규칙, Codex 확정 수치)
`assess(limits, day_start, current, peak, economic_loss)` 우선순위:
1. **PERMANENT_STOP** — economic_loss ≥ ₩3M(실현+평가, 정지종목 0) → 전량청산·영구중단
2. **KILL** — kill-switch 파일
3. **max-DD LIQUIDATE** — peak 대비 −15%
4. **일일 서킷** — −5% 전량청산 / −3.5% gross→50% / −2% 신규중단
5. PROCEED → `clamp_weights`(per-name tier cap 8/5/3% + gross ≤95%)
+ ADV 5% 참여 캡 · earn-the-scale 램프 · 중간복리 스윕.

## 6. Phase-1 — 매일 도는 증명 시스템
**3-arm**(A 동일가중 벤치·B momentum·C 투자자플로)을 *각자 일정대로* 전진:
- `run_arm`: [start,today] **매 거래일** 순회 — 리밸런스일=`session.step`(제출), 아니면 `session.mark`(거래없이 MTM). → equity 곡선·day-count가 *실제 거래일*.
- `compute_arm_metrics(ledger)`: ledger → ArmMetrics. **비용을 기간에 귀속**(Session이 step 전 mark → 그 fill 비용은 그 기간) → 정직한 gross/net Sharpe. + 턴오버·economic_loss·max_dd·벤치/ETF 대비 초과.
- `phase1_verdict(arm, m)` (동결):
  - 리스크 breach → **KILL**(항시)
  - 엣지표본 <60일 → **INSUFFICIENT**
  - 비용잠식·턴오버 드리프트 → **KILL**
  - 음의 엣지 → **KILL**(조기, 18개월 안 기다림)
  - 양의 엣지·실행표본(100체결/30종결) 미달 → **CONTINUE**(유망, 램프 아직)
  - 양의 엣지+실행표본 → **PASS**(다음 staging만, *수익주장 아님*)
- **라이브**(`phase1_live_day`): 영업일 1일치 — 리밸런스 제출 or 마크 + **비동기 체결 reconcile**(KIS 체결은 제출 몇 분 후 도착 → 영속상태 `<arm>.kisstate.json`로 *다른 프로세스가* 회수). 멱등(같은날 재실행=중복 안 함). **cost=commission+tax**(백테스트 정합).
- **안전:** `KISPaperBroker`는 vps(모의투자) 도메인 하드코딩 → 실자본 주문 *물리적 불가*. 실전 키 안 읽음.

## 7. 어떻게 돌리나
```bash
# 백테스트 dry-run (오프라인, 아무때나)
python -m pythia.phase1_run --mode dry-run --start 2025-09-01

# 라이브 (영업일 09:00–15:30 KST, .env에 KIS 모의 키)
set -a; . ./.env; set +a
python -c "import datetime as dt; from pythia.data.refresh import refresh_today; print(refresh_today('data_cache', dt.date.today()))"
python -m pythia.phase1_run --mode live   --ledger-dir runs/phase1   # KIS 제출
python -m pythia.phase1_run --mode report --ledger-dir runs/phase1   # 체결 reconcile + verdict 표
```
스케줄: **종가 D 결정 → 다음 세션 체결**(no same-day-close 누수). 상세 = `docs/PHASE1_RUNBOOK.md`.

## 8. 그래서 결과는? (정직)
3 family·14 config 정직 심판 → **현재 데이터로 통과 = momentum/monthly 하나(모뎀·해자아님).** 나머지 전부 무엣지/희석. **= 싸구려데이터 retail 엣지는 marginal.** 이건 *실패가 아니라 정직한 증명* — 시스템이 자기 창조자의 최강 가설까지 기각하며 "안 속였다". 진짜 증거는 **첫 영업일 live-forward** 후.
