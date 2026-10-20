#!/usr/bin/env python3
"""Build a visual storyboard of candidate received-power figures for the MH370 paper.

The output is deliberately a design-selection packet.  MH371 phase values shown in
the thumbnails are taken from the project calibration data; the gain lobes and
posterior shapes are schematic previews that will be regenerated from the full
models after a visual direction is selected.
"""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "output" / "pdf"
GRAPHICS_DIR = ROOT / "output" / "graphics"
PDF_DIR.mkdir(parents=True, exist_ok=True)
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

STORYBOARD_PDF = PDF_DIR / "MH370_received_power_graphics_storyboard.pdf"
CONTACT_PDF = PDF_DIR / "MH370_received_power_graphics_contact_sheet.pdf"
OPTIONS_MD = GRAPHICS_DIR / "MH370_received_power_graphics_options.md"
AIRCRAFT_IMAGE = ROOT / "generated_images" / "exec-b362cfd4-2f33-47e5-88a0-e81baf2607ab.png"

FONT_REG = "DejaVu"
FONT_BOLD = "DejaVu-Bold"
for name, path in [
    (FONT_REG, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    (FONT_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]:
    if Path(path).exists():
        pdfmetrics.registerFont(TTFont(name, path))


NAVY = HexColor("#17324D")
INK = HexColor("#1D2935")
BLUE = HexColor("#2B78B8")
CYAN = HexColor("#58B7D7")
GOLD = HexColor("#E7A93B")
ORANGE = HexColor("#E8753D")
PLUM = HexColor("#6D5A9A")
GREEN = HexColor("#2E8B74")
RED = HexColor("#C75050")
PALE = HexColor("#F4F7FA")
MID = HexColor("#D9E2EA")
GREY = HexColor("#647687")
LIGHT_GREY = HexColor("#E9EEF2")
WHITE = colors.white

GROUP_COLOURS = {
    "Geometry": BLUE,
    "Gain": PLUM,
    "Attitude": ORANGE,
    "MH371": GREEN,
    "Inference": NAVY,
}


OPTIONS = [
    dict(n=1, group="Geometry", title="Perspective geometry triad", kind="hero_triad", rec=True,
         story="Toward, broadside and away at low satellite elevation, with the side-mounted arrays called out.",
         use="Opening figure; immediate intuition", status="EXPLAIN + MODEL"),
    dict(n=2, group="Geometry", title="Rotate the aircraft, hold the satellite fixed", kind="rotate_aircraft",
         story="Three headings at one ground point isolate why heading—not position alone—changes antenna gain.",
         use="Opening alternative / animation", status="EXPLAIN"),
    dict(n=3, group="Geometry", title="Aircraft-space coordinate frame", kind="axes",
         story="Defines relative azimuth and elevation, body axes, attitude and the satellite line-of-sight vector.",
         use="Technical inset beside equations", status="EXPLAIN + DEFINITIONS"),
    dict(n=4, group="Geometry", title="Same map position, different received power", kind="same_position",
         story="A plan-view counterexample: identical aircraft and satellite positions, but different headings and gains.",
         use="General-reader bridge", status="EXPLAIN"),
    dict(n=5, group="Geometry", title="Port/starboard antenna hand-off", kind="handoff",
         story="Shows the two canted side arrays and which panel supplies the larger gain as the look direction moves.",
         use="Hardware/geometry explanation", status="EXPLAIN + MODEL"),
    dict(n=6, group="Geometry", title="Horizon compass of strong and weak sectors", kind="compass",
         story="A top-down coverage ring makes the low-elevation nose/tail weakness visible without a 3-D surface.",
         use="Compact main-text alternative", status="MODEL"),

    dict(n=7, group="Gain", title="Twin gain lobes mounted on the airframe", kind="mounted_lobes",
         story="An aircraft carries the two directional gain volumes, connecting the side-mounted hardware to the pattern.",
         use="Hero alternative / graphical abstract", status="EXPLAIN + MODEL"),
    dict(n=8, group="Gain", title="3-D gain hemisphere", kind="gain_hemisphere", rec=True,
         story="A colour-coded upper-hemisphere surface shows broadside maxima and low-elevation nose/tail valleys.",
         use="Primary gain-pattern figure", status="MODEL"),
    dict(n=9, group="Gain", title="Polar slices at several elevations", kind="polar_slices",
         story="Azimuthal gain curves at 0°, 15°, 30° and 45° elevation improve the dissertation's two-slice plot.",
         use="Quantitative main or supplement", status="MODEL + DATA"),
    dict(n=10, group="Gain", title="Elevation–azimuth gain heat map", kind="gain_heatmap",
         story="A rectangular aircraft-space map is easiest for readers to query and for particles to interpolate.",
         use="Methods figure / model validation", status="MODEL + DATA"),
    dict(n=11, group="Gain", title="Beam steering and scan loss", kind="scan_loss",
         story="A three-step diagram follows the beam from boresight toward the array edge as peak gain falls.",
         use="Phased-array explainer", status="EXPLAIN"),
    dict(n=12, group="Gain", title="Boresight-to-horizon gain profile", kind="gain_profile",
         story="A single annotated curve turns the 3-D pattern into the one-dimensional quantity used in the link budget.",
         use="Compact quantitative inset", status="MODEL + DATA"),

    dict(n=13, group="Attitude", title="Pitch–bank–yaw coverage matrix", kind="attitude_matrix", rec=True,
         story="Small multiples show how the same spacecraft direction moves across the gain map under attitude changes.",
         use="Controlled/unusual-flight discussion", status="MODEL"),
    dict(n=14, group="Attitude", title="Bank-angle sweep", kind="bank_sweep",
         story="A continuous sweep shows when a low-elevation spacecraft enters a strong lobe, weak sector or hand-off region.",
         use="Sensitivity figure", status="MODEL"),
    dict(n=15, group="Attitude", title="Climb and descent sweep", kind="pitch_sweep",
         story="Contrasts level flight, descent and climb without conflating flight-path angle with aircraft-space elevation.",
         use="Controlled-flight scenario inset", status="MODEL"),
    dict(n=16, group="Attitude", title="Normal versus unusual attitude sky domes", kind="sky_domes",
         story="Two hemispheres compare routine cruise coverage with a steep bank/pitch case, including no-coverage regions.",
         use="End-of-flight caveat / supplement", status="MODEL"),
    dict(n=17, group="Attitude", title="Coverage ribbon through a controlled turn", kind="turn_ribbon",
         story="A route ribbon is coloured by predicted gain while heading and bank evolve through a turn.",
         use="Trajectory-model integration", status="MODEL + TRAJECTORY"),
    dict(n=18, group="Attitude", title="Operational envelope and edge cases", kind="envelope",
         story="A two-panel map separates well-constrained normal-attitude behaviour from extrapolative unusual attitudes.",
         use="Uncertainty disclosure", status="MODEL + UNCERTAINTY"),

    dict(n=19, group="MH371", title="MH371 route as a natural experiment", kind="mh371_map", rec=True,
         story="The route map marks 01:55, 03:21 and 03:29, where heading changes produced large predicted gain changes.",
         use="Primary validation figure", status="DATA"),
    dict(n=20, group="MH371", title="Three matched geometry snapshots", kind="mh371_snapshots",
         story="At each phase, a plane, line of sight, heading, predicted gain and path-corrected power are shown together.",
         use="General-reader validation figure", status="DATA + MODEL"),
    dict(n=21, group="MH371", title="Time-aligned heading, gain and power", kind="time_series",
         story="Stacked traces show whether received-power changes occur where the geometry model predicts them.",
         use="Technical validation figure", status="DATA + MODEL"),
    dict(n=22, group="MH371", title="Same-channel counterfactual test", kind="counterfactual", rec=True,
         story="The three phase means are compared with complete, partial and zero gain-precompensation predictions.",
         use="Core hypothesis-test figure", status="DATA + INFERENCE"),
    dict(n=23, group="MH371", title="Observed change versus predicted gain change", kind="delta_plot",
         story="A change-on-change plot removes the arbitrary power intercept and makes agreement or attenuation visible.",
         use="Robustness / supplement", status="DATA + INFERENCE"),
    dict(n=24, group="Inference", title="Gain-precompensation coefficient β", kind="beta_dial", rec=True,
         story="A visual continuum links β=0 (complete compensation), the estimate, and β=1 (none).",
         use="Hypothesis-test summary", status="INFERENCE"),

    dict(n=25, group="Inference", title="End-to-end received-power chain", kind="link_chain",
         story="A left-to-right link budget separates AES gain, space loss, satellite/ground terms and recorded power.",
         use="Methods overview", status="EXPLAIN + MODEL"),
    dict(n=26, group="Inference", title="Causal graph and nuisance separation", kind="causal",
         story="Geometry drives gain; channel, path, terminal control and slower RF offsets also influence the observation.",
         use="Statistical-model architecture", status="INFERENCE + MODEL"),
    dict(n=27, group="Inference", title="How power intersects the BTO/BFO solution", kind="likelihood", rec=True,
         story="Layered likelihood ridges show power narrowing—but not independently locating—the satellite-constrained path.",
         use="Integrated-estimator explanation", status="INFERENCE"),
    dict(n=28, group="Inference", title="Posterior before and after received power", kind="posterior_compare", rec=True,
         story="Side-by-side 00:11 maps reveal which modes are reweighted when the received-power likelihood is added.",
         use="Results figure", status="INFERENCE + DATA"),
]


def set_font(c: canvas.Canvas, bold: bool, size: float):
    c.setFont(FONT_BOLD if bold else FONT_REG, size)


def text_width(text: str, size: float, bold: bool = False) -> float:
    return pdfmetrics.stringWidth(text, FONT_BOLD if bold else FONT_REG, size)


def wrapped_lines(text: str, width: float, size: float, bold: bool = False, max_lines: int | None = None):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        candidate = word if not cur else cur + " " + word
        if text_width(candidate, size, bold) <= width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_width(lines[-1] + "…", size, bold) > width:
            lines[-1] = lines[-1][:-1]
        if lines:
            lines[-1] += "…"
    return lines


def draw_wrapped(c, text, x, y_top, width, size, leading=None, colour=INK, bold=False, max_lines=None):
    leading = leading or size * 1.25
    c.setFillColor(colour)
    set_font(c, bold, size)
    lines = wrapped_lines(text, width, size, bold, max_lines)
    y = y_top
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def arrow(c, x1, y1, x2, y2, colour=BLUE, width=1.4, head=5, dashed=False):
    c.setStrokeColor(colour)
    c.setFillColor(colour)
    c.setLineWidth(width)
    if dashed:
        c.setDash(4, 3)
    else:
        c.setDash()
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    pts = [
        (x2, y2),
        (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45)),
        (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45)),
    ]
    p = c.beginPath()
    p.moveTo(*pts[0]); p.lineTo(*pts[1]); p.lineTo(*pts[2]); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setDash()


def draw_satellite(c, x, y, scale=1.0):
    c.setStrokeColor(NAVY); c.setFillColor(GOLD); c.setLineWidth(0.8)
    c.rect(x - 5*scale, y - 4*scale, 10*scale, 8*scale, fill=1, stroke=1)
    c.setFillColor(CYAN)
    c.rect(x - 15*scale, y - 4*scale, 8*scale, 8*scale, fill=1, stroke=1)
    c.rect(x + 7*scale, y - 4*scale, 8*scale, 8*scale, fill=1, stroke=1)
    c.setStrokeColor(NAVY)
    c.line(x, y - 4*scale, x, y - 10*scale)
    c.circle(x, y - 12*scale, 3*scale, fill=0, stroke=1)


def draw_plane(c, cx, cy, length=55, heading=0, fill=WHITE, stroke=NAVY, accent=GOLD, alpha=1.0):
    """Simple top-view aircraft; heading 0 points upward."""
    c.saveState()
    c.translate(cx, cy)
    c.rotate(-heading)
    c.setLineWidth(0.8)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    # Wings, tailplane, fuselage and fin.
    p = c.beginPath()
    p.moveTo(-3, -8); p.lineTo(-0.42*length, -2); p.lineTo(-0.45*length, 2)
    p.lineTo(-4, 8); p.lineTo(4, 8); p.lineTo(0.45*length, 2)
    p.lineTo(0.42*length, -2); p.lineTo(3, -8); p.close()
    c.drawPath(p, fill=1, stroke=1)
    p = c.beginPath()
    p.moveTo(-2.5, -0.33*length); p.lineTo(-0.17*length, -0.42*length)
    p.lineTo(-0.16*length, -0.46*length); p.lineTo(-2, -0.40*length)
    p.lineTo(2, -0.40*length); p.lineTo(0.16*length, -0.46*length)
    p.lineTo(0.17*length, -0.42*length); p.lineTo(2.5, -0.33*length); p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.roundRect(-3.7, -0.40*length, 7.4, 0.78*length, 3.5, fill=1, stroke=1)
    p = c.beginPath(); p.moveTo(-3.7, 0.38*length); p.lineTo(0, 0.49*length); p.lineTo(3.7, 0.38*length); p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(accent)
    c.circle(-4.4, 0.18*length, 1.7, fill=1, stroke=0)
    c.circle(4.4, 0.18*length, 1.7, fill=1, stroke=0)
    c.restoreState()


def label(c, text, x, y, size=6.4, colour=INK, bold=False, align="left"):
    c.setFillColor(colour); set_font(c, bold, size)
    if align == "center": c.drawCentredString(x, y, text)
    elif align == "right": c.drawRightString(x, y, text)
    else: c.drawString(x, y, text)


def gain_value(az_deg: float, el_deg: float) -> float:
    """Schematic dual 45-degree-canted side-array gain surface."""
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    u = (math.cos(el)*math.cos(az), math.cos(el)*math.sin(az), math.sin(el))
    s = math.sqrt(0.5)
    normals = [(0, s, s), (0, -s, s)]
    best = max(sum(a*b for a, b in zip(u, n)) for n in normals)
    theta = math.acos(max(-1.0, min(1.0, best)))
    gain = 14.5 - 9.5 * (math.sin(theta) ** 8)
    return max(4.8, min(14.5, gain))


def heat_colour(v, vmin=5.0, vmax=14.5):
    t = max(0, min(1, (v-vmin)/(vmax-vmin)))
    stops = [(0.0, NAVY), (0.35, BLUE), (0.62, CYAN), (0.82, GOLD), (1.0, ORANGE)]
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        if a <= t <= b:
            f = (t-a)/(b-a)
            return colors.Color(ca.red+(cb.red-ca.red)*f, ca.green+(cb.green-ca.green)*f, ca.blue+(cb.blue-ca.blue)*f)
    return ORANGE


def axes_box(c, x, y, w, h):
    c.setStrokeColor(GREY); c.setLineWidth(0.6)
    c.line(x, y, x+w, y); c.line(x, y, x, y+h)


def thumb_hero_triad(c, x, y, w, h):
    if AIRCRAFT_IMAGE.exists():
        # A single clean perspective airframe establishes the editorial style.
        c.drawImage(ImageReader(str(AIRCRAFT_IMAGE)), x+2, y+4, width=w*0.55, height=h-8,
                    preserveAspectRatio=True, anchor="c", mask="auto")
    else:
        draw_plane(c, x+w*0.25, y+h*0.52, 52, 35)
    draw_satellite(c, x+w*0.86, y+h*0.78, 0.75)
    arrow(c, x+w*0.76, y+h*0.72, x+w*0.53, y+h*0.58, GOLD, 2.0, 6)
    # Three small heading badges.
    for i, (ang, title, col) in enumerate([(90, "toward", RED), (0, "broadside", GREEN), (270, "away", RED)]):
        bx = x+w*(0.62+i*0.115); by = y+h*0.22
        c.setFillColor(WHITE); c.setStrokeColor(MID); c.roundRect(bx-16, by-12, 31, 25, 5, fill=1, stroke=1)
        draw_plane(c, bx, by+2, 20, ang, fill=PALE, accent=GOLD)
        label(c, title, bx, by-10, 4.6, col, True, "center")
    label(c, "satellite line of sight", x+w*0.65, y+h*0.88, 5.5, NAVY, True)


def thumb_rotate(c, x, y, w, h):
    sx, sy = x+w*0.78, y+h*0.72
    draw_satellite(c, sx, sy, 0.7)
    for i, (ang, g) in enumerate([(235, "weak"), (155, "strong"), (215, "mid")]):
        px=x+w*(0.20+i*0.25); py=y+h*0.38
        draw_plane(c, px, py, 35, ang, fill=WHITE)
        arrow(c, px+5, py+5, sx-5, sy-5, [RED,GREEN,GOLD][i], 1.2, 4)
        label(c, g, px, y+h*0.08, 5.5, [RED,GREEN,GOLD][i], True, "center")
    c.setStrokeColor(GREY); c.setDash(3,2); c.circle(x+w*0.45,y+h*0.38,w*0.31,fill=0,stroke=1); c.setDash()


def thumb_axes(c, x, y, w, h):
    cx, cy=x+w*0.45,y+h*0.40
    draw_plane(c,cx,cy,45,0,fill=WHITE)
    arrow(c,cx,cy,cx,y+h*0.88,NAVY,1.6,5); label(c,"x: nose",cx+4,y+h*0.83,5.4,NAVY,True)
    arrow(c,cx,cy,x+w*0.83,cy,BLUE,1.6,5); label(c,"y: right",x+w*0.70,cy+5,5.4,BLUE,True)
    arrow(c,cx,cy,x+w*0.62,y+h*0.74,GOLD,2.0,6); label(c,"look vector",x+w*0.59,y+h*0.75,5.2,GOLD,True)
    c.setStrokeColor(GREY); c.setDash(3,2); c.arc(cx-26,cy-26,cx+26,cy+26,5,50); c.setDash()
    label(c,"azimuth ψ",cx+23,cy+20,5.0,GREY)
    label(c,"elevation ε",cx+10,cy+34,5.0,GREY)


def thumb_same_position(c,x,y,w,h):
    cx,cy=x+w*0.48,y+h*0.46
    c.setFillColor(HexColor("#EAF2F7")); c.setStrokeColor(MID)
    for dx in range(-2,4): c.line(cx+dx*22,y+5,cx+dx*22,y+h-5)
    for dy in range(-1,3): c.line(x+5,cy+dy*22,x+w-5,cy+dy*22)
    draw_satellite(c,x+w*0.86,y+h*0.78,0.65)
    draw_plane(c,cx-2,cy,42,0,fill=WHITE,accent=GOLD)
    draw_plane(c,cx+2,cy,42,90,fill=colors.Color(1,1,1,alpha=0.4),stroke=BLUE,accent=CYAN)
    arrow(c,cx,cy,x+w*0.82,y+h*0.72,GOLD,1.4,5)
    label(c,"one position",cx,y+h*0.08,5.4,NAVY,True,"center")
    label(c,"two headings → two gains",x+w*0.52,y+h*0.90,5.7,INK,True,"center")


def thumb_handoff(c,x,y,w,h):
    cx,cy=x+w*0.42,y+h*0.38
    draw_plane(c,cx,cy,48,0,fill=WHITE)
    c.setFillColor(colors.Color(BLUE.red,BLUE.green,BLUE.blue,alpha=0.24)); c.setStrokeColor(BLUE)
    c.wedge(cx-64,cy-12,cx+4,cy+58,40,90,fill=1,stroke=1)
    c.setFillColor(colors.Color(ORANGE.red,ORANGE.green,ORANGE.blue,alpha=0.24)); c.setStrokeColor(ORANGE)
    c.wedge(cx-4,cy-12,cx+64,cy+58,50,90,fill=1,stroke=1)
    for px,col,txt in [(cx-7,BLUE,"PORT"),(cx+7,ORANGE,"STARBOARD")]:
        c.setFillColor(col); c.circle(px,cy+12,2.5,fill=1,stroke=0); label(c,txt,px,y+5,4.7,col,True,"center")
    draw_satellite(c,x+w*0.82,y+h*0.72,0.65); arrow(c,cx,cy+10,x+w*0.77,y+h*0.68,GOLD,1.8,5)
    label(c,"choose larger panel gain",x+w*0.70,y+h*0.91,5.3,NAVY,True,"center")


def thumb_compass(c,x,y,w,h):
    cx,cy=x+w*0.50,y+h*0.48; r=min(w,h)*0.37
    for a0,a1,col in [(0,55,RED),(55,120,GREEN),(120,235,RED),(235,300,GREEN),(300,360,RED)]:
        c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.42)); c.setStrokeColor(WHITE)
        c.wedge(cx-r,cy-r,cx+r,cy+r,90-a1,a1-a0,fill=1,stroke=1)
    c.setFillColor(WHITE); c.circle(cx,cy,r*0.53,fill=1,stroke=0)
    draw_plane(c,cx,cy,44,0,fill=WHITE)
    label(c,"NOSE",cx,cy+r+2,4.8,NAVY,True,"center")
    label(c,"strong",cx+r*0.77,cy,4.8,GREEN,True,"center")
    label(c,"weak",cx,cy-r*0.82,4.8,RED,True,"center")


def thumb_mounted_lobes(c,x,y,w,h):
    cx,cy=x+w*0.43,y+h*0.36
    draw_plane(c,cx,cy,52,0,fill=WHITE)
    for side,col,shift in [(-1,BLUE,-1),(1,ORANGE,1)]:
        c.saveState(); c.translate(cx+side*6,cy+12); c.rotate(-side*28)
        c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.28)); c.setStrokeColor(col); c.setLineWidth(1.0)
        p=c.beginPath(); p.moveTo(0,0); p.curveTo(side*15,12,side*36,38,side*39,65); p.curveTo(side*9,50,side*3,20,0,0); p.close()
        c.drawPath(p,fill=1,stroke=1); c.restoreState()
    label(c,"two canted arrays",x+w*0.50,y+h*0.91,5.5,NAVY,True,"center")
    label(c,"gain volume",x+w*0.77,y+h*0.72,5.0,PLUM,True)


def thumb_gain_hemisphere(c,x,y,w,h):
    cx,cy=x+w*0.50,y+h*0.33; rx=w*0.39; ry=h*0.25
    # Pseudo-3D sampled upper hemisphere.
    for el in range(0,91,10):
        rr=rx*math.cos(math.radians(el)); zz=ry*math.sin(math.radians(el))
        pts=[]
        for az in range(0,361,10):
            g=gain_value(az,el); rad=(0.72+0.28*(g-5)/9.5)
            px=cx+rr*rad*math.cos(math.radians(az)); py=cy+zz+0.30*rr*rad*math.sin(math.radians(az))
            pts.append((px,py,g))
        for (p1,p2) in zip(pts[:-1],pts[1:]):
            c.setStrokeColor(heat_colour((p1[2]+p2[2])/2)); c.setLineWidth(1.7); c.line(p1[0],p1[1],p2[0],p2[1])
    c.setStrokeColor(GREY); c.setLineWidth(0.6); c.ellipse(cx-rx,cy-0.30*rx,cx+rx,cy+0.30*rx,fill=0,stroke=1)
    draw_plane(c,cx,cy-2,34,0,fill=WHITE)
    label(c,"weak nose/tail",cx,cy+ry+28,5.0,RED,True,"center")
    label(c,"strong broadside",cx+rx*0.62,cy+4,5.0,GREEN,True,"center")


def thumb_polar_slices(c,x,y,w,h):
    cx,cy=x+w*0.48,y+h*0.47; r=min(w,h)*0.38
    for rr in [0.35,0.65,1.0]:
        c.setStrokeColor(LIGHT_GREY); c.circle(cx,cy,r*rr,fill=0,stroke=1)
    for el,col in [(0,BLUE),(15,CYAN),(30,GOLD),(45,ORANGE)]:
        pts=[]
        for az in range(361):
            g=gain_value(az,el); rr=r*(0.22+0.78*(g-4.8)/(14.5-4.8)); a=math.radians(90-az)
            pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
        p=c.beginPath(); p.moveTo(*pts[0])
        for px,py in pts[1:]: p.lineTo(px,py)
        c.setStrokeColor(col); c.setLineWidth(1.25); c.drawPath(p,fill=0,stroke=1)
    for i,(el,col) in enumerate([(0,BLUE),(15,CYAN),(30,GOLD),(45,ORANGE)]):
        c.setStrokeColor(col); c.setLineWidth(2); c.line(x+w*0.77,y+h*(0.78-i*0.13),x+w*0.83,y+h*(0.78-i*0.13)); label(c,f"{el}°",x+w*0.85,y+h*(0.78-i*0.13)-2,4.8,col,True)


def thumb_gain_heatmap(c,x,y,w,h):
    gx,gy=x+w*0.14,y+h*0.17; gw,gh=w*0.72,h*0.66
    na,ne=36,9
    for ia in range(na):
        az=(ia+0.5)*360/na
        for ie in range(ne):
            el=(ie+0.5)*90/ne
            c.setFillColor(heat_colour(gain_value(az,el))); c.setStrokeColor(heat_colour(gain_value(az,el)))
            c.rect(gx+ia*gw/na,gy+ie*gh/ne,gw/na+0.2,gh/ne+0.2,fill=1,stroke=0)
    c.setStrokeColor(NAVY); c.rect(gx,gy,gw,gh,fill=0,stroke=1)
    label(c,"elevation",gx-4,gy+gh/2,4.7,NAVY,True,"right")
    label(c,"nose",gx,gy-8,4.5,NAVY,True,"center"); label(c,"side",gx+gw*0.25,gy-8,4.5,NAVY,True,"center")
    label(c,"tail",gx+gw*0.50,gy-8,4.5,NAVY,True,"center"); label(c,"side",gx+gw*0.75,gy-8,4.5,NAVY,True,"center")


def thumb_scan_loss(c,x,y,w,h):
    base=y+h*0.20
    for i,(tilt,g,col) in enumerate([(0,"14.5",GREEN),(35,"≈12",GOLD),(70,"≈5",RED)]):
        cx=x+w*(0.18+i*0.31); cy=base
        c.setStrokeColor(NAVY); c.setLineWidth(3); c.line(cx-18,cy,cx+18,cy)
        ang=math.radians(90-tilt); ex=cx+45*math.cos(ang); ey=cy+45*math.sin(ang)
        c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.22)); c.setStrokeColor(col)
        p=c.beginPath(); p.moveTo(cx,cy); p.lineTo(ex-8,ey); p.curveTo(ex,ey+4,ex+8,ey,ex+10,ey-4); p.lineTo(cx,cy); p.close(); c.drawPath(p,fill=1,stroke=1)
        arrow(c,cx,cy,ex,ey,col,1.3,4)
        label(c,f"{g} dBic",cx,y+4,5.2,col,True,"center")
    label(c,"boresight",x+w*0.18,y+h*0.83,4.8,GREEN,True,"center"); label(c,"edge steering",x+w*0.80,y+h*0.83,4.8,RED,True,"center")


def thumb_gain_profile(c,x,y,w,h):
    ax=x+w*0.13; ay=y+h*0.18; aw=w*0.72; ah=h*0.62; axes_box(c,ax,ay,aw,ah)
    pts=[]
    for i in range(101):
        theta=90*i/100; gain=14.5-9.5*(math.sin(math.radians(theta))**8)
        pts.append((ax+aw*i/100,ay+ah*(gain-4.8)/(14.5-4.8)))
    p=c.beginPath();p.moveTo(*pts[0])
    for pt in pts[1:]:p.lineTo(*pt)
    c.setStrokeColor(BLUE);c.setLineWidth(2.2);c.drawPath(p,fill=0,stroke=1)
    for frac,txt,col in [(0.0,"boresight",GREEN),(0.52,"scan loss",GOLD),(1.0,"edge",RED)]:
        px=ax+aw*frac; idx=int(frac*100); py=pts[idx][1]; c.setFillColor(col); c.circle(px,py,2.6,fill=1,stroke=0);label(c,txt,px,py+7,4.6,col,True,"center")
    label(c,"steering angle",ax+aw/2,ay-10,4.8,NAVY,True,"center"); label(c,"gain",ax-4,ay+ah,4.8,NAVY,True,"right")


def thumb_attitude_matrix(c,x,y,w,h):
    titles=[("level",0,0),("bank 25°",25,0),("pitch −10°",0,-10),("bank 45°",45,0),("pitch +10°",0,10),("combined",30,-8)]
    for i,(txt,bank,pitch) in enumerate(titles):
        col=i%3; row=1-i//3; cx=x+w*(0.18+col*0.32); cy=y+h*(0.30+row*0.43)
        c.saveState(); c.translate(cx,cy); c.rotate(bank)
        c.setStrokeColor(NAVY); c.setLineWidth(2); c.line(-17,0,17,0); c.setFillColor(WHITE); c.circle(0,0,4,fill=1,stroke=1); c.restoreState()
        arrow(c,cx,cy,cx+10+pitch*0.5,cy+22,GOLD,1.0,3)
        label(c,txt,cx,cy-13,4.5,INK,True,"center")


def thumb_bank_sweep(c,x,y,w,h):
    ax=x+w*0.12;ay=y+h*0.18;aw=w*0.74;ah=h*0.60;axes_box(c,ax,ay,aw,ah)
    pts=[]
    for i in range(101):
        bank=-60+120*i/100; val=9.4+4.4*math.exp(-((bank-23)/26)**2)-2.2*math.exp(-((bank+50)/15)**2)
        pts.append((ax+aw*i/100,ay+ah*(val-6)/(14.5-6)))
    p=c.beginPath();p.moveTo(*pts[0])
    for pt in pts[1:]:p.lineTo(*pt)
    c.setStrokeColor(ORANGE);c.setLineWidth(2.2);c.drawPath(p,fill=0,stroke=1)
    c.setFillColor(colors.Color(GOLD.red,GOLD.green,GOLD.blue,alpha=0.16)); c.rect(ax+aw*0.37,ay,aw*0.26,ah,fill=1,stroke=0)
    label(c,"bank angle",ax+aw/2,ay-10,4.8,NAVY,True,"center"); label(c,"gain",ax-3,ay+ah,4.8,NAVY,True,"right"); label(c,"panel hand-off",ax+aw*0.51,ay+ah+2,4.5,GOLD,True,"center")


def thumb_pitch_sweep(c,x,y,w,h):
    for i,(pitch,txt,col) in enumerate([(-10,"descent",BLUE),(0,"level",GREEN),(10,"climb",ORANGE)]):
        cx=x+w*(0.18+i*0.32);cy=y+h*0.36
        c.saveState();c.translate(cx,cy);c.rotate(pitch);c.setStrokeColor(NAVY);c.setLineWidth(2.5);c.line(-22,0,22,0);c.setFillColor(WHITE);c.ellipse(-9,-3,9,3,fill=1,stroke=1);c.restoreState()
        arrow(c,cx,cy,cx+18,cy+44,GOLD,1.3,4)
        label(c,txt,cx,y+h*0.08,5.0,col,True,"center"); label(c,f"{pitch:+d}°",cx,y+h*0.80,4.7,GREY,True,"center")


def thumb_sky_domes(c,x,y,w,h):
    for i,(title,shift) in enumerate([("normal",0),("unusual",35)]):
        cx=x+w*(0.27+i*0.46);cy=y+h*0.34;r=min(w,h)*0.30
        c.setFillColor(colors.Color(CYAN.red,CYAN.green,CYAN.blue,alpha=0.16));c.setStrokeColor(NAVY);c.wedge(cx-r,cy-r*0.25,cx+r,cy+r*1.75,0,180,fill=1,stroke=1)
        c.setFillColor(colors.Color(RED.red,RED.green,RED.blue,alpha=0.24));c.setStrokeColor(RED);c.wedge(cx-r,cy-r*0.25,cx+r,cy+r*1.75,70+shift,38,fill=1,stroke=1)
        c.setFillColor(colors.Color(GREEN.red,GREEN.green,GREEN.blue,alpha=0.22));c.setStrokeColor(GREEN);c.wedge(cx-r,cy-r*0.25,cx+r,cy+r*1.75,5+shift,50,fill=1,stroke=1)
        c.saveState();c.translate(cx,cy);c.rotate(shift);c.setStrokeColor(NAVY);c.setLineWidth(2);c.line(-18,0,18,0);c.restoreState();label(c,title,cx,y+5,5.0,INK,True,"center")


def thumb_turn_ribbon(c,x,y,w,h):
    pts=[(x+w*0.10,y+h*0.30),(x+w*0.30,y+h*0.32),(x+w*0.48,y+h*0.50),(x+w*0.61,y+h*0.73),(x+w*0.85,y+h*0.70)]
    cols=[BLUE,CYAN,GREEN,GOLD,ORANGE]
    for i in range(len(pts)-1):
        c.setStrokeColor(cols[i]);c.setLineWidth(8);c.line(*pts[i],*pts[i+1])
    for i,pt in enumerate(pts):
        c.setFillColor(cols[i]);c.circle(*pt,3,fill=1,stroke=0)
        if i in [0,2,4]:draw_plane(c,pt[0],pt[1]+7,22,[90,30,300][[0,2,4].index(i)],fill=WHITE)
    label(c,"predicted gain along a manoeuvre",x+w*0.50,y+h*0.90,5.4,NAVY,True,"center")
    # Mini colour key.
    for i,col in enumerate([BLUE,CYAN,GREEN,GOLD,ORANGE]):
        c.setFillColor(col);c.rect(x+w*(0.35+i*0.06),y+4,w*0.055,4,fill=1,stroke=0)


def thumb_envelope(c,x,y,w,h):
    for i,(title,col,wide) in enumerate([("calibrated cruise",GREEN,0.33),("edge cases",ORANGE,0.48)]):
        cx=x+w*(0.27+i*0.47);cy=y+h*0.44
        c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.16));c.setStrokeColor(col);c.ellipse(cx-w*wide/2,cy-h*0.28,cx+w*wide/2,cy+h*0.28,fill=1,stroke=1)
        c.setDash(4,2);c.setStrokeColor(GREY);c.ellipse(cx-w*0.20,cy-h*0.37,cx+w*0.20,cy+h*0.37,fill=0,stroke=1);c.setDash()
        draw_plane(c,cx,cy,31,0 if i==0 else 45,fill=WHITE);label(c,title,cx,y+6,4.8,col,True,"center")
    arrow(c,x+w*0.45,y+h*0.47,x+w*0.55,y+h*0.47,GREY,1,4)


MH371_TRACK = [
    (116.598,40.072),(115.004,39.462),(114.820,35.988),(114.331,31.257),
    (113.615,29.634),(113.718,29.400),(113.872,29.048),(114.002,28.413),
    (113.790,27.882),(113.883,24.073),(113.453,20.310),(112.521,17.298),
    (109.793,13.638),(107.672,10.309),(104.452,5.193),(101.837,2.582),
]


def map_xy(lon,lat,x,y,w,h):
    return x+(lon-100)/(117-100)*w, y+(lat-1)/(41-1)*h


def thumb_mh371_map(c,x,y,w,h):
    mx,my=x+w*0.18,y+h*0.08;mw,mh=w*0.58,h*0.82
    c.setFillColor(HexColor("#E9F2F6"));c.setStrokeColor(MID);c.roundRect(mx,my,mw,mh,5,fill=1,stroke=1)
    pts=[map_xy(lon,lat,mx,my,mw,mh) for lon,lat in MH371_TRACK]
    p=c.beginPath();p.moveTo(*pts[0])
    for pt in pts[1:]:p.lineTo(*pt)
    c.setStrokeColor(NAVY);c.setLineWidth(2.0);c.drawPath(p,fill=0,stroke=1)
    phases=[("01:55",115.004,39.462,236,10.4,RED),("03:21",113.718,29.400,158,14.1,GREEN),("03:29",114.002,28.413,219,11.7,GOLD)]
    for i,(t,lon,lat,hdg,g,col) in enumerate(phases):
        px,py=map_xy(lon,lat,mx,my,mw,mh);c.setFillColor(col);c.circle(px,py,3.3,fill=1,stroke=0);label(c,t,px+5,py+2,4.7,col,True)
    label(c,"Beijing",pts[0][0]-2,pts[0][1]+5,4.5,NAVY,True,"right");label(c,"Kuala Lumpur",pts[-1][0]+3,pts[-1][1]-1,4.5,NAVY,True)
    # Phase legend at right.
    for i,(t,lon,lat,hdg,g,col) in enumerate(phases):
        yy=y+h*(0.72-i*0.24);c.setFillColor(col);c.circle(x+w*0.81,yy,3,fill=1,stroke=0);label(c,f"{hdg}°T",x+w*0.85,yy+2,4.7,col,True);label(c,f"G {g:.1f}",x+w*0.85,yy-6,4.5,INK)


def thumb_mh371_snapshots(c,x,y,w,h):
    phases=[("01:55","236°T","10.4",RED,236),("03:21","158°T","14.1",GREEN,158),("03:29","219°T","11.7",GOLD,219)]
    sx,sy=x+w*0.86,y+h*0.79;draw_satellite(c,sx,sy,0.58)
    for i,(t,hd,g,col,ang) in enumerate(phases):
        px=x+w*(0.17+i*0.28);py=y+h*0.34;draw_plane(c,px,py,29,ang,fill=WHITE);arrow(c,px,py,sx-3,sy-4,col,1.0,3)
        label(c,t,px,y+h*0.10,4.9,col,True,"center");label(c,f"{hd}  |  {g} dBic",px,y+h*0.03,4.3,INK,False,"center")


def thumb_time_series(c,x,y,w,h):
    left=x+w*0.15;right=x+w*0.90; rows=[("heading",GREEN),("gain",PLUM),("power",BLUE)]
    for r,(name,col) in enumerate(rows):
        base=y+h*(0.72-r*0.27);c.setStrokeColor(LIGHT_GREY);c.line(left,base,right,base);label(c,name,left-4,base+2,4.6,col,True,"right")
        values={0:[0.25,0.25,0.22,0.15,0.75,0.70,0.28,0.26],1:[0.18,0.20,0.24,0.35,0.88,0.85,0.42,0.38],2:[0.22,0.25,0.27,0.40,0.78,0.80,0.51,0.47]}[r]
        p=c.beginPath()
        for i,v in enumerate(values):
            px=left+(right-left)*i/(len(values)-1);py=base+(v-0.5)*h*0.16
            if i==0:p.moveTo(px,py)
            else:p.lineTo(px,py)
        c.setStrokeColor(col);c.setLineWidth(1.8);c.drawPath(p,fill=0,stroke=1)
    for frac,t in [(0.03,"01:55"),(0.58,"03:21"),(0.78,"03:29")]:
        px=left+(right-left)*frac;c.setStrokeColor(GREY);c.setDash(2,2);c.line(px,y+h*0.12,px,y+h*0.90);c.setDash();label(c,t,px,y+h*0.04,4.3,GREY,True,"center")


def thumb_counterfactual(c,x,y,w,h):
    ax=x+w*0.13;ay=y+h*0.18;aw=w*0.75;ah=h*0.64;axes_box(c,ax,ay,aw,ah)
    gains=[10.422,11.722,13.947];powers=[124.671,127.040,127.174]
    xmin,xmax=10.0,14.4;ymin,ymax=124.4,128.6
    def xy(g,p):return ax+aw*(g-xmin)/(xmax-xmin),ay+ah*(p-ymin)/(ymax-ymin)
    # Counterfactual lines pivot around 12 dB / 126.3.
    for beta,col,dash in [(0,GREEN,True),(0.645,ORANGE,False),(1,RED,True)]:
        x1,y1=xy(xmin,126.3+beta*(xmin-12));x2,y2=xy(xmax,126.3+beta*(xmax-12));c.setStrokeColor(col);c.setLineWidth(1.7);c.setDash(4,2) if dash else c.setDash();c.line(x1,y1,x2,y2);c.setDash()
    for i,(g,p,t) in enumerate(zip(gains,powers,["01:55","03:29","03:21"])):
        px,py=xy(g,p);c.setFillColor(BLUE);c.circle(px,py,3,fill=1,stroke=0);label(c,t,px+4,py+3,4.3,INK,True)
    label(c,"reconstructed gain",ax+aw/2,ay-10,4.5,NAVY,True,"center")
    label(c,"path-corrected power",ax+3,ay+ah-8,4.1,NAVY,True)
    label(c,"β=0",ax+aw*0.73,ay+ah*0.43,4.3,GREEN,True);label(c,"β≈0.65",ax+aw*0.70,ay+ah*0.73,4.3,ORANGE,True);label(c,"β=1",ax+aw*0.82,ay+ah*0.92,4.3,RED,True)


def thumb_delta_plot(c,x,y,w,h):
    ax=x+w*0.16;ay=y+h*0.18;aw=w*0.68;ah=h*0.64;axes_box(c,ax,ay,aw,ah)
    c.setStrokeColor(GREY);c.setDash(3,2);c.line(ax,ay,ax+aw,ay+ah);c.setDash()
    pts=[(3.53,2.50,"01:55→03:21",GREEN),(1.53,2.37,"01:55→03:29",GOLD),(-2.23,-0.13,"03:21→03:29",BLUE)]
    xmin,xmax=-3,4;ymin,ymax=-1,4
    for dx,dy,t,col in pts:
        px=ax+aw*(dx-xmin)/(xmax-xmin);py=ay+ah*(dy-ymin)/(ymax-ymin);c.setFillColor(col);c.circle(px,py,3.4,fill=1,stroke=0);label(c,t,px+4,py+2,4.1,col,True)
    label(c,"Δ predicted gain",ax+aw/2,ay-10,4.5,NAVY,True,"center")
    label(c,"Δ power",ax+3,ay+ah-8,4.3,NAVY,True)


def thumb_beta_dial(c,x,y,w,h):
    cx=x+w*0.50;cy=y+h*0.23;r=min(w,h)*0.43
    # Upper-half dial: complete compensation at left, no compensation at right.
    c.setLineWidth(9);c.setStrokeColor(RED);c.arc(cx-r,cy-r,cx+r,cy+r,0,60)
    c.setStrokeColor(GOLD);c.arc(cx-r,cy-r,cx+r,cy+r,60,60)
    c.setStrokeColor(GREEN);c.arc(cx-r,cy-r,cx+r,cy+r,120,60)
    for val,txt,col in [(0,"complete",GREEN),(0.645,"estimate",ORANGE),(1,"none",RED)]:
        a=math.radians(180-180*val);px=cx+r*math.cos(a);py=cy+r*math.sin(a);c.setFillColor(col);c.circle(px,py,3.4,fill=1,stroke=0)
        if val in (0,1): label(c,txt,px,cy-13,4.5,col,True,"center")
        else: label(c,txt,px,py+8,4.5,col,True,"center")
    a=math.radians(180-180*0.645);arrow(c,cx,cy,cx+(r-8)*math.cos(a),cy+(r-8)*math.sin(a),NAVY,2.2,5)
    label(c,"β",cx,cy-2,8,NAVY,True,"center");label(c,"gain surviving terminal control",cx,y+h*0.87,5.2,NAVY,True,"center")


def thumb_link_chain(c,x,y,w,h):
    nodes=[("AES\npower",ORANGE),("antenna\ngain",PLUM),("uplink\nloss",BLUE),("satellite\nrelay",GOLD),("downlink\nloss",BLUE),("GES\nrecord",GREEN)]
    bw=w*0.115;gap=w*0.032;start=x+w*0.04;cy=y+h*0.44
    for i,(txt,col) in enumerate(nodes):
        bx=start+i*(bw+gap);c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.16));c.setStrokeColor(col);c.roundRect(bx,cy-h*0.16,bw,h*0.32,5,fill=1,stroke=1)
        lines=txt.split("\n")
        for j,line in enumerate(lines):label(c,line,bx+bw/2,cy+3-j*8,4.3,col,True,"center")
        if i<len(nodes)-1:arrow(c,bx+bw,cy,bx+bw+gap-2,cy,GREY,1.0,3)
    c.setFillColor(colors.Color(PLUM.red,PLUM.green,PLUM.blue,alpha=0.12));c.setStrokeColor(PLUM);c.roundRect(start+bw+gap-4,cy-h*0.23,bw+8,h*0.46,7,fill=1,stroke=1)
    label(c,"geometry-sensitive term",start+bw+gap+bw/2,cy+h*0.27,4.7,PLUM,True,"center")


def thumb_causal(c,x,y,w,h):
    nodes={"geometry":(0.18,0.72,BLUE),"attitude":(0.18,0.30,ORANGE),"gain":(0.48,0.60,PLUM),"terminal β":(0.48,0.23,GOLD),"path/channel":(0.75,0.76,CYAN),"received power":(0.80,0.36,GREEN)}
    for a,b in [("geometry","gain"),("attitude","gain"),("gain","received power"),("terminal β","received power"),("path/channel","received power")]:
        x1=x+w*nodes[a][0];y1=y+h*nodes[a][1];x2=x+w*nodes[b][0];y2=y+h*nodes[b][1];arrow(c,x1,y1,x2,y2,GREY,1,4)
    for name,(fx,fy,col) in nodes.items():
        cx=x+w*fx;cy=y+h*fy;tw=max(38,text_width(name,4.6,True)+12);c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.16));c.setStrokeColor(col);c.roundRect(cx-tw/2,cy-8,tw,16,6,fill=1,stroke=1);label(c,name,cx,cy-2,4.5,col,True,"center")


def thumb_likelihood(c,x,y,w,h):
    # Stylised map domain with BTO arc, BFO ridge and power bands.
    c.setFillColor(HexColor("#EDF3F6"));c.setStrokeColor(MID);c.roundRect(x+5,y+5,w-10,h-10,5,fill=1,stroke=1)
    c.setStrokeColor(BLUE);c.setLineWidth(7);c.setStrokeAlpha(0.24);c.arc(x-w*0.15,y-h*0.20,x+w*1.10,y+h*1.55,300,75);c.setStrokeAlpha(1)
    c.setStrokeColor(GOLD);c.setLineWidth(6);c.setStrokeAlpha(0.28);c.line(x+w*0.20,y+h*0.12,x+w*0.78,y+h*0.90);c.setStrokeAlpha(1)
    # Power likelihood islands along the intersection.
    for fx,fy,sc in [(0.43,0.44,1.0),(0.64,0.71,0.7)]:
        cx=x+w*fx;cy=y+h*fy;c.setFillColor(colors.Color(PLUM.red,PLUM.green,PLUM.blue,alpha=0.35));c.setStrokeColor(PLUM);c.ellipse(cx-20*sc,cy-8*sc,cx+20*sc,cy+8*sc,fill=1,stroke=1)
    label(c,"BTO",x+w*0.12,y+h*0.72,4.9,BLUE,True);label(c,"BFO",x+w*0.74,y+h*0.85,4.9,GOLD,True);label(c,"power reweights",x+w*0.55,y+h*0.36,4.9,PLUM,True)


def thumb_posterior_compare(c,x,y,w,h):
    for i,(title,add_power) in enumerate([("BTO + BFO",False),("+ received power",True)]):
        bx=x+w*(0.04+i*0.49);by=y+h*0.14;bw=w*0.43;bh=h*0.70
        c.setFillColor(HexColor("#EDF3F6"));c.setStrokeColor(MID);c.roundRect(bx,by,bw,bh,5,fill=1,stroke=1)
        modes=[(0.45,0.72,0.8),(0.57,0.42,1.0),(0.68,0.22,0.55)]
        if add_power:modes=[(0.44,0.72,0.35),(0.57,0.42,1.0),(0.68,0.22,0.20)]
        for fx,fy,a in modes:
            cx=bx+bw*fx;cy=by+bh*fy
            for j,sc in enumerate([1.0,0.68,0.38]):
                col=heat_colour(10+j*1.8);c.setFillColor(colors.Color(col.red,col.green,col.blue,alpha=0.10+0.10*a));c.setStrokeColor(col);c.ellipse(cx-24*sc*a,cy-10*sc,cx+24*sc*a,cy+10*sc,fill=1,stroke=1)
        c.setStrokeColor(GREY);c.setDash(3,2);c.arc(bx-bw*0.3,by-bh*0.3,bx+bw*1.25,by+bh*1.45,300,70);c.setDash();label(c,title,bx+bw/2,y+4,4.8,NAVY,True,"center")
    arrow(c,x+w*0.47,y+h*0.50,x+w*0.53,y+h*0.50,NAVY,1.3,4)


THUMBNAILS = {
    "hero_triad": thumb_hero_triad, "rotate_aircraft": thumb_rotate, "axes": thumb_axes,
    "same_position": thumb_same_position, "handoff": thumb_handoff, "compass": thumb_compass,
    "mounted_lobes": thumb_mounted_lobes, "gain_hemisphere": thumb_gain_hemisphere,
    "polar_slices": thumb_polar_slices, "gain_heatmap": thumb_gain_heatmap,
    "scan_loss": thumb_scan_loss, "gain_profile": thumb_gain_profile,
    "attitude_matrix": thumb_attitude_matrix, "bank_sweep": thumb_bank_sweep,
    "pitch_sweep": thumb_pitch_sweep, "sky_domes": thumb_sky_domes,
    "turn_ribbon": thumb_turn_ribbon, "envelope": thumb_envelope,
    "mh371_map": thumb_mh371_map, "mh371_snapshots": thumb_mh371_snapshots,
    "time_series": thumb_time_series, "counterfactual": thumb_counterfactual,
    "delta_plot": thumb_delta_plot, "beta_dial": thumb_beta_dial,
    "link_chain": thumb_link_chain, "causal": thumb_causal,
    "likelihood": thumb_likelihood, "posterior_compare": thumb_posterior_compare,
}


def draw_card(c, opt, x, y, w, h, compact=False):
    group_col=GROUP_COLOURS[opt["group"]]
    c.setFillColor(WHITE);c.setStrokeColor(MID);c.setLineWidth(0.8);c.roundRect(x,y,w,h,8,fill=1,stroke=1)
    c.setFillColor(group_col);c.roundRect(x,y+h-22,w,22,8,fill=1,stroke=0);c.rect(x,y+h-14,w,14,fill=1,stroke=0)
    c.setFillColor(WHITE);set_font(c,True,8.5 if not compact else 7.5);c.drawString(x+9,y+h-15,f"{opt['n']:02d}  {opt['group'].upper()}")
    if opt.get("rec"):
        c.setFillColor(GOLD);c.circle(x+w-12,y+h-11,5,fill=1,stroke=0);label(c,"★",x+w-12,y+h-13.5,6,WHITE,True,"center")
    thumb_h=h*(0.44 if not compact else 0.43)
    tx=x+7;ty=y+h-22-thumb_h-3;tw=w-14
    c.setFillColor(PALE);c.setStrokeColor(LIGHT_GREY);c.roundRect(tx,ty,tw,thumb_h,5,fill=1,stroke=1)
    c.saveState();
    try:
        # Several concepts deliberately use oversized arcs or coverage rings.  Clip
        # them to the thumbnail so they cannot collide with card copy or neighbours.
        clip = c.beginPath()
        clip.rect(tx, ty, tw, thumb_h)
        c.clipPath(clip, stroke=0, fill=0)
        THUMBNAILS[opt["kind"]](c,tx+2,ty+2,tw-4,thumb_h-4)
    finally:
        c.restoreState()
    title_size=9.3 if not compact else 7.9
    story_size=6.9 if not compact else 5.8
    meta_size=5.8 if not compact else 5.0
    top=ty-10
    top=draw_wrapped(c,opt["title"],x+9,top,w-18,title_size,title_size*1.18,INK,True,2)-3
    top=draw_wrapped(c,opt["story"],x+9,top,w-18,story_size,story_size*1.28,GREY,False,3)-4
    # Meta rows are anchored to avoid card-to-card drift.
    label(c,opt["status"],x+9,y+19,meta_size,group_col,True)
    label(c,opt["use"],x+9,y+8,meta_size,INK,False)


def cover_page(c, page_w, page_h):
    c.setFillColor(NAVY);c.rect(0,0,page_w,page_h,fill=1,stroke=0)
    c.setFillColor(WHITE);set_font(c,True,26);c.drawString(42,page_h-62,"Received power: 28 visual options")
    c.setFillColor(CYAN);set_font(c,False,12);c.drawString(44,page_h-83,"A figure storyboard for the integrated MH370 estimation paper")
    # Hero aircraft base in the upper-right.
    if AIRCRAFT_IMAGE.exists():
        c.drawImage(ImageReader(str(AIRCRAFT_IMAGE)), page_w*0.55,page_h*0.54,page_w*0.42,page_h*0.36,preserveAspectRatio=True,anchor="c",mask="auto")
    draw_satellite(c,page_w*0.90,page_h*0.79,1.0);arrow(c,page_w*0.84,page_h*0.74,page_w*0.69,page_h*0.66,GOLD,2.1,7)
    # Narrative frame.
    c.setFillColor(colors.Color(1,1,1,alpha=0.08));c.roundRect(40,page_h*0.51,page_w*0.46,page_h*0.30,12,fill=1,stroke=0)
    draw_wrapped(c,"The visual story",58,page_h*0.77,page_w*0.40,12,15,WHITE,True,1)
    body=("The terminal did not measure position. It measured a signal after aircraft-spacecraft "
          "geometry, a directional antenna, propagation, channel effects and possible terminal "
          "power control had all acted on it. The figure sequence should make that conditional "
          "nature visible before showing the statistical result.")
    draw_wrapped(c,body,58,page_h*0.72,page_w*0.39,9.2,13.5,HexColor("#DDE8F0"),False,7)
    # Suggested reader journey.
    y=page_h*0.39
    label(c,"SUGGESTED READER JOURNEY",42,y+49,8,CYAN,True)
    journey=[("01","geometry"),("19","natural experiment"),("24","precompensation"),("27","integration"),("28","posterior")]
    for i,(num,txt) in enumerate(journey):
        cx=78+i*(page_w-150)/4;c.setFillColor(GOLD if i in [0,2] else CYAN);c.circle(cx,y,18,fill=1,stroke=0);label(c,num,cx,y-3,8,NAVY,True,"center");label(c,txt,cx,y-33,6.7,WHITE,True,"center")
        if i<len(journey)-1:arrow(c,cx+22,y,cx+(page_w-150)/4-22,y,HexColor("#B7C9D7"),1.2,4)
    # Calibration / caveat boxes.
    box_y=44;box_h=92;box_w=(page_w-102)/2
    for i,(heading,body,col) in enumerate([
        ("What is already data-anchored",
         "MH371 phase headings and reconstructed gains: 01:55—236°T, 10.4 dBic; 03:21—158°T, 14.1 dBic; 03:29—about 219°T, 11.7 dBic. The same R1200-0-36E3 channel is used in the counterfactual options.",GREEN),
        ("What remains deliberately schematic",
         "The thumbnail lobes, attitude cases and posterior islands communicate visual form only. Selected plates will be regenerated from the full reconstructed gain surface, particle output and uncertainty model, with provenance stated in the caption.",ORANGE),
    ]):
        bx=40+i*(box_w+22);c.setFillColor(colors.Color(1,1,1,alpha=0.08));c.setStrokeColor(colors.Color(1,1,1,alpha=0.20));c.roundRect(bx,box_y,box_w,box_h,9,fill=1,stroke=1);label(c,heading,bx+14,box_y+box_h-22,8.3,col,True);draw_wrapped(c,body,bx+14,box_y+box_h-39,box_w-28,6.9,10,HexColor("#DDE8F0"),False,6)
    label(c,"Gold star = recommended shortlist",page_w-42,18,6.5,HexColor("#B7C9D7"),False,"right")


def group_page(c, page_w, page_h, opts, page_num):
    c.setFillColor(PALE);c.rect(0,0,page_w,page_h,fill=1,stroke=0)
    first,last=opts[0]["n"],opts[-1]["n"]
    group_names=" / ".join(dict.fromkeys(o["group"] for o in opts))
    c.setFillColor(NAVY);set_font(c,True,18);c.drawString(34,page_h-37,group_names)
    label(c,f"OPTIONS {first:02d}–{last:02d}",page_w-34,page_h-34,7.5,GREY,True,"right")
    c.setStrokeColor(MID);c.line(34,page_h-48,page_w-34,page_h-48)
    cols_n=3;rows_n=2;gap_x=13;gap_y=13;margin_x=34;bottom=29;top=57
    card_w=(page_w-2*margin_x-(cols_n-1)*gap_x)/cols_n
    card_h=(page_h-top-bottom-(rows_n-1)*gap_y)/rows_n
    for i,opt in enumerate(opts):
        col=i%cols_n;row=1-i//cols_n
        x=margin_x+col*(card_w+gap_x);y=bottom+row*(card_h+gap_y)
        draw_card(c,opt,x,y,card_w,card_h)
    label(c,"Selection packet — thumbnails are concepts, not final calibrated plates",34,12,6,GREY)
    label(c,str(page_num),page_w-34,12,6,GREY,False,"right")


def build_storyboard():
    page_w,page_h=landscape(A4)
    c=canvas.Canvas(str(STORYBOARD_PDF),pagesize=(page_w,page_h),pageCompression=1)
    c.setTitle("MH370 received-power graphics storyboard")
    c.setAuthor("OpenAI — prepared for figure selection")
    cover_page(c,page_w,page_h);c.showPage()
    chunks=[OPTIONS[i:i+6] for i in range(0,len(OPTIONS),6)]
    for p,chunk in enumerate(chunks,start=2):
        group_page(c,page_w,page_h,chunk,p);c.showPage()
    c.save()


def build_contact_sheet():
    cols_n,rows_n=4,7
    card_w,card_h=420,295;gap=14;margin=28;header=64
    page_w=margin*2+cols_n*card_w+(cols_n-1)*gap
    page_h=margin*2+header+rows_n*card_h+(rows_n-1)*gap
    c=canvas.Canvas(str(CONTACT_PDF),pagesize=(page_w,page_h),pageCompression=1)
    c.setFillColor(NAVY);c.rect(0,page_h-header-margin,page_w,header+margin,fill=1,stroke=0)
    c.setFillColor(WHITE);set_font(c,True,22);c.drawString(margin,page_h-42,"MH370 received-power graphics — 28-option contact sheet")
    label(c,"Gold star = recommended shortlist  |  choose by number",page_w-margin,page_h-40,8,HexColor("#DDE8F0"),False,"right")
    c.setFillColor(PALE);c.rect(0,0,page_w,page_h-header-margin,fill=1,stroke=0)
    for i,opt in enumerate(OPTIONS):
        col=i%cols_n;row=rows_n-1-i//cols_n
        x=margin+col*(card_w+gap);y=margin+row*(card_h+gap)
        draw_card(c,opt,x,y,card_w,card_h,compact=True)
    c.save()


def build_markdown():
    lines=[
        "# MH370 received-power graphics: option index",
        "",
        "This is a selection index for the visual storyboard. A gold star in the PDF marks the initial recommended shortlist.",
        "",
        "The MH371 phase values are data-anchored. Other thumbnail lobes, attitude cases and posterior shapes are schematic and will be regenerated from the full model after figure selection.",
        "",
    ]
    current=None
    for opt in OPTIONS:
        if opt["group"] != current:
            current=opt["group"]
            lines += [f"## {current}", ""]
        star=" ★" if opt.get("rec") else ""
        lines += [f"### {opt['n']:02d}. {opt['title']}{star}", "", opt["story"], "", f"Best use: {opt['use']}.  Status: {opt['status']}.", ""]
    lines += [
        "## Data anchors used in the MH371 thumbnails", "",
        "- 01:55 UTC: heading 236°T; reconstructed gain approximately 10.4 dBic.",
        "- 03:21 UTC: heading 158°T; reconstructed gain approximately 14.1 dBic.",
        "- 03:29 UTC: right turn of more than 60°; heading approximately 219°T; reconstructed gain approximately 11.7 dBic.",
        "- Same-channel test: R1200-0-36E3; free-space-path-corrected phase means.",
        "- β=0 denotes complete gain precompensation; β=1 denotes no gain precompensation.",
        "",
    ]
    OPTIONS_MD.write_text("\n".join(lines),encoding="utf-8")


if __name__ == "__main__":
    build_storyboard()
    build_contact_sheet()
    build_markdown()
    print(STORYBOARD_PDF)
    print(CONTACT_PDF)
    print(OPTIONS_MD)
