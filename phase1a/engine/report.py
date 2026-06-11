#!/usr/bin/env python3
"""Phase 2 M7 — Research Engine report module. 표준 md/csv 생성 *만*.
규율: 메트릭/kill 계산 0(evaluate·kills 결과 포맷만) · API 0. 기존 리포트 포맷 호환."""
import os, pandas as pd

STD_COLS = ["name", "n", "ic", "icir", "ic_pos", "gross_ls", "net_ls",
            "act_cw", "act_ew", "net_cw", "turnover", "rec_icir", "rec_net", "verdict", "kills"]

def summary_row(name, s, verdict, kill_labels):
    r = {"name": name, "n": s.get("n"), "ic": round(s["ic"], 4), "icir": round(s["icir"], 3),
         "ic_pos": round(s["ic_pos"], 3), "gross_ls": round(s["gross_ls"], 4), "net_ls": round(s["net_ls"], 4),
         "act_cw": round(s["act_cw"], 4), "act_ew": round(s["act_ew"], 4), "net_cw": round(s["net_cw"], 4),
         "turnover": round(s["turnover"], 3), "rec_icir": round(s["rec_icir"], 3), "rec_net": round(s["rec_net"], 4),
         "verdict": verdict, "kills": ";".join(kill_labels)}
    return r

def write_csv(rows, path):
    pd.DataFrame(rows).reindex(columns=STD_COLS).to_csv(path, index=False)
    return path

def render_md(title, rows, note=""):
    lines = [f"# {title}", ""]
    if note:
        lines += [note, ""]
    lines += ["| name | n | IC | IC-IR | net_ls | net_cw | turnover | verdict | kills |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['n']} | {r['ic']:+.4f} | {r['icir']:+.3f} | "
                     f"{r['net_ls']:+.4f} | {r['net_cw']:+.4f} | {r['turnover']:.2f} | {r['verdict']} | {r['kills']} |")
    return "\n".join(lines) + "\n"

def write_md(text, path):
    with open(path, "w") as f:
        f.write(text)
    return path
