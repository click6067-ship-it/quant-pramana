# P3.1 — US Engine Final Packaging 결과 v0.1
**Date:** 2026-06-11 · **Status:** P3.1 DONE(PASS) · **Scope:** US-only. 다른 세션/사람이 봐도 바로 실행 가능한 상태로 정리.

## 한 줄
**clean 상태에서 `data.py validate` + 회귀 게이트(7실험 동결 재현)가 키 없이 PASS** — US-only 엔진이 재현·실행 가능하게 패키징됨. 결과 숫자·raw 데이터 0 변경.

## 산출물 (8/8)
1. **`phase1a/README_ENGINE.md`** — 빠른시작·8모듈 책임·config 사용법·snapshot 설명·불변규칙·디렉터리·다음단계.
2. **engine/ 모듈 사용법** — README에 `run_experiment(cfg)` 예시 + config 필드 + 7 앵커 config 위치(`_smoke_run.py` CFGS).
3. **`phase1a/legacy/`** — 원본 실험/빌더/pull 스크립트 **14개 copy 보존**(미접촉·증거·참조). engine/은 미의존.
4. **snapshot 설명** — README에 `manifest.json`(권위 기록, 13 raw + TICKERS) 기준 정리. `validate`로 무결성 확인.
5. **`requirements.txt`** — 핀(Python 3.12.3·pandas 3.0.3·numpy 2.4.6·Nasdaq-Data-Link 1.0.4·yfinance 1.4.1). 엔진 코어는 pandas+numpy만·API-free 명시.
6. **회귀 게이트 command** — `python engine/data.py validate` · `python engine/_smoke_run.py` (README 빠른시작).
7. **US-only scope + KR Deferred** — README 최상단 명시("KR = Future Market Adapter (Deferred), 미착수").
8. **본 문서.**

## 인증 (clean·키 숨기고)
| 검증 | 결과 |
|---|---|
| `data.py validate` | **PASS** — 기존 9 hash 1:1 무손상 · 신규 5개(TICKERS 포함) manifest 편입 |
| `_smoke_run.py` (회귀 게이트) | **PASS** — config로 7실험(B2~B5·sm q/e/b) 동결 숫자/verdict 재현 · exit 0 |

→ 패키징이 숫자를 바꾸지 않았음(리팩터 유효) + 키/인터넷 없이 재현 가능.

## P3.1에서 안 한 것 (범위 규율)
새 실험 0 · 결과 숫자 변경 0 · raw 데이터 변경 0 · API 호출 0 · KR 추상화 0 · 범용 플랫폼화 0.

## 디렉터리 (정리 후)
```
phase1a/
  engine/   (8 모듈 + 6 smoke, 정본·API-free)
  legacy/   (원본 14 스크립트 copy 보존)
  outputs/raw/ (동결 snapshot + manifest.json + HASHES.txt + TICKERS.csv)
  outputs/engine/ (universe·regression_report)
  reports/ · registry/ · requirements.txt · README_ENGINE.md
integrated/ (Lock·Protocol·Result·Roadmap 정본)
```

## 다음 (US-Only Roadmap)
P3.1 완료 → **P3.2 config/run/report workflow 정리**(named config registry · `run.py` CLI · `reports/` 표준화) → P3.4 housekeeping / P3.3 next-edge protocol or paper-ready simulator. 정본 = `US_Only_Completion_Roadmap_v0.1.md`.
