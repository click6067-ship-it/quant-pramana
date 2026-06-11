# 07 · DR-1A Claude Code Red-team Audit (KR Official Source Gap Lock)

> **Provenance:** Claude Code `deep-research` harness, 2026-06-07. Target = `06_dr1a_chatgpt_kr_gap_primary.md` (ChatGPT DR-1A). 5 angles → 23 sources → 86 claims → **25 verified by 3-vote adversarial verification → 22 confirmed / 3 killed** → 10 synthesized findings. Primary tilt: KRX TR 방법론, 국가법령정보센터 거래세법 개정연혁, NXT 공식 수수료, OpenDART/FSS.
> **역할:** 새 primary 아님. ChatGPT DR-1A 적대 감사. 입력=`00`·`04`·`06`(`03`은 비어있음 — 풀 DR-1 Primary 미실행, 좁은 KR-gap 패스로 직행).
>
> ## 🔥 한 줄 결론 — ChatGPT DR-1A는 **뒤집혔다**
> ChatGPT가 KR을 "아직 못 잠금"이라며 든 **가장 무거운 두 근거(KRX300 TR·거래세)가 진짜 부재가 아니라 ChatGPT 검색 실패(false-negative)**다. 공식 소스는 실재하고 찾을 수 있다. 그 false-negative 위에 세운 **"KR이 막혔으니 US-first로 가라" 권고는 ① scope creep(DR-1A 범위는 KR 소스잠금이지 시장순서 재결정 아님) ② absence-of-evidence 오류 ③ v2 KR-first LOCK 위반**이라 **기각**. 실제로 KR은 DR-1A 결론보다 **훨씬 준비돼 있고**, 7개 항목이 ChatGPT 등급보다 상향된다.

---

## 1. Verdict — **PATCH-BEFORE-LOCK** (+ "US-first 권고"는 REJECT)

- **KRX300 TR "Do-not-lock" = FALSE-NEGATIVE.** 공식 KRX 총수익지수로 실재(기준일 2011-01-03·산출개시 2018-12-24·기준 1,216·2초). KRX가 TR/NTR을 *별도 문서*로 분리하는 구조를 ChatGPT가 "부재"로 오독.
- **거래세 "못 잠금" = FALSE-NEGATIVE.** 국가법령정보센터 개정연혁(제31290→33209→35359→36001)으로 연도·시장별 단계 세율 완전 잠금 가능.
- **NXT/SOR "Lock now" = 정확.** 5개+ 브로커 최선집행 문서로 과검증. ChatGPT가 유일하게 제대로 잠근 항목 — 메커니즘 잠금 OK, 고객 수수료 pass-through만 broker-confirm으로 남긴 것도 옳음.
- **KR 펀더멘털 "유료벤더 필요" = 과장.** OpenDART(FSS 무료 API)가 2015년+ 기계판독 전체 재무제표 제공 → "FnGuide 필수"는 거짓, FnGuide는 *편의*지 필수 아님.
- **"Proceed US-first" = REJECT.** 검색실패에서 합리화한 scope creep. KR이 더 준비됐음이 드러나 피벗 전제가 붕괴. → **KR DR-2(또는 split)로 진행, KR-first 시퀀싱 유지.**

---

## 2. Source Grounding Check

**사용 파일:** `00_control_sheet.md`, `04_dr1_claude_audit.md`, `06_dr1a_chatgpt_kr_gap_primary.md` (+ `03`은 비어있어 미사용).

**판정: ChatGPT DR-1A는 소스를 올바르게 *명명*했으나 *소진(exhaust)하지 못했다.*** 자기가 이름 댄 바로 그 포털에서 한두 클릭 깊이의 항목을 "Unknown"으로 처리했다. 패턴이 체계적이다:
- 지수 *포털*은 찾았으나 그 안의 *TR 시리즈*는 못 찾음.
- 거래세 *시행령*은 찾았으나 *세율 개정연혁 체인*은 못 찾음.
- *DART*는 찾았으나 유료벤더로 디폴트.

→ 이것은 **공식 소스 부재가 아니라 under-exhaustion** = "absence of evidence를 evidence of absence로" 쓴 실패 모드. (내가 독립 확인: KRX 주가지수 공지 board `boardId=MDCINFO005`·개별지수 구성종목/PER/PBR 페이지·KRX OpenAPI(2010~)·Global KRX Index Methodology 다운로드 섹션·거래세법 개정연혁 `lsId=005028`·OpenDART 전체재무제표 API `DS003/2019020` 전부 도달 가능.)

---

## 3. Overconfident / Under-sourced Lock Audit

| ChatGPT DR-1A claim | 왜 false-negative/과신인가 | Evidence gap 진짜? | Severity | Required patch |
|---|---|---|---|---|
| "KRX300 TR 공식 페이지/방법론 없음 → Do-not-lock" | KRX 「총수익지수 방법론」 별도문서 p9 'TR 산출현황'에 KRX300 TR 명시. price 방법론에 TR 키워드 0인 건 *구조적 분리* 탓 | ❌ 가짜 (실재) | **Critical** | krx.co.kr 직접서 방법론·시리즈 재취득 후 **Lock 승격** |
| "거래세 시장별 분해 못 잠금 → Provisional" | 개정연혁 체인으로 연도·시장 단계세율 확정 가능 | ❌ 가짜 (법령 공개) | **High** | 개정연혁서 2024/25/26 세율 확정 후 **Lock** |
| "KR PIT 펀더멘털 유료벤더(FnGuide) 필요 → Do-not-lock" | OpenDART 무료 전체재무제표(2015+) 존재 | △ 부분 (2015+ as-reported는 무료, *정제 PIT 패널*만 self-build) | High | "do-not-lock"→Provisional, OpenDART floor 명시 |
| "filing/earnings dates 벤더 필요" | DART/OpenDART 공시·접수일 무료 | ❌ 가짜 (무료) | Medium | Provisional로 하향, event file 품질만 확인 |
| "self-built cap-weight TR이 주 내부경로" | 공식 KOSPI200 TR/NTR·KOSDAQ150 TR 실재 → 자체구축 불필요 | ❌ 프레이밍 오류 | Medium | self-built TR = optional fallback로 강등 |
| "NXT venue fee Unknown" | NXT 공식 수수료표 공개(maker 0.00134%/taker 0.00182%) | ❌ 가짜 (venue 수수료 공개) | Medium | venue 수수료 Lock, *고객 pass-through만* broker-confirm |
| "NXT/SOR Lock now" | (정확) | — | — | 유지 (메커니즘 잠금 옳음) |

---

## 4. KR Benchmark Audit

| Item | ChatGPT treatment | 내 수정 treatment (독립 확인) | Evidence gap | Decision |
|---|---|---|---|---|
| KRX300 | Provisional/Medium | 공식 cross-market 300지수·ETF 투자가능 확인 | 최신판 방법론(2020.05 이후) 확인 | **Lock** |
| **KRX300 TR** | **Do-not-lock/Low** | **실재** — 기준 2011-01-03·산출 2018-12-24·기준값 1,216·2초, 「총수익지수 방법론」 p9. 라이브 심볼 KRX300TR | 무료 시리즈 *히스토리* 다운로드 경로 미확인 | **Lock** (←대폭 상향) |
| KOSPI200 | sole 벤치로 Reject | 지수+**TR/NTR 실재**(TR/NTR 기준 273.81·산출 2016-01-11). sleeve로 적합 | PIT 구성종목 무료경로 | **Lock**(지수+TR) / 구성종목 Provisional |
| KOSDAQ150 | sole 벤치로 Reject | 지수+**TR 실재**(기준값 1,014) | 동일 | **Lock**(지수+TR) / 구성종목 Provisional |
| self-built cap-weight TR | Provisional(내부 fallback) | 공식 TR 시리즈가 있으므로 **불필요** | — | **Optional fallback only** (강등) |

핵심: **외부 KR 벤치 후보들은 PR뿐 아니라 공식 TR/NTR 시리즈가 전부 존재한다.** ETF(RISE 200TR·KODEX/RISE KOSDAQ150 TR 등)가 이 공식지수를 추종 = 비존재 지수는 추종 불가. 단 **TR *시리즈 존재* ≠ 무료 PIT *구성종목 멤버십*** — 후자는 별개 항목(§7).

---

## 5. KR Cost / Tax Audit

| Cost item | ChatGPT treatment | Missing official evidence | Broker-specific? | Backtest impact | Required patch |
|---|---|---|---|---|---|
| **증권거래세(단계)** | Provisional(못 잠금) | **없음 — 개정연혁으로 확정** | No(법령) | **시변(時變) 세율 필수** | 아래 확정 스케줄 Lock |
| 브로커 수수료 | Requires confirmation | 약정/기본수수료표 | **Yes** | 단일상수 금지 | 대상 브로커 수수료표 확보 |
| KRX/NXT venue 수수료 | Unknown | **venue 수수료는 공개**(아래) | pass-through만 Yes | venue별 분리 | 고객 pass-through만 broker-confirm |
| 배당원천세 | Unknown | **없음 — 14%+1.4%=15.4%(거주자)** | 투자자별 | net 배당 | 15.4% Lock(거주자), 조약/외국인 별도 |
| FX | Requires confirmation | 은행별 스프레드 | Yes | KRW 기능통화 아니면 별도항 | broker FX 확인 |
| 스프레드 | Provisional | 고정값 없음 | No | bucketed half-spread | 경험적 추정 |
| 슬리피지 | Do-not-lock | 고정값 없음 | No | empirical | **(ChatGPT 정확)** |
| 시장임팩트 | Do-not-lock | 공식수치 없음 | No | 규모-민감 모델 | **(ChatGPT 정확)** |

**확정된 거래세 스케줄 (매도측, 개정연혁 제31290→33209→35359→36001):**

| 연도 | KOSPI 합계 | (증권거래세 + 농어촌특별세) | KOSDAQ | KONEX | 장외/K-OTC |
|---|---|---|---|---|---|
| 2024 | **0.15%** | 0.00% + 0.15% | 0.18% | — | — |
| 2025 | **0.15%** | 0.00% + 0.15% | 0.15% | — | — |
| 2026~ (제36001, 시행 2026-01-01) | **0.20%** | 0.05% + 0.15% | **0.20%** | 0.10% | 0.20% |

- **농어촌특별세 0.15%는 KOSPI에만** 부과(KOSDAQ엔 없음). 2026 KOSPI 0.20%는 금투세 폐지 후 세율조정 결과.
- **백테스트 함의:** 세율이 *시변*이다. 2024–2025 KOSPI는 0.15%, 2026+ 0.20% → flat 0.20% 가정은 과거구간 과대계상. (프로젝트 메모의 "2026 0.20%"는 *2026 KOSPI* 기준으로 맞음.)
- ⚠️ **caveat:** 2024/2025 *연도별 세부*는 검증서 split(2개 tax claim refuted) — 위 스케줄은 종합·교차확인본이나, 백테스트 비용 잠금 전 개정연혁 원문서 2024/2025 KOSPI/KOSDAQ 수치 재확인 권장.

---

## 6. NXT / ATS / SOR Audit

| Issue | ChatGPT treatment | 틀렸거나 불완전한 점 | 필요 공식/브로커 증거 | paper→live drift risk | Required patch |
|---|---|---|---|---|---|
| 2-venue 체제(2025-03-04~) | Lock now | (정확·과검증) | 브로커 약관 | regime flag 필요 | 유지 |
| NXT 수수료 구조 | "Unknown" | **공개됨** — maker 0.00134%·taker 0.00182%·단일가 0.00158%(maker-taker), KRX flat ~0.0023% 대비 maker ~42%↓ | NXT charge-info(공식) | venue별 비용차 | venue 수수료 Lock |
| SOR 라우팅 | Lock now | (정확) Taker 분할/Maker 미분할, 통합호가·비용·체결가능성 | 브로커 최선집행 | child-order 추적 | 유지 |
| SOR opt-out/직접선택 | Lock now | (정확) 90일 갱신 opt-out, 부동의시 KRX 처리 | KIS/NH 문서 | 계정 default 확인 | 유지 |
| SOR 윈도/세션 | (부분) | 09:00:30–15:20:00 SOR 윈도, NXT 잔량 after-market 유지 | 브로커 문서 | **close/carryover/cancel = drift 핵심** | venue별 세션 로직 |
| 고객 fee pass-through | Requires confirm | (정확) 최선집행 문서는 수치 0 공개, "기본수수료 기준"·"실제 비용과 차이" | 대상 브로커 수수료표 | 비용 calibration | **유일한 진짜 미해결 비용항** |
| venue-tagged fill log | inference | 추론 정당 | 브로커 export에 venue tag/child ID/timestamp 有無 | reconcile 실패 | broker export 실측 |

**판정: ChatGPT의 "Lock now"는 *메커니즘 수준에서 정확하고 over-lock 아님*.** 메커니즘(2-venue·SOR·분할·opt-out)을 잠그고 고객 수수료 pass-through만 broker-confirm으로 남긴 분리가 옳다. drift risk는 *메커니즘은 잠겼고, 실현 fill/split 행동 + 정확 pass-through 수수료*만 라이브 전 calibration 필요.

---

## 7. KR Data Feasibility Audit

| Data requirement | ChatGPT treatment | 아직 unknown인 것 | Blocking severity | DR-2 진행 가능? | Required patch |
|---|---|---|---|---|---|
| PIT 구성종목 | Provisional(자동화 미검증) | 무료 *end-to-end* 다운로드 경로 | High | **Yes**(floor 존재) | KRX 구성종목+주가지수 공지 archive+pykrx로 self-assembly 실증 |
| Corporate actions | Provisional | 정규화 워크플로 | High | Yes | SEIBro 권리/배당 + KIND 정규화 |
| 배당 | Provisional | — | Medium | Yes | SEIBro 무료 floor |
| 상폐/생존편향 | Provisional | 상폐 *이후* 시세 아카이브 | High | Yes(이벤트는 무료) | KIND 상폐현황 무료, post-delist self-build |
| **PIT 펀더멘털** | **Do-not-lock(유료벤더)** | 정제 PIT 패널·2015 이전 | High | **Yes** | OpenDART(무료·2015+·BS/IS/CIS/CF/SCE·OFS/CFS) floor 명시, FnGuide=편의 |
| filing/earnings dates | Requires vendor | event file 품질 | Medium | Yes | DART/OpenDART 무료, 필드매핑만 |
| 거래일정/정지 | (대체로 OK) | per-security 정합 | Low | Yes | KRX 캘린더 |

**핵심:** ChatGPT가 KR 데이터를 과소평가했다. **무료 공식 floor가 실재**한다 — OpenDART(FSS 운영, 누구나 무료, 2015년+ 기계판독 전체 재무제표), KIND(상폐/신규상장), SEIBro(배당/권리), KRX(구성종목/공지/OHLCV). **유료 FnGuide가 진짜 불가피한 구간은 ① 2015 이전 깊이 ② 사전정제 PIT 패널뿐** — 편의지 필수 아님. 진짜 self-build 작업은 *정제·PIT 정렬·생존편향 처리*(데이터 *입수*가 아니라 *조립*).

---

## 8. Lock Decision Reconciliation

| Item | ChatGPT | **내 최종 권고** | 이동 |
|---|---|---|---|
| KRX300 | Provisional | **Lock** | ↑ |
| KRX300 TR | Do-not-lock | **Lock** | ↑↑ |
| KOSPI200+KOSDAQ150 | Provisional | **Lock**(지수+TR) / 구성종목 Provisional | ↑ |
| self-built cap-weight TR | Provisional | **Optional fallback only** | ↓(불필요) |
| KR 거래세 | Provisional | **Lock**(시변 스케줄) | ↑ |
| 브로커 수수료 | Requires confirm | **Requires broker confirm** | = (정확) |
| NXT/SOR 실행모델 | Lock now | **Lock**(메커니즘) | = (정확) |
| KR PIT 구성종목 | Provisional | **Provisional**(무료 floor·self-assembly) | = |
| KR corporate actions | Provisional | **Provisional→leaning Lock** | ↑ |
| KR 상폐/생존편향 | Provisional | **Provisional**(이벤트 무료·post-delist self-build) | = |
| KR PIT 펀더멘털 | Do-not-lock | **Provisional**(OpenDART 무료 2015+) | ↑ |
| filing/earnings dates | Requires vendor | **Provisional**(DART 무료) | ↑ |

**순효과: 7개 항목이 상향**(KRX300 TR·거래세·펀더멘털·filing·CA·KOSPI200/KOSDAQ150 TR·KRX300). 진짜 잔여 갭은 **브로커 수수료 + 고객 fee pass-through + 스프레드/슬리피지/임팩트** 셋뿐 — **어느 것도 KR-first를 버릴 KR-고유 blocker가 아니다.**

---

## 9. Required Patches Before Final DR-1 Lock Sheet

1. **KRX300 TR Lock 승격** — `data.krx.co.kr`/`eindex.krx.co.kr`/Global KRX Index Methodology 섹션서 「총수익지수 방법론」 *직접* 재취득(현재 근거는 브로커 미러 fdata.kbsec/samsungpop — verbatim·교차확인됐으나 최종잠금엔 원본). 최신판(2020.05 이후) 확인.
2. **거래세 시변 스케줄 Lock** — 개정연혁(lsId=005028) 원문서 2024(KOSPI 0.15·KOSDAQ 0.18)·2025(0.15·0.15)·2026(0.20·0.20·KONEX 0.10) 재확인 후 백테스트 비용엔진에 *연도·시장별* 세율 주입. 농특세 KOSPI-only.
3. **NXT venue 수수료 Lock** — maker 0.00134/taker 0.00182/단일가 0.00158 (post-promo 표준; 2025-03~04 프로모 면제는 과거). 고객 pass-through만 broker-confirm 잔류.
4. **OpenDART floor 채택** — KR 펀더멘털을 "유료벤더 필요"에서 "무료 as-reported 2015+ + self-build PIT 정제"로 재기술. FnGuide는 2015 이전·사전정제 패널 한정 옵션.
5. **무료 PIT 구성종목 end-to-end 실증** — KRX 구성종목+주가지수 공지 archive+pykrx로 KOSPI200/KOSDAQ150/KRX300 일자별 멤버십 재구성을 *실제로 한 번 뽑아* floor 확정(DR-2 첫 작업).
6. **배당원천세 15.4%(거주자) Lock** — 조약/외국인·2025 고배당 분리과세는 별도.
7. **잔여 broker/empirical 항목 병렬 처리** — 브로커 수수료표·fill log venue tag·스프레드/슬리피지/임팩트는 KR-first를 막지 않는 병렬 트랙.
8. **refuted 항목 폐기** — Global KRX "Factsheet/Constituents 전용섹션" 주장(1-2)·거래세 연도별 세부 2건(0-3/1-2)은 §refuted 참조, 본 문서 확정 스케줄로 대체.

---

## 10. Recommendation — **Proceed to KR DR-2** (또는 split US/KR). "US-first" REJECT.

ChatGPT의 US-first 피벗을 기각하는 이유:
- **(a) Scope creep** — DR-1A 정의 범위는 *KR 공식소스 갭 잠금*이지 시장순서 재결정이 아니다. KR-소스-갭 감사가 전략적 시장 재배열을 결론낼 수 없다.
- **(b) v2 LOCK 위반** — KR-first는 relevance(KRW 자본·솔로)로 이미 잠긴 frame.
- **(c) absence-of-evidence 오류** — US-first 정당화에 쓴 KR "갭"(KRX300 TR·거래세·펀더멘털)이 전부 ChatGPT *검색 실패*. "KR 안 됐으니 US"는 검색한계의 합리화.
- **(d) 자기모순** — US도 prior DR-1(`04`)의 미해결 항목(Russell 2026-12 반기전환·CRSP packeting·생존편향프리 RETURNS 벤더 OPEN)을 KR만큼 안고 있다. ※ US 항목은 `04`·프로젝트 맥락서 인용(이 KR-범위 감사서 재검증 안 함) — 자기모순 비판은 ChatGPT 자신의 prior 자백에 근거.

KR이 DR-1A 결론보다 *훨씬* 준비됐음이 1차소스로 드러난 이상 피벗 전제는 붕괴. **DR-2 = KR(또는 split)로 진행, 잔여 broker/empirical 항목은 병렬 패치.**

---

## Open Questions (머지 시 대조)
1. KOSPI200/KOSDAQ150/KRX300 **무료 PIT 구성종목 end-to-end** 경로가 실제로 완결되나(KRX+공지 archive+pykrx) — floor는 확립, 전구간 다운로드는 미실행.
2. KRX300 TR **연속 시리즈 히스토리**(메타데이터 아닌)가 2018-12-24부터 무료 다운로드되나, 최신판 방법론이 2020.05판과 실질 차이 있나.
3. 대상 브로커의 **정확한 KRX vs NXT 고객 fee pass-through** — 유일한 진짜 미해결 비용항(공식문서 아닌 broker 직접확인 필요).
4. KR이 더 준비된 것으로 드러난 지금, DR-2를 **KR-only vs split**으로? US 미해결 항목이 US를 KR보다 *덜* 준비된 상태로 만들어 ChatGPT 전제를 형식적으로 역전시키나.

## 검증 원장 (Verification Ledger)
- **CONFIRMED (3-0):** KRX300 TR 실재(2011-01-03/2018-12-24/1,216/2초); KOSPI200 TR·NTR(273.81/2016-01-11)·KOSDAQ150 TR(1,014); KRX300 price 방법론(2020.05)이 TR을 별도문서로 분리; KRX 주가지수 공지 board·data.krx.co.kr 구성종목; 거래세법 개정연혁 체인; NXT 공식 수수료(maker 0.00134/taker 0.00182/단일가 0.00158, maker-taker); KIS/NH SOR(분할·opt-out·윈도·수치 미공개); 2-venue 공식 체제; OpenDART 무료 전체재무제표(2015+·BS/IS/CIS/CF/SCE·OFS/CFS·누구나).
- **REFUTED (인용 금지·대체됨):** Global KRX "Factsheet/Constituents 전용섹션"(1-2); 거래세 2026 세부 단일주장(0-3); 거래세 2024 연도별 세부(1-2) → §5 확정 스케줄로 supersede.
- **CAVEATS:** ① 방법론 PDF는 브로커 *미러*서 취득(verbatim·교차확인, 단 최종잠금엔 krx.co.kr 원본) ② KRX300 방법론 2020.05 최신판 여부 ③ 거래세 staged·시변 ④ NXT 2025-03~04 프로모 면제는 과거 ⑤ 브로커 최선집행 문서 주기적 개정 ⑥ TR *시리즈 존재* 증명됐으나 무료 PIT *구성종목*·연속 히스토리 end-to-end 미다운로드 ⑦ OpenDART=as-reported raw XBRL 2015+, 정제 PIT 패널 아님 ⑧ 배당 15.4%=거주자 표준(조약/외국인 별도) ⑨ US DR-1 항목은 재검증 안 함(맥락 인용).

### Sources (primary 위주)
- KRX300 price 방법론: `fdata.kbsec.com/ETN/RULE_580012.pdf` (브로커 미러·2020.05)
- 총수익지수 방법론(TR·KRX300 TR/KOSPI200 TR·NTR/KOSDAQ150 TR): `samsungpop.com …RB_총수익지수+설명.pdf` (브로커 미러)
- KRX 데이터포털·주가지수 공지: `data.krx.co.kr/` · board `boardId=MDCINFO005`
- 거래세법 개정연혁: `law.go.kr/LSW/lsRvsDocListP.do?lsId=005028&chrClsCd=010102` · MOEF 시행령 개정령안 · taxtimes
- NXT 공식 수수료: `nextrade.co.kr/html/charge-info.html`
- 브로커 최선집행: `file.truefriend.com/…/nxt01.html`(KIS) · `downloadcdn.nhqv.com/attach/nxt/terms517.pdf`(NH)
- OpenDART: `opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020` · `/intro/main.do`
- KIND 상폐: `kind.krx.co.kr/investwarn/delcompany.do` · SEIBro: `m.seibro.or.kr`
- (feasibility floor only, labeled) pykrx: `github.com/sharebook-kr/pykrx`

> **stats:** 5 angles · 23 sources · 86 claims · 25 verified · **22 confirmed / 3 killed** · 10 synthesized · 105 agent calls · ~70min.
