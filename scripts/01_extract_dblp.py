"""Extract robotics venue papers (years in scripts/config.py) from the dblp XML dump.

Input : ~/.cache/robotics-trends/dblp/dblp.xml.gz (+ dblp.dtd beside it), downloaded from
        https://dblp.org/xml/ (CC0). The search API sits behind an anti-bot page, the dump does not.
Output: data/dblp_venues_<first>_<last>.jsonl  (one record per paper)
Venues are selected by dblp key prefix, which is unambiguous (booktitle strings vary).
"""
import gzip
import json
import os
import sys
from collections import Counter

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # noqa: E402

DUMP = os.path.expanduser("~/.cache/robotics-trends/dblp/dblp.xml.gz")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", config.DBLP_EXTRACT))
YEARS = {str(y) for y in config.YEARS}
VENUES = {  # dblp key prefix -> short name
    "conf/icra/": "ICRA", "conf/iros/": "IROS", "conf/rss/": "RSS", "conf/corl/": "CoRL",
    "journals/trob/": "T-RO", "journals/ijrr/": "IJRR", "journals/scirobotics/": "SciRobotics",
    # candidates outside the default set, extracted so scope can change without re-parsing
    "journals/ral/": "RA-L", "conf/hri/": "HRI", "conf/humanoids/": "Humanoids",
}


def text(el):
    return "".join(el.itertext()).strip() if el is not None else None


def main():
    os.chdir(os.path.dirname(DUMP))  # dblp.xml references dblp.dtd relatively
    counts = Counter()
    n_seen = 0
    with open(OUT, "w") as out:
        for _, el in etree.iterparse(gzip.open(DUMP), events=("end",), tag=("inproceedings", "article"),
                                     load_dtd=True, resolve_entities=True, huge_tree=True):
            n_seen += 1
            key = el.get("key", "")
            venue = next((v for p, v in VENUES.items() if key.startswith(p)), None)
            year = text(el.find("year"))
            if venue and year in YEARS:
                rec = {
                    "key": key, "venue": venue, "type": el.tag, "year": int(year),
                    "title": text(el.find("title")),
                    "booktitle": text(el.find("booktitle")), "journal": text(el.find("journal")),
                    "volume": text(el.find("volume")), "number": text(el.find("number")),
                    "pages": text(el.find("pages")), "crossref": text(el.find("crossref")),
                    "ee": [text(e) for e in el.findall("ee")],
                    "publtype": el.get("publtype"),
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                counts[(venue, int(year))] += 1
            el.clear()
            while el.getprevious() is not None:  # free already-processed siblings
                del el.getparent()[0]
    print(f"records scanned: {n_seen}", file=sys.stderr)
    venues = sorted({v for v, _ in counts})
    print("venue        " + " ".join(f"{y:>6d}" for y in sorted(int(y) for y in YEARS)))
    for v in venues:
        print(f"{v:12s} " + " ".join(f"{counts[(v, int(y))]:>6d}" for y in sorted(YEARS)))


if __name__ == "__main__":
    main()
