"""Topic share trends 2024-2026 at ICRA, IROS, RSS, CoRL, T-RO, IJRR, Science Robotics.

Per topic, paper-level logistic regression  topic ~ C(venue) + C(year)  on 2024-2026, so a year effect is a
within-venue change (2026 has ICRA, RSS and the journals only; IROS 2026 and CoRL 2026 are not published).
Venues with zero topic papers in 2024-2026 are dropped for that topic (they carry no year information and
cause separation). Also a linear-in-year version (annual odds multiplier). Benjamini-Hochberg over topics.
Output: results/trends.csv, results/shares_by_venue_year.csv
"""
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
VENUES = ["ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"]

import sys  # noqa: E402
MATRIX = sys.argv[1] if len(sys.argv) > 1 else "topic_matrix.csv"   # data/<MATRIX>
SUFFIX = sys.argv[2] if len(sys.argv) > 2 else ""                  # results/trends<SUFFIX>.csv
m = pd.read_csv(os.path.join(ROOT, "data", MATRIX))
m = m[m.venue.isin(VENUES) & m.year.between(2024, 2026)].copy()
topics = [c for c in m.columns if c not in ("uid", "venue", "year")]
fam = dict(__import__("importlib").import_module("importlib").import_module  # placeholder, replaced below
           and [])
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("t", os.path.join(ROOT, "scripts", "04_topics.py"))
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
family = {n: f for n, f, _ in t.TOPICS}

rows, share_rows = [], []
for topic in topics:
    d = m[["venue", "year", topic]].rename(columns={topic: "y"})
    for (v, yr), g in d.groupby(["venue", "year"]):
        share_rows.append({"topic": topic, "venue": v, "year": yr, "n": len(g), "k": int(g.y.sum())})
    keep = d.groupby("venue").y.sum()
    d = d[d.venue.isin(keep[keep > 0].index)]
    res = {"topic": topic, "family": family[topic]}
    for yr in (2024, 2025, 2026):
        g = m[m.year == yr]
        res[f"n_{yr}"] = int(g[topic].sum()); res[f"share_{yr}"] = g[topic].mean()
    # like-for-like raw shares for 2024 vs 2026 (venues present in 2026)
    s26 = m[m.venue.isin(["ICRA", "RSS", "T-RO", "IJRR", "SciRobotics"])]
    res["share_2024_same5"] = s26[s26.year == 2024][topic].mean()
    res["share_2026_same5"] = s26[s26.year == 2026][topic].mean()
    try:
        f1 = smf.glm("y ~ C(venue) + C(year)", data=d, family=sm.families.Binomial()).fit()
        # 2026 vs 2025 contrast (within venue; 2026 has ICRA, RSS and the journals) with its covariance
        a, b_ = "C(year)[T.2026]", "C(year)[T.2025]"
        cov = f1.cov_params()
        diff = f1.params[a] - f1.params[b_]
        se_d = np.sqrt(cov.loc[a, a] + cov.loc[b_, b_] - 2 * cov.loc[a, b_])
        res["OR_26v25"] = np.exp(diff); res["OR_26v25_lo"] = np.exp(diff - 1.96 * se_d); res["OR_26v25_hi"] = np.exp(diff + 1.96 * se_d)
        res["p_26v25"] = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(diff / se_d)))
        for yr in (2025, 2026):
            name = f"C(year)[T.{yr}]"
            b, se = f1.params[name], f1.bse[name]
            res[f"OR_{yr}"] = np.exp(b); res[f"OR_{yr}_lo"] = np.exp(b - 1.96 * se); res[f"OR_{yr}_hi"] = np.exp(b + 1.96 * se)
            res[f"p_{yr}"] = f1.pvalues[name]
        d2 = d.assign(t=d.year - 2024)
        f2 = smf.glm("y ~ C(venue) + t", data=d2, family=sm.families.Binomial()).fit()
        b, se = f2.params["t"], f2.bse["t"]
        res["annual_OR"] = np.exp(b); res["annual_OR_lo"] = np.exp(b - 1.96 * se); res["annual_OR_hi"] = np.exp(b + 1.96 * se)
        res["p_trend"] = f2.pvalues["t"]
    except Exception as e:  # noqa: BLE001
        res["error"] = str(e)[:120]
    rows.append(res)

out = pd.DataFrame(rows)
ok = out.p_trend.notna()
out.loc[ok, "q_trend"] = multipletests(out.loc[ok, "p_trend"], method="fdr_bh")[1]
out["call"] = np.where(out.q_trend < 0.05, np.where(out.annual_OR > 1, "rising", "declining"), "unclear")
okc = out.p_26v25.notna()
out.loc[okc, "q_26v25"] = multipletests(out.loc[okc, "p_26v25"], method="fdr_bh")[1]
out["shape_26v25"] = np.where(out.q_26v25 < 0.05, np.where(out.OR_26v25 > 1, "up 2025->26", "down 2025->26"), "no clear change 2025->26")
out = out.sort_values("annual_OR", ascending=False)
out.to_csv(os.path.join(ROOT, "results", f"trends{SUFFIX}.csv"), index=False)
pd.DataFrame(share_rows).to_csv(os.path.join(ROOT, "results", f"shares_by_venue_year{SUFFIX}.csv"), index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100)
show = out[["family", "topic", "n_2024", "n_2025", "n_2026", "share_2024", "share_2025", "share_2024_same5", "share_2026_same5",
            "annual_OR", "annual_OR_lo", "annual_OR_hi", "q_trend", "call", "OR_26v25", "OR_26v25_lo", "OR_26v25_hi", "shape_26v25"]].copy()
for c in ("OR_26v25", "OR_26v25_lo", "OR_26v25_hi"):
    show[c] = show[c].round(2)
for c in ("share_2024", "share_2025", "share_2024_same5", "share_2026_same5"):
    show[c] = (100 * show[c]).round(2)
for c in ("annual_OR", "annual_OR_lo", "annual_OR_hi"):
    show[c] = show[c].round(2)
show["q_trend"] = show.q_trend.map(lambda q: f"{q:.1e}")
show["topic"] = show.topic.str.slice(0, 44)
print(show.to_string(index=False))
print("\npapers per year:", m.groupby("year").size().to_dict())
