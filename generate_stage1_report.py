#!/usr/bin/env python3
"""Generate the audited PDF report for the MH370 00:11 stage-1 estimator."""

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_stage1_0011"
PDF = OUT / "MH370_stage1_integrated_estimate_through_0011Z.pdf"

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Oblique", boldItalic="DejaVu-BoldOblique")

summary = pd.read_csv(OUT / "stage1_summary.csv")
hyp = pd.read_csv(OUT / "control_family_hypothesis_tests.csv")
sens = pd.read_csv(OUT / "sensitivity_summary.csv")
terminal = pd.read_csv(OUT / "terminal_scenario_summary.csv")

primary = summary[summary["case"] == "Primary equal-control priors"].set_index("estimate")
air = primary.loc["00:11 airborne"]
impact = primary.loc["Impact after model-averaged drift"]
ph = hyp[hyp["case"] == "Primary equal-control priors"].copy()
pt = terminal[terminal["case"] == "Primary equal-control priors"].copy()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleMH", parent=styles["Title"], fontName="DejaVu-Bold", fontSize=22,
                          leading=25, textColor=colors.HexColor("#0B1F33"), alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="SubTitleMH", parent=styles["Normal"], fontName="DejaVu", fontSize=10.5, leading=14,
                          textColor=colors.HexColor("#425466"), alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="H1MH", parent=styles["Heading1"], fontName="DejaVu-Bold", fontSize=16,
                          leading=19, textColor=colors.HexColor("#12355B"), spaceBefore=6, spaceAfter=8))
styles.add(ParagraphStyle(name="H2MH", parent=styles["Heading2"], fontName="DejaVu-Bold", fontSize=12,
                          leading=15, textColor=colors.HexColor("#2C7A7B"), spaceBefore=5, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyMH", parent=styles["BodyText"], fontName="DejaVu", fontSize=9.5, leading=13, spaceAfter=6))
styles.add(ParagraphStyle(name="SmallMH", parent=styles["BodyText"], fontName="DejaVu", fontSize=8, leading=10, textColor=colors.HexColor("#4B5563")))
styles.add(ParagraphStyle(name="CalloutMH", parent=styles["BodyText"], fontName="DejaVu", fontSize=10.5, leading=14,
                          backColor=colors.HexColor("#EAF1F8"), borderColor=colors.HexColor("#9BB7D4"),
                          borderWidth=0.7, borderPadding=7, spaceBefore=4, spaceAfter=8))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D6DEE8"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(18 * mm, 9 * mm, "MH370 stage-1 integrated estimate — observations through 00:11 UTC")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(str(PDF), pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm,
                      topMargin=15 * mm, bottomMargin=18 * mm, title="MH370 Stage-1 Integrated Bayesian Estimate")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=footer)])


def P(text, style="BodyMH"):
    return Paragraph(text, styles[style])


def styled_table(data, widths, header=True, number_align_cols=()):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.2),
        ("LEADING", (0, 0), (-1, -1), 10.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D4E1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for col in number_align_cols:
        commands.append(("ALIGN", (col, 1), (col, -1), "RIGHT"))
    t.setStyle(TableStyle(commands))
    return t


story = []
story += [P("MH370 Stage-1 Integrated Bayesian Estimate", "TitleMH"),
          P("Airborne observations through 00:11 UTC; 00:19 data deliberately excluded", "SubTitleMH")]

story.append(P(
    "<b>Outcome.</b> The integrated impact posterior has a 2-D mode at "
    f"<b>{abs(impact.mode_lat_deg):.2f}°S, {impact.mode_lon_deg_E:.2f}°E</b>. "
    f"Its marginal median is {abs(impact.median_lat_deg):.2f}°S, {impact.median_lon_deg_E:.2f}°E, "
    f"with a 95% latitude interval of {abs(impact.lat_95_high):.2f}°S–{abs(impact.lat_95_low):.2f}°S. "
    "This is a probability region, not a declared crash point.", "CalloutMH"))

key = [
    ["Estimate", "2-D mode", "Median", "95% latitude interval", "P(south of 36°S)"],
    ["00:11 airborne", f"{abs(air.mode_lat_deg):.2f}°S, {air.mode_lon_deg_E:.2f}°E",
     f"{abs(air.median_lat_deg):.2f}°S, {air.median_lon_deg_E:.2f}°E",
     f"{abs(air.lat_95_high):.2f}°S–{abs(air.lat_95_low):.2f}°S", f"{air.prob_south_of_36S:.1%}"],
    ["Impact after drift average", f"{abs(impact.mode_lat_deg):.2f}°S, {impact.mode_lon_deg_E:.2f}°E",
     f"{abs(impact.median_lat_deg):.2f}°S, {impact.median_lon_deg_E:.2f}°E",
     f"{abs(impact.lat_95_high):.2f}°S–{abs(impact.lat_95_low):.2f}°S", f"{impact.prob_south_of_36S:.1%}"],
]
story.append(styled_table(key, [35 * mm, 34 * mm, 37 * mm, 40 * mm, 28 * mm]))
story.append(Spacer(1, 5 * mm))
story.append(Image(str(OUT / "mh370_stage1_integrated_impact_heatmap.png"), width=174 * mm, height=136 * mm))
story.append(P("Yellow and white contours enclose 50% and 90% highest-posterior-density regions. The dashed cyan contour is the 00:11 airborne 50% region. The star marks the impact-density mode.", "SmallMH"))

story.append(PageBreak())
story.append(P("1. Model architecture and conditioning", "H1MH"))
story.append(P(
    "The model conditions the airborne state only on data available through 00:11. It then integrates over terminal-flight and ocean-drift uncertainty to obtain an impact-location posterior. In compact form:", "BodyMH"))
story.append(P(
    "<i>p</i>(x<sub>I</sub>|D≤00:11, debris) ∝ ∫ <i>p</i><sub>SAT/RF</sub>(x<sub>7</sub>|D≤00:11) "
    "<i>p</i><sub>perf</sub>(x<sub>7</sub>) <i>p</i>(x<sub>I</sub>|x<sub>7</sub>,H<sub>EOF</sub>) "
    "Σ<sub>m</sub> π<sub>m</sub><i>p</i><sub>m</sub>(debris|x<sub>I</sub>) dx<sub>7</sub> dH<sub>EOF</sub>.", "CalloutMH"))

architecture = [
    ["Layer", "Treatment in this stage"],
    ["Radar / initial dynamics", "Inherited refined prior at 18:01:49 and evidence of no turn through 18:22; stochastic trajectory model continues to 00:11."],
    ["BTO", "All regular post-radar BTOs through 00:11; altitude-dependent first-order slant-range correction for added low-altitude states."],
    ["BFO", "Correlated-bias refined likelihood through 00:11. Active vertical speed adds 0.009 Hz/fpm with effective σ=12 Hz; 8 and 18 Hz are tested."],
    ["Received power", "Refined 3-D AES gain likelihood with gain-precompensation survival coefficient marginalized from independent calibration."],
    ["Aircraft performance", "Mach/altitude/speed feasibility, M0.84 ceiling, stochastic wind allowance, low-level/descent distance loss, and broad remaining-fuel time."],
    ["Control at 00:11", "Equal prior weights for high/near-level, an earlier completed descent at lower altitude, and active controlled descent."],
    ["Terminal flight", "Equal prior weights for controlled descent/ditch, fuel exhaustion plus controlled glide, and fuel exhaustion plus short uncontrolled descent."],
    ["Ocean drift", "50:50 average of a smooth Davey Fig. 11.2 likelihood and the broad 12-study drift meta-analysis; normalized before averaging, not multiplied."],
]
story.append(styled_table([[P(c, "SmallMH") for c in row] for row in architecture], [42 * mm, 132 * mm]))
story.append(Spacer(1, 4 * mm))
story.append(P("What is not conditioned on", "H2MH"))
story.append(P(
    "The 00:19 BTO, BFO, log-on and received-power values do not enter this stage. A trajectory may be controlled before or after 00:11 and may remain airborne after 00:19. The retained sample's airborne-at-00:19 fraction is reported only as a prior-predictive diagnostic.", "BodyMH"))
story.append(P(
    "The drift likelihood is applied to the propagated impact state, not to the 00:11 arc. This prevents debris evidence from being incorrectly interpreted as evidence about the airborne arc point itself.", "BodyMH"))

story.append(PageBreak())
story.append(P("2. Control and descent hypothesis tests", "H1MH"))
story.append(P(
    "The test starts with equal prior weights. It asks whether the combined satellite/RF and performance evidence distinguishes the three 00:11 control families. All three can represent a human-controlled aircraft; the labels concern altitude and vertical motion, not pilot presence.", "BodyMH"))

ht = [["00:11 family", "Prior", "Posterior", "BF vs comp.", "Mean altitude", "Mean |v-rate|"]]
for _, r in ph.iterrows():
    ht.append([r.family, f"{r.prior_probability:.1%}", f"{r.posterior_probability:.1%}",
               f"{r.Bayes_factor_vs_complement:.2f}", f"{r.mean_altitude_ft_posterior:,.0f} ft",
               f"{r.mean_abs_vertical_rate_fpm_posterior:,.0f} fpm"])
story.append(styled_table(ht, [51 * mm, 18 * mm, 20 * mm, 24 * mm, 33 * mm, 29 * mm], number_align_cols=(1, 2, 3, 4, 5)))
story.append(Spacer(1, 4 * mm))
story.append(P(
    "<b>Test result.</b> High-altitude/near-level flight rises from 33.3% to 50.8% (BF 2.06 versus its complement). "
    "An earlier completed descent retains 24.9%, and active controlled descent retains 24.3%. Their individual Bayes factors, 0.66 and 0.64, are only weak evidence against them. "
    "Therefore the 00:11 data do not justify excluding either a lower-altitude state or an active controlled descent.", "CalloutMH"))
story.append(Image(str(OUT / "mh370_stage1_latitude_marginals.png"), width=174 * mm, height=103 * mm))
story.append(P(
    "Terminal propagation moves and broadens the latitude density because the primary heading is southerly. The model-averaged drift evidence then shifts the median impact latitude north by about 0.22° relative to the no-drift impact distribution.", "SmallMH"))

story.append(PageBreak())
story.append(P("3. Terminal flight, glide and sensitivity", "H1MH"))
tt = [["Terminal scenario", "Prior", "Posterior", "Median nmi", "95th pct nmi", "P(airborne 00:19)*"]]
for _, r in pt.iterrows():
    short_scenario = {
        "Controlled descent/ditch (power if available)": "Controlled descent/ditch",
        "Fuel exhaustion + controlled glide": "EOF + controlled glide",
        "Fuel exhaustion + short uncontrolled descent": "EOF + short uncontrolled descent",
    }[r.terminal_scenario]
    tt.append([short_scenario, f"{r.prior_probability:.1%}", f"{r.posterior_probability_after_drift:.1%}",
               f"{r.median_terminal_distance_nm:.1f} nmi", f"{r.q95_terminal_distance_nm:.1f} nmi",
               f"{r.probability_airborne_at_0019_29:.1%}"])
story.append(styled_table(tt, [54 * mm, 17 * mm, 25 * mm, 25 * mm, 25 * mm, 29 * mm], number_align_cols=(1, 2, 3, 4, 5)))
story.append(P("*Diagnostic only; 00:19 evidence is not used. The aggregate prior-predictive probability is about 72%.", "SmallMH"))
story.append(Spacer(1, 3 * mm))
story.append(P(
    "Controlled glide range is altitude-scaled with L/D uniformly distributed from 12 to 18, plus a broad along-track wind term. "
    "This includes the approximately 100 nmi human-controlled glide scale discussed by Davey et al.; powered distance before exhaustion can make total terminal displacement larger.", "BodyMH"))

st = [["Sensitivity case", "Mode", "Median lat.", "95% latitude interval", "P(south of 36°S)"]]
for _, r in sens.iterrows():
    st.append([r.case, f"{abs(r.impact_mode_lat_deg):.2f}°S, {r.impact_mode_lon_deg_E:.2f}°E",
               f"{abs(r.impact_median_lat_deg):.3f}°S",
               f"{abs(r.impact_lat_95_high):.2f}°S–{abs(r.impact_lat_95_low):.2f}°S",
               f"{r.prob_south_of_36S:.1%}"])
story.append(P("Sensitivity of the integrated impact posterior", "H2MH"))
story.append(styled_table(st, [43 * mm, 35 * mm, 27 * mm, 42 * mm, 27 * mm], number_align_cols=(1, 2, 3, 4)))
story.append(Spacer(1, 4 * mm))
story.append(P(
    "Across the tested control priors, BFO vertical-error scales, and drift-model weights, the median impact latitude spans only 0.15°. "
    "The 2-D mode spans about 0.33° latitude and 0.15° longitude. This is much smaller than the posterior's terminal-flight width, so the result is stable to these specified perturbations but still sensitive to untested terminal-control priors.", "CalloutMH"))

story.append(PageBreak())
story.append(P("4. Interpretation, limitations and reproducibility", "H1MH"))
story.append(P("What this run supports", "H2MH"))
for text in [
    "A southern high-density impact region centered near 37.3°S, 89.2°E under the declared stage-1 priors.",
    "A meaningful northern secondary component near roughly 35°S and 92–93°E; it should not be discarded merely because it is not the global mode.",
    "Only weak evidence favoring high/near-level flight over lower-altitude or actively descending controlled flight at 00:11.",
    "A weak debris-drift update: it shifts and reweights the terminal distribution but does not overwhelm the satellite/RF likelihood.",
]:
    story.append(P("• " + text, "BodyMH"))

story.append(P("Important limitations", "H2MH"))
limitations = [
    ["Limitation", "Consequence"],
    ["Refined particle checkpoint absent", "The reported multimodal 00:11 posterior was reconstructed from its summary. Exact particle-level correlations between location, Mach, heading, gain and BFO bias are unavailable."],
    ["Exact ACCESS-G March 2014 fields absent", "The inherited stochastic wind-error model and a broad terminal wind term are used; this is not a numerical reanalysis-weather rerun."],
    ["Fuel workbook not coupled cell-by-cell", "The run uses the workbook's performance domain, a Mach/distance feasibility likelihood and a broad remaining-endurance prior. A later run should directly couple fuel mass, engine state and descent schedule."],
    ["Vertical-BFO coefficient uncertain", "A conservative effective likelihood is used and stress-tested. A full 3-D Doppler rerun could alter active-descent odds."],
    ["Drift likelihood partly digitized", "Davey Fig. 11.2 is represented by a smooth relative surface; the meta-analysis supplies a second broad model. Equal weights are a declared choice, not learned from independent validation."],
    ["Terminal-control prior dominates width", "Forward-biased versus arbitrary turns, glide utilization and ditching strategy are not identifiable from data through 00:11. The heat map must remain broad."],
]
story.append(styled_table([[P(c, "SmallMH") for c in row] for row in limitations], [48 * mm, 126 * mm]))

story.append(P("Reproducibility package", "H2MH"))
story.append(P(
    "The accompanying workbook contains linked summaries, hypothesis tests, terminal scenarios, sensitivities, assumptions and source limitations. "
    "The Python program, run manifest, CSV posterior samples and random seed 3,700,011 reproduce the computation. The main run uses 900,000 augmented airborne states and 1.2 million terminal propagations per sensitivity case.", "BodyMH"))

story.append(P("Project sources used", "H2MH"))
sources = [
    "Refined v3 00:11 SMC notes, summary, heat map and measurement ledger.",
    "Davey, Gordon, Holland, Rutten and Williams, <i>Bayesian Methods in the Search for MH370</i> (pre-publication draft, 2015), especially Chapters 7, 10 and 11.",
    "Project dissertation, <i>A Meta Analysis of Geospatial Estimates in the Case of Malaysian Airlines Flight MH370</i>, ocean-drift subgroup (Q=6.55, p=0.83, mean 30.2°S).",
    "9M-MRO Fuel Model V5.X, B777-200ER / RR Trent 892B performance and endurance workbook.",
]
for s in sources:
    story.append(P("• " + s, "SmallMH"))

doc.build(story)
print(PDF)
