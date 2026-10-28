"""Checks of the semantic labels (2026-10-28): stability, comparison with the keyword rules, blind re-judgement of the
disagreements, and what changes in the trends. Needs the raw label and re-judgement files, which are kept locally
(data/semantic_labels_v2/, with paper texts in adjudication/cases/); run after 13 on the three matrices
(results/shares_and_change_ta.csv, _keyword.csv, _main.csv) and after 20/20b, whose per-venue tables it compares with
the keyword-rule ones archived at the switch. Ported from the checking tools of the comparison (audited
2026-10-28; same numbers).

Re-judgement scoring: cells where keyword rules and labels agree are taken as right (cells both get wrong are invisible
here, see "cells both miss"); a disagreement cell counts as true with the yes-rate of its (direction, topic) stratum in
the re-judgement ("unsure" = 0.5); strata are weighted by their size.
Output: results/semantic_validation.md, results/semantic_vs_keyword_by_topic.csv, results/semantic_stability.csv,
        results/semantic_score_by_topic.csv
"""
import collections
import csv
import glob
import json
import os
import statistics as st

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.join(ROOT, "data", "semantic_labels_v2")
ADJ = os.path.join(RAW, "adjudication")
ARCHIVE_KW = os.path.join(ROOT, "archive", "2020-2026_keyword_round3_pushed", "results")   # keyword results at the switch


def load(pat):
    out = {}
    for fn in sorted(glob.glob(os.path.join(RAW, pat))):
        for line in open(fn):
            if line.strip():
                r = json.loads(line); out[r["pid"]] = r
    return out


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    ids = {r["pid"]: r for r in csv.DictReader(open(os.path.join(RAW, "ids.csv")))}
    kw = {r["uid"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data", "topic_matrix_ta_keyword.csv")))}
    names = [c for c in next(csv.reader(open(os.path.join(ROOT, "data", "topic_matrix_ta_keyword.csv"))))[3:] if not c.startswith("[term]")]
    M, R = load("b*.jsonl"), load("r*.jsonl")
    pids = [p for p in ids if p in M]
    assert len(pids) == len(ids) == len(kw)
    per = lambda y: "2020-22" if y <= 2022 else "2023-24" if y <= 2024 else "2025-26"   # noqa: E731
    out = []

    # stability (repeat pass)
    rp = [p for p in R if p in M]
    stab = []
    for k, n in enumerate(names, 1):
        a = [int(k in M[p]["involves"]) for p in rp]; b = [int(k in R[p]["involves"]) for p in rp]
        stab.append({"topic": n, "first_pass": sum(a), "second_pass": sum(b), "kappa": round(kappa(a, b), 4)})
    pd.DataFrame(stab).to_csv(os.path.join(ROOT, "results", "semantic_stability.csv"), index=False)
    ks = [r["kappa"] for r in stab]
    same = sum(set(R[p]["involves"]) == set(M[p]["involves"]) for p in rp) / len(rp)

    # keyword vs semantic
    rows, dis = [], collections.defaultdict(list)
    for k, n in enumerate(names, 1):
        x = [int(kw[ids[p]["uid"]][n]) for p in pids]; y = [int(k in M[p]["involves"]) for p in pids]
        for p, a, b in zip(pids, x, y):
            if a != b: dis[("kw_only" if a else "sem_only", k)].append(p)
        rows.append({"topic": n, "keyword": sum(x), "semantic": sum(y), "semantic_main": sum(int(k in M[p]["main"]) for p in pids),
                     "both": sum(a & b for a, b in zip(x, y)), "keyword_only": sum(a & (1 - b) for a, b in zip(x, y)),
                     "semantic_only": sum(b & (1 - a) for a, b in zip(x, y)), "kappa": round(kappa(x, y), 4)})
    C = pd.DataFrame(rows); C.to_csv(os.path.join(ROOT, "results", "semantic_vs_keyword_by_topic.csv"), index=False)
    lp = collections.defaultdict(lambda: [0, 0, 0])
    for p in pids:
        v = lp[ids[p]["year"]]; v[0] += len(M[p]["involves"]); v[1] += len(M[p]["main"]); v[2] += 1

    # re-judgement
    key = json.load(open(os.path.join(ADJ, "cases_key.json")))
    adj = {}
    for fn in glob.glob(os.path.join(ADJ, "cases", "out_c*.jsonl")):
        for line in open(fn):
            if line.strip():
                r = json.loads(line); adj[r["cid"]] = r
    assert set(adj) == set(key), "re-judgement incomplete"
    val = lambda v: 1.0 if v == "yes" else 0.5 if v == "unsure" else 0.0   # noqa: E731
    drawn = collections.Counter((k["type"], k["topic"]) for k in key.values())
    rate, reasons, period = collections.defaultdict(list), collections.defaultdict(collections.Counter), collections.defaultdict(lambda: [0.0, 0.0])
    for cid, k in key.items():
        v = adj[cid]["verdict"]; w = k["n_stratum"] / drawn[(k["type"], k["topic"])]
        rate[(k["type"], k["topic"])].append(val(v))
        reasons[k["type"]]["unsure" if v == "unsure" else f"{v}/{adj[cid].get('reason')}"] += w
        pp = period[(k["type"], per(int(ids[k["pid"]]["year"])))]; pp[0] += w * val(v); pp[1] += w
    rate = {s: sum(v) / len(v) for s, v in rate.items()}
    acc = {m: collections.Counter() for m in ("keyword", "semantic")}
    per_topic = collections.defaultdict(lambda: {m: collections.Counter() for m in acc})
    for k, n in enumerate(names, 1):
        for p in pids:
            a = int(kw[ids[p]["uid"]][n]); b = int(k in M[p]["involves"])
            t = a if a == b else rate[("kw_only" if a else "sem_only", k)]
            for m, pred in (("keyword", a), ("semantic", b)):
                for c in (acc[m], per_topic[n][m]):
                    c["tp"] += pred * t; c["fp"] += pred * (1 - t); c["fn"] += (1 - pred) * t
    pr = lambda c: (c["tp"] / (c["tp"] + c["fp"]), c["tp"] / (c["tp"] + c["fn"]))   # noqa: E731
    P = pd.DataFrame([{"topic": n, "keyword_precision": round(pr(d["keyword"])[0], 3), "keyword_recall": round(pr(d["keyword"])[1], 3),
                       "semantic_precision": round(pr(d["semantic"])[0], 3), "semantic_recall": round(pr(d["semantic"])[1], 3),
                       "cases_per_direction": drawn.get(("kw_only", k), 0), "true_members_est": round(d["keyword"]["tp"] + d["keyword"]["fn"])}
                      for k, (n, d) in enumerate(((n, per_topic[n]) for n in names), 1)])
    P.to_csv(os.path.join(ROOT, "results", "semantic_score_by_topic.csv"), index=False)
    # cells both miss, seen through the repeat pass (keyword no, first pass no, second pass yes)
    cells = {(p, k) for p in rp for k, n in enumerate(names, 1)
             if kw[ids[p]["uid"]][n] == "0" and k not in M[p]["involves"] and k in R[p]["involves"]}
    seen = [adj[c]["verdict"] for c, k in key.items() if k["type"] == "pass_split" and (k["pid"], k["topic"]) in cells]
    miss = len(cells) * len(pids) / len(rp) * (sum(map(val, seen)) / len(seen))
    (kp, kr), (sp, sr) = pr(acc["keyword"]), pr(acc["semantic"])
    both, so, sem = int(C.both.sum()), int(C.semantic_only.sum()), int(C.semantic.sum())

    # trends
    T = {m: pd.read_csv(os.path.join(ROOT, "results", f)).set_index("topic") for m, f in
         (("semantic", "shares_and_change_ta.csv"), ("keyword", "shares_and_change_ta_keyword.csv"), ("main", "shares_and_change_ta_main.csv"))}
    def changes(a, b, col):
        x, y = T[a][col], T[b][col].reindex(T[a].index)
        flips = [t for t in x.index if {x[t], y[t]} == {"rising", "declining"}]
        return int((x != y).sum()), flips, [t for t in x.index if x[t] != y[t]]
    venue = {}
    if os.path.isdir(ARCHIVE_KW):
        for f in ("scope_trends_ta.csv", "scope_trends_subsets_ta.csv"):
            K = pd.read_csv(os.path.join(ARCHIVE_KW, f)); S = pd.read_csv(os.path.join(ROOT, "results", f))
            G = K.merge(S, on=["scope", "topic"], suffixes=("_kw", "_sem"))
            venue[f] = (len(G), int((G.call_kw != G.call_sem).sum()),
                        [f"{r.scope}: {r.topic}" for _, r in G[((G.call_kw == "rising") & (G.call_sem == "declining")) | ((G.call_kw == "declining") & (G.call_sem == "rising"))].iterrows()])

    tot_kw, tot_sem = int(C.keyword.sum()), int(C.semantic.sum())
    out += ["# Semantic topic labels: checks (2026-10-28)", "",
            "Generated by scripts/13b_semantic_validation.py. How the labels were made: data/semantic_labelling_prompt.md;",
            "topic definitions: data/semantic_codebook_v2.md; labels: data/semantic_labels.csv.", "",
            "## Stability", "",
            f"A random {len(rp):,} papers were labelled a second time, in other batches by other agents. Agreement per topic",
            f"(Cohen's kappa) has median {st.median(ks):.2f} and minimum {min(ks):.2f}; {100 * same:.0f}% of these papers got exactly",
            "the same topics both times. This shows that the model is consistent with itself, not that it is right.", "",
            "## Labels compared with the keyword rules", "",
            f"Keyword rules (data/topic_matrix_ta_keyword.csv): {tot_kw:,} paper-topic labels; semantic labels: {tot_sem:,}; both: {both:,};",
            f"keyword only: {tot_kw - both:,}; semantic only: {so:,}. Per topic: results/semantic_vs_keyword_by_topic.csv.",
            "Topics per paper (semantic, involves / main): " + ", ".join(f"{y} {v[0] / v[2]:.2f} / {v[1] / v[2]:.2f}" for y, v in sorted(lp.items())) + ".", "",
            "## Blind re-judgement of the disagreements", "",
            f"{len(key):,} cells were judged again without saying which method said \"yes\": up to 8 per topic for each direction of",
            "disagreement, and up to 3 per topic where the two semantic passes disagree. Share of each verdict (weighted by stratum size):", "",
            "| cells | involves, words used | involves, other words | passing mention | other sense of the word | absent | unsure |",
            "|---|---|---|---|---|---|---|"]
    for t, lab in (("kw_only", "keyword only"), ("sem_only", "semantic only"), ("pass_split", "the two passes differ")):
        c = reasons[t]; s = sum(c.values())
        out.append(f"| {lab} | " + " | ".join(f"{100 * c[x] / s:.0f}%" for x in ("yes/explicit", "yes/implicit", "no/passing", "no/other_sense", "no/absent", "unsure")) + " |")
    out += ["",
            f"Scored against this re-judgement, the keyword rules have precision {kp:.2f} and recall {kr:.2f}; the semantic labels {sp:.2f} and {sr:.2f}",
            "(per topic: results/semantic_score_by_topic.csv; 8 cases per stratum, so a single topic's numbers are rough: 8 of 8",
            "right still has a 95% lower bound of about 0.63).", "",
            "**What this does not show.** The re-judgement was made by the same model (Claude Opus 5.5) with the same codebook, and",
            "it behaves much like labelling again: the semantic numbers measure the model's agreement with itself, not an",
            "independent error rate. No human check has been made. Two more limits:",
            f"- Cells both methods miss are invisible here. The repeat pass shows some ({len(cells)} cells where the keyword rules and the",
            f"  first pass say no and the second pass says yes; {100 * sum(map(val, seen)) / len(seen):.0f}% of the {len(seen)} re-judged ones are yes): about {miss:,.0f} such",
            f"  cells in all papers, which caps recall at about {acc['semantic']['tp'] / (acc['semantic']['tp'] + acc['semantic']['fn'] + miss):.2f} (semantic) and {acc['keyword']['tp'] / (acc['keyword']['tp'] + acc['keyword']['fn'] + miss):.2f} (keyword).",
            "- If the semantic-only cells were right less often than the re-judgement says, the semantic precision would still be",
            "  " + ", ".join(f"{(both + r * so) / sem:.2f} at {int(100 * r)}%" for r in (0.9, 0.8, 0.7)) + f" (keyword rules: {kp:.2f}).", "",
            "Yes-rate of the re-judged cells by period (weighted): " + "; ".join(
                f"{lab} " + " / ".join(f"{period[(t, q)][0] / period[(t, q)][1]:.2f}" for q in ("2020-22", "2023-24", "2025-26"))
                for t, lab in (("kw_only", "keyword only"), ("sem_only", "semantic only"))) + " (2020-22 / 2023-24 / 2025-26).",
            "With 0-6 cases per topic and period, this cannot show whether a single topic's errors change over the years.", "",
            "## What changes in the trends", ""]
    n1, f1, c1 = changes("keyword", "semantic", "call"); n2, f2, c2 = changes("keyword", "semantic", "recent_call")
    n3, f3, _ = changes("keyword", "main", "call"); n4, f4, _ = changes("keyword", "main", "recent_call")
    out += [f"All venues together: {n1} of 59 whole-period calls and {n2} of the 2024-2026 calls differ between the keyword rules and",
            f"the semantic labels ({len(f1) + len(f2)} from rising to declining or back). Whole period: " + "; ".join(
                f"{t} ({T['keyword'].loc[t, 'call']} -> {T['semantic'].loc[t, 'call']})" for t in c1) + ".",
            f"2024-2026: " + "; ".join(f"{t} ({T['keyword'].loc[t, 'recent_call']} -> {T['semantic'].loc[t, 'recent_call']})" for t in c2) + ".",
            f"With the \"main\" labels (results/shares_and_change_ta_main.csv) {n3} and {n4} calls differ from the keyword rules"
            + (f", flips: {', '.join(f3 + f4)}." if f3 + f4 else ".")]
    for f, lab in (("scope_trends_ta.csv", "each venue and the conference / journal groups"), ("scope_trends_subsets_ta.csv", "the other venue combinations")):
        if f in venue:
            n, c, fl = venue[f]
            out.append(f"By {lab}: {c} of {n} whole-period calls differ ({100 * c / n:.0f}%)" + (f"; flips: {'; '.join(fl)}." if fl else ", no flips."))
    out += ["Which version is right where they differ has no independent evidence here; several changes are q values crossing 0.05.", ""]
    open(os.path.join(ROOT, "results", "semantic_validation.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
