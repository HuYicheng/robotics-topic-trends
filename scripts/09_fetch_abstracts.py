"""Collect abstracts for every 2024-2026 paper in data/papers.csv (seven venues). Resumable (cache file).

Order of sources per paper (first non-empty wins; the source is recorded):
  ICRA      : OpenAlex record already fetched (data/extra_venues.jsonl)
  IROS, T-RO, IJRR, SciRobotics : OpenAlex by DOI (batches of 50)
  RSS       : roboticsproceedings.org paper page ("Abstract:")
  CoRL      : PMLR bibliography.bib of the volume
  fallbacks for papers with a DOI: Crossref works API, then Semantic Scholar batch (DOI ids)
  ICRA still missing: OpenAlex title search for another version of the same paper (e.g. the arXiv preprint),
                      accepted only if the normalised title is identical.
No personal data in requests. Output: data/abstracts.jsonl ; cache: data/abstracts_cache.jsonl
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UA = {"User-Agent": "robotics-trends-study/0.1 (research script)"}
CACHE = os.path.join(ROOT, "data", "abstracts_cache.jsonl")
VENUES = {"ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def get(url, data=None, headers=None, tries=5, base_sleep=20, timeout=60):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            log(f"  HTTP {e.code} on {url[:90]} (attempt {i + 1}/{tries})")
            if e.code == 401:
                return None
        except Exception as e:  # noqa: BLE001
            log(f"  {type(e).__name__} on {url[:90]} (attempt {i + 1}/{tries})")
        time.sleep(base_sleep * 2 ** i)
    return None


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def oa_abstract(w):
    inv = w.get("abstract_inverted_index") or {}
    words = sorted((p, word) for word, ps in inv.items() for p in ps)
    return " ".join(word for _, word in words) or None


def main():
    import csv
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        papers = [r for r in csv.DictReader(f) if r["venue"] in VENUES and 2024 <= int(r["year"]) <= 2026]
    dblp = {r["key"]: r for r in map(json.loads, open(os.path.join(ROOT, "data", "dblp_venues_2022_2026.jsonl")))}
    extra = {r.get("id"): r for r in map(json.loads, open(os.path.join(ROOT, "data", "extra_venues.jsonl")))}
    got = {}
    if os.path.exists(CACHE):
        for l in open(CACHE):
            r = json.loads(l); got[r["uid"]] = r
    cache = open(CACHE, "a")

    def put(uid, abstract, source):
        if abstract and uid not in got and len(abstract.split()) >= 20:
            r = {"uid": uid, "abstract": abstract, "source": source}
            got[uid] = r; cache.write(json.dumps(r, ensure_ascii=False) + "\n"); cache.flush()

    doi_of = {}
    for p in papers:
        if p["source"] == "dblp":
            d = next((e.split("doi.org/")[1] for e in dblp[p["uid"]]["ee"] if "doi.org/10." in e), None)
        else:
            d = ((extra.get(p["uid"]) or {}).get("doi") or "").replace("https://doi.org/", "") or None
        if d:
            doi_of[p["uid"]] = d.lower()

    # 1. ICRA from the OpenAlex records already on disk
    for p in papers:
        if p["venue"] == "ICRA":
            put(p["uid"], (extra.get(p["uid"]) or {}).get("abstract"), "openalex")
    log("after ICRA records:", len(got))

    # 2. OpenAlex by DOI for dblp-sourced papers
    todo = [p for p in papers if p["source"] == "dblp" and p["uid"] not in got and p["uid"] in doi_of]
    by_doi = {doi_of[p["uid"]]: p["uid"] for p in todo}
    dois = list(by_doi)
    for i in range(0, len(dois), 50):
        chunk = dois[i:i + 50]
        q = urllib.parse.urlencode({"filter": "doi:" + "|".join(chunk), "per_page": 50,
                                    "select": "id,doi,title,abstract_inverted_index"})
        txt = get("https://api.openalex.org/works?" + q)
        if txt:
            for w in json.loads(txt)["results"]:
                d = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                if d in by_doi:
                    put(by_doi[d], oa_abstract(w), "openalex")
        time.sleep(1.5)
    log("after OpenAlex DOI batches:", len(got))

    # 3. RSS pages
    for p in papers:
        if p["venue"] == "RSS" and p["uid"] not in got:
            vol, pid = p["uid"].split("/")
            page = get(f"https://www.roboticsproceedings.org/{vol}/{pid}.html")
            if page:
                m = re.search(r"Abstract:(.*?)(?:<h\d|<div|Bib[Tt]e[Xx]|Download|<hr)", page, flags=re.S)
                put(p["uid"], strip_tags(m.group(1)) if m else None, "roboticsproceedings")
            time.sleep(1.2)
    log("after RSS pages:", len(got))

    # 4. CoRL from PMLR bib files
    for vol in ("v270", "v305"):
        bib = get(f"https://proceedings.mlr.press/{vol}/assets/bib/bibliography.bib") or ""
        for entry in re.split(r"\n@", bib):
            url = re.search(r"url\s*=\s*\{(https://proceedings\.mlr\.press/[^}]+)\}", entry)
            i = entry.find("abstract")
            if not url or i < 0:
                continue
            j = entry.find("{", i); depth, k = 0, j
            while k < len(entry):
                depth += entry[k] == "{"; depth -= entry[k] == "}"
                if depth == 0:
                    break
                k += 1
            put(url.group(1), strip_tags(entry[j + 1:k]).replace("{", "").replace("}", ""), "pmlr-bib")
        time.sleep(2)
    log("after PMLR:", len(got))

    # 5. Crossref for anything with a DOI still missing
    for p in papers:
        if p["uid"] not in got and p["uid"] in doi_of:
            txt = get("https://api.crossref.org/works/" + urllib.parse.quote(doi_of[p["uid"]]), tries=3, base_sleep=5)
            if txt:
                put(p["uid"], strip_tags(json.loads(txt)["message"].get("abstract")), "crossref")
            time.sleep(0.4)
    log("after Crossref:", len(got))

    # 6. Semantic Scholar batch (DOI ids), with backoff on 429
    miss = [p for p in papers if p["uid"] not in got and p["uid"] in doi_of]
    for i in range(0, len(miss), 400):
        chunk = miss[i:i + 400]
        body = json.dumps({"ids": ["DOI:" + doi_of[p["uid"]] for p in chunk]}).encode()
        txt = get("https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,abstract", data=body,
                  headers={"Content-Type": "application/json"}, tries=6, base_sleep=30)
        if txt:
            for p, r in zip(chunk, json.loads(txt)):
                if r and norm(r.get("title")) == norm(p["title"]):
                    put(p["uid"], r.get("abstract"), "semanticscholar")
        time.sleep(5)
    log("after Semantic Scholar:", len(got))

    # 7. ICRA still missing: OpenAlex title search for another version (identical normalised title)
    miss = [p for p in papers if p["venue"] == "ICRA" and p["uid"] not in got]
    log("ICRA still missing before title search:", len(miss))
    for p in miss:
        q = urllib.parse.urlencode({"filter": "title.search:" + re.sub(r"[,:|]", " ", p["title"])[:200], "per_page": 10,
                                    "select": "id,title,abstract_inverted_index"})
        txt = get("https://api.openalex.org/works?" + q, tries=3, base_sleep=10)
        if txt:
            for w in json.loads(txt)["results"]:
                if norm(w.get("title")) == norm(p["title"]) and w.get("abstract_inverted_index"):
                    put(p["uid"], oa_abstract(w), "openalex-other-version"); break
        time.sleep(1.2)
    log("after title search:", len(got))

    with open(os.path.join(ROOT, "data", "abstracts.jsonl"), "w") as f:
        for p in papers:
            if p["uid"] in got:
                f.write(json.dumps({**got[p["uid"]], "venue": p["venue"], "year": int(p["year"])}, ensure_ascii=False) + "\n")
    from collections import Counter
    n = Counter((p["venue"], int(p["year"])) for p in papers)
    h = Counter((p["venue"], int(p["year"])) for p in papers if p["uid"] in got)
    log("coverage:")
    for k in sorted(n):
        log(f"  {k[0]:12s} {k[1]}: {h[k]}/{n[k]} = {100 * h[k] / n[k]:.1f}%")


if __name__ == "__main__":
    sys.exit(main())
