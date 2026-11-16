"""Figure 5 - methodology flow chart. Drawn from code only (no data values).
Box labels = manuscript headings (Sect. 2, 3.1-3.8, 4) so that figure and Methods match (Referee 1).
Run: python code/fig5_flowchart.py  -> Figure03_methods_flowchart.png / .pdf in the parent folder."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "figures")
C_IN, C_MOD, C_DES, C_OUT = "#dbe7f3", "#e3efe0", "#fbe8cf", "#ececec"
EDGE = "#33415c"

fig, ax = plt.subplots(figsize=(7.2, 7.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 106); ax.axis("off")

def box(cx, cy, w, h, num, title, color, fs=8.6):
    ax.add_patch(FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                 boxstyle="round,pad=0.25,rounding_size=1.4",
                 fc=color, ec=EDGE, lw=1.1))
    ax.text(cx, cy, f"{num}\n{title}" if num else title, ha="center", va="center",
            fontsize=fs, color="#111", linespacing=1.25)
    return dict(l=cx-w/2, r=cx+w/2, t=cy+h/2, b=cy-h/2, cx=cx, cy=cy)

def arrow(p, q, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11,
                 lw=1.2, color=EDGE, linestyle=ls,
                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

# row 1: input data
inp = box(50, 98, 88, 9, "Sect. 2", "Study area and input data\n(land use, rainfall, storage inventory, population and tourism)", C_IN)

# row 2: demand / roof / inflow
w2, h2, y2 = 28, 13, 79
b31 = box(18, y2, w2, h2, "3.1", "Population and\nwater demand", C_MOD)
b32 = box(50, y2, w2, h2, "3.2", "Roof catchment\nestimation", C_MOD)
b33 = box(82, y2, w2, h2, "3.3", "Harvestable inflow and\nstorage architecture", C_MOD)
for b in (b31, b32, b33):
    arrow((b["cx"], inp["b"]-0.4), (b["cx"], b["t"]+0.4))
arrow((b32["r"]+0.4, y2), (b33["l"]-0.4, y2))

# row 3: water balance + climate input
b34 = box(40, 56, 50, 12, "3.4", "Two-subsystem monthly\nwater balance", C_MOD)
b38 = box(82, 56, 28, 12, "3.8", "Climate input\nand cases", C_IN)
arrow((b31["cx"]+3, b31["b"]-0.4), (b34["l"]+6, b34["t"]+0.4))
arrow((b32["cx"]-4, b32["b"]-0.4), (b34["cx"]-4, b34["t"]+0.4))
arrow((b33["cx"]-9, b33["b"]-0.4), (b34["r"]-10, b34["t"]+0.4))
arrow((b38["l"]-0.4, 56), (b34["r"]+0.4, 56))

# row 4: RRV
b35 = box(40, 38, 50, 10, "3.5", "Supply performance:\nreliability, resilience, vulnerability", C_MOD)
arrow((b34["cx"], b34["b"]-0.4), (b35["cx"], b35["t"]+0.4))

# row 5: designs
b36 = box(22, 19, 40, 13, "3.6", "Mean-year design and the\ncatchment–storage trade-off", C_DES)
b37 = box(72, 19, 46, 13, "3.7", "Stochastic rainfall generation\nand robust design", C_DES)
arrow((b35["cx"]-8, b35["b"]-0.4), (b36["cx"]+4, b36["t"]+0.4))
arrow((b35["cx"]+8, b35["b"]-0.4), (b37["cx"]-8, b37["t"]+0.4))
arrow((b36["r"]+0.4, 19), (b37["l"]-0.4, 19))
# climate input also feeds the generator / projected rainfall
arrow((b38["cx"], b38["b"]-0.4), (b38["cx"], b37["t"]+0.4), ls="--")

# outputs
out = box(50, 3.5, 88, 6, "Sect. 4", "Results: mean-year and drought-robust design targets", C_OUT, fs=8.6)
arrow((b36["cx"], b36["b"]-0.4), (b36["cx"], out["t"]+0.4))
arrow((b37["cx"], b37["b"]-0.4), (b37["cx"], out["t"]+0.4))

plt.savefig(os.path.join(OUT, "Figure03_methods_flowchart.png"), dpi=300, bbox_inches="tight")
plt.savefig(os.path.join(OUT, "Figure03_methods_flowchart.pdf"), bbox_inches="tight")
