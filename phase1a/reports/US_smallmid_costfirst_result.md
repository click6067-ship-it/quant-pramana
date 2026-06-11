# US Small/Mid Cost-First — 결과 (사전등록 1회 kill-test, 마지막 US arena)

**날짜:** 2026-06-11 · **데이터:** rank 1001–3000 PIT, 필터후 ≈1438종/월, 125개월 · **프로토콜:** `integrated/US_SmallMid_CostFirst_Protocol_v0.1.md`(결과 전 박음) · **튜닝 0.**
**필터:** price≥$5 · ADV(20d $vol) 하위10% 컷 · survivorship 포함. **비용:** 보수적 ADV tier 25/45/75bp, base/2x/3x.

## 한 줄 결론
**quality·event 핵심후보 전부 FAIL → US public-data cross-sectional arena 종료(TERMINATE) → KR feasibility로 이동.**
단 — **small/mid는 large-cap보다 *확실히* 더 살아있다(메타패턴 확증)**. 죽은 이유가 *cap-weight 벽*이 아니라 **유동성-집중·IC-IR 바·turnover·최근decay**로 바뀌었다.

## 결과

| 신호 | IC-IR | long-only net vs CW (1x/2x/3x) | Q5-Q1 net(1x) | 2021–26 (net/IC-IR) | 유동성버킷 net(저/고) | 판정 |
|---|---|---|---|---|---|---|
| quality | +0.157 | +0.66 / +0.00 / −0.65% | +2.56% | **−2.92% / +0.047** | **+5.06 / −4.88%** | ❌ FAIL |
| event | +0.164 | +1.85 / +0.31 / −1.24% | +4.00% | **+3.66% / +0.301** | +9.72 / **+1.69%** | ❌ FAIL |
| blend | **+0.335 (t≈3.75)** | +2.20 / +0.74 / −0.73% | +3.57% | **+5.67% / +0.501** | +11.07 / **−2.96%** | ❌ FAIL |
| (참고) value | +0.224 | — | +1.52% | — | — | (large선 DEAD였음) |

KILLS: quality=`IC-IR<0.20·2021-26사망·최저유동성에만` · event=`IC-IR<0.20·turnover>300%&net약` · blend=`최저유동성에만`.

## 읽는 법 (no echo — 양쪽 다 정직히)

**① 메타패턴 확증 — 메가캡 cap-weight 벽은 large-cap 현상이었다.**
large/event에선 long-only가 cap-weight에 *졌다*(−). small/mid에선 셋 다 base cost서 cap-weight를 *이긴다*(+0.66~+2.20%). value도 large선 DEAD였는데 여기선 IC-IR 0.224. **신호는 small/mid에서 더 산다** — 가설이 맞았다.

**② 그런데 예고한 새 killer(비용·유동성)가 정확히 문다.**
edge가 **최저유동성 버킷에 집중**. 거래 가능한 고유동성 버킷에서 quality −4.88%·blend −2.96%(둘 다 음수). blend는 IC t=3.75로 통계적으론 강하지만 **잡을 수 있는 곳(고유동성)에선 음수** = 사전 kill #6 정확히 발동. 셋 다 3x cost서 음수.

**③ 단 하나 진짜 흥미로운 잔여 = event.**
event는 (a) **최근 절반에서 살아있고**(2021–26 IC-IR +0.301, net +3.66% — level과 달리 decay 안 함), (b) **2x cost 생존**, (c) **고유동성 버킷도 양수**(+1.69%, 유일). 그런데도 **IC-IR 0.164 < 0.20 바**와 **turnover 321%**로 사전규칙상 FAIL. → 바를 낮춰 살리는 건 goalpost 이동 = 금지. **규칙대로 FAIL.**

## 판정 (사전등록 규칙 — goalpost 불변)
quality·event 둘 다 ≥1 kill → **US public-data cross-sectional arena 종료(TERMINATE).** no tuning to rescue, no live/paper.

## US 챕터 종합 (4 arena)
| arena | 결과 | 핵심 |
|---|---|---|
| level (1A) | TERMINATE | 단순팩터 large 무신호 |
| 결합 (1B) | TERMINATE | OOS ridge IC-IR 0.01 |
| event (A) | FAIL | decay 안 하나 large cap-weight 벽 |
| small/mid (B) | FAIL | 신호 더 살지만 유동성-집중·IC-IR 바·cost |

**결론: 공개 데이터·cross-sectional·long-only로는 US에서 거래 가능한 standalone edge 없음.** 단 방향 신호 2개 — **(i) 신호는 small/mid에서 더 산다, (ii) event/surprise는 decay 안 한다.** 둘 다 **KR small/mid + event** 가설(v2)을 *향한다*. → 다음 = **KR feasibility**(명분 강해짐).
