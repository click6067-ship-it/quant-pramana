# PRAMANA A2 — Convex Raider Book

> **정제 완성본** (중복·상충 정리·2026-06-13). v1~v7 결론("검증된 알파는 없다")에서 출발해 **전략을 뒤집은** 고위험 공격형 convex book.
> **PAPER only · NO LIVE · 자본권한 0 · V7 생존코어·A1과 완전 분리.** 검증된 알파 ❌ — *QQQ를 크게 이길 확률을 사는* 시스템.

## 0. 왜 A2인가 — v1~v7이 남긴 결론
- 8세대 엄격 검증: 알파 시그널 대부분 죽음·SPY조차 못 이김. **이미 알려지고 수치로 검증된 순간, 그건 알파가 아니라 베타·팩터·상품이 된다.**
- v1→v7 진화 = "QQQ 수익은 따라가되 낙폭만 줄이자(하락·반등 타이밍)"는 아이디어 → 결국 **잘 만든 분산 안전장치일 뿐, 초과수익을 죽임.** 분산은 안전하지만 초과수익의 무덤.
- QQQ/SPY = 미국 혁신기업 승자독식·네트워크효과·AI/SW 레버리지 베팅. 시장 양극화 심화 → **솔로가 이걸 "검증된 알파"로 이기긴 불가능.**
- **버려야 할 두 착각:** ① 검증·증명된 전략을 찾을 수 있다 ② 검증이 강할수록 좋다(검증엔진만 만들다 전부 폐기).
- **그래서 뒤집는다:** 알파 찾기 포기 → **QQQ/TQQQ 베타를 의식적으로 증폭 + Attack/Moonshot 비대칭 + Profit Vault로 수익 회수 + Risk Dashboard로 자멸 방지.**

## 1. 정직한 정체성 (라벨)
- **A2는 검증된 알파 시스템이 아니다.** QQQ를 *안정적으로* 이기는 게 아니라 **크게 이길 확률을 사는** convex book.
  - 강세장 + 리더십 유지 + 문샷 1~2개 적중 → QQQ 초과 가능.
  - 횡보·급락·리더십 붕괴 → QQQ보다 **훨씬** 나쁨. (정직하게 인정.)
- **TQQQ는 Core가 아니라 Booster.** TQQQ = Nasdaq-100 *일일* 3배·매일 reset·장기엔 목표배수와 크게 달라지고 급격한 손실 가능(ProShares/SEC 경고). → "코어니까 버티자" 금지. TQQQ = 의식적 리스크 엔진.
- **A1의 "레버 ETF 금지"를 의식적으로 뒤집은 버전.** A1=레버 없이 catalyst / A2=레버 적극 convex. 둘은 별개 트랙(§10).

## 2. 자본 배분 — regime-shifting (고정 비중 아님)
| Sleeve | Base | Risk-On(Berserker) | Risk-Off | 역할 |
|---|---|---|---|---|
| **QQQ Core** | 30% | 30% | 40% | 성장 베타 기본 |
| **TQQQ Booster** | 40% | 45% | 0~10% | 상승 폭발력(레버) |
| **Attack/Catalyst** | 12% | 15~20% | 5% | 이유 있는 급등주 |
| **Moonshot** | 8% | 8~12% | 0% | 비대칭 베팅 |
| **Profit Vault/Cash** | 10% | 2% | 45~55% | 수익 회수·재장전·생존 |

**실질 노출 인지(Beta Governor):** Base에서 QQQ 30% + TQQQ 40%×3 = QQQ beta ≈ 120%, 합계 ≈ **QQQ 1.5배 노출**. + Attack/Moonshot 성장주 쏠림 → 실질 1.5배+. "공격적"이 아니라 *계좌 성격 자체가 바뀌는* 수준 — 알고 간다.

## 3. 5 엔진 구조
| 엔진 | 구성 | 역할 |
|---|---|---|
| **Beta Engine** | QQQ + TQQQ (+ Beta Governor) | 성장 베타 증폭 |
| **Raid Engine** | Attack + Moonshot | 비대칭 약탈 |
| **Control Engine** | Leadership Risk · TQQQ Decay · Market Stress · LLM Narrative · NEG Gate | 켜고/끄고/줄이기 |
| **Extraction Engine** | Profit Vault (Hard + Reload) | 수익 잠금 |
| **Survival Engine** | Drawdown ladder · Kill switch · Anti-martingale · Human lockout · Crash Reload | 자멸 방지 |

## 4. Control Engine — 계기판 (자동매도 ❌ · 신규/증액 게이트)
### 4.1 Beta Governor
매일 계좌 실질 QQQ beta 계산(QQQ 1× + TQQQ 3× + Attack/Moonshot 추정). 상한 초과 시 TQQQ 증액 금지.
### 4.2 Leadership Risk Score (메가캡 리더 붕괴 감시)
대상: NVDA·MSFT·AAPL·AMZN·GOOGL·META·AVGO·TSLA·AMD·(NFLX/COST). 종목당 1점: 20일선 이탈·50일선 이탈·고거래량 하락일·실적 gap-down·QQQ 대비 상대약세·negative filing.
- **0~10 GREEN** → TQQQ 유지·Attack 허용
- **11~25 YELLOW** → TQQQ 증액 금지·Attack size 50%
- **26+ RED** → TQQQ 신규 금지·Attack/Moonshot 신규 금지 *(기존 강제매도 아님 — 휩쏘 방지)*
### 4.3 TQQQ Decay Meter (횡보 고변동 = 레버 녹는 환경)
QQQ 20일 수익률 ±3% 이내인데 20일 실현변동성↑·고저폭↑ → decay zone → TQQQ 증액 금지·Vault 우선·Attack 축소. ("하락 예측"이 아니라 *TQQQ 불리 환경* 감지.)
### 4.4 Market Stress
QQQ 20/50/200일선·VXN·realized vol·drawdown·credit(HYG/IEF)·yield shock → TQQQ 추가 금지·Attack 축소·Moonshot 보류.
### 4.5 LLM Narrative Risk (정보 요약관·판사 아님)
AI capex·빅테크 가이던스·금리/규제 narrative → GREEN/YELLOW/RED + 근거 3줄 + 영향 sleeve. **LLM은 매도/매수 명령·확률 결정 금지. 포지션 변경은 규칙이 한다.**
### 4.6 NEG Filing Gate (★ 8세대 유일 일관 신호 · 즉시 금지)
3.02 희석/유증 · 3.01 상폐위험 · 4.01 감사인변경 · 4.02 재무신뢰불가 · going concern · ATM offering · S-3 shelf · 반복 유증 · reverse split · 회계오류 → **신규 매수 즉시 금지**(확률 감점 아님). 급등주 = "좋은 놈 찾기" 전에 *지뢰 제거* 먼저.

## 5. Extraction Engine — Profit Vault (수익 약탈 · 핵심)
**왜:** TQQQ·문샷은 폭발하지만 토해내는 속도도 빠름. Vault = 평가익을 *내 돈*으로 잠그는 장치.
### 5.1 Benchmark Vault Rule (excess high-water mark 기반)
`A2_excess = A2 NAV 수익 − QQQ 수익` · `excess_HWM = 누적 최고치`. **새 excess HWM 갱신 시에만** 작동(중복 입금 방지):
- excess HWM ≥ **+4%p** → 신규 초과분의 **25%** Vault
- ≥ **+8%p** → 추가 **25%** Vault
- ≥ **+12%p** → **50%** Vault
- **제한:** 주 1회만 · 월 최대 이동 = NAV의 10% · Vault 자금 임의 재투입 금지.
### 5.2 Hard / Reload 분리
- **Hard Vault (유입 70%)** — 절대 재투입 금지 · 진짜 내 돈 · 심리적 감옥(접근 어렵게).
- **Reload Vault (유입 30%)** — Crash Reload 조건(§7.3)에서만 재장전.
### 5.3 Moonshot Vault
2배 → 원금 회수 / 3배 → 절반 Vault / thesis 깨짐 → 미련 없이 종료.

## 6. Raid Engine — 사이징·진입·청산 (R 단위 · anti-martingale)
### 6.1 R 단위 (비중 아님)
1R = A2 NAV의 0.5% 손실(공격 모드 1.0%). Attack 기본 0.5R·A급 1R·**2R 초과 금지**. Moonshot 기본 1R·강하면 2R·**최대 3R**. (8% sleeve를 한 종목에 몰빵 금지.)
### 6.2 베팅 등급 + EV 게이트
`EV = P_up×Upside − P_down×Downside − Tail − Cost`. 통과: **Reward/Risk ≥ 3:1 · EV > +0.5R · 최대손실 사전확정 · 무효화 조건 명확.**
⚠️ 급등주는 *갭*으로 죽음 → Downside에 **gap risk를 크게** 반영(허접한 문샷 탈락). **P_up 과대평가 금지** — LLM은 bull/bear case만 제공, 확률은 사람이 입력.
### 6.3 Attack 진입
A/B catalyst + **NEG filing 없음** + RVOL 발생 + VWAP 위 + ORB/전고점 돌파 + Leadership RED 아님. **ORB/VWAP/RVOL은 매수 이유가 아니라 confirmation sensor**(총알 = catalyst).
### 6.4 Moonshot thesis 템플릿 (+ expiry)
`Ticker · Thesis · Catalyst · 판정일 · 성공조건 · 실패조건 · 무효화조건 · 최대손실 · Reward/Risk · Exit`. **판정일 필수**(없으면 신앙됨).
**Thesis Decay Timer:** catalyst momentum 10거래일 / delayed recognition 20거래일 / 판정일 경과 — follow-through 없으면 강제 재평가·종료.
### 6.5 Anti-martingale (물타기 금지 = 생존선)
손실 종목 추가매수 ❌. **이긴 것만 피라미딩:** +1R → stop을 breakeven / +2R → 1/3 익절 또는 Vault / +3R → 추가 1/3 Vault / 남은 1/3 trailing. 추가매수는 *+1R 이상 수익 중 & RVOL·VWAP 유지 & RED 아닐 때만*.

## 7. Survival Engine — Drawdown ladder · 모드 · 인간 잠금
### 7.1 Drawdown ladder (완벽한 폭락 방어가 아니라 "물타다 망하는 것" 방지)
A2 MDD −20% → Attack 신규 50% 축소 / −30% → Attack·Moonshot 신규 중지 / TQQQ sleeve −35% → TQQQ 추가 금지·dashboard RED / Attack 연속 손실 3회 → 그 주 신규 금지 / Moonshot 무효화 → 즉시 종료.
### 7.2 모드 (regime-shifting)
- **Berserker** (Leadership GREEN·Decay GREEN·excess+·Attack 최근 5중 3성공·NEG 없음) → Attack 12→20%·Moonshot 8→12%·Vault 유지. *이길 때 더 세게(anti-martingale).*
- **Base** — 기본 비중(§2).
- **Red King** (Leadership/Decay/Narrative 전부 YELLOW) → TQQQ 증액 금지·Attack 50%·Moonshot 금지·Vault 우선. *공격 중립기어.*
- **Risk-Off** (RED) → TQQQ 0~10%·Attack 5%·Moonshot 0·Vault 45~55%.
### 7.3 Crash Reload Rule (폭락 후가 진짜 기회)
QQQ drawdown −20% + VIX spike 후 하락 전환 + QQQ 10일 고점 회복 + 리더 5중 3 20일선 회복 → **Reload Vault** 25%→QQQ · 추가 확인 시 25%→TQQQ. (무지성 저점매수 아님 · 회복 *확인* 매수.)
### 7.4 Regret Budget + Human lockout
숫자 전에 심리 한도 사전 정의(견딜 수 있는 최대 손실·최대 언더퍼폼). Vault·핵심 한도 변경 = 인간 게이트(즉흥 변경 금지).

## 8. 성과지표 (Sharpe 아님 · 고위험 book)
QQQ 대비 누적 excess · excess HWM · **Vault 누적액(실제 잠근 돈)** · Attack hit rate · Moonshot payoff ratio · TQQQ 기여 · 최대낙폭·회복기간 · 큰 승자 의존도 · 월별 worst loss · 리더십 RED에서 손실 회피 여부.
**핵심 = Vault-adjusted return** — 평가익만 오르면 실패, Vault에 *잠근 돈*이 성공.
**성공 정의:** `A2 NAV > QQQ` AND `Vaulted Profit > 0` AND `게임을 계속할 수 있음`.

## 9. 금지 (LOCK)
TQQQ를 알파/Core라 부르기 · 손실 후 물타기 · NEG filing 무시 · Moonshot thesis 없이 진입 · Vault(특히 Hard) 임의 재투입 · LLM이 매도/매수 직접 명령 · "남들이 안 하니까 기회"(안 하는 *이유*를 알고 감당 가능할 때만 — 너무 위험/고비용/심리/장기 실패일 수 있음). · PAPER only · NO LIVE · 자본권한 0 · 사람 = 자본 게이트.

## 10. V7 / A1 / A2 분리 (혼동 금지)
- **V7** = 생존코어(분산·위험효율·Sharpe). **A1** = catalyst attack(레버 없이). **A2** = convex high-risk growth(레버 적극).
- A2 성과가 좋다고 V7이 무용한 게 아니고, A2가 깨져도 PRAMANA 전체 실패가 아니다. **각 트랙 독립 평가.**

## 11. Graveyard Revival — 폐기 전략 부활 (역할 변경 · 다음 작업)
"부활" = 예전 역할로 되살리기 ❌ / **역할 바꿔 살리기** ⭕:
- **A. 수치상 아쉽게 죽은 것** (재검토 후보): quality(broad) · event positive 평균 양수 · 8-K item spread · v2 catalyst weak signal.
- **B. 역할 변경 부활:** ORB/VWAP/RVOL = 매수신호 ❌ → confirmation sensor / NEG 8-K = 숏 ❌ → 매수 금지 필터 / trend = 코어 타이밍 ❌ → risk dashboard 입력.
- **C. 영구 격리:** VRP short-vol · v1 look-ahead 오염 결과 · pure reversal(turnover 폭발).
> **다음 작업:** 폐기 전략 전체를 "수치상 아쉽게 죽은 것부터" 표(전략·죽은 이유·수치·부활 가능 역할)로 정리 → 용하가 부활/격리 직접 판정.

---
> **한 줄:** A2는 검증된 알파가 아니라 — QQQ/TQQQ 성장 베타를 의식적으로 증폭하고, Attack/Moonshot으로 비대칭을 붙이고, Profit Vault로 수익을 잠그며, Risk Dashboard·NEG Gate로 자멸을 줄이는 **고위험 convex book**이다. *이겼을 때만 더 세게, 졌을 때 절대 물타지 않고, 수익은 Vault로 빼고, TQQQ를 알파로 착각하지 않는다.*
