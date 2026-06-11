# B0 Result v1 — Data-only Benchmark Sanity (REAL Sharadar)
## data gate + benchmark drift + reproducibility + final decision (consolidated)

**Date:** 2026-06-10
**Experiment:** `B0-sharadar` · cap-weight total-return benchmark sanity
**Source:** Sharadar (Nasdaq Data Link, Core US Equities Bundle, 구독 활성) — 실제 데이터
**Snapshot:** `outputs/snapshots/sharadar_035b85ec4b68/` (동결) · **data_hash=`a41b3972bcb6e20d`** · **series_hash=`671431c05bc492e3`**
**Universe (demo):** 12 live + **6 delisted**(MRO·ENV·CNSL·LUMO·MNTX·AUMN) = 18 · 2016-01-04~2026-06-09 (2623일, 88 월리밸런스)
**Verdict:** **PASS (machinery, real data)** — *단 demo 유니버스. 수익률(index 100→801)은 신뢰 대상 아님.*

> B0의 성공 = 수익이 아니라 "데이터·벤치가 정직·재현 가능". 아래 6게이트로 판정.

---

## 1. Data Gate / Checks (실측)
| Check | 대응 게이트 | 결과 | 근거 |
|---|---|---|---|
| CHK-W weights sum≈1 | (가중 정합) | **PASS** | 88 rebalances, 0 bad — cap-weight(DAILY.marketcap) 합=1 |
| CHK-S survivorship | G-04 delisting/inactive | **PASS** | 상장폐지 6종이 유니버스에 보존(isdelisted=Y), 폐지 전까지 보유 후 자연 제외 |
| CHK-F no-future | G-01/G-02 | **PASS** | 0 violations — firstpricedate 이전 편입 0 |
| CHK-TR total-return≥price-return | G-06 dividend/TR | **PASS** | same cap-weight TR×8.0134 ≥ PR×6.4553 (10년 배당기여 +155.8%p) → **배당이 실제로 TR에 반영됨** |
| CHK-D drift vs SPY | G-09 benchmark sanity | **INFO** | SPY(SFP) 상관 **0.935** = 재구성 벤치가 광범위 지수처럼 거동(sanity OK). 연환산차 +6.37%p = demo 유니버스 구성효과(자동실패 아님, 신뢰 금지) |
| CHK-R reproducibility | G-12 lineage/hash | **PASS** | 동결본 재실행 시 data_hash·series_hash 동일 재현 |

**미적용(이 demo 범위 밖):** G-03 filing-lag·G-13 restatement(펀더멘털=B2+), G-10 cost(B1+), G-14 license lineage(=구독 license_state는 §4).

## 2. Benchmark Drift
- **Internal reconstruction (hard):** 88개 월말 cap-weight 합=1, 폐지종목 폐지 전까지 반영, 배당 TR 반영 → **재구성 일관, 미설명 drift 없음 → PASS.**
- **External comparator (diagnostic):** vs SPY(SFP closeadj) 상관 **0.935**. 연환산차 +6.37%p는 **유니버스 차이**(18종 집중·NVDA/V 등 고성장 편향)로 설명됨 — 외부지수와 다른 건 정상(자동실패 아님). 광범위 유니버스로 가면 차이 축소 예상.

## 3. Reproducibility Manifest
| 항목 | 값 |
|---|---|
| snapshot dir | `outputs/snapshots/sharadar_035b85ec4b68/` (px_tr·px_unadj·divs·mktcap·spy·meta 동결) |
| data_hash | `a41b3972bcb6e20d` |
| series_hash | `671431c05bc492e3` |
| 재실행 결과 | 동결본 재사용 → **동일 hash 재현 (CHK-R PASS)** |
| code | `phase1a/b0_benchmark_sanity.py` (venv: pandas 3.0.3) |
| 주의 | 라이브 재다운로드(--refresh)는 데이터 갱신으로 hash 달라질 수 있음 → **동결 스냅샷이 재현의 기준** |

## 4. License / Data lineage
- 데이터: Sharadar Core US Equities Bundle (Nasdaq Data Link), 구독 **활성**(개인 Non-Pro 월간). 키=`phase1a/.ndl_key`(gitignore, 로그 미출력).
- ⚠️ **구독 해지 후 이 데이터로 추가 연구(B2~)는 약관 회색지대** — B0는 구독 중 완료(OK). 후속은 재구독 권장.

## 5. Final Decision
**B0 = PASS (machinery, real data).** 데이터 로드·상장폐지 포함·cap-weight 합1·기업행동/배당 처리·self-built TR 생성·drift 설명·재현 — **전부 실제 10년 Sharadar 데이터에서 충족.**

**정직한 범위 한계 (중요):**
- 이건 **18종 demo 유니버스**의 B0 — *기계·데이터·체크가 진짜 데이터에서 작동함*을 증명. **완성된 production 벤치마크가 아님.**
- production B0는 **정의된 광범위 유니버스**(예: 전체 Domestic Common Stock + 유동성필터, 또는 월별 top-N by marketcap)로 확장해야 함. 그땐 SEP/DAILY 더 많은 종목 export 필요.

## 6. Next
1. (선택, 권장) **유니버스 확장 B0** — top-N by marketcap(월별) 또는 SP500 구성종목 기반 PIT 유니버스로 재실행 → 진짜 광범위 벤치.
2. **B1 = 1/N universe baseline** (B0의 cap-weight 대신 동일가중) — B0 통과했으니 진행 가능.
3. 구독 1개월 내 필요한 raw export(SEP/DAILY/TICKERS/ACTIONS/SP500)를 hoard하려면 별도 bulk export(큼). 해지 후 사용은 §4 caveat.

---
> 산출물: 벤치 series `outputs/b0_benchmark_sharadar.csv` · 스냅샷 `outputs/snapshots/sharadar_035b85ec4b68/` · registry `registry/b0_runs.csv` · 코드 `b0_benchmark_sanity.py`
