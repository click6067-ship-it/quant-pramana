# PRAMANA V6 — Diversified Aggressive Book (Codex 확정 스펙 · SHIP-as-paper)

> **용하: v6 ㄱㄱ + 결정은 Codex 회의로.** Codex v6 스펙 council 확정 → 빌드 완료(forward_runner_v6.py·라이브 인셉션 2026-06-11).
> 동기: V5(레버드 Core)가 SPY/QQQ와 *같이* 낙폭(레버 증폭). 용하 "같이 안 맞기·최소한 빼기(숏 아님)". → 파훼법 = **managed-futures 분산.**
> 상태: **RESEARCH_ONLY / PRODUCTION_UNSAFE / PAPER_ONLY.** 작성 2026-06-12.

## 정체
**V6 = 85% 레버드 Core(SPY/QQQ·vol-target 28%·캡 1.5x·DD ladder) + 15% managed-futures(DBMF).** 정직: 레버드 베타 + *구조적 분산*(위기 컨벡시티)지 alpha 아님·no-ruin 아님.

## Codex 확정 스펙 (v6 council)
- **mode = vol_target** (고정레버 아님). 근거: v6A가 고정 1.5보다 명확히 나음(Sharpe 0.99>0.89·MDD −27<−39). 6mo chop −6.3%p는 *보험료지 결함 아님* — 버리면 "같이 안 맞기"를 버리는 것.
- **leverage_cap = 1.5** ("낮은 레버"라는 v6 이름에 정직한 상한·V5 2.0은 paper max였음).
- **managed_futures = DBMF 15%** (20% 아님 — 더 줄지만 bull 드래그↑; 용하 목표는 "낙폭 최소화"가 아니라 "공격 + 낙폭 분산").
- **추가 cash/trend de-risk gate = OFF** (vol-target+DBMF+cap1.5로 방어 충분; gate 추가 = config-mining → crash-pack OOS 사전등록 전 research toggle OFF).

## 측정 (2019-2026 yfinance·비용후 · v6_book.py)
| | 풀(2019~) | 2022 bear | 2023 회복 |
|---|---|---|---|
| **V6 (v6A)** | +257% · MDD −27% · **Sharpe 0.99** | **−26% · −27%MDD** | +48% |
| V5 (cap2.0·DBMF無) | +344% · −32% · 0.95 | −31% · −32% | +65% |
| v6C (고정1.5·DBMF無) | +380% · **−44%** · 0.85 | −40% · −43% | +61% |
| QQQ | +316% · −35% | −33% | +56% |

DBMF 15% 기여(고정1.5 기준): Sharpe 0.85→0.89·MDD −44→−39%·수익 +380→+336%. **2022 동반하락서 DBMF가 *오르며* 방어(2022 DBMF +21.5%).**

## 정직한 트레이드오프 (가짜 승리 없음)
- **얻는 것:** 낙폭 ↓ (풀 −27% vs V5 −32%·v6C −44%), 2022 상관크래시 방어, Sharpe ↑(0.99). = 네가 원한 "같이 안 맞기".
- **내는 것:** 풀사이클 수익 ↓ (+257% vs V5 +344%) · 2023 bull 드래그. **"낙폭 보험료를 상승장 수익으로 낸다"** — Codex: "+257%가 V5보다 낮은 건 결함이 아니라 *명시적 보험료*."
- **공짜 아님 재확인:** 알파 없으니 낙폭 감소는 항상 수익으로 지불. 최대수익(v6C +380%)을 고르면 −44% MDD = "같이 안 맞기" 포기.

## ⚠️ 핵심 caveat (RESEARCH_ONLY인 이유)
DBMF 역사 짧음(2019~·2008/dot-com 없음) · managed futures 2011-20 "lost decade" 존재 · +0.05~0.14 Sharpe 개선은 *샘플 의존* · 15%는 미최적화 → **검증된 win 아님·유망한 분산기.** 실자본 = crash-pack + 12mo forward 판정표(v5 frame) + 사람 게이트 전 금지.

## Operational
- `forward_runner_v6.py` 무인 일1회(free yfinance·SPY/QQQ/DBMF·fail-closed·append-only). 라이브 인셉션 2026-06-11. 대시보드 `v6_forward_dashboard.html`. cron `0 6 * * 2-6`.
- 판정표 = LIVE-only(현재 PENDING·12mo 필요)·미구현 항목 UNKNOWN=불합격. reconciliation = 무료 독립소스 막힘 → 실자본 전 유료 2nd피드.
- 12mo STOP 기준(v5 frame 상속): 못 맞추면 "쉬운 알파 없음·Core Beta만 production-safe" 수용.

> **한 줄:** V6 = 네 "같이 안 맞기"의 정직한 답 — managed-futures 분산 + 낮은 레버로 상관 낙폭을 *구조적으로* 줄였다(2022 방어·Sharpe↑). 단 alpha 아니라 보험료(상승장 수익↓), 검증은 forward 몫.
