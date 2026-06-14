# A2 BUILD PLAN — resume 앵커 (crash-safe)

> 목적: 세션이 API 소켓 끊김으로 죽어도 여기서 그대로 이어간다. 결정·인벤토리·남은 작업의 단일 진실.
> 작성 2026-06-14. 규율: PAPER · 자본권한 0 · 사전등록 kill · next-bar · Codex 적대검수.

## 0. API 에러 — 해결됨 (2026-06-14 · Claude+Codex 수렴 진단)
- 증상 = Claude Code "socket connection closed unexpectedly" (긴 스트림 도중·A2 코드 무관).
- 실측: HTTPS 5/5 안정 · DF 1500B가 8.8.8.8·anthropic IPv4 둘 다 0% loss → **MTU 진범 아님(1280으로 낮출 필요 없음)** · DNS 간헐 실패(hetzner FAIL/others OK) · **api.anthropic.com IPv6(2607:6bc0::10) "Network unreachable"** · Tailscale=Windows 호스트(WSL2엔 tailscale0 없음) · 메모리 OK(4.2Gi 여유=범인 아님).
- **근본 원인 = WSL2 NAT 네트워킹 계층 불안정** (DNS 터널 간헐실패+IPv6 깨짐+NAT 긴연결 reset; Windows Tailscale이 겹쳐 악화). Codex 독립 진단도 "WSL DNS 터널/프록시 불안정 → networkingMode=mirrored"로 일치.
- **★ 적용한 수정 = `.wslconfig`에 `networkingMode=mirrored`+`dnsTunneling=true`+`firewall=true`+`autoProxy=true`** (Win11 25H2 build26200=지원). NAT 폐기→Windows 네트워크 직접 사용=DNS·IPv6·VPN·긴연결 한방 해결. 백업 `/mnt/c/Users/click/.wslconfig.bak.20260614`.
- **사용자 액션 1개 = PowerShell `wsl --shutdown` 후 Claude Code 재오픈.** (mirrored는 재시작해야 적용.) 재오픈 후 "이어서"라고만 하면 이 BUILD_PLAN으로 A2 재개.
- fallback(mirrored가 문제 시): .wslconfig 4줄 삭제+`wsl --shutdown`으로 원복 / 또는 DNS만 고정(`/etc/wsl.conf [network] generateResolvConf=false` + resolv.conf 1.1.1.1·8.8.8.8) / 또는 `ethtool -K eth0 tso off gso off gro off`.

## 1. 잠금된 결정 (직전 6ff21099 세션 02:53→04:39 · 용하 승인)
- **위치** = 이 repo 새 클린 트리 `a2/` + 데이터 자산·기존 모듈 재사용("코드는 새로, 난제의 정답은 참조").
- **동적 비중** = 전면 재도입하되 **알고리즘 새로 설계**(기존 −113%p는 *옛 v3 알고*의 기각 → 새 알고는 새 가설·**킬조건 추후논의**). ← 미해결·용하 결정 필요.
- **1차 deliverable** = 전체 빌드 구조화 + 시각화 HTML (사용자 이해용). ← 이번 작업.

## 2. 현재 빌드 인벤토리 (phase1a/engine/ · 전부 커밋됨)
- `a2_live_runner.py` — 메인. 듀얼 A2-T(QQQ/TQQQ)/A2-Q(no TQQQ) NAV·동적 ablation·forward Vault ledger·sleeve 회계(QQQ35/TQQQ35/Attack10/Moon10/Cash10)·대시보드. **동적 OFF**.
- `a2_attack_ledger.py` (Phase B) — positions schema·NEG gate 차등(Attack=size축소/Moon=절대금지)·entry/exit 게이트·token 회계.
- `a2_moonshot_ledger.py` (Phase B) — thesis 필수필드·EV·draft score·Moonshot Vault rule·판정일 expiry.
- `a2_attack_scanner.py` (Phase C3) — 분봉 ORB15/VWAP/RVOL/Bollinger·등급 A/B/C/D·attack_candidates.csv. **이미 빌드됨**.
- `a2_intraday_provider.py` (Phase C4) — yfinance PROXY / Polygon·Alpaca stub·DATA_QUALITY 라벨.
- `a2_daily_war_plan.py` (Phase C1/C2) — rule engine state→sleeve 게이트(GREEN/YELLOW/RED)·war_plan.json+md.
- config: `config/a2_convex_raider.yaml`(allocation·sleeve_ranges·vault·verdict·dynamic OFF) · `config/a2_revived_components.yaml`(Graveyard 판정).
- cron: `5 6 * * 2-6 a2_live_runner` + `15 6 * * 2-6 a2_daily_war_plan`. deploy_minipc.sh = a2_live_runner 포함.
- outputs/a2_live/: prices.csv·state.json·nav_log.csv·war_plan.json·attack_candidates.csv·health.json·positions/.

## 3. Codex 적대검수로 박힌 버그픽스 (재구현 시 반드시 보존 — 백지면 재지불)
1. **next-bar** — 동적 신호 `mds[i-2]`(close-only 보수적·same-day look-ahead 제거).
2. **live/backtest 분리** — 백테스트(2016~)와 라이브 paper(inception~) 별도 NAV.
3. **to_won** — 첫 거래일 종가 기준(월평균 정규화=부분 look-ahead 폐기).
4. **sleeve 회계 #4** — 빈슬롯=cash·차면 정확 valuation(장식 NAV 금지).
5. **Vault** — 백테스트 OFF(장기 누적 excess 단위 부적합)·forward live ledger만(vault.json append-only·절대수익일 때만·Hard70/Reload30·Hard 재투입 금지).
6. **동적 allocator v3 = REJECT** — ablation −113%p < fixed 35/35. "이 구현/2016~ benign/무비용" 한정·"동적 마켓타이밍 일반 사망" 확장 금지.
7. **Alpaca/IEX = 알파 증거 불인정** — SIP ~2%·QA only. 유료 분봉은 v2 forward 양의신호+병목확인 후 1개월 파일럿.

## 4. 남은 작업 (이번 세션 진행)
- [진행] **1차 = 구조화 시각화 HTML** → `a2/A2_BUILD_STRUCTURE.html`.
- [ ] **C3 통합 수정** — a2_attack_scanner cron 등록 + war_plan 연결순서(현재 daily_war_plan이 top_attack:[] 하드코딩으로 scanner 출력 덮음 → scanner를 war_plan 다음 실행하거나 war_plan이 scanner 출력 read).
- [ ] **D** — 통합 대시보드(build_unified_dashboard에 A2 카드/iframe) + deploy_minipc.sh에 scanner/war_plan 추가 + A2 build 리포트.
- [ ] **동적 allocator 재설계** — 새 알고리즘·킬조건. **용하 결정 필요**(Phase 0/kickoff급·deferred). 그 전엔 config dynamic OFF 유지.

## 5. 금지 (LOCK)
TQQQ=알파/Core라 부르기 · 물타기 · NEG 무시 · Moonshot thesis 없이 진입 · Vault Hard 재투입 · LLM 매수/매도 직접 명령 · PAPER only · NO LIVE · 자본권한 0 · 사람=자본 게이트. 설계 정본=`PRAMANA_V4/PRAMANA_A2_Convex_Raider_Book.md`.
