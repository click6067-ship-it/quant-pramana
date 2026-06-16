#!/usr/bin/env python3
"""방법론 섹션 — 데이터(무엇/왜/특징)·핵심 수식(쉽게)·검증 7장치. 정적 HTML.
render_methodology_section(n)을 dashboard가 호출. 사실은 docs/context·리포트 기록값."""
import os
LANG = os.environ.get("PRAMANA_LANG", "ko")
def _t(ko, en): return en if LANG == "en" else ko

DATA = [
    ("Sharadar SEP", _t("유료·PIT", "paid·PIT"), _t("미국 주식 일별 종가(배당조정 closeadj)", "US equity daily close (dividend-adjusted closeadj)"), _t("백테스트 주가 기준선", "backtest price baseline"),
     _t("PIT=시점고정 → 생존편향·미래누수 없음", "PIT = point-in-time → no survivorship bias or look-ahead leakage")),
    ("Sharadar SFP", _t("유료·PIT", "paid·PIT"), _t("ETF 펀드 가격(closeadj)", "ETF fund prices (closeadj)"), _t("벤치·sleeve(SPY/QQQ 등)", "benchmarks · sleeves (SPY/QQQ, etc.)"), _t("ETF 배당조정가", "dividend-adjusted ETF prices")),
    ("Sharadar DAILY", _t("유료·PIT", "paid·PIT"), _t("시가총액(역사적)", "market cap (historical)"), _t("cap-weight 지수 자작", "self-built cap-weighted index"), _t("historical marketcap(현재값 아님)", "historical marketcap (not the current value)")),
    ("Sharadar SF1", _t("유료·PIT", "paid·PIT"), _t("펀더멘털(gp/assets 등)", "fundamentals (gp/assets, etc.)"), _t("quality 팩터", "quality factor"), _t("PIT-by-datekey(공시시점 반영)", "PIT-by-datekey (reflects the filing date)")),
    ("Sharadar TICKERS·ACTIONS·SP500", _t("유료·PIT", "paid·PIT"), _t("상폐·배당·지수 멤버십", "delistings · dividends · index membership"), _t("생존편향 제거·PIT 유니버스", "survivorship-free · PIT universe"), _t("permaticker·isdelisted·as-of 멤버십", "permaticker · isdelisted · as-of membership")),
    ("yfinance", _t("무료", "free"), "TQQQ/QQQ/SPY/DBMF/GLD/IEF (2010~)", _t("TQQQ 인셉션(2010) 도달·fallback", "reaches TQQQ inception (2010) · fallback"), _t("auto_adjust·sanity 교차검증용", "auto_adjust · for sanity cross-checks")),
    ("SEC EDGAR", _t("무료", "free"), _t("8-K 공시(실적·뉴스·34,381건/200종)", "8-K filings (earnings · news · 34,381 across 200 names)"), _t("catalyst·이벤트 스터디(A1/A2 attack)", "catalyst · event study (A1/A2 attack)"), _t("acceptanceDateTime=실제 공개시각 → look-ahead 차단", "acceptanceDateTime = actual publication time → blocks look-ahead")),
    ("^IRX (T-bill)", _t("무료", "free"), _t("단기 국채 금리", "short-term Treasury yield"), _t("현금 수익률(0% 아님)", "cash return (not 0%)"), _t("레버 vol-target의 cash sleeve(연 ~4-5%)", "cash sleeve of the levered vol-target (~4–5%/yr)")),
]

FORMULAS = [
    (_t("vol-target 비중", "vol-target weight"), _t("w_t = clip( 목표변동성 ÷ 최근변동성 , 0 , 상한 )", "w_t = clip( target vol ÷ recent vol , 0 , cap )"),
     _t("변동성이 크면 TQQQ 비중을 줄이고, 작으면 늘린다. <b>미래 예측 0</b> — 위험량만 조절.", "When volatility is high, cut the TQQQ weight; when low, raise it. <b>No forecast of the future</b> — it only adjusts the amount of risk.")),
    (_t("최근 변동성(realized vol)", "recent (realized) volatility"), _t("σ = (최근 21일 일수익 표준편차) × √252", "σ = (std dev of daily returns over the last 21 days) × √252"),
     _t("최근 한 달 '출렁임' 크기를 연율로 환산.", "Converts the last month's 'choppiness' into an annualized figure.")),
    (_t("next-bar 실행", "next-bar execution"), _t("오늘 종가 신호 → <b>내일</b> 체결", "signal at today's close → fill <b>tomorrow</b>"),
     _t("오늘 본 정보로 오늘 사고팔지 않는다 = same-day 미래정보 누수 차단.", "We never trade today on information we saw today = blocks same-day look-ahead leakage.")),
    (_t("팩터 예측력 IC-IR", "factor predictive power IC-IR"), _t("IC-IR = 평균(Rank IC) ÷ 표준편차(Rank IC)", "IC-IR = mean(Rank IC) ÷ std dev(Rank IC)"),
     _t("팩터가 다음달 수익을 <b>일관되게</b> 맞히나. 0.3 넘어야 거래가치 — 우린 전부 &lt;0.05(노이즈).", "Does the factor predict next month's return <b>consistently</b>? It must clear 0.3 to be worth trading — ours were all &lt;0.05 (noise).")),
    (_t("Timing Log Alpha (핵심 판정)", "Timing Log Alpha (the key verdict)"), _t("Σ ln(1+정책수익) − Σ ln(1+같은평균비중 고정전략수익)", "Σ ln(1+policy return) − Σ ln(1+fixed-strategy return at same avg weight)"),
     _t("내 타이밍이 '그냥 같은 비중 들고 있기'보다 <b>복리로</b> 나았나. 양수=진짜 타이밍 / 음수=노출효과. 결과: 전부 음수.", "Did my timing beat 'just holding the same weight' on a <b>compound</b> basis? Positive = real timing / negative = exposure effect. Result: all negative.")),
    (_t("레버드 ETF 기대 로그성장", "expected log growth of a levered ETF"), "≈ 3μ − 4.5σ²",
     _t("3배 ETF는 변동성(σ²)이 수익을 갉아먹는다(decay). 그래서 '변동성 통제'가 레버의 핵심.", "For a 3x ETF, volatility (σ²) eats into returns (decay). That's why 'volatility control' is the core of leverage.")),
    (_t("상방 capture / 고통 회피", "upside capture / pain avoided"), _t("capture = ln(내배수) ÷ ln(TQQQ배수) · pain회피 = 1 − 내낙폭 ÷ TQQQ낙폭", "capture = ln(my ×) ÷ ln(TQQQ ×) · pain avoided = 1 − my drawdown ÷ TQQQ drawdown"),
     _t("TQQQ 상방을 몇 % 따라갔고, TQQQ 고통을 몇 % 피했나(절대합 척도).", "What % of TQQQ's upside you captured, and what % of TQQQ's pain you avoided (a net trade-off measure).")),
    (_t("낙폭 회복의 비선형성", "the non-linearity of drawdown recovery"), _t("회복 필요수익 = 1 ÷ (1 − 낙폭) − 1", "return needed to recover = 1 ÷ (1 − drawdown) − 1"),
     _t("−42%는 +72%, −82%는 +456% 올라야 본전. 그래서 낙폭이 수익만큼 중요.", "−42% needs +72%, −82% needs +456% just to break even. That's why drawdown matters as much as return.")),
]

PROCEDURE = [
    (_t("① 모든 전략을 'w_t' 하나로 환원", "① Reduce every strategy to a single 'w_t'"),
     _t("복잡한 상태기계든 vol-target이든, 결국 매일 <b>'오늘 TQQQ 몇 %, 현금 몇 %'</b>를 정하는 기계다. "
        "하루 수익 = <code>w_t × TQQQ수익 + (1−w_t) × 현금수익 − 비용</code>. 이렇게 환원하면 모든 모델을 같은 잣대로 비교 가능.",
        "Whether it's a complex state machine or a vol-target, every strategy is ultimately a machine that decides <b>'how much TQQQ and how much cash today'</b>. "
        "Daily return = <code>w_t × TQQQ return + (1−w_t) × cash return − costs</code>. Reducing them this way lets you compare every model on the same yardstick.")),
    (_t("② 각 정책이 w_t를 정하는 규칙 (전날까지 정보만)", "② The rule each policy uses to set w_t (only information up to the prior day)"),
     _t("<b>VT(vol-target):</b> w = 목표변동성 ÷ 최근21일 변동성(예측 0·위험만 조절). "
        "<b>C1:</b> 충격(−8%/5일)·추세이탈이면 w=0(현금), 아니면 VT 비중으로 하루 ≤5%p씩 복귀. "
        "<b>C2:</b> C1 + 변동성 식는 구간이면 VT의 절반. <b>C3:</b> 고정 70% base + 상태 게이트. "
        "★ 모든 신호는 <b>전날 종가까지만</b> 써서 다음날 적용(next-bar) → 미래정보 0.",
        "<b>VT (vol-target):</b> w = target vol ÷ trailing-21-day vol (no forecast, only adjusts risk). "
        "<b>C1:</b> on a shock (−8% over 5 days) or trend break, w=0 (cash); otherwise ramp back toward the VT weight by ≤5pp/day. "
        "<b>C2:</b> C1 + when volatility is cooling, half the VT weight. <b>C3:</b> a fixed 70% base + state gates. "
        "★ Every signal uses <b>only data through the prior close</b> and is applied the next day (next-bar) → zero look-ahead.")),
    (_t("③ '진짜 타이밍'인지 가르는 법 — exposure-matched 비교", "③ How we tell 'real timing' apart — an exposure-matched comparison"),
     _t("정책의 <b>평균 비중</b>(예: 64%)을 구해, 똑같이 <b>64%를 고정</b>으로 든 멍청한 전략을 만든다. "
        "둘을 복리로 비교(<b>Timing Log Alpha</b>). 정책이 그 고정전략을 못 이기면 = 수익은 '타이밍 실력'이 아니라 "
        "'그냥 TQQQ를 그만큼 들고 있었던' <b>노출 효과</b>. (결과: 모든 정책이 음수 = 노출 효과)",
        "Take the policy's <b>average weight</b> (e.g. 64%) and build a dumb strategy that just holds a <b>fixed 64%</b>. "
        "Compound-compare the two (<b>Timing Log Alpha</b>). If the policy can't beat that fixed strategy, the returns aren't 'timing skill' — "
        "they're the <b>exposure effect</b> of 'simply having held that much TQQQ'. (Result: every policy is negative = exposure effect.)")),
    (_t("④ 수익 원천 분해 (attribution)", "④ Decompose where the returns came from (attribution)"),
     _t("<b>Timing P&amp;L</b>=Σ(w_t−평균)×(TQQQ−현금) [좋을 때 더 들었나] · "
        "<b>Cash Drag vs Defense</b> [현금화가 놓친 상승 vs 피한 하락] · "
        "<b>Missed Recovery</b> [폭락 후 반등을 현금이라 놓쳤나]로 쪼개 '왜 그 결과인지' 규명.",
        "<b>Timing P&amp;L</b> = Σ(w_t−avg)×(TQQQ−cash) [did it hold more when it was good?] · "
        "<b>Cash Drag vs Defense</b> [upside missed by going to cash vs downside avoided] · "
        "<b>Missed Recovery</b> [did being in cash miss the post-crash bounce?] — split this way to pin down 'why the result is what it is'.")),
    (_t("⑤ 사전등록 falsification 순서 (A4-0)", "⑤ The pre-registered falsification sequence (A4-0)"),
     _t("baseline 먼저 측정 → 진단 히트맵(<b>진단 only·셀로 규칙 만들기 금지</b>) → 후보 3~5개를 "
        "<b>결과 보기 전에</b> 등록 → full-path로 pseudo-OOS(2022~26)·purged folds 검증 → "
        "vol-target을 못 이기면 <b>미리 박아둔 NULL(실패)</b> 발동. 결과 보고 후보 추가·임계값 튜닝 <b>금지</b>.",
        "Measure the baseline first → build a diagnostic heatmap (<b>diagnosis only · no building rules from cells</b>) → register 3–5 candidates "
        "<b>before seeing any results</b> → validate full-path on pseudo-OOS (2022–26) and purged folds → "
        "if it can't beat vol-target, the <b>pre-set NULL (failure)</b> fires. Adding candidates or tuning thresholds after seeing results is <b>forbidden</b>.")),
]

CHECKS = [
    (_t("PIT 데이터", "PIT data"), _t("'그 시점에 실제로 알 수 있던' 값만 사용 → <b>미래정보 누수·생존편향</b>(살아남은 종목만 보기) 원천 차단. 가짜 알파의 2대 원인.", "Uses only values that were 'actually knowable at that point in time' → cuts off <b>look-ahead leakage and survivorship bias</b> (only looking at the stocks that survived) at the source. The two biggest causes of fake alpha.")),
    (_t("next-bar 실행", "next-bar execution"), _t("신호 다음날 체결 → same-day 누수 차단.", "Fill the day after the signal → blocks same-day leakage.")),
    (_t("사전등록 (falsification)", "pre-registration (falsification)"), _t("결과를 보기 <b>전에</b> 성공/실패·kill 기준을 박는다. '좋은 것만 골라보기' 차단. <b>NULL(실패)도 미리 등록</b> → 억지로 살리기 금지.", "Lock in the success/failure and kill criteria <b>before</b> seeing results. Blocks 'cherry-picking the good ones'. <b>The NULL (failure) is registered in advance too</b> → no forcing a dead result back to life.")),
    (_t("비용 포함", "costs included"), _t("회전율 × 스프레드(bp) + 현금은 T-bill 수익. → 종이수익(비용 전 환상) 차단.", "Turnover × spread (bp) + cash earns the T-bill yield. → blocks paper returns (the pre-cost illusion).")),
    (_t("OOS 분리 + purged walk-forward", "OOS split + purged walk-forward"), _t("2010~21 설계 / 2022~26 pseudo-OOS 검증. forward 라벨 겹침은 embargo로 격리.", "Design on 2010–21 / validate pseudo-OOS on 2022–26. Overlapping forward labels are isolated by an embargo.")),
    (_t("다중검정 보정 (DSR·PBO)", "multiple-testing correction (DSR·PBO)"), _t("여러 번 시도하면 우연히 좋아 보인다 → Deflated Sharpe·Probability of Backtest Overfitting로 깎아냄.", "Try many times and something looks good by chance → discount it with the Deflated Sharpe ratio and the Probability of Backtest Overfitting.")),
    (_t("적대 교차검증 (Claude×Codex)", "adversarial cross-validation (Claude×Codex)"), _t("Claude가 만들면 Codex가 <b>코드 안 본 채 차갑게</b> 깬다(no-echo). 이걸로 look-ahead 2건(RVOL·A2 same-day) 실제 적발.", "When Claude builds it, Codex tears it apart <b>cold, without seeing the code</b> (no-echo). This actually caught 2 look-ahead bugs (RVOL · A2 same-day).")),
]


def render_methodology_section(n=7):
    drows = "".join(
        f'<tr><td><b>{src}</b><br><span class="tag">{kind}</span></td><td>{what}</td><td>{why}</td><td>{feat}</td></tr>'
        for src, kind, what, why, feat in DATA)
    frows = "".join(
        f'<div class="fcard"><div class="fname">{name}</div><div class="fexpr"><code>{expr}</code></div>'
        f'<div class="fplain">{_t("쉽게 — ", "In plain terms — ")}{plain}</div></div>'
        for name, expr, plain in FORMULAS)
    prows = "".join(
        f'<div class="pcard"><div class="pname">{name}</div><div class="pdesc">{desc}</div></div>'
        for name, desc in PROCEDURE)
    crows = "".join(
        f'<li><b>{i+1}. {name}</b> — {desc}</li>' for i, (name, desc) in enumerate(CHECKS))
    return f"""
<section>
<h2><span class="n">{n}</span>{_t("방법론 — 데이터·수식·검증 (가짜 알파를 어떻게 걸렀나)", "Methodology — data, formulas, verification (how we filtered out fake alpha)")}</h2>
<p class="sub">{_t("이 모든 숫자가 '진짜'인지 어떻게 보장했나. 최대한 쉽게, 핵심만.", "How we made sure all these numbers are 'real'. As simply as possible, just the essentials.")}</p>

<h3 style="margin:14px 0 8px;font-size:16px">{_t("① 어떤 데이터를 왜 썼나", "① What data we used and why")}</h3>
<div style="overflow-x:auto">
<table class="dtab"><thead><tr><th>{_t("데이터", "Source")}</th><th>{_t("무엇", "What")}</th><th>{_t("왜", "Why")}</th><th>{_t("특징", "Characteristics")}</th></tr></thead>
<tbody>{drows}</tbody></table></div>
<p class="cap">{_t("<b>왜 Sharadar(유료)?</b> = 가장 싼 <b>깨끗한 PIT 데이터.</b> PIT(Point-In-Time)는 '과거 그날 실제로 알 수 있던 값'만 줘서 — <b>미래정보 누수</b>와 <b>생존편향</b>(살아남은 종목만 보기)을 막는다. 이 둘이 가짜 알파의 최대 원인이라 제일 중요. 무료 yfinance는 2010년(TQQQ 탄생)까지 닿아서 TQQQ 실험·교차검증에 씀.", "<b>Why Sharadar (paid)?</b> = the cheapest <b>clean PIT data.</b> PIT (Point-In-Time) gives only 'the values that were actually knowable on that past day' — preventing <b>look-ahead leakage</b> and <b>survivorship bias</b> (only looking at the stocks that survived). These two are the biggest causes of fake alpha, so this matters most. Free yfinance reaches back to 2010 (TQQQ's birth), so we use it for TQQQ experiments and cross-checks.")}</p>

<h3 style="margin:22px 0 8px;font-size:16px">{_t("② 핵심 수식 (쉽게)", "② Key formulas (made simple)")}</h3>
<div class="fgrid">{frows}</div>

<h3 style="margin:22px 0 8px;font-size:16px">{_t("③ 타이밍을 <u>어떻게 계산하고 검증했나</u> (실험 절차)", "③ <u>How we computed and validated timing</u> (the experimental procedure)")}</h3>
<p class="cap" style="margin:0 0 10px">{_t('"타이밍을 무슨 방식으로 계산했나?"의 단계별 답.', 'A step-by-step answer to "how exactly did you compute the timing?"')}</p>
<div class="pflow">{prows}</div>

<h3 style="margin:22px 0 8px;font-size:16px">{_t("④ 가짜 알파 거르는 검증 7장치", "④ The 7 safeguards that filter out fake alpha")}</h3>
<ul class="checklist">{crows}</ul>
<p class="cap">{_t("+ <b>파이프라인 검증:</b> 직접 만든 PIT S&amp;P500 cap-weight 지수가 <b>실제 SPY와 상관 0.998</b> = 데이터·처리(배당·상폐·멤버십)가 정확하다는 강한 증거. <b>도구는 정확했고, 단지 찾을 알파가 없었다.</b>", "+ <b>Pipeline validation:</b> our self-built PIT S&amp;P500 cap-weighted index has <b>0.998 correlation with the real SPY</b> = strong evidence that the data and its handling (dividends, delistings, membership) are accurate. <b>The tools were correct; there simply was no alpha to find.</b>")}</p>
</section>"""
