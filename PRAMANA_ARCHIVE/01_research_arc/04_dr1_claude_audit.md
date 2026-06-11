# 04 · DR-1 Claude Code Red-team Audit (Adversarial Fact Auditor)

> **Provenance:** Claude Code `deep-research` harness, 2026-06-07. 5 search angles → 23 sources fetched → 85 claims extracted → **25 verified by 3-vote adversarial verification (need 2/3 refutes to kill)** → 18 confirmed / 7 killed → 9 synthesized findings. Primary-source tilt: FSC, FTSE Russell/LSEG, CRSP, Journal of Finance / RFS / JFE.
> **역할:** Primary 보고서가 아님. ChatGPT DR-1 Primary(`03`)에 대한 적대 감사. `05`에서 머지.
>
> ## ⚠️ 이 라운드의 단일 최대 갭 (먼저 읽을 것)
> 비용 증거는 **전부 US/CRSP 기반**이다. "flat-bps/스프레드-only 모델은 위험하다"는 검증됐지만, **한국 고유 비용 크기(증권거래세 2025–26 단계적 인하·NXT vs KRX 수수료·FX·배당원천세)는 이번 라운드에서 검증되지 않았다.** KR cost-lock 전 KRX/FSC/한국 세법 1차 소스 확보가 게이팅 의존성. **아래 한국 관련 수치는 어느 것도 잠금 근거로 쓰지 말 것.**
> 또한 refute된 정량값(아래 §refuted)은 인용 금지: 50% 턴오버 컷·모멘텀 7.2–7.6%·밸류 2.6–4.1% 비용·Russell 결정론적 rank 컷·$1 가격스크린·CRSP DelRet=clean solution.

---

## 1. Verdict — **PATCH-BEFORE-LOCK**

- 프로젝트가 "~일 수 있다(may be)"로 깃발 단 리스크가 **전부 문서화된 live 조건으로 확인**됐다. 가설이 아니라 현실. 방향(KR/US benchmark·universe·cost·data를 잠그기 전 검증)은 옳다.
- **KR = 확정 2-venue 시장** (KRX + Nextrade ATS, 2025-03-04 live). SOR 의무, 유동성 분산을 규제당국이 공식 예상 → 가정 #6(paper→live drift) **CONFIRMED**. NXT 거래가능 종목군은 분기 재선정되는 **PIT 문제**.
- **US 유니버스 전부 non-trivial PIT 캘린더 보유**: Russell 연1회→**반기(2026-12부터)** 레짐 전환 + 분기 IPO/float; CRSP는 breakpoint/packeting·고정 N 없음·분기 transition window → 가정 #7 **CONFIRMED**. 연 1회 스냅샷 모델은 투자가능 유니버스를 오기재.
- **생존편향/상폐편향 크고**(누락 상폐수익률 ~-30%) **cross-sectional 알파가 만드는 바로 그 포트폴리오**(소형·저가·동일가중·CAR)에 집중 → 생존편향프리+상폐수익률 보정 데이터가 **알파 연구 전 hard prerequisite**.
- 비용은 수익성 + **통계 유의성**을 동시에 깎고, all-in > 스프레드 기반, 규모와 함께 악화 → 가정 #5 지지. **단** 고턴오버에서 결정적이고 cost-mitigation 설계에 조건부 → flat-bps 위험. **CRITICAL: KR 비용 크기는 이번 라운드 미검증 = KR cost-lock 전 최대 갭.**

---

## 2. Assumption Attack Table

| # | Assumption | Why it may be wrong / under-specified | Official evidence needed | Severity | Patch required |
|---|---|---|---|---|---|
| 1 | KR-first > US-first/parallel | 검증된 PIT/생존편향 **툴링 증거가 압도적으로 US/CRSP-중심**. 동등한 KR 벤더 capability(생존편향프리·PIT 멤버십·상폐수익률)는 미확인 → KR-first가 "relevance엔 유리하나 data-feasibility 근거는 가장 약한" 역설 | KR 생존편향프리/PIT 벤더(FnGuide 등) 실측 spec | **High** | KR 데이터 벤더 capability 검증 전 KR-first '조건부'. §7 참조 |
| 2 | KOSPI200+KOSDAQ150(유동성필터) = 합리적 KR Phase1 유니버스 | KR 인덱스 methodology 1차 소스가 이번 라운드 **확보 실패**(KRX 사이트 unreliable/0-claim). 멤버십 PIT 재구성 가능성·유동성 decile 미검증 | KRX KOSPI200/KOSDAQ150 구성·재조정 규정 원문, PIT 멤버십 이력 | **High** | KR 인덱스 methodology를 Missing Source로 등록·재조사 |
| 3 | KRX300 TR = 합리적 KR primary 벤치 | KRX300 TR 산출·TR 처리·재조정 methodology **1차 소스 미확보**. (US 벤치만 깊게 검증됨) | KRX300 TR index methodology 원문(TR 계산·리밸런스) | **High** | KRX300 TR methodology 확보 전 벤치 잠금 보류 |
| 4 | 자체 cap-weight TR = secondary 필요 | 자체구축 시 배당 재투자·CA·생존편향 처리가 그대로 §6 데이터 문제 상속. "대조 벤치"가 오히려 데이터 부채 | (위 데이터 피저빌리티에 종속) | Medium | 자체 벤치는 Layer 0 데이터 계약 통과 후에만 |
| 5 | KR 거래세/수수료/FX/배당세/스프레드/슬리피지/임팩트가 모델선택 지배 | 방향은 지지(비용이 유의성까지 깎음)되나 **수치는 US 연구 기반**. KR 거래세 단계적 변경·NXT/KRX 수수료·FX·배당세 **미검증**. flat-bps도 unsafe | 증권거래세법 단계율(2025–26), NXT/KRX 수수료표, FX·배당원천세 | **Critical** | flat-bps→turnover-aware+cost-mitigation+scale-sensitive; KR 비용 1차 소스 확보 |
| 6 | NXT/SOR·분절 거래가 paper→live drift | **CONFIRMED LIVE** (가설 아님). 단 drift의 *존재*만 확인 — *크기*(실현 fragmentation·체결 divergence)는 별도 실측 필요 | FSC best-execution 기준, NXT 체결·수수료, 실현 fill 데이터 | **Critical** | SOR fragmentation·분기 venue 구성을 백테스트 실행조건으로 모델링 |
| 7 | PIT 멤버십/생존편향프리/CA/상폐/공시일 = blocking | **CONFIRMED**. US는 CRSP 멤버십 이력으로 PIT 재구성 *가능*(벤더 구독 조건). 단 **상폐수익률(returns)** clean solution은 미확정(DelRet=clean = REFUTED). KR 대응 mechanism 미확인 | CRSP 멤버십/이력 item spec, 상폐수익률 벤더 item, KR 동등물 | **Critical** | 생존편향프리+상폐보정 데이터를 알파연구 전 선결로 잠금 |
| 8 | US Phase1 = S&P500/Russell/벤더 broad (미잠금) | Russell breadth는 **동적**(분기 IPO/float·2026 반기전환), 결정론적 rank-cut은 **REFUTED**. CRSP는 고정 N 없음. "broad"는 단일 컷 아님 | S&P US methodology(이번 소스 unreliable/404), Russell·CRSP live edition | High | US 유니버스는 자체 유동성 필터 명시 + 레짐-aware PIT |

---

## 3. Benchmark Mismatch Audit

> **소스 상태 주의:** KR 인덱스(KRX300/KOSPI200/KOSDAQ150) methodology는 이번 라운드 1차 소스 확보 **실패**(KRX 공식 사이트가 unreliable/0-claim 반환, 보조 소스만). 아래 KR 행은 **검증 미완 — Missing Source(§8)로 이월**. US 행(Russell/CRSP)은 primary 소스로 검증.

| Benchmark | What it represents | Main mismatch risk | Data/methodology gap | Recommended treatment |
|---|---|---|---|---|
| KRX300 TR | KRX 통합 300종목 TR | TR 산식·리밸런스 미검증; 섹터/대형주 집중 | **KRX300 TR methodology 원문 미확보** | primary 후보로 유지하되 methodology 확보 전 잠금 금지 |
| KOSPI200 | 유가 200 대형주 | 대형주 편중, KOSDAQ 미포함 | 구성/재조정 규정 미확보 | universe와 벤치 정합성 별도 확인 |
| KOSDAQ150 | 코스닥 150 | 고변동·유동성 이질 | methodology 미확보 | KOSPI200과 합성 시 가중·리밸런스 정의 필요 |
| KOSPI / KOSDAQ | 전시장 시총지수 | 광의·비투자가능 종목 포함 | — | 벤치보다 시장맥락용 |
| custom cap-weight TR | 자체 대조 벤치 | 배당재투자·CA·생존편향 처리 부채 상속 | 데이터 계약 종속 | Layer 0 통과 후에만 |
| **S&P 500** | 대형주 위원회 선정 | 위원회 재량·추가/삭제 timing | **이번 S&P methodology 소스 unreliable(0-claim)** | S&P DJI live methodology 재확보 |
| **Russell 1000** | 대형주 룰베이스 | **2026-12 반기전환**·분기 IPO/float로 멤버십 동적 | LSEG primary 확보됨 | **레짐-aware PIT**(연-6월 ↔ 6+12월) |
| **Russell 3000** | broad 룰베이스 | 결정론적 rank-cut **REFUTED**; micro 포함 여부·$1 스크린 주장 refute | breadth 동적 | 자체 유동성 필터 필수 |
| **CRSP broad** | breakpoint/packeting | **고정 N 없음**·packet 50% 부분이동·분기 5일 transition | CRSP primary 확보됨 | banded·partial 멤버십을 분기 캘린더로 재현 |

---

## 4. Universe Feasibility Audit

| Universe | Breadth | Liquidity | PIT feasibility | Survivorship risk | Cross-sectional 적합 | Failure mode | Recommended treatment |
|---|---|---|---|---|---|---|---|
| KOSPI100 | 좁음 | 높음 | **미검증(KR)** | 중 | 낮음(breadth 부족) | 종목수 부족으로 신호 분산↓ | KR PIT 벤더 확보 후 평가 |
| KOSPI200 | 중 | 높음 | **미검증(KR)** | 중 | 중 | 대형주 편중 | 멤버십 이력 확보 선결 |
| **KOSPI200+KOSDAQ150** (v2 후보) | 중+ | 혼합(코스닥 이질) | **미검증(KR)** | 중–고(코스닥 상폐) | 중–상 | 코스닥 저유동·상폐 미보정 시 편향 | 유동성 decile 자체산출 + PIT 멤버십 DB(선결) |
| KRX300 universe | 중+ | 높음 | **미검증(KR)** | 중 | 중–상 | methodology 미확보 | KRX300 구성규정 확보 후 |
| US S&P500 | 좁음 | 매우 높음 | 가능(위원회 timing 주의) | 낮음 | 중 | 위원회 재량 timing 누수 | 추가/삭제 effective date 정밀화 |
| US Russell 1000/3000 | 중–광 | 혼합 | 가능, **레짐-aware 필수** | 중(3000 micro) | 상(breadth) | 연1회 스냅샷 사용 시 오기재 | 분기+2026반기 재구성, 자체 유동성 필터 |
| US 벤더 broad(CRSP) | 광·동적 | 혼합 | 가능(멤버십 이력) | 중–고 | 상 | 고정컷 가정 시 paper→live drift | banded 분기 transition 재현 |

---

## 5. Cost / Tax / Slippage Risk Audit

> **KR 행 = 전부 "official source needed", 미검증.** US 행만 primary 검증.

| Cost item | KR/US | Why it matters | Official source needed | Backtest modeling implication | Sensitivity test |
|---|---|---|---|---|---|
| 증권거래세(단계율) | KR | 지배 비용 후보, 2025–26 단계적 변경 | **증권거래세법/기재부 고시(미검증)** | flat 금지, 시점별 세율 | 세율 시나리오 ±, break-point |
| 위탁수수료 | KR | 분기 NXT/KRX 차등 가능 | **NXT·KRX·브로커 수수료표(미검증)** | venue별 수수료 분리 | venue mix 민감도 |
| FX 변환비용 | KR(US거래시) | KRW↔USD 왕복 | **브로커 FX 스프레드(미검증)** | 환전비 별도 항 | FX 비용 ± |
| 배당원천세 | KR/US | TR·net 수익에 직접 | **한국 세법/조세조약(미검증)** | TR에 net 배당 | 원천율 시나리오 |
| 호가 스프레드 | KR/US | 실현비용 핵심 | KRX/거래소 틱·스프레드 | 스프레드 기반은 **과소추정**(검증됨) | all-in vs 스프레드 비교 |
| 슬리피지 | KR/US | 체결 drift | 실현 fill 데이터 | 도착가 대비 모델 | 보수/공격 시나리오 |
| 시장 임팩트 | KR/US | **규모와 함께 악화**(검증됨) | 임팩트 모델 문헌 | 규모-민감 함수 | AUM 스케일링 |
| SEC fee | US | 매도 수수료 | SEC fee schedule | 매도측 bps | — |
| 차입(borrow) | US | 롱숏 단계 | 브로커 borrow rate | 숏 비용 | borrow ± |

**검증된 비용 원칙(US 근거, 방향만):** ① 비용은 수익성 + **통계 유의성** 동시 감소(데이터스누핑 우려↑) — Novy-Marx & Velikov (2016, RFS). ② all-in > 스프레드 기반, **규모와 함께 과소추정 악화** — Patton & Weller (2020, JFE, 2-1 directional). ③ net 생존은 **cost-mitigation 설계 조건부**(banding/buy-hold spread) → flat-bps 위험. **인용 금지(REFUTED):** 50% 턴오버 컷, 모멘텀 7.2–7.6%, 밸류 2.6–4.1%.

---

## 6. Data Feasibility Blocking Register

| Data requirement | KR issue | US issue | Blocking severity | Vendor 필요? | How to test availability | 알파연구 전 필수? |
|---|---|---|---|---|---|---|
| PIT 인덱스 멤버십 | **KR 벤더 capability 미확인** | CRSP MbrStartDt/MbrEndDt(PERMNO/INDNO)로 가능, 단 non-trading-day·cross-year edge | **Critical** | KR=Yes(미확인), US=Yes(CRSP) | 과거 일자 멤버십 쿼리 → 재조정일 경계 확인 | **Yes** |
| 생존편향프리 가격 | KR 동등물 미확인 | 가능 | **Critical** | Yes | 상폐종목 가격이력 존재 여부 | **Yes** |
| Corporate actions | KR 정합 미검증 | 표준 | High | Yes | 분할/배당/권리락 누적 일치 테스트 | **Yes** |
| **상폐수익률(returns)** | KR mechanism 미확인 | **DelRet=clean = REFUTED** → addressable item 미확정 = **OPEN** | **Critical** | Yes | 성과상폐 코드의 최종수익률 존재율 측정 | **Yes** |
| 공시/effective date | KR 미검증 | Russell/CRSP 분기 effective date 명시 | High | 일부 | announce vs effective 분리 확인 | **Yes** |
| **NXT 동적 구성** | 분기 재선정(분기말 5거래일 전 공지, 익분기 첫날 발효), 10→800→steady-state>800 | N/A | **Critical(KR)** | Yes(FSC/NXT) | 분기별 거래가능 종목 이력 재구성 | **Yes** |

핵심: **US PIT 멤버십 재구성은 가능(벤더 구독 전제)하나, 상폐 RETURNS의 깨끗한 단일 벤더 item은 미확정(OPEN).** KR은 멤버십·생존편향·상폐 전부 벤더 capability **미검증**.

---

## 7. KR-first vs US-first vs Parallel Audit

Score 1–5 (5=best). KR 데이터/벤치 1차 소스가 이번 라운드 미확보 → KR 칸은 "현재 *검증된* 명료도" 기준(낮음 = 증거부족이지 시장결함 아님).

| 축 | KR-first | US-first | Parallel |
|---|---|---|---|
| benchmark clarity | 2 (KRX300 TR methodology 미확보) | 4 (Russell/CRSP primary 검증) | 2 |
| universe breadth | 3 | 4 | 4 |
| data availability | 2 (KR 벤더 미확인) | 4 (CRSP) | 2 |
| PIT feasibility | 2 (미검증) | 4 (멤버십 이력) | 2 |
| cost/tax clarity | 1 (**KR 비용 전부 미검증**) | 3 (방향만, KR 세금 무관) | 1 |
| execution simplicity | 2 (**NXT/SOR 2-venue·분기 재구성**) | 4 (성숙·단일 SIP 환경) | 2 |
| relevance to user | 5 (KRW 자본·솔로 관련성 최고) | 2 | 4 |
| risk of false conclusion | 2 (증거 US-중심이라 KR 검증탑 = theater 위험) | 4 | 2 |

**Auditor recommendation: KR-first 조건부 + KR cost/data lock은 HOLD.** 근거: relevance는 KR-first가 압도적이나, *검증된 data-feasibility 증거 기반이 US-중심*이라 지금 KR을 잠그면 "비PIT/생존편향 데이터 위 검증탑 = theater"(v2 리스크 #1) 위험이 가장 큼. → **순서:** ① KR PIT/생존편향/상폐/비용 벤더 capability를 KRX/FSC/벤더 1차 소스로 검증(= v2 stage0b 선결과 일치) → ② 그 후 KR-first 잠금. US는 데이터 측면이 더 잘 입증돼 있으나 user relevance가 낮음 → KR-first 의도는 유지하되 **데이터 게이트를 먼저 통과**. (이는 전략 추천이 아니라 lock 순서 권고.)

---

## 8. Missing Official Source List (DR-1 잠금 전 필수 확인)

**KR (이번 라운드 미확보 — 최우선):**
1. KRX300 / KOSPI200 / KOSDAQ150 index methodology 원문 (구성·재조정·TR 산식)
2. KRX 유가증권/코스닥 시장 업무규정 (기준가·틱·거래)
3. 증권거래세법 + 기재부 단계적 세율 고시 (2025–2026)
4. NXT(Nextrade) 거래수수료표 + 현재 거래가능 종목 수/이력
5. KRX 위탁·거래소 수수료, FSC best-execution 기준 원문
6. 한국 배당 원천징수율 + 조세조약 (US 거래 시)
7. KR 생존편향프리/PIT/CA 벤더(FnGuide 등) 데이터 spec 실측

**US (보강):**
8. S&P US Indices methodology live edition (이번 소스 unreliable/404)
9. CRSP live edition (인용 URL이 2026-04판으로 redirect — live 인용)
10. 상폐 RETURNS을 실제 제공하는 addressable 벤더 item 확정 (DelRet=clean 반증됨)
11. NYSE/NASDAQ 거래 캘린더·수수료, SEC fee schedule

---

## 9. Required Patches Before DR-1 Lock

1. **KR 2-venue 실행 모델링:** KRX+NXT SOR fragmentation + 분기 venue 구성(분기말 5거래일 전 공지/익분기 첫날 발효)을 백테스트 실행조건으로. drift 존재가 아니라 *크기* 실측.
2. **레짐-aware US PIT 멤버십:** Russell 연-6월(≤2026-06) ↔ 6+12월(2026-12부터, partial·size vs style 차등) + 분기 IPO/float; CRSP 분기 5일 transition·packeting. 연1회 스냅샷 금지.
3. **생존편향프리+상폐보정 데이터 선결:** 알파 연구 *전*. 상폐수익률 보정(가중·cumulation 방식 의존, ~-30%/최대-100%; NASDAQ -55% 참고). US 상폐 RETURNS의 addressable 벤더 item 먼저 확정(OPEN).
4. **비용 모델 교체:** flat-bps/스프레드-only → turnover-aware + cost-mitigation 로직 + scale-sensitive. 유의성까지 net 검정.
5. **KR 비용 1차 소스 확보 (게이팅):** 증권거래세 단계율·NXT/KRX 수수료·FX·배당세를 KRX/FSC/세법 원문으로. **이게 KR cost-lock의 단일 최대 의존성.**
6. **KR 인덱스/유니버스 methodology 확보:** KRX300 TR·KOSPI200·KOSDAQ150 구성·재조정·TR 산식 (이번 라운드 미확보).
7. **자체 유동성 필터 명시:** Russell/CRSP eligibility는 투자가능 breadth를 과대표현 → 자체 ADV/유동성 컷 별도 정당화.
8. **refuted 수치 폐기:** 50% 턴오버 컷·모멘텀 7.2–7.6%·밸류 2.6–4.1%·Russell 결정론 rank-cut·$1 스크린·CRSP DelRet=clean 인용 금지.

---

## 10. One-page DR-1 Lock Template (Primary 도착 후 채움)

```
DR-1 LOCK SHEET v0.1                                    날짜: ____  소스버전: ____
─────────────────────────────────────────────────────────────────────
A. BENCHMARK
   KR primary  : ______________  [methodology 원문 확인? Y/N]  근거URL: ____
   KR secondary: ______________  [TR/CA/배당재투자 처리 정의? Y/N]
   US primary  : ______________  [레짐-aware PIT 코딩? Y/N]
B. UNIVERSE
   KR Phase1   : ______________  [PIT 멤버십 이력 확보? Y/N] [유동성필터 정의? ____]
   US Phase1   : ______________  [자체 유동성필터? ____] [분기/반기 재구성? Y/N]
C. COST/TAX  (KR = 1차 소스 확인 필수)
   KR 거래세 단계율: ____  근거: ____   위탁수수료(NXT/KRX): ____
   FX: ____  배당세: ____  스프레드/슬리피지/임팩트 모델: ____
   US: SEC fee ____  borrow ____   비용모델 = turnover-aware? Y/N  scale-sensitive? Y/N
D. DATA FEASIBILITY
   PIT 멤버십(KR/US): ____ / ____   생존편향프리: ____   상폐수익률 item: ____
   CA: ____   NXT 동적구성 모델: ____   벤더: ____
E. MARKET SLEEVE 결정: [ ] KR-first  [ ] US-first  [ ] parallel  [ ] hold
   조건/게이트: ________________________________________________
F. OPEN (lock 못 한 항목): ____________________________________
─────────────────────────────────────────────────────────────────────
검증상태: Primary(ChatGPT) ☐ 저장  Red-team(Claude) ☑ 저장  Merge ☐ 완료
```

---

## Open Questions (머지 시 Primary와 대조)

1. **KR 비용 스택 미검증:** 증권거래세 단계율(2025–26)·NXT vs KRX 수수료·FX·배당세·실현 스프레드/슬리피지 — KRX/FSC/세법 1차 소스 필요. KR cost-lock 게이팅.
2. **생존편향프리 RETURNS:** US에서 DelRet=clean이 반증됨 → addressable 벤더 item 무엇? KR 동등물 존재하나(생존편향프리+상폐보정+PIT 멤버십)?
3. **KRX↔NXT fragmentation의 *실현 크기*:** 존재는 확인, 크기는 별도 실측(paper→live drift 정량).
4. **KR-first 우위 재검토:** 검증된 PIT/생존편향 툴링이 US/CRSP-중심인데 KR 동등 벤더 capability가 실재하는가 — 이 증거기반이 KR-first vs US-first 결정을 기울이는가.

## 검증 원장 (Verification Ledger)

- **CONFIRMED (3-0):** NXT 2025-03-04 launch / SOR 의무 / KR 2-venue 전환 / 유동성분산 공식예상; NXT 분기 재선정; Russell 2026-12 반기전환; Russell 분기 IPO/float; CRSP 고정N 없음·breakpoint·packeting·분기 transition; CRSP 멤버십 이력(MbrStartDt/EndDt); 상폐수익률 ~-30%·소형/저가/동일가중/CAR 집중; 비용이 수익성+유의성 동시감소·cost-mitigation 조건부.
- **CONFIRMED (2-1, directional):** all-in > 스프레드·규모와 악화 (Patton-Weller; Frazzini-Israel-Moskowitz 반론 존재 → 방향만).
- **REFUTED (인용 금지):** Russell 결정론적 rank-cut(0-3); Russell $1 가격스크린 약함 주장(1-2); CRSP DelRet=clean solution(1-2); CRSP 상폐 다수 누락 통계(1-2); 50% 턴오버 컷(0-3); 모멘텀 7.2–7.6%(0-3); 밸류 2.6–4.1%(0-3).

### Sources (primary 위주)
- FSC: pr010101/83967 (NXT 승인·SOR·분기재선정), po110101/82796 (2-venue 전환·유동성분산), pr010101/82268
- FTSE Russell/LSEG: russell-us-indexes-construction-and-methodology.pdf; russell-us-indexes-move-to-semi-annual-reconstitution.pdf (2026-12 반기); IPO fast-entry
- CRSP: Market Indexes Methodology Guide; US Stock & Indexes DB Guide Flat File 2.0
- Shumway (1997) Journal of Finance 52(1):327-340 (상폐편향); Shumway-Warther (1999, NASDAQ -55%)
- Novy-Marx & Velikov (2016) RFS 29(1) / NBER WP20721 (비용 taxonomy); Patton & Weller (2020) JFE (WYSINWYG)
- 미확보/약함: KRX 인덱스 methodology(unreliable), S&P US methodology(unreliable/404), 한국 세법(2차 소스만)

> **stats:** 5 angles · 23 sources · 85 claims · 25 verified · 18 confirmed / 7 killed · 9 synthesized · 105 agent calls.
