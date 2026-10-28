# Robotics Topic Trends

**Page:** https://huyicheng.github.io/robotics-topic-trends/

**Submission deadlines** of the seven venues, one year from 20 October 2026, with official links: https://huyicheng.github.io/robotics-topic-trends/deadlines.html

What 23,204 research articles at ICRA, IROS, RSS, CoRL, T-RO, IJRR and Science Robotics (2020 to October 2026) are
about, read from their titles and abstracts: the share and the number of papers of each of 59 topics per year, how they
changed, the same for any combination of venues, one small chart per topic, and a topic word cloud that lists the papers combining any set of
topics, each linked to the original.

## What is measured

- **Papers**: research articles only. Accepted papers of ICRA, IROS, RSS and CoRL; research articles of T-RO, IJRR and
  Science Robotics. Editorials, commentaries, Focus / highlight / viewpoint pieces, errata, special-issue introductions
  and reviews or surveys are removed (`scripts/03b_research_articles.py`; Science Robotics article types from PubMed;
  the list of removed items is `results/removed_nonresearch.txt`). 23,323 research articles, 23,204 with an abstract.
  2026 so far covers ICRA, RSS, CoRL and the journals up to mid-October; IROS 2026 is not published yet (data of
  2026-10-14, CoRL 2026 added 2026-10-28).
- **CoRL 2026**: its PMLR volume is not out yet, so the papers are the accepted-papers list of the conference site (687;
  the 2025 site list matches PMLR v305 paper for paper: 263 = 263). OpenReview holds all abstracts but turns away
  automated access, so the abstracts are those of the papers' arXiv versions, found for 575 (532 by an identical title,
  43 by reading title pairs that differ slightly, `data/corl_site_manual_matches.csv`); the other 112 have no public
  version yet and, like every paper without an abstract, are not counted. The page marks CoRL 2026 as incomplete.
- **Topics**: each topic is a written rule (`scripts/04_topics.py`). A paper counts for a topic when the rule matches its
  title or its abstract; words that are generic inside abstracts have stricter abstract rules. Random papers matched only
  through the abstract were read for every topic, in 2024-2026 and again in 2020-2023, to check that the words keep the
  topic's sense in the early years too (`results/precision_review.md`). On 2026-10-28 a review of CoRL 2026 found words
  used in new senses (learned "whole-body control", conformal "calibration", "frontier models", task-level "planners",
  paired human-robot data, ML "prototypes"); ten rules were narrowed, URLs in abstracts are no longer matched, and every
  paper that left or entered a topic in any year was read (last section of `results/precision_review.md`).
- **Shares**: percentage of papers, standardised to the 2025 venue mix so the years compare; 2026 uses the within-venue
  change at ICRA, RSS, CoRL and the journals. IROS 2026 (44% of the 2025 mix) is extrapolated from that common change, so
  the 2026 shares are provisional until IROS 2026 is out: adding CoRL 2026 alone moved some of them by up to 2.4 points. **Numbers of papers**: raw counts, all venues (2026 is not a full year).
  **Trends**: logistic regression of topic on venue and year, Benjamini–Hochberg correction across topics; a topic is
  called rising or declining only at q < 0.05, over 2020-2026 and separately over 2024-2026. Per venue: raw shares with
  Wilson intervals and a likelihood-ratio trend test.
- **Limits**: a share counts papers that name a topic, including in passing; keyword rules miss papers that describe a
  topic in other words; abstracts got slightly longer over the years (median 164 words in 2020, 173 in 2025), which gives
  every topic slightly more chances to be named later; RSS, CoRL, IJRR and Science Robotics are small, so their trends are
  rarely significant.

Main tables: `results/REPORT.md` (all topics: shares, changes and numbers of papers), `results/scope_trends_ta.csv` and
`results/venue_matrix_ta.md` (by venue), `results/combination_manip_il_vla_flow_gs.md` (co-occurrence of manipulation,
imitation learning, VLA/VLM, diffusion/flow and Gaussian splatting). For choosing a topic: `results/method_penetration.md` (how often each rising method appears inside each application domain) and `results/relative_attention.md` (topic growth against the growth of all topic mentions).

## Data sources

| source | used for | licence |
|---|---|---|
| [dblp](https://dblp.org/xml/) XML dump of 2026-10-13 | IROS, T-RO, IJRR, Science Robotics records; venue checks | CC0 |
| [OpenAlex](https://openalex.org) | ICRA records and most abstracts | CC0 |
| [RSS proceedings](https://www.roboticsproceedings.org) | RSS 2020–2026 titles and abstracts | — |
| [PMLR](https://proceedings.mlr.press) v155, v164, v205, v229, v270, v305 | CoRL 2020–2025 titles and abstracts | — |
| [CoRL 2026 accepted papers](https://www.corl.org/program/accepted-papers) | CoRL 2026 titles and OpenReview links | — |
| [arXiv](https://arxiv.org) listing pages, dblp's arXiv records, OpenAlex by arXiv DOI | CoRL 2026 abstracts (arXiv versions) | arXiv / CC0 |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov) (NCBI E-utilities) | Science Robotics article types and abstracts; its 2026 articles not yet in dblp | NLM terms |
| [Crossref](https://www.crossref.org), [Semantic Scholar](https://www.semanticscholar.org), [arXiv](https://arxiv.org) | a few abstracts missing elsewhere (identical titles only) | API terms |

Abstract texts were used only to assign topics and are **not redistributed** here; `scripts/09_fetch_abstracts.py`
fetches them again from the sources above.

## Layout

| path | content |
|---|---|
| `index.html`, `data.json`, `subsets.json` | the page (static; `data.json` holds titles, venues, years, links and topic labels; `subsets.json` the results for every combination of venues, loaded when one is picked) |
| `deadlines.html` | submission deadlines of the seven venues for one year from 20 October 2026, each date with the official page it was read from (built by `scripts/23_deadlines_page.py`, which holds the dates) |
| `scripts/` | the pipeline, numbered in run order; `config.py` holds years, venues and the reviews switch; `page_template.html` is the page source |
| `results/` | tables and reports; `figures/` the figures |
| `data/` | `papers.csv` (research articles), `article_types.csv` (type of every item and why), `topic_matrix_ta.csv` (paper × topic, final measure), `topic_matrix.csv` (title only), `dblp_venues_2020_2026.jsonl` (venue subset of the dblp dump), `extra_corl_site.jsonl` (CoRL 2026 list), `corl_site_arxiv.csv` (arXiv version found for each CoRL 2026 paper and how), `corl_site_manual_matches.csv` (the 43 read title pairs with the reason) |

`results/trends*.csv`, `compare_measures.csv`, `SUMMARY.md`, `arxiv_combination_check.json` and `figures/fig1-3` are
robustness records of the earlier 2024–2026 title-only study and were not rerun for 2020–2026.

## Reproduce

```
python scripts/01_extract_dblp.py         # dblp dump at ~/.cache/robotics-trends/dblp/dblp.xml.gz
python scripts/02_fetch_extra_venues.py   # RSS, PMLR, OpenAlex
python scripts/02b_fetch_corl_site.py     # CoRL years without a PMLR volume: conference-site list
python scripts/03_build_dataset.py
python scripts/03b_research_articles.py   # PubMed article types; research articles only
python scripts/04_topics.py
python scripts/09b_corl_site_abstracts.py # CoRL 2026 abstracts from the papers' arXiv versions
python scripts/09_fetch_abstracts.py      # abstracts (resumable; --no-fetch only assembles the cached ones)
python scripts/12_title_abstract.py
python scripts/13_shares_and_change.py
python scripts/14_figures_ta.py
python scripts/15_report.py
python scripts/16_combination_and_supplements.py
python scripts/21_method_penetration.py   # method_penetration / relative_attention tables
python scripts/20_scope_trends.py
python scripts/20b_scope_subsets.py      # every other venue combination (page: free venue selection)
python scripts/18_build_site_data.py
python scripts/19_build_site.py
```
To view the page locally run `python -m http.server` in the repository and open http://127.0.0.1:8000/.
