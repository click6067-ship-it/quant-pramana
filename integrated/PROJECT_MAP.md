# Pramana — Project Map (단일 네비게이션)
**Updated:** 2026-06-11 · **Status: WRAPPED** (`PROJECT_WRAP_v0.1.md`) · **Scope:** US-only (KR = Future Market Adapter, Deferred). · *각 항목 = 한 줄 + 정본 문서.*
> **현 사이클 매듭됨** — 6 edge 가설 전멸(정직한 negative) + 재사용 엔진/simulator 완성. 재개 트리거는 하단 결정 트리.

## 큰 그림
> v1 = **검증 엔진 만들기**(완료) · v2 = **엔진으로 새 edge source 1개씩 검증**(진행) · v3 = 살아남으면 quarantine 심화 · v4 = paper-ready candidate.
> **돈 되는 전략 만들기가 아니라, edge가 죽는지/사는지 *엄밀히 검증*하는 단계.**

## v1.0 — US validation engine = ✅ DONE (전부 CLOSED/COMPLETE)
| 단계 | 결과 | 정본 |
|---|---|---|
| Phase 1A 데이터·벤치(B0/B1) | PASS (SPY corr 0.998) | `Phase1A_Final_Empirical_Lock` |
| Phase 1A 단순팩터(B2~B5)·broad | value/mom/lowvol DEAD·quality quarantine FAIL | 같은 Lock |
| Phase 1B 저DoF 결합 | FAIL (OOS ridge IC-IR 0.01) | `Phase1B_LowDoF_Challenger` |
| arena A US event/surprise | FAIL (cap-weight 벽) | `US_event_drift_result` |
| arena B US small/mid cost-first | FAIL (유동성 집중) | `US_smallmid_costfirst_result` |
| **US 공개 cross-sectional/event** | **CLOSED** — edge 없음(정직한 negative) | `US_Public_Data_..._Chapter_Final_Lock` |
| Phase 2 Engine Hardening (M1~M8) | COMPLETE — `engine/` 8모듈 config-driven 동결재현 | `Phase2_M7_M8_Report_Run_Result` |
| P3 US-only Completion (P3.1~3.4) | COMPLETE — packaging·CLI·simulator·housekeeping | `P3_2_to_4_Completion_Result` |

**자산:** `phase1a/engine/`(data·universe·features·cost·evaluate·kills·report·run·configs·simulator) — API-free·config 하나로 7실험 동결 재현. `legacy/` 원본 보존. `README_ENGINE.md`.

## v2.0 — 새 edge source 검증 (진행 중)
| 사이클 | 결과 | 정본 |
|---|---|---|
| v2.0 True PEAD(가격반응 drift) | **FAIL** — IC 부호 반대(반전); 대형주 PEAD 없음 | `V2_pead_true_result` |
| **→ US public daily edge search** | **CLOSED** (5 family 전부 사망 = 로버스트 negative) | `Next_Data_Axis_Selection` |
| 방법 전환 | full validation 전 **rapid screen** 먼저(속도) | 〃 |
| v2.1 데이터축 선택 | 추천 A=analyst revision · B intraday 후순위 · C KR Deferred | 〃 |
| v2.1 Zacks 데이터 게이트 | **GO(구조)/HOLD(가격)** — ZACKS/EEH obs_date(PIT)+rev_up/down 존재, 무료=2018만 | `V2_1_estimate_data_gate` |
| **v2.1 2018 부호 스크린** | **FAIL(샘플)** — 무료=Dow30 메가캡 22종+2018뿐, *부호는 양수*(방향 안틀림). 디리스크 불가 | `V2_1_zacks_2018_rapid_screen` |
| v2.2 revision full kill-test | 📋 사전등록·**CONTINGENT**(Zacks 구독 시) — **결제 결정 대기** | `V2_2_Analyst_Revision_Protocol` |

## 현재 결정 트리 (라이브 — 결제 결정 대기)
```
[2018 부호 스크린 FAIL(샘플)]   무료=메가캡22종 → 디리스크 불가, 단 부호 양수
   → cheap 우회 없음 = 순수 결제 결정:
        (a) Zacks 전체 구독 ▶ v2.2 full kill-test
              ⚠ base-rate: v1 패턴 5회 반복(메가캡 cap-weight벽·소형 비용벽),
                revision도 소형강세 → top-1500서 같은 벽 가능
        (b) HOLD — blind spend 안 함(6 prior negative)
        (c) FMP/Finnhub free key 가입 후 대체 PIT 확인
        (d) 프로젝트 매듭(완성된 엔진+negative 자산)
```

## 불변 규칙 (전 구간 LOCKED)
데이터 접근 안 됨→실험 안 함 · PIT 불명확→실험 안 함 · 결제 전 rapid screen 먼저 · feature/cost/kill 튜닝 0 · universe 재조정 0 · KR/XGBoost/LLM/TSFM 0 · kill 결과 전 박기 · **no live/paper(통과 edge 0).**

## 진행률 (대략)
US-only v1: 100% · 장기 프로젝트: ~35–40% · v2: 데이터축 게이트 통과, 부호 스크린 실행 중.
