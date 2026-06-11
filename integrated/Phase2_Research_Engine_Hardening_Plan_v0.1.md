# Phase 2 — Research Engine Hardening Plan v0.1
**Date:** 2026-06-11 · **Status:** US 챕터 종료 후 엔진 고도화(알파 실험 아님) · **목표:** 같은 방식으로 어떤 데이터(KR·US event·다른 벤더)든 *빠르게 죽이거나 살리는* config-driven 검증 엔진.
**전제(LOCKED):** 추가 알파 실험 금지. 이 단계는 *기존 검증된 로직을 재사용 가능 모듈로 정리*하는 리팩터 — **feature/cost/kill 정의는 동결값 그대로(숫자 1:1 재현)**, 새 정의·튜닝 0.

> **재검토 교정(2026-06-11, 구현 전 적용):**
> 1. **범위 규율 = consolidation, NOT 플랫폼.** Phase 2 = 기존 7스크립트 복붙 제거 + 잠긴 숫자 재현으로 한정. KR 대응은 부산물(Deferred를 위한 지금 추상화 = 투기적 금지). analysis-paralysis 재발 방지.
> 2. **Acceptance 완화:** "7개 전부 1:1"은 evaluate.py를 kitchen-sink로 만듦 → **앵커 2~3개(b2b5_broad·b_smallmid·quality_quarantine)**만 회귀 기준, 나머지는 "표현 가능하면 됨".
> 3. **data.py = long-form만**(pivot/feature 수학 0·config 의존 0). thin 모듈(kills/report)은 class 아닌 **함수로 시작**(과설계 방지).
> 4. **legacy/ = move 아닌 copy**(기존 리포트/마일스톤 참조 보존).
> 5. **신규 발견 결함:** ① HASHES.txt가 이미 stale(13파일 중 10·파생파일 오포함) → manifest 일원화가 정확히 그 fix. ② **TICKERS가 live API**(8스크립트) → 동결 필요(M1에 `snapshot_tickers` 명시플래그 추가, M2 전 실행).

## 왜
지금 7개 스크립트(`b2b5_broad·quality_quarantine·phase1b_lowdof·us_event_drift·build_*_universe·b_smallmid`)가 **같은 로직을 복붙**(PIT 멤버십·forward return·z-score·Q5-Q1·cost tier·IC/IC-IR·subperiod·turnover·kill). 실제로 같은 버그를 두 번 잡았다(PIT ffill, `.loc[list]` KeyError, momentum 캘린더월말). 모듈화하면 버그 한 번만 잡고, KR/다른 arena를 *며칠*이 아니라 *시간* 단위로 검증.

## 타겟 구조 (config-driven)
```
phase1a/engine/
  config.py     # @dataclass ExperimentConfig (universe·dates·filters·cost·kills·features) — YAML/dict 로드
  data.py       # 캐시 로드 + hash/manifest 검증 (snapshot 동결·재현성)
  universe.py   # PIT 유니버스 빌더 (marketcap rank 범위·price/ADV 필터·survivorship)
  features.py   # 동결 feature registry (value/quality/momentum/lowvol/event/blend) — 정의 변경 잠금
  cost.py       # 비용 모델 (mktcap/ADV tier, base/2x/3x) — 동결 tier
  evaluate.py   # 메트릭 (IC·IC-IR·Q5-Q1·long-only vs CW/1N·subperiod·size/liq 버킷·turnover)
  kills.py      # kill-condition 프로토콜 템플릿 + verdict 적용 (사전등록 dict)
  report.py     # 표준 report.md + result.csv 생성기
  run.py        # config 받아 위를 오케스트레이션하는 단일 러너
```
기존 스크립트 = 이 모듈을 호출하는 얇은 config로 축소. 원본 스크립트는 `legacy/`로 보존(재현 기준).

## 작업 항목 (M1–M8)
| # | 모듈 | 내용 | done 기준 |
|---|---|---|---|
| M1 | `data.py` | snapshot 로드·hash/manifest 검증·재현성(동결) 일원화 | HASHES.txt 대조 PASS·동일 data_hash 재현 |
| M2 | `universe.py` | PIT 빌더(rank 범위·필터·survivorship) — broad/smallmid 빌더 통합 | top-1500·rank1001-3000 diagnostics **동일 재현** |
| M3 | `features.py` | 동결 feature registry(6개) — 정의·부호·PIT 로직 잠금 | 각 feature 단위테스트(정의 1:1) |
| M4 | `cost.py` | tier 비용 모델(mktcap/ADV)·base/2x/3x | 동결 tier(5/10/15·25/45/75bp) 재현 |
| M5 | `evaluate.py` | 메트릭 일원화(IC~버킷~turnover) | 7개 리포트 핵심수치 **재현 일치** |
| M6 | `kills.py` | 사전등록 kill 템플릿(dict)·verdict | 각 protocol kill 그대로 적용 |
| M7 | `report.py` | 표준 md+csv 생성기 | 기존 리포트 포맷 호환 |
| M8 | `run.py`+`config.py` | config-driven 러너 | **회귀: b_smallmid/quality_quarantine를 엔진으로 재실행 → 동결 숫자 재현** |

## ★ Acceptance (회귀 게이트)
리팩터 완료 = **과거 잠긴 실험(예: b_smallmid·quality_quarantine·phase1b)을 새 엔진 config로 재실행했을 때 동결 리포트 숫자를 재현**(IC-IR·net·kill verdict 일치). 재현 안 되면 리팩터 무효(숫자가 바뀌면 그건 리팩터가 아니라 새 실험 = 금지). → snapshot hash로 데이터 동일성도 보장.

## 종료선 유지 (Phase 2 동안 금지)
feature 재정의·cost bar 변경·universe 범위 변경·kill threshold 변경·새 신호 추가·XGBoost/LLM/TSFM·KR 즉시 착수. **Phase 2는 코드 정리지 알파 탐색이 아니다.**

## KR = Future Arena Module
- **상태:** Not started / **Deferred.**
- **진입 조건:** US chapter final lock(완료) **+** engine hardening(M1–M8) 완료.
- **첫 단계(진입 시):** 바로 팩터 금지. **KR-B0 = data feasibility 먼저** — PIT 유니버스 · 상장폐지/관리종목 · 거래세/수수료 · 벤치마크 · 공시 timestamp(KIND/DART I002) · 데이터 라이선스(KRX OpenAPI 비상업·재배포). (기존 DR-2A/DR-2 red-team 산출물 재활용.)
- **원칙:** KR 대형주 단순팩터 포팅 금지 · small/mid + 공시이벤트 + 구조적 데이터우위 중심 · carry-forward 가설(event decay 덜함·신호 small/mid서 강함) 검증.
- 엔진이 모듈화돼 있으면 KR은 새 `data.py` 어댑터 + config로 *같은 kill-test*를 빠르게 돌릴 수 있음.

## 산출물
`phase1a/engine/*` · `phase1a/legacy/`(원본 보존) · `registry/phase1a_milestones.csv` 갱신 · 회귀 재현 로그.
