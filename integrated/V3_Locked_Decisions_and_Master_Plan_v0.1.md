# Pramana v3 — Locked Decisions + Master Plan v0.1 (Autonomous Build)
**Date:** 2026-06-11 · **Mode:** 자동 빌드(사용자 추가입력 없음). 옵션결정=Codex 상의 후 확정 · **모델선택=deep-research+council** · 검증 kill-gate/risk veto 유지 · paper-only.

## 0. LOCKED DECISIONS (사용자 확정 — 불변)
| 항목 | 값 |
|---|---|
| 시장 | **US only** |
| 자본 | **₩100M 가상(paper)** — no live |
| 목적함수 | **공격적 절대수익 최대** (고변동·큰 DD 감내, 레버리지/출렁임 허용) |
| 모델 공간 | **OPEN** — ML·ensemble·deep 포함 가능, deep-research+council이 결정. 단 검증 kill-gate·과적합 통제 유지 |
| 데이터 예산 | **Sharadar 고정**(~$69/mo). 추가 유료는 research가 강하게 정당화 → *결제 요청 1회*만 사용자에게 |
| 상품 범위 | US **주식 + ETF + 레버리지 ETF + 선물(또는 선물-proxy)** — 모든 신호 취합 |
| 아키텍처 | 8레이어(아래) |
| 거버넌스 | paper→live 승격만 human sign-off, 그 외 자동 |

## 1. 8-Layer 아키텍처 → 구체 컴포넌트 (기존 engine/ 확장)
| # | 레이어 | 구현(기존 자산 → 확장) |
|---|---|---|
| 1 | **데이터 인프라** | `engine/data.py`(Sharadar SEP/DAILY/SF1/SFP/TICKERS 캐시·manifest·API-free) → **ETF/레버리지(SFP)·선물(NDL 무료 연속물 또는 futures-proxy ETF)·macro 어댑터** 추가 |
| 2 | **신호/모델 팩토리** | `engine/features.py` → **feature library 확장**(cross-sectional + TS trend/momentum·vol·carry) + **walk-forward 모델 학습 프레임**(선형·penalized·tree·… 모델공간 OPEN). ★모델 아키텍처=deep-research+council |
| 3 | **alpha ensemble** | meta-signal v0(z 평균) → **다중 alpha 결합**(equal-risk/stacking, 상관조정). 검증 kill-gate 통과한 sleeve만 편입 |
| 4 | **portfolio optimizer** | quintile-EW v0 → **forecast→weight optimizer**(공격적: max expected return s.t. leverage/risk 제약; 또는 robust MV/risk-parity). Codex/research 결정 |
| 5 | **risk engine(veto)** | `ls_book` v2(vol-target·per-name cap·sector-neutral·DD-stop) → **결정적 final veto**(포지션/노출/레버리지/유동성 한도 + hard kill). 공격적이라 레버리지↑ 허용하되 kill-switch 강화 |
| 6 | **execution engine** | `engine/simulator.py`·`ls_book` → **현실 체결 시뮬**(spread/commission/borrow/impact·리밸런스 스케줄·fills) → 후속 Alpaca/IBKR **paper broker** 연동 |
| 7 | **monitoring/kill switch** | NAV·리스크·데이터이상 실시간 추적 + 임계 breach 시 **자동 kill**. 리포트/대시보드 |
| 8 | **human governance** | LOCKED 결정·kill-gate·**paper→live 승격 게이트(human only)**. 그 외 자동 |

## 2. 단계 (Plan → Design → Implement, 각 게이트)
- **Plan(현재):** 본 문서 + **Codex 적대 리뷰**(gap/risk/우선순위/모델선택 프레이밍) → 반영.
- **Design:** 레이어별 설계 결정. **★ 모델 팩토리/alpha 아키텍처 = deep-research(풀 팬아웃) + council(다관점 회의)**. 데이터(선물/ETF 소스)·optimizer·risk·execution 설계 = Codex 상의. 각 설계 = 사전등록 spec + kill-gate.
- **Implement:** 기존 engine 위에 증분 구현. 각 컴포넌트 검증(walk-forward·OOS·kill-gate) 후 통합 → **자동 paper book 1개가 굴러가게**. 회귀 게이트로 동결.

## 3. 규율 (전 단계 유지, 공격적이어도)
walk-forward·OOS·사전등록 kill-gate · 과적합 통제(DSR/PBO/multiple-testing) · 데이터/비용 정직 · risk engine 결정적 veto · paper-only(live=human gate) · 모든 옵션결정 Codex 상의 · 모델선택 deep-research+council · 동결 숫자 재현.

## 4. 자동주행 운영
- 옵션·설계 결정마다 Codex `exec`(비-git→`--skip-git-repo-check`, foreground) 상의 후 확정·기록.
- 모델선택/중대설계는 deep-research Workflow + council(멀티에이전트) 풀가동.
- 진행은 milestone/메모리/PROJECT_MAP에 기록. 사용자 입력 불요(결제 요청 시에만 1회).

## 5. 즉시 다음 (이 문서 직후)
1. ~~Codex 적대 리뷰~~ ✅ 완료 → v0.2 반영(아래).
2. Design 진입: 모델 research는 *제약·후순위*(v0.2 참조).
3. 데이터 인프라 확장(ETF/선물)=**DEFER**(v0.2).

---

# v0.2 — Codex 적대 리뷰 반영 (2026-06-11, 방향 재설정)
**Codex 핵심 평결:** *"마법 모델 찾기 그만. 작동하는 그거(시장중립 book)를 레버리지 + 잔혹한 스트레스 + 운영 패러노이아로 *지금* 굴려라. ML/deep는 증명 전까진 유죄. 공격적 절대수익의 정직한 천장 = 레버리지된 modest edge(고-Sharpe 기계 아님)."*

## ★ 재정렬된 우선순위 (BUILD FIRST → DEFER)
**BUILD NOW (OS spine):**
1. **일간 자율 루프(OS 척추):** 데이터refresh → manifest/hash 체크 → signal → portfolio → **risk veto** → orders → 시뮬 fills → **ledger** → report → kill status.
2. **risk ledger**(optimizer 정교화보다 먼저): gross/net 노출·factor·sector·beta·margin·single-name gap손실·유동성 참가율·borrow·ETF 집중·crash 시나리오 손실.
3. **현재 book 잔혹 스트레스:** 2018Q4·2020·2022·2023·2024-26 레짐 + 지연체결·결측·2x/5x 비용·1일 5-10% 갭·강제 de-risk.
4. **작동하는 그것(시장중립 L/S)의 레버리지 버전** + 하드 리스크 감사 = *지금 굴러가는 공격적 paper book*.

**DEFER:** deep learning · 복잡 optimizer · **선물 통합** · 멀티에이전트 모델 council · 대시보드 · "alpha factory" 추상화.

## ★ 모델-선택 research = 제약 + 후순위 (layer 2 게이트, 척추 아님)
사용자 명령(모델선택=deep-research+council)은 *유지*하되 Codex대로 **constrain**: council이 답할 것만 —
1. 기존 선형/rank 신호 *위에 증분 OOS 알파*가 있나(포트폴리오 레벨 Sharpe/DD, IC 아님)?
2. 어느 label horizon(1/5/21/63d·earnings·rebal)에 신호가 있나(불안정하면 ML kill)?
3. ML이 랭킹 개선인가 tail 과적합인가(ridge/GBM/RF vs rank baseline, 동일 walk-forward)?
4. **trial ledger**(다중검정 소비 추적) 없으면 결과 무효.
5. regime/universe 교란(대형만·no biotech/financials·지연펀더·2x비용) 생존?
**Codex 평결: open deep/ML은 제약 없으면 trap. GBM/정규화 선형은 도울 수도, Sharadar 일별에 deep=theater.** → research는 척추 가동 *후* layer 2 게이트로, "ML 쓸 가치 있나"를 *판정*(유죄추정).

## ★ 공격적 레버리지 = 설계초기부터 박을 리스크 (Codex)
- **레버리지 ETF**: 일간 리셋 경로의존 → `3×index`로 근사 금지, **LETF 실제 경로수익 직접 모델**.
- **선물/proxy**: roll yield(콘탱고/백워데이션) 지배 → 명시적 roll 캘린더·슬리피지·만기·margin (→ 그래서 선물은 DEFER).
- **gap 리스크**: 일간 시스템은 장중 참사에 눈멈 → **pre-trade crash 손실 추정**("SPY −7%·QQQ −10%·고베타 long −15%·short +8%면?").
- **vol-target 폭발**: 잔잔할 때 노출↑(잠재 crash 직전)·급등후 컷(손실고정·반등놓침) → **vol 무관 max 레버리지 cap·DD기반 노출감쇠·cooldown·kill 후 즉시 재가동 금지**.
- **kill-switch 4종 분리**: ① 데이터무결성 kill(즉시 중단) ② 리스크breach kill(gross 축소) ③ 모델decay kill(신규리스크 동결·청산만) ④ 시장crash kill(결정적 노출 스케줄, 패닉청산 아님).

## ★ 정직한 천장 (Codex)
unlevered = modest Sharpe~0.5(엄격비용·paper열화 생존 시) / levered = CAGR↑·Sharpe 동일~악화·DD 크게↑ / **공격적 절대수익 = 레버리지된 modest edge로만 가능, 발견된 고-Sharpe 기계 아님.** 경로: **modest edge가 진짜임을 증명 → 레버리지로 *얼마나 고통을 살지* 결정.** (Sharpe 0.5를 3x 하면 −3σ 달·borrow drift·레짐반전서 터짐.)

## ★ 솔로-자동-공격 3대 함정 (Codex)
1. **야망으로 위장한 research debt** — edge 약하니 모델/피처/레이어 자꾸 추가 = 아름다운 백테스트로 죽음.
2. **운영 패러노이아보다 앞선 자동화** — stale 파일·ticker매핑·split·refresh실패 하나가 수년 알파 잡아먹음. 자동시스템은 *배관*부터 터진다.
3. **청산로직 없는 레버리지** — 진입만 정하고 강제 de-risk 경로·재진입·margin스트레스·유동성한도 미정의.

## v0.2 즉시 다음 (자동주행)
1. **레버리지 + 잔혹 스트레스 + risk ledger 버전 book**(ls_book v3) — *지금 굴러가는 공격적 paper book*.
2. **일간 자율 루프 스켈레톤**(데이터→signal→risk veto→fills→ledger→report→kill).
3. ~~모델-선택 deep-research+council~~ ✅ **RESOLVED → `V3_Model_Selection_Council_Decision_v0.1.md`**: 3독립소스(Codex·우리 bake-off·deep-research 105에이전트) 수렴 → **모델공간 CONSTRAIN**(정규화선형+GBM challenger only·trial ledger·no deep). 진짜 lever=*분산 앙상블+실행+리스크엔지니어링*(모델복잡도 아님). LOCKED 결정의 "모델공간 OPEN" → research결정=CONSTRAINED.
