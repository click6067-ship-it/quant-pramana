# B0 Pre-Implementation — Free-Sample Machine Validation Evidence
## (진짜 B0 결과 아님 — pre-B0 머신 검증 증거)

**Date:** 2026-06-10
**Scope:** Phase 1A / B0 직전, 데이터 파이프라인·체크 기계가 **실제 데이터로 작동하는지** 검증.
**상태:** **NOT a real B0 result.** Sharadar 무료 키 = 샘플(제한기간)이라, 본 문서는 *machine validation evidence*일 뿐 알파/벤치 결론이 아니다.
**스크립트:** `phase1a/b0_benchmark_sanity.py` (free=yfinance / sharadar=Nasdaq Data Link)

---

## 1. 무엇을 검증했나
- 데이터 로드 → 일별수익 → 월말 cap/equal 가중 → total-return 지수 → 6체크 → 스냅샷 동결(재현성) → CSV/registry 출력.
- 두 데이터 소스(yfinance free, Sharadar)에서 **end-to-end 작동 확인.**

## 2. Sharadar API/Schema (라이브 캡처 — `--inspect-schema`)
> 내가 문서로 추측한 게 아니라, 키로 라이브 API가 돌려준 실제 컬럼.

| Table | Columns |
|---|---|
| **SHARADAR/SEP** | `ticker, date, open, high, low, close, volume, closeadj, closeunadj, lastupdated` |
| **SHARADAR/DAILY** | `ticker, date, lastupdated, ev, evebit, evebitda, marketcap, pb, pe, ps` |
| **SHARADAR/TICKERS** | `table, permaticker, ticker, name, exchange, isdelisted, category, cusips, siccode, sicsector, sicindustry, figi, famaindustry, sector, industry, scalemarketcap, scalerevenue, relatedtickers, currency, location, lastupdated, firstadded, firstpricedate, lastpricedate, firstquarter, lastquarter, secfilings, companysite` |
| **SHARADAR/ACTIONS** | `date, action, ticker, name, value, contraticker, contraname` |

**B0 필드 매핑 확정:** TR=`SEP.closeadj` · 미조정=`SEP.closeunadj` · 시총(과거 일별)=`DAILY.marketcap` · 배당=`ACTIONS(action=dividend, value)` · 식별자=`TICKERS.permaticker` · 상폐플래그=`TICKERS.isdelisted` · 상장일=`TICKERS.firstpricedate` · 종목군=`TICKERS.category`(Domestic Common Stock).

## 3. ⚠️ 데이터 제한 (핵심 발견)
무료 키로 받은 SEP/DAILY = **2018-09-04 ~ 2018-12-31 (82 거래일), 9종목**(T 누락)뿐. 전체 이력 아님.
→ **다년·survivorship 포함 진짜 B0는 Sharadar Core US Equities 유료 구독 필요.** (무료 키는 키동작·스키마·기계 검증까지.)

## 4. 체크 결과
### (a) Sharadar 샘플 (cap-weight, 2018 Q4)
| Check | 결과 | 사유 |
|---|---|---|
| CHK-W weights sum≈1 | **PASS** | 3 rebalances, 0 bad |
| CHK-S survivorship | **WARN** | 표본에 상장폐지 종목 0 — 대형 생존주만이라 미검증. 풀데이터/폐지종목 필요 |
| CHK-F no-future | **PASS** | 상장(firstpricedate) 전 편입 0 |
| CHK-TR TR≥PR (same weighting) | **PASS** | TR×0.8584 ≥ PR×0.8522, 배당기여 +0.62%p (수정 후: 같은 cap-가중 비교) |
| CHK-D drift vs SPY | N/A | 샘플창에 SPY 비교 비어있음(풀데이터면 정상) |
| CHK-R reproducibility | FROZEN→PASS | 스냅샷 동결 후 재실행 시 data_hash/series_hash 동일 |

### (b) yfinance free (equal-weight, 2018~2026, smoke test)
| Check | 결과 | 사유 |
|---|---|---|
| CHK-W | PASS | 71 rebalances, 0 bad |
| CHK-S / CHK-F / CHK-TR | N/A | free=survivorship-biased·조정 semantics 불신 (숫자 불신 모드) |
| CHK-D vs SPY | INFO | corr=0.883 |
| CHK-R | FROZEN→PASS | 동결 후 동일 hash 재현 |

## 5. 수정 이력
- **CHK-TR 가짜경보 수정**: 기존 cap-weight TR vs equal-weight PR(가중 불일치) → **같은 가중 TR vs PR(=TR수익−배당수익률, ACTIONS 배당 사용)**. SEP엔 배당제외 가격 컬럼이 없어 ACTIONS 배당으로 PR 도출.
- **스냅샷 동결 추가**: 라이브 데이터 재실행 시 hash 흔들림 → 동결본 재사용으로 재현성 확보(CHK-R).
- **TICKERS dedup**: 티커당 여러 행(table=SF1/SEP) → SEP 행 우선 1행. (CHK-F 크래시 수정.)

## 6. 분류 / 결론
- 본 문서 = **pre-B0 machine validation evidence** (진짜 B0 아님).
- **기계는 실제 Sharadar 데이터로 작동 확인됨.** 남은 건 데이터 *범위*(유료 구독으로 다년 + 폐지종목 확보).
- 다음: Sharadar Core US Equities 구독 → SEP/DAILY/TICKERS/ACTIONS(+SP500) 전체 export → snapshot+hash → 진짜 cap-weight+survivorship B0.

## 7. 산출물
- 벤치 series: `outputs/b0_benchmark_{free,sharadar}.csv`
- 스냅샷(동결): `outputs/snapshots/{source}_<key>/`
- registry: `registry/b0_runs.csv`
- 코드: `b0_benchmark_sanity.py` · 키: `phase1a/.ndl_key`(gitignore, 로그 미출력)
