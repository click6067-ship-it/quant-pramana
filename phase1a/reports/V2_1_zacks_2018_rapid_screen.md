# V2.1 — ZACKS/EEH 2018 Rapid Sign Screen 결과
**Date:** 2026-06-11 · **목적:** 결제 전 *부호 확인만*(full validation 아님·튜닝 0·window 사냥 0). · **데이터:** ZACKS/EEH 무료 2018 샘플(obs_date PIT) + 기존 SEP 가격.
**한 줄 판정:** **FAIL — 단, 부호 때문이 아니라 *샘플 불충분*.** 무료 샘플 = **2018 + Dow 30 메가캡 22종뿐** → cross-section 불가(5분위=종목당 4개). **결제 전 zero-cost 디리스크가 구조적으로 불가능.**

## 결과
- EEH 매핑 tickers = **22** (=Dow 30 subset: AAPL·MSFT·JPM·XOM·…)·100% 매핑·이벤트 264·월 12.
- primary `(rev_up−rev_down)/cnt`: Rank IC **+0.0104** · IC-IR +0.074 · Q5-Q1(21d) **+0.20%**
- raw `rev_up−rev_down`(참고): Rank IC +0.0236 · IC-IR **+0.182** · Q5-Q1 +0.41%

## 읽는 법 (정직히)
- **부호는 양수**(IC>0·Q5-Q1>0, raw는 더 강함) — PEAD의 *반전*(음수)과 달리 **방향은 안 틀렸다.** 약한 긍정 힌트.
- **그러나 n=22 메가캡·1년 = 통계적으로 무의미**(5분위에 4종). 사전 기준 "mapping/sample 부족 → FAIL"에 정확히 걸림.
- → **무료 샘플로는 이 축을 디리스크할 수 없다.** 부호 스크린이라는 zero-cost 우회가 *데이터 캡(22종+2018)* 때문에 막힘. 진짜 검증 = 유료 Zacks 전체 history(top-1500·2016–2026)만 가능.

## 판정 → 결정 분기 (라이브)
사전 룰상 **FAIL(샘플)** → analyst-revision 축은 **HOLD**(CLOSE 아님 — 부호는 살아있음, 데이터만 막힘). 이제 *cheap 디리스크가 없으므로* 순수 결정:
- **(a) Zacks 전체 history 구독 → v2.2 사전등록 kill-test** (`V2_2_Analyst_Revision_Protocol`). 단 base-rate 경고: v1에서 *동일 패턴*(메가캡/대형주에선 cap-weight 벽, 소형선 비용 벽)이 5번 반복 — revision도 문헌상 *소형에서 강함*이라 top-1500서 같은 벽 가능. 그리고 무료가 준 22종이 *정확히 그 메가캡*이라 가장 불리한 구간.
- **(b) HOLD/보류** — cheap 디리스크 불가 + 6 prior negative base-rate → blind spend 안 함.
- **(c) 대체 벤더**(FMP/Finnhub) free key 가입 후 *그쪽* PIT revision 품질 확인 — 단 Zacks보다 PIT 약할 가능성.

## 결론
**부호는 안 틀렸다(긍정 힌트)지만, 무료론 검증 불가 = 결제 결정.** 추격·튜닝 0. 가장 정직한 다음은 (a) blind spend의 base-rate를 인정하고 갈지, (b) 멈출지 — 용하 결정.
