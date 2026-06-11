# pythia — 기술보고서 (2026-05-31)

> **라이브 멀티전략 KR 자동매매 + 리서치-검증 시스템.** 본 보고서는 프로젝트 전체(목적·구조·방법론·결과·정직한 한계)를 담는다.
> 규모: **212 commits · 92 모듈 · 코드 7.3k LOC · 테스트 10.2k LOC(629 passed) · Claude×Codex 공동제작.**

---

## 0. 한 줄 — 정직하게
**pythia는 "진짜 돈이 현실에서 *누수 없이* 살아남는지를 *증명*하는, 창피할 만큼 정직한 KR 검증 하니스"다.** 알파를 *발견*했다고 주장하지 않는다 — 오히려 14개 후보를 정직히 심판해 **13개를 기각**(자기 최강 가설까지 포함)하고, 현재 데이터로 **momentum-modest가 경험적 천장**임을 *증명*했다. 가치는 *수익 주장*이 아니라 **자기를 안 속이는 규율**이다.

## 1. 북극성 · 피벗
- **2026-05-29 피벗:** 목적함수를 "시험·발표·학술 채점" → **오로지 수익(실자본 생존)**으로 재설정.
- **성공의 정의:** *"실제 배포 자본 크기에서, 비용(세금 0.20%·수수료·스프레드·슬리피지·미체결·현금drag) 차감 후, 패시브 벤치마크 대비 초과수익."* 단순 "P&L +" 아님. **못 이기면 정직히 보고.**
- **불변 원칙(절대):** ① 비용후 벤치 못 이기면 "진짜" 아님 · ② paper는 운영검증, 자본생존은 사전등록·실거래만 · ③ 결과 본 뒤 바꾸면 새 실험(증거시계 리셋) · ④ **LLM 주문권 0** · ⑤ 증거 불충분하면 "불충분"이라 말함.

## 2. 아키텍처 — 2 레이어
```
① 리서치/카운슬 엔진  →  TargetWeights(계약)  →  ② 결정론적 실행 엔진
  (LLM=리서처·결함감사)     (pydantic, fingerprint)    (KIS, LLM 0, 멱등)
        │                                                    │
        └──── leak-gate (연구↔집행 사이 필수 관문) ──────────┘
```
- **①** = 멀티-LLM 카운슬(병렬 비평·결함적발) + 결정론 팩터 파이프. 역할 = *리서치·누수/과적합/환각 적발*이지 매매 방아쇠 아님.
- **②** = `ExecutionEngine` + stateful `Session` 스파인. append-only JSONL ledger에서 day_start/peak/economic_loss를 복원해 **시간/PnL 리스크 게이트가 실제 작동**(일일 서킷·max-DD −15% kill·−₩3M quit-line·kill switch). crash-safe·멱등.
- **leak-gate** = 두 레이어 사이의 통계적 관문(아래 §4).

**서브시스템 LOC:** execution 2042 · council 1064 · dashboard 729 · data 592 · phase1 558 · backtest 419 · factors 370 · leakgate 330 · strategy 230.

## 3. 방법론 갑옷 (= 자본 보존)
- **No lookahead:** 모든 피처에 `available_at` 타임스탬프; PIT 읽기로 구조적 차단. 공시 09:00 stamp·투자자플로 18:00(장후) → 당일 누수 방지.
- **No survivorship:** point-in-time KOSPI200/KOSDAQ150 멤버십(과거 시점 구성종목) → 생존편향 제거 + 실제 종목별 tier cap(8/5/3%).
- **비용 진실:** 세금(시장별 KOSPI 0.05%+농특세 0.15% / KOSDAQ 0.20%)·수수료·슬리피지·next-bar fill(no same-bar)·현금drag.
- **리스크 게이트:** per-name tier cap · ADV 5% 참여 · 일손실 −2/−3.5/−5% · max-DD −15% kill · gross ≤95% · earn-the-scale 램프(₩2M→…→₩10M) · 중간복리 스윕(50% 통장·천장 ₩2천만).
- **Codex 하드닝:** Session 스파인을 Codex 적대 리뷰 → 회계/안전 버그 **8개 적발·수정 → APPROVED**(sweep 누적합산·손실 oversweep·새날 day_start·정지vs데이터누락·초과매도 short 등).

## 4. leak-gate — 핵심 기여
연구가 *진짜인지(누수 아님)* 를 집행 전에 강제하는 관문. "Profit Mirage"(arXiv 2510.07920: LLM 트레이딩 백테스트 수익 50–72% out-of-sample 붕괴 = 사후지식 암송)에 대한 방어.
- **단계별 독립 verdict**(단일 배지 금지): `in_sample_edge`(연환산 Sharpe) → `cutoff_decay`(LLM cutoff 전후 붕괴율, >50% 기각 = Profit Mirage 경계) → `baseline_excess`(paired t).
- **walk-forward**: 5 fold 중 supermajority(≥⅔)가 baseline을 이겨야 robust — 단일 짧은 OOS 창의 운을 거름.
- **prereg lockbox**: 전략·유니버스·파라미터공간·중단/kill 규칙·trial_count 동결(과적합 회계).
- **검증:** 오염전략(cutoff 붕괴)→decay 기각, 무엣지→1단계 기각, 무초과→baseline 기각, 정상→authorized. *계측 버그(일간 Sharpe에 연환산 바)까지 스스로 잡음.*

## 5. 엣지 탐색 — 정직한 결과 (5 family · 14 config)
실 캐시(KOSPI 100종목, 2022–2026, 비용후)로 게이트+walk-forward 심판:

| family | 결과 |
|---|---|
| 단순 팩터 6개 | **5/6 무엣지**, momentum/monthly만 통과(모뎀·해자아님) |
| 앙상블(momentum+low_vol) | **KILL** — 희석(KR long-only 다양화 적음, Saejoon Kim 실증) |
| 이벤트(공시 PEAD·대량보유) | **무엣지** — title-only 데이터 한계(서프라이즈 크기 없음) |
| 투자자플로(외국인+기관) | flow 단독 sub-bar, flow+momentum ≈ momentum(개선 없음) |

→ **robust 통과 = momentum/monthly 단 하나.** 카운슬의 최강 행태가설(투자자플로)조차 momentum을 못 이김. **병목이 "팩터 영리함"→"데이터 풍부함"으로 이동.** 싸구려데이터 retail 엣지 = marginal(전략방향 회의 D+E 확정, KR 학술 증거 일치).

## 6. Phase-1 — live-forward 증명 시스템
백테스트가 못 보는 것(실 타이밍·체결·비용·degradation)을 측정하는 사전등록 3-arm 페이퍼.
- **동결 프로토콜**(prereg + Amendment 1): A 동일가중 벤치 · B momentum/monthly · C 투자자플로/weekly.
- **결정 로직** `phase1_verdict`: INSUFFICIENT(엣지표본<60일) → KILL(음엣지, 조기) → **CONTINUE**(양엣지·실행표본 미달=유망) → PASS(양엣지+실행표본→다음 staging만, 수익주장 아님). 리스크/비용/턴오버 kill 항시.
- **운영층**: 매일-MTM 마크 러너 · KIS 모의투자 broker(vps 하드코딩=실자본 물리불가) · **비동기 체결 reconcile**(크로스프로세스 영속) · 실 ETF 벤치(KODEX 200) · CLI(`--mode dry-run/report/live`) · `refresh_today` · RUNBOOK.
- **Codex 최종리뷰 → 라이브 결함 8개 수정**: cost=0, 부분체결, 크로스프로세스 상태, 중복마크, report-reconcile, 스케줄 일관, walk_forward 누락baseline, refresh 멱등.
- **dry-run 검증**: B_momentum → CONTINUE(벤치 +32%p, 실행표본 누적중).

## 7. 정직한 완성도 (Claude×Codex 루브릭, 0–10)
| 차원 | 점수 | |
|---|---|---|
| 방법론 엄밀 | 7 | PIT·비용·leak-gate·walk-forward 강함; 다중검정·counterfactual은 gate-v2 |
| 누수-안전 | 6 | 게이트 작동; 카운슬-누수 ablation 미측정 |
| 실행현실 | 4→**6** | 리스크 스파인·KIS broker·비용·크로스프로세스 fix; NXT/VI/실체결 스모크 미완 |
| 시연된 엣지 | 2 | momentum-modest 천장(정직한 발견) |
| 코드/엔지니어링 | 7 | 629 tests·codex 하드닝·crash-safe |
| **반자기기만 규율** | **8–9** | **최강 차별점** — 자기 버그·자기 최강가설까지 기각 |
| KR-특화 | 6 | 멤버십·플로·세금·niche; 관리/정지 플래그 미소싱 |
| 운영성 | 6 | Phase-1 CLI·runbook·broker; 라이브 가동만 영업일 |
| 신규성 | 5 | 카운슬 신규 아님(TradingAgents 선행); 차별=규율·KR niche |
| 북극성 완성도 | 5 | 시스템 완성, 증명은 라이브 후 |

**종합 ~6 — 방법론·엔지니어링·정직은 우수, 엣지·증명은 정직한 미달.**

## 8. 차별화 무기 (정직한 SWAG)
- **창피할 만큼 정직한 leakage-safe KR 검증 하니스** — TradingAgents류(Profit Mirage 50–72% 누수)와 정반대로 *기각 규율*. QuantConnect/LEAN·Zipline(범용·라이브 성숙)엔 범용성으론 지지만 *KR-특화×leak-gate×정직*은 아무도 안 함.
- **소자본이 *이점*인 행태 niche** — 기관이 못 들어갈 저용량 왜곡(외국인/기관 플로 확인, 리테일 혼잡 회피). ₩10M 작음 = 한계가 아니라 사냥터. *가설, 미증명.*
- **LLM 주문권 0 × 결정론 집행 × leak-gate** — "Profit Mirage 시대의 정직한 시스템".

## 9. 남은 것
- **실 KIS 체결경로 영업일 스모크** (코드는 맞으나 실응답 미검증).
- **첫 live-forward 가동**(영업일 09:00–15:30) → 진짜 증거 수집.
- gate-v2: 다중검정(FWER/FDR)·counterfactual(PC/CI/IDS)·카운슬-누수 ablation.
- KR 실행현실: NXT 멀티venue·VI·관리/정지 플래그.

## 10. 스택
Python · pandas/numpy · Parquet · 한투 KIS REST(모의투자) · claude/codex CLI(리서치 카운슬, bwrap 격리) · Streamlit 대시보드. **DL/GPU·관측 SaaS 불채택**(자체 RunManifest·해시).
