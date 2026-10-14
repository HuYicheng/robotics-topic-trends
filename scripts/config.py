"""Shared settings for the pipeline: one place for the analysed years, venues and file names."""
YEAR_MIN, YEAR_MAX = 2020, 2026
YEARS = list(range(YEAR_MIN, YEAR_MAX + 1))
VENUES = ["ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"]
REF_YEAR = 2025                                  # shares are standardised to this year's venue mix
DBLP_EXTRACT = f"data/dblp_venues_{YEAR_MIN}_{YEAR_MAX}.jsonl"
# per-venue sources (one source per venue for every year)
RSS_VOLUMES = {2020: "rss16", 2021: "rss17", 2022: "rss18", 2023: "rss19", 2024: "rss20", 2025: "rss21", 2026: "rss22"}
CORL_PMLR = {2020: "v155", 2021: "v164", 2022: "v205", 2023: "v229", 2024: "v270", 2025: "v305"}
ICRA_OPENALEX_SOURCE = "S4210217939"

# Only research articles are analysed (user, 2026-10-14). Editorials, commentaries, Focus/highlight pieces, errata and
# special-issue introductions are always removed; reviews/surveys too unless KEEP_REVIEWS (scripts/03b_research_articles.py).
KEEP_REVIEWS = False
