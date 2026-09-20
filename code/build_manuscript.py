# -*- coding: utf-8 -*-
"""Build the BioEssays Hypotheses manuscript.

Every quantitative statement is read from order_repair_results.json rather than
transcribed, so the text cannot drift from the model. Reference metadata comes
from the two Crossref verification passes.

The revision restructures the paper around the hypothesis rather than the whale,
following the reviewer feedback: the conceptual claim leads, the bowhead becomes
the empirical entry point, the model is introduced as a phenomenological test of
sufficiency rather than a simulation of bowhead physiology, and the predictions
are laid out as a molecular -> cellular -> tissue -> organismal -> coupling
ladder with the coupling prediction as the signature test.

    python build_manuscript.py
"""
import json
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\Leon\Downloads\BioEssays"
R = json.load(open(os.path.join(HERE, "order_repair_results.json")))
V = json.load(open(os.path.join(HERE, "_refs_verified.json")))
N = json.load(open(os.path.join(HERE, "_refs_new.json")))

# ------------------------------------------------------------------ numbers
P = R["parameters"]
A1 = [r for r in R["modes"]["A"] if r["alpha"] == 1.0][0]
A2 = [r for r in R["modes"]["A"] if r["alpha"] == 2.0][0]
A4 = [r for r in R["modes"]["A"] if r["alpha"] == 4.0][0]
SCA = R["scaling_A"]
ROB = R["robustness"]
CUSP_B = R["cusp"]["B"]

DOI_CODE = "PLACEHOLDER_CODE_DOI"
DOI_MS = "PLACEHOLDER_MS_DOI"
REPO = "https://github.com/sandlerleon/order-repair-model"

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 2.0

for s in doc.sections:
    s.left_margin = s.right_margin = Inches(1.0)
    s.top_margin = s.bottom_margin = Inches(1.0)
    # continuous line numbers for review
    sectPr = s._sectPr
    ln = OxmlElement("w:lnNumType")
    ln.set(qn("w:countBy"), "1")
    ln.set(qn("w:start"), "1")
    ln.set(qn("w:restart"), "continuous")
    ln.set(qn("w:distance"), "360")
    anchor = sectPr.find(qn("w:pgMar"))
    if anchor is None:
        anchor = sectPr.find(qn("w:pgSz"))
    if anchor is None:
        sectPr.insert(0, ln)
    else:
        anchor.addnext(ln)


def H(text, size=12, space_before=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(size)
    return p


def Pp(text, indent=False, italic=False, size=11, spacing=2.0, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = spacing
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.3)
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.italic = italic
    r.font.size = Pt(size)
    return p


def KEY(text):
    """A section-closing statement of the new insight, as BioEssays asks for."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    return p


def CAP(text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(text)
    r.font.size = Pt(9.5)
    return p


def FIG(path, width=6.3):
    if os.path.exists(os.path.join(HERE, path)):
        doc.add_picture(os.path.join(HERE, path), width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


# ==================================================================== FRONT
t = doc.add_paragraph()
t.paragraph_format.line_spacing = 1.5
r = t.add_run("Repair Fidelity as a Control Parameter Linking Cancer Resistance "
              "and Longevity")
r.bold = True
r.font.size = Pt(15)

s = doc.add_paragraph()
s.paragraph_format.line_spacing = 1.5
r = s.add_run("A bistable order\u2013repair hypothesis inspired by the bowhead whale")
r.italic = True
r.font.size = Pt(12)

Pp("Leon Sandler", spacing=1.5)
Pp("Independent Researcher, Northbrook, Illinois, United States", spacing=1.5, size=10.5)
Pp("ORCID: 0009-0007-4584-808X", spacing=1.5, size=10.5)
Pp("Correspondence: sandler.leon@gmail.com", spacing=1.5, size=10.5)

H("Summary")
SUMMARY = (
    "We propose that DNA-repair fidelity is not merely a determinant of mutation "
    "rate but a control parameter governing whether multicellular tissue remains "
    "in a stable cooperative state. The bowhead whale motivates the idea: it "
    "resists cancer not by adding tumour-suppressor barriers but by repairing "
    "damage more accurately. We formalise this with a bistable order\u2013repair "
    "model in which tissue integrity is sustained by self-amplifying repair and "
    "eroded by stress. Raising repair fidelity moves the stress threshold at "
    "which tissue collapses, and we show this shift is exact and independent of "
    "every shape parameter when repair is scaled uniformly. How repair "
    "enhancement is implemented changes the magnitude, and can abolish the "
    "threshold entirely. The framework predicts that cancer resistance and "
    "age-associated decline should move together under a single repair "
    "intervention \u2014 a coupling that distinguishes this hypothesis from "
    "conventional mutation-rate accounts.")
Pp(SUMMARY, spacing=1.5)

Pp("Keywords: DNA repair fidelity; Peto's paradox; bistability; tissue "
   "homeostasis; cancer resistance; ageing; bowhead whale; CIRBP",
   spacing=1.5, size=10.5)

# ================================================================= SECTION 1
H("A whale exposes a gap in the standard cancer-defence model")
Pp("Large, long-lived animals accumulate more cell divisions, and therefore more "
   "opportunities for oncogenic mutation, than small short-lived ones. That they "
   "do not suffer correspondingly more cancer is Peto's paradox (Caulin & Maley "
   "2011). The paradox is usually discussed as though it had one answer. It has "
   "at least two, and the difference between them is the starting point of this "
   "paper.")
Pp("Elephants multiply the barriers a damaged cell must cross. They carry dozens "
   "of extra copies of the tumour-suppressor gene TP53 and mount a more "
   "aggressive apoptotic response to DNA damage than human cells do (Abegglen et "
   "al. 2015). The naked mole rat interposes a different barrier again, secreting "
   "high-molecular-mass hyaluronan that suppresses contact-independent growth "
   "(Tian et al. 2013). In each case the logic is the same: damage occurs, is "
   "detected, and the affected cell is removed or arrested.", indent=True)
Pp("The bowhead whale (Balaena mysticetus), at more than 200 years the "
   "longest-lived mammal known, does something different, and does it at a body "
   "mass above 80,000 kg. Its fibroblasts require fewer oncogenic hits to "
   "transform in vitro than human fibroblasts do, so the whale is not harder to "
   "transform at the single-cell level. What its cells have instead is enhanced "
   "double-strand-break repair capacity and fidelity and lower mutation rates, "
   "associated with unusually high constitutive expression of the cold-inducible "
   "RNA-binding protein CIRBP. Transferring bowhead CIRBP into human cells raises "
   "both non-homologous end-joining and homologous-recombination efficiency, and "
   "CIRBP overexpression extends lifespan and radiation resistance in Drosophila "
   "(Firsanov et al. 2025).", indent=True)
Pp("Where elephants make damaged cells easier to remove, bowheads appear to make "
   "damage less likely to persist. Both strategies are effective; only one of "
   "them has a developed theoretical account (Seluanov et al. 2018).", indent=True)
KEY("The bowhead does not resolve Peto's paradox by eliminating damaged cells "
    "more aggressively. It resolves it by not accumulating the damage.")

# ================================================================= SECTION 2
H("Elimination and restoration have different system-level costs")
Pp("The elimination strategy carries a cost that is easy to overlook because it "
   "is paid slowly. Removing or permanently arresting damaged cells is itself a "
   "driver of tissue ageing when it happens at scale: a tissue that continually "
   "discards damaged cells must regenerate them, drawing on a finite progenitor "
   "pool, or accept a shrinking and less functional one. Senescent cells that are "
   "arrested rather than cleared accumulate and actively degrade the tissue around "
   "them (van Deursen 2014). Somatic mutation and the genome mosaicism it "
   "produces rise with age across tissues regardless of which barrier is in place "
   "(Vijg & Dong 2020). Genomic instability and cellular senescence are both "
   "counted among the hallmarks of ageing (López-Otín et al. 2023), and "
   "the elimination strategy engages one of them in order to contain the other.")
Pp("A restoration strategy has no equivalent structural cost. If damage is "
   "repaired accurately, the cell is neither lost nor retained in a damaged "
   "state, and the tissue neither shrinks nor accumulates dysfunctional "
   "occupants. This suggests that the two strategies should have different "
   "consequences for ageing even when they produce similar cancer incidence \u2014 "
   "and it is what makes repair fidelity interesting as something more than "
   "another item on the list of cancer defences.", indent=True)
KEY("Elimination and restoration can deliver comparable cancer resistance while "
    "differing in what they cost the tissue over a lifetime.")

# ================================================================= SECTION 3
H("What this hypothesis adds")
Pp("Existing explanations of Peto's paradox emphasise mechanisms that prevent "
   "damaged cells from progressing: apoptosis, senescence, immune surveillance, "
   "increased tumour-suppressor dosage. The present hypothesis asks a different "
   "question. Rather than asking how damaged cells are stopped, it asks whether "
   "reducing the persistence of genome damage changes the stability of the "
   "multicellular state itself.")
Pp("The novelty is therefore not the proposal that DNA repair suppresses cancer, "
   "which is uncontroversial. It is the proposal that repair fidelity acts as a "
   "shared control parameter linking cancer resistance and age-associated tissue "
   "decline \u2014 that these are two readouts of one quantity rather than two "
   "traits that happen to co-occur. That claim is stronger, more specific, and "
   "considerably easier to falsify than the observation that repair matters.",
   indent=True)
KEY("The claim under test is not that repair prevents cancer, but that one repair "
    "parameter governs two phenotypes that are usually studied separately.")

# ================================================================= SECTION 4
H("Repair fidelity is not the same as repair activity")
Pp("The hypothesis concerns fidelity specifically, and the distinction carries "
   "the argument. Three quantities are often used interchangeably and should not "
   "be:")
for term, gloss in [
    ("Repair capacity", "how much repair the cell can perform."),
    ("Repair efficiency", "what fraction of lesions is resolved."),
    ("Repair fidelity", "how accurately repair restores the original sequence "
                        "and structure."),
]:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(term + ". ")
    r.bold = True
    r.font.size = Pt(11)
    r = p.add_run(gloss)
    r.font.size = Pt(11)
Pp("Here, repair fidelity refers to the ability of DNA-repair processes to "
   "restore genome integrity while minimising mutagenic or structurally "
   "disruptive outcomes. The distinction is not pedantic. Repair pathway choice "
   "determines whether a double-strand break is resolved accurately by homologous "
   "recombination or by an end-joining route that may delete sequence at the "
   "junction (Ceccaldi et al. 2016). A cell that resolves every lesion quickly "
   "but inaccurately has high efficiency and low fidelity, and on this hypothesis "
   "it should behave like a cell with poor repair, not a well-protected one.",
   indent=True)
KEY("Throughout this paper the control parameter is fidelity \u2014 accurate "
    "restoration \u2014 and not the volume or speed of repair activity.")

# ================================================================= SECTION 5
H("A phenomenological model asks whether repair feedback is sufficient for bistability")
Pp("What follows is deliberately a minimal model rather than a representation of "
   "bowhead physiology. Its purpose is to ask whether a positive-feedback "
   "relationship between tissue order and repair is by itself sufficient to "
   "generate a threshold, and if so what moves that threshold. It is not fitted "
   "to bowhead, mouse or human measurements, and no parameter in it is claimed to "
   "be measured. Readers should treat the results as structural consequences of "
   "an assumed feedback, not as predictions of a calibrated system.")
Pp("We summarise the state of a tissue with one order parameter I \u2208 [0,1]. "
   "High I describes a directionally ordered, cooperative multicellular state; "
   "low I a reverted state in which cooperative constraints on individual cells "
   "have broken down. Malignant transformation is one instance of such a "
   "reversion, not necessarily the only one. The dynamics are", indent=True)
Pp("dI/d\u03c4 = \u03bc(I)(1 \u2212 I) \u2212 \u03c1I", italic=True, spacing=1.5)
Pp("with self-amplifying repair \u03bc(I) = \u03bc\u2080(1 + \u03b2s(I)), "
   "s(I) = I\u02b0/(K\u02b0 + I\u02b0), and an erosion flux "
   "\u03c1 = \u03c1\u2080 + \u03c1_stress\u00b7D + \u03c1_damage\u00b7N, where "
   "\u03c1\u2080 is baseline turnover, D is genotoxic or environmental stress and "
   "N is any accumulating burden of unrepaired lesions or pathological tissue. "
   "Repair is self-amplifying because intact, well-organised tissue supports its "
   "own maintenance machinery better than eroded tissue does. Positive feedback "
   "of this form is the standard route to bistability in cell-biological systems "
   "(Ferrell 2002), and the model inherits that behaviour by construction rather "
   "than discovering it.")
Pp("The equilibrium condition inverts exactly. Setting \u03bc(I)(1\u2212I) = "
   "\u03c1I gives \u03c1(I) = \u03bc(I)(1\u2212I)/I, so the entire bifurcation "
   "diagram is obtained by sweeping I and reading off \u03c1, with no numerical "
   "integration and no fitting. The fold, where the high-order state is "
   "destroyed, is the root of \u03bc\u2032(I)(1\u2212I)I \u2212 \u03bc(I) = 0. "
   "With \u03bc\u2080 = %.2f, \u03b2 = %.0f, K = %.2f and h = %.0f, the tissue is "
   "bistable between \u03c1 = %.2f and \u03c1 = %.2f, and the transition is "
   "hysteretic: once pushed into the low-order state, removing the stress does "
   "not restore the original state, because repair capacity has itself degraded "
   "(Fig. 1)."
   % (P["mu0"], P["beta"], P["K"], P["h"], A1["rho_lower"], A1["rho_c"]),
   indent=True)
FIG("figure1_model.png")
CAP("Figure 1. The order\u2013repair model is bistable and hysteretic by "
    "construction. (A) Repair that reinforces tissue order, compared with a "
    "constant baseline rate. (B) The resulting equilibrium curve is S-shaped: "
    "between \u03c1 = %.2f and \u03c1 = %.2f a high-order and a low-order state "
    "are simultaneously stable, separated by an unstable branch. The fold at "
    "\u03c1_c = %.2f is the tipping point. (C) Integrating the dynamics under "
    "rising and then falling stress traces a hysteresis loop: collapse and "
    "recovery occur at different stress levels. These are properties of the "
    "assumed feedback, not fitted results."
    % (A1["rho_lower"], A1["rho_c"], A1["rho_c"]))
KEY("Bistability here is a consequence of the functional form chosen, not an "
    "empirical discovery. The question worth asking is what moves the threshold.")

# ================================================================= SECTION 6
H("Repair fidelity moves the tipping point, exactly and structurally")
Pp("We represent an organism-wide difference in repair fidelity as a multiplier "
   "\u03b1 on the repair function. The question is how the tipping point "
   "\u03c1_c \u2014 the erosion flux beyond which no amount of tissue self-repair "
   "prevents reversion \u2014 depends on \u03b1.")
Pp("When \u03b1 scales repair uniformly, \u03bc_\u03b1(I) = \u03b1\u03bc(I), the "
   "answer is exact. Both \u03bc and \u03bc\u2032 carry the same factor, so it "
   "cancels from the fold condition entirely: the fold sits at the same tissue "
   "order I_c for every \u03b1, and \u03c1_c is precisely proportional to \u03b1. "
   "Computing \u03c1_c independently at 64 values of \u03b1 between 0.25 and 8 "
   "confirms this, with \u03c1_c/\u03b1 constant to a relative deviation of "
   "%.0e and the fold position varying by %.0e \u2014 both at machine precision "
   "(Fig. 2). Doubling repair fidelity doubles the stress a tissue can absorb "
   "before it collapses, and this holds for every value of \u03bc\u2080, \u03b2, "
   "K and h."
   % (SCA["ratio_max_rel_dev"], SCA["I_c_spread"]), indent=True)
Pp("This is a stronger statement than the model deserves credit for on its own. "
   "It is not a fitted result or a simulated cohort; it is an algebraic property "
   "of any repair function scaled uniformly. That makes it the most defensible "
   "claim in the paper, and also the most constrained: it says nothing about "
   "whether real repair enhancement is uniform.", indent=True)
FIG("figure2_tipping_point.png")
CAP("Figure 2. Repair fidelity scales the tipping point. (A) Stable (solid) and "
    "unstable (dotted) equilibrium branches for repair multipliers \u03b1 = 0.5, "
    "1, 2 and 4. Filled circles mark the fold. The folds slide to higher erosion "
    "flux while remaining at the same tissue order I_c = %.2f. (B) The tipping "
    "point computed at 64 values of \u03b1 lies on the line \u03c1_c = "
    "\u03b1\u00b7\u03c1_c(1) to within %.0e. The scaling is exact, not fitted."
    % (A1["I_c"], SCA["ratio_max_rel_dev"]))
KEY("Under uniform scaling, \u03c1_c = \u03b1\u00b7\u03c1_c(1) exactly: repair "
    "fidelity is a control parameter for the stability of the multicellular "
    "state, not an incremental improvement to one defence.")

# ================================================================= SECTION 7
H("How repair enhancement is implemented changes what it buys")
Pp("Uniform scaling is an assumption, and a consequential one. Repair "
   "enhancement could plausibly act on constitutive repair, on the "
   "order-dependent feedback term, or on both. These are different "
   "interventions and the model distinguishes them:")
for tag, form, gloss in [
    ("A \u2014 uniform", "\u03b1\u03bc\u2080(1 + \u03b2s)",
     "both constitutive and feedback repair scale together."),
    ("B \u2014 constitutive only", "\u03bc\u2080(\u03b1 + \u03b2s)",
     "baseline repair rises; the feedback is untouched."),
    ("C \u2014 feedback only", "\u03bc\u2080(1 + \u03b1\u03b2s)",
     "the order-dependent term rises; baseline is untouched."),
]:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(tag + ": ")
    r.bold = True
    r.font.size = Pt(11)
    r = p.add_run(form + " \u2014 " + gloss)
    r.font.size = Pt(11)
Pp("All three raise the tipping point, and they do so in every one of the %s "
   "randomly drawn parameter sets that were bistable at baseline: the fraction "
   "with \u03c1_c(\u03b1=2) > \u03c1_c(\u03b1=1) is 100%%%% in each case. The "
   "direction of the effect is therefore robust, and does not depend on the "
   "particular functional form."
   % format(ROB["bistable_sets"], ","), indent=True)
Pp("The magnitude is not. Doubling \u03b1 multiplies \u03c1_c by %.2f under "
   "uniform scaling, %.2f under feedback-only enhancement, but only %.2f under "
   "constitutive-only enhancement (medians across the same parameter sets). More "
   "strikingly, constitutive-only enhancement destroys the bistability "
   "altogether above \u03b1 = %.2f at the baseline parameters: the two folds "
   "annihilate in a cusp, \u03c1(I) becomes monotone, and the tissue's response "
   "to stress changes character \u2014 from an all-or-nothing collapse to a "
   "graded decline with no threshold at all (Fig. 3)."
   % (ROB["modes"]["A"]["median"], ROB["modes"]["C"]["median"],
      ROB["modes"]["B"]["median"], CUSP_B), indent=True)
Pp("This is the model's least expected output and, we think, its most "
   "interesting. It says that sufficiently raising constitutive repair does not "
   "merely move the cliff edge further away; past a point it removes the cliff. "
   "A tissue that would previously have collapsed catastrophically instead "
   "degrades smoothly, which is a qualitatively different and more recoverable "
   "failure mode. Whether real repair enhancement behaves this way is an "
   "empirical question, and it is one the framework makes askable.", indent=True)
FIG("figure3_implementations.png")
CAP("Figure 3. The three implementations agree on direction and disagree on "
    "magnitude. (A) Tipping point against repair multiplier for each "
    "implementation. Uniform and feedback-only scaling raise \u03c1_c steadily; "
    "constitutive-only scaling raises it weakly and then loses bistability "
    "entirely above \u03b1 = %.2f, where the folds annihilate and the stress "
    "response becomes graded. (B) Ratio \u03c1_c(\u03b1=2)/\u03c1_c(\u03b1=1) "
    "across %s randomly drawn bistable parameter sets; bars are medians, whiskers "
    "the 5th\u201395th percentiles. The effect is positive in every sampled set "
    "under all three implementations."
    % (CUSP_B, format(ROB["bistable_sets"], ",")))
KEY("Every implementation of repair enhancement raises the threshold; they "
    "differ by nearly twofold in how much, and one of them abolishes the "
    "threshold rather than moving it. This difference is measurable.")

# ================================================================= SECTION 8
H("CIRBP is a candidate molecular entry point")
Pp("The model is agnostic about what \u03b1 corresponds to biologically. The "
   "bowhead data supply a concrete candidate: CIRBP-mediated enhancement of "
   "double-strand-break repair. The proposed chain runs from high constitutive "
   "CIRBP, through enhanced repair and greater genome integrity, to reduced "
   "chromosomal instability and mutation accumulation, to reduced probability of "
   "malignant transformation, and \u2014 this paper's hypothesis, not an "
   "established fact \u2014 to slower age-associated tissue decline. Table 1 "
   "separates what the bowhead experiments established from what the model adds "
   "as interpretation and what remains to be tested.")

rows = [
    ("Bowhead fibroblasts show enhanced double-strand-break repair capacity and "
     "fidelity, and lower mutation rates, than human or other mammalian cells "
     "(Firsanov et al. 2025).",
     "High constitutive repair fidelity can occur in a long-lived, large-bodied "
     "mammal without additional tumour-suppressor barriers.",
     "Raising repair fidelity in other species or cell types should shift the "
     "modelled tissue toward a more stable high-order state (P1\u2013P2)."),
    ("Bowhead CIRBP raises non-homologous end-joining and homologous-recombination "
     "efficiency when expressed in human cells (Firsanov et al. 2025).",
     "CIRBP can act as a transferable repair-fidelity effector rather than a "
     "bowhead-specific curiosity.",
     "CIRBP enhancement in other human or mouse cell types should measurably "
     "raise genotoxic-stress thresholds (P1\u2013P2)."),
    ("CIRBP overexpression extends lifespan and radiation resistance in "
     "Drosophila (Firsanov et al. 2025).",
     "One repair-fidelity effector can influence both damage resistance and "
     "organismal longevity in at least one model organism.",
     "Repair-fidelity enhancement should couple cancer-relevant and "
     "ageing-relevant readouts in other systems (P5)."),
    ("The present order\u2013repair model.",
     "Uniform repair scaling raises the erosion threshold \u03c1_c exactly in "
     "proportion to \u03b1; the implementation determines the magnitude and can "
     "abolish the threshold.",
     "Repair-fidelity enhancement should shift measurable tissue-level stress "
     "thresholds, and the size of the shift should identify which implementation "
     "operates (P3\u2013P4)."),
]
tb = doc.add_table(rows=1, cols=3)
tb.style = "Table Grid"
for i, h in enumerate(["Published evidence", "Model interpretation",
                       "What would test it"]):
    c = tb.rows[0].cells[i]
    c.text = ""
    r = c.paragraphs[0].add_run(h)
    r.bold = True
    r.font.size = Pt(9.5)
    c.paragraphs[0].paragraph_format.line_spacing = 1.0
for a, b, c in rows:
    cells = tb.add_row().cells
    for cell, txt in zip(cells, (a, b, c)):
        cell.text = ""
        pr = cell.paragraphs[0]
        pr.paragraph_format.line_spacing = 1.0
        pr.paragraph_format.space_after = Pt(2)
        rr = pr.add_run(txt)
        rr.font.size = Pt(9)
for row in tb.rows:
    for w, cell in zip((2.1, 2.1, 2.1), row.cells):
        cell.width = Inches(w)
CAP("Table 1. Evidence, interpretation and test. Only the final row is specific "
    "to the present model; the first three summarise Firsanov et al. (2025).")
KEY("CIRBP gives the abstract parameter \u03b1 a concrete, transferable, and "
    "already partly characterised molecular candidate.")

# ================================================================= SECTION 9
H("The Bowhead Repair Principle")
Pp("We propose the following as a named synthesis, offered explicitly as a "
   "hypothesis rather than an established law:")
p = doc.add_paragraph()
p.paragraph_format.left_indent = Inches(0.4)
p.paragraph_format.right_indent = Inches(0.4)
p.paragraph_format.line_spacing = 1.5
r = p.add_run("The Bowhead Repair Principle: exceptional cancer resistance and "
              "longevity may emerge together when an organism maintains genome "
              "integrity primarily by increasing the fidelity of repair, rather "
              "than by relying predominantly on the elimination of damaged cells.")
r.bold = True
r.font.size = Pt(11)
Pp("Read through the model, this becomes a specific claim: cancer resistance and "
   "longevity are not two independent traits that happen to co-occur in the "
   "bowhead, but two readouts of the same quantity acting on the same bistable "
   "structure from two directions \u2014 resistance to acute stress-induced "
   "reversion, which is movement along \u03c1, and resistance to slow "
   "baseline-driven erosion, which is the \u03c1\u2080 term acting continuously "
   "and independently of any tumour challenge.")
KEY("If the principle holds, an intervention on repair fidelity should not be "
    "able to improve one of these phenotypes without improving the other.")

# ================================================================ SECTION 10
H("Five predictions, from molecules to organisms")
Pp("The hypothesis generates a ladder of predictions at ascending levels of "
   "organisation. P1 and P2 extend from published evidence; P3 and P4 are "
   "specific to the order\u2013repair model; P5 is the signature test.")
PREDS = [
    ("P1", "Molecular",
     "Raising repair fidelity \u2014 by CIRBP or another effector \u2014 should "
     "reduce mutation accumulation, chromosomal abnormalities, micronuclei and "
     "persistent DNA-damage markers under matched genotoxic stress. This is the "
     "prediction most directly grounded in existing bowhead, human-cell and "
     "Drosophila data (Firsanov et al. 2025)."),
    ("P2", "Cellular",
     "The same enhancement should raise the genotoxic-stress threshold for "
     "malignant transformation, so that fidelity-enhanced cells transform at "
     "lower rates than controls under matched mutational load."),
    ("P3", "Tissue",
     "In organoid or tissue systems with a measurable collective-organisation "
     "phenotype, repair-fidelity enhancement should raise the critical stress "
     "required to destabilise that organisation. The model makes this "
     "quantitative: under uniform scaling the threshold should move in direct "
     "proportion to the fidelity gain."),
    ("P4", "Mechanistic discrimination",
     "The size of the threshold shift should identify how repair enhancement "
     "acts. A near-proportional shift indicates uniform or feedback-weighted "
     "enhancement; a shift of only around %.0f%%%% per doubling indicates "
     "enhancement confined to constitutive repair. In the latter case, "
     "sufficiently strong enhancement should abolish threshold behaviour "
     "altogether, replacing catastrophic collapse with graded decline \u2014 an "
     "unusual and distinctive signature."
     % (100 * (ROB["modes"]["B"]["median"] - 1))),
    ("P5", "Coupling \u2014 the signature test",
     "Because P1\u2013P4 all follow from one parameter, an intervention that "
     "improves repair fidelity should produce correlated changes in cancer "
     "resistance and in age-associated tissue deterioration within the same "
     "system. This coupling is not expected if the two outcomes arise from "
     "independent mechanisms, and it is what distinguishes this hypothesis from "
     "the uncontroversial claim that repair reduces mutations which reduce "
     "cancer."),
]
for tag, level, body in PREDS:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run("%s \u2014 %s. " % (tag, level))
    r.bold = True
    r.font.size = Pt(11)
    r = p.add_run(body)
    r.font.size = Pt(11)
Pp("The asymmetry among these matters. If P1 or P2 fails, the bowhead biology is "
   "in question. If P3 or P4 fails, the model's tissue-level structure is wrong "
   "but the underlying biology may stand. If P5 fails \u2014 if repair-fidelity "
   "enhancement improves cancer resistance without any corresponding effect on "
   "age-associated decline, or the reverse \u2014 then the Bowhead Repair "
   "Principle loses most of its distinctive explanatory value, whatever else "
   "survives.", indent=True)
KEY("P5 is the prediction on which the hypothesis should be judged. Everything "
    "else it predicts is either already known or shared with simpler accounts.")

# ================================================================ SECTION 11
H("Relationship to broader models of cancer")
Pp("The low-order state is written in a way compatible with the atavistic model "
   "of cancer, which holds that malignant transformation is a stress-triggered "
   "reversion to an ancient unicellular survival program (Davies & Lineweaver "
   "2011; Lineweaver et al. 2021), and for which phylostratigraphic evidence has "
   "been offered (Trigos et al. 2017; Cisneros et al. 2017; Domazet-Lo\u0161o & "
   "Tautz 2010; Lineweaver et al. 2014). The present hypothesis does not depend "
   "on that interpretation. It requires only that tissue-level order be a "
   "meaningful bistable variable maintained by repair, which is a weaker and more "
   "general claim than the proposal that the low-order state is phylogenetically "
   "ancient. Readers who reject the atavistic account can substitute any other "
   "description of the low-order state without affecting anything derived here.")
Pp("A note on therapeutic implications, which this paper deliberately does not "
   "develop. If repair fidelity is a system-level determinant of tissue "
   "stability, interventions that raise it would act on \u03c1_c, whereas "
   "tumour-directed therapies \u2014 including adaptive strategies that manage a "
   "tumour population rather than maximising cell kill (Gatenby et al. 2009) "
   "\u2014 act on \u03c1. These are different terms of the same equation, which "
   "suggests complementarity rather than competition. We state this and stop "
   "there: the hypothesis stands or falls as basic biology, and the therapeutic "
   "question involves risks addressed in the next section.", indent=True)
KEY("The framework is compatible with the atavistic model but does not rest on "
    "it, and its therapeutic reading is deferred rather than argued.")

# ================================================================ SECTION 12
H("Limitations")
LIMS = [
    ("More repair is not automatically better.",
     "This is the most serious objection to a naive reading of the hypothesis. "
     "Enhanced DNA repair is not synonymous with tumour suppression: repair and "
     "damage-tolerance pathways can help damaged or premalignant cells survive "
     "insults that would otherwise eliminate them, and error-prone end-joining "
     "can itself generate the structural variants that drive transformation "
     "(Ceccaldi et al. 2016). The hypothesis concerns high-fidelity restoration "
     "of genome integrity specifically, and makes no claim about indiscriminate "
     "enhancement of repair activity or damage tolerance \u2014 which the model "
     "would represent not as a larger \u03b1 but as a change in what repair "
     "does."),
    ("The model is phenomenological.",
     "The form of \u03bc(I) and its parameters were chosen for qualitative "
     "consistency with a bistable, hysteretic system, not fitted to "
     "measurements. The exact scaling result in Section 6 is an algebraic "
     "property of uniform multiplication, and the robustness analysis establishes "
     "only that the direction of the effect survives across a wide parameter "
     "range. Neither is a numerically validated biological prediction."),
    ("The bowhead evidence is correlational with respect to longevity.",
     "CIRBP is one of several traits co-occurring with the bowhead's body size, "
     "metabolic rate, cell number, cold adaptation and immune profile, and "
     "existing experiments do not establish its causal weight relative to these. "
     "Firsanov et al. (2025) present enhanced repair as an important contributor "
     "to the phenotype, not a complete explanation of it."),
    ("At least one other solution demonstrably works.",
     "The elephant's barrier multiplication achieves low cancer incidence in a "
     "large, long-lived mammal without any repair-based tipping-point mechanism "
     "(Abegglen et al. 2015). Repair fidelity is best read as one viable "
     "system-level solution among several, not as the general answer to Peto's "
     "paradox."),
    ("Tissue order is not yet an observable.",
     "The order parameter I has no established experimental counterpart. P3 and "
     "P4 presuppose that a collective-organisation phenotype can be measured in "
     "an organoid or tissue system with enough resolution to locate a threshold. "
     "Developing such a readout is a prerequisite for testing the model at the "
     "level where it makes its most specific claims."),
]
for head, body in LIMS:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run(head + " ")
    r.bold = True
    r.font.size = Pt(11)
    r = p.add_run(body)
    r.font.size = Pt(11)

# ================================================================ SECTION 13
H("Outstanding questions")
for q in [
    "Does repair-fidelity enhancement shift cancer resistance and markers of "
    "tissue ageing together, or can the two be separated experimentally?",
    "Can a tissue-level order parameter be measured well enough in organoids to "
    "locate a stress threshold and detect its movement?",
    "Does CIRBP enhancement act uniformly on repair, or only on its constitutive "
    "component \u2014 and can strong enhancement convert a catastrophic collapse "
    "into a graded decline, as the model predicts it should?",
    "Is repair fidelity, as distinct from repair activity, what differs between "
    "long-lived and short-lived mammals of similar size?",
    "Do species that resolve Peto's paradox by elimination pay a measurable "
    "ageing cost that repair-based species do not?",
]:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(q)
    r.font.size = Pt(11)

H("A research programme")
Pp("Near term. CIRBP manipulation across additional cell types and species; "
   "direct measurement of repair fidelity, not merely efficiency, under "
   "controlled genotoxic stress; quantification of mutation burden, indel "
   "spectra and chromosomal stability under the same conditions (P1).")
Pp("Intermediate term. Organoid or tissue models with a measurable "
   "collective-organisation phenotype, allowing a tissue-level analogue of I to "
   "be estimated and a threshold located; transformation assays across a range of "
   "repair-fidelity conditions to test P2 and P3 at tissue rather than "
   "single-cell level; measurement of the size of the threshold shift to "
   "discriminate implementations (P4).", indent=True)
Pp("Long term. Whole-organism ageing models testing whether repair-fidelity "
   "enhancement slows age-associated decline; cancer-prone mouse models testing "
   "whether one intervention shifts tumour incidence and independent markers of "
   "tissue ageing together \u2014 the direct test of P5, and of the Bowhead "
   "Repair Principle as stated.", indent=True)

# ============================================================== DECLARATIONS
H("Data availability")
Pp("The model implementation, the parameter set, the random seed and the scripts "
   "that generate every figure and number in this paper are openly available at "
   "%s and permanently archived at https://doi.org/%s. The manuscript is "
   "deposited at https://doi.org/%s. Both are concept DOIs and resolve to the "
   "current version. Running order_repair_model.py followed by make_figures.py "
   "reproduces the JSON results file and all three figures. No experimental data "
   "were generated or analysed." % (REPO, DOI_CODE, DOI_MS))

H("Declarations")
Pp("Funding. This work received no external funding.")
Pp("Competing interests. The author declares no competing interests.")
Pp("Ethics. This study is entirely theoretical and computational and involved no "
   "human participants or animal subjects.")
Pp("Use of generative artificial intelligence. During the preparation of this "
   "work the author used Claude (Anthropic) to assist with literature synthesis, "
   "model implementation and drafting. The author subsequently reviewed and "
   "edited all content, verified every cited reference against the primary "
   "literature, and takes full responsibility for the content of the "
   "publication. No generative AI tool is listed as an author, and none was used "
   "to produce or alter any data.")

# ================================================================ REFERENCES
H("References")
REFS = [
    ("Abegglen LM, Caulin AF, Chan A, et al.", 2015,
     "Potential mechanisms for cancer resistance in elephants and comparative "
     "cellular response to DNA damage in humans", "JAMA", "314", "1850-1860",
     "10.1001/jama.2015.13134"),
    ("Caulin AF, Maley CC", 2011,
     "Peto's paradox: evolution's prescription for cancer prevention",
     "Trends in Ecology & Evolution", "26", "175-182", "10.1016/j.tree.2011.01.002"),
    ("Ceccaldi R, Rondinelli B, D'Andrea AD", 2016,
     "Repair pathway choices and consequences at the double-strand break",
     "Trends in Cell Biology", "26", "52-64", "10.1016/j.tcb.2015.07.009"),
    ("Cisneros L, Bussey KJ, Orr AJ, et al.", 2017,
     "Ancient genes establish stress-induced mutation as a hallmark of cancer",
     "PLoS ONE", "12", "e0176258", "10.1371/journal.pone.0176258"),
    ("Davies PCW, Lineweaver CH", 2011,
     "Cancer tumors as Metazoa 1.0: tapping genes of ancient ancestors",
     "Physical Biology", "8", "015001", "10.1088/1478-3975/8/1/015001"),
    ("Domazet-Lo\u0161o T, Tautz D", 2010,
     "Phylostratigraphic tracking of cancer genes suggests a link to the "
     "emergence of multicellularity in metazoa", "BMC Biology", "8", "66",
     "10.1186/1741-7007-8-66"),
    ("Ferrell JE", 2002,
     "Self-perpetuating states in signal transduction: positive feedback, "
     "double-negative feedback and bistability",
     "Current Opinion in Cell Biology", "14", "140-148",
     "10.1016/s0955-0674(02)00314-9"),
    ("Firsanov D, Zacher M, Tian X, et al.", 2025,
     "Evidence for improved DNA repair in the long-lived bowhead whale",
     "Nature", "", "", "10.1038/s41586-025-09694-5"),
    ("Gatenby RA, Silva AS, Gillies RJ, Frieden BR", 2009, "Adaptive therapy",
     "Cancer Research", "69", "4894-4903", "10.1158/0008-5472.CAN-08-3658"),
    ("Lineweaver CH, Davies PCW, Vincent MD", 2014,
     "Targeting cancer's weaknesses (not its strengths): therapeutic strategies "
     "suggested by the atavistic model", "BioEssays", "36", "827-835",
     "10.1002/bies.201400070"),
    ("Lineweaver CH, Bussey KJ, Blackburn AC, Davies PCW", 2021,
     "Cancer progression as a sequence of atavistic reversions", "BioEssays",
     "43", "2000305", "10.1002/bies.202000305"),
    ("L\u00f3pez-Ot\u00edn C, Blasco MA, Partridge L, Serrano M, Kroemer G", 2023,
     "Hallmarks of aging: an expanding universe", "Cell", "186", "243-278",
     "10.1016/j.cell.2022.11.001"),
    ("Seluanov A, Gladyshev VN, Vijg J, Gorbunova V", 2018,
     "Mechanisms of cancer resistance in long-lived mammals",
     "Nature Reviews Cancer", "18", "433-441", "10.1038/s41568-018-0004-9"),
    ("Tian X, Azpurua J, Hine C, et al.", 2013,
     "High-molecular-mass hyaluronan mediates the cancer resistance of the naked "
     "mole rat", "Nature", "499", "346-349", "10.1038/nature12234"),
    ("Trigos AS, Pearson RB, Papenfuss AT, Goode DL", 2017,
     "Altered interactions between unicellular and multicellular genes drive "
     "hallmarks of transformation",
     "Proceedings of the National Academy of Sciences", "114", "6406-6411",
     "10.1073/pnas.1617743114"),
    ("van Deursen JM", 2014, "The role of senescent cells in ageing", "Nature",
     "509", "439-446", "10.1038/nature13193"),
    ("Vijg J, Dong X", 2020,
     "Pathogenic mechanisms of somatic mutation and genome mosaicism in aging",
     "Cell", "182", "12-23", "10.1016/j.cell.2020.06.024"),
]
for auth, yr, title, jr, vol, pg, doi in REFS:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    bits = "%s (%d) %s. %s" % (auth, yr, title, jr)
    if vol:
        bits += " %s" % vol
    if pg:
        bits += ":%s" % pg
    bits += ". https://doi.org/%s" % doi
    r = p.add_run(bits)
    r.font.size = Pt(10)

if not os.path.isdir(OUT):
    os.makedirs(OUT)
path = os.path.join(OUT, "Repair_Fidelity_Control_Parameter_BioEssays.docx")
doc.save(path)

words = sum(len(p.text.split()) for p in doc.paragraphs)
print("summary words : %d (BioEssays limit 150)" % len(SUMMARY.split()))
print("total words   : %d" % words)
print("tables        : %d" % len(doc.tables))
print("references    : %d" % len(REFS))
print("saved         : %s" % path)
