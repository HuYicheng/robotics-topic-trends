"""Persist the tables that were only printed during the 2026-10-14 session, on the final title + abstract measure.

1. results/combination_manip_il_vla_flow_gs.csv / .md : how often manipulation, imitation learning, VLA/VLM,
   diffusion/flow generative models and Gaussian splatting co-occur, per year (raw shares; 2026 = ICRA, RSS, journals),
   pairwise lift in 2025, and every paper that combines manipulation + imitation + Gaussian splatting.
   Flow matching is also measured on its own (flow matching / rectified flow / flow policy).
2. results/venue_series_ta.csv : per venue and year, k/n, share and Wilson 95% interval for every topic.
3. results/standardisation_check.csv : standardised vs raw shares (2024, 2025) and 2026 vs the five-venue raw share.
"""
import json
import os
import re

import pandas as pd
from statsmodels.stats.proportion import proportion_confint
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
m = pd.read_csv(os.path.join(ROOT, "data", "topic_matrix_ta.csv"))
papers = pd.read_csv(os.path.join(ROOT, "data", "papers.csv")).set_index("uid")
ab = {r["uid"]: r["abstract"] for r in map(json.loads, open(os.path.join(ROOT, "data", "abstracts.jsonl")))}
topics = [c for c in m.columns if c not in ("uid", "venue", "year")]

# 1. combination
flow_rx = re.compile(r"flow[- ]matching|rectified flow|flow[- ]based (polic|generative)|flow polic", re.I)
m["FlowMatching"] = [int(bool(flow_rx.search(papers.loc[u, "title"]) or flow_rx.search(ab.get(u, "")))) for u in m.uid]
S = {"M": "Manipulation (any)", "IL": "Imitation learning / LfD", "VLA": "VLA / robot foundation models", "VLM": "LLM / VLM",
     "Gen": "Diffusion / flow generative models", "GS": "3D Gaussian splatting"}
for k, c in S.items():
    m[k] = m[c]
m["VLx"] = ((m.VLA + m.VLM) > 0).astype(int)
combos = {"manipulation": ["M"], "M+IL": ["M", "IL"], "M+IL+Gen(diffusion/flow)": ["M", "IL", "Gen"],
          "M+IL+VLA/VLM": ["M", "IL", "VLx"], "M+IL+VLA/VLM+Gen": ["M", "IL", "VLx", "Gen"], "M+GS": ["M", "GS"],
          "M+IL+GS": ["M", "IL", "GS"], "all five: M+IL+VLA/VLM+Gen+GS": ["M", "IL", "VLx", "Gen", "GS"],
          "flow matching (any)": ["FlowMatching"], "M+IL+flow matching": ["M", "IL", "FlowMatching"]}
rows = []
for name, ks in combos.items():
    hit = m[ks].all(axis=1)
    r = {"combination": name}
    for y in config.YEARS:
        g = hit[m.year == y]; r[f"n_{y}"] = int(g.sum()); r[f"pct_{y}"] = round(100 * g.mean(), 2)
    rows.append(r)
comb = pd.DataFrame(rows)
comb.to_csv(os.path.join(ROOT, "results", "combination_manip_il_vla_flow_gs.csv"), index=False)
g = m[m.year == 2025]
lift = []
for a, b in [("IL", "Gen"), ("IL", "VLx"), ("VLx", "Gen"), ("M", "GS"), ("IL", "GS"), ("VLx", "GS"), ("Gen", "GS")]:
    obs = (g[a] & g[b]).mean(); exp = g[a].mean() * g[b].mean()
    lift.append({"pair": f"{a} & {b}", "observed_pct": round(100 * obs, 2), "expected_if_independent_pct": round(100 * exp, 2),
                 "lift": round(obs / exp, 2)})
lift = pd.DataFrame(lift)
mig = m[m[["M", "IL", "GS"]].all(axis=1)]
with open(os.path.join(ROOT, "results", "combination_manip_il_vla_flow_gs.md"), "w") as f:
    f.write("# Co-occurrence of manipulation, imitation learning, VLA/VLM, diffusion/flow, Gaussian splatting\n\n")
    f.write("Title + abstract measure; papers with abstracts; raw shares (2026 = ICRA, RSS, T-RO, IJRR, Science Robotics only; years from scripts/config.py).\n\n")
    f.write(comb.to_markdown(index=False) + "\n\nPairwise lift in 2025 (all seven venues):\n\n" + lift.to_markdown(index=False) + "\n\n")
    f.write("Papers with manipulation + imitation learning + Gaussian splatting:\n\n")
    for u in mig.uid:
        f.write(f"- {papers.loc[u, 'venue']} {papers.loc[u, 'year']} | {papers.loc[u, 'title']}\n")
print(comb.to_string(index=False)); print(lift.to_string(index=False))

# 2. venue series with Wilson intervals
vs = []
for (v, y), gg in m.groupby(["venue", "year"]):
    for t in topics:
        k, n = int(gg[t].sum()), len(gg)
        lo, hi = proportion_confint(k, n, method="wilson")
        vs.append({"topic": t, "venue": v, "year": y, "k": k, "n": n, "share_pct": round(100 * k / n, 2),
                   "wilson_lo_pct": round(100 * lo, 2), "wilson_hi_pct": round(100 * hi, 2)})
pd.DataFrame(vs).to_csv(os.path.join(ROOT, "results", "venue_series_ta.csv"), index=False)

# 3. standardisation check
d = pd.read_csv(os.path.join(ROOT, "results", "shares_and_change_ta.csv"))
s5 = m[m.venue.isin(["ICRA", "RSS", "T-RO", "IJRR", "SciRobotics"])]
chk = d[["topic"] + [c for y in config.YEARS for c in (f"share_{y}", f"raw_{y}")] + ["share_2026_lo", "share_2026_hi"]].copy()
chk["raw5_first"] = [100 * s5[s5.year == config.YEARS[0]][t].mean() for t in chk.topic]
chk["raw5_2026"] = [100 * s5[s5.year == 2026][t].mean() for t in chk.topic]
chk.round(2).to_csv(os.path.join(ROOT, "results", "standardisation_check.csv"), index=False)
print("wrote combination, venue_series_ta, standardisation_check")
