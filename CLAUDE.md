# CLAUDE.md — PRAMANA V4 (project · 전역 ~/.claude/CLAUDE.md 보강)

> 전역 CLAUDE.md = 내 행동 헌법. 이 파일 = 이 repo의 프로젝트 컨텍스트 + **공유 기억 라우터.**
> Codex(AGENTS.md)와 **같은 기억을 공유한다** → `docs/context/*` 가 단일 진실.

## 세션 시작 시 읽을 것 (Codex의 AGENTS.md와 동일 파일)
1. `docs/context/PROJECT_STATE.md`  — 현재 상태 (**날짜 확인**, 오래됐으면 의심)
2. `docs/context/LOCKS.md`          — 불변 결정 (근거 → `PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v0.2.md`)
3. `docs/context/ADVERSARIAL_COUNSEL.md`
4. `docs/context/DECISION_LOG.md`
(내 auto-memory도 이 상태를 갖지만, **docs/context = Claude·Codex 공유 정본**.)

## 영구 사실
- 데이터: **Sharadar(유료)=backtest, yfinance(무료)=forward 데모/sanity만.**
- PAPER only / NO LIVE · US only · core-satellite · next-bar · attribution 필수 · 결정적 risk veto 최종 · LLM/TSFM off-path · 사람=자본 게이트.

## 상태 갱신 규율 (staleness 방지 — 유일한 실패점)
상태가 바뀌면 `docs/context/PROJECT_STATE.md` + `DECISION_LOG.md` 갱신. rationale는 락시트에만(중복 금지).

## Codex 적대 카운슬 호출
`./council.sh "질문"` — 현재 컨텍스트(STATE+LOCKS) 자동 주입. 대화 붙여넣기 불필요.
