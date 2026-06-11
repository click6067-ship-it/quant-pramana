# PRAMANA — 24/7 무인 forward 페이퍼 운영 가이드

> **결론부터:** 이 전략은 **매일 1회(미국 장마감 후)**면 충분하다. 6시간/실시간 불필요(미국 주식·ETF는 24h 시장이 아니고, 추세 sleeve는 200일선 교차 때만 바뀐다). **GPU·클라우드 API 전혀 불필요** — 전부 CPU pandas 산술이라 미니PC로 차고 넘친다.

## 무엇이 도는가
- `engine/forward_runner.py` — **ETF 추세 + LETF sleeve** 페이퍼 북. **무료 EOD(yfinance, ETF 17개)** 만 쓴다 → Sharadar 구독이 끝나도 매일 돈다.
  - 신호: 각 ETF 종가 vs 200일 이동평균(위=롱/아래=현금) + SPY 20일 변동성>22%면 노출 ½.
  - LETF: QQQ/SPY가 추세 ON이면 TQQQ/UPRO 소량(위험예산 4%).
  - look-ahead 없음: 가중치는 **종가 t에 확정 → 수익은 t+1에 실현**.
  - 가격캐시 append-only(과거값 동결=NAV 재현성) · 멱등(하루 중복 실행 무해).
- 산출: `outputs/forward_dashboard.html`(라이브 대시보드, 1시간마다 자동 새로고침) · `outputs/forward/forward_log.csv`(NAV 로그) · `state.json`(라이브 인셉션).
- **equity 시장중립 sleeve는 유료 펀더멘털(Sharadar SF1) 필요** → 무료 forward에선 일시정지. 구독 버스트 때 월 1회 갱신(별도).

## 미니PC 셋업 (3단계)
```bash
# 1) 1회 셋업 (이미 .venv 있음)
cd /path/to/quant-pramana/phase1a
python3 -m venv .venv && .venv/bin/pip install yfinance pandas numpy matplotlib

# 2) 수동 1회 테스트
.venv/bin/python engine/forward_runner.py        # 네트워크로 EOD pull
.venv/bin/python engine/forward_runner.py --dry   # 캐시만(네트워크 X)

# 3) cron 등록 (매일 미국 장마감+데이터 정착 후 = UTC 06:00, 화~토)
crontab -e
# 아래 한 줄 추가:
0 6 * * 2-6 cd /path/to/quant-pramana/phase1a && .venv/bin/python engine/forward_runner.py >> outputs/forward/cron.log 2>&1
```
- **왜 화~토 06:00 UTC?** 미국 장마감 16:00 ET = 21:00 UTC(겨울)/20:00(서머타임). 06:00 UTC면 EOD가 확실히 정착된 뒤 직전 미국장을 잡는다. 시각이 좀 어긋나도 무해(새 거래일 없으면 no-op).
- **라이브 대시보드 보기:** 미니PC에서 `python -m http.server 8000 -d outputs` 후 브라우저로 `http://<미니PC-IP>:8000/forward_dashboard.html`. (또는 파일 직접 열기.)

## 리밸런싱 주기 — 왜 매일인가
| 주기 | 적합? | 이유 |
|---|---|---|
| 실시간/장중 | ❌ | 이 전략에 일중 신호 없음. 비용·노이즈만↑, 엣지 0. |
| **매일(장마감 후)** | ✅ | 추세 sleeve가 200일선 교차를 매일 체크. vol-gate도 일별. **권장.** |
| 6시간 | ❌ | 미국장 닫혀있는 시간엔 EOD 안 바뀜 → 무의미. |
| 주간/월간 | △ | equity sleeve는 월간이 맞음. 추세는 매일 체크가 낫다(교차 지연 최소화). |

## ⚠️ 정직 고지
- **PAPER다.** 실주문·실자본 아님. 실거래는 12개월 라이브 트랙 + 사람 승인 게이트 통과 후에만.
- **무료데이터 리스크:** yfinance는 배당/분할 조정 오류·결측이 가끔 있다 → 러너에 배드틱 가드(단일일 |수익|>60% 경보) 내장. 레버리지 북엔 데이터 품질이 곧 생존이므로, 실자본 단계에선 유료 피드로 교체 필요.
- **forward는 trend+LETF만** = 백테스트 풀북과 다르다(equity 분산 빠짐). 이건 의도된 한계(무료로 무인 운영 가능한 부분만).
