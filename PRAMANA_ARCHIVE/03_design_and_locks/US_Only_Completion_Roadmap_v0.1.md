# US-Only Completion Roadmap v0.1
**Date:** 2026-06-11 · **Status:** ACTIVE handoff (Phase 2 Engine Hardening COMPLETE 직후) · **Scope 결정: US-only 고정.**
**한 줄:** KR은 나중에. 지금은 US-only로 좁혀 프로젝트를 *끝까지 완성*한다.

## Scope 결정 (LOCKED)
- **프로젝트 scope = US-only 고정.** 모든 다음 작업은 US 데이터/인프라 위에서.
- **KR = Future Market Adapter (Deferred).** 버리지 않음 — `engine/`이 모듈화돼 있어 나중에 새 `data` 어댑터 + config로 *같은 kill-test*를 붙일 수 있음. **단 next-immediate 아님.** 진입은 US 완성 후 별도 결정.
- 기존 KR 산출물(DR-2/DR-2A red-team·Arena Gate의 C안)은 **Deferred 보관** — 폐기 아님, 재가동 시 재사용.

## 현 위치
- **Phase 1A/1B (US) = CLOSED** — 공개데이터 cross-sectional·long-only standalone edge 없음(level·결합·event·small/mid 4 arena 종료). `US_Public_Data_CrossSectional_Chapter_Final_Lock_v0.1.md`.
- **Phase 2 (Engine Hardening) = COMPLETE** — `engine/` 8모듈 config-driven 동결재현, 회귀게이트 7실험 PASS. `Phase2_M7_M8_Report_Run_Result_v0.1.md`.

## ★ US-Only Completion Roadmap (재정렬 — KR-B0 제거)

### P3.1 — US engine final packaging
**목표:** `engine/`을 깨끗·문서화·재현가능한 패키지로 동결.
- `engine/README.md`(모듈 책임·데이터 계약·API-free 보장·실행법).
- 원본 실험 스크립트 → `legacy/`로 **copy**(증거 보존, 참조 유지).
- snapshot/manifest 동결 재확인(`data.py validate` 통과 고정) + `TICKERS.csv` 포함.
- 종속성 핀(`requirements.txt` 버전 고정), `.venv` 재현.
- **Acceptance:** clean clone에서 `data.py validate` + 회귀게이트(`_smoke_run.py`) PASS.

### P3.2 — config/run/report workflow 정리
**목표:** "config 하나 = 실험 하나"를 운영 가능한 워크플로로.
- config 스키마 문서화 + **named config registry**(`engine/configs.py` 또는 yaml: B2~B5·smallmid·quarantine·phase1b·event 등 기존 실험을 named config로).
- `run.py` **CLI**(`python -m engine.run <config_name>` → 표준 report 출력).
- report 표준화(`reports/` 디렉터리·md+csv·verdict/kill 일관).
- **Acceptance:** named config로 임의 실험 1-커맨드 재실행 → 동결 숫자 재현.

### P3.3 — US next-edge protocol **또는** paper-ready simulator (택1, 사전등록)
**목표:** 다음 가치 단계 — *둘 중 하나를 사전등록하고 1회.* (둘 다 kill 조건 먼저.)
- **(A) US next-edge protocol:** *레벨/단순결합이 아닌* 새 edge type을 사전등록(예: 진짜 PEAD=공시 직후 *가격반응* drift, 또는 다른 미탐색 신호). 단순팩터 재탕 금지·feature 재정의 금지·kill 먼저. event/small-mid 잔여(decay 안 함)가 가리킨 방향.
- **(B) Paper-ready simulator:** config(통과 시)를 *paper-trade-ready* 백테스트로 — 체결·슬리피지·포지션 사이징·리밸런스 캘린더·리스크 veto. **단 현재 통과한 edge 0** → 이건 *edge보다 앞선 인프라*(준비). edge가 통과하면 즉시 paper 가능하게.
- **권고:** A(next-edge)로 "혹시 잡을 게 있나"를 *한 번 더 규율 있게* 확인 → 또 죽으면 B(simulator)는 미래 edge 대비 인프라로. 또는 B를 먼저 깔고 A를 그 위에서 돌려도 됨. **결정 보류 → 이 단계 진입 시 택1.**
- **Acceptance(A):** 사전등록 kill-test 1회 결과(PASS=Phase1C 후보 / FAIL=US 다음 후보). **(B):** 통과 config를 넣으면 paper-trade 신호·비용반영 PnL 시뮬 산출.

### P3.4 — subscription/key housekeeping
**목표:** 비용·보안 정리(엔진은 라이브 구독 불필요 = 캐시 기반).
- **API 키 재발급**(노출됨; 데이터 캐시 완료라 분석 무영향) → `.ndl_key` 교체.
- 데이터 백업·hash 매니페스트 최종 검증(`HASHES.txt`/`manifest.json`).
- **구독 해지**(윈도우 끝). 해지 후 사용은 약관 회색지대 — 추가 pull 필요하면 해지 전에.

## 실행 순서 (권고)
**P3.1 → P3.2 → P3.4 → P3.3** 또는 **P3.1 → P3.2 → P3.3 → P3.4.**
- P3.1·P3.2(패키징·워크플로)는 지금 바로·기계적·저위험 → 먼저.
- P3.4(housekeeping)는 P3.3에서 추가 데이터 pull이 필요 없다고 확정되면 바로 가능(라이브 불필요). P3.3에서 새 데이터(예: intraday/가격반응)가 필요하면 **해지 전에 pull**.
- P3.3은 방향 결정(A/B)이 필요한 단계 → P3.1/P3.2 끝내고 결정.

## 불변 (US-only 동안)
KR 즉시 점프 금지 · XGBoost/LLM/TSFM/deep 금지 · 기존 feature/cost/kill 정의·튜닝 변경 금지 · kill 조건 먼저 박기 · 동결 숫자 바뀌면 실패.

## Future Market Adapter (KR) — Deferred (참고만)
재가동 시: 새 `engine/data` 어댑터(KR PIT 유니버스·상폐/관리종목·거래세·공시 timestamp KIND/DART·라이선스 KRX OpenAPI) → **KR-B0 data feasibility 먼저**, 대형주 단순팩터 포팅 금지. 산출물 DR-2/DR-2A·Arena Gate C안 보관. **단 US 완성 전엔 착수 안 함.**
