# Pramana — Project Wrap v0.1 (US-only, WRAPPED)
**Date:** 2026-06-11 · **Status:** **WRAPPED** (현 사이클 매듭) · **Scope:** US-only. KR = Future Market Adapter (Deferred).
**한 줄:** 돈 버는 전략은 못 찾았다. 대신 **가짜 알파를 엄밀히·반복적으로 죽이는 검증 시스템 + 감사 가능한 negative + 실행 인프라**를 완성했다. blind spend 없이 깨끗이 닫는다.

## 무엇을 만들었나 (자산 — 재사용 가능)
- **`engine/` 8모듈 config-driven 검증 엔진** (data·universe·features·cost·evaluate·kills·report·run·configs·simulator). **API-free**(캐시 snapshot+manifest+TICKERS), config 하나로 과거 실험 동결 재현(회귀 게이트 PASS). `README_ENGINE.md`·`requirements.txt` 핀·`legacy/` 원본 보존.
- **paper-ready simulator** — 통과 edge 나오면 즉시 NAV/PnL·체결비용·risk-veto로 돌릴 인프라.
- **데이터 정직성 레이어 검증** — 자작 S&P500 cap-weight TR이 SPY와 corr 0.998(PIT·survivorship·배당·CA 정확).

## 무엇을 죽였나 (엄밀한 negative — 진짜 결과물)
사전등록 kill로 **6개 edge 가설 전멸**:
| # | 가설 | 결과 |
|---|---|---|
| 1 | 단순 level 팩터(value/quality/momentum/lowvol) | DEAD |
| 2 | 저DoF 결합(blend/rank/ridge OOS) | DEAD (OOS IC-IR 0.01) |
| 3 | small/mid 비용후 | DEAD (유동성 집중) |
| 4 | event/surprise proxy | FAIL (cap-weight 벽) |
| 5 | True PEAD(가격반응 drift) | FAIL (반전) |
| 6 | analyst revision(데이터 게이트) | HOLD (무료론 디리스크 불가; 부호만 양수) |
**→ 공개·일별·cross-sectional US 데이터로 솔로가 잡을 거래가능 standalone edge = 없음.** 로버스트한 negative(운 아님).

## 미래 재방문 후보 (HOLD/Deferred — 폐기 아님)
- **analyst estimate revision** — 유일하게 *부호가 안 틀린* 신호(2018 메가캡 22종서 IC+). 데이터=Zacks `ZACKS/EEH`(obs_date PIT+rev_up/down) 구조 완벽하나 전체 history=유료. 재개 시: 구독 → 사전등록 `V2_2_Analyst_Revision_Protocol` 실행. **단 base-rate 경고: revision도 소형강세 → top-1500서 cap-weight 벽 반복 가능.**
- **intraday/microstructure** — 고비용·HFT 경쟁(후순위). **KR adapter** — Deferred(새 data 어댑터+config).

## 정직한 최종 결론 (no echo)
대부분의 리테일 퀀트는 `sm_blend t=3.75`나 `revision 부호 +` 같은 걸 보고 라이브로 갔을 것이다. 이 시스템은 그걸 `lowest_liq_only`·`sample 부족`으로 잡고 **멈췄다.** "edge 없음을 엄밀히 증명 + 멈출 줄 아는 규율"이 이 프로젝트의 산출물이고, 그게 정직한 성공이다. 같은 우물을 6번째 파지 않는 것도 결과다.

## 남은 housekeeping (사용자 액션, 엔진엔 무영향)
- **API 키 재발급**(노출됨; 데이터 캐시 완료라 분석 무영향).
- **Sharadar 구독 해지**(~2026-07-10 갱신 전; 엔진은 라이브 불필요). 추가 pull 필요하면 해지 전에.

## 완수율 (기준별 — 헷갈리지 않게 나눔)
| 기준 | 완수율 | 비고 |
|---|---|---|
| **US-only v1 (검증 엔진)** | **100%** | 완료 |
| **검증 엔진 + negative research 결과물** | **100%** | 완성품으로 봐도 됨 |
| 수익 모델 → paper/live 프로젝트 | **~45–50%** | 엔진·파이프·시뮬·negative 완료 / edge·모델·paper·live·risk monitor 미완 |
| 원래 상상한 US+KR 장기 전체 | **~35–40%** | KR·실거래·운영체계 미포함 |

## 한눈에 (done / not-done)
```
[완료] 설계 · US 데이터 검증 · 단순/결합/event/small-mid/PEAD 검증
       · 검증 엔진(8모듈) · paper-ready simulator · US-only v1 wrap
[미완] 살아있는 edge · 최종 모델 · paper/live candidate
       · broker 연동 · production risk engine · 실시간 모니터링
[보류] KR adapter · intraday/microstructure · analyst revision full-history
```

## 모델 결정은 언제? (아직 아님)
`새 데이터축 선택 → rapid screen 통과 → full validation 통과 → 비용/유동성/최근구간 통과 → **그때** 모델 결정.`
현재 = 검증 엔진 있음 · **살아있는 edge 없음** → 최종 모델 없음(정상). *모델을 못 정한 게 아니라, 정할 만한 edge가 없다는 걸 검증했다.*

## 재개 트리거 (나중에 누가 봐도)
다음 진짜 진전 = 모델 고르기가 아니라 **새 데이터축에서 edge 후보 1개를 rapid screen으로 살리는 것.** → `PROJECT_MAP.md` 결정 트리: (a) Zacks 구독→v2.2 revision, (c) FMP/Finnhub 대체, KR adapter, intraday. 엔진은 새 `data` 어댑터+config면 *같은 kill-test* 즉시 가동.
