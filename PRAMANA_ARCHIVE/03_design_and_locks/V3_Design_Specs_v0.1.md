# Pramana v3 — Design Specs (병렬 산출 통합) v0.1
**Date:** 2026-06-11 · **출처:** Codex 설계상의 + 서브에이전트 2(데이터인프라·모니터링/거버넌스) + 척추 빌드. deep-research(모델선택)는 진행중→완료시 council 합산.

## A. 데이터 인프라 (ETF/LETF/선물) — agent probe 확정
- **모든 타깃 SHARADAR/SFP에 실재**(closeadj+volume, 2016–2026 번들창): SPY·QQQ·IWM·DIA·섹터SPDR(XLK/F/E/V/I)·**LETF TQQQ/SQQQ/UPRO/SPXU/SOXL/SOXS**·vol UVXY(ETF)·VXX(ETN).
- **LETF 가격 실재(decay 내장)**: TQQQ 실제 +3155% vs naive 3× +6520% → **반드시 실제 closeadj 사용, 3×index 합성 금지.** closeadj가 reverse split 정확 처리.
- **native 선물 없음**(SFP/SEP/SF1/SF3B만) → **선물=proxy ETF**(UVXY/VXX=VIX선물, 콘탱고 bleed=overlay/단기만). 진짜 term-structure는 별도 벤더(범위밖).
- **용량 $75k엔 무관**(최악 UVXY ≤0.024% ADV).
- **구현=1파일 스냅샷**: gated `snapshot_funds(allow_pull)` → `outputs/raw/SFP_FUNDS.csv`(FUND_LIST 큐레이트) + provenance + manifest + HASHES 1줄. **core data.py 변경 0**(load/manifest/validate 이름무관). VXX=ETN(issuer risk) 태그.

## B. 리스크엔진/실행/일간루프 — Codex 설계
- **일간 루프(29단계 척추):** run-lock → 데이터refresh → **manifest/hash 무결성**(불일치=data kill) → features → 합성 signal → eligible universe → sector-neutral target weights → vol추정→leverage scalar → **Kelly guard** → 유동성/borrow 필터 → **결정적 risk veto**(막히면 de-risk 주문만) → orders(현재→target) → fills(비용/슬리피지/borrow/부분체결) → positions/cash/financing → **ledger** → post-trade exposures → persist(atomic) → daily report → kill state → release lock.
- **실패처리:** refresh실패→manifest유효시 캐시만/아니면 data kill; manifest불일치→data kill; feature실패→무주문; risk실패→risk kill; exec실패→ledger 불변; partial write→temp+atomic rename.
- **idempotency:** run_id=sha256(date+config+manifest+code) → 동일시 기존반환. runs/{date}/{run_id}/{config·manifest·signals·targets·risk_decision·orders·fills·positions·ledger·report·kill_state}.
- **build-first:** ManifestVerifier·Ledger·SignalSnapshot·TargetBuilder·RiskEngine·PaperExecutionEngine·DailyRunner·ReportWriter. SKIP: 선물·LETF·intraday·복잡optimizer·tax·broker.
- **acceptance:** 동일입력→동일 orders/fills/NAV·corrupt manifest→data kill·gross>4x→veto·DD-15%→cooldown·order>ADV→부분체결·exec실패→ledger불변.

## C. 모니터링/킬스위치/거버넌스 — agent 스펙
- **원칙(LOCKED):** LLM=off-path advisory only·결정적 규칙이 order/veto/kill 트리거·human이 capital-at-risk 게이트·**fail-closed**(결측=breach).
- **모니터링 A~O**(daily, WARN/CRIT): 데이터freshness/무결성·NAV/PnL·DD·실현vol·gross/net·beta/corr·name/sector/factor 집중·turnover·borrow drift·signal IC drift·capacity. **WARN 3개 동시→CRIT 승격.**
- **kill K1~K5**(always-on, 래치, graded L1축소/L2halt/L3flat/L4shutdown): ①데이터무결성(hash불일치→즉시 flat) ②DD(-12→L1/-15→L2/-18→L3·cooldown≥10일·즉시 재risk 금지) ③vol폭발(>40%) ④**상관붕괴**(60d|β|>0.4 or |ρ|>0.5=시장중립 깨짐→halt) ⑤모델decay(120d IC-IR<0.2×backtest→halt). heartbeat 워치독(모니터 침묵→halt). 글로벌 수동 KILL=L4.
- **거버넌스:** 자동(daily mark·모니터·WARN·K1~K4 발화·de-lever). human 사인오프(capital-at-risk): kill override/re-arm·자본변경·모델/피처/비용가정 변경·**paper→live 승격**. **승격 게이트(STRICT, 현재 book FAIL): live-paper OOS ≥12mo·Sharpe≥0.8(현0.33=부적격)·maxDD≤15%·2×비용서 Sharpe≥0.5(현 5×사망=취약)·무결성 CRIT 0건·용량≥5×·첫 live ≤10%.** governance_log.csv(record_id·type·trigger·evidence·deterministic_checks_passed·ai_advisory(non-binding)·approver·decision·hash).
- **우선순위 P1(자동화 전 필수): 데이터무결성 kill + heartbeat**(프로세스 drift가 #1 위험). P2 DD/vol kill. P3 상관붕괴. P4 decay/signal health. P5 governance gate object.

## D. 척추 구현 결과 (engine/{risk_engine,book_runner}.py 실행)
- signal→risk_engine(사이징·veto·4 kill)→ledger→kill state 루프 **작동.** 110 리밸런스·beta −0.14·capacity $501M.
- 결과: CAGR +3.24%·**Sharpe 0.36**·**maxDD −18.1%**(aggr_book −26%보다 안전)·평균레버리지 1.00x(risk engine이 수익↔안전 트레이드). kill 50건(correlation_breakdown 26·model_decay 24).
- **Codex acceptance: 결정성 PASS·데이터무결성 kill PASS·레버리지 cap≤4 PASS·DD cooldown(미발동=DD가 -15% 안 침).**
- **calibration TODO:** correlation_breakdown 26회=12점 corr 추정 노이즈(과민) → 모니터 스펙대로 **60d β/ρ**로 교체. kill 임계값 전반 monitoring 스펙 수치로 보정.

## 다음 (deep-research 완료 트리거)
모델선택 deep-research(wplcn0l0v) → **council 합산 → 모델공간 결정**(empirical=ML 무증분·Codex=유죄추정 → 제약 예상). 이후 척추 증분: execution.py(per-name fills)·kill 임계값 보정·SFP_FUNDS 스냅샷·일간화. paper-only.
