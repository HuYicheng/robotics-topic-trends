"""Compare topic trends across measures: title (all papers), title (papers with abstracts), mention, focus.

A call is 'robust' when title, mention and focus (all on the papers with abstracts) agree on rising/declining
at q < 0.05; 'measure-dependent' when they disagree. Output: results/compare_measures.csv (+ printed table)
"""
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
cols = ["topic", "family", "share_2025", "annual_OR", "annual_OR_lo", "annual_OR_hi", "q_trend", "call", "OR_26v25"]
frames = {}
for name, f in (("titleAll", "trends.csv"), ("titleSub", "trends_title_sub.csv"), ("mention", "trends_mention.csv"),
                ("focus", "trends_focus.csv")):
    d = pd.read_csv(os.path.join(ROOT, "results", f))[cols].set_index("topic")
    frames[name] = d
topics = frames["titleSub"].index
rows = []
for tp in topics:
    r = {"topic": tp, "family": frames["titleSub"].loc[tp, "family"]}
    for name, d in frames.items():
        x = d.loc[tp]
        r[f"{name}_share25"] = 100 * x.share_2025
        r[f"{name}_OR"] = x.annual_OR; r[f"{name}_lo"] = x.annual_OR_lo; r[f"{name}_hi"] = x.annual_OR_hi
        r[f"{name}_call"] = x.call
    calls = {r["titleSub_call"], r["mention_call"], r["focus_call"]}
    if calls == {"rising"}:
        r["verdict"] = "robust rising"
    elif calls == {"declining"}:
        r["verdict"] = "robust declining"
    elif calls == {"unclear"}:
        r["verdict"] = "unclear in all"
    elif "rising" in calls and "declining" in calls:
        r["verdict"] = "CONTRADICTORY"
    else:
        r["verdict"] = "measure-dependent: " + "/".join(sorted(c for c in calls if c != "unclear")) + " in some"
    rows.append(r)
out = pd.DataFrame(rows).sort_values("focus_OR", ascending=False)
out.to_csv(os.path.join(ROOT, "results", "compare_measures.csv"), index=False)


def cell(r, n):
    mark = {"rising": "↑", "declining": "↓", "unclear": "·"}[r[f"{n}_call"]]
    return f"{r[f'{n}_share25']:5.2f}% ×{r[f'{n}_OR']:.2f}{mark}"


print(f"{'topic':46s} {'title (all papers)':>20s} {'title (w/ abstract)':>20s} {'mention':>20s} {'focus':>20s}  verdict")
for _, r in out.iterrows():
    print(f"{r.topic[:46]:46s} {cell(r, 'titleAll'):>20s} {cell(r, 'titleSub'):>20s} {cell(r, 'mention'):>20s} {cell(r, 'focus'):>20s}  {r.verdict}")
print("\nshare = 2025 share (all seven venues); ×OR = annual odds multiplier; ↑/↓ significant after FDR, · unclear")
