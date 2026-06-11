#!/usr/bin/env bash
# PRAMANA 적대 카운슬 wrapper — Codex에 현재 컨텍스트를 자동 주입(대화 붙여넣기 불필요).
# 현재 STATE+LOCKS를 프롬프트에 *임베드*하므로 Codex가 파일을 안 읽어도 맥락이 보장됨.
#   사용:  ./council.sh "비판할 질문/주장"
#          ./council.sh -f brief.txt
#          ./council.sh --dry "..."        # codex 호출 없이 조립된 프롬프트만 출력(확인용)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="$ROOT/docs/context"
DRY=0; [ "${1:-}" = "--dry" ] && { DRY=1; shift; }
if [ "${1:-}" = "-f" ]; then Q="$(cat "${2:?brief 파일 경로 필요}")"; else Q="${*:?사용법: ./council.sh \"비판할 질문\"}"; fi
LOCKSHEET="$(ls -1 "$ROOT"/PRAMANA_V4/PRAMANA_V4_LOCK_SHEET_v*.md 2>/dev/null | sort -V | tail -1 || true)"

PROMPT="[PRAMANA 적대 카운슬 · no-echo. AGENTS.md / ADVERSARIAL_COUNSEL.md 역할대로 차갑게 두들겨라.]

=== PROJECT_STATE (현재 사실) ===
$(cat "$CTX/PROJECT_STATE.md")

=== LOCKS (재논쟁 말 것 — 새 반박은 새 데이터로만) ===
$(cat "$CTX/LOCKS.md")

=== 검토 대상 ===
$Q

위 STATE/LOCKS를 현재 진실로 받고(데이터=Sharadar backtest, Evidence 측정치 재논쟁 X) →
≤6 sharpest objections([발견]/왜 실패/임팩트/수정안) + 판정 라벨 + VERDICT(SHIP/REVISE/STOP) + 가장 먼저 고칠 1개.
web_search로 외부 근거 인라인 인용. 깊은 근거 필요 시 ${LOCKSHEET:-PRAMANA_V4 락시트} 를 읽어라."

if [ "$DRY" = 1 ]; then printf '%s\n' "$PROMPT"; echo; echo "[--dry: codex 미호출. 위가 Codex에 들어갈 프롬프트.]"; exit 0; fi
OUT="$CTX/council_$(date +%Y%m%d_%H%M%S).md"
printf '%s\n' "$PROMPT" | codex exec --skip-git-repo-check -s read-only -c tools.web_search=true | tee "$OUT"
echo; echo "→ saved: $OUT"
