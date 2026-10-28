# How the semantic topic labels were made (2026-10-28)

- Model: Claude Opus 5.5 (claude-opus-5-5), run as agents in a multi-agent workflow, one agent per batch.
- Papers: the 23,204 research articles with an abstract (data/papers.csv, data/topic_matrix_ta_keyword.csv), shuffled and
  split into 186 batches of 125 (the last 79). Each line of a batch: an anonymous id, the title and the abstract, with URLs
  replaced by "(link)". Venue and year were not shown.
- Codebook: data/semantic_codebook_v2.md (59 numbered topics; v2 settles the boundary cases a 500-paper pilot exposed;
  the pilot's materials, results/semantic_pilot_2026-10-28/, are not published because they contain paper texts).
- Repeat: a random 10% (2,320 papers) was shuffled into 20 new batches and labelled again by fresh agents, to measure
  stability. The final labels are those of the first pass.
- Each agent read the codebook first, then its papers in chunks of about 25, and wrote one JSON line per paper. The agents'
  tool calls were checked afterwards: none opened another batch's files, and none used code to match words.
- Blind re-judgement: 1,070 (paper, topic) cells where the keyword rules and the labels disagree (up to 8 per topic and
  direction) or where the two passes disagree (up to 3 per topic) were judged again by 9 agents of the same model, without
  being told which method said "yes". Because it is the same model with the same codebook, this is not an independent check
  (results/semantic_validation.md).

## Labelling prompt (one agent per batch; paths shortened)

```
You label robotics papers by topic, by reading them. Do not use the network. Do not edit any project file.

Inputs:
- Codebook (59 numbered topics, with what counts and what does not, including the [v2] clarifications): <codebook> — read
  it fully first and apply it exactly.
- Papers: <batch>.jsonl (one JSON object per line: pid, title, abstract; URLs were replaced by "(link)").

Task: for EVERY paper, read the title and abstract and decide, by meaning and by the codebook's definitions:
- "involves": the topic numbers the paper's own work involves (several per paper is normal);
- "main": the 1-3 topic numbers that best describe its main contribution (a subset of involves; may be empty only if no
  topic fits).
This must be semantic judgement: do NOT write keyword, regex or embedding scripts to assign topics, and do not open any
file in <labels folder> except your own output. Read in chunks of about 25 papers. Be consistent from the first paper to
the last.

Output: write exactly one JSON object per paper, in input order, to <labels folder>/<batch>.jsonl
like {"pid": "S01234", "involves": [2, 6, 35], "main": [6, 35]} (numbers sorted ascending, all within 1-59). Check at the
end that the file has one valid JSON line per input paper and every pid once. Keep any scratch files only in
<work folder>/<batch>/.
Return done = number of papers written, and problems = a short note (empty string if none).
```

## Re-judgement prompt (one agent per file of about 120 cells; paths shortened)

```
You adjudicate whether robotics papers involve given topics, by reading. No network; do not edit any project file.

Inputs:
- Codebook (59 numbered topics with what counts and what does not, including the [v2] clarifications): <codebook> — read
  it fully first; apply the definition of "involves" exactly (the paper's own work — its method, system, task, platform,
  data or evaluation — involves the topic; background, motivation, contrast, related or future work do not count; judge
  meaning, not words).
- Cases: <cases>.jsonl — each line: cid, topic (number), pid, title, abstract (URLs replaced by "(link)"). The same paper
  may appear in several cases with different topics, or twice with the same topic; judge each case on its own.

For EVERY case decide whether the paper involves that one topic, and why:
- verdict "yes" with reason "explicit" (the work involves it and the abstract uses the topic's usual words) or "implicit"
  (the work involves it, but without the usual words);
- verdict "no" with reason "passing" (named only as background, motivation, contrast, related or future work),
  "other_sense" (a topic word appears in another sense) or "absent" (not part of the paper);
- verdict "unsure" with a short reason.
Do this by reading; do not write keyword, regex or embedding scripts to decide. Do not open any file except your case file
and your own output and scratch files. Read the cases in chunks of about 25 and be consistent from the first case to the
last.

Output: one JSON object per case, in input order, to <out>.jsonl:
{"cid": "F00001", "verdict": "yes", "reason": "implicit", "note": "<=15 words why"}
Check at the end that every cid of your case file appears exactly once and the JSON is valid.
Return done = number of cases written, the yes / no / unsure counts, and problems = a short note (empty string if none).
```
