# Robotics Topic Atlas

**Page:** https://huyicheng.github.io/robotics-topic-atlas/

What 11,017 papers at ICRA, IROS, RSS, CoRL, T-RO, IJRR and Science Robotics (2024 to October 2026) are about, read from
their titles and abstracts: the share of each of 59 topics per year, how it changed, the same by venue, and a finder that
lists the papers combining any set of topics, each linked to the original.

## What is measured

- **Papers**: accepted papers of ICRA, IROS, RSS and CoRL, and articles of T-RO, IJRR and Science Robotics, 2024–2026,
  that have an abstract (11,017 of 11,135). 2026 so far covers ICRA, RSS and the journals; IROS 2026 and CoRL 2026 were
  not published when the data were collected (2026-10-14).
- **Topics**: each topic is a written rule (`scripts/04_topics.py`). A paper counts for a topic when the rule matches its
  title or its abstract; words that are generic inside abstracts have stricter abstract rules. Random papers matched only
  through the abstract were read for every topic to check the sense of the match (`results/precision_review.md`).
- **Shares**: percentage of papers, standardised to the 2025 venue mix so the years compare; 2026 uses the within-venue
  change at ICRA, RSS and the journals. **Trends**: logistic regression of topic on venue and year, Benjamini–Hochberg
  correction across topics; a topic is called rising or declining only at q < 0.05. Per venue: raw shares with Wilson
  intervals and a likelihood-ratio trend test.
- **Limits**: a share counts papers that name a topic, including in passing; keyword rules miss papers that describe a
  topic in other words; RSS, CoRL, IJRR and Science Robotics are small, so their trends are rarely significant.

Main tables: `results/REPORT.md` (all topics, all venues), `results/scope_trends_ta.csv` and `results/venue_matrix_ta.md`
(by venue), `results/combination_manip_il_vla_flow_gs.md` (co-occurrence of manipulation, imitation learning, VLA/VLM,
diffusion/flow and Gaussian splatting).

## Data sources

| source | used for | licence |
|---|---|---|
| [dblp](https://dblp.org/xml/) XML dump of 2026-10-13 | IROS, T-RO, IJRR, Science Robotics records; venue checks | CC0 |
| [OpenAlex](https://openalex.org) | ICRA records and most abstracts | CC0 |
| [RSS proceedings](https://www.roboticsproceedings.org) | RSS 2024–2026 titles and abstracts | — |
| [PMLR](https://proceedings.mlr.press) v270, v305 | CoRL 2024–2025 titles and abstracts | — |
| [Semantic Scholar](https://www.semanticscholar.org) | abstracts missing elsewhere (mostly ICRA 2026) | API terms |

Abstract texts were used only to assign topics and are **not redistributed** here; `scripts/09_fetch_abstracts.py`
fetches them again from the sources above.

## Layout

| path | content |
|---|---|
| `index.html`, `data.json` | the page (static; `data.json` holds titles, venues, years, links and topic labels) |
| `scripts/` | the pipeline, numbered in run order; `page_template.html` is the page source |
| `results/` | tables and reports; `figures/` the figures |
| `data/` | `papers.csv` (paper table), `topic_matrix_ta.csv` (paper × topic, final measure), `topic_matrix.csv` (title only), `dblp_venues_2022_2026.jsonl` (venue subset of the dblp dump) |

## Reproduce

```
python scripts/01_extract_dblp.py         # dblp dump at ~/.cache/robotics-trends/dblp/dblp.xml.gz
python scripts/02_fetch_extra_venues.py   # RSS, PMLR, OpenAlex
python scripts/03_build_dataset.py
python scripts/04_topics.py
python scripts/09_fetch_abstracts.py      # abstracts (resumable)
python scripts/12_title_abstract.py
python scripts/13_shares_and_change.py
python scripts/14_figures_ta.py
python scripts/15_report.py
python scripts/16_combination_and_supplements.py
python scripts/20_scope_trends.py
python scripts/18_build_site_data.py
python scripts/19_build_site.py
```
Scripts 05–08, 10 and 11 produce the title-only and alternative-measure checks kept in `results/`. To view the page
locally run `python -m http.server` in the repository and open http://127.0.0.1:8000/.
