"""Single chart style used across every notebook exhibit.

Figure sizes and font sizes are set together deliberately. Exhibits are placed
at roughly 6.0in in the report and 5.8-7.3in in the deck; authoring them much
wider than that shrinks every glyph on placement. Figures are therefore
authored at ~7.5in wide and fonts set large enough that, at the ~0.8 scale
factor that placement implies, nothing renders below ~8pt.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

PALETTE = {
    "primary": "#1a3a5c",
    "secondary": "#c0392b",
    "accent": "#2e8b57",
    "gold": "#b8860b",
    "grey": "#7f7f7f",
    "light_grey": "#d9d9d9",
}

# ordered cycle for multi-series plots - keeps every exhibit on the same
# palette instead of falling back to matplotlib's default tab10 (which
# introduces an orange that clashes with this scheme)
SERIES = [PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"], PALETTE["gold"]]

# standard authored figure sizes (inches)
FIG_WIDE = (7.5, 3.9)
FIG_STD = (7.5, 4.2)
FIG_TALL = (7.5, 4.6)


def apply_style():
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.9,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#e6e6e6",
        "grid.linewidth": 0.7,
        "font.size": 13,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlepad": 10,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 11,
        # opaque white legend box: legends here frequently sit over the zero
        # line, gridlines or a plotted series, and a frameless legend lets
        # those rules strike through the label text
        "legend.frameon": True,
        "legend.facecolor": "white",
        "legend.edgecolor": "#d9d9d9",
        "legend.framealpha": 0.95,
        "legend.borderpad": 0.6,
        "lines.linewidth": 1.8,
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.prop_cycle": mpl.cycler(color=SERIES),
    })


def save_chart(fig, name: str, out_dir):
    path = out_dir / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    return path


def source_note(ax, text="Source: Yahoo Finance / SEC EDGAR"):
    """Source line sized to stay legible after the figure is scaled down on
    placement. Figures are authored at 7.5in and placed as small as ~5.5in
    (a 0.73 scale factor), so 11pt here is the floor that still clears 8pt
    effective at the smallest placement used in the deck."""
    ax.annotate(text, xy=(0, -0.20), xycoords="axes fraction",
                fontsize=11, color=PALETTE["grey"])


def stagger_event_labels(ax, events, top=0.97, color=None, fontsize=10.5,
                          row_gap=0.085):
    """Draw dated vertical event markers with labels that cannot collide.

    events: list of (datetime-like, label) in chronological order.

    Each event gets its OWN vertical row (not an alternating two-row cycle -
    with three markers that still puts events 1 and 3 on the same line, and a
    long label on the left then overprints the one on its right). Labels are
    also right-aligned when their marker sits in the right-hand part of the
    axes, so the text extends inward across empty chart area instead of
    running off the edge and being clipped.
    """
    import pandas as pd
    color = color or PALETTE["secondary"]
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    span = xmax - xmin

    for i, (d, label) in enumerate(events):
        x = pd.Timestamp(d)
        ax.axvline(x, color=color, linestyle="--", linewidth=1.1, alpha=0.85)
        xpos = ax.transLimits.transform((mpl.dates.date2num(x), 0))[0] \
            if span else 0.5
        right_side = xpos > 0.55
        y = ymin + (ymax - ymin) * (top - i * row_gap)
        ax.annotate(
            label,
            xy=(x, y),
            xytext=(-6 if right_side else 6, 0), textcoords="offset points",
            fontsize=fontsize, color=color, fontweight="bold",
            ha="right" if right_side else "left", va="center",
            clip_on=False,
            bbox=dict(boxstyle="round,pad=0.24", facecolor="white",
                      edgecolor="none", alpha=0.88),
        )
