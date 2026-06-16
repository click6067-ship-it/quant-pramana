#!/usr/bin/env python3
"""'왜' 해석 섹션 — 교수 예상질문 Q&A. 왜 알파가 실패했나·왜 이 그래프·왜 이 결론.
render_why_section(n)을 dashboard가 호출. 정적·접근성 우선·핵심 포함."""
import os
LANG = os.environ.get("PRAMANA_LANG", "ko")
def _t(ko, en): return en if LANG == "en" else ko

WHY = [
    (_t("Q. 왜 <u>모든 알파가 실패</u>했나? (가장 중요)", "Q. Why did <u>every alpha fail</u>? (the most important question)"), [
        _t("알파 = 시장이 <b>아직 모르는</b> 비효율. 그런데 내가 쓴 건 전부 <b>공개 데이터 + 이미 알려진 방법</b>(교과서 팩터·차트 기술). 알려진 신호는 모두가 동시에 거래해 <b>가격에 즉시 반영(arbitraged away)</b>되고 프리미엄이 사라진다.",
           "Alpha = an inefficiency the market <b>doesn't yet know about</b>. But everything I used was <b>public data + already-known methods</b> (textbook factors, chart techniques). Known signals get traded by everyone at once, get <b>instantly priced in (arbitraged away)</b>, and the premium disappears."),
        _t("미국 대형주는 지구에서 가장 효율적·경쟁 치열한 시장. SPIVA 통계상 15년에 액티브 펀드 약 90%가 S&amp;P500에 진다. <b>솔로가 공개 데이터로 비용 후 초과</b>할 확률은 0에 가깝다.",
           "US large caps are the most efficient, most competitive market on earth. Per SPIVA, over 15 years about 90% of active funds lose to the S&amp;P500. The odds that <b>a solo researcher beats it after costs with public data</b> are close to zero."),
        _t("진짜 알파의 원천(비공개 정보 우위·구조적 위험 인수·실행 속도·자본 capacity)은 솔로+공개 데이터에 없다.",
           "The real sources of alpha (a non-public information edge, taking on structural risk, execution speed, capital capacity) aren't available to a solo researcher with public data."),
        _t("→ 이건 '실패'가 아니라 <b>효율적 시장의 정직한 확인</b>이고, 8세대 내내 <b>가짜 알파를 안 만든 것</b>이 진짜 성과다.",
           "→ This isn't a 'failure' but an <b>honest confirmation of efficient markets</b>, and the real achievement is that across 8 generations <b>I never manufactured fake alpha</b>."),
    ]),
    (_t("Q. 왜 <u>이런 그래프</u>가 나왔나? (차트별 인과)", "Q. Why did <u>these charts</u> come out this way? (the cause behind each chart)"), [
        _t("<b>팩터 IC≈0:</b> 알려진 팩터(value·momentum…)는 이미 모두가 알아 가격에 반영 → 다음 달 수익 예측력이 0.",
           "<b>Factor IC ≈ 0:</b> known factors (value, momentum…) are already known by everyone and priced in → zero power to predict next month's return."),
        _t("<b>어떤 모델도 SPY/QQQ를 못 이김:</b> 효율적 시장 + 거래비용. 분산·안정화는 위험을 낮출 뿐 초과수익을 만들지 못한다.",
           "<b>No model beats SPY/QQQ:</b> efficient markets + trading costs. Diversification and stabilization only lower risk; they don't create excess return."),
        _t("<b>TQQQ 376배인데 −82%:</b> 강세장에서 레버리지가 복리로 증폭된 것(베타×3)이지 알파가 아니다. −82%는 레버의 구조적 대가.",
           "<b>TQQQ is 376x but −82%:</b> that's leverage compounding in a bull market (beta ×3), not alpha. The −82% is the structural price of leverage."),
        _t("<b>VT가 고정선보다 왼쪽:</b> 변동성을 통제해 같은 수익을 <b>덜 위험하게</b> 가져간 것(레버 decay 회피). 알파가 아니라 '리스크 형태' 개선.",
           "<b>VT sits to the left of the fixed line:</b> by controlling volatility it earned the same return <b>with less risk</b> (avoiding leverage decay). Not alpha, but an improvement in the 'shape of the risk'."),
        _t("<b>타이밍 알파가 전부 음수:</b> 신호가 후행 + 레버 자산은 폭락 직후 급반등(V자 회복) → 위험할 때 줄이면 그 반등을 놓친다 → 현금 드래그가 방어 이득보다 크다.",
           "<b>Timing alpha is all negative:</b> signals lag + levered assets snap back sharply right after a crash (V-shaped recovery) → trimming when it's risky misses that bounce → the cash drag exceeds the defensive benefit."),
    ]),
    (_t("Q. 어떤 <u>방식</u>으로 실험했나?", "Q. What <u>approach</u> did you experiment with?"), [
        _t("<b>최적화가 아니라 falsification(죽이기).</b> 결과를 보기 전에 '못 이기면 폐기'할 기준을 박고(사전등록), 그걸 못 넘으면 정직하게 버린다.",
           "<b>Not optimization but falsification (killing).</b> Before seeing results, I lock in a 'discard it if it can't win' criterion (pre-registration); if it doesn't clear that bar, I honestly throw it away."),
        _t("<b>next-bar</b>(다음날 체결)·<b>PIT 데이터</b>(그날 알 수 있던 값만)·<b>비용 포함</b>·<b>OOS 분리</b>·<b>Codex 적대 교차검증</b>이 전부 '가짜로 좋아 보이는 것'을 거르는 장치. (자세한 수식·절차 = 섹션 7)",
           "<b>next-bar</b> (fill the next day) · <b>PIT data</b> (only values knowable that day) · <b>costs included</b> · <b>OOS split</b> · <b>Codex adversarial cross-validation</b> are all safeguards that filter out 'things that only look good by accident'. (Detailed formulas and procedure = Section 7.)"),
    ]),
    (_t("Q. 그래서 왜 결론이 <u>'vol-target'</u>인가?", "Q. So why is the conclusion <u>'vol-target'</u>?"), [
        _t("미래 수익은 <b>추정이 안 된다</b>(20일 기대수익을 안정적으로 못 맞힌다). 예측이 안 되면 통제할 수 있는 건 <b>위험의 크기</b>뿐이다.",
           "Future returns <b>can't be estimated</b> (you can't reliably predict the 20-day expected return). If you can't forecast, the only thing you can control is <b>the amount of risk</b>."),
        _t("변동성으로 노출을 조절하면 <b>알파 없이도</b> TQQQ 낙폭을 −82%→−42%로 절반으로 줄인다. 예측 0의 정직한 최선 = <b>'버틸 수 있는 레버'</b>.",
           "Adjusting exposure by volatility halves TQQQ's drawdown from −82% to −42% <b>without any alpha</b>. The honest best you can do with zero forecast = <b>'leverage you can live through'</b>."),
    ]),
    (_t("Q. 그래서 <u>직접 작동</u>은 하나? (live)", "Q. So does it <u>actually run live</u>?"), [
        _t("네 — paper forward 러너가 <b>cron으로 자동</b> 돌아갑니다. 데이터는 <b>Sharadar(유료·PIT)</b> primary(yfinance는 fallback)·fail-closed·append-only. 라이브 데모: VT-CANON·v7·Static 70/30 + SPY/QQQ/TQQQ를 ₩1억으로 지난주부터 forward. <a href=\"https://click6067-ship-it.github.io/quant-pramana/pramana_live.html\" target=\"_blank\" style=\"color:var(--accent);font-weight:700\">▶ 라이브 차트 보기</a>",
           "Yes — paper forward runners run <b>automatically via cron</b>. Data is <b>Sharadar (paid·PIT)</b> primary (yfinance is only a fallback), fail-closed, append-only. Live demo: VT-CANON, v7, Static 70/30 + SPY/QQQ/TQQQ run forward from ₩100M since last week. <a href=\"https://click6067-ship-it.github.io/quant-pramana/pramana_live.html\" target=\"_blank\" style=\"color:var(--accent);font-weight:700\">▶ Open live chart</a>"),
        _t("정직하게: <b>PAPER · 자본권한 0 · 일봉(EOD) 기준.</b> 분봉 체결·실계좌·2-피드 대조는 유료 분봉+브로커가 필요해 보류 — '시스템이 돈다'의 증명이지 수익 주장 아님.",
           "Honestly: <b>PAPER · zero capital authority · daily (EOD) basis.</b> Intraday fills, a real account, and 2-feed reconciliation need paid intraday data + a broker, so they're deferred — this proves 'the system runs', not a profit claim."),
    ]),
    (_t("Q. 왜 <u>딥러닝 / TSFM / Chronos</u>를 안 쓰나?", "Q. Why not use <u>deep learning / TSFM / Chronos</u>?"), [
        _t("<b>신호가 없는데 모델이 클수록 과적합만 커진다.</b> 8세대 내내 예측 신호가 0이었어요. 더 큰 망치가 없는 못을 찾아주진 않습니다. 공개 일별 주식은 SNR이 낮고 비정상(non-stationary)이라 DL이 잡을 안정적 패턴이 없어요.",
           "<b>When there's no signal, a bigger model just overfits more.</b> Across 8 generations the predictive signal was zero. A bigger hammer doesn't find a nail that isn't there. Public daily equities have low signal-to-noise and are non-stationary — there's no stable pattern for DL to latch onto."),
        _t("문헌·자체 실증: ML 알파의 OOS R²는 ~0.3–0.4%(GKX)에 불과하고, 제 bake-off에서도 ridge·GBM이 단순 선형 블렌드를 못 넘었습니다. → <b>ML/TSFM은 '알파 엔진'으로는 기각.</b>",
           "Literature + my own tests: ML alpha's OOS R² is only ~0.3–0.4% (Gu-Kelly-Xiu), and in my own bake-off ridge and GBM couldn't beat a simple linear blend. → <b>ML/TSFM are rejected as the 'alpha engine'.</b>"),
        _t("<b>TSFM(Chronos 등)은 내일 수익을 예측하지 않습니다</b> — off-path로 격리해 *overlay/meta-labeler* challenger로만, 그것도 비용 후 OOS로 baseline을 이겨야 채택. 'DL이 쓸모없다'가 아니라 '이 문제(공개 일별·저SNR)의 알파 원천으로는 부적합'이라는 뜻.",
           "<b>TSFM (Chronos, etc.) don't forecast tomorrow's return</b> — they're quarantined off-path as an *overlay / meta-labeler* challenger only, and even then must beat the baseline OOS after cost to be adopted. Not 'DL is useless', but 'unfit as the alpha source for this problem (public daily, low SNR)'."),
    ]),
]


def render_why_section(n=8):
    cards = []
    for q, bullets in WHY:
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        cards.append(f'<div class="qcard"><div class="qq">{q}</div><ul class="qa">{lis}</ul></div>')
    return f"""
<section>
<h2><span class="n">{n}</span>{_t("왜 이런 결과가 나왔나 — 해석", "Why these results came out this way — interpretation")}</h2>
<p class="sub">{_t('"왜 이 그래프? 왜 이 결론? 왜 알파가 다 실패했나?"에 대한 인과적 답. 결과(2~6) + 방법(7)을 \'왜\'로 잇는다.', 'A causal answer to "why this chart? why this conclusion? why did every alpha fail?" It ties the results (2–6) and the method (7) together through the "why".')}</p>
{''.join(cards)}
</section>"""
