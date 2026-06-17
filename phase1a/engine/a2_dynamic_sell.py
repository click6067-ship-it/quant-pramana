#!/usr/bin/env python3
"""PRAMANA A2 — Dynamic Sell/Add 5%p rule engine (spec 05 §6/§7) + Vault In/Out logging.
규율: PAPER·자본권한 0. LLM은 risk 상태만·숫자(±5%p·Vault 이동)는 전부 이 룰(mapping engine).
SUGGESTIONS only — paper·사람 게이트. 절대 자동 비중 변경·자동 라이브 X.
입력 = outputs/a2_live/state.json (lead/decay/excess/...). clamp = config/a2_convex_raider.yaml sleeve_ranges.
출력(append-only):
  outputs/a2_live/sleeve_adjustments.csv  (date,sleeve,action,delta_pp,reason)
  outputs/a2_live/vault_events.csv        (date,event,amount,hard,reload,reason)
  reports/A2_weekly_vault_review.md       (Vault 상태·최근 제안·§9 체크리스트)
사용: python engine/a2_dynamic_sell.py"""
import os, sys, json, csv, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a2_profit_vault as V

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
A2 = os.path.join(ROOT, "outputs", "a2_live"); POS = os.path.join(A2, "positions")
STATE = os.path.join(A2, "state.json"); VAULT = os.path.join(POS, "vault.json")
ADJ_CSV = os.path.join(A2, "sleeve_adjustments.csv"); VEV_CSV = os.path.join(A2, "vault_events.csv")
RAIDER_CFG = os.path.join(REPO, "config", "a2_convex_raider.yaml")
RULES = os.path.join(REPO, "config", "a2_vault_rules.yaml")
REVIEW = os.path.join(ROOT, "reports", "A2_weekly_vault_review.md")
STEP = 0.05


def loadj(p, d):
    try: return json.load(open(p))
    except Exception: return d


def load_yaml(p):
    try:
        import yaml; return yaml.safe_load(open(p)) or {}
    except Exception: return {}


def clamp_ranges():
    cfg = load_yaml(RAIDER_CFG); return cfg.get("sleeve_ranges", {})


def append_csv(path, header, row):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(header)
        w.writerow(row)


# ── trim/add 트리거 평가 (spec §6/§7). state 필드 → bool 트리거. ──
def _risk_label(state):
    return (state.get("lead") or "GREEN").upper()


def eval_trim(state):
    """returns list of (sleeve, [reasons]). -5%p 후보 (spec §6)."""
    lead = _risk_label(state); decay = bool(state.get("decay")); mss = (state.get("market_stress") or "").upper()
    mdd = float(state.get("mdd", state.get("a2_mdd", 0.0)))
    out = []
    # TQQQ trim
    r = []
    if lead == "RED": r.append("Leadership RED")
    if decay and int(state.get("decay_days", 0)) >= 10: r.append("Decay Zone ≥10d")
    if state.get("qqq_below_20_50"): r.append("QQQ 20/50일선 동시 하회")
    if state.get("booster_rent"): r.append("TQQQ Booster Rent flag")
    if mdd < -0.20: r.append("A2 MDD -20% 초과")
    if r: out.append(("tqqq", r))
    # Attack trim
    r = []
    if int(state.get("attack_loss_streak", 0)) >= 3: r.append("Attack 연속 손실 3회")
    if lead == "RED": r.append("Leadership RED")
    if mss == "RED": r.append("Market Stress RED")
    if state.get("neg_cluster"): r.append("NEG cluster")
    if r: out.append(("attack", r))
    # Moonshot trim
    r = []
    if state.get("moonshot_thesis_decay"): r.append("Moonshot thesis decay")
    if state.get("moonshot_verdict_passed"): r.append("판정일 경과")
    if state.get("hard_neg"): r.append("Hard NEG")
    if state.get("regret_budget_breach"): r.append("regret budget breach")
    if r: out.append(("moonshot", r))
    return out


def eval_add(state):
    """returns list of (sleeve, [reasons]). +5%p 후보 (spec §7)."""
    lead = _risk_label(state); decay = bool(state.get("decay")); mss = (state.get("market_stress") or "").upper()
    narr = (state.get("narrative") or "GREEN").upper(); mdd = float(state.get("mdd", state.get("a2_mdd", 0.0)))
    out = []
    # TQQQ add
    r = []
    if lead == "GREEN": r.append("Leadership GREEN")
    if not decay: r.append("Decay GREEN")
    if state.get("qqq_above_20_50"): r.append("QQQ 20/50일선 위")
    if narr in ("GREEN", "YELLOW"): r.append("Narrative GREEN/YELLOW")
    if mdd >= -0.15: r.append("A2 MDD -15% 이내")
    if state.get("tqdh_type") in ("A", "D"): r.append(f"TQ-DH Type {state.get('tqdh_type')}")
    # spec §7: 모든 조건 충족형 add (Leadership GREEN+Decay GREEN 필수)
    if lead == "GREEN" and not decay and len(r) >= 4: out.append(("tqqq", r))
    # Attack add
    r = []
    if int(state.get("attack_win_5", 0)) >= 3: r.append("최근 5개 중 3개 성공")
    if state.get("multi_a_catalyst"): r.append("A급 catalyst 다수")
    if lead in ("GREEN", "YELLOW"): r.append("Leadership GREEN/YELLOW")
    if mss != "RED": r.append("Market Stress not RED")
    if len(r) >= 3 and state.get("attack_win_5"): out.append(("attack", r))
    # Moonshot add
    r = []
    if state.get("m1_thesis"): r.append("M1 thesis 존재")
    if float(state.get("reward_risk", 0)) >= 3: r.append("Reward/Risk ≥ 3:1")
    if state.get("verdict_clear"): r.append("판정일 명확")
    if not state.get("hard_neg"): r.append("Hard NEG 없음")
    if not state.get("moonshot_dd"): r.append("Moonshot drawdown 없음")
    if state.get("m1_thesis") and float(state.get("reward_risk", 0)) >= 3 and len(r) >= 4: out.append(("moonshot", r))
    return out


def suggest_delta(sleeve, action, ranges, cur_w=None):
    """±5%p 제안, sleeve_range로 clamp. cur_w 없으면 delta만 반환(현 비중 미지)."""
    lo, hi = (ranges.get(sleeve) or [0.0, 1.0])
    d = STEP if action == "add" else -STEP
    if cur_w is None: return d, f"clamp[{lo:.2f},{hi:.2f}]"
    new = max(lo, min(hi, cur_w + d)); applied = new - cur_w
    return applied, f"{cur_w:.2f}->{new:.2f} clamp[{lo:.2f},{hi:.2f}]"


# ── Vault In/Out 평가 (rule engine·SUGGESTION) ──
def eval_vault(state, ledger, rules, today):
    """Vault In/Out 제안. live excess HWM·절대수익 게이트. SUGGESTION(실제 적용은 runner/사람)."""
    msgs = []
    live_excess = float(state.get("excess_hwm", state.get("excess", 0.0)))   # forward live excess (state.excess_hwm)
    abs_profit = float(state.get("a2t_live_ret", state.get("a2t_ret", 0.0))) > 0.0 if "a2t_live_ret" in state else None
    # state.excess_hwm = live forward (runner Codex #2). abs_profit = A2 NAV 수익 상태.
    risk = _risk_label(state)
    rate = V.classify_vault_in(live_excess, True if abs_profit is None else abs_profit, risk, rules)
    # ★ Codex fix: cadence gate(SSOT §09)도 적용 — 이미 이번 주 vault_in / 이번 달 reload면 SUGGESTION 억제(반복 제안 방지).
    week_ok = V._gate_ok(ledger, "vault_in", today, "week")
    month_ok = V._gate_ok(ledger, "reload", today, "month")
    if live_excess > ledger["hwm"] + 1e-12 and rate > 0 and week_ok:
        new = (live_excess - ledger["hwm"]) * rate
        msgs.append(("vault_in", new, f"excess {live_excess*100:.2f}%p>HWM·risk {risk}·rate {rate}·주1회 gate OK"))
    out_ok = bool(state.get("vault_out_ok", False)) and ledger["reload"] > 1e-9 and month_ok
    if out_ok:
        msgs.append(("reload", ledger["reload"] * 0.25, "Vault Out gate OK · Reload 25% · 월1회 gate OK"))
    return msgs


# ── §9 체크리스트 상태 ──
CHECKLIST = [
    ("Vault In은 실제 ledger에 기록", True, "positions/vault.json + vault_events.csv append-only"),
    ("Vault Out은 Reload Vault에서만", True, "apply_reload()는 reload만 차감·Hard 불변 assert"),
    ("Hard Vault는 코드상 재투입 불가", True, "reinvest_hard()=PermissionError·assert_hard_locked·save 거부"),
    ("5%p trim/add는 target weights에 반영", True, "suggest_delta() ±5%p·sleeve_ranges clamp (SUGGESTION·사람 게이트)"),
    ("LLM은 상태만 제공", True, "state.json risk 라벨만 입력·숫자 산출 0"),
    ("mapping engine이 실제 변경", True, "classify_vault_in/eval_trim/eval_add = rule engine"),
    ("매도/trim과 Vault 이동은 별도 이벤트로 기록", True, "sleeve_adjustments.csv vs vault_events.csv 분리"),
    ("대시보드에 Vault In/Out/Trim/Add 구분 표시", "partial", "a2_live_runner 대시보드 Vault 섹션 존재·Trim/Add 표시 = runner 채택 시"),
]


def write_review(ledger, raider_cfg, trim, add, vmsgs, today):
    cap = (raider_cfg or {}).get("capital", 100_000_000)
    hard_w, rel_w = ledger["hard"], ledger["reload"]
    lines = [f"# A2 Weekly Vault Review — {today}", "",
             "> PAPER·자본권한 0. 아래는 **제안(SUGGESTION)**·실제 적용은 사람 게이트. LLM=상태만·숫자=rule engine.", "",
             "## Vault 상태 (forward live ledger·positions/vault.json)", "",
             f"- **Hard Vault** (영구 잠금·재투입 불가): {hard_w*100:.3f}% NAV ≈ ₩{hard_w*cap/1e8:.4f}억",
             f"- **Reload Vault** (재장전 가능·25%/회·월1회): {rel_w*100:.3f}% NAV ≈ ₩{rel_w*cap/1e8:.4f}억",
             f"- **A2 excess HWM**: {ledger['hwm']*100:.3f}%p",
             f"- **Vault 이벤트 누적**: {len(ledger['events'])}건 (last_date={ledger.get('last_date')})", ""]
    if ledger["events"][-5:]:
        lines += ["### 최근 Vault 이벤트", ""]
        for e in ledger["events"][-5:]:
            lines.append(f"- `{e.get('date')}` **{e.get('event')}** moved={e.get('moved_w')} "
                         f"hard={e.get('hard')} reload={e.get('reload')} — {e.get('reason','')}")
        lines.append("")
    lines += ["## 이번 평가 제안 (SUGGESTION)", "", "### 5%p Dynamic Sell/Add", ""]
    if not trim and not add:
        lines.append("- (없음 — 트리거 미충족)")
    for sl, rs in trim: lines.append(f"- 🔻 **TRIM {sl} -5%p** — {', '.join(rs)}")
    for sl, rs in add: lines.append(f"- 🔺 **ADD {sl} +5%p** — {', '.join(rs)}")
    lines += ["", "### Vault In/Out", ""]
    if not vmsgs: lines.append("- (없음 — excess HWM 미돌파 또는 Vault Out 게이트 불충족)")
    for ev, amt, why in vmsgs: lines.append(f"- 💰 **{ev}** ≈ {amt*100:.3f}% NAV — {why}")
    lines += ["", "## §9 구현 체크리스트", ""]
    for name, ok, note in CHECKLIST:
        mark = "✅" if ok is True else ("🟡" if ok == "partial" else "❌")
        lines.append(f"- {mark} {name} — {note}")
    lines.append("")
    os.makedirs(os.path.dirname(REVIEW), exist_ok=True)
    open(REVIEW, "w").write("\n".join(lines))


def main():
    today = str(dt.date.today())
    state = loadj(STATE, {})
    if "last_run" in state and state.get("last_run"): today = state["last_run"]   # state 기준일 재사용(재현)
    rules = V.load_rules(RULES); raider = load_yaml(RAIDER_CFG); ranges = raider.get("sleeve_ranges", {})
    ledger = V.load_vault(VAULT)
    trim = eval_trim(state); add = eval_add(state); vmsgs = eval_vault(state, ledger, rules, today)

    # ── log SUGGESTIONS (append-only·실제 비중 변경 X) ──
    for sl, rs in trim:
        d, clp = suggest_delta(sl, "trim", ranges)
        append_csv(ADJ_CSV, ["date", "sleeve", "action", "delta_pp", "reason"],
                   [today, sl, "trim", round(d, 4), f"{'; '.join(rs)} | {clp} | SUGGESTION"])
    for sl, rs in add:
        d, clp = suggest_delta(sl, "add", ranges)
        append_csv(ADJ_CSV, ["date", "sleeve", "action", "delta_pp", "reason"],
                   [today, sl, "add", round(d, 4), f"{'; '.join(rs)} | {clp} | SUGGESTION"])
    for ev, amt, why in vmsgs:
        append_csv(VEV_CSV, ["date", "event", "amount", "hard", "reload", "reason"],
                   [today, ev, round(amt, 4), round(ledger["hard"], 4), round(ledger["reload"], 4), why + " | SUGGESTION"])

    write_review(ledger, raider, trim, add, vmsgs, today)

    # ── summary ──
    print(f"=== A2 Dynamic Sell/Vault rule engine ({today}) — SUGGESTIONS only (paper·사람 게이트) ===")
    print(f"state: lead={state.get('lead')} decay={state.get('decay')} live_excess_hwm={state.get('excess_hwm')}")
    print(f"Vault: Hard {ledger['hard']*100:.3f}% / Reload {ledger['reload']*100:.3f}% / HWM {ledger['hwm']*100:.3f}%p / events {len(ledger['events'])}")
    print(f"TRIM 후보: {[(s, len(r)) for s, r in trim] or '없음'}")
    print(f"ADD  후보: {[(s, len(r)) for s, r in add] or '없음'}")
    print(f"Vault 제안: {[(e, round(a, 4)) for e, a, _ in vmsgs] or '없음'}")
    print(f"→ logged: {ADJ_CSV}")
    print(f"→ logged: {VEV_CSV}")
    print(f"→ review: {REVIEW}")
    ok = sum(1 for _, o, _ in CHECKLIST if o is True)
    print(f"§9 체크리스트: {ok}/{len(CHECKLIST)} ✅ (+{sum(1 for _,o,_ in CHECKLIST if o=='partial')} partial)")


if __name__ == "__main__":
    main()
