"""CoRL years whose PMLR volume is not out yet: the accepted-papers list on the conference site (config.CORL_SITE).

CoRL 2026 (added 2026-10-28; the site posted the list on 10/19): www.corl.org/program/accepted-papers. The list sits in a
Google Sites custom embed (the data-code attribute of the page): 687 accepted papers, each in one of three poster
sessions with its OpenReview forum link; orals and spotlights are listed again in their talk sessions.
Check of the source on a year both cover: the CoRL 2025 site (2025.corl.org/program/main-conference) against PMLR v305
(data/extra_venues.jsonl): same number of papers, titles compared after compacting (letters and digits only).
The raw pages are kept in data/raw/corl/ (the fetch date is in the file name); a rerun parses the saved pages unless
--refresh. No personal data in requests.
Output: data/extra_corl_site.jsonl  (venue, year, title, source, id = OpenReview forum URL, poster, talk)
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.join(ROOT, "data", "raw", "corl")
OUT = os.path.join(ROOT, "data", "extra_corl_site.jsonl")
UA = {"User-Agent": "robotics-trends-study/0.1 (research script)"}
CHECK_2025 = "https://2025.corl.org/program/main-conference"


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def compact(t):
    return re.sub(r"[^a-z0-9]+", "", html.unescape(t or "").lower())


def page(url, stem):
    """Newest saved copy of url in data/raw/corl/<stem>_<date>.html, fetched first if none (or with --refresh)."""
    os.makedirs(RAW, exist_ok=True)
    saved = sorted(f for f in os.listdir(RAW) if f.startswith(stem + "_") and f.endswith(".html"))
    if saved and "--refresh" not in sys.argv:
        fn = os.path.join(RAW, saved[-1])
    else:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            body = r.read()
        fn = os.path.join(RAW, f"{stem}_{time.strftime('%Y-%m-%d')}.html")
        open(fn, "wb").write(body)
        time.sleep(3)
    print("page:", os.path.relpath(fn, ROOT))
    return open(fn, encoding="utf-8", errors="replace").read()


def parse_embed(text, year):
    code = html.unescape(re.search(r'data-code="([^"]*)"', text).group(1))
    print("  list header:", clean(re.search(r'<p class="sub">(.*?)</p>', code, flags=re.S).group(1)))
    recs = {}
    for sec in re.finditer(r'<section class="session poster" id="post-p(\d)">(.*?)</section>', code, flags=re.S):
        for row in re.finditer(r'<tr class="paper"><td class="num">(\d+)</td><td><a href="(https://openreview\.net/forum\?id=[^"]+)"'
                               r'[^>]*>(.*?)</a></td>', sec.group(2), flags=re.S):
            num, url, title = row.groups()
            assert url not in recs, url
            recs[url] = {"venue": "CoRL", "year": year, "title": clean(title), "source": f"corl.org/{year}", "id": url,
                         "poster": f"P{sec.group(1)}-{num}", "talk": []}
    n_talk = 0
    for sec in re.finditer(r'<section class="session" data-sess="([OS]\d+)">(.*?)</section>', code, flags=re.S):
        for li in re.finditer(r'<li class="paper"><a href="(https://openreview\.net/forum\?id=[^"]+)"', sec.group(2)):
            recs[li.group(1)]["talk"].append(sec.group(1)); n_talk += 1   # KeyError if a talk has no poster
    print(f"  {year}: {len(recs)} papers in the poster sessions; {n_talk} talk entries, all among them")
    return list(recs.values())


def check_2025():
    text = page(CHECK_2025, "corl2025_main_conference")
    site = {}
    for m in re.finditer(r'<a [^>]*href="https://openreview\.net/forum\?id=([A-Za-z0-9_-]+)"[^>]*>(.*?)</a>', text, flags=re.S):
        site.setdefault(m.group(1), clean(m.group(2)))
    pmlr = [r for r in map(json.loads, open(os.path.join(ROOT, "data", "extra_venues.jsonl")))
            if r["venue"] == "CoRL" and r["year"] == 2025]
    S, P = {compact(t): t for t in site.values()}, {compact(r["title"]): r["title"] for r in pmlr}
    print(f"  check 2025: site {len(site)} papers, PMLR v305 {len(pmlr)}; identical compact titles {len(set(S) & set(P))}")
    for k in sorted(set(P) - set(S)):
        print("    PMLR only:", P[k])
    for k in sorted(set(S) - set(P)):
        print("    site only:", S[k])


def main():
    recs = []
    for year, url in sorted(config.CORL_SITE.items()):
        recs += parse_embed(page(url, f"corl{year}_accepted_papers"), year)
    check_2025()
    with open(OUT, "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", len(recs), "records to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
