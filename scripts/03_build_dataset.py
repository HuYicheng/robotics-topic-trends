"""Build the paper table used by the analysis: one source per venue across years.

ICRA  2024-2026 : OpenAlex (has 2026; title sets match dblp for 2024/25 apart from front matter)
IROS  2022-2025 : dblp            (IROS 2026 proceedings not published yet)
RSS   2024-2026 : roboticsproceedings.org (2024 identical to dblp); 2022-23 dblp (context only)
CoRL  2024-2025 : PMLR v270/v305  (2024 matches dblp); 2022-23 dblp; CoRL 2026 list not public
T-RO, IJRR, Science Robotics 2022-2026 : dblp (2026 = issues published so far)
ICRA 2022-2023 : dblp (context only)
Output: data/papers.csv (venue, year, title, source, uid) and results/removed_nonpapers.txt
"""
import csv
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NONPAPER = re.compile(
    r"^(front matter|back matter|table of contents|author index|cover page|contributor page|organizing committee|"
    r"program|conference information|top menu|preface|welcome|message from|keynote|plenary|editorial|guest editorial|"
    r"erratum|errata|corrigendum|corrections? to|retraction|retracted|expression of concern|in memoriam|reviewers|"
    r"list of reviewers|editor'?s note|information for authors|ieee transactions on robotics information)\b"
    r"|^icra 20\d\d\b|^iros 20\d\d\b|^\d{4} ieee international conference on robotics",
    re.I)


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def main():
    dblp = [json.loads(l) for l in open(os.path.join(ROOT, "data", "dblp_venues_2022_2026.jsonl"))]
    extra = [json.loads(l) for l in open(os.path.join(ROOT, "data", "extra_venues.jsonl"))]
    rows = []
    for r in dblp:
        v, y = r["venue"], r["year"]
        use = ((v == "IROS") or (v in ("T-RO", "IJRR", "SciRobotics"))
               or (v in ("ICRA", "RSS", "CoRL") and y <= 2023))
        if use:
            rows.append({"venue": v, "year": y, "title": r["title"], "source": "dblp", "uid": r["key"]})
    for r in extra:
        rows.append({"venue": r["venue"], "year": r["year"], "title": r["title"], "source": r["source"],
                     "uid": r.get("id") or f'{r["source"]}:{norm(r["title"])[:60]}'})
    removed, seen, out = [], set(), []
    for r in rows:
        t = (r["title"] or "").strip().rstrip(".")
        if not t or NONPAPER.search(t):
            removed.append(f'{r["venue"]} {r["year"]} | {t}')
            continue
        k = (r["venue"], r["year"], norm(t))
        if k in seen:
            removed.append(f'{r["venue"]} {r["year"]} | DUPLICATE | {t}')
            continue
        seen.add(k)
        r["title"] = t
        out.append(r)
    with open(os.path.join(ROOT, "data", "papers.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["venue", "year", "title", "source", "uid"])
        w.writeheader(); w.writerows(out)
    with open(os.path.join(ROOT, "results", "removed_nonpapers.txt"), "w") as f:
        f.write("\n".join(removed) + "\n")
    from collections import Counter
    c = Counter((r["venue"], r["year"]) for r in out)
    venues = ["ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"]
    print("papers kept:", len(out), " removed:", len(removed))
    print("venue        " + " ".join(f"{y:>6d}" for y in range(2022, 2027)))
    for v in venues:
        print(f"{v:12s} " + " ".join(f"{c[(v, y)]:>6d}" for y in range(2022, 2027)))


if __name__ == "__main__":
    main()
