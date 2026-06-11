# 00 · DR-1 Control Sheet (프라마나)

> **이 파일이 DR-1에 넣는 유일한 컨텍스트다.** 긴 v1/v2 보고서·stage0b 전문을 다시 넣지 말 것 — 범위가 다시 넓어진다.
> DR-1 = benchmark / universe / cost / tax / data feasibility **잠금**. 회사·모델·전략 조사 **금지**.

## Project frame (locked)
- **Objective:** 소규모/솔로+AI systematic equity research·validation·trading operating system (KR/US).
- **Target:** benchmark-relative, after-cost excess return.
- **Trading horizon:** 일봉 swing / mid-long (cross-sectional).
- **Markets:** Korean equities + U.S. equities.
- **Excluded:** crypto, direct HFT, direct market making.
- **Auxiliary signals (later):** options, futures, rates, FX, commodities, macro, news, filings, earnings calls.
- **Authority topology:** signal ≠ order · alpha ≠ position · optimizer가 forecast→weight 변환 · 결정론 risk engine이 production 최종 veto.
- **LLM:** off-path advisory/critic only (주문권 0), schema-locked weak-signal artifact 예외.
- **Evidence rule:** firm-income · public track record · user-replicable strategy return 은 **분리 유지**.
- **Data honesty 우선:** 데이터·비용 정직이 알파 정교함보다 먼저.

## DR-1에서 잠그는 4축
1. **Benchmark** — KR/US 각 primary + secondary, methodology·TR 처리.
2. **Universe** — KR/US Phase 1 유니버스 정의, 유동성 필터, PIT 가능성.
3. **Cost / Tax / FX / Slippage** — KR 거래세·수수료·배당세·스프레드·임팩트, US 대응 항목.
4. **Data feasibility** — PIT 멤버십·생존편향·corporate actions·상폐·공시일, 벤더 필요 여부.

## 공격할 provisional 가정 (8)
1. KR-first가 US-first / KR-US parallel보다 나을 수 있다.
2. KOSPI200 + KOSDAQ150(유동성필터) = 합리적 KR Phase 1 유니버스일 수 있다.
3. KRX300 TR = 합리적 KR primary 벤치마크일 수 있다.
4. 자체구축 cap-weight TR = secondary 벤치마크로 필요할 수 있다.
5. KR 거래세·수수료·FX·배당세·스프레드·슬리피지·임팩트가 모델 선택을 지배할 수 있다.
6. NXT/SOR·분절 거래가 paper→live drift를 만들 수 있다.
7. PIT 멤버십·생존편향프리 데이터·CA·상폐·공시일이 blocking issue일 수 있다.
8. US Phase 1 = S&P500 / Russell 1000·3000 / 벤더정의 broad universe 후보(미잠금).

## 명시적 비범위 (DR-1에서 하지 말 것)
- AQR/XTX/Man 등 회사 case study
- TSFM/LLM/XGBoost 등 모델 비교
- 최종 아키텍처·알파 전략 추천

## 소스 규칙
공식·고신뢰 only: KRX, 한국 세법/규제당국, NXT/ATS/SOR 공식자료, S&P DJI, FTSE Russell, MSCI, CRSP, NYSE/NASDAQ rule·calendar, 브로커 수수료표, 벤더 PIT/CA/상폐/생존편향 문서, 학술논문. 블로그·유튜브·X·포럼·마케팅 페이지는 core evidence 금지.

## 산출물 (DR-1 양쪽)
- **ChatGPT (Primary):** Benchmark/Universe/Cost/Data decision matrix + Locked Assumptions v0.1.
- **Claude Code (Red-team, 이 트리의 `04`):** Assumption Attack Table · Official Source Gap · KR/US split critique · Patch-Before-Lock.
- **Merge (`05`, ChatGPT 측):** DR-1 Lock Sheet → DR-2 입력.
