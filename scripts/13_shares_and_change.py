"""Main table (title + abstract measure): share of each topic per year, comparable across years, and its change.

Share per year = topic share standardised to the 2025 venue mix (all seven venues), from the per-topic logistic
model  topic ~ C(venue) + C(year)  fitted on 2024-2026 papers with abstracts. For 2024 and 2025 this is close to the
raw pooled share; for 2026 (no IROS, no CoRL yet) it is the 2025 mix moved by the within-venue 2026 change seen at
ICRA, RSS and the journals. 95% intervals by simulating the coefficients from their estimated covariance (2,000 draws).
Raw pooled shares are kept alongside. Change: percentage points 2024->2026, annual odds multiplier with 95% CI,
Benjamini-Hochberg q; call 'rising'/'declining' only at q < 0.05.
Output: results/shares_and_change_ta.csv
"""
import importlib.util
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = importlib.util.spec_from_file_location("t", os.path.join(ROOT, "scripts", "04_topics.py"))
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
family = {n: f for n, f, _ in t.TOPICS}
m = pd.read_csv(os.path.join(ROOT, "data", "topic_matrix_ta.csv"))
m = m[m.year.between(2024, 2026)]
ref = m[m.year == 2025].venue.value_counts(normalize=True)          # 2025 venue mix
rng = np.random.default_rng(0)
rows = []
for topic in [n for n, f, _ in t.TOPICS if f != "E term"]:
    d = m[["venue", "year", topic]].rename(columns={topic: "y"})
    keep = d.groupby("venue").y.sum(); d = d[d.venue.isin(keep[keep > 0].index)]
    f1 = smf.glm("y ~ C(venue) + C(year)", data=d, family=sm.families.Binomial()).fit()
    names = f1.params.index
    draws = rng.multivariate_normal(f1.params.values, f1.cov_params().values, size=2000)
    r = {"topic": topic, "family": family[topic]}
    for yr in (2024, 2025, 2026):
        X = []
        w = []
        for v, share in ref.items():
            x = np.zeros(len(names)); x[list(names).index("Intercept")] = 1
            if f"C(venue)[T.{v}]" in names:
                x[list(names).index(f"C(venue)[T.{v}]")] = 1
            elif v not in keep[keep > 0].index:
                continue                                                 # venue never has the topic: share 0
            if f"C(year)[T.{yr}]" in names:
                x[list(names).index(f"C(year)[T.{yr}]")] = 1
            X.append(x); w.append(share)
        X, w = np.array(X), np.array(w)
        point = float((w / ref.sum() * (1 / (1 + np.exp(-X @ f1.params.values)))).sum())
        sims = ((1 / (1 + np.exp(-draws @ X.T))) * w).sum(axis=1)
        r[f"share_{yr}"] = 100 * point
        r[f"share_{yr}_lo"], r[f"share_{yr}_hi"] = 100 * np.percentile(sims, 2.5), 100 * np.percentile(sims, 97.5)
        g = m[m.year == yr]
        r[f"raw_{yr}"] = 100 * g[topic].mean(); r[f"n_{yr}"] = int(g[topic].sum())
    f2 = smf.glm("y ~ C(venue) + t", data=d.assign(t=d.year - 2024), family=sm.families.Binomial()).fit()
    b, se = f2.params["t"], f2.bse["t"]
    r.update(annual_OR=np.exp(b), annual_OR_lo=np.exp(b - 1.96 * se), annual_OR_hi=np.exp(b + 1.96 * se), p=f2.pvalues["t"])
    r["change_pp_24_26"] = r["share_2026"] - r["share_2024"]
    rows.append(r)
out = pd.DataFrame(rows)
out["q"] = multipletests(out.p, method="fdr_bh")[1]
out["call"] = np.where(out.q < 0.05, np.where(out.annual_OR > 1, "rising", "declining"), "unclear")
out = out.sort_values("share_2025", ascending=False)
out.to_csv(os.path.join(ROOT, "results", "shares_and_change_ta.csv"), index=False)
print("papers with abstracts per year:", m.groupby("year").size().to_dict())
show = out[["topic", "share_2024", "share_2025", "share_2026", "change_pp_24_26", "annual_OR", "annual_OR_lo", "annual_OR_hi", "q", "call"]].copy()
for c in ("share_2024", "share_2025", "share_2026", "change_pp_24_26"):
    show[c] = show[c].map(lambda v: f"{v:+.1f}" if c.startswith("change") else f"{v:.1f}")
for c in ("annual_OR", "annual_OR_lo", "annual_OR_hi"):
    show[c] = show[c].round(2)
show["q"] = show.q.map(lambda v: f"{v:.0e}")
show["topic"] = show.topic.str.slice(0, 44)
pd.set_option("display.width", 220)
print(show.to_string(index=False))
