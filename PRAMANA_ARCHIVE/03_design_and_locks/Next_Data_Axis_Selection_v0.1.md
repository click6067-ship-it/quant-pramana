# Next Data Axis Selection v0.1
**Date:** 2026-06-11 · **Status:** US public **daily cross-sectional/event** edge search = **CLOSED.** 다음 = 데이터축 전환 선택(실험 전).
**방법 전환:** 앞으로는 full validation(사전등록 kill-test) *전에* **rapid screen** 먼저 — 무료/샘플 데이터로 *단일 IC-IR + 비용부호 1회 체크*. 신호 없으면 풀 파이프라인 안 만든다(진척 속도↑).

## 1. 왜 US public daily edge search를 닫는가
사전등록 kill로 **5개 edge family 전부 사망**: ① 단순 level 팩터 ② 저DoF 결합 ③ small/mid(비용후) ④ event/surprise proxy ⑤ True PEAD(반전). "운 나쁜 5번"이 아니라 **로버스트한 negative** — 솔로가 *공개·일별·cross-sectional* US 데이터로 잡을 수 있는 edge는 없다(있어도 비용/유동성/메가캡 벽). 같은 우물을 더 파면 6번째 negative. → **이 축은 닫고, 데이터 축을 바꾼다.** (엔진은 재사용.)

## 2~3. 다음 후보 데이터축 3개
| 축 | 예상 edge source | 비용 | 데이터 접근성 | 솔로 구현난이도 | 엔진 재사용 |
|---|---|---|---|---|---|
| **A. Analyst estimate / revision** | **estimate revision momentum·진짜 SUE(consensus vs actual)·dispersion** — v1이 못 한 *진짜 surprise* (가장 로버스트한 공개 anomaly 중 하나) | **저~중** (Zacks via NDL·Finnhub·FMP·EODHD ~$30–100/mo; I/B/E/S=고가) | **중** (염가벤더 접근 쉬우나 **PIT consensus/revision history**=look-ahead 리스크, 확인 필요) | **낮음** (cross-sectional 신호 → 기존 engine universe/cost/evaluate/kills 직접 재사용, feature만 추가) | **높음** |
| **B. Intraday / microstructure** | 단기 reversal·overnight vs intraday·order-flow imbalance | **중~고** (Polygon ~$30–200/mo; tick/L2 훨씬 비쌈) | **중~하** (분봉 접근가능, 정밀 tick/quote 비쌈) | **높음** (일별 엔진과 다른 인프라·데이터량 大·슬리피지 지배; 빠른 alpha=HFT 영역 솔로 불리) | **낮음** (event/intraday는 재작성) |
| **C. KR adapter** | KR small/mid + 공시이벤트(less-arbitraged) | 낮음(OpenDART/KRX 무료) but **엔지니어링 大** | **하** (처음부터 구축·KRX OpenAPI 비상업 라이선스·PIT 멤버십 난) | **높음** (새 시장·벤치·거래세·NXT/SOR) | 중(data 어댑터만 새로) |

## 4. 다음에 실제로 할 1개 (추천)
**→ A. Analyst estimate / revision.** 이유:
1. **v1의 *정확한* 데이터 공백을 메운다** — v1 event는 "analyst estimate 없어 순수 surprise 제한"이 한계였다. revision/SUE가 그 진짜 신호.
2. **기존 엔진 직접 재사용** — cross-sectional·일별·universe/cost/evaluate/kills 그대로, feature(revision) 하나만 추가 = 빠름.
3. **문헌상 가장 견고한 공개 anomaly 중 하나**(가격반응 PEAD보다 강함) → "5개 죽였는데 이것도?"의 가장 공정한 마지막 테스트.
4. 비용·접근성 현실적(염가 벤더). **단 핵심 리스크 = PIT(look-ahead-free) revision history 확보** — 이게 rapid screen의 첫 확인 대상.

**rapid screen 계획(실험 아님, 다음 단계):** 염가 벤더의 *무료/샘플* estimate revision으로 (a) PIT 이력 존재 여부, (b) 소규모 종목/기간 단일 IC-IR + 비용부호 1회 — 신호 부호라도 맞으면 풀 사전등록 kill-test, 아니면 즉시 폐기.

**B/C 보류:** B(intraday)=고비용·HFT 경쟁·인프라 재작성 → 후순위. C(KR)=Deferred 유지(최대 scope 확장).
