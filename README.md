# Order–repair model: repair fidelity as a control parameter for tissue stability

Leon Sandler, Independent Researcher — sandler.leon@gmail.com
ORCID [0009-0007-4584-808X](https://orcid.org/0009-0007-4584-808X)

Model and manuscript for *"Repair Fidelity as a Control Parameter Linking Cancer
Resistance and Longevity: a bistable order–repair hypothesis inspired by the
bowhead whale,"* submitted to **BioEssays** as a Hypotheses article.

The bowhead whale resists cancer without adding tumour-suppressor barriers — its
cells are *easier* to transform than human cells. What they have instead is more
accurate DNA repair. This repository asks what follows if repair fidelity is
treated not as one more cancer defence but as a parameter controlling whether
multicellular tissue stays in a stable cooperative state at all.

## The model

A single order parameter `I ∈ [0,1]` describes tissue integrity, maintained by
self-amplifying repair and eroded by stress:

```
dI/dτ = μ(I)(1 − I) − ρI        μ(I) = μ₀(1 + β·I^h/(K^h + I^h))
```

The equilibrium condition inverts exactly. Setting `μ(I)(1−I) = ρI` gives

```
ρ(I) = μ(I)(1 − I)/I
```

so the whole bifurcation diagram comes from sweeping `I` and reading off `ρ` —
no integration, no fitting. The fold, where the high-order state is destroyed,
is the root of `μ′(I)(1−I)I − μ(I) = 0`.

**Bistability here is assumed, not discovered.** Positive feedback of this form
produces bistability by construction. The interesting question is what moves the
threshold.

## Results

Repair enhancement is represented by a multiplier `α`, and it can enter three
ways — which are *not* equivalent:

| | form | ρ_c(α=2)/ρ_c(α=1) |
|---|---|---|
| **A** uniform | `α·μ₀(1 + βs)` | **2.000** |
| **B** constitutive only | `μ₀(α + βs)` | 1.099 |
| **C** feedback only | `μ₀(1 + αβs)` | 1.892 |

Three findings:

**1. Under uniform scaling the relation is exact.** Both `μ` and `μ′` carry the
factor `α`, so it cancels from the fold condition entirely: the fold sits at the
same tissue order for every `α`, and `ρ_c = α·ρ_c(1)` precisely. Computed
independently at 64 values of `α` from 0.25 to 8, `ρ_c/α` is constant to a
relative deviation of **3×10⁻¹⁶** and the fold position varies by **1×10⁻¹⁶** —
both at machine precision. This is algebra, not curve-fitting, and it holds for
every value of `μ₀`, `β`, `K` and `h`.

**2. The direction is robust; the magnitude is not.** Across **17,583** randomly
drawn parameter sets that were bistable at baseline, raising `α` raised the
tipping point in **100%** of cases under all three implementations. But the
three differ by nearly twofold in how much.

**3. Enough constitutive repair removes the cliff rather than moving it.** Above
`α = 2.60` at the baseline parameters, the two folds annihilate in a cusp, `ρ(I)`
becomes monotone, and the tissue's stress response changes character — from
all-or-nothing collapse to graded decline with no threshold at all. This was not
anticipated and is the model's most distinctive prediction.

## What this is and is not

Every result here is a structural consequence of an assumed feedback, not a
fitted or validated biological prediction. The model is not calibrated to
bowhead, mouse or human measurements, and the order parameter `I` has no
established experimental counterpart — developing one is a prerequisite for
testing the tissue-level claims. No experimental data were generated or used.

The hypothesis concerns repair **fidelity** — accurate restoration — and
explicitly not repair capacity or speed. More repair is not automatically better:
error-prone end-joining can itself generate the structural variants that drive
transformation.

## Contents

```
code/
  order_repair_model.py    the model, fold finding, scaling and robustness
                           -> order_repair_results.json
  make_figures.py          all three figures
  build_manuscript.py      manuscript, every number read from the JSON
  build_cover_letter.py    cover letter
  audit_manuscript.py      re-checks the built document against the model
  verify_refs.py           Crossref verification of the original references
  harvest_new_refs.py      Crossref lookup for references added in revision
figures/                   three figures, 300 dpi
manuscript/                manuscript and cover letter
```

## Reproducing

```bash
pip install -r requirements.txt
python code/order_repair_model.py    # model -> order_repair_results.json
python code/make_figures.py          # three figures
python code/build_manuscript.py      # manuscript
python code/audit_manuscript.py      # checks the document against the model
```

The manuscript builder reads every number from `order_repair_results.json`
rather than from transcribed values, so the text cannot drift from the
computation. The audit re-checks 12 headline quantities, verifies that every
reference is cited and every citation is listed, and looks for values described
as being on the wrong side of a threshold named in the same sentence.

All 17 references were verified against Crossref.

## Citation

Concept DOIs, which always resolve to the latest version:

- Code and model: [10.5281/zenodo.22851970](https://doi.org/10.5281/zenodo.22851970)
- Manuscript: [10.5281/zenodo.22851972](https://doi.org/10.5281/zenodo.22851972)

## License

Code MIT (`LICENSE`); manuscript text and figures CC BY 4.0.
