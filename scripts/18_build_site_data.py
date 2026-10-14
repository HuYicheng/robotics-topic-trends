"""Data for the interactive page: site/data.json.

Contents: topics (name, family, standardised shares 2024/25/26 with 2026 interval, change, annual multiplier, call),
papers of the final measure (title, venue, year, link, topic indices), papers per venue-year, build metadata.
No abstract text is published (publishers hold the copyright); abstracts were only used to assign topics.
Links: DOI where known (dblp ee / OpenAlex doi), RSS proceedings page, PMLR page, else the OpenAlex record.
"""
import csv
import json
import os
import time

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "site", "data.json")
VENUES = ["ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"]


def main():
    sc = pd.read_csv(os.path.join(ROOT, "results", "shares_and_change_ta.csv")).sort_values("share_2025", ascending=False)
    topics = list(sc.topic)
    m = pd.read_csv(os.path.join(ROOT, "data", "topic_matrix_ta.csv"))
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        papers = {r["uid"]: r for r in csv.DictReader(f)}
    dblp = {r["key"]: r for r in map(json.loads, open(os.path.join(ROOT, "data", "dblp_venues_2022_2026.jsonl")))}
    extra = {r.get("id"): r for r in map(json.loads, open(os.path.join(ROOT, "data", "extra_venues.jsonl")))}

    def link(uid, src):
        if src == "dblp":
            ee = dblp[uid]["ee"]
            return next((e for e in ee if "doi.org/" in e), ee[0] if ee else None)
        if src.startswith("openalex"):
            r = extra.get(uid) or {}
            return r.get("doi") or uid.replace("https://openalex.org/", "https://openalex.org/works/")
        if src.startswith("roboticsproceedings"):
            return f"https://www.roboticsproceedings.org/{uid}.html"
        if src.startswith("pmlr"):
            return uid
        return None

    rows, missing = [], 0
    cols = [m.columns.get_loc(t) for t in topics]
    for rec in m.itertuples(index=False):
        uid, venue, year = rec[0], rec[1], int(rec[2])
        p = papers[uid]
        url = link(uid, p["source"])
        missing += url is None
        ks = [i for i, c in enumerate(cols) if rec[c] == 1]
        rows.append([p["title"], VENUES.index(venue), year, url or "", ks])
    rows.sort(key=lambda r: (-r[2], r[1], r[0].lower()))
    totals = {f"{v}|{y}": int(n) for (v, y), n in m.groupby(["venue", "year"]).size().items()}
    # full precision (6 decimals): the page rounds once for display, so it shows the same numbers as REPORT.md
    tp = [{"name": r.topic, "family": r.family.split(" ", 1)[1], "s24": round(r.share_2024, 6), "s25": round(r.share_2025, 6),
           "s26": round(r.share_2026, 6), "s26lo": round(r.share_2026_lo, 6), "s26hi": round(r.share_2026_hi, 6),
           "dpp": round(r.change_pp_24_26, 6), "or": round(r.annual_OR, 6), "orlo": round(r.annual_OR_lo, 6),
           "orhi": round(r.annual_OR_hi, 6), "q": float(f"{r.q:.3g}"), "call": r.call} for r in sc.itertuples()]
    # per-scope results (scripts/20_scope_trends.py): all venues, conferences, journals, each venue
    st = pd.read_csv(os.path.join(ROOT, "results", "scope_trends_ta.csv"))
    tindex = {r["name"]: i for i, r in enumerate(tp)}
    scopes = {}
    for scope, g in st.groupby("scope", sort=False):
        years = [int(y) for y in g.years.iloc[0].split(",")]
        srows = []
        for r in g.itertuples():
            def f(c, r=r):
                v = getattr(r, c, float("nan"))
                return None if v is None or pd.isna(v) or not np.isfinite(float(v)) else round(float(v), 6)
            srows.append({"i": tindex[r.topic], "s": [f(f"share_{y}") for y in years], "lo": [f(f"lo_{y}") for y in years],
                          "hi": [f(f"hi_{y}") for y in years], "k": [int(getattr(r, f"k_{y}")) for y in years],
                          "n": [int(getattr(r, f"n_{y}")) for y in years], "dpp": f("change_pp"), "or": f("OR"),
                          "orlo": f("OR_lo"), "orhi": f("OR_hi"), "q": f("q"), "call": r.call,
                          "note": (r.note if isinstance(getattr(r, "note", None), str) else None)})
        scopes[scope] = {"years": years, "single": scope in VENUES, "rows": srows}
    data = {"built": time.strftime("%Y-%m-%d"), "venues": VENUES, "topics": tp, "totals": totals, "papers": rows, "scopes": scopes}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)  # fail on NaN/Infinity
    print(f"{len(rows)} papers, {len(tp)} topics, links missing for {missing}; {os.path.getsize(OUT) / 1e6:.2f} MB")
    by = {}
    for r in rows:
        dom = (r[3].split("/")[2] if r[3] else "none")
        by[dom] = by.get(dom, 0) + 1
    print("link hosts:", dict(sorted(by.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
