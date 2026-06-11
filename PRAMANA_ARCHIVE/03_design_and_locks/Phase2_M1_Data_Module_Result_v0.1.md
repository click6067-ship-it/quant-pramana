# Phase 2 M1 — Data Module 결과 v0.1
**Date:** 2026-06-11 · **Status:** M1 DONE(PASS) · **Scope:** `phase1a/engine/data.py` — snapshot 로딩·해시·manifest *만*. 알파/feature/cost 로직 0.

## 한 줄
**기존 잠긴 snapshot 9/9 해시 byte-identical 재현(데이터 무손상·숫자 안 바뀜)** + stale HASHES.txt를 완전한 manifest.json으로 대체. M1 acceptance 8개 전부 충족.

## 무엇을 했나
`engine/data.py`: `load`(long-form 로드, pivot/feature 0) · `file_sha256` · `build_manifest`/`write_manifest` · `validate`(기존 HASHES 1:1 대조) · `snapshot_tickers`(명시 플래그 전용 1회 pull). `ALLOW_PULL=False` 기본.
- CLI: `python engine/data.py {validate|manifest|snapshot-tickers}`.

## 검증 결과 (hash 1:1 — 먼저 보고)
```
raw/ csv 13 · HASHES.txt 엔트리 10
[MATCH] 기존 해시 1:1 일치: 9/9  ✅ (재계산 == 기존 = 데이터 무손상)
  DAILY_all · SFP_SPY · SHARADAR_DAILY · SHARADAR_SEP · SHARADAR_SF1_ARQ
  · SP500_membership · broad_DAILY_pb · broad_SEP · broad_SF1
[MISMATCH] 없음 ✅
판정: PASS — 기존 B0/B1/B2~B5/Phase1B 데이터 안 바뀜
```
→ **기존 hash vs 새 data.py 재계산 hash = 완전 일치.** (요청대로 이걸 먼저 확인.)

## 재검토가 잡은 실제 결함 2개 (M1이 고침)
1. **HASHES.txt가 stale였다** — 디스크 raw 13개인데 HASHES엔 10개 + 파생파일(`broad_universe_top1500.csv`, 실제론 outputs/ 소속)이 잘못 포함. 최근 pull 4개(`broad_SF1_ext·smallmid_SEP·smallmid_DAILY·smallmid_SF1`)가 manifest에 누락. → **manifest.json으로 완전·일관 재생성**(13파일 전부 + rows/tickers/date범위/columns 메타).
2. **TICKERS가 live API** — 8개 스크립트가 `SHARADAR/TICKERS` 실시간 호출 → "API off + 재현가능"과 모순. data.py에 `snapshot_tickers`(명시 플래그 1회 pull) 추가. **아직 실행 안 함**(M2 universe builder 직전 동결 예정; API 키 재발급 후 실행 권장).

## Acceptance 대조 (8/8)
| # | 조건 | 결과 |
|---|---|---|
| 1 | 기존 raw 경로 그대로 읽기 | ✅ |
| 2 | 기존 HASHES와 동일 hash 재계산 | ✅ 9/9 일치 |
| 3 | manifest가 기존 hash 정보 포함(superset) | ✅ manifest.json 13파일+메타 |
| 4 | B0/B1/B2~B5/Phase1B 숫자 불변 | ✅ 해시 무손상(byte-identical) |
| 5 | data.py = 로딩·해시·manifest만 | ✅ |
| 6 | feature/signal/portfolio/cost 미접촉 | ✅ |
| 7 | API 기본 off | ✅ `ALLOW_PULL=False` |
| 8 | 명시 플래그 없이 pull 금지 | ✅ `snapshot_tickers`는 `allow_pull` 필수 |

## 산출물
- `phase1a/engine/data.py`
- `phase1a/outputs/raw/manifest.json` (권위있는 snapshot 기록, HASHES.txt superset)
- 검증 로그(위) · 본 문서

## 다음 (M2 직전)
- **API 키 재발급** 후 `python engine/data.py snapshot-tickers`로 TICKERS 동결(재현성 prerequisite).
- M2 `universe.py` — `build_broad_universe`·`build_smallmid_universe`를 PIT 빌더 1개로 통합(rank 범위·필터·survivorship), diagnostics **동일 재현**이 done 기준.
