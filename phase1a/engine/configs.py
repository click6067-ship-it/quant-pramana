#!/usr/bin/env python3
"""Phase 2 P3.2 — named config registry. 검증된 과거 실험 = named config.
규율: 새 실험/feature/kill 0 (전부 동결 재현용). run.run_named(name) 또는 CLI `python engine/run.py <name>`."""

CONFIGS = {
    # ── broad top-1500 단순 슬리브 (broad_retest kills) ──
    "B2_value":    dict(bundle="broad", rank=(1, 1500), score={"kind": "raw", "feature": "value"},
                        dropna=["score", "fwd"], cost_tier="marketcap", kill_set="broad_retest"),
    "B3_quality":  dict(bundle="broad", rank=(1, 1500), score={"kind": "raw", "feature": "quality"},
                        dropna=["score", "fwd"], cost_tier="marketcap", kill_set="broad_retest"),
    "B4_momentum": dict(bundle="broad", rank=(1, 1500), score={"kind": "raw", "feature": "momentum"},
                        dropna=["score", "fwd"], cost_tier="marketcap", kill_set="broad_retest"),
    "B5_lowvol":   dict(bundle="broad", rank=(1, 1500), score={"kind": "raw", "feature": "lowvol"},
                        dropna=["score", "fwd"], cost_tier="marketcap", kill_set="broad_retest"),
    # ── broad quality quarantine ──
    "broad_quality_quarantine": dict(bundle="broad", rank=(1, 1500), score={"kind": "raw", "feature": "quality"},
                        dropna=["score", "fwd", "mc"], cost_tier="marketcap", kill_set="quality_quarantine"),
    # ── broad low-DoF blend / event ──
    "phase1b_blend": dict(bundle="broad", rank=(1, 1500),
                        score={"kind": "composite", "components": ["value", "quality", "momentum", "lowvol"]},
                        dropna=["score", "fwd", "mc"], cost_tier="marketcap", kill_set="phase1b"),
    "broad_event": dict(bundle="broad", rank=(1, 1500), score={"kind": "composite_event"},
                        dropna=["score", "fwd", "mc"], cost_tier="marketcap", kill_set="event"),
    # ── small/mid cost-first (smallmid kills, ADV 비용, 필터, composite_predropna=False) ──
    "sm_quality":  dict(bundle="smallmid", rank=(1001, 3000), score={"kind": "raw", "feature": "quality"},
                        dropna=["score", "fwd", "mc", "adv"], cost_tier="adv", kill_set="smallmid",
                        min_names=100, filters={"price_min": 5, "adv_floor_q": 0.10}),
    "sm_event":    dict(bundle="smallmid", rank=(1001, 3000), score={"kind": "composite_event"},
                        dropna=["score", "fwd", "mc", "adv"], cost_tier="adv", kill_set="smallmid",
                        min_names=100, composite_predropna=False, filters={"price_min": 5, "adv_floor_q": 0.10}),
    "sm_blend":    dict(bundle="smallmid", rank=(1001, 3000),
                        score={"kind": "composite", "components": ["value", "quality", "momentum", "lowvol"]},
                        dropna=["score", "fwd", "mc", "adv"], cost_tier="adv", kill_set="smallmid",
                        min_names=100, composite_predropna=False, filters={"price_min": 5, "adv_floor_q": 0.10}),
}

def get(name):
    if name not in CONFIGS:
        raise KeyError(f"unknown config '{name}'. 사용가능: {list(CONFIGS)}")
    return dict(CONFIGS[name], name=name)
