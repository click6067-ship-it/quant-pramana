# DR-1A KR Official Source Gap Lock

## 연구 계획

- KRX, KRX Data Marketplace, KIND, KSD SEIBro, 법령정보센터, 한국은행, 공식 브로커 문서, 공식 벤더 문서만 우선 사용해 KR 벤치마크·유니버스·세금·수수료·실행·데이터 가용성의 **잠금 가능성**만 판정합니다.
- **KRX300 / KRX300 TR**는 공개 방법론 채널 존재 여부, TR 버전의 공식 공개 여부, 공시 가능한 히스토리 길이, 정기변경 규칙 노출 수준을 분리해서 검증합니다.
- **KOSPI200 / KOSDAQ150**는 단일 벤치마크가 아니라 후보 **연구 유니버스(universe)** 로 보고, 구성종목 정기변경 공지와 PIT(point-in-time) 복원 가능성을 우선 확인합니다.
- **한국 거래세·거래소/venue 수수료·브로커 수수료**는 법률/공식 수수료표와 브로커별 적용치를 분리해서 기록하고, 공식 확인이 안 되는 수치에는 `Unknown` 또는 `Requires broker/vendor confirmation`만 부여합니다.
- **NXT / ATS / SOR**는 일반 슬리피지 항목으로 뭉개지지 않도록, KRX-only, NXT-direct, SOR-enabled를 별도 실행 체계로 분리해야 하는지 공식 최선집행 문서로 검증합니다.
- **Korean PIT constituents, delisting, corporate actions, dividends, fundamentals**는 무료 공식 소스만으로 가능한 범위와, 유료 벤더가 사실상 필요한 구간을 구분합니다.
- 최종적으로 각 핵심 가정을 **Lock now / Provisional / Do not lock yet / Requires broker/vendor confirmation** 네 상태 중 하나로 강제 분류합니다.

## 핵심 판정

### Executive Decision Summary

- **KRX300 외부 벤치마크**: **Provisional**, 신뢰도 **Medium**. KRX300은 공식적으로 KOSPI+KOSDAQ 300종목 통합 대표지수로 확인되고, ETF로 구현 가능하지만, 본 라운드에서는 최신 공식 방법론 PDF와 TR 쌍(series pair)까지는 잠그지 못했습니다. citeturn45search11turn45search19turn35search7turn43view0
- **KRX300 TR**: **Do not lock yet**, 신뢰도 **Low**. KRX 공공 노출 메뉴와 공개 검색 결과에서는 KRX300 PR은 반복적으로 확인되지만, KRX300 TR의 공식 공개 페이지·방법론·장기 히스토리는 이번 조사에서 식별되지 않았습니다. citeturn35search0turn35search1turn36search3turn36search6turn35search2turn36search11
- **KOSPI200 + KOSDAQ150 + liquidity filter 연구 유니버스**: **Provisional**, 신뢰도 **Medium-High**. 두 지수 모두 공식 정기변경 공지가 있고, KOSDAQ150의 선별 규칙 요약도 공식 문서에서 확인되지만, “기간 전체 PIT 구성종목 다운로드 경로”는 추가 확인이 필요합니다. citeturn35search7turn45search6turn47search3turn45search2
- **self-built cap-weight TR benchmark**: **Provisional**, 신뢰도 **Medium**. KRX 시세, KIND 상장/상폐, SEIBro 배당·권리일정을 결합하면 공학적으로 구축은 가능하지만, 최종 외부 벤치마크로 쓰면 “benchmark–universe separation”을 훼손할 수 있어 내부 통제용 fallback으로만 잠정 수용하는 편이 안전합니다. citeturn35search0turn35search1turn38search1turn38search4turn37search1turn37search9
- **한국 거래세**: **Provisional**, 신뢰도 **Medium**. 현행 시행령의 상장주권 세율표는 공식 확인되지만, 실제 고객 명세서상 시장별 총매도세 분해는 이번 라운드에서 완전 잠금하지 못했습니다. citeturn16search5
- **브로커 수수료**: **Requires broker/vendor confirmation**, 신뢰도 **High**. 공식 최선집행 문서상 수수료는 라우팅 판단의 일부이며, 실제 고객 적용 수수료는 브로커·채널·이벤트에 따라 달라질 수 있습니다. citeturn40search2turn40search5turn41view0
- **NXT / SOR 실행 모델**: **Lock now**, 신뢰도 **High**. 2025-03-04 이후 복수시장 체제가 도입되었고, SOR은 KRX/NXT 통합호가와 비용·체결가능성을 반영하며 주문을 분할 전송할 수 있으므로, 일반 슬리피지 한 줄로 숨기면 안 됩니다. citeturn40search12turn40search2turn41view2turn40search19
- **KR PIT constituents + delisting + corporate actions**: **Provisional**, 신뢰도 **Medium**. 공식 building block은 충분합니다. KRX 주가지수 공지, KIND 상장폐지/신규상장, SEIBro 배당·권리일정이 각각 존재합니다. 다만 “자동화된 PIT 패널 조립”은 검증이 더 필요합니다. citeturn35search7turn46search3turn38search1turn38search4turn37search1turn37search6turn37search9
- **KR PIT fundamentals**: **Do not lock yet**, 신뢰도 **Medium**. 공식 공시 원천은 존재하지만, 무료 공식 스택만으로 정규화된 as-reported PIT 펀더멘털 패널을 바로 쓸 수 있는지는 잠기지 않았고, 유료 벤더 사용 가능성이 높습니다. citeturn34search6turn34search7turn35search16
- **KR filing / earnings dates**: **Requires broker/vendor confirmation**, 신뢰도 **Medium**. 공시·IR 플랫폼은 존재하지만, 알파 리서치용 event file 수준의 필드 매핑과 PIT 청결성은 이번 라운드에서 잠기지 않았습니다. citeturn45search20turn46search9turn34search6

## 출처와 벤치마크

### Official Source Register

| Source | Institution | Source type | What it supports | Date or latest version | Access date | Reliability | Notes |
|---|---|---|---|---|---|---|---|
| KRX Data Marketplace 메인/지수 메뉴 citeturn35search0turn35search1turn36search3 | KRX | 공식 데이터 포털 | KRX300, KOSPI, KOSPI200 등 공식 노출 지수와 지수 통계 화면 존재 | 실시간 화면 | 2026-06-07 | High | 공개 메뉴 기준으로 PR 지수는 명확히 확인되나, KRX300 TR은 본 조사에서 식별 실패 |
| 주가지수 공지 게시판 citeturn35search7turn45search6turn46search3 | KRX | 공식 공지 | KOSPI200, KOSDAQ150, KRX300 구성종목 정기변경 | 2021-05-25, 2022-12, 2021-06 등 | 2026-06-07 | High | PIT membership 복원의 핵심 building block |
| Global KRX Publication 메뉴 citeturn43view0turn49search0 | KRX | 공식 글로벌 포털 | Index Methodology / Factsheet/Constituents 공식 채널 존재 | 메뉴 페이지, undated | 2026-06-07 | High | 채널 존재는 확인됐지만 직접 문서 잠금은 이번 라운드에서 미완료 |
| 상장폐지현황 citeturn38search1 | KIND / KRX | 공식 이벤트 페이지 | 상장폐지 이벤트, 투자유의 상태 | 실시간 화면 | 2026-06-07 | High | delisting / survivorship 처리의 핵심 |
| 신규상장기업현황 / 상장종목현황 citeturn38search4turn38search5 | KIND / KRX | 공식 통계/현황 페이지 | 신규상장, 상장종목 상태, 시장 breadth | 실시간 화면 | 2026-06-07 | High | listing / active universe 복원에 필요 |
| SEIBro 배당·권리일정·대금지급일정 citeturn37search1turn37search3turn37search6turn37search9turn37search10 | KSD | 공식 증권정보 포털 | 배당, 권리일정, 지급일, corporate actions building block | 실시간 화면 | 2026-06-07 | High | self-built TR / corp action 엔지니어링의 핵심 |
| 증권거래세법 시행령 세율표 citeturn16search5 | 국가법령정보센터 | 공식 법령 | 거래세 세율 테이블 | 시행 2026-01-02 표출 | 2026-06-07 | Highest | 법률 레벨 근거 |
| 최선집행기준 설명서 / 안내 citeturn40search1turn40search2turn40search5turn40search7turn41view0turn41view2 | 한국투자증권, 카카오페이증권, 미래에셋증권 | 공식 브로커 문서 | KRX/NXT 통합호가, 비용 고려, SOR opt-out, 주문 분할/전환 | 2025-02 ~ 2025-12 | 2026-06-07 | High | 실행 모델 잠금의 핵심 근거 |
| 넥스트레이드 출범 공지 citeturn40search12 | 유안타증권 | 공식 브로커 공지 | 2025-03-04 NXT 출범 및 복수시장 체제 | 2025-02-13 | 2026-06-07 | High | 제도 전환 시점 확인용 |
| BOK Exchange Rate System citeturn39search1 | Bank of Korea | 공식 설명 페이지 | 고객 환율은 각 은행이 interbank를 참고해 결정 | undated official page | 2026-06-07 | High | FX cost는 broker/bank-specific임을 뒷받침 |
| FnSpace / QuantiWise 공식 페이지 citeturn34search6turn34search7 | FnGuide | 공식 벤더 문서 | API 제공, 시계열 데이터/이벤트형 데이터 서비스 존재 | 2024-10 공지, 서비스 페이지 | 2026-06-07 | Medium-High | PIT fundamentals/event vendor 필요성 판단용 |
| 공식 ETF 상품 페이지 citeturn45search11turn45search15turn45search19turn47search4 | KB/NH-Amundi/SOL/삼성자산운용 | 공식 운용사 페이지 | KRX300, KOSDAQ150 등 지수의 investability·replicability | 실시간 상품 페이지 | 2026-06-07 | High | methodology 자체보다는 investability 근거 |

이번 라운드에서 가장 강한 공식 근거는 **KRX 공지·KIND 이벤트·SEIBro 권리정보·법령정보센터·브로커 최선집행 문서**였습니다. 반대로 **KRX300 TR의 공식 공개 산출물**, **브로커 실제 적용 수수료표의 일관된 잠금**, **무료 공식 소스만으로 바로 쓸 수 있는 PIT fundamentals/event file**은 끝까지 잠기지 않았습니다. citeturn35search7turn38search1turn37search1turn16search5turn41view2turn34search6

### KR Benchmark Evidence Matrix

| Candidate | Official methodology available? | Total-return version available? | Public history length known? | Universe represented | Rebalance / review rules | Investability / replicability | Fit with KOSPI200 + KOSDAQ150 trading universe | Main mismatch risk | Recommended treatment |
|---|---|---|---|---|---|---|---|---|---|
| KRX300 | 공식 방법론 채널은 존재 확인, 직접 방법론 문서는 이번 라운드에서 미잠금 citeturn43view0turn49search0 | **Unknown**; 공식 공개 KRX300 TR 페이지/시계열 미식별 citeturn35search0turn35search1turn36search3turn36search6 | 2018년 초부터 공개 사용 흔적 확인 가능, 정확한 공식 inception 문서 미잠금 citeturn46search1turn46search5turn45search15 | KOSPI·KOSDAQ 통합 300종목, 섹터별 선별 citeturn45search11turn45search19 | 정기변경은 공식 공지로 반복 확인 citeturn35search7turn45search6turn46search3 | ETF로 구현 가능 citeturn45search15turn45search19turn45search11 | 높음 | PR만 잠그면 after-dividend 비교에서 왜곡 가능 | **Provisional** |
| KRX300 TR | **Unknown**; 공식 공개 방법론 미식별 citeturn35search0turn36search6 | 공식 공개 존재 여부 자체가 미잠금 citeturn35search0turn35search1turn36search3turn36search6 | **Unknown** | 개념상 KRX300과 동일일 가능성 있으나 공식 확인 미완료 | **Unknown** | 공식 series 미잠금으로 재현성 낮음 | 개념상 높음 | 시계열·방법론·배당처리 모두 미잠금 | **Do not lock yet** |
| KOSPI200 | 장기 사용 지수는 공식 확인되나, 최신 방법론 PDF는 이번 라운드에서 직접 확보 못함; 공식 정기변경 공지는 확인 citeturn45search2turn35search7 | 이번 라운드에서 **Unknown** | 1994-06-15부터 산출·발표 확인 citeturn45search2turn45search5turn45search13 | KOSPI 대형주 중심 | 정기변경 공식 공지 확인 citeturn35search7turn45search6 | 매우 높음; 파생/운용상품 기반 강함 citeturn42search1turn45search2 | 중간 | KOSDAQ sleeve 부재 | **Reject** as sole KR benchmark |
| KOSDAQ150 | 공식 선별 규칙 요약은 확보, 최신 방법론 PDF는 직접 미잠금 citeturn47search3 | 이번 라운드에서 **Unknown** | 2015년 도입·공개 상품 존재 확인 citeturn47search0turn47search1 | KOSDAQ 대표 150, 기술주 섹터 중점 citeturn47search3 | 정기변경 공식 공지 확인 citeturn35search7turn45search6 | 높음; ETF/파생 존재 citeturn47search0turn42search1 | 중간 | KOSPI sleeve 부재 | **Reject** as sole KR benchmark |
| KOSPI | 공식 대표 시장지수. 장기 public history는 확인 가능 citeturn48search6 | KOSPI TR 존재 흔적은 공식 ETF 공시에서 확인 citeturn35search2turn35search6turn36search11 | 1983년 1월 4일 발표 시작 근거 확인 citeturn48search6 | KOSPI 전체 | 일반 시장지수 | 높음 | 낮음~중간 | KOSDAQ 부재, breadth 과다 | **Reject** |
| KOSDAQ | 시장/지수군의 장기 공식 존재는 확인되나 exact index-history lock 미완료 citeturn42search0 | **Unknown** | 시장은 1996년 출범 citeturn42search0 | KOSDAQ 전체 | 일반 시장지수 | 중간~높음 | 낮음 | KOSPI 부재, 변동성 편향 | **Reject** |
| self-built cap-weight TR benchmark | 공식 방법론이 아니라 내부 규칙 | 구축 가능 citeturn37search1turn37search9turn38search1turn38search4 | 소스가 허용하는 만큼 가능 | 사용자가 정의 | 사용자가 정의 | 규칙 공개 시 재현 가능 | 매우 높음 | benchmark–universe separation 훼손 위험, 엔지니어링 부담 | **Provisional** as internal fallback |

핵심은 단순합니다. **외부 KR benchmark 후보로는 KRX300 PR만 provisional**, **KRX300 TR은 아직 잠그지 말아야** 합니다. **KOSPI200 / KOSDAQ150는 전체 KR benchmark라기보다 sleeve benchmark 또는 universe component**로 보는 편이 공식 근거와 운영 현실에 더 맞습니다. citeturn45search11turn35search7turn47search3turn45search2

## 유니버스와 비용

### KR Universe Evidence Matrix

| Universe | Breadth | Official membership history availability | PIT feasibility | Liquidity suitability | Survivorship / delisting risk | Corporate action handling requirement | Suitability for cross-sectional alpha research | Recommended treatment |
|---|---|---|---|---|---|---|---|---|
| KOSPI100 | 좁음 | 이번 라운드에서 full official history는 미검증 | Medium-Low | 매우 높음 | 낮지만 0은 아님 | 중간 | 중간 | **Reject** as Phase 1 core universe |
| KOSPI200 | 중간 | 정기변경 공지는 공식 확인, full downloadable PIT history는 추가 확인 필요 citeturn35search7turn45search6 | Medium | 매우 높음 | KIND 상폐/신규상장 결합 시 관리 가능 citeturn38search1turn38search4 | 중간 | 높음 | **Provisional** |
| KOSDAQ150 | 중간 | 정기변경 공지 공식 확인, 규칙 요약 확보, full PIT history 추가 확인 필요 citeturn35search7turn47search3 | Medium | 높음 | KOSDAQ 특성상 상폐·관리 risk 상대적으로 큼 citeturn38search1 | 중간~높음 | 높음 | **Provisional** |
| KOSPI200 + KOSDAQ150 | 중간~넓음 | 두 지수 공지 결합으로 부분 복원 가능, 자동화 경로는 추가 확인 필요 citeturn35search7turn45search6 | Medium | 높음 | KIND 상폐/신규상장과 결합 필요 citeturn38search1turn38search4 | 높음 | 매우 높음 | **Provisional** |
| KRX300 | 중간~넓음 | 공식 정기변경 공지 확인, 과거 전체 membership path는 추가 확인 필요 citeturn35search7turn46search3 | Medium | 높음 | 관리 가능 | 높음 | 높음 | **Do not lock yet** as core universe |
| custom liquidity-filtered KR universe | 가변 | 공식 membership history라는 개념이 없음 | Source-stack dependent | 사용자가 통제 가능 | 소스가 불완전하면 높음 | 매우 높음 | 매우 높음 | **Do not lock yet** |

연구 유니버스 관점에서는 **KOSPI200 + KOSDAQ150 + liquidity filter**가 가장 실무적입니다. 다만 이것을 **Lock now**로 올리기에는, 공식 공지 기반 membership reconstruction이 가능하다는 것과 “장기 전기간 PIT 패널을 자동으로, 누락 없이 뽑을 수 있다”는 것은 다른 문제입니다. 그래서 판정은 **Provisional**이 맞습니다. citeturn35search7turn45search6turn38search1turn38search4

### KR Cost / Tax / Fee Lock Table

| Cost item | Official source | Applies to | Current official value or status, if available | Broker-specific? | How to model in backtest | Conservative minimum assumption | Sensitivity test required | Recommended treatment |
|---|---|---|---|---|---|---|---|---|
| Securities transaction tax | 국가법령정보센터 시행령 세율표 citeturn16search5 | KR single stocks, sell-side | 상장주권 세율표는 공식 공개. 다만 실제 고객 명세서상 시장별 총매도세 분해는 이번 라운드 미잠금 | No for law / Yes for applied statement interpretation | **explicit sell-side tax bucket**로 분리 | 법령 확인 전 0 가정 금지; provisional placeholder가 필요하면 법령 확인 수치만 사용 | Yes | **Provisional** |
| Exchange / venue fees | 공식 브로커 최선집행 문서 citeturn40search2turn40search5turn41view2 | KRX/NXT execution | 비용이 최선집행 판단요소임은 공식 확인. 고객 pass-through exact rate는 이번 라운드 미잠금 | Partly | venue별 explicit fee bucket | KRX/NXT 동일·0 가정 금지 | Yes | **Requires broker confirmation** |
| Broker commission | 공식 브로커 문서 citeturn40search2turn40search5turn40search7 | All live trades | **Unknown** as universal value; broker/channel/campaign dependent | Yes | broker parameter table | 계약서/기본수수료표 확보 전 단일 상수 잠금 금지 | Yes | **Requires broker confirmation** |
| NXT / KRX venue fee differences | 최선집행 문서상 fee가 집행 판단요소로 반영 citeturn40search2turn41view0 | SOR / direct venue orders | 고객 적용 차등은 **Unknown**; 다만 venue 차이는 비용판단에 반영됨 | Yes | KRX-only / NXT-direct / SOR-enabled 별도로 분리 | non-zero scenario test | Yes | **Requires broker confirmation** |
| SOR or best-execution-related costs | 공식 최선집행 기준 설명서 citeturn40search5turn41view0turn41view2 | SOR-enabled execution | 가격·수수료·체결가능성 기준 반영, 분할전송 가능 | Yes | generic slippage가 아닌 **separate execution simulator** | SOR-disabled와 SOR-enabled 둘 다 돌리기 | Yes | **Lock separate regime now** |
| Dividend withholding / tax assumption level | 이번 라운드에서 universal official lock 미완료 | Cash dividends | **Unknown** as universal net assumption in this run | Investor-specific | gross-dividend series와 net-dividend sensitivity 분리 | universal net-dividend hard-code 금지 | Yes | **Requires broker/tax confirmation** |
| FX cost | BOK 환율제도 설명 citeturn39search1 | Non-KRW funded KR sleeve | 고객 환율은 각 은행이 독자적으로 결정, interbank 참조 | Yes | equity cost와 별도 FX spread/commission bucket | KRW 기능통화가 아니면 0 가정 금지 | Yes | **Requires broker confirmation** |
| Spread | 통합호가/가격 개념 공식 문서 citeturn40search2turn40search5 | All orders | 규정상 고정값 없음 | No | venue/time bucketed half-spread | 일정 상수보다 bucketed spread 사용 | Yes | **Provisional** |
| Slippage | 체결가능성·시장상황 반영 공식 문서 citeturn41view2turn40search0 | All orders | 규정상 고정값 없음 | No | empirical slippage by venue/time/order ratio | fixed zero 금지 | Yes | **Do not lock yet** |
| Market impact | 암묵적 비용 개념 공식 문서 citeturn40search5 | Larger orders / less liquid names | 시장충격비용은 implicit cost로 설명되나 공식 수치 없음 | No | separate impact model | scenario grid | Yes | **Do not lock yet** |
| ETF vs single stock difference | KRX regulation menu에 ETF tax regulation 섹션 존재만 확인 citeturn43view0 | ETFs vs single stocks | 이번 라운드 상세 과세 잠금 실패 | Product-specific | separate asset-class tax/fee model | single-stock tax를 ETF에 복사 금지 | Yes | **Requires confirmation** |

비용 항목에서 지금 잠글 수 있는 것은 **구조(structure)** 뿐입니다. 즉, **세금·수수료·venue fee·FX·spread/slippage/impact를 분리 모델링해야 한다**는 점은 잠글 수 있지만, **브로커 적용치**와 **SOR 반영 fees의 실제 customer pass-through**는 잠글 수 없습니다. citeturn16search5turn40search2turn41view0turn39search1

## 실행과 데이터

### NXT / ATS / SOR Execution Register

| Issue | Official source | What is known | What is unknown | Backtest implication | Paper trading implication | Broker confirmation needed? | Recommended treatment |
|---|---|---|---|---|---|---|---|
| NXT 출범과 복수시장 체제 | 유안타 공지, 브로커 최선집행 문서 citeturn40search12turn41view2 | 2025-03-04부터 NXT 출범, 복수시장 체제 도입 | 계좌/채널별 사용 가능 범위 | 2025-03-04 전후를 동일 execution regime으로 보면 안 됨 | paper도 regime flag 필요 | Yes | **Lock now** |
| SOR routing logic | 한국투자·카카오페이·미래에셋 최선집행 문서 citeturn40search2turn40search5turn40search15turn41view2 | 통합호가, 가격·비용·체결가능성 고려, 주문 분할 가능 | 세부 우선순위 weight, 내부 latency | single-venue slippage로 단순화 금지 | 주문 child-level 추적 필요 | Yes | **Lock now** |
| SOR opt-out / direct venue selection | 한국투자 문서 citeturn41view0turn41view2 | 투자자는 SOR 미사용 또는 개별 거래소 직접 선택 가능 | 브로커별 default setting | KRX-only, NXT-direct, SOR-enabled를 분리 시뮬레이션해야 함 | 실제 계정 default 확인 필요 | Yes | **Lock now** |
| Session asymmetry and residual handling | 한국투자 문서 citeturn41view2 | KRX 미체결 잔량은 취소될 수 있고, NXT 잔량은 after-market까지 유지될 수 있으며, 자동전환은 보편 규칙이 아니라 opt-in/브로커 규칙 | 브로커별 자동전환 세부조건 | close handling, carryover logic, cancel logic을 venue별로 달리 써야 함 | paper-to-live drift의 핵심 원인 | Yes | **Lock now** |
| SOR failure / fallback path | 한국투자 문서 citeturn41view2 | SOR 장애시 직접 KRX/NXT 선택 주문 필요 | 장애 시 주문로그/알림 포맷 | 장애 fallback 시나리오 필요 | paper에서 장애 처리정책 필요 | Yes | **Requires broker confirmation** |
| Venue-level fill data necessity | 위 문서들에 대한 **추론(inference)** citeturn41view2turn40search2 | 주문이 venue split될 수 있고 session handling도 다름 | 실제 broker export에 venue tag / child order ID / execution timestamp가 있는지 | venue-level fill 데이터 없으면 drift 원인분석 불가 | paper/live reconciliation 실패 가능 | Yes | **Requires broker confirmation** |

여기서 잠가야 하는 결론은 명확합니다. **NXT는 한국 주식 execution model을 바꿉니다.** 따라서 **SOR / best execution을 별도 execution regime으로 모델링해야 하고**, **KRX-only와 SOR-enabled 시나리오는 반드시 분리해야 하며**, **venue-level fill data는 paper-to-live reconciliation에 사실상 필요**합니다. 마지막 항목은 공식 문서의 주문 분할·세션 비대칭성을 바탕으로 한 추론입니다. citeturn40search12turn41view2turn40search19

### KR Data Feasibility Register

| Data requirement | Free source feasibility | Official source feasibility | Paid vendor likely needed? | PIT requirement | Blocking severity | Required before alpha research? | Notes |
|---|---|---|---|---|---|---|---|
| Daily OHLCV | Yes | Yes citeturn35search0turn35search1 | No | Medium | Low | Yes | KRX Data Marketplace로 공식 시장데이터 접근 가능 |
| Adjusted prices | Partial | Raw/official market data는 가능, clean adjusted series는 이번 라운드 미잠금 citeturn35search0turn37search9 | Likely | High | Medium | Yes | corporate actions와 결합 필요 |
| Unadjusted prices | Yes | Yes citeturn35search0turn35search1 | No | Medium | Low | Yes | 기본 시세는 공식 가능 |
| Corporate actions | Partial | Yes via SEIBro rights schedules / KIND events citeturn37search6turn37search9turn38search1 | Maybe | High | High | Yes | 정규화 작업이 필요 |
| Dividends | Yes | Yes via SEIBro / KIND dividend pages citeturn37search1turn46search9 | Maybe | High | Medium | Yes | self-built TR에 필요 |
| Delisted names / delisting events | Partial | Yes via KIND 상장폐지현황 citeturn38search1 | Likely for clean archive | High | High | Yes | delisting 이후 시세 아카이브는 추가 확인 필요 |
| Constituents through time | Partial | KRX 공지로 부분 가능, 자동화 full PIT history는 추가 확인 필요 citeturn35search7turn45search6turn46search3 | Likely | Very High | High | Yes | 핵심 blocker 중 하나 |
| KOSPI200 historical membership | Partial | 정기변경 공지 가능 citeturn35search7turn45search6 | Maybe | Very High | High | Yes | query-by-date 가능 여부 추가 확인 필요 |
| KOSDAQ150 historical membership | Partial | 정기변경 공지 및 규칙 요약 가능 citeturn35search7turn47search3 | Maybe | Very High | High | Yes | query-by-date 확인 필요 |
| KRX300 historical membership | Partial | 정기변경 공지 가능 citeturn35search7turn46search3 | Maybe | Very High | High | Yes | 공식 public history path 미잠금 |
| PIT fundamentals | Partial | 공시 원천은 있으나 정규화 PIT panel 미잠금 citeturn34search6turn34search7 | **Yes** | Very High | **Critical** | Yes | 유료 벤더 가능성 높음 |
| Filing dates | Partial | official disclosure ecosystem exists, field-level lock 미완료 citeturn45search20turn46search9 | Likely | High | Medium-High | Yes | event file 품질 확인 필요 |
| Earnings announcement dates | Partial | IR/공시로 부분 가능, standardized PIT event file 미잠금 citeturn45search20turn34search6 | **Likely** | High | High | Yes | manual parsing 부담 큼 |
| Sector / industry classification through time | Partial | current listing status는 KIND에 존재, history는 미잠금 citeturn38search5 | Likely | High | Medium | Yes | history vendor 확인 필요 |
| Trading calendar | Yes | Yes via KRX market calendar channel 존재 citeturn43view0turn49search0 | No | Medium | Low | Yes | 공식 달력 사용 가능 |
| Suspensions / trading halts | Partial | market-wide halt rules official, security-level warning/halt 채널 존재 citeturn42search1turn38search1 | Maybe | High | Medium | Yes | per-security event feed 정합성 확인 필요 |
| FX rates | Yes | Yes via BOK reference framework citeturn39search1 | No | Low | Low | No for KRW-only | 기능통화가 KRW면 blocker 아님 |
| News / filings / earnings calls later auxiliary | Partial | Not core in this round | Maybe | Low | Low | No | Phase 1 core blocker는 아님 |

데이터 측면에서 진짜 blocker는 세 가지입니다. **historical PIT constituents**, **delisting-aware panel**, **standardized PIT fundamentals / event dates**입니다. 반대로 **OHLCV, 배당, 권리일정, 상폐 이벤트의 official building block**은 이미 충분히 보입니다. citeturn35search7turn38search1turn37search1turn34search6

## 잠금 판정과 DR-1 영향

### KR Lock Decision Table

| Item | Decision | Reason | Evidence | What must be verified next | Impact on DR-2 |
|---|---|---|---|---|---|
| KRX300 | **Provisional** | 공식 cross-market benchmark이지만 TR pair와 최신 방법론 직접 잠금 미완료 | 통합 300종목 benchmark 정의, ETF investability, 정기변경 공지 citeturn45search11turn45search19turn35search7 | 최신 공식 methodology PDF / official history query path | KR benchmark 후보로만 유지 |
| KRX300 TR | **Do not lock yet** | 공식 공개 series/방법론/장기 history를 식별하지 못함 | KRX 노출 메뉴에는 PR 지수 위주, KRX300TR 공식 공개 흔적 미약 citeturn35search0turn35search1turn36search3turn36search6 | KRX 또는 vendor의 official TR document / history 확인 | KR benchmark final lock 보류 |
| KOSPI200 + KOSDAQ150 + liquidity filter | **Provisional** | 공식 index universe 기반이고 liquidity 적합성이 높지만 장기 PIT constituent path 자동화는 추가 확인 필요 | 정기변경 공지, KOSDAQ150 규칙 요약, KOSPI200 공식 history 확인 citeturn35search7turn47search3turn45search2 | query-by-date membership / vendor cross-check | KR universe candidate로 유지 |
| self-built cap-weight TR benchmark | **Provisional** | 공식 building block으로 구축 가능하나 external benchmark라기보다 fallback/internal control에 적합 | KRX prices + KIND listing/delisting + SEIBro dividends/rights citeturn35search0turn38search1turn38search4turn37search1turn37search9 | benchmark-universe separation rule에 맞는 설계 정의 | fallback benchmark only |
| KR transaction tax | **Provisional** | 법령 근거는 확인됐지만 실제 customer tax decomposition은 미잠금 | 법령 세율표 citeturn16search5 | broker tax statement로 시장별 총매도세 분해 확인 | 비용 가정은 provisional |
| broker commission | **Requires broker/vendor confirmation** | broker/channel/event-specific | 공식 브로커 최선집행 문서상 비용이 판단요소 citeturn40search2turn40search5 | 대상 브로커 약정/기본 수수료표 확보 | live cost stack 미잠금 |
| NXT/SOR model | **Lock now** | 구조적으로 execution regime가 달라짐 | NXT 출범, 복수시장, SOR 통합호가/분할전송/opt-out citeturn40search12turn41view0turn41view2 | broker별 default/로그 포맷 확인 | DR-2 execution simulator requirements 고정 |
| KR PIT constituents | **Provisional** | official notices로 부분 복원 가능하나 자동화 full panel은 미검증 | KRX 정기변경 공지 citeturn35search7turn45search6 | date-query / vendor parity 확인 | alpha research 전 추가 확인 필요 |
| KR corporate actions | **Provisional** | official rights/dividend schedules 존재 | SEIBro 권리일정/배당정보 citeturn37search1turn37search6turn37search9 | split/bonus/rights normalization workflow 검증 | 백테스트 정합성 필수 |
| KR delisting / survivorship | **Provisional** | official delisting event pages 존재하지만 clean historical panel은 별도 조립 필요 | KIND 상장폐지현황 citeturn38search1 | delisted price archive / identifier continuity 확인 | survivorship-free panel 전제 추가 |
| KR PIT fundamentals | **Do not lock yet** | 무료 공식 stack로 즉시 usable standardized PIT panel 여부 미잠금 | FnGuide vendor/API/time-series 서비스 존재 citeturn34search6turn34search7 | vendor spec / field dictionary / as-reported timing 확인 | KR alpha research blocker |
| KR filing / earnings dates | **Requires broker/vendor confirmation** | official event ecosystem은 있으나 clean event file 잠금 실패 | KIND IR schedule / official disclosure platform 흔적 citeturn45search20turn46search9 | vendor event file 또는 공식 API field mapping 검증 | event-driven validation은 pending |

이 표를 요약하면, **지금 KR에서 Lock now로 올릴 수 있는 것은 NXT/SOR를 별도 execution regime로 다뤄야 한다는 구조적 결론 하나**입니다. 나머지는 대부분 **Provisional**이거나 **Requires confirmation / Do not lock yet**입니다. citeturn41view2turn35search7turn37search1turn38search1

### Impact on DR-1 Final Lock Sheet

| Category | What should change in DR-1 | Evidence | Impact |
|---|---|---|---|
| Confirmed locks | “NXT / ATS / SOR는 generic slippage에 숨기지 말고 별도 execution regime로 모델링”을 **확정 lock**으로 승격 | 공식 최선집행 문서상 KRX/NXT 통합호가, 비용·체결가능성 고려, 분할전송, opt-out 존재 citeturn40search2turn41view0turn41view2 | KR live simulation 설계조건 고정 |
| Downgraded assumptions | “KRX300 또는 KRX300 TR을 바로 최종 benchmark로 채택” 가정은 **downgrade**. 특히 KRX300 TR은 미잠금 | KRX300 PR은 보이지만 KRX300 TR 공식 공개 시리즈는 미식별 citeturn35search0turn35search1turn36search3turn36search6 | final benchmark 미정 유지 |
| Newly added blockers | “PIT constituents 자동화 경로”, “PIT fundamentals/event dates”, “venue-tagged fill logs”를 **신규 blocker**로 명시 | KRX notices/KIND/SEIBro는 building block이지만 panel-grade automation은 별도 확인 필요 citeturn35search7turn38search1turn37search1turn34search6turn41view2 | KR alpha/paper-live 검증은 추가 조사 필요 |
| Items safe to pass into DR-2 | KOSPI200+KOSDAQ150+liquidity filter를 **provisional universe candidate**, KRX300 PR을 **provisional external benchmark candidate**, KRX/KIND/SEIBro를 **official event backbone**으로 넘길 수 있음 | 공식 정기변경·상폐·배당·권리 데이터 존재 citeturn35search7turn38search1turn37search1turn37search9 | DR-2에서 구조 검토 가능 |
| Items to keep in pending KR bucket | KRX300 TR, broker commission, venue fee pass-through, PIT fundamentals, filing/earnings event file, vendor-confirmed constituent history | 위 각 항목 미잠금 citeturn16search5turn34search6turn35search16turn41view0 | KR은 여전히 gated |

즉, DR-1의 기존 “**US-first가 더 명확하다**”는 결론은 이번 DR-1A 이후에도 **약화되지 않았고 오히려 구조적으로 강화**됩니다. KR은 중요하지만, 지금 단계에서는 **완전 잠금된 운영 전제보다 provisional bucket이 더 큽니다.** citeturn35search7turn41view2turn34search6

## 권고

### Next Step Recommendation

**Proceed to US-first DR-2**

- KR 쪽에서 **Lock now**까지 오른 핵심 항목은 사실상 **NXT/SOR를 별도 execution regime로 분리해야 한다**는 구조적 결론뿐입니다. citeturn41view2
- KR benchmark의 핵심인 **KRX300 TR**이 아직 잠기지 않았고, 외부 벤치마크 final lock이 남아 있습니다. citeturn35search0turn36search3
- KR 데이터 스택은 official building block은 충분하지만, **PIT fundamentals / filing dates / earnings dates / full constituent history**에서 유료 벤더 또는 추가 official-source 검증이 필요합니다. citeturn34search6turn35search7turn45search20
- 브로커 수수료, venue pass-through, venue-level fill logging은 실제 브로커 확인 없이는 production-grade cost/execution 가정을 잠글 수 없습니다. citeturn40search2turn41view0turn41view2
- 따라서 DR-2는 US-first로 진행하되, KR은 **vendor/broker confirmation 전용의 좁은 pending bucket**으로 유지하는 것이 이번 공식소스 조사 결과와 가장 일치합니다. citeturn16search5turn34search6turn41view2