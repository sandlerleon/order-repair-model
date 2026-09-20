# -*- coding: utf-8 -*-
"""Three figures, all computed from order_repair_model rather than drawn by hand.

    Fig 1  the model: self-amplifying repair, the S-shaped equilibrium curve,
           and the hysteresis that follows from it
    Fig 2  how the tipping point moves with repair fidelity under the uniform
           implementation, including the exact linearity of rho_c in alpha
    Fig 3  the three ways repair enhancement can enter, which agree on direction
           and disagree on magnitude -- the basis of prediction P5

    python make_figures.py
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from order_repair_model import BASE, ALPHAS, analyse, mu_mup, rho_of, cusp_alpha

DPI = 300
C = {"A": "#1b6ca8", "B": "#c1553b", "C": "#3f8f4a",
     "stable": "#1b1b1b", "unstable": "#9a9a9a", "fold": "#c1553b"}
plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 9, "axes.titlesize": 9,
                     "legend.fontsize": 7.5, "xtick.labelsize": 8,
                     "ytick.labelsize": 8, "axes.linewidth": 0.8,
                     "font.family": "DejaVu Sans"})

R = json.load(open("order_repair_results.json"))


def branches(p, a, mode, n=4000):
    """Split the equilibrium curve into stable and unstable arms.

    rho(I) is single-valued, so the S-curve is obtained by plotting I against
    rho(I) rather than by solving for I. The middle arm -- between the two folds
    -- is the unstable one.
    """
    I = np.linspace(1e-4, 1 - 1e-4, n)
    rho = rho_of(I, p, a, mode)
    r = analyse(p, a, mode)
    if not r["bistable"]:
        return [(I, rho, True)], r
    lo, hi = r["I_lower"], r["I_c"]
    mid = (I >= lo) & (I <= hi)
    return [(I[~mid & (I < lo)], rho[~mid & (I < lo)], True),
            (I[mid], rho[mid], False),
            (I[~mid & (I > hi)], rho[~mid & (I > hi)], True)], r


def integrate(I0, rho, p, a, mode, dt=0.01, steps=4000):
    I = I0
    for _ in range(steps):
        mu, _ = mu_mup(np.array([I]), p, a, mode)
        I = float(np.clip(I + dt * (mu[0] * (1 - I) - rho * I), 1e-6, 1 - 1e-6))
    return I


# ================================================================== FIGURE 1
fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))

# --- A: the repair function
I = np.linspace(0, 1, 500)
mu, _ = mu_mup(np.clip(I, 1e-6, 1), BASE, 1.0, "A")
mu_flat = np.full_like(I, BASE["mu0"])
ax[0].plot(I, mu, color=C["A"], lw=1.8, label=r"self-amplifying $\mu(I)$")
ax[0].plot(I, mu_flat, color=C["unstable"], lw=1.4, ls="--", label=r"constant $\mu_0$")
ax[0].set_xlabel("tissue order $I$")
ax[0].set_ylabel(r"repair rate $\mu(I)$")
ax[0].set_title("A   Repair reinforces order", loc="left", fontweight="bold")
ax[0].legend(frameon=False, loc="upper left")
ax[0].set_xlim(0, 1)
ax[0].set_ylim(0, None)

# --- B: the S-curve
segs, r1 = branches(BASE, 1.0, "A")
for x, y, stable in segs:
    ax[1].plot(y, x, color=C["stable"] if stable else C["unstable"],
               lw=1.8 if stable else 1.2, ls="-" if stable else ":")
ax[1].plot([r1["rho_c"]], [r1["I_c"]], "o", ms=5, color=C["fold"], zorder=5)
ax[1].plot([r1["rho_lower"]], [r1["I_lower"]], "o", ms=5, color=C["fold"], zorder=5)
ax[1].annotate(r"$\rho_c$ = %.2f" % r1["rho_c"], xy=(r1["rho_c"], r1["I_c"]),
               xytext=(r1["rho_c"] + 0.28, r1["I_c"] + 0.16), fontsize=8,
               arrowprops=dict(arrowstyle="->", lw=0.8, color=C["fold"]))
ax[1].set_xlim(0, 2.2)
ax[1].set_ylim(0, 1)
ax[1].set_xlabel(r"erosion flux $\rho$")
ax[1].set_ylabel("equilibrium order $I^*$")
ax[1].set_title("B   Two stable states coexist", loc="left", fontweight="bold")
ax[1].legend(handles=[Line2D([], [], color=C["stable"], lw=1.8, label="stable"),
                      Line2D([], [], color=C["unstable"], lw=1.2, ls=":", label="unstable"),
                      Line2D([], [], color=C["fold"], marker="o", ls="", ms=5, label="fold")],
             frameon=False, loc="upper right")

# --- C: hysteresis
rho_up = np.linspace(0.05, 2.0, 160)
up, I0 = [], 0.95
for rho in rho_up:
    I0 = integrate(I0, rho, BASE, 1.0, "A")
    up.append(I0)
down = []
for rho in rho_up[::-1]:
    I0 = integrate(I0, rho, BASE, 1.0, "A")
    down.append(I0)
ax[2].plot(rho_up, up, color=C["A"], lw=1.8, label="rising stress")
ax[2].plot(rho_up[::-1], down, color=C["B"], lw=1.8, ls="--", label="falling stress")
ax[2].set_xlabel(r"erosion flux $\rho$")
ax[2].set_ylabel("tissue order $I$")
ax[2].set_title("C   The collapse does not reverse", loc="left", fontweight="bold")
ax[2].legend(frameon=False, loc="upper right")
ax[2].set_xlim(0, 2.0)
ax[2].set_ylim(0, 1)

for a in ax:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("figure1_model.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("figure1_model.png")

# ================================================================== FIGURE 2
fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.6),
                       gridspec_kw={"width_ratios": [1.55, 1]})
cmap = plt.get_cmap("viridis")
cols = [cmap(t) for t in np.linspace(0.08, 0.82, len(ALPHAS))]
for a, col in zip(ALPHAS, cols):
    segs, r = branches(BASE, a, "A")
    top = max(range(len(segs)), key=lambda k: segs[k][0].max())  # high-order arm
    for k, (x, y, stable) in enumerate(segs):
        ax[0].plot(y, x, color=col, lw=1.7 if stable else 1.0,
                   ls="-" if stable else ":",
                   label=(r"$\alpha$ = %.1f" % a) if k == top else None)
    if r["rho_c"]:
        ax[0].plot([r["rho_c"]], [r["I_c"]], "o", ms=5.5, color=col,
                   markeredgecolor="white", markeredgewidth=0.7, zorder=6)
ax[0].set_xlim(0, 3.2)
ax[0].set_ylim(0, 1)
ax[0].set_xlabel(r"erosion flux $\rho$")
ax[0].set_ylabel("equilibrium order $I^*$")
ax[0].set_title(r"A   Higher repair fidelity $\alpha$ moves the tipping point",
                loc="left", fontweight="bold")
ax[0].legend(frameon=False, loc="upper right", ncol=2)

af = np.array(R["scaling_A"]["alpha"])
rc = np.array(R["scaling_A"]["rho_c"])
ax[1].plot(af, rc, "o", ms=3.4, color=C["A"], label=r"computed $\rho_c(\alpha)$")
ax[1].plot(af, R["scaling_A"]["ratio_mean"] * af, "-", lw=1.2, color=C["fold"],
           label=r"$\rho_c = \alpha\,\rho_c(1)$")
ax[1].set_xlabel(r"repair multiplier $\alpha$")
ax[1].set_ylabel(r"tipping point $\rho_c$")
ax[1].set_title("B   The relation is exactly linear", loc="left", fontweight="bold")
ax[1].legend(frameon=False, loc="upper left")
ax[1].text(0.97, 0.05,
           "max deviation\n%.0e (machine precision)" % R["scaling_A"]["ratio_max_rel_dev"],
           transform=ax[1].transAxes, ha="right", va="bottom", fontsize=7,
           color="#555555")
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("figure2_tipping_point.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("figure2_tipping_point.png")

# ================================================================== FIGURE 3
fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.6))
alphas = np.linspace(0.5, 6.0, 120)
labels = {"A": r"A  uniform: $\alpha\mu_0(1+\beta s)$",
          "B": r"B  constitutive only: $\mu_0(\alpha+\beta s)$",
          "C": r"C  feedback only: $\mu_0(1+\alpha\beta s)$"}
for mode in ("A", "B", "C"):
    xs, ys = [], []
    for a in alphas:
        r = analyse(BASE, float(a), mode)
        if r["rho_c"]:
            xs.append(a); ys.append(r["rho_c"])
    ax[0].plot(xs, ys, color=C[mode], lw=1.8, label=labels[mode])
    c = R["cusp"].get(mode)
    if c:
        ax[0].plot([c], [analyse(BASE, c * 0.999, mode)["rho_c"]], "v", ms=7,
                   color=C[mode], markeredgecolor="white", markeredgewidth=0.7, zorder=6)
        ax[0].annotate("bistability lost\nabove $\\alpha$ = %.2f" % c,
                       xy=(c, analyse(BASE, c * 0.999, mode)["rho_c"]),
                       xytext=(c + 0.45, 0.35), fontsize=7.2, color=C[mode],
                       arrowprops=dict(arrowstyle="->", lw=0.8, color=C[mode]))
ax[0].set_xlabel(r"repair multiplier $\alpha$")
ax[0].set_ylabel(r"tipping point $\rho_c$")
ax[0].set_title("A   Same direction, different magnitude", loc="left", fontweight="bold")
ax[0].legend(frameon=False, loc="upper left")
ax[0].set_xlim(0.5, 6)
ax[0].set_ylim(0, None)

rob = R["robustness"]["modes"]
pos = np.arange(3)
med = [rob[m]["median"] for m in ("A", "B", "C")]
lo = [rob[m]["median"] - rob[m]["p5"] for m in ("A", "B", "C")]
hi = [rob[m]["p95"] - rob[m]["median"] for m in ("A", "B", "C")]
ax[1].bar(pos, med, yerr=[lo, hi], color=[C["A"], C["B"], C["C"]], width=0.55,
          capsize=4, error_kw=dict(lw=1.0))
ax[1].axhline(1.0, color="#888888", lw=1.0, ls="--")
ax[1].set_xticks(pos)
ax[1].set_xticklabels(["A\nuniform", "B\nconstitutive", "C\nfeedback"])
ax[1].set_ylabel(r"$\rho_c(\alpha{=}2)\,/\,\rho_c(\alpha{=}1)$")
ax[1].set_title("B   Direction holds across %s parameter sets"
                % format(R["robustness"]["bistable_sets"], ","),
                loc="left", fontweight="bold")
for x, m in zip(pos, ("A", "B", "C")):
    ax[1].text(x, rob[m]["p95"] + 0.06, "%.0f%% > 1" % (100 * rob[m]["fraction_above_one"]),
               ha="center", fontsize=7.2, color="#444444")
ax[1].set_ylim(0, 2.45)
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("figure3_implementations.png", dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("figure3_implementations.png")
print("\nall figures written")
