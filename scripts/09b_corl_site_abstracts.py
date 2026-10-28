"""Abstracts for the CoRL papers taken from the conference site (config.CORL_SITE years: no PMLR bibliography yet).

The complete source would be OpenReview, but its API answers anonymous requests with an anti-bot challenge
(403 "ChallengeRequiredError", checked 2026-10-28); this study does not get around such pages. So the abstract of the
paper's arXiv version is used, as 09_fetch_abstracts.py does for its last fallback:
  1. arXiv ids and titles from
     a. the arXiv monthly listing pages (arxiv.org/list/<archive>/<yyyy-mm>; allowed by arxiv.org/robots.txt, one
        request per 16 s, Crawl-delay is 15), saved in data/raw/arxiv_listings/: cs.RO for 2025-09 .. 2026-10, and all
        of cs for 2026-06, 2026-09 and 2026-10, the three months with the most CoRL 2026 papers in cs.RO (the all-cs
        pages added 3 papers; other months were not fetched);
     b. the arXiv (CoRR) records of the dblp dump (dump of 2026-10-13, ~/.cache/robotics-trends/dblp), extracted once to
        data/dblp_corr_2025_2026.jsonl. dblp holds only part of arXiv: about 60% of the cs.RO listing of 2026-01 ..
        2026-09 and none of 2026-10.
  2. a paper gets an arXiv id when the titles are identical after compacting (letters and digits only, the rule of
     09_fetch_abstracts.py), here after also folding formatting: NFKC (superscripts), Greek letters spelled out,
     LaTeX commands dropped (\\pi kept as pi). Pairs whose titles differ in wording were read one by one; the accepted
     ones are listed with the reason in data/corl_site_manual_matches.csv.
  3. abstract: the OpenAlex record of the arXiv DOI (10.48550/arxiv.<id>, batches of 50, 1 credit each); for ids
     without an OpenAlex abstract, the arXiv abstract page (arxiv.org/abs/<id>, one request per 16 s).
     export.arxiv.org (its robots.txt disallows everything) and Semantic Scholar are not used.
Abstracts go into data/abstracts_cache.jsonl (source "arxiv <id> via openalex" / "arxiv <id> abstract page");
09_fetch_abstracts.py --no-fetch then writes data/abstracts.jsonl. Papers without an arXiv version have no abstract and,
like every paper without one, are not in the analysis. Check (2026-10-28): OpenAlex title search for 10 random papers
still without one found none of them (its positive control, a matched CoRL paper, was found), so most of the rest seem
not to be public yet; the PMLR volume should replace this source when it is out. Per-paper record: data/corl_site_arxiv.csv.
No personal data in requests (no email, no API key).
"""
import csv
import gzip
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UA = {"User-Agent": "robotics-trends-study/0.1 (research script)"}
CACHE = os.path.join(ROOT, "data", "abstracts_cache.jsonl")
LISTINGS = os.path.join(ROOT, "data", "raw", "arxiv_listings")
LISTING_PAGES = ([("cs.RO", f"{y}-{m:02d}") for y, m in [(2025, 9), (2025, 10), (2025, 11), (2025, 12)] + [(2026, m) for m in range(1, 11)]]
                 + [("cs", ym) for ym in ("2026-06", "2026-09", "2026-10")])
CORR = os.path.join(ROOT, "data", "dblp_corr_2025_2026.jsonl")
DUMP = os.path.expanduser("~/.cache/robotics-trends/dblp/dblp.xml.gz")
MANUAL = os.path.join(ROOT, "data", "corl_site_manual_matches.csv")
OUT = os.path.join(ROOT, "data", "corl_site_arxiv.csv")
GREEK = dict(zip("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ",
                 ("alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau "
                  "upsilon phi chi psi omega").split() * 2))
LATEX_GREEK = {"\\" + v for v in set(GREEK.values())}
_last = [0.0]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def get(url, spacing=0.0, tries=3):
    for i in range(tries):
        wait = spacing - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            log(f"  HTTP {e.code} on {url[:100]} (attempt {i + 1}/{tries})")
            if e.code in (403, 404):
                return None                                  # not found, or a block: do not retry
        except Exception as e:  # noqa: BLE001
            log(f"  {type(e).__name__} on {url[:100]} (attempt {i + 1}/{tries})")
        time.sleep(30 * 2 ** i)
    return None


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def fold(t):
    """Compact title: letters and digits only, after NFKC, Greek letters spelled out and LaTeX commands dropped."""
    t = unicodedata.normalize("NFKC", html.unescape(t or ""))
    t = "".join(GREEK.get(c, c) for c in t)
    t = re.sub(r"\\([A-Za-z]+)", lambda m: m.group(1) if "\\" + m.group(1) in LATEX_GREEK else " ", t)
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def listing_titles():
    os.makedirs(LISTINGS, exist_ok=True)
    out = {}
    for arch, ym in LISTING_PAGES:
        skip = 0
        while True:
            fn = os.path.join(LISTINGS, f"{arch}_{ym}_{skip}.html")
            if not os.path.exists(fn):
                page = get(f"https://arxiv.org/list/{arch}/{ym}?skip={skip}&show=2000", spacing=16)
                if page is None:
                    log("  listing not fetched:", ym, skip); break
                open(fn, "w").write(page)
            page = open(fn, encoding="utf-8", errors="replace").read()
            total = int(re.search(r"Total of (\d+) entries", page).group(1))
            for dt, dd in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", page, flags=re.S):
                m = re.search(r'id="(\d{4}\.\d{4,5})"', dt)
                ti = re.search(r"<div class='list-title mathjax'><span class='descriptor'>Title:</span>(.*?)</div>", dd, flags=re.S)
                if m and ti:
                    out[m.group(1)] = text(ti.group(1))
            skip += 2000
            if skip >= total:
                break
    return out


def corr_titles():
    if not os.path.exists(CORR):                     # one line-by-line pass over the dump (each record starts a line)
        start = re.compile(r'^<article [^>]*key="journals/corr/abs-(\d{4})-')
        buf = None
        with gzip.open(DUMP, "rt", encoding="utf-8", errors="replace") as f, open(CORR, "w") as out:
            for line in f:
                if buf is None:
                    m = start.match(line)
                    if m and m.group(1) >= "2501":
                        buf = [line]
                    continue
                buf.append(line)
                if line.startswith("</article>"):
                    rec, buf = "".join(buf), None
                    ti = re.search(r"<title>(.*?)</title>", rec, flags=re.S)
                    out.write(json.dumps({"key": re.search(r'key="([^"]+)"', rec).group(1),
                                          "title": text(ti.group(1)) if ti else None,
                                          "ee": [text(e) for e in re.findall(r"<ee[^>]*>(.*?)</ee>", rec, flags=re.S)]},
                                         ensure_ascii=False) + "\n")
    out = {}
    for r in map(json.loads, open(CORR)):
        m = re.search(r"abs-(\d{4})-(\d{4,5})$", r["key"])
        out[f"{m.group(1)}.{m.group(2)}"] = (r["title"] or "").rstrip(".")
    return out


def oa_abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    words = sorted((p, word) for word, ps in inv.items() for p in ps)
    return " ".join(word for _, word in words) or None


def main():
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        papers = [r for r in csv.DictReader(f) if r["source"].startswith("corl.org/")]
    lst, corr = listing_titles(), corr_titles()
    log(f"CoRL papers from the site: {len(papers)}; arXiv titles: listings {len(lst)}, dblp CoRR {len(corr)}")
    index = {}
    for src, d in (("listing", lst), ("dblp", corr)):
        for aid, t in d.items():
            index.setdefault(fold(t), {}).setdefault(aid, (t, set()))[1].add(src)
    manual = {}
    if os.path.exists(MANUAL):
        for r in csv.DictReader(open(MANUAL)):
            manual[r["openreview"]] = r
    match = {}
    for p in papers:
        hits = index.get(fold(p["title"]), {})
        if len(hits) == 1:
            aid, (t, srcs) = next(iter(hits.items()))
            match[p["uid"]] = {"arxiv": aid, "arxiv_title": t, "how": "identical title (" + "+".join(sorted(srcs)) + ")"}
        elif len(hits) > 1:
            log("  several arXiv ids for one title, left out:", p["title"][:80], sorted(hits))
        elif p["uid"] in manual:
            r = manual[p["uid"]]
            match[p["uid"]] = {"arxiv": r["arxiv_id"], "arxiv_title": r["arxiv_title"], "how": "read: " + r["reason"]}
    used = {}
    for u, m in match.items():
        used.setdefault(m["arxiv"], []).append(u)
    for aid, us in used.items():
        assert len(us) == 1, f"arXiv {aid} matched to several CoRL papers: {us}"
    log(f"matched: {len(match)} ({sum(m['how'].startswith('identical') for m in match.values())} identical titles, "
        f"{sum(m['how'].startswith('read') for m in match.values())} read pairs)")

    got = {}
    if os.path.exists(CACHE):
        for l in open(CACHE):
            r = json.loads(l); got[r["uid"]] = r
    cache = open(CACHE, "a")

    def put(uid, abstract, source):
        if abstract and uid not in got and len(abstract.split()) >= 20:
            r = {"uid": uid, "abstract": abstract, "source": source}
            got[uid] = r; cache.write(json.dumps(r, ensure_ascii=False) + "\n"); cache.flush()

    todo = [u for u in match if u not in got]
    by_aid = {match[u]["arxiv"]: u for u in todo}
    aids = sorted(by_aid)
    for i in range(0, len(aids), 50):
        chunk = aids[i:i + 50]
        q = urllib.parse.urlencode({"filter": "doi:" + "|".join("10.48550/arxiv." + a for a in chunk), "per_page": 50,
                                    "select": "id,doi,title,abstract_inverted_index"})
        page = get("https://api.openalex.org/works?" + q, spacing=1.5)
        for w in (json.loads(page)["results"] if page else []):
            a = (w.get("doi") or "").lower().split("10.48550/arxiv.")[-1]
            if a in by_aid:
                put(by_aid[a], oa_abstract(w), f"arxiv {a} via openalex")
    log("after OpenAlex:", sum(u in got for u in match), "of", len(match))
    for a in aids:
        u = by_aid[a]
        if u in got:
            continue
        page = get(f"https://arxiv.org/abs/{a}", spacing=16)
        m = re.search(r'<blockquote class="abstract mathjax">(.*?)</blockquote>', page or "", flags=re.S)
        put(u, re.sub(r"^Abstract:\s*", "", text(m.group(1))) if m else None, f"arxiv {a} abstract page")
    log("after arXiv abstract pages:", sum(u in got for u in match), "of", len(match))

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["openreview", "year", "title", "arxiv_id", "arxiv_title", "match", "abstract_source"])
        for p in papers:
            m = match.get(p["uid"], {})
            w.writerow([p["uid"], p["year"], p["title"], m.get("arxiv", ""), m.get("arxiv_title", ""), m.get("how", "none"),
                        (got.get(p["uid"]) or {}).get("source", "")])
    n_abs = sum(p["uid"] in got for p in papers)
    log(f"CoRL site papers with an abstract: {n_abs}/{len(papers)} = {100 * n_abs / len(papers):.1f}%")


if __name__ == "__main__":
    main()
