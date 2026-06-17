# A2 — Attack / Moonshot Blind/PIT Backtest 결과

> 작성 2026-06-14 · 엔진 `engine/a2_blind_backtest.py` (+ `a2_feature_store.py`·`a2_event_store.py`·`a2_data.py`)
> 설계 정본 `pramana_a2_delta_patch_pack/02_ATTACK_MOONSHOT_BLIND_BACKTEST.md`
> **판정 라벨: RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 자본권한 0 · 검증된 알파 아님.**
> 이 문서는 Attack/Moonshot을 **forward 빈 슬롯이 아니라 과거데이터로 실제 검증**한다(Attack=광역 backtest·Moonshot=EDGAR 표본 coverage test). 결과 = **Attack DEAD(두 유니버스)·Moonshot 표본 내 edge 없음(NEEDS_EVIDENCE)** — 8세대 결론과 일관. 실패가 아니라 *false-alpha-rejection machine이 또 가짜를 걸러낸 것*.

---

## 0. 사전등록(PRE-REGISTERED) kill 조건 — 결과 보기 **前** 잠금
코드 `PREREG` 딕셔너리에 박혀 있고, 결과로 goalpost를 바꾸지 않았다.

**Attack** (primary horizon = 5거래일, cost 20bp round-trip):
- 트리거(고정): gap≥4% · RVOL20≥2.0 · 21일 momentum≥0 · dollar-vol≥$3M · NEG filing(PIT 90일) 제외
- **DEAD 조건(하나라도 충족 시):** ① net mean excess(vs QQQ) ≤ 0 · ② net median excess < 0 · ③ net win-rate(excess>0) < 50% · ④ 후보 net drift ≤ universe baseline net drift

**Moonshot** (event-study, horizon 21/63거래일):
- event-type별 비대칭 페이오프(up_mean/|dn_mean|) 측정 · 진입 = 공시 available_at **다음 bar**
- **DEAD/INSUFFICIENT 조건:** ① 어떤 event-type도 비대칭(asym≳2) **+ 양의 excess median**을 못 보이면 edge 없음 · ② type별 n<30이면 PASS 금지(INSUFFICIENT)

---

## 1. PIT 무결성 (02 §10 체크리스트)
| 항목 | 상태 |
|---|---|
| 모든 feature에 available_at | ✅ close-of-day t known → `available_at=t`, 진입 t+1 |
| 모든 event에 acceptance/timestamp | ✅ EDGAR `acceptanceDateTime` → available_at(장마감 후/주말 → 다음 거래일) |
| decision_time 저장 | ✅ `decision_log_{universe}.csv` (planned-only·미래값 없음·smallmid 60,136/sp500 4,289행·decision_id·run_id·hash) + `outcome_log_{universe}.csv`(realized fwd 격리) |
| execution_time > decision_time | ✅ 신호 close(t) → 진입 next bar(t+1) |
| same-bar/same-close 체결 금지 | ✅ groupby shift(-1) 진입·shift(-(1+h)) 청산 |
| EDGAR acceptanceDateTime = ET wall-clock | ✅ (Codex fix) 'Z' suffix 무시·tz 제거 후 ET로 취급·16:00 후/주말 → 다음 거래일 |
| yfinance = PROXY 라벨 | ✅ (분봉 경로·여기선 미사용) |
| Sharadar = daily/PIT only | ✅ closeadj·OHLC·SF1 datekey |
| LLM input은 미래정보 배제 | ✅ (LLM on-path 아님·event_store는 timestamp만) |
| decision log | ⚠️ **append-only 아님** — 동결 캐시(HASHES.txt sha256)에서 **결정적 재생성**되는 universe별 스냅샷(run_id·as_of). PIT 무결성은 *데이터 동결*에 근거. decision_log=planned-only(미래값 격리)·realized는 outcome_log 분리(Codex fix). |

---

## 2. ATTACK Stage-A Daily Proxy — 결과 = **DEAD** (두 유니버스 모두)

### 2-A. smallmid 유니버스 (급등주·gap=close-to-close PROXY·진입 next close = 보수적)
트리거 65,178 → forward 없어 제외 2,290(상폐/halt censoring·3.5%) → **후보 60,136건** (NEG PIT 제외 2,752 · NEG coverage 197종)

| horizon | n | net_mean | **excess vs QQQ (mean)** | **excess (median)** | win-rate(excess) | universe baseline |
|---|---:|---:|---:|---:|---:|---:|
| 1d | 60,136 | +0.51% | +0.41% | **−0.25%** | 47% | −0.11% |
| 3d | 60,136 | +1.72% | +1.46% | **−0.34%** | 48% | +0.06% |
| **5d** | 60,136 | +2.51% | +2.08% | **−0.42%** | **48%** | +0.22% |
| 10d | 58,643 | +4.61% | +3.75% | **−0.42%** | 49% | +0.63% |

### 2-B. sp500 유니버스 (대형주·**진짜 open-gap**·진입 **next open** = 정밀)
트리거 4,384 → 제외 11(censoring) → **후보 4,289건**

| horizon | n | net_mean | **excess vs QQQ (mean)** | **excess (median)** | win-rate(excess) |
|---|---:|---:|---:|---:|---:|
| **5d** | 4,289 | +0.29% | **−0.21%** | **−0.43%** | **46%** |
| 10d | 4,268 | +0.84% | −0.09% | −0.49% | 47% |

### 판정 = **DEAD** (사전등록 kill 충족·코드 `verdict_attack`=JSON 일치)
정확한 fail 내역(goalpost 불변·코드/JSON과 1:1):
- **smallmid (h5):** ②(median excess −0.42%<0) · ③(win-rate 48%<50%) 충족 → DEAD. ①(mean +2.08%>0)·④(net drift +2.51%>baseline +0.22%)는 *fail 아님*. (이전 보고서가 "②③④"로 쓴 건 오기 → 정정.)
- **sp500 (h5):** ①(mean −0.21%≤0) · ②(median −0.43%<0) · ③(win 46%<50%) 충족 → DEAD.

**핵심 정직 해석:** smallmid의 양의 평균 excess(+2%)는 *우측 꼬리(소수 대박)가 끌어올린 lottery 분포*다 — **중앙값 trader는 QQQ에 지고(median excess −0.42%) 승률 50% 미만(48%)**. 즉 "평균은 양수지만 전형적 거래는 손해"인 momentum/복권 페이오프. 더 정밀한 sp500(진짜 open-gap·next-open)에서는 **평균조차 음수**가 되어 더 명확히 죽는다. smallmid 평균이 양수인 건 ① close 진입의 보수성 ② 소형주 우측꼬리 ③ **상폐/halt censoring(3.5% 제외=disaster 누락→낙관 편향)** 탓이지 edge가 아니다.

---

## 3. MOONSHOT Event Proxy — 결과 = **edge 없음 / NEEDS_EVIDENCE** (beta 제거 후)
> ⚠️ **범위 정직(Codex fix):** 이건 *전종목 blind/PIT event-study*가 아니라 **EDGAR 표본 200종 event-universe coverage test**다(표본 = leadership + feature_store strong-candidate 빈출 종목 = 전기간 feature 빈도 기반). "Moonshot 전략 완전 검증 증명"이 아니라 **인프라(EDGAR PIT·next-bar·payoff 분포)는 완비, 데이터 커버리지는 표본**. Moonshot 판정 = **NEEDS_EVIDENCE/INSUFFICIENT** (negative는 capital veto엔 충분).
EDGAR 표본 200종·event-study. **excess = QQQ 차감(beta-stripped)** 이 진짜 측정치(raw는 3개월 시장 drift 포함→오도).

| event-type | h | n | **excess_mean** | **excess_median** | asym(up/dn) | win(ex) | [raw_mean] |
|---|---:|---:|---:|---:|---:|---:|---:|
| POS material (1.01/425/M&A) | 63 | 5,352 | +3.0% | **−11.5%** | 1.95 | 37% | [+7.2%] |
| NEG 파산/회계 (1.03/4.02) | 63 | **53** | +18.1% | −2.4% | 2.55 | 47% | [+23.1%] |
| POS 실적 (8-K 2.02) | 63 | 8,137 | +4.2% | **−7.3%** | 1.86 | 41% | [+9.3%] |
| NEG 희석 (S-3/424B/3.02) | 63 | 4,547 | +3.2% | **−11.5%** | 1.92 | 38% | [+7.3%] |

### 판정 = **edge 없음 (대형 그룹) / INSUFFICIENT (소표본 그룹)**
- 모든 대형 그룹: **excess median 음수(−7~−11%) · win-rate(excess) 35~41% < 50%.** raw가 +7~9%였던 건 순전히 3개월 강세장 베타. beta 빼면 *전형적 event 베팅은 QQQ에 크게 진다*.
- 양의 excess_mean은 다시 우측꼬리(asym~2)일 뿐 — 평균이 아니라 *오른쪽 꼬리를 실제로 잡아야* 의미. 중앙값은 음수.
- 흥미로운 "NEG 파산/회계 h63 +18%"는 **n=53 소표본·median −2.4%·win 47%** = 사전등록 ②(n<30 아니지만 소표본)대로 PASS 금지·noise/lottery. 추가검증 가치는 있으나 현재 증거 불충분.

---

## 4. 데이터 한계 (정직)
- **분봉 ORB/VWAP/RVOL 과거검증은 무료/캐시 데이터로 불가**(02 §2·§4). Sharadar=daily backbone. 이 backtest는 **Stage-A daily proxy**만. Stage-B(분봉 confirmation)는 recent yfinance PROXY / 유료 provider forward로만 가능(인프라=`a2_attack_scanner.py`·`a2_intraday_provider.py` 완비, 성과증거 아님).
- smallmid gap = close-to-close PROXY(OHLC 없음). sp500은 진짜 open-gap이라 더 신뢰 → 그쪽이 더 명확히 DEAD.
- EDGAR 이벤트 = 표본 200종(leadership + attack 빈출). 전종목 10년 크롤 = rate-limit상 미실시(인프라 완비). Moonshot은 소표본 탐색.
- 샘플 = 2016~2026 = **닷컴(−49%)·2008(−55%) 없음**(강세장 편향). 모든 결론은 이 한계 안에서.
- cost = flat 20bp round-trip. 실제는 소형주 spread·quote-level execution이 더 깎음 → 결론은 *더 강해질* 방향(낙관 아님).

---

## 5. 결론 — Attack/Moonshot **구현 완료 · Attack(광역) DEAD · Moonshot(EDGAR 표본) edge 없음/NEEDS_EVIDENCE**
1. Attack/Moonshot은 이제 forward 빈 슬롯이 아니라 **feature store(available_at)·event store(EDGAR PIT)·blind backtest(next-bar·decision log)** 로 구현·검증되었다 = 사용자 요구("미구현 금지·전부 구현") 충족. 단 정직: **Attack = 광역 backtest(smallmid 4,414종·sp500 712종)**, **Moonshot = EDGAR 표본 200종 event-study(coverage test)** — 인프라는 둘 다 완비, Moonshot 데이터 커버리지는 표본(전종목 확장은 rate-limit·시간문제).
2. 검증 결과 = **Attack DEAD(광역·두 유니버스)·Moonshot 표본 내 edge 없음(NEEDS_EVIDENCE)** = 8세대 "솔로·공개데이터로 SPY/QQQ 위험조정 초과 = 미발견"과 일관. 시스템이 또 가짜 알파를 안 만들었다(성공). (Moonshot negative는 capital veto엔 충분·"전종목 검증 완료"는 아님.)
3. **그래도 A2가 Attack/Moonshot 슬롯을 유지하는 근거 = "성과 edge"가 아니라 "forward 관찰용 손실제한 실험"(Codex fix·부활경로 차단):**
   ① **smallmid 평균 +2%는 부활 근거 ❌** — median 음수·win<50%·sp500 real open-gap 평균 음수·censoring 낙관편향이면 이건 edge가 아니라 **lottery 분포**. 다중시도/선택편향 환경에서 DSR/PBO류 보정 없이 양의 평균을 살리는 건 금지(Deflated Sharpe = selection bias·overfitting·non-normality 보정 도구). **"우측꼬리 있으니 Attack 살리자" = 명시적 금지.**
   ② Stage-B 분봉 confirmation(VWAP/ORB/RVOL·진입정밀)은 daily proxy가 못 봄 = *유일한 미검증 여지*지만 그것도 forward로만(무료 과거검증 불가).
   ③ 슬롯 유지의 진짜 정당화 = NEG 게이트·token·draft board·thesis = **손실 통제 장치**(backtest와 독립). A2는 "검증된 알파"가 아니라 **"위험을 정직히 인정한 convex 베팅"**(A1 Book과 동일). 매수권 0·사람 게이트·튜닝 금지.
4. **금지:** 트리거 임계값 튜닝(config-mining) · daily proxy 평균 양수를 "Attack 알파/약한 엣지"로 포장 · Moonshot 소표본 +18%(n=53·median −2.4%)를 edge로 승격 · 분봉 proxy를 production 증거로 포장 · EDGAR 표본 coverage test를 "전종목 검증"으로 포장.

산출물: `outputs/a2_decisions/blind_backtest_summary_{smallmid,sp500}.json` · `decision_log_{smallmid,sp500}.csv`(planned·60,136/4,289행) + `outcome_log_{universe}.csv`(realized) · `outputs/a2_features/feature_store.csv` · `outputs/a2_events/event_store.csv`(34,381 EDGAR + zacks).
