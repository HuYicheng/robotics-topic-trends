"""Fetch titles for venue-years that dblp does not index yet (as of the 2026-10-13 dump).

- RSS 2025/2026  : roboticsproceedings.org index pages (rss21, rss22); rss20 (2024) fetched as a check vs dblp.
- CoRL 2025      : PMLR v305 index; v270 (CoRL 2024) fetched as a check vs dblp.
- ICRA 2026      : OpenAlex source S4210217939 (ICRA proceedings), publication_year 2026;
                   2024/2025 fetched as a check vs dblp.
Output: data/extra_venues.jsonl  (venue, year, title, source, id)
Requests carry no personal data (no email); one request at a time with pauses.
"""
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "robotics-trends-study/0.1 (research script)"}
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "extra_venues.jsonl"))


def get(url, timeout=60, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            body = e.read()[:300] if isinstance(e, urllib.error.HTTPError) else b""
            print(f"  request failed ({e}); {body!r}; attempt {i + 1}/{tries}", flush=True)
            if i == tries - 1:
                raise
            time.sleep(30 * 2 ** i)  # OpenAlex answers bursts with 401/429; back off 30 s .. 4 min


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def rss(vol, year):
    page = get(f"https://www.roboticsproceedings.org/{vol}/index.html")
    recs = {}
    # each paper: <a href="p001.html">Title</a> (titles may contain tags)
    for m in re.finditer(r'<a href="(p\d{3})\.html">(.*?)</a>', page, flags=re.S):
        pid, title = m.group(1), clean(m.group(2))
        if title and pid not in recs:
            recs[pid] = {"venue": "RSS", "year": year, "title": title, "source": f"roboticsproceedings/{vol}", "id": f"{vol}/{pid}"}
    return list(recs.values())


def pmlr(vol, year):
    page = get(f"https://proceedings.mlr.press/{vol}/")
    recs = []
    # each paper: <div class="paper"><p class="title">Title</p> ... <a href="https://proceedings.mlr.press/vNNN/xxx.html">abs</a>
    for m in re.finditer(r'<div class="paper">(.*?)</div>', page, flags=re.S):
        block = m.group(1)
        t = re.search(r'<p class="title">(.*?)</p>', block, flags=re.S)
        a = re.search(r'href="(https://proceedings\.mlr\.press/' + vol + r'/[^"]+\.html)"', block)
        if t:
            recs.append({"venue": "CoRL", "year": year, "title": clean(t.group(1)), "source": f"pmlr/{vol}", "id": a.group(1) if a else None})
    return recs


def openalex_icra(year):
    # Numbered paging (page=1..N, <=10k results): cursor paging past page 1 needs an API key since 2026.
    recs, page, total = [], 1, None
    while total is None or (page - 1) * 200 < total:
        q = urllib.parse.urlencode({"filter": f"primary_location.source.id:S4210217939,publication_year:{year}",
                                    "per_page": 200, "page": page, "select": "id,doi,title,type,abstract_inverted_index"})
        d = json.loads(get("https://api.openalex.org/works?" + q))
        total = d["meta"]["count"]
        for w in d["results"]:
            inv = w.get("abstract_inverted_index") or {}
            words = sorted((pos, word) for word, poss in inv.items() for pos in poss)
            recs.append({"venue": "ICRA", "year": year, "title": w.get("title"), "source": "openalex/S4210217939",
                         "id": w["id"], "doi": w.get("doi"), "oa_type": w.get("type"),
                         "abstract": " ".join(word for _, word in words) or None})
        page += 1
        time.sleep(3)
    assert len({r["id"] for r in recs}) == total, (len(recs), total)
    return recs


def main():
    all_recs = []
    for vol, year in (("rss20", 2024), ("rss21", 2025), ("rss22", 2026)):
        r = rss(vol, year); print(f"RSS {year} ({vol}): {len(r)}"); all_recs += r; time.sleep(3)
    for vol, year in (("v270", 2024), ("v305", 2025)):
        r = pmlr(vol, year); print(f"CoRL {year} ({vol}): {len(r)}"); all_recs += r; time.sleep(3)
    for year in (2024, 2025, 2026):
        r = openalex_icra(year); print(f"ICRA {year} (OpenAlex): {len(r)}"); all_recs += r
    with open(OUT, "w") as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", len(all_recs), "records to", OUT)


if __name__ == "__main__":
    main()
