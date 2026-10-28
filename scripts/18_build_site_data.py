"""Data for the interactive page: site/data.json.

Contents: topics (name, family, standardised share per year with 95% interval, change, annual multiplier, call, the same
for 2024 onwards), per-scope results (all venues, conferences, journals, each venue: share, interval, papers k of n per
year, trend), papers of the final measure (title, venue, year, link, topic indices), papers per venue-year, build metadata.
Per scope, "partial" lists years that are not complete (a member venue not yet published, a journal year still running, or a
member venue-year where under 95% of the papers have an abstract, listed in "coverage")
and "estimated" the years whose standardised share includes a venue without papers (model estimate).
No abstract text is published (publishers hold the copyright); abstracts were only used to assign topics.
Links: DOI where known (dblp ee / OpenAlex doi / PubMed), RSS proceedings page, PMLR page, OpenReview page (CoRL from the
conference site), else the OpenAlex record.
"""
import csv
import json
import os
import time

import numpy as np
import pandas as pd
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "site", "data.json")
VENUES = config.VENUES
JOURNALS = {"T-RO", "IJRR", "SciRobotics"}          # their last year is still running when the data are collected
GROUPS = {"All venues": VENUES, "Conferences": ["ICRA", "IROS", "RSS", "CoRL"], "Journals": ["T-RO", "IJRR", "SciRobotics"]}


def main():
    sc = pd.read_csv(os.path.join(ROOT, "results", "shares_and_change_ta.csv")).sort_values(f"share_{config.REF_YEAR}", ascending=False)
    topics = list(sc.topic)
    m = pd.read_csv(os.path.join(ROOT, "data", "topic_matrix_ta.csv"))
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        papers = {r["uid"]: r for r in csv.DictReader(f)}
    dblp = {r["key"]: r for r in map(json.loads, open(os.path.join(ROOT, config.DBLP_EXTRACT)))}
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
        if src.startswith("pmlr") or src == "pubmed":       # PubMed-only Science Robotics items: uid is the DOI link
            return uid
        if src.startswith("corl.org/"):                      # CoRL from the conference site: uid is the OpenReview page
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
    # venue-years where under 95% of the papers have an abstract (only those are analysed): [with abstract, all papers].
    # CoRL 2026 (conference-site list, arXiv abstracts): its counts are not comparable with earlier years.
    n_all = pd.DataFrame(papers.values()).astype({"year": int}).groupby(["venue", "year"]).size()
    coverage = {f"{v}|{y}": [totals.get(f"{v}|{y}", 0), int(n)] for (v, y), n in n_all.items()
                if y in config.YEARS and totals.get(f"{v}|{y}", 0) < 0.95 * n}
    print("venue-years with under 95% abstracts:", coverage)
    # full precision (6 decimals): the page rounds once for display, so it shows the same numbers as REPORT.md
    R6 = lambda v: None if v is None or pd.isna(v) or not np.isfinite(float(v)) else round(float(v), 6)
    tp = [{"name": r["topic"], "family": r["family"].split(" ", 1)[1],
           "s": [R6(r[f"share_{y}"]) for y in config.YEARS], "lo": [R6(r[f"share_{y}_lo"]) for y in config.YEARS],
           "hi": [R6(r[f"share_{y}_hi"]) for y in config.YEARS], "dpp": R6(r["change_pp"]), "or": R6(r["annual_OR"]),
           "orlo": R6(r["annual_OR_lo"]), "orhi": R6(r["annual_OR_hi"]), "q": float(f"{r['q']:.3g}"), "call": r["call"],
           "ror": R6(r["recent_OR"]), "rcall": r["recent_call"]} for _, r in sc.iterrows()]
    # per-scope results: the ten named scopes (scripts/20_scope_trends.py) go into data.json; the other 117 venue
    # combinations (scripts/20b_scope_subsets.py) into subsets.json, which the page loads when a combination is chosen
    tindex = {r["name"]: i for i, r in enumerate(tp)}

    def build_scopes(st):
        out = {}
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
                              "ror": f("rec_OR"), "rcall": (r.rec_call if isinstance(getattr(r, "rec_call", None), str) else "unclear"),
                              "note": (r.note if isinstance(getattr(r, "note", None), str) else None)})
            members = GROUPS.get(scope, scope.split("+"))
            last = config.YEARS[-1]
            missing = [v for v in members if totals.get(f"{v}|{last}", 0) == 0]
            running = [v for v in members if v in JOURNALS]
            incomplete = [v for v in members if f"{v}|{last}" in coverage]
            partial = [last] if last in years and (missing or running or incomplete) else []
            estimated = [last] if last in years and missing and len(members) > 1 else []
            out[scope] = {"years": years, "single": len(members) == 1, "members": members, "partial": partial,
                          "estimated": estimated, "rows": srows}
        return out
    scopes = build_scopes(pd.read_csv(os.path.join(ROOT, "results", "scope_trends_ta.csv")))
    subsets = build_scopes(pd.read_csv(os.path.join(ROOT, "results", "scope_trends_subsets_ta.csv")))
    with open(os.path.join(os.path.dirname(OUT), "subsets.json"), "w") as fh:
        json.dump({"scopes": subsets}, fh, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    print(f"subsets.json: {len(subsets)} venue combinations, {os.path.getsize(os.path.join(os.path.dirname(OUT), 'subsets.json')) / 1e6:.2f} MB")
    ab = pd.DataFrame([json.loads(l) for l in open(os.path.join(ROOT, "data", "abstracts.jsonl"))])
    abs_words = {int(y): int(w) for y, w in ab.assign(w=ab.abstract.str.split().str.len()).groupby("year").w.median().items()}
    data = {"built": time.strftime("%Y-%m-%d"), "years": config.YEARS, "ref": config.REF_YEAR, "venues": VENUES, "topics": tp,
            "abs_words": abs_words, "coverage": coverage,
            "totals": totals, "papers": rows, "scopes": scopes}
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
