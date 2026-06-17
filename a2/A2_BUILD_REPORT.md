# A2 Build Report — Attack/Moonshot 전부 구현 + Delta 완료

> 2026-06-14 · 브랜치 `a2-build-blind-backtest` · 설계정본 `PRAMANA_V4/A2_DELTA/`·`A2_IMPL_PACK/`
> 사용자 지시: "a2 빌드할 때 attack·moonshot 미구현하면 안 됨. 제대로 전부 구현." → **충족.**
> 규율: PAPER · 자본권한 0 · 사전등록 kill · next-bar · Codex 적대검수.

## 1. 쉬운 말 요약
A2는 QQQ/TQQQ 레버 베타(35/35) + **Attack(10·분봉 급등주 단타)** + **Moonshot(10·thesis 비대칭 베팅)** + Vault(10)다. 직전까지 Attack/Moonshot은 **forward 빈 슬롯(스키마만)** 이라 "정말 값을 하나"가 미검증이었다. 이번에 **과거데이터로 실제 검증하는 blind/PIT 백테스트를 전부 구현**했다.
- 결과: **Attack DEAD · Moonshot edge 없음** (정직한 negative·8세대 결론과 일관). 평균은 양수지만 *우측꼬리(소수 대박)가 끌어올린 lottery*고 **중앙값은 QQQ에 지고 승률 <50%**. = 시스템이 또 가짜 알파를 안 만들었다(성공).
- A2가 그래도 슬롯을 유지하는 근거: convex 우측꼬리는 실재(asym~2)·분봉 confirmation은 미검증 여지·NEG/token/thesis는 손실통제 장치. **단 "검증된 알파"가 아니라 "위험을 정직히 인정한 비대칭 베팅".**

## 2. 추가/수정 파일
**신규 엔진 (phase1a/engine/):** `a2_data.py`(PIT 로더) · `a2_feature_store.py`(available_at) · `a2_event_store.py`(EDGAR PIT) · `a2_blind_backtest.py`(Attack/Moonshot 검증) · `a2_attack_tokens.py` · `a2_moonshot_draft.py` · `a2_benchmarks.py` · `a2_tq_dh.py` · `a2_dynamic_sell.py` · `a2_profit_vault.py`
**수정:** `a2_attack_scanner.py`(NEG=EDGAR 연결완료) · `build_a2_overview.py`(blind backtest 섹션) · `deploy_minipc.sh`(cron 8 jobs)
**config:** `a2_tq_dh.yaml` · `a2_vault_rules.yaml`
**리포트:** `phase1a/reports/A2_attack_moonshot_blind_backtest.md`·`A2_monthly_benchmark_review.md`·`A2_tq_dh_weekly_review.md`·`A2_weekly_vault_review.md` · `reports/moonshot_thesis/{TEMPLATE,_SAMPLE_EXAMPLE}.md`
**문서:** `PRAMANA_V4/A2_DELTA/`(7) · `PRAMANA_V4/A2_IMPL_PACK/`(17)
**산출물(gitignore):** `outputs/a2_features/feature_store.csv`(51MB) · `outputs/a2_events/event_store.csv`(34,381 EDGAR+zacks)·`edgar_cache/` · `outputs/a2_decisions/{decision_log.csv 60,136행, blind_backtest_summary_*.json}` · `outputs/a2_live/{benchmark_panel.csv, tq_dh_decisions.csv, sleeve_adjustments.csv, vault_events.csv}`

## 3. 구현된 기능 (Phase 0~D + Delta 전부)
- **Phase 0/A** (직전 세션·유지): 무결성(next-bar·live/backtest 분리·to_won)·forward Vault ledger.
- **Phase B (연료) = 이번에 완성:** Attack ledger+**token system**(주3·A=1/B=0.5·손실−1·+2R+1·RED 0) · Moonshot ledger+**draft board**(10축 점수·M1만 상위2 진입)+**thesis 템플릿/샘플** · NEG Gate 차등(Attack=size축소/Moon=절대금지).
- **Phase B+ Blind/PIT Backtest = 핵심:** feature store(gap/RVOL/momentum/52wk/quality·available_at) · event store(EDGAR 8-K item·acceptance_datetime·NEG/POS 분류·zacks) · blind backtest(decision_time/available_at≤decision_time·signal<execution·same-bar 금지·decision_log hash).
- **Phase C:** War Plan(LLM=GYR만) · Attack scanner(분봉 ORB/VWAP/RVOL/Bollinger·**NEG=EDGAR 연결완료**) · 분봉 provider(yfinance PROXY/Polygon·Alpaca stub).
- **Delta:** TQ-DH(Dip A/B/C/D·Reload만·Hard 영구잠금) · benchmark panel(SPY/QQQ/TQQQ/naive/synthetic1.4x/DCA/V7·3y/12/6/3mo) · dynamic vault/sell engine(Vault In/Out·5%p trim/add·Hard 재투입 3중 차단).
- **Phase D:** A2 종합 대시보드(blind backtest 섹션) · cron 8 jobs · deploy_minipc.sh.

## 4. 아직 미구현 / 의도적 보류
- **분봉 ORB/VWAP/RVOL 과거검증** = 무료/캐시 불가(Sharadar=daily). Stage-B는 yfinance PROXY/유료 provider forward로만. 인프라 완비·성과증거 아님.
- **EDGAR 전종목 10년 크롤** = rate-limit상 표본 200종(인프라 완비·확장은 시간문제). Moonshot은 소표본 탐색.
- **동적 allocator 재설계(새 알고·킬조건)** = 용하 결정 필요(Phase 0/kickoff급·deferred). 그 전엔 config dynamic OFF 유지(기존 −113%p REJECT).
- **유료 분봉(Polygon/Alpaca SIP)** = v2 forward 양의신호+체결 병목 확인 후 1개월 파일럿(현재 보류).

## 5. 벤치마크 표 (백테스트 2016~·inception·강세장 편향·검증된 알파 아님)
| 벤치 | 총수익 | MDD | Sharpe |
|---|---:|---:|---:|
| SPY | +327% | −34% | 0.87 |
| QQQ | +583% | −35% | 0.94 |
| TQQQ | +3155% | −82% | 0.84 |
| naive QQQ35/TQQQ35/Cash30 (=A2 base 고정) | +882% | −48% | 0.87 |
| synthetic QQQ 1.4x | +935% | −48% | 0.88 |
| V7 생존코어 | +170% | **−18%** | **1.18** |

A2 base +882% > QQQ but **== naive**(동적 OFF라 동일·tautological) → 부분성공. A2-over-QQQ = **레버지 알파 아님**(beta≈1.4x). Attack/Moonshot 부가가치는 backtest로 미측정(blind backtest 결과 = no edge).

## 6. Codex STOP 잔여 리스크
- 기존 STOP #1~#5 = CLOSED(next-bar·live/backtest·to_won·sleeve 회계·Vault forward). #6(동적 REJECT) = 확정.
- 이번 신규 리스크(Codex 적대검수 대상): blind backtest look-ahead 누수 가능성(available_at·next-bar 검증)·smallmid gap proxy·EDGAR 표본 selection·moonshot 소표본 과해석·DCA 벤치 normalize 오도 가능성.

## 7. 다음 사용자 입력 필요
- **동적 allocator 재설계 방향**(새 가설·킬조건) — kickoff급 결정.
- 유료 분봉 파일럿 GO/보류(현재 보류 권고).
- 이 브랜치 merge/PR 여부.
