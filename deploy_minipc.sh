#!/bin/bash
# PRAMANA A1 — 미니PC(우분투) 24/7 배포 스크립트.
# 미니PC에서:  bash deploy_minipc.sh
# 전제: git·python3·python3-venv 설치됨. .ndl_key는 git에 없으니 따로 복사(아래 4단계).
set -euo pipefail
REPO="${PRAMANA_REPO:-$HOME/ghq/github.com/click6067-ship-it/quant-pramana}"
echo "▶ PRAMANA A1 미니PC 배포 — repo: $REPO"

# 1. 최신 코드
if [ -d "$REPO/.git" ]; then echo "▶ git pull"; cd "$REPO" && git pull --ff-only
else echo "▶ git clone"; git clone https://github.com/click6067-ship-it/quant-pramana.git "$REPO" && cd "$REPO"; fi
cd "$REPO/phase1a"

# 2. venv + 의존성
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
echo "✓ venv + requirements"

# 3. 시크릿 확인 (.ndl_key는 git에 없음 — git 절대 커밋 금지)
if [ ! -f .ndl_key ]; then
  echo "⚠️  .ndl_key 없음. WSL에서 tailscale로 복사하세요:"
  echo "     (WSL)  scp phase1a/.ndl_key <minipc-tailscale-host>:$REPO/phase1a/.ndl_key"
  echo "   복사 후 다시 실행."
  exit 1
fi
echo "✓ .ndl_key 존재"

# 4. 동작 확인 (Sharadar 데이터 pull + NAV 1회)
if .venv/bin/python engine/a1_live_runner.py >/tmp/a1_test.log 2>&1; then
  tail -1 /tmp/a1_test.log; echo "✓ a1_live_runner 동작"
else echo "⚠️ runner 실패 — /tmp/a1_test.log 확인"; exit 1; fi

# 5. cron 등록 (기존 PRAMANA 줄 정리 후 재등록 = 중복 방지)
P="$REPO/phase1a"
(crontab -l 2>/dev/null | grep -v "engine/a1_live_runner\|engine/forward_runner_v7\|engine/alpha_lab_v2_scanner\|engine/build_unified_dashboard" || true; \
 echo "0 6 * * 2-6 cd $P && .venv/bin/python engine/a1_live_runner.py >> outputs/a1_live/cron.log 2>&1"; \
 echo "0 6 * * 2-6 cd $P && .venv/bin/python engine/forward_runner_v7.py >> outputs/forward_v7/cron.log 2>&1"; \
 echo "30 6 * * 2-6 cd $P && .venv/bin/python engine/alpha_lab_v2_scanner.py >> outputs/alpha_lab/cron.log 2>&1"; \
 echo "40 6 * * 2-6 cd $P && .venv/bin/python engine/build_unified_dashboard.py >> outputs/unified.log 2>&1") | crontab -
echo "✓ cron 등록:"; crontab -l | grep engine || true

cat <<'EOF'

▶ 배포 완료. 미니PC 24/7 운영 체크리스트(수동):
  □ 절전/슬립 OFF:  sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
  □ cron 부팅 자동:  sudo systemctl enable --now cron
  □ 노트북이면 덮개 닫아도 유지:  /etc/systemd/logind.conf → HandleLidSwitch=ignore
  □ 원격 접속:  tailscale(이미 세팅) → 어디서든 claude code/ssh로 디버그
  □ daily backup:  outputs/a1_live/nav_log.csv·state.json (cron으로 별도 복사 권장)
  □ ⚠️ WSL의 기존 cron은 제거 (single source — 두 머신서 동시 실행 금지):
       (WSL에서)  crontab -r   또는 PRAMANA 줄만 삭제
EOF
