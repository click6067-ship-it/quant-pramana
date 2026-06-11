# 🔖 NEXT SESSION CHECKPOINT — 2026-05-30

> 용하: "내일 'ㄱㄱ' 하면 바로 시작". 이 파일 = 재개 진입점. (빌드는 오늘 보류, 내일 시작.)

## 📍 지금 어디 (오늘 한 일)
1. **XTX 벤치마크 회의** (Claude+Codex, web) → XTX 엣지=데이터·컴퓨트·신호결합·마이크로구조. 이식가능=*규율*(이미 보유), 함정=*스케일*. 기록: `~/main/council/2026-05-30_pythia_xtx-ml-benchmark/`.
2. **실측 진단** (`scripts/factor_ic_diagnostic.py`) → **모델≠병목, 데이터=병목**: KOSPI momentum-only R²−0.0259→ridge-5 −0.0253(ε), KOSDAQ 플로-레벨 IC 음(−0.018). momentum만 부호-안정.
3. **패러다임 피벗 회의** (Claude+Codex 2라운드, web, +Gemini 교차) → **강한 수렴.** 기록: `~/main/council/2026-05-30_pythia_paradigm-pivot/` (plan·council·codex-r1·codex-r2·claude-r1-independent).

## 🎯 회의 수렴 결론 (메모리: `paradigm-pivot-conclusion.md`)
- **pythia = 엄밀한 *작은 자동 트레이딩 랩* (XTX 같은 돈기계 아님).** 생존 = 좁은 비용후 KR/US 엣지를 *증명*하는 것, 약한 신호를 어려운 수학으로 *장식*하는 게 아님.
- **Binding truth:** rigor ≠ edge. 검증수학(gate-v2)은 거짓말을 줄이지 수익을 만들지 않음. 최대 자기기만 = "걸맞는 rigor"를 "충분한 edge"와 혼동.
- **진짜 수학 vs 글래머:** 🟢 횡단면 랭킹·Ledoit-Wolf·HRP·분수Kelly·vol타겟·베이지안수축(좁게)·gate-v2  /  🚫 무제약 평균분산·HMM잠재레짐(→관측레짐 쓰기)·앙상블·TSFM-알파.
- **시장:** US=추세/매크로(저비용), KR=행동/수급/공시(비효율). 전략-종속, 양자택일 아님. (미장 데이터 실재: Norgate $630/yr.)
- **TSFM:** 알파 동결(제로샷 R² 음수=forecaster). 리스크/vol/레짐 오버레이로만.
- **인간/LLM:** 거버넌스 레이어만(킬·자본배분·주말리뷰·승급·사고리뷰). 라이브 알파/집행 결정 ❌. LLM 주문권 0·오프라인 비평만.

## ▶️ 내일 "ㄱㄱ" → 바로 시작 (1번 작업 = gate-v2)
**왜 1번:** 전략 레지스트리(여러 전략·유료데이터 실험)는 false-discovery를 증폭 → 안 깔면 새 "통과"가 우연인지 모름. 싸고(기존 게이트 위 통계), 데이터 안 사도 지금 가능, "방법론=제품" 해자를 논문급으로 깊게 함.

**gate-v2 = 다중검정 하드닝. TDD 착수 스펙:**
1. **Deflated Sharpe Ratio** → 새 `pythia/leakgate/deflated.py`
   - `probabilistic_sharpe_ratio(returns, sr_star=0.0)`: PSR = Φ( (SR − SR*)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²) ), γ₃=skew, γ₄=kurtosis.
   - `deflated_sharpe_ratio(returns, n_trials, sr_variance)`: SR* = √(sr_variance)·[ (1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e)) ], γ=0.5772(Euler). DSR = PSR(SR*). 통과 = DSR ≥ 0.95(설정가능).
   - 테스트: Bailey/López de Prado 논문 예시값으로 watch-fail. N = `PreregSpec.trial_count`.
2. **FDR/FWER over family** → `pythia/leakgate/multipletesting.py`
   - `benjamini_hochberg(pvalues, alpha=0.05)` → family(등록 전략들)의 baseline_excess p값에 적용, 생존 가설 반환.
3. **Frozen holdout** → split 로직 확장: 마지막 N개월(예: 6~12mo)을 *어떤 스테이지도 안 건드림*, 최종 확인용으로 별도 보고.
4. **통합:** `gate.py:run_gate`에 DSR 스테이지 추가(trial_count 사용); 레지스트리 레벨 FDR은 여러 `GateOutcome` 위 별도 패스.

**참고 출처:** Deflated Sharpe = Bailey/López de Prado (SSRN 2460551); FDR = Benjamini-Hochberg 1995; 강건공분산 = Ledoit-Wolf; HRP = López de Prado.

## ⏭️ gate-v2 이후 (보류 결정 — 그때 정함)
- 유료 데이터 1개 구매: 회의 랭킹 = **PIT 펀더멘털+섹터/사이즈 먼저** → 실적서프라이즈(비쌈) → **KR 공시 본문(차별 해자)** → 인트라데이 → 대체데이터 꼴찌.
- 시장×전략 첫 타겟: KR 섹터/사이즈 중립화 vs US 추세암(Norgate). 둘 다 정직 — 용하 선택.
- 그 위에 prereg 가설 1~2개를 gate-v2로.

## 🗂 자산 위치
- 회의록: `~/main/council/2026-05-30_pythia_{xtx-ml-benchmark,paradigm-pivot}/`
- 메모리: `paradigm-pivot-conclusion.md` (+ MEMORY.md 인덱스)
- 진단: `scripts/factor_ic_diagnostic.py` (data_cache & data_cache_kosdaq 대상)
- 캐시: `data_cache/` (KOSPI100) · `data_cache_kosdaq/` (KOSDAQ150, 오늘 소싱)
- 브랜치: `feat/p0-wrap-up` (미커밋: clients.py·isolation.py — gate-v2와 무관, 오늘 안 건드림)
