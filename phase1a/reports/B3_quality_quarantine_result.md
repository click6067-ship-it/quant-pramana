# B3 Quality (gp/assets) — Quarantine 검증 결과

**날짜:** 2026-06-11 · **데이터:** top-1500 PIT broad universe (2016–2026, 122개월) · **정의 고정:** quality = gp/assets (SF1 ARQ, datekey ≤ asof). **튜닝 0.**
**전제:** 어떤 결과든 live/paper 승격 금지. PASS는 "Phase 1B 입력 후보"까지만.

---

## 한 줄 결론

**FAIL — standalone 단순 quality 팩터로는 종료.** 결정타 2개:
1. **신호 붕괴(decay):** 2016–2020 IC-IR **0.42** → 2021–2026 IC-IR **0.046** (≈동전던지기). 2025·2026 IC **음수**.
2. **실거래 가능한 long-only가 실제 벤치를 못 이김:** Q5 long-only가 cap-weight 벤치 대비 **−1.15%/yr** (IR −0.16).

단, 무력(noise)은 아님 — 아래 "층위 분리" 참조. 잔존 정보가치는 Phase 1B *입력 feature* 논의로만 넘긴다.

---

## 5개 검증 결과

### [1] Subperiod — ❌ 사실상 붕괴
| 구간 | Rank IC | IC-IR | IC>0 | Q5-Q1(gross) |
|---|---|---|---|---|
| 2016–2020 (n=57) | +0.0394 | **+0.424** | 67% | +7.9%/yr |
| 2021–2026 (n=65) | +0.0042 | **+0.046** | 52% | +1.7%/yr |

연도별 IC: `17:+.083 18:+.037 19:+.024 20:+.050` (강) → `22:−.010 24:+.018 25:−.040 26:−.034` (소멸/음수).
→ **방향이 뒤집힌 건 아니나(여전히 미세 양수), 최근 절반은 신호가 없다.** 전 표본 IC-IR 0.22는 거의 전부 2016–2020에서 나옴.

### [2] Cost stress — ✅ 통과 (단, long-SHORT 기준)
| | net Q5-Q1 |
|---|---|
| 1x | +4.41%/yr |
| 2x | +4.19%/yr |
| 3x | +3.98%/yr |

비용에 거의 안 흔들림(턴오버 모데레이트·Q5/Q1 비용 상쇄). **그러나 이 +4%는 long-SHORT 숫자** — 저품질 ~300종 공매도를 전제. 솔로/소형 펀드가 실제로 못 잡는 알파.

### [3] Long-only — ❌ (vs CW) / ⚠️ 순수 long-leg은 양수
| 비교 대상 | active(gross) | TE | IR |
|---|---|---|---|
| **vs cap-weight 벤치** (실제 측정선) | **−1.15%/yr** | 7.2% | −0.16 |
| vs 1/N EW 벤치 (apples-to-apples) | **+1.79%/yr** | 4.6% | +0.39 |

**해석(핵심):** Q5-EW는 동일가중 유니버스(1/N)는 +1.79%/yr 이김 → **quality long-leg 틸트 자체는 진짜·양수.** 그런데 cap-weight 벤치엔 짐 → 차이 ~−2.9%/yr는 **EW-vs-CW 스타일 드래그**(2016–2026 메가캡 지배 10년). 즉 "−1.15%"는 *quality 무력*이 아니라 *quality(+) − 메가캡드래그(−−)*의 합.

### [4] Multiple-testing (4팩터 중 1 생존) — ⚠️ 경계
IC t≈**2.43** → one-sided p≈0.0075 → **Bonferroni×4 p≈0.030** (5% 통과). 단 DSR-lite 관점 t=2.43은 "경계", 그리고 이 t는 거의 전부 2016–2020산 — 2021–2026만 보면 t≈0.37(완전 비유의). **표면 통과, 실질 취약.**

### [5] Stability — ✅ 통과 (몰빵 없음)
- size-bucket IC: 하위절반 +0.0195 / 상위절반 +0.0191 → **size 중립** (소형 몰빵 아님).
- sector: Q5 최대섹터 24% (Consumer Cyclical) → **과집중 아님**.
- turnover: Q5 99%/yr · Q1 116%/yr → 모데레이트.
- *liquidity bucket: volume 미pull → marketcap proxy=size와 동치라 별도 정보 없음(한계 명시).*

---

## 층위 분리 (스핀 없이)

| 층위 | 결과 | 거래가능성 |
|---|---|---|
| Long-SHORT Q5-Q1 spread | +4.4%/yr net (cost robust) | ❌ 공매도 300종 — 솔로 불가 |
| Long-leg quality 틸트 (vs EW) | +1.79%/yr, IR 0.39 | ⚠️ 진짜지만 약함, 그리고 |
| 실제 측정선(vs cap-weight) | **−1.15%/yr** | ❌ 인덱스만 들고 있는 게 나음 |
| 시간 안정성 | 2021–2026 ≈ 0 | ❌ decay |

**잡을 수 있는(long-only, vs 실벤치) 부분은 음수이고, 양수인 부분(long-short, vs EW)은 못 잡거나 decay했다.**

---

## 판정 (사전등록 규칙 적용)

- 사전등록 FAIL 조건 발동: **long-only active(vs CW) ≤ 0**. 보강: subperiod decay.
- → **단순 single-factor family를 "직접 거래하는 standalone 전략"으로서는 종료(TERMINATE).**
- **live/paper 승격: 금지 (애초에 대상 아님).**
- 잔존: long-leg가 EW 대비 양수(+1.79%)이고 spread가 cost를 견딘 점은 **noise는 아님** → quality를 **Phase 1B의 weak input feature 후보**로 둘지는 *별도 결정* (decay 감안하면 회의적).

이 결과는 prior-art(factor decay·"Alpha Illusion"·post-publication 소멸·long-short 종이알파)와 정합. 검증 프로토콜이 의도대로 작동 — **틀린 방향을 자신있게 만들기 전에 죽였다.**
