# Pramana — US Research Engine (`engine/`)

**Scope: US-only (고정).** KR = Future Market Adapter (Deferred) — 미착수. 새 시장은 나중에 `engine/data` 어댑터 + config로 붙인다.
**무엇:** 미국 주식 cross-sectional 신호를 *데이터 정직성 → 비용 정직성 → 검증(kill-test) → 판정*의 순서로 돌리는 config-driven 검증 엔진. **알파 생성기가 아니라 가짜 알파를 죽이는 규율 엔진.**
**결론(이미 확정):** 공개데이터·cross-sectional·long-only로 US 거래가능 standalone edge 없음(4 arena 종료). 자세히는 `integrated/US_Public_Data_CrossSectional_Chapter_Final_Lock_v0.1.md`.

---

## 빠른 시작 (API 키 불필요 — 캐시 snapshot으로 동작)
```bash
cd phase1a
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 1) snapshot 무결성 검증 (기존 HASHES와 1:1, 데이터 무손상 확인)
python engine/data.py validate

# 2) 회귀 게이트 — config 하나로 과거 7실험 재실행 → 동결 숫자/verdict 재현
python engine/_smoke_run.py
```
> 엔진 코어는 **인터넷/키 없이** 실행된다(모든 입력이 `outputs/raw/`의 동결 snapshot). 키는 *새 데이터 pull*과 *TICKERS 동결*에만 필요.

## 모듈 (`engine/`, 8개 — 단일 책임)
| 모듈 | 책임 | 핵심 API |
|---|---|---|
| `data.py` | snapshot 로딩·해시·manifest·TICKERS(동결) | `load(name)` · `load_tickers()` · `validate()` · `file_sha256()` |
| `universe.py` | PIT universe (SP500 멤버십·marketcap rank·survivorship) | `sp500_pit()` · `rank_universe(lo,hi)` |
| `features.py` | 동결 6 feature 정의 | `value/quality/momentum/lowvol` · `event_subsignals` · `composite` · `REGISTRY` |
| `cost.py` | 동결 비용 tier + turnover | `tier_marketcap_bps` · `tier_adv_bps` · `turnover_oneway` |
| `evaluate.py` | 메트릭 (IC·IC-IR·Q5-Q1·long-only·subperiod·버킷·turnover) | `evaluate_panel(L,...)` · `summarize(R)` · `subperiod_icir` |
| `kills.py` | 사전등록 kill-set + verdict | `KILL_SETS` · `apply(name, m)` |
| `report.py` | 표준 md/csv 출력 | `summary_row` · `write_csv` · `render_md` |
| `run.py` | **config-driven 오케스트레이션** (M1~M7) | `run_experiment(cfg)` |
| `engine/_smoke_*.py` | 각 모듈 재현 검증(키 없이) | 6개 smoke |

데이터 흐름: `data → universe → features → cost → evaluate → kills → report`, `run`이 config로 묶음.

## 한 실험 = 한 config
```python
import sys; sys.path.insert(0, "engine")
import run
cfg = dict(name="B3_quality", bundle="broad", rank=(1,1500),
           score={"kind":"raw","feature":"quality"}, dropna=["score","fwd"],
           cost_tier="marketcap", kill_set="broad_retest")
res = run.run_experiment(cfg)
print(res["verdict"], res["summary"]["icir"], res["kill_keys"])
```
config 필드: `name·bundle(broad|smallmid)·rank(lo,hi)·score(raw|composite|composite_event)·dropna·cost_tier(marketcap|adv)·kill_set·filters·composite_predropna·min_names`.
검증된 7개 앵커 config는 `engine/_smoke_run.py`의 `CFGS` 참조(B2~B5 broad + small/mid quality/event/blend).

## 데이터 snapshot (`outputs/raw/`)
- **권위 기록 = `manifest.json`** (13 raw CSV의 sha256·rows·tickers·date범위·columns + `TICKERS.csv` generated_at). `HASHES.txt`는 과거 기록(superset = manifest).
- 핵심 파일: `DAILY_all.csv`(marketcap 전종목)·`broad_SEP/DAILY_pb/SF1/SF1_ext`·`smallmid_SEP/DAILY/SF1`·`SP500_membership`·`SFP_SPY`·`TICKERS.csv`(21847종·28컬럼, 동결).
- **재현성:** `python engine/data.py validate` 가 기존 9개 hash 1:1 재계산. 숫자 바뀌면 FAIL = 데이터 변형 신호.
- 출처: Sharadar (Nasdaq Data Link) 구독 윈도우 내 pull. 라이선스 = 구독 중 사용.

## 불변 규칙 (LOCKED)
새 feature/cost/kill 정의·튜닝 변경 금지 · 동결 숫자 바뀌면 실패 · API 기본 off(`snapshot-tickers`·pull만 명시 플래그) · XGBoost/LLM/TSFM/deep 금지 · **KR 추상화 금지(US-only)** · 범용 플랫폼화 금지.

## 디렉터리
```
phase1a/
  engine/            # 정본 (config-driven 검증 엔진, API-free)
  legacy/            # 원본 실험 스크립트 보존 (증거·참조; 미접촉)
  outputs/raw/       # 동결 snapshot + manifest.json + HASHES.txt + TICKERS.csv
  outputs/engine/    # 엔진 재현 산출 (universe·regression_report)
  reports/           # 실험 결과 리포트 (B0~B5·quarantine·event·smallmid)
  registry/          # phase1a_milestones.csv
  requirements.txt · README_ENGINE.md
integrated/          # Lock/Protocol/Result 정본 (Phase1A·Phase2·Roadmap)
```

## 다음 (US-only)
`integrated/US_Only_Completion_Roadmap_v0.1.md` — P3.1 packaging(본 문서) → P3.2 config/run/report workflow → P3.3 next-edge protocol **or** paper-ready simulator → P3.4 subscription/key housekeeping.
