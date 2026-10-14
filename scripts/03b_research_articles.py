"""Keep research articles only (user, 2026-10-14: no editorials or commentaries, only research articles).

Input data/papers_all.csv (03_build_dataset.py). Every item gets a type:
  research      : kept
  review        : reviews and surveys; kept only if config.KEEP_REVIEWS (default False)
  non-research  : editorials, commentaries, Focus / highlight / viewpoint / fiction pieces, errata, special-issue
                  introductions; always removed
Rules by venue:
  ICRA, IROS, RSS, CoRL : accepted papers are research papers (front matter already removed by 03).
  Science Robotics      : PubMed record (NCBI E-utilities, cached in data/pubmed_scirobotics.jsonl).
                          non-research = publication type Editorial / Comment / News / Erratum / ... , or an abstract
                          shorter than 60 words: Focus, Research Highlight, Viewpoint and fiction pieces carry a one-
                          sentence teaser of 6-31 words, research articles 98 words or more, so 60 separates them.
                          review = publication type Review with a full abstract (>= 60 words).
                          Items missing from PubMed are non-research unless an abstract of >= 60 words exists.
  T-RO, IJRR            : title rules (editorial, special issue / selected papers, a look back, in memoriam, errata;
                          survey / review / tutorial). Every hit is listed and was read.
Science Robotics research articles that PubMed lists but the dblp dump does not yet contain (latest 2026 issues) are
added from PubMed (source "pubmed", uid = DOI link).
Output: data/papers.csv (kept items; same columns as papers_all.csv), data/article_types.csv (every item with its type
and the reason), results/removed_nonresearch.txt. No personal data in requests.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UA = {"User-Agent": "robotics-trends-study/0.1 (research script)"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CACHE = os.path.join(ROOT, "data", "pubmed_scirobotics.jsonl")
MIN_WORDS = 60

NONRESEARCH_PT = {"Editorial", "Comment", "News", "Published Erratum", "Retraction of Publication", "Retraction Notice",
                  "Interview", "Biography", "Portrait", "Introductory Journal Article", "Letter", "Lecture",
                  "Expression of Concern", "Correction"}
REVIEW_PT = {"Review", "Systematic Review", "Meta-Analysis", "Scoping Review"}
NONRESEARCH_TITLE = re.compile(
    r"^(guest )?editorial\b|\beditorial\s*$|editorialspecial|^introduction to the special|^special (issue|section|collection)\b|"
    r"^selected papers from|\ba look back\b|^in memoriam|^(erratum|errata|corrigendum|correction|retraction)\b|"
    r"^why we must trust ourselves$|^robotics: science and systems \(rss\) \d{4}$", re.I)
REVIEW_TITLE = re.compile(
    r"\b(a|an) (comprehensive |systematic |brief |short |tutorial )?(survey|review)\b|:\s*(a|an)? ?(comprehensive |systematic )?(survey|review)\b"
    r"|\b(survey|review) (of|on)\b|\btutorial\b|^review\b|^survey\b", re.I)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            log(f"  {type(e).__name__} {e} on {url[:100]} (attempt {i + 1}/{tries})")
            time.sleep(5 * 2 ** i)
    return None


def norm(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def fetch_pubmed():
    q = urllib.parse.urlencode({"db": "pubmed", "term": f'"Sci Robot"[jour] AND {config.YEAR_MIN}:{config.YEAR_MAX}[dp]',
                                "retmax": 5000, "retmode": "json", "tool": "robotics-trends-study"})
    ids = json.loads(get(EUTILS + "esearch.fcgi?" + q))["esearchresult"]["idlist"]
    log("PubMed Science Robotics records:", len(ids))
    recs = []
    for i in range(0, len(ids), 200):
        q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids[i:i + 200]), "retmode": "xml", "tool": "robotics-trends-study"})
        root = ET.fromstring(get(EUTILS + "efetch.fcgi?" + q))
        for art in root.iter("PubmedArticle"):
            t = art.find(".//ArticleTitle")
            doi = next((e.text for e in art.iter("ArticleId") if e.get("IdType") == "doi"), None) \
                or next((e.text for e in art.iter("ELocationID") if e.get("EIdType") == "doi"), None)
            recs.append({"pmid": art.findtext(".//PMID"), "doi": (doi or "").lower(),
                         "title": "".join(t.itertext()) if t is not None else "",
                         "types": [e.text for e in art.iter("PublicationType")],
                         "abstract": " ".join("".join(a.itertext()).strip() for a in art.iter("AbstractText")).strip(),
                         "year": art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//ArticleDate/Year")})
        time.sleep(0.5)
    with open(CACHE, "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return recs


def main():
    recs = [json.loads(l) for l in open(CACHE)] if os.path.exists(CACHE) and "--refresh" not in sys.argv else fetch_pubmed()
    by_doi = {r["doi"]: r for r in recs if r["doi"]}
    by_title = {norm(r["title"]): r for r in recs}
    dblp = {r["key"]: r for r in map(json.loads, open(os.path.join(ROOT, config.DBLP_EXTRACT)))}
    cached = {}
    cpath = os.path.join(ROOT, "data", "abstracts_cache.jsonl")
    if os.path.exists(cpath):
        for l in open(cpath):
            r = json.loads(l); cached.setdefault(r["uid"], r["abstract"])
    with open(os.path.join(ROOT, "data", "papers_all.csv")) as f:
        papers = list(csv.DictReader(f))
    types = []
    for p in papers:
        v, title = p["venue"], p["title"]
        typ, reason = "research", "accepted conference paper" if v in ("ICRA", "IROS", "RSS", "CoRL") else ""
        if v in ("T-RO", "IJRR"):
            if NONRESEARCH_TITLE.search(title):
                typ, reason = "non-research", "title"
            elif REVIEW_TITLE.search(title):
                typ, reason = "review", "title"
            else:
                reason = "title rules: no hit"
        elif v == "SciRobotics":
            doi = next((e.split("doi.org/")[1].lower() for e in dblp.get(p["uid"], {}).get("ee", []) if "doi.org/10." in e), None)
            r = by_doi.get(doi) or by_title.get(norm(title))
            if r is None:
                w = len(cached.get(p["uid"], "").split())
                typ, reason = ("research", f"not in PubMed; abstract {w} words") if w >= MIN_WORDS \
                    else ("non-research", f"not in PubMed; abstract {w} words")
            else:
                pts, w = set(r["types"]), len(r["abstract"].split())
                if pts & NONRESEARCH_PT:
                    typ, reason = "non-research", "PubMed type " + ", ".join(sorted(pts & NONRESEARCH_PT))
                elif w < MIN_WORDS:
                    typ, reason = "non-research", f"PubMed abstract {w} words (teaser)"
                elif pts & REVIEW_PT:
                    typ, reason = "review", "PubMed type " + ", ".join(sorted(pts & REVIEW_PT))
                else:
                    reason = f"PubMed {', '.join(sorted(pts))}; abstract {w} words"
        types.append({**p, "type": typ, "reason": reason})
    # research articles in PubMed that the dblp dump does not contain yet (its latest issues lag)
    known_doi, known_title = set(), {norm(p["title"]) for p in papers if p["venue"] == "SciRobotics"}
    for p in papers:
        if p["venue"] == "SciRobotics":
            known_doi |= {e.split("doi.org/")[1].lower() for e in dblp.get(p["uid"], {}).get("ee", []) if "doi.org/10." in e}
    for r in recs:
        y = int(r["year"]) if (r.get("year") or "").isdigit() else None
        pts = set(r["types"])
        if (y in config.YEARS and r["doi"] and r["doi"] not in known_doi and norm(r["title"]) not in known_title
                and not pts & (NONRESEARCH_PT | REVIEW_PT) and len(r["abstract"].split()) >= MIN_WORDS):
            types.append({"venue": "SciRobotics", "year": str(y), "title": r["title"].strip().rstrip("."), "source": "pubmed",
                          "uid": "https://doi.org/" + r["doi"], "type": "research",
                          "reason": f"PubMed only (not yet in dblp); {', '.join(sorted(pts))}"})
    with open(os.path.join(ROOT, "data", "article_types.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["uid", "venue", "year", "title", "type", "reason"])
        w.writeheader(); w.writerows({k: t[k] for k in ("uid", "venue", "year", "title", "type", "reason")} for t in types)
    keep = {"research", "review"} if config.KEEP_REVIEWS else {"research"}
    kept = [t for t in types if t["type"] in keep]
    with open(os.path.join(ROOT, "data", "papers.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["venue", "year", "title", "source", "uid"])
        w.writeheader(); w.writerows({k: t[k] for k in ("venue", "year", "title", "source", "uid")} for t in kept)
    with open(os.path.join(ROOT, "results", "removed_nonresearch.txt"), "w") as f:
        f.write(f"# Items removed by scripts/03b_research_articles.py (KEEP_REVIEWS={config.KEEP_REVIEWS}): venue year | type | reason | title\n")
        for t in sorted((t for t in types if t["type"] not in keep), key=lambda t: (t["venue"], t["year"], t["type"], t["title"])):
            f.write(f'{t["venue"]} {t["year"]} | {t["type"]} | {t["reason"]} | {t["title"]}\n')
    c = Counter((t["venue"], t["type"]) for t in types)
    log("items:", len(types), " kept:", len(kept))
    for v in config.VENUES:
        log(f"  {v:12s} research {c[(v, 'research')]:5d}  review {c[(v, 'review')]:3d}  non-research {c[(v, 'non-research')]:3d}")


if __name__ == "__main__":
    main()
