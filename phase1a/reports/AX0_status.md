# AX-0 Status — 2026-06-14

> RESEARCH_ONLY / PRODUCTION_UNSAFE · PAPER · 가상 $100k · 자본권한 0 · 검증된 알파 아님 · FORWARD_PAPER_ONLY_UNVERIFIED
> 사전등록: PRAMANA_V4/AX0_Protocol.md (gate 결과 前 잠금). 정본: ~/main/council/2026-06-14_aggressive-pivot/

## Graduation gate (Protocol §3 — net>0만으론 절대 통과 X·fail-closed)
| 항목 | 값 | 기준 |
|---|---|---|
| 독립 trade N(event) | 0 | ≥ 30 |
| closed trade | 0 | — |
| median P&L | — | > 0 |
| raw P&L 하한 CI | — | (attribution 후 residual로 평가) |
| attribution 가용 | False | True 필요(Greeks/factor 분해) |
| compliance OK | — | True 필요 (clean) |
| **VERDICT** | **INSUFFICIENT** | 독립 trade 0 < 30 → 통계적 판정 불가(우연을 엣지로 착각 금지·net>0이라도 통과 X) |

## 해석 (정직)
- 현재 = **INSUFFICIENT**. 독립 trade 부족 → 판정 불가(우연 방지). forward 축적 필요.
- AX-0 = S1 long-convex catalyst 1 sleeve(옵션 long·defined-risk). feeder catalyst 후보 → 보수 fill(ask·OI/vol/spread floor)·heat rails hard-veto.
- **옵션 paper = UNVERIFIED**(무료 yfinance 체인·이력 없음·NBBO 아님). "검증됨" 포장 금지. 유료 quote 데이터 전엔 signal vs tradable 분리.
- 죽으면 graveyard·trial registry 다음 sleeve(S2). "쉬운 공격 엣지도 없음" 수용 조건 = 무한루프 차단.

_cron: 일1회 feeder → book → attribution. 산출: outputs/ax0/{candidates,option_ledger,nofill_log,attribution}.csv·positions.json·trial_registry.json._
