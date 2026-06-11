# 한국 주식 Phase 1 PIT 데이터 아키텍처 판정

## 연구 계획

- KOSPI200, KOSDAQ150, KRX300의 **point-in-time constituents**를 만들기 위해 KRX 주가지수 공지, 지수구성종목 메뉴, 지수 방법론 변경 공지를 함께 대조한다. citeturn35search0turn39search7turn39search4turn36view1turn36view0turn37search10
- KOSPI200 / KOSDAQ150 / KRX300의 **membership history**는 정기변경 공지와 수시변경 공지를 이벤트 로그(event ledger)로 만들고, 유니버스별 as-of-date membership 테이블로 재생성한다. citeturn39search7turn39search2turn10search13turn35search0
- **corporate actions와 dividends**는 KSD SEIBro의 권리행사·배당 일정, KIND 배당정보, DART 주요사항보고서를 결합해 self-built adjustment factor 체인으로 설계한다. citeturn15search0turn15search9turn15search19turn33search1turn26search0
- **상장폐지와 survivorship**는 KIND 상장폐지현황·관리종목·매매거래정지, DART 공시원문, KRX 일별시세를 결합해 마지막 거래가능일과 delisting case type을 보존하는 방식으로 설계한다. citeturn13search0turn14search0turn14search6turn25search1turn32search6
- **OpenDART / DART fundamentals floor**는 접수일자(rcept_dt), 접수번호(rcept_no), 정정 포함 여부(last_reprt_at), 재무제표 API(fnlttSinglAcntAll), 연결/별도(fs_div)를 중심으로 PIT 적합성을 평가한다. citeturn12search0turn11search9turn12search5
- **KIND / KRX / SEIBro / DART / KSD의 역할 분담**을 security master, event timestamp, benchmark membership, corporate action ledger, fundamentals floor 관점에서 분리한다. citeturn34view0turn13search1turn15search0turn11search5
- **Data Acceptance Test Suite**는 no-future-membership, no-future-fundamentals, CA/dividend reconciliation, delisting-safe panel, calendar consistency, benchmark replication sanity check를 중심으로 정의한다. 이 테스트를 통과하기 전에는 alpha research를 열지 않는다. citeturn20view0turn35search0turn12search0turn15search9turn13search0
- **DR-3 handoff**는 구현이 아니라 검증으로 넘긴다. 즉, DR-3의 핵심 산출물은 “공식 소스 기반 패널이 실제로 acceptance tests를 통과하는가”이다. citeturn20view0turn12search0turn15search11

## 의사결정 요약과 공식 소스 등록부

### 의사결정 요약

- **판정:** **PATCH-BEFORE-ALPHA**. 한국 주식 Phase 1 연구 패널은 공식/고신뢰 소스만으로 **구축 가능성은 높지만**, corporate action, dividend, delisting stitching과 검증을 끝내기 전에는 alpha research를 열면 안 된다. citeturn20view0turn35search0turn13search0turn12search0turn15search9
- **Confidence:** **Medium**. 가격·기본정보·공시시각·상장/상폐·권리일정은 공식 소스가 충분하지만, PIT sector history, separate earnings announcement date, NXT/broker fill schema는 공개 공식 문서만으로 완결 확인이 되지 않았다. citeturn20view0turn33search1turn27search1turn29search0turn29search2
- **Lock now:** KRX raw daily price/basic data, KRX notice-based PIT membership architecture, OpenDART filing timestamp floor, benchmark universe와 trading universe의 분리, common stock 중심 security scope. citeturn20view0turn35search0turn39search7turn12search0turn36view1turn36view0
- **Provisional:** self-built adjusted close, total-return construction, dividend ledger, corporate action ledger, halt/suspension stitching, delisting-safe exit mapping, self-built cap-weight TR benchmark input set. citeturn23search5turn33search1turn15search19turn14search5turn13search0turn26search0
- **Do not lock yet:** separate earnings announcement dates, PIT sector/industry history, final numeric liquidity thresholds. citeturn12search0turn33search1turn14search7
- **Requires vendor or broker confirmation:** NXT eligible-universe history export, venue-level fill tag, broker routing metadata, best-execution log granularity, production licensing path. citeturn27search1turn27search9turn29search0turn29search2turn19search3turn19search8
- **왜 진행 가능한가:** KRX는 일별 주식/종목기본정보를 2010년 이후 제공하고, KRX 주가지수 공지는 정기·수시 편출입 이벤트를 공지하며, KIND는 상장/상폐/정지/관리 상태를 제공하고, OpenDART는 공시 접수일자와 재무 API를 제공한다. citeturn20view0turn35search0turn39search7turn13search0turn14search0turn12search0turn11search9
- **왜 아직 GO가 아닌가:** KIND 배당정보는 업종변경 반영과 결산월 처리에 PIT 주의사항이 있고, SEIBro 포털은 오류·지연 가능성을 고지하며, 상장폐지 수익과 권리조정은 케이스별 결합 검증이 필요하다. citeturn33search1turn15search9turn32search6turn25search1

### 공식 소스 등록부

| Source | Institution | Source type | What data field or requirement it supports | Date or latest version | Access date | Reliability | Notes |
|---|---|---|---|---|---|---|---|
| **SR-A KRX Open API 서비스 목록 및 주식 API 명세** | 한국거래소 KRX | 공식 API 문서 | 일별 주식시세, 종목기본정보, 시장별 가격/거래량/시총/상장주식수 | 서비스 목록 현재, 주식 일별명세 최근수정 2026-01-16 | 2026-06-07 | High | 주식·지수·기본정보 API 제공, 2010년 이후 데이터 명시. FAQ상 비상업적 이용 제한 주의. citeturn20view0turn19search5turn19search3turn22search9 |
| **SR-B KRX Data Marketplace 메뉴/이용안내** | 한국거래소 KRX | 공식 데이터 포털 | 지수구성종목, 전종목 기본정보, 전종목 지정내역, 업종분류 현황 등 메뉴 존재 | 현재 페이지 | 2026-06-07 | High | 기본 통계/이슈 통계 메뉴 구조와 다운로드 계통을 확인하는 기준 소스. citeturn34view0turn24search4turn39search6 |
| **SR-C KRX 주가지수 공지 보드 및 정기변경 notices** | 한국거래소 KRX | 공식 공지 | KOSPI200/KOSDAQ150/KRX300 정기·수시 변경 effective date, 편입/편출 종목 | 2022-06-10, 2022-12-09, 2023-12-15, 2026-05-22 확인 | 2026-06-07 | High | membership replay의 이벤트 로그. 보드에서 여러 연도 notices 확인 가능. citeturn39search2turn39search7turn39search4turn35search0 |
| **SR-D KOSPI 200 방법론 변경 공지** | KIND / KRX | 공식 공시 | Eligible universe, 제외대상, 유동주식비율 10% 기준, 코스피지수 연계 | 2024-01-02 | 2026-06-07 | High | KOSPI200 심사대상종목과 exclusions의 최신 공시형 텍스트. citeturn36view1 |
| **SR-E KOSDAQ 150 방법론 변경 공지** | KIND / KRX | 공식 공시 | Eligible universe, 신규상장 특례(상위 30위), 기업분할 심사, exclusions | 2024-01-02 | 2026-06-07 | High | KOSDAQ150 특수 케이스 처리 규칙의 공식 텍스트. citeturn36view0 |
| **SR-F KRX 300 방법론 변경 공지** | KIND / KRX | 공식 공시 | 최소 유동주식비율 10%, 신규상장 특례, 시장통합 대표지수 규칙 | 2024-01-02, 2024-09-30 | 2026-06-07 | High | KRX300 benchmark membership/benchmark replication 판단 근거. citeturn37search10turn37search4turn37search3 |
| **SR-G KIND 상장종목현황 및 신규상장기업현황** | KIND / KRX | 공식 상장정보 | listing date, market, 업종, 최초상장주식수, 신규상장 이벤트 | 현재 / 신규상장현황 현재 | 2026-06-07 | High | listed/unlisted 구분과 신규상장 기준 데이터의 공식 소스. citeturn13search1turn13search8turn25search2 |
| **SR-H KIND 상장폐지현황 및 상장폐지 최종 심의 의사록** | KIND / KRX | 공식 상폐정보 | delisting date, delisting reason, case review track | 현재 | 2026-06-07 | High | survivorship-safe master에 필수. 상장폐지 최종 심의 의사록도 제공. citeturn13search0turn13search9 |
| **SR-I KIND 관리종목 / 매매거래정지종목 / 투자주의환기 / 상세검색** | KIND / KRX | 공식 시장조치 정보 | halt/suspension, admin flag, warning flag, 시장조치 이벤트 | 현재 | 2026-06-07 | High | tradability filter와 suspension handling의 핵심 소스. citeturn14search0turn14search6turn14search2turn14search5 |
| **SR-J KIND 배당정보** | KIND / KRX | 공식 요약정보 | 배당 관련 summary, 제공기간 2010~최근 사업연도 | 현재 | 2026-06-07 | Medium | 유용한 보조 소스지만 “현재 결산월”, “업종변경 익년 반영” 주의가 있어 PIT truth로 단독 사용 금지. citeturn33search1 |
| **SR-K OpenDART 공시검색(list) 및 corpCode** | 금융감독원 FSS / OpenDART | 공식 API 문서 | rcept_dt, rcept_no, amended/final filing logic, corp_code mapping | 가이드 현재, OpenDART 서비스 2020-01-21 이후 | 2026-06-07 | High | list API는 접수일자 기반 검색, last_reprt_at로 정정 포함/최종만 구분. corpCode API 제공. citeturn12search0turn11search7turn11search3 |
| **SR-L OpenDART 재무정보 API** | 금융감독원 FSS / OpenDART | 공식 API 문서 | fnlttSinglAcntAll, bsns_year, reprt_code, fs_div, stock_code, rcept_no | 가이드 현재 | 2026-06-07 | High | 연결/별도 구분과 종목코드 매핑까지 제공하는 foundations floor. citeturn11search9turn12search5 |
| **SR-M OpenDART 주요사항보고서 API** | 금융감독원 FSS / OpenDART | 공식 API 문서 | merger/spin-off/rights 등 event extraction 후보 | 가이드 현재 | 2026-06-07 | High | 회사합병 결정 등 주요사건 API 존재. corporate action normalization의 event source 후보. citeturn26search0turn23search12 |
| **SR-N DART 원문 검색** | 금융감독원 FSS / DART | 공식 원문 시스템 | 원문 filing, 정정보고서 검색, 오래된 filing 접근 | 현재 | 2026-06-07 | High | OpenDART가 충분하지 않은 case에서 final legal/source-of-truth 원문 확인용. citeturn11search4turn11search1 |
| **SR-O FSS 기업공시길라잡이** | 금융감독원 FSS | 공식 제도 해설 | 정리매매기간 법적 status, 공시/지분보고 해석 | 현재 | 2026-06-07 | High | 정리매매기간 중에도 상장법인 status가 유지된다는 제도 설명 확인. citeturn25search1turn25search9 |
| **SR-P KSD SEIBro 포털 및 오픈플랫폼** | 한국예탁결제원 KSD | 공식 포털/API 포털 | 권리행사정보, 배당내역상세, 주식권리일정, 오픈플랫폼 | 현재 | 2026-06-07 | High | CA/dividend 일정에 매우 중요하나 포털은 오류·지연 가능성 고지. 오픈플랫폼은 machine-readable candidate. citeturn15search0turn15search1turn15search9turn15search19turn15search11 |
| **SR-Q NXT 공식 사이트 및 시장정보** | 넥스트레이드 NXT | 공식 시장자료 | ATS launch date, eligible securities, daily venue stats, trading hours | 2025-03-04 개시, 현재 시장정보 | 2026-06-07 | High | KRX와 별개 execution regime를 데이터로 explicit하게 분리해야 함. citeturn27search11turn27search1turn27search9turn27search0 |
| **SR-R 공식 broker SOR / 최선집행 문서** | 키움증권, 한국투자증권 등 | 공식 브로커 문서 | SOR logic, routing consideration, order/fill metadata 필요성 | 2025-02-13, 2026-03-03 등 | 2026-06-07 | High | 주문은 KRX/NXT 비교 후 집행될 수 있고, venue 로그와 routing metadata가 별도 필요함을 확인. citeturn29search0turn29search2turn29search5turn29search8turn29search9 |
| **SR-S FnGuide DataGuide / QuantiWise** | FnGuide | 공식 vendor documentation | 대체 vendor floor, 시계열 재무/자본변동/주가/매매동향 제공 여부 | 현재 | 2026-06-07 | Medium | KR-specific production acceleration 후보지만 field-level PIT 검증은 별도 필요. citeturn42search0turn42search5turn42search8 |
| **SR-T Bloomberg Reference Data / Research Data** | Bloomberg | 공식 vendor documentation | reference data, corporate actions, classifications, PIT research datasets | 현재 | 2026-06-07 | Medium | 글로벌 production-grade validation 후보. KR local event-depth와 licensing scope는 별도 확인 필요. citeturn42search2turn42search9turn42search11turn42search15 |

공식 소스 등록부를 기준으로 보면, **가격·지수·상장/상폐·공시·권리행사**의 핵심 축은 KRX, KIND, FSS/DART, KSD SEIBro로 닫힌다. 다만 Open API의 이용조건과 vendor/broker 계약범위는 별도 확인이 필요하므로, **prototype에는 official stack**, **production 검증에는 vendor/broker confirmation track**을 병행하는 것이 가장 안전하다. citeturn19search3turn19search8turn20view0turn12search0turn15search11turn29search2

## 소스 역할 지도와 PIT 멤버십 아키텍처

### KR 데이터 소스 역할 지도

| Source | Data type | Official or convenience layer? | PIT usefulness | Coverage | Machine-readability | Known limitation | Recommended treatment |
|---|---|---|---|---|---|---|---|
| KRX Data Marketplace | 일별 가격, 종목기본정보, 지정내역, 지수구성종목 메뉴 | Official | High | KRX 상장주식/지수 | Medium~High | 메뉴 기반 접근, 일부 UI/권한 의존 | **Use** |
| KRX index notices / methodology | 편입·편출 이벤트, 규칙, effective date | Official | High | KOSPI200/KOSDAQ150/KRX300 | Medium | notice scraping 필요, 수시변경 누락 위험 | **Use** |
| KIND | listing/delisting, halt, admin, dividend summary, stock issuance | Official | High | KRX listed issuers | Medium | summary 성격 데이터 존재, 일부 PIT caveat | **Use** |
| DART / OpenDART | filing timestamp, filings, financial statements, major issues | Official | High | 상장법인 + 기타법인 | High | “latest-only” 사용 시 PIT 훼손 가능 | **Use** |
| FSS | corporate disclosure rules and interpretation | Official | Medium | 제도/절차 | Low~Medium | 데이터 패널보다는 규정 해석용 | **Use with caution** |
| KSD SEIBro | rights calendar, dividend detail, security/corporate-action ledger candidate | Official | High | 증권권리·배당·일정 | Medium | 포털 오류·지연 가능성 고지, API coverage 확인 필요 | **Use with caution** |
| NXT / Nextrade | ATS eligible list, venue-level volumes, hours | Official | Medium | ATS phase 이후 | Medium | history export completeness Unknown | **Requires validation** |
| Broker fill reports / API fields | order/fill timestamps, venue tag, routing log | Official broker-specific | High for reconciliation | broker account scope | Medium~High | 브로커별 필드 상이, 공개 명세 불완전 | **Requires validation** |
| pykrx or similar libraries | python wrapper / convenience client | Convenience layer | Low by itself | wrapper가 지원하는 범위 | High | upstream schema drift, provenance ambiguity | **Convenience only** |
| FnGuide DataGuide | vendor data workstation | Vendor | Medium~High | KR broad | Medium | 계약/field-level PIT validation 필요 | **Requires validation** |
| QuantiWise | vendor data workstation | Vendor | Medium~High | KR broad | Medium | Excel 설치형, exact PIT semantics 별도 검증 필요 | **Requires validation** |
| NICE / KISVALUE | vendor reference/fundamental stack | Vendor | Unknown | KR corporate/reference | Unknown | 공개 KR-specific PIT spec 미확인 | **Requires validation** |
| Bloomberg | global reference / CA / research data | Vendor | High in principle | Global incl. KR | High | KR local mappings와 라이선스 확인 필요 | **Use with caution** |
| Refinitiv | vendor global data | Vendor | Unknown | Global incl. KR | Unknown | 공개 KR-specific PIT doc 미확인 | **Requires validation** |
| FactSet | vendor global data | Vendor | Unknown | Global incl. KR | Unknown | 공개 KR-specific PIT doc 미확인 | **Requires validation** |
| S&P/Compustat | vendor global reference/fundamentals | Vendor | Unknown | Global | Unknown | 공개 KR-specific PIT doc 미확인 | **Requires validation** |

이 역할 지도에서 중요한 점은 **truth hierarchy**다. **official raw/event layer는 KRX-KIND-DART-SEIBro**, **broker layer는 execution reconciliation**, **vendor layer는 acceleration/secondary validation**, **pykrx 같은 라이브러리는 convenience only**로 두는 것이 가장 안전하다. 특히 OpenDART의 `last_reprt_at` 필터와 KIND 배당 summary는 편의성이 높지만, 이를 그대로 training panel에 넣으면 PIT가 무너질 수 있다. citeturn12search0turn33search1turn20view0turn15search9

### PIT 멤버십 아키텍처

KOSPI200, KOSDAQ150, KRX300의 PIT membership은 **공식 정기변경 공지 + 공식 수시변경 공지 + 지수구성종목 snapshot**의 조합으로 재구성할 수 있다. KOSDAQ150은 신규상장 특례와 기업분할 심사 규칙이 더 복잡하고, KRX300은 방법론 개정과 benchmark 용도 때문에 검증 강도가 높아야 하지만, 세 유니버스 모두 **look-ahead-free replay** 자체는 가능하다고 보는 것이 합리적이다. citeturn39search7turn39search2turn39search4turn35search0turn36view0turn36view1turn37search4

**명시적 답변**

- **KOSPI200 + KOSDAQ150 historical membership을 look-ahead bias 없이 재구성할 수 있는가?**  
  **Yes, but event-ledger + validation 필수**다. 정기변경 공지와 수시변경 공지를 effective date 기준으로 재생하고, 각 change가 공지 이전 날짜에 보이지 않는지 테스트해야 한다. citeturn39search7turn39search2turn10search13turn35search0
- **KRX300 membership을 benchmark 비교용으로 충분히 재구성할 수 있는가?**  
  **Yes, benchmark comparison용으로는 가능**하다. 다만 KRX300 TR 자체를 replication sanity check로 통과시키기 전까지는 **benchmark input set은 Provisional**로 두는 편이 안전하다. citeturn39search4turn37search10turn37search4
- **custom liquidity-filtered universe가 raw index membership보다 안전한가?**  
  **Yes.** index membership은 benchmark 목적 규칙을 반영하지만, 연구 유니버스는 PIT tradability와 market-status flags를 직접 반영해야 한다. 따라서 **KOSPI200+KOSDAQ150 union을 base로 하고 liquidity/halting/admin filters를 별도 적용**하는 방식이 더 안전하다. citeturn14search0turn14search6turn20view0
- **as-of-date membership table에 필요한 정확한 파일/테이블은 무엇인가?**  
  아래 “필수 파일/테이블 목록” 참조. citeturn34view0turn39search6turn35search0

| Universe | Membership source | Regular review / rebalancing rule availability | Historical notices availability | PIT reconstruction feasibility | Automation difficulty | Main failure mode | Required validation test | Status |
|---|---|---|---|---|---|---|---|---|
| KOSPI200 | SR-C + SR-D + SR-B 지수구성종목 | Yes | Yes | High | Medium | 수시변경 notice 누락, code change mapping 오류 | notice replay vs as-of constituent snapshot | **Lock now** |
| KOSDAQ150 | SR-C + SR-E + SR-B 지수구성종목 | Yes | Yes | High | Medium-High | 신규상장 특례/기업분할 특례 누락 | special-entry / split-case replay test | **Lock now** |
| KRX300 | SR-C + SR-F + SR-B 지수구성종목 | Yes | Yes | High | Medium-High | 방법론 개정 미반영, benchmark sanity mismatch | membership replay + benchmark sanity check | **Lock now** |
| KOSPI200 + KOSDAQ150 combined universe | KOSPI200 PIT ∪ KOSDAQ150 PIT | Derived | Derived | High | Low-Medium | 이전상장/재상장/중복 mapping | no-duplicate instrument_id test | **Lock now** |
| Custom liquidity-filtered KR universe | combined PIT universe + SR-A daily price/basic + SR-I status flags + SR-H delisting | Self-defined | N/A | High | High | rolling-window look-ahead, halted name leakage | rolling window lag test + no future tradability test | **Lock now** |

**필수 파일/테이블 목록**

| Needed file or table | Why needed | Primary source |
|---|---|---|
| KRX 주가지수 공지의 정기변경 notice 원문/텍스트 | 반기 정기 편입·편출 이벤트 ledger | SR-C |
| KRX 주가지수 공지의 수시변경 notice 원문/텍스트 | 이전상장, 신규상장 특례, 기업분할, 상폐 등 instant events | SR-C |
| KRX 지수구성종목 as-of-date export 또는 snapshot | replay 결과의 교차 검증 | SR-B |
| KRX 전종목 기본정보 / 종목기본정보 | 시장구분, 종목명, shares, issue type, base universe | SR-A / SR-B |
| KRX 전종목 지정내역 | 관리종목/거래정지/시장조치 상태 | SR-B |
| KIND 상장종목현황 / 신규상장기업현황 | listing date, 신규상장 이벤트 | SR-G |
| KIND 상장폐지현황 / 관리종목 / 정지종목 | delisting/halt/admin event layer | SR-H / SR-I |
| DART major issue filings | split, merger, rights, spin-off case stitching | SR-M / SR-N |

## 시큐리티 마스터와 가격·리턴 계약

### 시큐리티 마스터와 corporate action 설계

한국 주식 panel은 **종목코드(short code)**를 primary key로 두면 안 된다. 내부 `instrument_id`를 고정하고, 여기에 **KRX 코드, ISIN, DART corp_code, issue type, listing/delisting status, preferred/common/SPAC/REIT flags**를 매핑하는 구조가 필요하다. OpenDART 재무 API는 `stock_code`, `rcept_no`, `fs_div`를 제공하므로 filing table과 security master의 연결점이 된다. citeturn12search5turn11search7turn34view0

| Requirement | Official source candidate | Field needed | PIT requirement | Adjustment rule | Failure mode if missing | Required acceptance test | Status |
|---|---|---|---|---|---|---|---|
| Stable internal instrument master | SR-A, SR-B, SR-K | instrument_id, stock_code, corp_code, market, issue_type | history-preserving mapping | no adjustment; immutable ID | code change 시 시계열 단절 | duplicate / remap test | **Lock now** |
| Stock code changes | SR-B, SR-G, SR-N, SR-P | old_code, new_code, effective_date | as-of effective date mapping | back-link only, no retro overwrite | 과거 데이터 orphan 발생 | code-chain continuity test | **Provisional** |
| Name changes | SR-B, SR-G, SR-N | old_name, new_name, effective_date | as-reported name at date | no price adjustment | filing/notice join 오류 | name-history replay test | **Provisional** |
| Listing date | SR-G | list_date | exact first tradable date | none | 신규상장 lag, universe leakage | listing date vs first price test | **Lock now** |
| Delisting date | SR-H | delist_date, delist_reason | exact last listed date | remove after delist date; keep history | survivorship bias | delist coverage test | **Lock now** |
| Trading suspension / resumption | SR-I, SR-B | halt_start, halt_end, reason | status by day | no synthetic returns during halt | stale price traded as live | halt-state test | **Provisional** |
| Splits / reverse splits | SR-P, SR-M, SR-N, SR-I | ratio, ex/effective date | event-date accuracy | multiplicative factor chain | false alpha via mechanical gap | CA factor reconciliation test | **Provisional** |
| Rights issues | SR-P, SR-M, SR-N | rights ratio, price, ex date | event before price adjustment | factor + optional cash/value leg | adjusted price distortion | rights-event replay test | **Provisional** |
| Bonus issues | SR-P, SR-M | ratio, ex date | event-date accuracy | factor chain | gap misclassification | abnormal return detection | **Provisional** |
| Dividends | SR-P, SR-J, SR-N | ex-date, record date, payment date, cash per share | ex-date usable in PIT | cash adjustment in TR only | TR benchmark error | dividend reconciliation test | **Provisional** |
| Mergers / spin-offs | SR-M, SR-N, SR-H | merger ratio, cash/stock consideration, effective date | case-level handling | case-specific; no generic factor-only rule | exit return error, duplicate continuation | merger/spin-off casebook test | **Provisional** |
| Share class changes | SR-B, SR-P, SR-N | class flag, old/new class | security identity continuity | no implicit merge | preferred/common contamination | share-class separation test | **Provisional** |
| ETF vs common stock exclusion | SR-B, SR-G | issue_type, security_category | exclude at universe build | none | ETF/ETN contamination | issue-type whitelist test | **Lock now** |
| Preferred stock / SPAC / REIT handling | SR-D, SR-E, SR-B, SR-G | preferred_flag, SPAC_flag, REIT_flag | explicit exclusion rule | none | benchmark/universe mismatch | whitelist / blacklist test | **Lock now** |

**설계 해석**

- **보통주(common stock)만 Phase 1 기본 대상**으로 두는 것이 안전하다. KOSPI200/KOSDAQ150 방법론 자체가 SPAC, REIT 계열, 낮은 유동주식비율 종목을 배제하는 방향으로 설계되어 있기 때문이다. citeturn36view1turn36view0
- **KIND 배당 summary 하나로는 부족**하다. 배당정보는 2010년 이후를 제공하지만, current 결산월/업종 기준 caveat가 명시되어 있어 PIT truth는 **SEIBro + DART source filing**으로 재구성하고 KIND는 reconciliation용으로 두는 편이 맞다. citeturn33search1turn15search9
- **M&A, spin-off, code changes는 event ledger 방식**이 필요하다. 이 영역은 단순 수정주가 방식보다 **casebook-driven normalization**이 더 안전하다. citeturn26search0turn23search12turn13search0

### Price / Return Data Contract

KRX 공식 소스로는 **raw unadjusted OHLCV, 거래대금, 시가총액, 상장주식수**를 확보할 수 있다. 반면 **adjusted close, adjustment factor, total return**은 공식 free field로 명확히 확인되지 않았으므로, Phase 1에서는 **self-built derived fields**로 설계하는 것이 타당하다. citeturn23search5turn23search8turn20view0turn15search9

| Field | Required? | Source candidate | PIT issue | Adjustment issue | Acceptance test | Blocking severity |
|---|---|---|---|---|---|---|
| trade_date | Yes | SR-A | exchange holiday / ATS session 분리 필요 | none | calendar consistency | Critical |
| market_code | Yes | SR-A, SR-B | KOSPI/KOSDAQ/NXT scenario 분리 | none | market enum validation | High |
| stock_code | Yes | SR-A, SR-B | mutable key 위험 | none | code-master join test | Critical |
| instrument_id | Yes | Derived from security master | must be immutable | none | duplicate mapping test | Critical |
| open | Yes | SR-A | as-of date only | raw only | OHLCV completeness check | Critical |
| high | Yes | SR-A | as-of date only | raw only | OHLCV completeness check | Critical |
| low | Yes | SR-A | as-of date only | raw only | OHLCV completeness check | Critical |
| close | Yes | SR-A | as-of date only | raw only | OHLCV completeness check | Critical |
| volume | Yes | SR-A | NXT+KRX 합산 여부 regime 의존 | raw only | missing/zero-volume logic test | High |
| traded_value | Yes | SR-A | venue split 가능 | raw only | ADV / MDVT recompute test | High |
| market_cap | Yes | SR-A | daily as-of needed | raw only | market-cap continuity test | High |
| listed_shares | Yes | SR-A | corporate action day jump | raw only | share-count jump vs CA test | High |
| trading_status_flag | Yes | SR-I, SR-B | halt/admin/warning by day 필요 | none | status-vs-price consistency | Critical |
| halt_flag | Yes | SR-I | suspend day missing-price 구분 필요 | none | halt handling test | Critical |
| missing_price_reason | Yes | Derived | must separate holiday / halt / bad ingest | none | null reason completeness | High |
| adjusted_close | Yes | Derived from SR-A + SR-P + SR-J + SR-M | cannot use future CA | factor chain depends on complete CA ledger | adjusted-close reconciliation | Critical |
| adjustment_factor | Yes | Derived | must be date-effective and monotone in chain | split/rights/bonus logic case-specific | CA factor chain test | Critical |
| dividend_cash_per_share | Yes | SR-P, SR-J, SR-N | ex-date vs pay-date distinction | cash-only TR leg | dividend reconciliation | Critical |
| total_return_1d | Yes | Derived | must use ex-date availability only | dividend + CA combined | self-built TR sanity check | Critical |
| total_return_index | Yes | Derived | index divisor / missing events risk | derived from daily TR | benchmark replication sanity | High |
| calendar_id | Yes | Derived from official trading days | holiday drift risk | none | trade-date universe test | High |
| price_limit_hit_flag | No | Unknown / derived if implemented | field availability not confirmed | do not infer unless validated | optional only | Medium |
| version_id | Yes | Ingestion metadata | raw file/version reproducibility | none | hash / lineage test | Critical |
| source_name | Yes | Ingestion metadata | provenance traceability | none | lineage completeness | Critical |
| ingest_timestamp | Yes | Ingestion metadata | replay / audit trail | none | audit log completeness | High |

**운영 규약**

- **Unadjusted OHLCV는 source-of-truth**, **adjusted close / total return은 derived layer**로 분리해야 한다. raw와 adjusted를 같은 테이블/같은 컬럼에서 교체하면 PIT 감사가 어려워진다. citeturn20view0turn15search9turn26search0
- **Dividend cash adjustment는 ex-date 기준 total return에 반영**하고, pay-date는 cash timeline으로 별도 보관하는 것이 맞다. KIND summary와 SEIBro detailed schedule은 둘 다 갖되, SEIBro/DART를 truth에 가깝게 두고 KIND는 reconciliation 보조로 둔다. citeturn15search9turn15search19turn33search1
- **Missing price handling**은 “휴장”, “halt”, “정리매매 미체결”, “ingestion failure”를 구분해야 한다. 단순 forward-fill은 feature engineering 편의에는 쓸 수 있어도 tradability 판단에는 사용하면 안 된다. citeturn14search0turn25search1
- **Data versioning**은 raw snapshot immutable 저장이 원칙이다. 이후 정정/재수집은 overwrite가 아니라 새 version row로 남겨야 acceptance test 재현이 가능하다. 이는 공식 filing 정정 구조와도 일치한다. citeturn12search0turn11search4

## 상장폐지와 펀더멘털 바닥선 및 유동성 데이터

### Delisting / Survivorship Bias Protocol

한국 시장에서는 involuntary delisting 주변의 가격 충격이 매우 크고 유동성이 사실상 사라질 수 있으므로, **상장폐지 안전(delisting-safe) 데이터 없이 cross-sectional alpha research를 여는 것은 금지**하는 편이 맞다. 한국 상장폐지 연구는 비자발적 상폐 주변에서 매우 큰 음(-)의 수익 충격을 보고했고, KIND/FSS는 상장폐지와 정리매매 상태를 공식적으로 구분해 제공한다. citeturn32search6turn13search0turn25search1

**명시적 답변**

- **delisted names / delisting dates를 잡을 수 있는가?**  
  **Yes.** KIND 상장폐지현황과 관련 시장조치 화면으로 가능하다. citeturn13search0turn13search9
- **final trade price를 항상 잡을 수 있는가?**  
  **Not always automatically.** 마지막 실제 거래가는 KRX 일별 price table에서 잡을 수 있지만, 장기정지 후 상폐, 현금합병, 청산형 case는 DART 원문과 casebook 검토가 필요하다. citeturn20view0turn25search1turn26search0
- **suspended-before-delisting는 어떻게 처리해야 하는가?**  
  마지막 거래일 이후 delist date 전 구간을 “non-tradable suspended state”로 보존하고, exit economics는 case type별로 계산해야 한다. forward-fill된 가격으로 거래 가능하다고 가정하면 안 된다. citeturn14search0turn25search1
- **post-delisting return을 exact하게 못 잡으면 근사할 수 있는가?**  
  **감도분석(sensitivity band)**에서는 가능하지만, **주요 연구 패널의 공식 return series로는 금지**하는 것이 안전하다. 특히 bankruptcy/liquidation형 case의 -100% 근사는 보조 시나리오일 뿐 truth가 아니다. citeturn32search6turn13search0
- **alpha research가 delisting-safe data 없이 진행 가능한가?**  
  **No.** 최소한 delisting-safe master, final tradable day, case-type tagging, approximation 여부 flag가 acceptance test를 통과해야 한다. citeturn32search6turn13search0turn14search0

| Issue | Source candidate | What must be captured | How it affects backtest | How to test it | Status |
|---|---|---|---|---|---|
| Delisted names | SR-H | all historical delisted issuers | survivorship bias 제거 | historical name-presence audit | **Lock now** |
| Delisting dates | SR-H | official delist effective date | last eligibility date 결정 | delist date vs last listed day test | **Lock now** |
| Final trade price | SR-A + SR-H | last actual traded close / liquidation market price | terminal return | last-price completeness test | **Provisional** |
| Suspended-before-delisting | SR-I + SR-H + SR-N | halt interval, whether resumption occurred | stale-price tradability 오류 방지 | halted-delist casebook test | **Provisional** |
| Merger / acquisition delisting | SR-M + SR-N + SR-H | cash/stock consideration, ratio, effective date | exit return mismeasurement | merger consideration reconciliation | **Provisional** |
| Liquidation / bankruptcy | SR-N + SR-H | liquidation terms, residual payout if any | severe tail return distortion | bankruptcy casebook test | **Provisional** |
| Post-delisting price path | Derived | zero-after-exit only if event economics settled | incorrect carry returns | post-delist no-trade test | **Provisional** |
| Approximation flag | Derived | exact vs approximated exit mark | research contamination control | approximation share report | **Lock now** |
| Alpha research gate | Acceptance layer | delisting-safe panel required | prevents false alpha | pre-alpha gate test | **Lock now** |

### Fundamentals and filing timestamp architecture

OpenDART는 **무료 fundamentals floor로는 충분하다**. 이유는 `list.json`이 **접수일자(rcept_dt)**와 **정정 포함/최종보고서 필터(last_reprt_at)**를 제공하고, 재무 API가 `rcept_no`, `stock_code`, `reprt_code`, `fs_div`를 제공하기 때문이다. 즉, **filing-timestamp-aware as-reported panel**을 만드는 데 필요한 최소한의 기둥은 있다. citeturn12search0turn11search9turn12search5

| Data requirement | Source candidate | Machine-readable? | Since when available? | PIT timestamp available? | Restatement risk | Release-lag handling | Mapping to listed securities | Required cleaning | Status |
|---|---|---|---|---|---|---|---|---|---|
| Financial statements | SR-L | Yes | OpenDART API 2020-, underlying DART history older | Partial | Yes | must join to filing table | stock_code, corp_code | unit/sign/account normalization | **Lock now** |
| Annual reports | SR-K, SR-N | Yes | DART history older; API current | Yes | Yes | use rcept_dt | corp_code | final/non-final separation | **Lock now** |
| Quarterly / semiannual reports | SR-K, SR-N | Yes | DART history older; API current | Yes | Yes | use rcept_dt | corp_code | report-code normalization | **Lock now** |
| Filing date | SR-K | Yes | current guide | Yes | Low | native field | corp_code | none | **Lock now** |
| Receipt date / filing timestamp | SR-K | Yes | current guide | Yes | Low | native field | corp_code | timezone normalization | **Lock now** |
| Amended filings | SR-K, SR-N | Yes | current guide | Yes | High | ingest all with last_reprt_at=N | rcept_no chain | amendment lineage table | **Lock now** |
| Consolidated vs separate | SR-L | Yes | current guide | via filing join | Medium | native `fs_div` | stock_code | choose policy by feature family | **Lock now** |
| Fiscal period end date | SR-L | Yes | current guide | Yes via report data | Low | native field | stock_code | period-end standardization | **Lock now** |
| Announcement date vs filing date | SR-K, SR-N, SR-I (IR schedule only as auxiliary) | Partial | Unknown | filing timestamp Yes; separate announce timestamp not standardized | Medium | treat filing date as minimum safe timestamp | mixed | separate event table if found | **Provisional** |
| Earnings announcement dates separately | SR-I IR schedule, vendor candidates | Partial / Unknown | Unknown | Not consistently confirmed | High | cannot lock | issuer mapping required | manual/vendor validation | **Do not lock yet** |
| Industry / sector classification history | SR-B current menus, SR-J caveat, vendor candidates | Partial | Unknown | PIT history not confirmed | Medium | no safe free history confirmed | issue-level mapping | historical classification table needed | **Requires vendor confirmation** |

**명시적 답변**

- **OpenDART가 free fundamentals floor로 충분한가?**  
  **Yes.** periodic filings, receipt dates, amendments, consolidated/separate flags, financial statements, stock-code linkage에 대해서는 충분하다. citeturn12search0turn11search9turn12search5
- **OpenDART가 해결하지 못하는 것은 무엇인가?**  
  separate earnings announcement date의 표준화, PIT sector/industry history, prebuilt adjusted share/corporate-action history, delisting return normalization, vendor-grade cross-source cleaning은 해결하지 못한다. citeturn33search1turn26search0turn13search0
- **언제 paid vendor가 필요한가?**  
  DR-3 이후 production-grade research 운영에서 **standardized point-in-time panel**, **historical sector taxonomy**, **event date enrichment**, **secondary validation**이 필요할 때다. FnGuide/Bloomberg 계열은 이 단계의 후보로는 적절하다. citeturn42search0turn42search5turn42search2turn42search15

### Liquidity / Tradability Dataset

KOSPI200 + KOSDAQ150 + liquidity filter를 **look-ahead bias 없이** 구현하려면, 단순히 현재 구성종목과 평균 거래대금만 있으면 안 된다. 필요한 것은 **(a) PIT membership**, **(b) daily raw price/value/volume**, **(c) daily shares/market cap**, **(d) halt/admin/warning/delist flags**, **(e) rolling-window trading-day counts**, 그리고 **(f) 2025-03-04 이후 execution regime flag**다. citeturn20view0turn14search0turn14search6turn13search0turn27search11turn27search1

| Filter candidate | Data required | PIT risk | Source candidate | Implementation difficulty | Risk of look-ahead | Recommended treatment |
|---|---|---|---|---|---|---|
| ADV | rolling traded value / volume | using future window | SR-A | Low | High if centered window | **Use**, trailing-only |
| Median daily value traded | daily traded_value rolling median | future data leakage | SR-A | Low | High if not lagged | **Use**, trailing-only |
| Turnover | traded_value / lagged market cap or volume / lagged shares | same-day shares change around CA | SR-A + derived | Medium | Medium | **Use with caution** |
| Market cap | daily market_cap | daily shares update timing | SR-A | Low | Low | **Use** |
| Price filter | lagged close | split day mechanical distortions | SR-A + derived adj flags | Low | Medium | **Use with caution** |
| Trading days count | count of non-halt tradable days in trailing window | holiday/halt confusion | SR-A + SR-I | Medium | Medium | **Use** |
| Suspension days | halt interval count | incomplete halt stitching | SR-I | Medium | Low | **Use** |
| Free float, if available | PIT free-float factor/history | public daily history not confirmed | SR-F + vendor candidates | High | Medium | **Provisional** |
| Bid-ask spread, if available | quote or effective spread | official free historical depth not confirmed | broker/vendor / KRX paid | High | Medium | **Provisional** |
| KRX+NXT combined volume | venue-level daily volume sum | eligible universe/time mismatch | SR-Q + SR-A | Medium-High | Medium | **Provisional** |
| Illiquid / 관리종목 exclusion | admin / warning / halt flags | designation effective date misuse | SR-I | Low | Low | **Use** |
| Delisting-warning exclusion | admin / delist review / warning flags | inconsistent taxonomy across screens | SR-I + SR-H | Medium | Low | **Use with caution** |

**실무 해석**

- **수치 임계값(threshold)**은 아직 잠그면 안 된다. rolling window 길이, ADV floor, price floor, turnover floor는 DR-3에서 empirical validation 후 잠가야 한다. 이 보고서에서는 **Provisional**이 맞다. citeturn20view0turn14search0turn14search6
- **관리종목, 투자주의환기, 장기정지, 상장폐지 review 대상**은 유동성 필터 이전에 **structural exclusion layer**로 분리하는 것이 좋다. 이들은 단순 slippage 문제가 아니라 tradability state 문제이기 때문이다. citeturn14search6turn14search2turn14search0
- **NXT 거래 개시 이후**에는 Research scenario를 최소 두 개로 분리해야 한다. `KRX-only`와 `SOR-enabled`. NXT의 eligible securities history가 확정되지 않으면 Phase 1 baseline은 KRX-only로 두는 편이 더 보수적이다. citeturn27search11turn27search1turn29search2

### NXT / SOR / Venue Data Implications

NXT는 2025-03-04부터 개시되었고, 공식 사이트는 **매매체결대상종목**, **일별거래현황**, **참여증권사**, **거래시간**을 구분해 제공한다. 또한 브로커 최선집행 문서는 주문이 KRX와 NXT 사이에서 SOR 기준으로 집행될 수 있다고 명시하므로, **execution-regime metadata를 generic slippage 안에 숨기면 안 된다.** citeturn27search11turn27search1turn27search9turn29search0turn29search2

| Data field | Why it matters | Official or broker source candidate | Required for backtest? | Required for paper/live reconciliation? | Unknowns | Status |
|---|---|---|---|---|---|---|
| KRX-only vs SOR-enabled scenario flag | research and execution regime 분리 | Derived + SR-Q + SR-R | Yes | Yes | none | **Lock now** |
| NXT-eligible universe through time | 어떤 종목이 NXT에서 거래 가능했는지 판정 | SR-Q | If SOR backtest, Yes | Yes | historical export completeness Unknown | **Requires vendor or broker confirmation** |
| Venue-level volume | route-aware capacity / slippage | SR-Q + KRX venue data | No for KRX-only baseline | Yes | cross-venue join design | **Provisional** |
| Venue-level fees | route selection economics | broker docs / venue fee schedule | No for baseline | Yes | broker pass-through fee logic | **Requires vendor or broker confirmation** |
| Venue-level fill tag | actual execution venue attribution | SR-R broker fill logs | No | Yes | field naming broker-specific | **Requires vendor or broker confirmation** |
| Order timestamp | audit trail / latency buckets | SR-R | No | Yes | broker API granularity | **Requires vendor or broker confirmation** |
| Fill timestamp | partial fill and venue sequencing | SR-R | No | Yes | timestamp timezone/ms precision | **Requires vendor or broker confirmation** |
| Partial fill status | execution reconciliation | SR-R | No | Yes | schema broker-specific | **Requires vendor or broker confirmation** |
| Broker routing logic | SOR simulation scope | SR-R | Only for SOR scenario | Yes | exact decision hierarchy proprietary | **Requires vendor or broker confirmation** |
| Best-execution report | governance / post-trade audit | broker docs, compliance reports | No | Yes | availability and retention | **Requires vendor or broker confirmation** |

## 데이터 승인 테스트와 블루프린트

### Data Acceptance Test Suite

아래 테스트는 **alpha research 시작 전 필수 게이트**다. 실패 시 “나중에 고치기”가 아니라, 실패 원인별로 **research block**, **symbol quarantine**, **event-case manual review** 중 하나로 즉시 조치해야 한다. citeturn20view0turn35search0turn12search0turn15search9turn13search0

| Test ID | Test name | Purpose | Input data | Pass condition | Failure action | Blocking severity |
|---|---|---|---|---|---|---|
| T-PTM | PIT membership replay | 지수 편입/편출 이벤트 재생 검증 | SR-C notices + replayed membership | 모든 effective date change가 replay와 일치 | research block | Critical |
| T-NFC | No future constituents | 미래 constituent leakage 방지 | membership table | 편입일 이전에 신규 편입 종목이 절대 나타나지 않음 | research block | Critical |
| T-NFF | No future fundamentals | 미래 공시 정보 누수 방지 | filing table + fundamentals table | feature availability date ≥ safe filing timestamp | research block | Critical |
| T-FLG | Filing lag integrity | receipt-date lag 처리 검증 | SR-K filing metadata | filing lag rule 위반 0건 | research block | Critical |
| T-CAF | Corporate action factor reconciliation | split/reverse/bonus/rights factor chain 검증 | price raw + CA ledger | event day gaps가 factor chain으로 설명 가능 | symbol quarantine + manual case | Critical |
| T-DIV | Dividend reconciliation | dividend cash leg와 TR 일치 검증 | SR-P/SR-J + TR series | ex-date cash adjustment와 TR jump 일치 | research block | Critical |
| T-DLS | Delisting coverage | delisted names 포함 여부 검증 | master + price + SR-H | delisted issuer 누락 0건 | research block | Critical |
| T-SHD | Suspension / halt handling | 거래정지 중 거래가능 가정 방지 | status table + prices | halt day는 tradable=false, missing reason 일관 | research block | Critical |
| T-CAL | Trading calendar consistency | 휴장일/영업일 일관성 검증 | prices + market calendar | 모든 non-trade day가 holiday/halt로 설명됨 | table rebuild | High |
| T-MOH | Missing OHLCV check | ingest failure 탐지 | raw daily prices | unexplained null/duplicate rows 0건 | pipeline rerun | High |
| T-ARD | Abnormal return / split detection | 미반영 split/rights 탐지 | returns + CA ledger | 사전 정의된 outlier가 casebook로 설명됨 | symbol quarantine | High |
| T-DUP | Duplicate ticker / code mapping | code remap 오류 탐지 | security master | one day one instrument one row | master rebuild | Critical |
| T-BMK | Benchmark replication sanity | KRX300 benchmark replay 품질 확인 | self-built benchmark + official index series | 허용오차 내 추적 | keep benchmark provisional | High |
| T-CTR | Self-built cap-weight TR sanity | internal fallback benchmark 품질 확인 | price + dividend + shares | 허용오차 내 재현 | keep fallback provisional | High |
| T-LIQ | Liquidity filter lag test | rolling liquidity look-ahead 방지 | liquidity table | centered/future window 사용 0건 | research block | Critical |
| T-VSN | Data version lineage | audit / reproducibility | raw snapshot metadata | raw-to-derived lineage 100% 추적 가능 | pipeline freeze | High |

### KR Data Architecture Blueprint v0.1

| Layer | Purpose | Required tables | Primary keys | Timestamp rule | Main risk | Status |
|---|---|---|---|---|---|---|
| Raw source layer | 공식 원천 데이터 immutable 저장 | raw_krx_prices, raw_krx_basic, raw_kind_events, raw_dart_filings, raw_seibro_events, raw_nxt_stats | source_name, raw_file_id, ingest_ts | source-native timestamp 보존 | overwrite / provenance 손실 | **Lock now** |
| Ingestion layer | parsing / schema capture | ingest_manifest, parse_log, source_schema_version | source_name, batch_id | ingest_ts | silent schema drift | **Lock now** |
| Normalization layer | 공통 형식 정규화 | norm_prices, norm_events, norm_filings | instrument_id, trade_date / event_id | KST normalized | locale/unit mismatch | **Lock now** |
| Security master | 안정적 instrument identity | dim_instrument, map_code, map_corp, map_isin | instrument_id | effective_start/end date | code-change discontinuity | **Lock now** |
| Corporate action table | splits/rights/bonus/merger/dividend ledger | fact_corporate_action, fact_dividend | instrument_id, event_date, event_type | event effective date + source filing ts | incomplete event capture | **Provisional** |
| PIT membership table | benchmark/universe as-of membership | pit_membership_benchmark, pit_membership_research | universe_id, instrument_id, asof_date | effective date only; no backfill overwrite | missed special notice | **Lock now** |
| Price table | raw EOD tradable series | fact_price_raw | instrument_id, trade_date | trade_date KST | missing/halt confusion | **Lock now** |
| Adjusted return table | adjusted close / TR derived layer | fact_price_adjusted, fact_total_return | instrument_id, trade_date | derived after CA/div check | bad factor chain | **Provisional** |
| Fundamentals table | as-reported / latest-known financials | fact_fundamental_asreported, fact_fundamental_latest | instrument_id, fiscal_period_end, rcept_no | filing receipt timestamp governs availability | restatement leakage | **Lock now** |
| Event timestamp table | filing / listing / delist / halt / venue 시간축 | fact_event_timestamp | event_id | source-native ts + KST normalized | mixed event semantics | **Lock now** |
| Liquidity / tradability table | universe filter inputs | fact_liquidity_daily, fact_tradability_state | instrument_id, trade_date | trailing-only windows | look-ahead in rolling stats | **Provisional** |
| Feature-ready panel | research consumption table | panel_equity_daily | instrument_id, trade_date, panel_version | asof_date = trade_date close + approved lag | hidden future data | **Provisional** |
| Data quality / acceptance layer | gatekeeping and quarantine | dq_test_run, dq_issue, quarantine_symbol | test_id, run_id | test_run_ts | ignored failures | **Lock now** |
| Versioning / audit log | reproducibility | data_release, lineage_map, audit_log | release_id | immutable release timestamp | unreproducible backtest | **Lock now** |

이 blueprint의 핵심은 **raw / normalized / derived / feature-ready**를 엄격히 분리하는 것이다. 특히 **adjusted returns는 derived**, **fundamentals는 as-reported와 latest-known을 분리**, **membership은 benchmark와 research universe를 분리**해야 한다. 이 분리를 해두면 DR-3에서 어떤 acceptance test가 실패했는지 계층별로 바로 역추적할 수 있다. citeturn20view0turn12search0turn35search0

## 잠금 판정과 권고 및 핸드오프

### DR-2A Lock Decision Table

| Item | Status | Rationale |
|---|---|---|
| KOSPI200 membership PIT reconstruction | **Lock now** | official rebalancing/special notices + methodology + constituent snapshots로 구현 가능 |
| KOSDAQ150 membership PIT reconstruction | **Lock now** | official notices와 특례 규칙이 공개되어 있음 |
| KRX300 membership PIT reconstruction | **Lock now** | benchmark용 membership replay 가능 |
| KOSPI200 + KOSDAQ150 combined universe | **Lock now** | 두 PIT membership의 union으로 가능 |
| custom liquidity-filtered universe | **Lock now** | base union + daily tradability facts로 구현 가능; threshold는 별도 |
| price data | **Lock now** | KRX official daily price/basic data 확보 가능 |
| adjusted / unadjusted prices | **Provisional** | unadjusted는 확실, adjusted는 self-built factor chain 검증 필요 |
| dividends | **Provisional** | official sources 존재하나 PIT reconciliation 필요 |
| corporate actions | **Provisional** | 공식 소스는 분산돼 있어 normalization patch 필요 |
| delisting / survivorship handling | **Provisional** | framework 가능, exact exit economics는 casebook 검증 필요 |
| OpenDART fundamentals | **Lock now** | free fundamentals floor로 충분 |
| filing timestamps | **Lock now** | rcept_dt / rcept_no 기반 PIT 게이트 가능 |
| earnings announcement dates | **Do not lock yet** | separate standardized field 공개 확인 부족 |
| sector / industry history | **Requires vendor or broker confirmation** | PIT historical taxonomy free/official 완결 확인 부족 |
| halt / suspension handling | **Provisional** | official events 존재하나 stitching 검증 필요 |
| NXT-eligible universe through time | **Requires vendor or broker confirmation** | 공개 공식 history export completeness 미확인 |
| venue-level fill data | **Requires vendor or broker confirmation** | broker별 공개 schema 불완전 |
| broker routing metadata | **Requires vendor or broker confirmation** | SOR decision logs와 field definitions broker-specific |
| self-built cap-weight TR benchmark input data | **Provisional** | input sources는 있으나 dividend/CA reconciliation 후 확정 가능 |

### Recommendation

**선택:** **Split KR into free-official prototype and paid-vendor production track**

- 공식 무료 스택만으로도 **KR data prototype**은 즉시 시작할 수 있다. raw price/basic/membership/filing timestamps/listing-delisting/halt는 공식 소스로 닫힌다. citeturn20view0turn35search0turn13search0turn12search0
- 다만 **alpha baseline은 patches 이후**여야 한다. adjusted return, dividend, corporate action, delisting-safe protocol이 acceptance tests를 통과하기 전에는 열지 않는다. citeturn15search9turn26search0turn32search6
- production track에서는 **vendor/broker confirmation**을 병행한다. priority는 PIT sector history, separate earnings date, NXT eligible history, venue fill/routing metadata다. citeturn33search1turn27search1turn29search0turn29search2
- benchmark는 KRX300/KTX300 TR 후보를 유지하되, 내부 self-built cap-weight TR은 **control/fallback**로만 두고 DR-3에서 sanity check를 통과할 때까지 Provisional로 유지한다. citeturn39search4turn20view0turn33search1
- 공개 공식 문서만으로 **Refinitiv/FactSet/S&P의 KR-specific PIT 세부**, 그리고 **broker fill schema의 완전 공개 명세**는 이번 패스에서 확정하지 못했다. 따라서 이 영역은 보수적으로 confirmation 상태를 유지한다. 

### Next Research Handoff

**DR-3 Validation Protocol handoff 문안**

> **DR-3 범위:**  
> KR Phase 1 PIT panel의 실제 검증.  
>   
> **검증 대상:**  
> KOSPI200, KOSDAQ150, KRX300의 2010-현재 membership replay,  
> KOSPI200+KOSDAQ150 research universe union,  
> official raw price/basic tables,  
> KIND listing/delisting/halt/admin state,  
> OpenDART filing timestamp/fundamentals,  
> SEIBro/KIND/DART 기반 dividend/CA ledger.  
>   
> **필수 구현물:**  
> `dim_instrument`, `fact_price_raw`, `fact_corporate_action`, `fact_dividend`, `fact_fundamental_asreported`, `pit_membership_benchmark`, `pit_membership_research`, `fact_tradability_state`, `panel_equity_daily`, `dq_test_run`.  
>   
> **필수 테스트:**  
> T-PTM, T-NFC, T-NFF, T-FLG, T-CAF, T-DIV, T-DLS, T-SHD, T-CAL, T-MOH, T-ARD, T-DUP, T-BMK, T-CTR, T-LIQ, T-VSN 전부 구현.  
>   
> **케이스북 샘플링:**  
> 신규상장 특례, 기업분할, 무상증자, 유상증자, 합병상폐, 장기정지 후 상폐, 코스닥→코스피 이전상장, 관리종목 지정/해제, 투자주의환기 지정/해제 각각 최소 5건 이상.  
>   
> **DR-3 성공 기준:**  
> alpha modeling 이전에 panel release 후보 1개가 모든 Critical test를 통과하고, benchmark replication과 dividend/CA reconciliation이 사전 정의 tolerance 내에 들어올 것.  
>   
> **DR-3 종료 시 의사결정:**  
> `PATCH-BEFORE-ALPHA → GO` 전환 여부,  
> 또는 `paid vendor / broker confirmation` 추가 요구 여부를 최종 판정할 것.