# v2.0 True PEAD / Announcement-Window Drift — 결과 (사전등록 1회 kill-test)

**날짜:** 2026-06-11 · **데이터:** top-1500 PIT, 2016–2026 · **이벤트=60,862**(SF1 datekey·price≥$5)·발표월 123·종목 2,810 · **튜닝 0.**
**프로토콜:** `integrated/V2_True_PEAD_Protocol_v0.1.md`(결과 전 박음). 정의: reaction=[-1,+1] · drift=[+2,+21](진입 +2, no look-ahead) · marketcap tier round-trip 비용.

## 한 줄 결론
**FAIL → True PEAD(이 정의) 종료/보류.** 단순 무신호가 아니라 **부호가 반대 = 반전(reversal)**. top-1500 대형주에선 강한 공시반응이 이후 **drift가 아니라 미세 되돌림**.

## 결과
| 지표 | 값 |
|---|---|
| Rank IC (reaction→drift) | **−0.0153** (IC-IR **−0.168**, t≈−1.85) |
| IC>0 | 46% |
| long-only Q5 vs announcer-EW | gross +0.11% / **net −2.25% / 2x −4.61%/yr** |
| long-only Q5 vs cap-weight | gross +1.65%/yr |
| Q5-Q1 spread | gross **−3.18%** / net −7.91%/yr |
| 2021–2026 | IC-IR **−0.107** / recent net −0.17%/yr |
| 유동성 버킷 net Q5-Q1 | 저 −4.48% / 고 −11.57% (둘 다 음수) |

**KILLS(4):** net active(long-only vs 벤치)≤0 · 2021-26 사망 · IC-IR<0.20(−0.168) · 2x cost 사망.

## 읽는 법 (no echo)
- **IC 부호가 음수** = 강한 +공시반응 종목이 이후 *상대적으로 못 감*(반전). PEAD under-reaction 가설의 *반대*. 대형주는 공시정보가 즉시·과하게 반영 후 되돌림(유동성 공급·효율성) — 교과서 PEAD가 **소형·under-followed** 현상이라는 것과 정합.
- **즉 거래 가능한(유동) 유니버스에선 PEAD가 edge가 아니다(반전).** 소형주엔 있을 수 있으나 거기선 v1에서 본 **비용/유동성 벽**이 먹는다. 어느 쪽이든 이 setup으로는 tradeable standalone edge 아님.

## 판정 (사전등록 규칙)
≥1 kill → **True PEAD(이 정의) = 종료/보류.** no tuning to rescue · no live/paper.

## 다음 (보류 옵션, 지금 추격 안 함 — 규율)
- 변형(small/mid PEAD·다른 window) 사전등록은 *가능하나*, 소형 PEAD는 비용 벽 예상 → 별도 결정. **이번엔 정의 하나만, FAIL로 닫음.**
- v2 사이클 결과 = **first new edge source(PEAD)도 죽음.** US 공개데이터에서 또 하나의 정직한 negative.
