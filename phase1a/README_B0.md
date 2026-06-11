# B0 실행 가이드 (minimal)

B0 = **data-only benchmark sanity**. "깨끗한 데이터로 self-built cap-weight TR 벤치를 재구성할 수 있나"만 확인. 알파·수익예측·종목추천 아님.

## 0. 설치 (WSL2에서)
```bash
cd phase1a
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 1. 오늘 당장 — 무료 dry-run (키 불필요)
```bash
python b0_benchmark_sanity.py --source free \
  --tickers AAPL,MSFT,JPM,XOM,KO,PG,JNJ,WMT,GE,T --start 2015-01-01
```
- yfinance로 **equal-weight TR index**를 만들고 SPY와 비교 → **파이프라인이 도는지**만 검증.
- ⚠️ **survivorship-biased(상장폐지 종목 없음)·cap-weight 불가**. 숫자/통과를 "진짜 B0 통과"로 **신뢰 금지**. 기계 smoke test 전용.
- 이게 깔끔히 돌면 = 코드/환경/로직 OK → 다음은 진짜 데이터.

## 2. 진짜 B0 — Sharadar (API 키 필요)
1) Nasdaq Data Link 계정 → API key. (무료 SF0 샘플로도 `--inspect-schema`까지는 시도 가능, 단 SEP/DAILY는 구독 필요)
2) ```bash
   export NASDAQ_DATA_LINK_API_KEY=발급받은키
   # (a) 스키마 capture — 라이브 API가 주는 실제 컬럼 출력:
   python b0_benchmark_sanity.py --source sharadar --inspect-schema
   # (b) 진짜 B0 (cap-weight TR + 상장폐지 포함):
   python b0_benchmark_sanity.py --source sharadar \
     --tickers AAPL,MSFT,JPM,XOM,KO,PG,JNJ,WMT,GE,T --start 2015-01-01
   ```
3) 유니버스를 넓히려면 `--tickers`에 더 많이(또는 추후 top-N 자동선정 추가). 첫 B0는 작게 시작해 체크가 도는지부터 본다.

## 3. 체크 6개 (14게이트 전체 아님 — 막히면 추가)
| ID | 의미 |
|---|---|
| CHK-W | 매 리밸런스 가중치 합 ≈ 1 |
| CHK-S | survivorship: 상장폐지 종목이 폐지 전까지 보유됨 (sharadar) |
| CHK-F | no-future: 상장(첫 거래일) 전 편입 금지 |
| CHK-TR | TR ≥ price-return (배당 반영) |
| CHK-R | data_hash + series_hash 기록(재현성) |
| CHK-D | SPY 대비 drift (진단용·자동실패 아님) |

## 4. 산출물
- `outputs/b0_benchmark_<source>.csv` — 벤치마크 지수 series
- `registry/b0_runs.csv` — 최소 실행기록(run_id·hash·체크요약). *60필드 registry 아님 — 솔로 스케일.*

## 5. 알아둘 것 (정직)
- **free 모드는 진짜 B0가 아니다** — survivorship-biased·equal-weight. "내가 만들 수 있나" 확인용.
- **진짜 cap-weight + survivorship은 Sharadar `DAILY.marketcap` + `SEP.closeadj` + `TICKERS.isdelisted`에서만** 나온다. 그래서 진짜 B0엔 Sharadar 구독이 필요.
- Claude(나)는 이 환경(샌드박스)에 인터넷이 없어 **직접 실행 못 함**. 너가 WSL2에서 돌리고 **출력 전체를 붙여주면** 같이 디버깅한다.
- 막히는 에러(컬럼명·API·날짜)는 거의 다 1~2줄 수정. 겁먹지 말고 일단 돌려.
