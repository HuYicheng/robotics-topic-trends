"""Figures: (1) forest plot of venue-adjusted annual odds multipliers; (2) per-venue shares for key topics.

Colors: reference palette of the dataviz method. Fig 1 encodes direction with the diverging pair (blue = rising,
red = declining) and a neutral gray for unclear, with filled vs hollow markers as the second encoding.
Fig 2 uses categorical slots 1-5 in fixed order for venues (validated: all checks pass; three slots are below
3:1 contrast, so a legend and the CSV tables carry the values).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
RISE, FALL, NEUTRAL = "#2a78d6", "#e34948", "#7c7b77"
VENUE_COLORS = {"ICRA": "#2a78d6", "IROS": "#eb6834", "RSS": "#1baf7a", "CoRL": "#eda100", "Journals": "#e87ba4"}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF, "font.family": "DejaVu Sans"})


def forest():
    t = pd.read_csv(os.path.join(ROOT, "results", "trends.csv"))
    t = t[t.family != "E term"].sort_values("annual_OR")
    fig, ax = plt.subplots(figsize=(9.2, 13))
    for i, r in enumerate(t.itertuples()):
        c = RISE if r.call == "rising" else FALL if r.call == "declining" else NEUTRAL
        ax.plot([r.annual_OR_lo, r.annual_OR_hi], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(r.annual_OR, i, "o", ms=6.5, color=c, mfc=c if r.call != "unclear" else SURF, mew=1.6)
        ax.text(1.02, i, f"{100 * r.share_2024:.2f} → {100 * r.share_2025:.2f}%", va="center", ha="left", fontsize=7.5,
                color=INK2, transform=ax.get_yaxis_transform(), clip_on=False)
    ax.axvline(1, color=INK2, lw=1)
    ax.set_xscale("log"); ax.set_xlim(0.3, 20)
    ax.set_xticks([0.5, 1, 2, 4, 8]); ax.set_xticklabels(["×0.5", "×1", "×2", "×4", "×8"])
    ax.set_yticks(range(len(t))); ax.set_yticklabels(t.topic, fontsize=8)
    ax.set_ylim(-0.8, len(t) - 0.2)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("Change in topic share per year (odds multiplier, within venue, 95% CI)")
    ax.text(1.02, len(t) - 0.2, "share of titles\n2024 → 2025", ha="left", va="bottom", fontsize=7.5, color=INK2,
            transform=ax.get_yaxis_transform(), clip_on=False)
    fig.suptitle("Topic trends at ICRA, IROS, RSS, CoRL, T-RO, IJRR, Science Robotics, 2024–2026\n"
                 "filled = significant (FDR q<0.05): blue rising, red declining;  hollow gray = unclear",
                 x=0.01, ha="left", fontsize=10, color=INK)
    fig.subplots_adjust(left=0.40, right=0.83, top=0.935, bottom=0.05)
    out = os.path.join(ROOT, "figures", "fig1_topic_trends_forest.png")
    fig.savefig(out, dpi=150); print(out)


def small_multiples():
    s = pd.read_csv(os.path.join(ROOT, "data", "topic_matrix.csv"))
    s = s[s.venue.isin(["ICRA", "IROS", "RSS", "CoRL", "T-RO", "IJRR", "SciRobotics"]) & s.year.between(2023, 2026)]
    s["group"] = s.venue.replace({"T-RO": "Journals", "IJRR": "Journals", "SciRobotics": "Journals"})
    topics = ["VLA / robot foundation models", "Diffusion / flow generative models", "Humanoid robots",
              "3D Gaussian splatting", "Reasoning / chain-of-thought", "World models / video prediction",
              "LLM / VLM", "Whole-body control / loco-manipulation", "Reinforcement learning",
              "NeRF / neural implicit fields", "SLAM / localization / state estimation", "Calibration / registration"]
    fig, axes = plt.subplots(3, 4, figsize=(13, 8.6), sharex=True)
    for ax, topic in zip(axes.flat, topics):
        for g, c in VENUE_COLORS.items():
            d = s[s.group == g].groupby("year")[topic].mean() * 100
            ax.plot(d.index, d.values, "-o", color=c, lw=2, ms=4.5, label=g, mec=SURF, mew=1)
        ax.axvspan(2022.7, 2023.5, color=GRID, alpha=0.6, lw=0)
        ax.set_title(topic, fontsize=9, color=INK, loc="left")
        ax.set_xticks([2023, 2024, 2025, 2026]); ax.set_xlim(2022.7, 2026.3)
        ax.set_ylim(bottom=0); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}%"))
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.suptitle("Share of paper titles by venue, 2023–2026  (gray band = 2023, context only; IROS 2026 and CoRL 2026 not yet "
                 "published;\nRSS and CoRL have 130–260 papers a year, so one paper moves their line by 0.4–0.8 points)",
                 x=0.01, ha="left", y=0.995, fontsize=10, color=INK)
    fig.legend(handles, labels, loc="upper left", ncol=5, frameon=False, bbox_to_anchor=(0.005, 0.948))
    fig.tight_layout(rect=(0, 0, 1, 0.915))
    out = os.path.join(ROOT, "figures", "fig2_key_topics_by_venue.png")
    fig.savefig(out, dpi=150); print(out)


def title_vs_abstract():
    """Fig 3: annual multiplier by title vs by title+abstract ('focus'), same papers (those with abstracts)."""
    a = pd.read_csv(os.path.join(ROOT, "results", "trends_title_sub.csv")).set_index("topic")
    b = pd.read_csv(os.path.join(ROOT, "results", "trends_focus.csv")).set_index("topic")
    topics = b[b.family != "E term"].sort_values("annual_OR").index
    fig, ax = plt.subplots(figsize=(9.6, 13.4))
    c_title, c_abs = "#2a78d6", "#eb6834"   # categorical slots 1-2 (validated pair)
    for i, tp in enumerate(topics):
        for d, c, off, lab in ((a, c_title, 0.17, "title only"), (b, c_abs, -0.17, "title + abstract (≥2 mentions)")):
            r = d.loc[tp]
            sig = r.q_trend < 0.05
            ax.plot([r.annual_OR_lo, r.annual_OR_hi], [i + off, i + off], color=c, lw=1.8, solid_capstyle="round")
            ax.plot(r.annual_OR, i + off, "o", ms=5.5, color=c, mfc=c if sig else SURF, mew=1.5,
                    label=lab if i == 0 else None)
    ax.axvline(1, color=INK2, lw=1)
    ax.set_xscale("log"); ax.set_xlim(0.3, 20)
    ax.set_xticks([0.5, 1, 2, 4, 8]); ax.set_xticklabels(["×0.5", "×1", "×2", "×4", "×8"])
    ax.set_yticks(range(len(topics))); ax.set_yticklabels(topics, fontsize=8); ax.set_ylim(-0.8, len(topics) - 0.2)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel("Change in topic share per year (odds multiplier, within venue, 95% CI)")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    fig.suptitle("Title vs title+abstract, same 11,017 papers (2024–2026, seven venues)\n"
                 "filled = significant (FDR q<0.05), hollow = unclear", x=0.01, ha="left", fontsize=10, color=INK)
    fig.subplots_adjust(left=0.40, right=0.97, top=0.94, bottom=0.05)
    out = os.path.join(ROOT, "figures", "fig3_title_vs_abstract.png")
    fig.savefig(out, dpi=150); print(out)


if __name__ == "__main__":
    forest()
    small_multiples()
    title_vs_abstract()
