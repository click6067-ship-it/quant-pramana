# 미국 주식 데이터 스택 DR-2B 심화 검토 보고서

본 보고서는 사용자가 지정한 DR-2B 보강 조건을 그대로 반영해 작성했다. 특히 Russell 1000·3000의 PIT 멤버십 구성, CRSP delisting/inactive 처리, CRSP–Compustat PIT linking, SEC EDGAR의 역할 한계, 무료 공식 트랙과 유료 벤더 트랙 분리, 그리고 각 항목의 최종 상태 분류를 중심으로 범위를 제한했다. alpha model, TSFM, LLM agent, XGBoost/LightGBM, 퀀트 운용사 사례, 최종 투자전략 추천으로의 확장은 의도적으로 제외했다. fileciteturn0file0

## 최종 판단

결론부터 말하면, **생산용 미국 주식 PIT 연구 스택은 CRSP US Stock Databases + CRSP/Compustat Merged 또는 Compustat Xpressfeed + WRDS 접근권**을 중심으로 지금 잠그는 것이 타당하다. 그 이유는 CRSP가 이미 **active와 inactive 보안을 모두 포함하는 survivor-bias-free 주가·수익률·상장폐지 정보·기업행사**를 제공하고, Compustat/CCM이 **PIT 링크 범위, filing dates/timestamps, RDQ, GICS history**를 함께 제공하기 때문이다. 반대로 SEC EDGAR와 공개 지수 방법론만으로는 **survivorship-free broad common-stock universe, CRSP-style returns, delisting returns, 안정적인 PIT constituent history**를 생산 수준으로 완결하기 어렵다. citeturn37view0turn40view5turn41view0turn50view3turn51view1

핵심적으로, **Russell과 S&P의 membership을 연 1회 snapshot으로 처리하면 안 된다.** FTSE Russell은 연례 reconstitution 외에 **분기별 IPO addition**, **breakpoint 주변 5% banding**, **추가 share class의 다음 연례 재검토**를 명시하고 있어, Russell 1000/3000 membership은 반드시 이벤트 테이블 기반으로 구성해야 한다. S&P도 반대로 순수 규칙형이 아니라 **Index Committee의 월례 검토·재량·기밀성**이 전제되며, daily constituent data는 **subscription**으로 제공된다고 밝히므로, 공개 자료만으로 S&P 500 PIT membership을 “잠그는” 것은 아직 이르다. citeturn25view0turn25view1turn23view0turn23view3

따라서 DR-2B의 정답은 다음과 같다. **무료 공식 트랙은 프로토타입과 검증용**, **유료 벤더 트랙은 생산용**으로 분리해야 한다. 이 구조에서 지금 잠가도 되는 것은 CRSP 가격/수익률·delisting·Compustat fundamentals·GICS history 같은 **연구용 핵심 패널**이고, 아직 잠그면 안 되는 것은 **S&P 500 및 Russell 1000/3000 membership PIT 재구성**, 그리고 **최종 share-code/exchange-code 화이트리스트·inactive gap handling·CIK bridge 정책**이다. citeturn37view0turn40view3turn41view0turn51view0turn23view0turn25view0

## 지수 멤버십과 PIT 유니버스 구성

Russell 1000과 Russell 3000은 **연례 재구성 한 번**으로 끝나는 지수가 아니다. FTSE Russell 방법론은 IPO를 **가장 최근 reconstitution에서 확정된 market-adjusted capitalization break**에 따라 배정하고, **분기별 IPO review**를 따로 운영하며, IPO rank day를 **각 분기 첫 달의 마지막 영업일**로 두고 3월·9월과 6월·12월의 구현 일정도 다르게 둔다. 또, Russell 1000/2000 경계에서는 **기존 구성종목에 대해 누적 시가총액 기준 5% banding**을 적용해 경계 종목의 잦은 이동을 억제한다. 즉, Russell membership을 “매년 6월 말 한 번 캡처”하는 방식은 PIT 관점에서 불충분하다. citeturn25view0turn25view1

또 하나 중요한 지점은 **추가 share class와 방법론 버전 관리**다. FTSE Russell은 IPO로 도입된 **additional share class가 적격 요건을 충족하지 못하면 즉시 편입되지 않고 다음 연례 reconstitution에서 재검토**된다고 명시한다. 문서 자체도 **버전 번호와 수정 시점**을 갖고 배포되므로, Russell PIT reconstruction 엔진에는 반드시 `methodology_version`과 `effective_date`가 별도 저장돼야 한다. 같은 2024년·2025년 데이터를 2026년 최신 규칙으로 소급 계산하면 PIT 오염이 발생한다. citeturn25view0turn4view0

S&P 500은 Russell보다 더 보수적으로 봐야 한다. S&P U.S. Indices 방법론은 S&P 500이 S&P Total Market Index·Composite 1500 체계 안에 있지만, 실제 **Index Committee가 월별로 corporate action, 후보 종목, 중요 이벤트를 검토**하고, **예외 적용 권한**을 가지며, **회의 내용은 기밀**이라고 명시한다. 또한 S&P는 **daily constituent and index level data는 subscription을 통해 제공**된다고 적시한다. 따라서 **공식 공개 자료만으로는 S&P 500 membership PIT reconstruction을 지금 잠그지 말아야 한다.** 생산용으로 가려면 S&P의 라이선스 데이터, 또는 그것을 재배포하는 벤더 데이터가 필요하다. citeturn23view0turn23view3turn20view0

다만 S&P 자료는 prototype에는 유용하다. S&P U.S. Indices 방법론은 **적격 거래소**, **부적격 증권 유형**, **복수 상장 share class 처리**, **Composite 1500의 12개월 IPO 대기 규칙**, **FALR와 수익성 요건** 등을 공개한다. 즉, **“S&P식 미국 common-stock universe가 어떤 철학으로 정의되는가”**는 공식 문서로 학습할 수 있지만, **실제 historical constituent file**는 subscription 문제 때문에 별도라고 보는 것이 정확하다. citeturn21view0turn21view1turn24view0turn24view1

이 기준으로 보면, DR-2B의 membership 관련 판정은 다음이 맞다. **S&P 500 PIT reconstruction: Do not lock yet. Russell 1000 PIT reconstruction: Do not lock yet. Russell 3000 PIT reconstruction: Do not lock yet.** 이유는 세 지수 모두 “규칙 이해”와 “production-grade PIT constituent history 확보”가 다른 문제이기 때문이다. Russell은 규칙이 공개돼도 constituent history와 licence 문제가 남고, S&P는 아예 committee-discretion 성격이 더 강하다. citeturn25view0turn25view1turn23view0turn23view3

## CRSP 공통주 유니버스와 수익률 처리

생산용 broad common-stock universe의 출발점은 **CRSP security-level universe**여야 한다. CRSP US Stock Databases는 **32,000개 이상 active·inactive U.S. securities**, **survivor-bias-free history**, **security delisting information**, **corporate actions**, **price and return data**, **PERMNO/PERMCO**를 제공한다. 이 자체가 “연구용 미국 주식 기본 우주”의 토대다. citeturn37view0

다만 user가 지적한 대로, 여기서 **share code / exchange code whitelist를 느슨하게 잡으면 ETF, ADR, REIT, closed-end fund, 기타 fund-like security, duplicate share class가 섞인다.** CRSP의 Share Type Code 설명에 따르면, 첫 번째 자릿수는 **1 = ordinary common shares**, **3 = ADRs**, **4 = shares of beneficial interest**, **7 = units/ETFs**, **8 = REITs**를 뜻한다. 또한 두 번째 자릿수에는 **3 = ETFs**, **4 = closed-end funds**, **5 = foreign-incorporated closed-end funds** 같은 구분이 있다. 따라서 broad common-stock universe의 최소 원칙은 **ordinary common shares만 허용하고, ADR·ETF·units·SBI·REIT·closed-end fund는 제거**하는 것이다. 다만 현대 CRSP 구간에서 어떤 세부 코드 집합을 최종 화이트리스트로 잠글지는 acceptance test 전에는 **Provisional**로 두는 것이 맞다. citeturn40view1

Exchange code도 같은 문제를 가진다. CRSP product page는 현대 데이터가 **NYSE, NYSE American, NYSE Arca, NASDAQ, Cboe BZX**를 커버한다고 설명하고, legacy data description guide는 header exchange code의 유효값이 **1~5**라고 적시한다. 즉, 과거 학계의 관행처럼 **EXCHCD in {1,2,3}**만 기계적으로 쓰면 NYSE Arca·Cboe BZX 구간을 누락할 수 있지만, 반대로 이를 모두 허용하면 ETF·기타 비의도 증권 오염 위험이 커질 수 있다. 이 때문에 **post-Arca/BZX 시대의 exchange-code whitelist는 그대로 잠그지 말고 Provisional**로 두고, security-type 필터와 교차 검증해야 한다. citeturn37view0turn40view0

Duplicate share class 오염은 “무조건 제거”가 아니라 **use case에 따라 설계**해야 한다. CRSP의 기본 식별자는 security-level인 **PERMNO**이고, 회사 단위는 **PERMCO**다. S&P 방법론도 복수 share class를 **별도 라인으로 포함**하되 회사 단위 시가총액으로 적격성을 판단한다고 설명한다. 따라서 백테스트가 **security-level** 전략이면 복수 share class는 오염이 아니라 사실 데이터이고, **company-level** 전략이면 `PERMCO` 또는 issuer 기준으로 **대표 line 선정 또는 집계**가 필요하다. 이 분리를 명시하지 않으면 “duplicate contamination”과 “정상적인 multi-class 구조”를 혼동하게 된다. citeturn40view5turn21view1turn22view0

CRSP delisting returns는 이 설계의 핵심이다. CRSP는 delisting return을 **상장폐지 후 가치**와 **마지막 거래일 가격**을 비교해 계산하며, 상장폐지 후 가치는 **다른 거래소 가격**이나 **주주 배분 가치의 총합**을 포함할 수 있다고 설명한다. 만약 상장폐지 후 거래 기회 없이 무가치가 되면 **상장폐지 후 가치는 0**이라고 명시한다. 또한 monthly delisting return 중 일부는 **partial-month proxy**일 수 있으며, 정확한 after-delisting value를 못 잡은 경우가 포함될 수 있음을 설명한다. 이것이 바로 survivorship-safe backtest에서 delisting acceptance test가 별도로 필요한 이유다. citeturn40view3turn39view6turn40view2

Inactive security handling도 반드시 분리해야 한다. CRSP knowledge base는 **exchange code 0**이 “CRSP가 커버하는 거래소를 떠났다가 나중에 돌아오는 공백 구간”을 뜻하며, 이 기간에는 **event data가 추적되지 않고 time series는 missing으로 채워진다**고 설명한다. 더 나아가 off-CRSP 기간 중 사건에 따라 **새로운 PERMNO 또는 PERMCO가 부여될 수 있다**고 적시한다. 따라서 inactive·off-coverage 구간을 단순히 “거래정지 = 0수익률”로 메우면 안 된다. 이 부분은 **Provisional**로 두고 acceptance tests로 잠그는 것이 맞다. citeturn40view4

제가 제안하는 **CRSP delisting / inactive acceptance test**는 아래와 같다.

| 테스트 | 목적 | 제안된 합격 기준 | 근거 |
|---|---|---|---|
| terminal return parity test | 구현한 terminal merge 로직이 CRSP 총수익률 시계열과 모순되지 않는지 검증 | holdout 샘플에서 terminal month/day 처리 결과가 CRSP 원천 수익률 정의와 충돌하지 않을 것 | delisting return 정의 및 partial-period caveat citeturn40view3turn39view6 |
| missing delisting audit | `DLRET` 누락을 자동 0으로 두는 오류 방지 | 누락건을 `DLSTCD`·event family별로 분류하고, 각 군집마다 명시적 정책이 있을 것 | delist history fields 존재 및 after-delist value rules citeturn39view2turn39view3turn40view3 |
| merger/liquidation/bankruptcy matrix | M&A·청산·무가치화 이벤트의 종료가치 처리 검증 | cash/stock/zero-value case가 구분되고, 종목 제거일과 지급일 로직이 정책서에 정의될 것 | CRSP delisting value rules, S&P M&A treatment case-by-case logic citeturn40view3turn16view0 |
| inactive gap test | off-CRSP gap을 잘못 연속 series로 해석하지 않도록 통제 | `EXCHCD=0` 구간은 tradable universe에서 제외되고, 재상장 시 identifier continuity가 재검토될 것 | exchange code 0 설명 citeturn40view4 |
| share/exchange contamination test | ETF/ADR/REIT/fund-like/units 오염 방지 | 허용 share code·exchange code 조합과 제외 사유가 표준화되고, 분기 릴리스마다 drift가 모니터링될 것 | CRSP share type taxonomy 및 exchange coverage citeturn40view1turn37view0turn40view0 |

이 섹션의 최종 판정은 다음과 같다. **CRSP price/return data: Lock now. CRSP delisting returns: Lock now. broad common-stock universe: Provisional. inactive securities: Provisional. share-code/exchange-code filters: Provisional. self-built cap-weight TR benchmark input data: Provisional.** 이유는 데이터셋 자체는 충분히 강하지만, 최종 완성도는 결국 필터·inactive·terminal event 정책을 acceptance test로 굳혀야 하기 때문이다. citeturn37view0turn40view3turn40view4

## Compustat 결합과 펀더멘털 타이밍

CRSP–Compustat linking은 **PERMNO/PERMCO/GVKEY/CUSIP/NCUSIP/CIK의 단순 매핑 문제**가 아니다. CRSP/Compustat Merged Database guide는 link history 파일이 **GVKEY, LinkDt, LinkEndDt, LPERMNO, LPERMCO, LIID, LinkType, LinkPrim**을 포함한다고 명시한다. 즉, 정답은 “어떤 키가 같았는가”가 아니라 **“어느 기간에 어떤 link가 유효했는가”**다. 이 구조에서는 ticker, CUSIP, NCUSIP, 심지어 CIK도 **descriptor 또는 bridge 용도**일 뿐, 기본 join key가 돼서는 안 된다. citeturn42view0turn42view4turn42view7turn40view5

더 중요한 것은 CRSP가 실제로 **default linking process**를 별도로 가지고 있다는 점이다. CCM guide는 fiscal period마다 **10-step process**로 link를 선택하며, 우선적으로 **primary link (P 또는 C)**를 fiscal trading period와 calendar period에 겹치는 방식으로 찾고, 마지막 단계에서야 non-primary link를 고려한다고 설명한다. 또한 `LinkMadeCnt`와 `LinkPERMNOCnt`가 1보다 크면 **드문 상황이 존재하며 CRSP data aggregation에 주의가 필요**하다고 경고한다. 이 문구는 user가 요구한 **ticker reuse, share-class changes, merger/spinoff, multi-link issues**를 실무적으로 어떻게 다뤄야 하는지 분명하게 보여준다. 단순 매핑 테이블 한 장으로 끝내면 안 된다. citeturn42view1turn46view0turn46view2

따라서 PIT linking 원칙은 다음처럼 잠그는 것이 맞다. **security-level CRSP join은 PERMNO, company-level rollup은 PERMCO, fundamentals join은 GVKEY + valid link interval, security disambiguation은 LIID 보조, primary/non-primary 우선순위는 LinkPrim + default linking process**로 처리한다. 반면 **ticker/CUSIP/NCUSIP/CIK는 검색·검증·bridge 보조 열로만 사용**하고, 단독 join key로 쓰지 않는다. 이 원칙 자체는 지금 잠가도 되지만, **정확한 LinkType whitelist**는 이번 패스에서 code-level 공식 정의를 끝까지 확보하지 못했으므로 아직 **Provisional**로 두는 것이 안전하다. citeturn42view0turn42view1turn46view0turn40view5

펀더멘털과 타이밍 면에서 Compustat/CCM은 DR-2B에 매우 적합하다. CCM guide는 별도 **FilingDates** 파일에 **FILEDATE**와 **FILEDATETIME (Timestamp Actual)**이 있음을 명시하고, quarterly descriptor에는 **FDATEQ (Final Date)**, **PDATEQ (Preliminary Date)**, **RDQ (Report Date of Quarterly Earnings)**가 존재한다고 적시한다. 또한 **GICSHISTORY** 파일은 **INDFROM / INDTHRU**와 함께 **GGROUPH, GINDH, GSECTORH, GSUBINDH**를 제공한다. 즉, **펀더멘털 panel, filing timestamp, earnings-related date, sector/industry history**가 벤더 트랙에서 한 묶음으로 구현 가능하다. citeturn50view3turn50view1turn50view2turn51view0turn51view1

따라서 이 섹션의 상태는 다음처럼 정리하는 것이 가장 보수적이면서 실무적이다. **Compustat fundamentals: Lock now. sector/industry history: Lock now. earnings announcement dates: Provisional. CIK/GVKEY/PERMNO linking: Provisional.** 이유는 fundamentals·GICS history는 파일 레벨에서 이미 구조가 명확하지만, **RDQ가 실제 장중/장후 발표 타이밍을 충분히 대표하는지**, 그리고 **CIK bridge를 어떤 reference source로 고정할지**는 아직 별도 확인이 필요하기 때문이다. citeturn50view1turn51view1turn42view0

## 무료 공식 트랙과 유료 벤더 트랙

**무료 공식 prototype track**은 다음 네 가지에 집중해야 한다. 첫째, **SEC EDGAR**는 filing timestamp의 **official floor**로만 사용한다. 둘째, **공식 거래소 calendar**는 “거래 가능일”의 정의에만 쓴다. 셋째, **FTSE Russell·S&P 공개 방법론과 공지**는 membership event engine의 규칙 사전으로 사용한다. 넷째, prototype 단계에서는 이러한 공개 자료로 **PIT logic, lag handling, acceptance test harness**를 먼저 검증한다. 그러나 이번 패스에서는 SEC의 기본 accepted timestamp 필드에 대한 1차 기술 문서를 line-by-line으로 회수하지 못했기 때문에, **EDGAR extraction spec 자체는 아직 Provisional**로 두는 것이 정직하다. citeturn25view0turn25view1turn23view0turn23view3

**유료 벤더 production track**은 훨씬 선명하다. CRSP US Stock Databases는 **active·inactive·returns·delisting·corporate actions·PERMNO/PERMCO**를 제공하고, CRSP/Compustat Merged는 **valid-date linking, filing dates/timestamps, quarterly report dates, GICS history**를 제공한다. 실제 배포 채널도 **WRDS, Snowflake, CRSP direct delivery**가 공식 문서에 명시돼 있다. 따라서 production 스택은 **CRSP + Compustat/CCM + WRDS**를 기본으로 잠그고, 필요하면 FactSet/Bloomberg/LSEG/Refinitiv는 **보조 검증·대체 공급원**으로만 검토하는 구조가 맞다. 다만 이들 보조 벤더의 field-level coverage와 redistribution rights는 이번 보고서에서 검증하지 않았으므로 **Requires vendor / broker / license confirmation**으로 남긴다. citeturn37view0turn41view0

이 구분은 user의 요구사항과도 일치한다. EDGAR는 공개·공식이라는 장점이 있지만, **as-reported fundamentals panel, CRSP-style returns, delisting returns, survivor-bias-free universe**를 하나의 research-grade 스키마로 제공하는 도구가 아니다. 이 보고서는 이를 “EDGAR가 못 한다”고 단정적으로 말하기보다, **반대로 production에 필요한 요소들은 CRSP/CCM 문서에서 명시적으로 확인됐고, EDGAR만으로는 같은 수준의 통합 패널을 이번 패스에서 잠글 수 없었다**는 쪽으로 정리한다. 즉, **EDGAR는 floor**, **CRSP/Compustat은 panel**이다. 이 항목은 추정이 아니라 설계 판정으로 이해하는 것이 적절하다. citeturn37view0turn41view0turn50view3

## 상태 분류표

아래 표는 DR-2B에서 반드시 판정하라고 한 항목들에 대한 **최종 상태**다. 상태는 “지금 설계에 잠가도 되는가”를 의미한다.

| 항목 | 상태 | 판단 요약 |
|---|---|---|
| S&P 500 membership PIT reconstruction | **Do not lock yet** | committee discretion·기밀성·subscription constituent data 때문에 공식 공개 자료만으로 production 잠금 불가. citeturn23view0turn23view3 |
| Russell 1000 membership PIT reconstruction | **Do not lock yet** | annual snapshot 방식은 오류이며 IPO additions·banding·versioned methodology를 반영해야 하나, constituent history/licence가 아직 확정되지 않음. citeturn25view0turn25view1 |
| Russell 3000 membership PIT reconstruction | **Do not lock yet** | Russell 1000과 동일. 특히 3000E/3000 breakpoint와 예외 규칙까지 이벤트형으로 처리해야 함. citeturn25view0turn25view1 |
| CRSP-style broad common-stock universe | **Provisional** | CRSP가 가능하게 해주지만 최종 share/exchange whitelist와 multi-class policy를 acceptance test로 굳혀야 함. citeturn37view0turn40view1turn40view0 |
| CRSP price / return data | **Lock now** | research-grade 주가·수익률·corporate action·survivor-bias-free history가 명시됨. citeturn37view0 |
| CRSP delisting returns | **Lock now** | 상장폐지 후 가치 반영 규칙과 delisting fields가 명시돼 있으며 survivorship-safe backtest의 핵심 축임. citeturn40view3turn39view2 |
| inactive securities | **Provisional** | `EXCHCD=0` off-CRSP gap, missing series, re-entry 시 identifier 변경 가능성 때문에 별도 정책 필요. citeturn40view4 |
| Compustat fundamentals | **Lock now** | production fundamentals panel의 중심. CCM/Compustat file 구조가 명확함. citeturn41view0 |
| SEC EDGAR filing timestamps | **Provisional** | free-official floor로는 채택 가능하지만, 이번 패스에서 SEC 1차 기술 문서 line citation을 회수하지 못해 extraction spec은 미잠금. |
| earnings announcement dates | **Provisional** | RDQ/PDATEQ/FDATEQ가 존재하지만 실제 발표 시각·장후 발표 구분까지 자동 잠금하기엔 검증 부족. citeturn50view1turn50view2 |
| CIK / GVKEY / PERMNO linking | **Provisional** | LinkDt/LinkEndDt/LinkPrim/LIID/default link process는 확인됐지만, 정확한 CIK bridge 및 LinkType whitelist는 추가 확인 필요. citeturn42view0turn46view0turn40view5 |
| sector / industry history | **Lock now** | GICSHISTORY와 effective-from/thru dates가 제공됨. citeturn51view0turn51view1 |
| share-code / exchange-code filters | **Provisional** | ordinary common shares와 부적격 타입 구분은 가능하지만, Arca/BZX 포함 여부와 세부 화이트리스트는 아직 미잠금. citeturn40view1turn37view0turn40view0 |
| self-built cap-weight TR benchmark input data | **Provisional** | price/return/shares/delists는 확보 가능하지만 최종 benchmark 정확도는 universe·inactive·delist 정책 잠금 후에 결정해야 함. citeturn37view0turn40view3 |
| data license for research / paper / production | **Requires vendor / broker / license confirmation** | CRSP·S&P constituent data·WRDS delivery 모두 subscription/licence 전제가 존재. citeturn37view0turn23view3 |

추가로, **무료 공식 prototype track 전체는 Provisional**, **유료 벤더 production track 전체는 Lock now**, **FactSet/Bloomberg/LSEG/Refinitiv를 production 보조 소스로 넣는 문제는 Requires vendor / broker / license confirmation**으로 두는 것이 가장 안전하다. citeturn37view0turn41view0

## 오픈 이슈와 제한사항

이번 패스에서 끝까지 잠그지 않은 것은 의도적이다. **SEC EDGAR accepted timestamp의 정확한 공식 필드/엔드포인트**, **CCM LinkType code별 최종 whitelist**, **현대 CRSP에서 exchange code 4/5를 security-type 필터와 함께 어떻게 반영할지**, 그리고 **CIK bridge의 최종 기준 소스**는 모두 “추정”이 아니라 **추가 확인 대상**으로 남겨두는 편이 맞다. 이 항목들은 보고서 요구사항대로 **Unknown 또는 Requires confirmation** 성격을 유지했다.

따라서 DR-2B 기준의 실무 결론은 한 문장으로 정리된다. **지금 잠글 것은 CRSP+Compustat 생산 스택이고, 아직 잠그지 말아야 할 것은 S&P/Russell membership PIT reconstruction과 최종 심볼·링크·inactive 정책이다.** Russell은 이벤트형 membership 엔진이 필요하고, S&P는 라이선스 constituent history 없이는 production 잠금이 어렵다. EDGAR는 free-official prototype의 filing-time floor에 머물러야 하며, production-grade survivor-bias-safe panel의 대체물이 아니다. citeturn25view0turn25view1turn23view0turn37view0turn41view0