"""Topic matrices from title + abstract, on papers (2024-2026) that have an abstract.

Three measures, all on the same papers so they compare like with like:
  title    : rule matches the title                                   -> data/topic_matrix_title_sub.csv
  mention  : rule matches the title or the abstract at least once     -> data/topic_matrix_mention.csv
  focus    : rule matches the title, or the abstract at least twice   -> data/topic_matrix_focus.csv
Also writes review samples of papers that match by abstract only (focus but not title), with the matching
sentences: results/precision_abstract_samples/<topic>.txt
"""
import csv
import importlib.util
import json
import os
import random
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = importlib.util.spec_from_file_location("t", os.path.join(ROOT, "scripts", "04_topics.py"))
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)


def main():
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        papers = {r["uid"]: r for r in csv.DictReader(f)}
    abstracts = {r["uid"]: r["abstract"] for r in map(json.loads, open(os.path.join(ROOT, "data", "abstracts.jsonl")))}
    names = [n for n, _, _ in t.COMPILED]
    rows = {"title_sub": [], "mention": [], "focus": []}
    abstract_only = {n: [] for n in names}
    for uid, a in abstracts.items():
        p = papers[uid]
        tt = [int(bool(rx.search(p["title"]))) for _, _, rx in t.COMPILED]
        na = [len(rx.findall(a)) for _, _, rx in t.COMPILED]
        head = [uid, p["venue"], p["year"]]
        rows["title_sub"].append(head + tt)
        rows["mention"].append(head + [int(x or y > 0) for x, y in zip(tt, na)])
        rows["focus"].append(head + [int(x or y >= 2) for x, y in zip(tt, na)])
        for n, x, y in zip(names, tt, na):
            if not x and y >= 2:
                abstract_only[n].append(uid)
    for k, rs in rows.items():
        with open(os.path.join(ROOT, "data", f"topic_matrix_{k}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["uid", "venue", "year"] + names); w.writerows(rs)
    out_dir = os.path.join(ROOT, "results", "precision_abstract_samples"); os.makedirs(out_dir, exist_ok=True)
    rnd = random.Random(int(os.environ.get("SAMPLE_SEED", "0")))
    for (n, fam, rx) in t.COMPILED:
        uids = abstract_only[n]
        safe = re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")
        with open(os.path.join(out_dir, f"{safe}.txt"), "w") as f:
            f.write(f"# {n}: {len(uids)} papers match by abstract (>=2 hits) but not by title\n")
            for uid in rnd.sample(uids, min(10, len(uids))):
                p = papers[uid]; a = abstracts[uid]
                sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", a) if rx.search(s)]
                f.write(f'\n{p["venue"]} {p["year"]} | {p["title"]}\n')
                for s in sents[:3]:
                    f.write("    > " + re.sub(rx, lambda m: "[[" + m.group(0) + "]]", s)[:300] + "\n")
    print(f"{len(abstracts)} papers with abstracts; matrices written for title_sub, mention, focus")


if __name__ == "__main__":
    main()
