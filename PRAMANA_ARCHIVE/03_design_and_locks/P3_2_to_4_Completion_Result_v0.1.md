# P3.2–P3.4 — US-Only Completion 결과 v0.1 (Roadmap COMPLETE)
**Date:** 2026-06-11 · **Status:** P3.2·P3.3·P3.4 DONE → **US-Only Completion Roadmap = COMPLETE** · **Scope:** US-only. KR = Future Market Adapter (Deferred).

## 한 줄
config registry+CLI(P3.2) · paper-ready simulator(P3.3) · housekeeping(P3.4) 완료 → **US-only 프로젝트가 끝까지 완성·재현 가능·실행 가능** 상태. 결과 숫자·raw 0 변경.

---

## P3.2 — config/run/report workflow ✅
- **`engine/configs.py`** — 검증된 과거 실험 **10개 = named config**(B2~B5 · broad_quality_quarantine · phase1b_blend · broad_event · sm_quality/event/blend).
- **`engine/run.py` CLI** — `python engine/run.py <name> | all | list`.
- **표준 리포트** — `reports/engine/engine_runs.{csv,md}`.
- **검증(키 숨기고):** 10 named config 전부 동결 verdict/숫자 재현(B3 broad_retest=SURVIVE / quarantine=FAIL · phase1b/event/smallmid FAIL 정확). 1-커맨드 재실행 = acceptance 충족.

## P3.3 — paper-ready simulator (B 택1) ✅
**선택: B(simulator).** 이유 = "끝까지 완성"엔 *edge→실행 루프를 닫는 인프라*가 맞음(A=새 edge 탐색은 open-ended). **A(next-edge protocol)는 미래 사전등록 옵션으로 보존**(event/small-mid 잔여가 입력).
- **`engine/simulator.py`** — config → paper-trade-ready: long-only quantile EW 사이징 · 월 리밸런스 · **체결비용**(cost.py tier × |Δw|) · **결정적 risk-veto 훅**(per-name≤5%·gross≤100%, 리스크 엔진 최종권한 자리) · 벤치(CW·1/N) · NAV/PnL·turnover·maxDD·Sharpe·active/TE.
- **데모(sm_blend, 키 숨기고):** 125개월·보유 median 287종·CAGR net +13.2%·maxDD −41.7%·turnover 306%/yr·cost 2.95%/yr·active(net) vs CW +0.87%.
- **⚠️ 무거운 주의:** sm_blend는 **kill-test FAIL 신호** → NAV는 *배관 검증*이지 **거래 추천 아님. 현재 통과 edge 0 = no live/paper(LOCKED).** 시뮬은 edge가 통과하면 즉시 paper 가능하게 *미리 깐 인프라*.

## P3.4 — subscription/key housekeeping ✅(가능분) + 사용자 액션
- **`HASHES.txt` 완전 재생성** — 14 파일(기존 9 hash byte-identical 보존 + 신규 broad_SF1_ext·smallmid_*·TICKERS 편입). `data.py validate` = **전부 matched·신규 0·PASS**.
- **`.ndl_key` gitignored 확인** · raw 백업 1.1G(`outputs/raw/` + manifest.json).
- **남은 사용자 액션(내가 못 함):**
  1. **API 키 재발급** — Nasdaq Data Link 계정 → regenerate → `.ndl_key` 교체. (노출됨; 데이터 캐시 완료라 분석 무영향.)
  2. **구독 해지** — 윈도우 끝(엔진은 라이브 불필요). 추가 데이터 pull 필요하면 *해지 전에*. 해지 후 사용은 약관 회색지대.

---

## US-Only Completion Roadmap — 최종 상태
| 단계 | 상태 |
|---|---|
| P3.1 engine final packaging | ✅ DONE |
| P3.2 config/run/report workflow | ✅ DONE |
| P3.3 paper-ready simulator (B) | ✅ DONE (A는 미래 옵션 보존) |
| P3.4 subscription/key housekeeping | ✅ DONE (사용자 액션 2개 잔여) |

## 프로젝트 전체 상태
```
Phase 1A/1B (US)   ✅ CLOSED   — 공개데이터 cross-sectional edge 없음(4 arena)
Phase 2 (Engine)   ✅ COMPLETE — 8모듈 config-driven 동결재현
P3 (US Completion) ✅ COMPLETE — packaging·workflow·simulator·housekeeping
KR Adapter         ⏸ Deferred — 진입조건 충족, 미착수(US-only 고정)
```

## 불변 (US-only)
new feature/cost/kill 정의·튜닝 0 · 동결 숫자 바뀌면 실패 · API 기본 off · XGBoost/LLM/TSFM 금지 · KR 추상화 금지 · **no live/paper(통과 edge 0).**

## 다음 (열린 선택지)
- **(a)** P3.3-A next-edge protocol 사전등록 → 새 edge type 1회 kill-test(진짜 PEAD 가격반응 등).
- **(b)** KR Adapter 재가동(별도 결정 시) — KR-B0 data feasibility부터.
- **(c)** 현 상태로 마침표(완성된 negative-result + 재사용 엔진 + simulator 인프라).
