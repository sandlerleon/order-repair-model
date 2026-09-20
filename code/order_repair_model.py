# -*- coding: utf-8 -*-
"""The bistable order-repair model, its fold points, and how they move with
repair fidelity.

    dI/dtau = mu(I) (1 - I) - rho I

with self-amplifying repair mu(I) = mu0 (1 + beta s(I)), s(I) = I^h/(K^h + I^h).

The equilibrium condition inverts exactly: mu(I)(1-I) = rho I gives

    rho(I) = mu(I) (1 - I) / I

so the bifurcation diagram is read off a sweep of I over (0,1) with no
integration. The fold (saddle-node) is d rho / d I = 0, which reduces to

    mu'(I) (1 - I) I - mu(I) = 0

and is solved by bracketing sign changes and refining with Brent's method,
rather than by taking the extremum of a dense grid.

Repair enhancement can enter three ways, and they are NOT equivalent:

    A  uniform     mu_a(I) = a * mu0 (1 + beta s)    both terms scaled
    B  baseline    mu_a(I) = mu0 (a + beta s)        constitutive repair only
    C  feedback    mu_a(I) = mu0 (1 + a beta s)      order-dependent repair only

Under A the fold condition loses its a-dependence entirely, so rho_c should be
exactly proportional to a with the fold position fixed. That is asserted by the
algebra above and then checked numerically. B and C are checked, not assumed.

    python order_repair_model.py
"""
import json
import numpy as np
from scipy.optimize import brentq

SEED = 20260919
BASE = dict(mu0=0.10, beta=12.0, K=0.50, h=4.0)
ALPHAS = [0.5, 1.0, 2.0, 4.0]


def s_of(I, K, h):
    Ih = np.power(I, h)
    return Ih / (np.power(K, h) + Ih)


def sp_of(I, K, h):
    Kh = np.power(K, h)
    return h * Kh * np.power(I, h - 1.0) / np.power(Kh + np.power(I, h), 2.0)


def mu_mup(I, p, a, mode):
    s, sp = s_of(I, p["K"], p["h"]), sp_of(I, p["K"], p["h"])
    b, m0 = p["beta"], p["mu0"]
    if mode == "A":
        return a * m0 * (1.0 + b * s), a * m0 * b * sp
    if mode == "B":
        return m0 * (a + b * s), m0 * b * sp
    if mode == "C":
        return m0 * (1.0 + a * b * s), m0 * a * b * sp
    raise ValueError(mode)


def rho_of(I, p, a, mode):
    mu, _ = mu_mup(I, p, a, mode)
    return mu * (1.0 - I) / I


def fold_eq(I, p, a, mode):
    mu, mup = mu_mup(I, p, a, mode)
    return mup * (1.0 - I) * I - mu


def analyse(p, a, mode, scan=2000):
    """Locate the interior turning points of rho(I).

    rho falls from +inf at I->0 to 0 at I->1. Monotone means one equilibrium per
    rho and no bistability. A local minimum followed by a local maximum is the
    S-shaped case; that maximum is the stress at which the high-order branch is
    destroyed, so it is the tipping point.
    """
    I = np.linspace(1e-6, 1.0 - 1e-6, scan)
    f = fold_eq(I, p, a, mode)
    roots = []
    sign = np.sign(f)
    for i in np.where(sign[:-1] * sign[1:] < 0)[0]:
        try:
            r = brentq(fold_eq, I[i], I[i + 1], args=(p, a, mode), xtol=1e-14)
        except ValueError:
            continue
        # classify: rho' changes sign; rho'(I) has the sign of fold_eq / I^2
        kind = "max" if f[i] > 0 else "min"
        roots.append({"I": float(r), "rho": float(rho_of(r, p, a, mode)), "kind": kind})
    maxima = [x for x in roots if x["kind"] == "max"]
    minima = [x for x in roots if x["kind"] == "min"]
    return {"alpha": a, "mode": mode,
            "bistable": bool(maxima and minima),
            "rho_c": maxima[-1]["rho"] if maxima else None,
            "I_c": maxima[-1]["I"] if maxima else None,
            "rho_lower": minima[0]["rho"] if minima else None,
            "I_lower": minima[0]["I"] if minima else None}



def cusp_alpha(p, mode, lo=1.0, hi=40.0, tol=1e-9):
    """Smallest alpha above which the fold pair has annihilated.

    Below the cusp the system is bistable and stress produces a catastrophic
    collapse; above it rho(I) is monotone and tissue order declines smoothly.
    Returns None if the mode stays bistable across the bracket.
    """
    if not analyse(p, lo, mode)["bistable"]:
        return None
    if analyse(p, hi, mode)["bistable"]:
        return None
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if analyse(p, mid, mode)["bistable"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    res = {"seed": SEED, "parameters": BASE, "alphas": ALPHAS}

    # ---------------------------------------------------------------- 1. base case
    print("baseline parameters: %s\n" % BASE)
    print("%-5s %-6s %-9s %10s %8s %12s" % ("mode", "alpha", "bistable", "rho_c", "I_c", "rho_c/alpha"))
    res["modes"] = {}
    for mode in ("A", "B", "C"):
        rows = [analyse(BASE, a, mode) for a in ALPHAS]
        res["modes"][mode] = rows
        for r in rows:
            print("%-5s %-6.1f %-9s %10.5f %8.4f %12.5f"
                  % (mode, r["alpha"], r["bistable"],
                     r["rho_c"] if r["rho_c"] else float("nan"),
                     r["I_c"] if r["I_c"] else float("nan"),
                     r["rho_c"] / r["alpha"] if r["rho_c"] else float("nan")))
        print()

    # ------------------------------------------- 2. is the scaling under A exact?
    a_fine = np.linspace(0.25, 8.0, 64)
    rc = np.array([analyse(BASE, float(a), "A")["rho_c"] for a in a_fine])
    Ic = np.array([analyse(BASE, float(a), "A")["I_c"] for a in a_fine])
    ratio = rc / a_fine
    res["scaling_A"] = {
        "alpha": a_fine.tolist(), "rho_c": rc.tolist(),
        "ratio_mean": float(ratio.mean()),
        "ratio_max_rel_dev": float(np.max(np.abs(ratio - ratio.mean())) / ratio.mean()),
        "I_c_spread": float(Ic.max() - Ic.min())}
    print("model A, alpha in [0.25, 8]:")
    print("   rho_c/alpha constant to %.2e relative deviation" % res["scaling_A"]["ratio_max_rel_dev"])
    print("   fold position I_c varies by %.2e\n" % res["scaling_A"]["I_c_spread"])

    # --------------------------------- 3. does the direction hold off this parameter set?
    rng = np.random.default_rng(SEED)
    N = 20000
    rows = {"A": [], "B": [], "C": []}
    bistable_sets = 0
    for _ in range(N):
        p = dict(mu0=float(rng.uniform(0.02, 0.30)), beta=float(rng.uniform(2.0, 30.0)),
                 K=float(rng.uniform(0.20, 0.80)), h=float(rng.uniform(2.0, 8.0)))
        if not analyse(p, 1.0, "A")["bistable"]:
            continue
        bistable_sets += 1
        for mode in ("A", "B", "C"):
            lo, hi = analyse(p, 1.0, mode), analyse(p, 2.0, mode)
            if lo["rho_c"] and hi["rho_c"]:
                rows[mode].append(hi["rho_c"] / lo["rho_c"])

    res["robustness"] = {"parameter_sets_tested": N, "bistable_sets": bistable_sets, "modes": {}}
    print("%d of %d random parameter sets were bistable at alpha=1 (%.1f%%)"
          % (bistable_sets, N, 100.0 * bistable_sets / N))
    print("\nratio rho_c(alpha=2) / rho_c(alpha=1):")
    print("%-5s %8s %9s %9s %9s %11s" % ("mode", "n", "median", "p5", "p95", "frac > 1"))
    for mode in ("A", "B", "C"):
        v = np.array(rows[mode])
        d = {"n": int(v.size), "median": float(np.median(v)),
             "p5": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95)),
             "fraction_above_one": float((v > 1.0).mean())}
        res["robustness"]["modes"][mode] = d
        print("%-5s %8d %9.3f %9.3f %9.3f %11.4f"
              % (mode, d["n"], d["median"], d["p5"], d["p95"], d["fraction_above_one"]))

    # ------------------------------------------------ 4. where does the fold die?
    res["cusp"] = {}
    print("\ncusp alpha (bistability lost above this value):")
    for mode in ("A", "B", "C"):
        c = cusp_alpha(BASE, mode)
        res["cusp"][mode] = c
        print("   mode %s : %s" % (mode, ("%.4f" % c) if c else "no cusp in [1, 40]"))

    json.dump(res, open("order_repair_results.json", "w"), indent=1)
    print("\nwrote order_repair_results.json")


if __name__ == "__main__":
    main()
