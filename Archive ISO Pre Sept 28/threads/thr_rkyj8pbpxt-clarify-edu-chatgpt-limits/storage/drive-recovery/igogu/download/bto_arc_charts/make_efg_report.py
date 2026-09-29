#!/usr/bin/env python3
"""Create a compact, self-contained two-page E/F/G BFO audit from calculated data."""
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
D=json.loads((OUT/'efg_analysis.json').read_text())
FONT=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
INK=colors.HexColor('#213446'); MUTED=colors.HexColor('#526477'); GREEN=colors.HexColor('#2e764c')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='DV-Bold',fontSize=18,leading=23,textColor=INK,spaceAfter=10))
styles.add(ParagraphStyle(name='HeadX',fontName='DV-Bold',fontSize=11,leading=15,textColor=INK,spaceBefore=13,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyX',fontName='DV',fontSize=9,leading=12.8,textColor=INK,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallX',fontName='DV',fontSize=8,leading=11,textColor=MUTED,spaceAfter=5))
styles.add(ParagraphStyle(name='TH',fontName='DV-Bold',fontSize=7.5,leading=9.4,textColor=colors.white))
styles.add(ParagraphStyle(name='Cell',fontName='DV',fontSize=8,leading=10.5,textColor=INK))
story=[]
def p(text,style='BodyX'):
    story.append(Paragraph(text,styles[style]))
def heading(text):p(text,'HeadX')
def table(headers,rows,widths,highlight=(),compact=False):
    content=[[Paragraph(x,styles['TH']) for x in headers]]+rows
    t=Table(content,colWidths=widths,repeatRows=1,hAlign='LEFT')
    cmds=[('FONTNAME',(0,1),(-1,-1),'DV'),('FONTSIZE',(0,1),(-1,-1),8),
          ('TEXTCOLOR',(0,1),(-1,-1),INK),('BACKGROUND',(0,0),(-1,0),INK),
          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4 if compact else 6),
          ('BOTTOMPADDING',(0,0),(-1,-1),4 if compact else 6),('LEFTPADDING',(0,0),(-1,-1),7),
          ('RIGHTPADDING',(0,0),(-1,-1),7),('ALIGN',(1,1),(-1,-1),'RIGHT'),
          ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f1f5f7'),colors.white]),
          ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#cddbe2'))]
    for r in highlight:
        cmds.extend([('BACKGROUND',(0,r),(-1,r),colors.HexColor('#e5f0e8')),('FONTNAME',(0,r),(-1,r),'DV-Bold')])
    t.setStyle(TableStyle(cmds));story.append(t);story.append(Spacer(1,7))

p('MH370 | E/F/G BFO on N571 and P627','TitleX')
p('<b>N571 gives the smaller residual at every point and every sampled speed.</b> '
  'For the raw E/F/G set, its best tested speed is 520 kt. F/G alone prefer 475 kt among the samples, '
  'with a formal continuous-speed minimum near 465 kt.')
p('Assumptions: level flight at 35,000 ft geometric altitude; N571 northwest toward IGOGU; '
  'P627 southwest toward POVUS. “P267” is interpreted as P627. The saved 152.5 Hz oscillator calibration '
  'and satellite AFC curve are fixed; no E startup correction or fitted frequency offset. Times are UTC on 7 March 2014.','SmallX')

heading('Residuals at each nominal BTO / airway intersection')
rows=[]
for r in D['pointwise_speed_comparison']:
    rows.append([r['airway'],f"{r['groundspeed_kt']:.0f}",*[f"{r[f'{a}_residual_hz']:+.2f}" for a in 'EFG'],
                 f"{r['rms_hz']:.2f}",f"{r['rss_hz2']:,.1f}",f"{r['fg_rms_hz']:.2f}"])
table(['Airway','GS<br/>kt','E<br/>Hz','F<br/>Hz','G<br/>Hz','EFG RMS<br/>Hz','EFG RSS<br/>Hz²','F/G RMS<br/>Hz'],
      rows,[52,37,61,61,61,59,72,66],highlight=(4,5))
p('Residual = predicted − observed. RSS = Σr²; RMS = √(RSS/n). Green rows mark each airway’s best '
  'sample for all three BFOs. E: 18:27:08.404, 12,520 µs, 172 Hz; F: 18:28:05.904, 12,500 µs, 144 Hz; '
  'G: 18:28:14.904, 12,480 µs, 143 Hz.','SmallX')

heading('Which speed minimizes each point?')
inter=[r for r in D['intersections'] if r['airway']=='N571']
rows=[[r['arc_id'],f"{r['zero_residual_signed_speed_kt']:,.1f}",str(v),'450'] for r,v in zip(inter,[520,475,450])]
table(['Point','N571 formal zero<br/>residual, kt','N571 best of four<br/>samples, kt','P627 best of four<br/>samples, kt'],rows,[52,169,127,121])
p('P627 has no positive zero-residual speed in the specified southwest direction: faster flight lowers '
  'its predicted BFO further below the measurements. N571’s formal common-speed minimum using E/F/G '
  'is <b>707.6 kt</b> (RMS 13.69 Hz), an implausible cruise-speed compromise. F/G alone give '
  '<b>465.4 kt</b> (RMS 0.567 Hz). The inherited 4.3 Hz BFO error scale is much larger than the difference '
  'between the 450 and 475 kt F/G fits; a 1 Hz calibration shift corresponds to about 25 kt here.')
p('<b>E’s timing and frequency need separate treatment.</b> Its 172 Hz BFO is only about 101 seconds '
  'after log-on. Holland describes roughly three minutes of oscillator settling. Trusting E’s BTO '
  'therefore does not establish a settled BFO. E is retained unchanged in the requested three-point '
  'comparison; the F/G result shows its influence. F/G are later in the settling interval, which by itself '
  'does not prove that all oscillator effects have disappeared.')
p('Sources: <link href="https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf" color="#1768ac">released SATCOM log</link>; '
  '<link href="https://arxiv.org/pdf/1702.02432" color="#1768ac">Holland, The Use of Burst Frequency Offsets in the Search for MH370</link>.','SmallX')

story.append(PageBreak())
p('Geometry and continuous trajectories','TitleX')
p('The six nominal intersections are exact solutions to the adopted BTO equation. '
  'Their displayed decimal places are for reproducibility and do not imply that the aircraft position is known this precisely.','SmallX')
rows=[]
for r in D['intersections']:
    rows.append([r['airway'],r['arc_id'],f"{r['latitude_deg']:.6f}",f"{r['longitude_deg']:.6f}",f"{r['true_track_deg']:.3f}°"])
table(['Airway','Arc','Latitude N','Longitude E','Local true track'],rows,[66,47,126,126,104],compact=True)

heading('Nominal arc centres do not form a 450–520 kt trajectory')
rows=[[r['airway'],r['interval'],f"{r['elapsed_s']:.1f}",f"{r['along_airway_nm']:.3f}",f"{r['implied_mean_groundspeed_kt']:,.1f}"]
      for r in D['nominal_intersection_timing']]
table(['Airway','Interval','Elapsed, s','Along airway, NM','Implied mean GS, kt'],rows,[66,67,106,126,104],compact=True)
p('The large F–G speeds result from treating noisy BTO arc centres as exact timed positions. '
  'None of the four constant speeds passes through all three centres at their logged times.','SmallX')

heading('Continuous fixed-speed paths allowing ±58 µs at each BTO')
rows=[]
for r in D['continuous_tracks']:
    if not r['objective'].startswith('BFO'):continue
    rows.append([r['airway'],f"{r['groundspeed_kt']:.0f}",f"{r['rms_hz']:.2f}",f"{r['rss_hz2']:,.1f}",
                 f"{r['max_abs_bto_residual_us']:.2f}",f"{r['fg_rms_hz']:.2f}"])
table(['Airway','GS, kt','EFG RMS, Hz','EFG RSS, Hz²','Max |BTO error|<br/>µs','F/G RMS, Hz'],
      rows,[66,47,84,101,95,76],highlight=(4,5),compact=True)
p('<b>All eight alternatives meet the three BTO gates, and the BFO ranking is unchanged.</b> '
  'For each speed, position along the airway at E is optimized to minimize raw E/F/G BFO RSS. '
  'Positions at F and G follow by time integration at that same speed. The ±58 µs gates are '
  'twice the adopted 29 µs R1200 timing standard deviation; they are not a joint confidence region. '
  'The listed F/G RMS is evaluated on that E/F/G-optimized path, not a separately optimized F/G path.','SmallX')
p('Model: WGS-84 geometry and local airway bearings; cubic-Hermite satellite position/velocity; aircraft '
  'and satellite Doppler; nominal-satellite aircraft precompensation; fixed oscillator and AFC terms. '
  'The independent implementation matches the saved model for all 24 point/speed cases within '
  '4 × 10⁻¹³ Hz. The ephemeris remains the project’s public-workbook transcription, not independently '
  'authenticated operator data. No route probabilities or full dynamic/fuel constraints are inferred here.','SmallX')
p('Airways and FIR limits: Malaysia AIP ENR 3.3 (3 June 2010) and ENR 2.1 (22 November 2007). '
  'The package README lists source links, provenance and the one-arcsecond NILAM coordinate convention. '
  'CSV files include all point predictions, residuals, root-sum-square values, continuous positions and timing errors.','SmallX')

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#cddbe2'));canvas.line(40,33,A4[0]-40,33)
    canvas.setFont('DV',7);canvas.setFillColor(MUTED)
    canvas.drawString(40,21,'MH370 research | Conditional level-flight BFO audit | 7 March 2014 UTC')
    canvas.drawRightString(A4[0]-40,21,str(doc.page))

pdf=OUT/'mh370_efg_airway_bfo_analysis.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=40,rightMargin=40,topMargin=34,bottomMargin=44,
                      title='MH370 E/F/G airway-constrained BFO analysis',author='MH370 research project')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(pdf)
