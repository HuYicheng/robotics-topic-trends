"""Collect the semantic topic labels (2026-10-28) into one table keyed by paper.

The labels were made by Claude Opus 5.5 agents, each reading a batch of about 125 papers (title and abstract, URLs replaced
by "(link)") against the codebook data/semantic_codebook_v2.md, with the prompt in data/semantic_labelling_prompt.md; no
keyword or embedding scripts assigned topics. Raw files (kept locally): data/semantic_labels_v2/b001-b186.jsonl, one line
per paper {"pid", "involves", "main"}, and ids.csv (pid -> uid). r01-r20.jsonl hold a random 10% labelled a second time in
other batches; they are used only to measure stability (scripts/12c_semantic_validation.py).

Output: data/semantic_labels.csv  uid, involves, main (topic numbers of the codebook joined by ";"; topic k = the k-th
        non-"[term]" topic column of the matrices)
"""
import csv
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.join(ROOT, "data", "semantic_labels_v2")


def main():
    ids = {r["pid"]: r["uid"] for r in csv.DictReader(open(os.path.join(RAW, "ids.csv")))}
    rows, seen = [], set()
    for fn in sorted(glob.glob(os.path.join(RAW, "b*.jsonl"))):
        for line in open(fn):
            if not line.strip():
                continue
            r = json.loads(line)
            inv, mn = sorted(set(r["involves"])), sorted(set(r["main"]))
            assert r["pid"] in ids and r["pid"] not in seen, r["pid"]
            assert all(1 <= k <= 59 for k in inv + mn) and set(mn) <= set(inv) and len(mn) <= 3, r
            seen.add(r["pid"])
            rows.append((ids[r["pid"]], ";".join(map(str, inv)), ";".join(map(str, mn))))
    assert len(seen) == len(ids), (len(seen), len(ids))
    rows.sort()
    with open(os.path.join(ROOT, "data", "semantic_labels.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["uid", "involves", "main"]); w.writerows(rows)
    print(f"{len(rows)} papers -> data/semantic_labels.csv")


if __name__ == "__main__":
    main()
