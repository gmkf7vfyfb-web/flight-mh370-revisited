#!/usr/bin/env python3
"""Build the final synthesis, not a new MH370 posterior. Offline, deterministic content."""
from pathlib import Path
import json,zipfile,hashlib,platform,sys,shutil,re
from datetime import datetime,timezone
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
R=Path(__file__).resolve().parents[1]
D=R/'data'; G=R/'figures'; G.mkdir(exist_ok=True)
OUT=R/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
def dump(name,obj): (D/name).write_text(json.dumps(obj,indent=2)+'\n')
def extract_one(archive,suffix,dest):
    with zipfile.ZipFile(R/'inputs'/archive) as z:
        names=[n for n in z.namelist() if n.endswith(suffix)]
        assert len(names)==1,(suffix,names)
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(names[0]))
def loadjson(archive,suffix):
    with zipfile.ZipFile(R/'inputs'/archive) as z:
        ns=[n for n in z.namelist() if n.endswith(suffix)];assert len(ns)==1,(suffix,ns)
        return json.loads(z.read(ns[0]))
for name in ['MH370_Pleiades_three_model_overlay.png','MH370_IGOGU_trajectories_34_36S.png','MH370_search_history_by_vessel.png']:
    extract_one('MH370_Pleiades_IGOGU_reproducible.zip','figures/'+name,G/name)
extract_one('MH370_Resolution_checkpoint_18.zip','figures/northwest_band_offsets.png',G/'northwest_band_offsets.png')
extract_one('MH370_Resolution_checkpoint_18.zip','analysis/proposal_bands_not_coverage.geojson',D/'proposal_bands_REFERENCE_ONLY.geojson')
extract_one('MH370_Pleiades_IGOGU_reproducible.zip','inputs/ga_seventh_arc_reference.geojson',D/'seventh_arc_REFERENCE_ONLY.geojson')
extract_one('MH370_Pleiades_IGOGU_reproducible.zip','analysis/numerical_results.json',D/'conditional_map_results.json')
extract_one('MH370_Resolution_milestone_12h.zip','data/citations.json',D/'first_milestone_citations.json')
extract_one('MH370_Resolution_milestone_12h.zip','START-HERE.md',D/'first_milestone_START-HERE.md')
extract_one('MH370_Resolution_checkpoint_18.zip','analysis/northwest_band_audit.json',D/'northwest_band_audit.json')
M=json.loads((D/'conditional_map_results.json').read_text())
base=json.loads((D/'first_milestone_citations.json').read_text())['sources']
sources=base+[
 {'id':'S6','title':'MOT update to families, 8 March 2026','url':'https://www.mot.gov.my/en/Kenyataan%20Media/Year%202026/MH370%20Search%20Operation%202025-2026%20-%20Update%20to%20Families.pdf','use':'Reported activity totals, not actual swaths'},
 {'id':'S7','title':'CAPTION 2025-2026 Armada paths','url':'https://www.mh370-caption.net/index.php/2025-armada-78-06-paths/','use':'Unofficial vessel tracks and proposal sketches'},
 {'id':'S8','title':'Iannello, Ocean Infinity proposal, 5 March 2024','url':'https://mh370.radiantphysics.com/2024/03/05/ocean-infinity-proposes-new-search-for-mh370/','use':'Contemporary reproduced slide and presenter identification'},
 {'id':'S9','title':'ATSB Operational Search, 3 October 2017, Figure 73 / p.96','url':'https://www.atsb.gov.au/sites/default/files/media/5773565/operational-search-for-mh370_final_3oct2017.pdf','use':'Report-assigned legacy detection categories; original PDF live access failed in final pass, prior extracted inputs retained'},
 {'id':'S10','title':'GA priority contacts layer','url':'https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/MH370_Phase_2_contacts/FeatureServer/0','use':'43-record priority ledger in checkpoint 14'},
 {'id':'S11','title':'GA WFS metadata','url':'https://ecat.ga.gov.au/geonetwork/srv/api/records/8f15e5f4-0937-4ce6-bbd5-803fd27fa3ef','use':'Catalogue geometries cannot stand for sonar valid-data coverage'},
 {'id':'P19','title':'Rerun checkpoint 19, 19 September 2026','url':'https://drive.google.com/file/d/1fjN9i9VrZbfxRedaesCyS4yXl3MFZgCS/view','use':'Fuel bridge code, exact validation and continuation; source manifest verified'},
 {'id':'PM','title':'Recovered Pleiades / IGOGU map atlas','url':'https://drive.google.com/file/d/1j5xi29Y4WgJs0WmeFBu8C6FZB8F1hYte/view','use':'Conditional mixture and provisional trajectory selection, not wreckage posterior'},
]
dump('citations.json',{'retrieved_or_rechecked_date':'2026-09-19','sources':sources})
changes=[
 {'topic':'Working region','first_milestone':'34-36 S near the seventh arc, emphasis near 35 S','final':'Unchanged as a qualitative pre-search working region; not a demonstrated residual maximum','why':'No calibrated geographic posterior or authoritative recent coverage layers became available'},
 {'topic':'Search recommendation','first_milestone':'Finish the 7,428.54 km2 official remainder','final':'Completion remains a practical candidate, not an established scientific optimum; 71.46 km2 balance unallocated','why':'Contract status is not locational likelihood; current boundaries, swaths and quality masks are missing'},
 {'topic':'Northwest proposal band','first_milestone':'Uncertain public proposal geometry','final':'2024 presentation provenance recovered; NW sketch 6,327.75 km2, about 54-80 km from CAPTION reference arc','why':'Reproduced Nathan presentation slide plus ellipsoidal geometry audit; not a current contract map'},
 {'topic':'Negative-search evidence','first_milestone':'Coverage/detection calibration missing','final':'43 priority contacts reconciled; dependent-repeat model controlled; reject cellwise use of 94% aggregate','why':'GA public ledger and ATSB categories sharpen the audit but do not supply cell-level operational detection calibration'},
 {'topic':'Estimator','first_milestone':'Physical guide compile and K=1 implementation gates open','final':'Later Rerun source records compiled affected tests and feed-resolved no-reset fuel boundary; full stochastic bridge still absent','why':'Checkpoint 19 verified source/logs and five independent Python tests replayed; no calibrated replacement estimator'},
 {'topic':'Conditional overlap','first_milestone':'No integrated Pleiades/IGOGU atlas in milestone','final':'Three-model equal-weight mixture and retained IGOGU endpoints overlap broadly, but not a validated impact PDF','why':'Recovered numerical grids and paths; conditional assumptions and shared observations prevent independent-vote counting'},
 {'topic':'Hydroacoustics','first_milestone':'Unvalidated alternatives; excluded from core weighting','final':'Still excluded from baseline; A/E/F attribution, CL/DG intersection and impact-to-arrival work remain pending','why':'No completed, validated A/E/F plus impact-model result was available in recovered final snapshot'},
]
dump('changes_from_first_milestone.json',changes)
decisions=[
 {'id':'FINAL-D01','decision':'Retain 34-36 S / roughly 35 S only as provisional synthesis','calibrated_probability':None,'exact_coordinate':None},
 {'id':'FINAL-D02','decision':'Do not claim contractual remainder is optimal or identify it with NW sketch','operational_polygon':None,'budget_km2':7500,'official_remainder_km2':7428.54,'unallocated_arithmetic_balance_km2':71.46},
 {'id':'FINAL-D03','decision':'Supersede checkpoint14 cellwise 16.67x inference; aggregate rating requires spatial weighting','basis':'negative_search_scale_correction.json'},
 {'id':'FINAL-D04','decision':'Keep conditional models separate; no product of alternative drift PDFs; no acoustic assimilation'},
 {'id':'FINAL-D05','decision':'No full physical sampler or impact model was run by this synthesis; software controls are not empirical calibration'},
]
dump('decision_log.json',decisions)
evidence=[
 {'id':'F-E01','claim':'Broad region is inherited evidence synthesis, not new calibrated posterior','source_ids':['S1','S2','S3'],'role':'qualitative synthesis','dependency':'SATCOM, aircraft assumptions and drift reused across published hypotheses'},
 {'id':'F-E02','claim':'7,428.54 km2 official remainder, extension to 30 June 2027','source_ids':['S5','S6'],'role':'official program accounting','limitation':'No actual boundary or swath geometry supplied'},
 {'id':'F-E03','claim':'43 priority contacts, 41 class2 plus 2 class1; both class1 resolved','source_ids':['S9','S10'],'role':'legacy contact audit','limitation':'Not the complete 661-contact or 82-investigation ledger'},
 {'id':'F-E04','claim':'94% nominal area-weighted rating, not arbitrary-cell detection floor','source_ids':['S9'],'role':'new exact arithmetic correction','limitation':'No blind calibration; nonuniform location prior changes footprint average'},
 {'id':'F-E05','claim':'Catalogue envelopes and vessel tracks are not valid-data swaths','source_ids':['S7','S11'],'role':'rejected proxy evidence','limitation':'Current OI quality coverage unavailable'},
 {'id':'F-E06','claim':'NW proposal geometry and dated source chain recovered','source_ids':['S7','S8'],'role':'conditional geography','limitation':'Full original deck and digitisation uncertainty unavailable'},
 {'id':'F-E07','claim':'Pleiades equal-model mixture peaks near 35.22S 92.25E','source_ids':['PM'],'role':'conditional model only','limitation':'Object identity unverified, grid truncated, family weights uncalibrated'},
 {'id':'F-E08','claim':'119088 retained IGOGU draws overlap mixture 90% region after kinematic continuation and R600 gate','source_ids':['PM'],'role':'separate terminal sensitivity','limitation':'Subset ESS about77; no impact simulation or baseline incorporation'},
 {'id':'F-E09','claim':'Feed-resolved fuel adapter checks anchor without reset','source_ids':['P19'],'role':'software/identity control','limitation':'Full stochastic aircraft proposal not run'},
 {'id':'F-E10','claim':'A/E/F hydroacoustic attribution and predicted impact/arrival PDF unestablished here','source_ids':[],'role':'pending research','limitation':'Do not label geographic intersections as measured source coordinates'},
]
dump('evidence_registry.json',evidence)
queue=[
 {'rank':1,'task':'Recover authoritative contract geometry and 2018/2025-26 AUV swaths, valid-data/quality masks, contacts and dispositions','acceptance':'Reconcile geodesic union and dates to official accounts; map shadows/LPD and repeated passes; never buffer AIS'},
 {'rank':2,'task':'Implement stochastic radar-to-anchor aircraft path emitting the exact powered fuel segments; attach correct bridge ratios','acceptance':'Synthetic recovery then matched-budget multi-seed physical tests; row/root ESS, evidence dispersion, CDF and coverage; no duplicate likelihood or fuel prior'},
 {'rank':3,'task':'Reconcile canonical SITA bursts, shared calibration, early radar provenance and fuel initial state','acceptance':'Channel/timing/units and covariance audit, nuisance calibration model, raw radar provenance and broad radar-boundary sensitivity'},
 {'rank':4,'task':'Validate end-of-flight dynamics as separately labelled conditional branch','acceptance':'Carry weighted terminal state including altitude/attitude/velocity/fuel/control uncertainty; compare uncontrolled descent, recovery/glide; preserve 00:19 timing-only baseline'},
 {'rank':5,'task':'Recover A/E/F source picks, array channels, timing uncertainty and bearing definition; predict CL/DG propagation from impact scenarios','acceptance':'Blind background days and shifted windows; bathymetry/sound speed/receiver response; coupling uncertainty; no tuning to chosen events; report hypotheses not attribution'},
 {'rank':6,'task':'Blind-validate debris drift and negative-search detection','acceptance':'Held-out trajectories/objects, windage and observation process; alternative model weights and outside-strip mass; correlated repeat misses and changed-aspect controls'},
 {'rank':7,'task':'Optimize and stress-test next 7500 km2 only after inputs pass gates','acceptance':'Calibrated prior times miss likelihood times conditional new detection per cost; outside-domain mass; compare near-arc/NW/SE; report regret and sensitivity'},
]
dump('research_priorities.json',queue)
dump('operational_search_recommendation.geojson',{'type':'FeatureCollection','name':'NO_OPERATIONAL_POLYGON_ESTABLISHED','features':[],
 'properties':{'status':'Blocked pending validated coverage and calibrated location/detection model','budget_km2':7500,'official_remainder_km2':7428.54,'NW_sketch_is_remainder':False,'warning':'Empty intentionally. Reference layers are not survey tasking polygons.'}})
dump('state_final.json',{'date':'2026-09-19','location':'34-36 S provisional, roughly35 S emphasis','geographic_posterior_calibrated':False,'operational_7500_polygon_established':False,
 'latest_resolution_checkpoint':18,'latest_estimator_checkpoint':19,'baseline':{'BTO_BFO_end':'00:11','0019':'timing only','fuel_jettison':False,'P627':'separate','WSPR':'zero locational weight pending blind calibration'},
 'conditional_maps':'included without reweighting baseline','impact_PDF':'not validated or created here','completed_controls':'see replay_results.json','original_sources_modified':False})
dump('inspected_vs_unread_inventory.json',{'inspected_in_final_synthesis':['First milestone summary, state, evidence and priorities','Resolution18 START/state/geometry and reproduction','Resolution13-14 search-decision/legacy-contact analyses','Pléiades/IGOGU assessment, numerical outputs and validation','Rerun19 START/findings/continuation, source manifest and test logs','Official MOT June29 and March8 statements freshly checked','CAPTION map provenance and contemporary slide reproduction','Archived01 reproduction contract and manifest'],
 'archived_not_fully_reread':['Checkpoint01 literature and 2310-file source inventory','All Resolution02-11 ZIP members; byte integrity not content review','Complete Rerun19 source tree; manifest verification not whole-code review','All prior model alternatives and raw source files'],
 'unavailable_or_pending':['Authoritative OI recent contract/survey/quality/contact GIS','Primary radar plots and sensor covariance','Canonical SITA burst package beyond recovered derivatives if separately held','Full original March2024 slide deck/recording','Validated stochastic aircraft/impact model','Completed A/E/F source identification and CL/DG propagation products'],
 'folder_snapshot':'resolution_folder_snapshot.json','inventory_warning':'No claim of exhaustive review or full download of historical project.'})
dump('failure_log.json',[
 {'item':'Personal context service','result':'Unavailable in this conversation','response':'Used actual Drive and local checkpoints'},
 {'item':'ATSB operational-search PDF fresh web open','result':'Internal error','response':'Preserved prior hashed extracted category inputs; no claim of new full-PDF inspection'},
 {'item':'Latest swaths/quality masks','result':'Not recovered','response':'No operational polygon fabricated'},
 {'item':'Full physical estimator and impact PDF','result':'Not completed','response':'Retained provisional/conditional labels'},
 {'item':'A/E/F request','result':'No completed source-specific assessment recovered in final snapshot','response':'Explicit next research task, not supplied as measured bearings'},
])
dump('environment.json',{'python':sys.version,'platform':platform.platform(),'matplotlib':matplotlib.__version__,'random_seed':None,'stochastic_run':False})
# A new scientific diagnostic visual, deliberately independent of geographic posterior.
fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained')
names=['High confidence cell','Lower confidence cell','Data-gap cell','Uniform footprint average']
vals=[.05,.30,1,.06]; ax.barh(names,vals,color=['#236d85','#e09b3c','#aa4651','#8199a4'])
for i,v in enumerate(vals):ax.text(v+.014,i,f'{100*v:g}%',va='center',fontsize=12)
ax.invert_yaxis();ax.set_xlim(0,1.13);ax.set_xlabel('Nominal miss likelihood under report-assigned categories')
ax.set_title('An area average is not a cellwise detection bound',loc='left',fontweight='bold');ax.spines[['top','right']].set_visible(False)
fig.savefig(G/'negative_search_scale_correction.png',dpi=180);plt.close(fig)
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/fonts/DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('Body-Bold',str(R/'assets/fonts/DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body',boldItalic='Body-Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='T',fontName='Body-Bold',fontSize=22,leading=27,textColor=colors.HexColor('#17364b'),spaceAfter=14))
styles.add(ParagraphStyle(name='H',fontName='Body-Bold',fontSize=13,leading=17,textColor=colors.HexColor('#21687a'),spaceBefore=9,spaceAfter=7))
styles.add(ParagraphStyle(name='B',fontName='Body',fontSize=10,leading=14,spaceAfter=7))
styles.add(ParagraphStyle(name='S',fontName='Body',fontSize=8,leading=10.5,spaceAfter=5,textColor=colors.HexColor('#4b5962')))
def p(t,kind='B'):
    # Clean compact numeric prose, without touching URLs or identifiers.
    for old,new in [('through00','through 00'),('baseline00','baseline 00'),('at00','at 00'),('to00','to 00'),('gated00','gated 00'),('with89','with 89'),('and72','and 72'),('the18','the 18'),('the213','the 213'),('of4.63','of 4.63'),('about77','about 77'),('about345','about 345'),('contains21','contains 21'),('01-18','01-18'),('SHA256 matches02','SHA256 matches 02'),('Checkpoint01','Checkpoint 01'),('Rerun19','Rerun 19'),('entries and12','entries and 12'),('tests and12','tests and 12'),('all21','all 21'),('the161','the 161'),('its337','its 337'),('Northwest2024','Northwest 2024')]:
        t=t.replace(old,new)
    return Paragraph(t,styles[kind])
def footer(c,d):
    c.setFont('Body',8);c.setFillColor(colors.HexColor('#647480'));c.drawString(40,22,'MH370 Resolution | Final milestone | 19 September 2026 | Provisional research')
    c.drawRightString(d.pagesize[0]-40,22,str(d.page))
def pdf(name,story,wide=False):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=landscape(A4) if wide else A4,leftMargin=40,rightMargin=40,topMargin=32,bottomMargin=39,title='MH370 Resolution final milestone',author='MH370 research synthesis',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
def figimg(name,width=748,height=335):
    im=PILImage.open(G/name);w,h=im.size;s=min(width/w,height/h);return Image(str(G/name),width=w*s,height=h*s)
def refs(ids):
    return p('Sources: '+'; '.join(f'<link href="{escape(s["url"])}" color="#21687a">{escape(s["id"]+" - "+s["title"])}</link>' for s in sources if s['id'] in ids),'S')
summary=[p('MH370 Resolution','T'),p('Final milestone - decision summary','H'),p('The working region remains <b>34-36 degrees S, emphasizing roughly 35 degrees S near the seventh-arc corridor</b>. This is a provisional synthesis, not an exact coordinate, a calibrated probability distribution, or a demonstrated maximum after all searches.'),
 p('Why this region','H'),p('The retained case combines published satellite/flight feasibility with debris drift and surface-search evidence. Those analyses share data and assumptions; overlapping conditional hypotheses are not independent votes. Recent search coverage is still too poorly resolved to compute the residual optimum.'),refs(['S1','S2','S3']),
 p('What to search next','H'),p('Completing the official <b>7,428.54 km2 remainder</b> is a practical candidate, <b>not a demonstrated scientific optimum</b>. The remaining 71.46 km2 of a 7,500 km2 budget stays unallocated until validated gaps, contacts or changed-aspect repeat opportunities can be ranked. The northwest proposal sketch is not established as that remainder. No operational polygon is supplied.'),refs(['S5','S6','S7']),
 p('Most important correction','H'),p('The earlier 94% legacy detection rating is an area-weighted calculation. It cannot be applied to every searched cell. Under the report-assigned categories, nominal miss likelihood is 5% for a high-confidence cell, 30% for a lower-confidence cell and 100% for a gap. Actual location and detection weights remain uncalibrated.'),
 p('What changed since the first milestone','H'),p('The search recommendation is more qualified; public geometry and negative-search pitfalls are better diagnosed; the fuel-bridge implementation has progressed; and a conditional Pléiades/IGOGU atlas is now integrated. The broad working region has not changed.'),PageBreak(),
 p('What the new evidence does - and does not - show','T'),
 p('Conditional geographic overlap','H'),p('The equal-weight BRAN2016, OSCAR and GLORYS12/WAVERYS mixture peaks near <b>35.22 S, 92.25 E</b>, conditional on the photographed-object hypothesis and specified drift assumptions. About 5.4% of that model mass is inside the northwest sketch and 2.4% inside the southeast sketch. These are not calibrated wreckage probabilities.'),
 p('The recovered IGOGU measure includes 119,088 draws in the mixture\'s 90% region after an assumed continuation to 00:19 and an R600 sensitivity gate. Their effective sample size is only about 77. No tested gated 00:19 position lies within either proposal sketch; that does not exclude a later impact there. The paths are not validated impact trajectories.'),refs(['PM']),
 p('Estimator progress','H'),p('Rerun checkpoint 19 has a feed-resolved powered fuel adapter that checks the 18:28 anchor without a reset. Its archived affected Rust log records 161 passing tests; five independent Python tests were rerun successfully for this synthesis. A full stochastic aircraft bridge and replacement geographic estimator remain unvalidated.'),refs(['P19']),
 p('Research priorities','H'),p('1. Obtain authoritative AUV coverage, quality masks, contract boundaries and contact dispositions.<br/>2. Finish and validate the stochastic aircraft bridge; reconcile canonical satellite bursts, shared calibration and radar provenance.<br/>3. Validate a separate end-of-flight model, then test hydroacoustic A/E/F attribution and CL/DG arrival predictions with blind controls.<br/>4. Calibrate drift and repeat-search detection before optimizing the 7,500 km2 allocation.'),
 p('Completed work and limitations','H'),p('This final synthesis verified the initial archive hash, assembled 21 dependency archives, checked 213 Rerun source-manifest entries, replayed five Python tests and passed 12 new exact arithmetic controls. No new physical particle-filter or impact simulation was run. This is not a claim of 18 hours of uninterrupted computation. The A/E/F chart and validated impact/acoustic PDF remain outstanding.'),
 p('Read the illustrated detailed report and START-HERE_final.md for changed conclusions, source links, failure records and exact continuation gates. All prior milestone versions are preserved.','S')]
pdf('MH370_Resolution_final_summary.pdf',summary)
story=[]
def page(title,paras,image=None,ids=None):
    if story:story.append(PageBreak())
    story.append(p(title,'T'))
    for t in paras:story.append(p(t))
    if image:story.append(figimg(image))
    if ids:story.append(refs(ids))
page('Final assessment: a region, not a solved location',[
 '<b>Answer A:</b> Retain 34-36 S near the seventh-arc corridor, with emphasis around 35 S, as the best-supported qualitative working region in the inspected record. No exact coordinate or numerical wreckage probability is justified. This is not necessarily the highest residual density after all sonar searches.',
 'The rationale is the overlap of published SATCOM/flight feasibility, endurance assumptions, and the CSIRO debris/surface-search synthesis. Published analyses are not independent votes. Their common measurements, priors and modelling choices must be represented once in a joint analysis.',
 '<b>Answer B:</b> Completion of the official 7,428.54 km2 remainder is a practical action to compare with alternatives, not a proved optimum. No authenticated remaining-area polygon or complete 2018/2025-26 quality mask was recovered. Reserve the arithmetic 71.46 km2 balance rather than drawing an arbitrary rectangle.',
 '<b>Answer C:</b> Coverage/detection data and a validated physical estimator are joint decision gates. Terminal modelling, acoustic attribution and drift controls are subsequent, explicitly separated research branches.',
 'The requested milestone documentation is complete; the calibrated impact posterior and operational 7,500 km2 polygon are not. The latest detailed record reviewed is Resolution checkpoint 18 and Rerun checkpoint 19, plus the recovered conditional atlas.'],ids=['S1','S2','S3','S5','P19'])
page('Search decision: use detection conditional on earlier misses',[
 'For location x, the post-search weight is proportional to its pre-search weight multiplied by P(previous misses | x). A new action is valued by integrating that residual weight times P(new detection | x, previous misses, action), then accounting for mission cost. The unconditional single-pass detection rate is not generally valid for repeat searches.',
 'Checkpoint 13 supplies 23 exact synthetic controls, including a ranking reversal caused by shared blind spots. These demonstrate the mathematical failure mode; they are not estimated MH370 detection probabilities.',
 'The official June 29 statement confirms 7,428.54 km2 remaining and an extension through June 30, 2027. March 8 reported approximately 7,571 km2 surveyed under the contract. Their arithmetic agreement does not provide a geographic union, unique new coverage, or a sonar quality map.',
 'Practical decision gate: authenticate contract boundary; reconcile 2018 and 2025-26 valid-data swaths; carry low-quality/shadow polygons and contacts; calibrate conditional detection; compare near-arc, northwest, southeast and outside-region alternatives under explicit location priors. Do not assume all useful area lies inside this working band.',
 '<b>Operational output:</b> the supplied operational GeoJSON has an intentionally empty feature set. Proposal-band and reference-arc layers are supplied separately, explicitly prohibited for search tasking.'],ids=['S5','S6','S9','S11'])
page('Correction: 94% does not apply to every cell',[
 'The report-assigned arithmetic is 0.974 x 0.95 + 0.021 x 0.70 + 0.005 x 0 = 0.94. It is an area average for a uniformly distributed target over that footprint. Checkpoint 14 overgeneralized its reciprocal miss ratio to arbitrary cells; this final milestone supersedes that interpretation.',
 'With equal pre-search cell density and these nominal category values, unsearched-to-searched retained-density ratios are 20, 3.33 and 1 for high-confidence, lower-confidence and gap cells. The 16.67 ratio applies only to a uniform mixture with the reported category proportions, not each cell. A prior concentrated in gaps can have a miss likelihood of 1.',
 'The new 12 exact controls verify arithmetic and a nonuniform-prior counterexample. Operational ratings still lack blind calibration, and spatial masks are required.'],image='negative_search_scale_correction.png',ids=['S9'])
page('Legacy contacts and rejected coverage shortcuts',[
 'Checkpoint 14 reconciles the public priority-contact ledger: 43 unique records, comprising 41 class-2 and two class-1 contacts. Both class-1 objects were resolved as a shipwreck and geology. This is not a complete 661-contact or 82-investigation case ledger. Blank reacquisition fields alone do not establish unresolved contacts.',
 'Checkpoint 16 rejects the Go Phoenix catalogue rectangle as a valid-data swath. The catalogue union is about 2.49 times the mosaic valid-image area; an apparent 99.6% corridor-coverage result is deprecated. Raster pixel presence is itself not calibrated detection, and merged mosaics hide aspect and pass-quality information.',
 'Checkpoint 17 found the two CAPTION bands total 15,812.26 km2, about 5.42% above the nominal 15,000 km2 contract. CAPTION says their precise coordinates were unknown. This difference and their 2024 provenance prevent equating them with the subsequently contracted area.',
 'The new map uses all three CAPTION expeditions, with vessel names and dates. Armada 86-05 Phase 3 was included in the earlier chart despite its confusing official-phase label. Neither support-vessel position nor its absence establishes submerged-AUV coverage.'],ids=['S7','S9','S10','S11'])
page('Search history: vessel activity, not sonar coverage',[
 'All three recovered CAPTION expeditions are shown. The Phase 3 file has records from December 23, 2025 to January 28, 2026 including transit; its filename advertises a narrower interval. Gaps over 12 hours are not joined. The uncertain white-band reconstructions are not the remaining contract area.'],image='MH370_search_history_by_vessel.png',ids=['S7','S8'])
page('Northwest band: provenance and physical questions',[
 'A contemporary March 5, 2024 account reproduces an Ocean Infinity-branded proposal map and identifies V.P.R. Nathan as the March 3 presenter. CAPTION digitised the bands from that presentation; the original full deck/recording and geographic registration remain unverified.',
 'The NW sketch is 6,327.75 km2. Sampled offset is 54.1-80.4 km from CAPTION\'s 20,000-ft reference arc, versus 62.8-89.1 km from GA\'s 40,000-ft arc. Provider and altitude both differ. At assumed 250 kt, the first range is 7.0-10.4 minutes of straight travel; it is not a descent simulation or impossibility proof.'],image='northwest_band_offsets.png',ids=['S7','S8'])
page('Conditional drift overlap: three alternatives, not three votes',[
 'Each BRAN2016, OSCAR and GLORYS12/WAVERYS source surface is normalized, then mixed with one-third weight. The mode is near 35.22 S, 92.25 E on a 5-NM grid. Density-ranked 50/90/99% areas are about 9,518 / 28,768 / 48,833 km2 within the declared source strip.',
 'The source hypothesis assigns one latent associated object across twelve rating-5 locations; the objects are not identified wreckage. Shared observations prohibit multiplying the three models as independent evidence. Outside the strip is uncomputed, not zero.'],image='MH370_Pleiades_three_model_overlay.png',ids=['PM'])
page('IGOGU paths: fuel exhaustion is not impact',[
 'Among 1,710,701 retained unequal-weight draws, 119,088 reach the mixture\'s 90% contour and pass the separate R600 gate after the stated 00:19 continuation (8.10% of original weight; subset ESS about77). The complete measure has ESS about345 and a largest individual weight of4.63%. These are model diagnostics, not calibrated probabilities.',
 'The 74 displayed paths end solid at fuel exhaustion; dashed segments hold horizontal speed, course and altitude to00:19:29. None of the tested gated00:19 endpoints falls in either proposal sketch. Later impact in a sketch is not excluded: that later segment was not simulated.'],image='MH370_IGOGU_trajectories_34_36S.png',ids=['PM'])
page('Core flight model and satellite calibration',[
 'The baseline remains BTO/BFO through00:11,00:19 timing only, and no fuel jettison. Reference arc geometry and the R600 gate in the atlas are diagnostic terminal sensitivities, not silently incorporated baseline observations. P627 and IGOGU remain separate conditional route hypotheses.',
 'BTO/BFO observations share nuisance calibration, satellite/aircraft state assumptions and channel/timing corrections. A defensible likelihood must retain those dependencies. The canonical SITA burst record and independent radar provenance remain priority targets; a derivative merged track must not become independent radar evidence.',
 'First-milestone wording that simply required compiling the guide is now stale. Rerun19 includes an affected Rust test log with89 end-of-flight and72 estimator tests passing. Its feed-resolved adapter propagates reconstructed radar fuel to the18:28:05.9 anchor and fails closed rather than resetting. The213-file manifest was verified and five independent Python tests replayed here.',
 'Still missing: a stochastic aircraft-path proposal producing those powered segments, attached to correct bridge weights without double likelihoods; exact synthetic recovery; and matched-budget multi-seed physical comparison. Terminal proposals must be importance-corrected. The user\'s00:15-00:17 exhaustion support and the recovered00:15-00:19 support are different hypotheses, not interchangeable data.',
 'Ancestry concentration can reflect a proposal bottleneck, true constraint or both. Root/row ESS, evidence dispersion and repeated-seed recovery are required to distinguish them. A large raw draw count cannot certify calibration.'],ids=['S1','P19','PM'])
page('Hydroacoustics and impact: next branch, not a current result',[
 'The latest A/E/F question is preserved as unfinished work. This milestone has not established what each letter denotes, a measured Cape Leeuwin bearing for each, a valid bearing intersection, or a joint CL/DG arrival window. No association with MH370 is inferred from a visually interesting location.',
 'First recover the underlying figure, event IDs, raw channels, time standards, picks, array geometry and bearing convention. Distinguish measured back-azimuths from drawn hypotheses. Intersections need uncertainty wedges and a propagation model, not just crossing straight lines.',
 'Then propagate weighted terminal aircraft states through validated end-of-flight branches. Retain impact time, velocity vector, mass, angle and fragment/contact assumptions. An assumed constant-altitude extension is not a glide; a surface impact distribution is not yet the seafloor wreckage distribution.',
 'For acoustic prediction, keep energy budget separate from acoustic coupling and propagation loss. Carry bathymetry, sound-speed structure, blockage, multipath and receiver response. Pre-register arrival/bearing windows before waveform inspection; compare blind background days, shifted windows and non-aircraft events. Do not choose coupling or travel-time parameters merely to hit A/E/F.',
 'Known Java-event, Cape Leeuwin-candidate, controlled-glide, magnetic and WSPR claims remain separately inventoried alternatives. None receives new locational weight here. WSPR specifically needs calibrated detection and false-positive rates from blind known-route controls.'],ids=['S1','P19','PM'])
page('Changes since the first milestone',[
 '<b>'+escape(c['topic'])+'</b>: '+escape(c['final'])+'<br/><font color="#60717b">Why: '+escape(c['why'])+'</font>' for c in changes])
page('Priorities, reproduction and honest completion',[
 '<b>'+str(q['rank'])+'. '+escape(q['task'])+'</b><br/>'+escape(q['acceptance']) for q in queue])
page('Provenance and continuation contract',[
 'The portable bundle contains21 immutable dependency archives: Resolution01-18, the first milestone, the conditional atlas package and Rerun19. It also contains the new report code, exact correction controls, registries, inventories, decisions, failures, geospatial reference layers and hashes. The preserved initial archive SHA256 matches02b4d20e2766ec6ca387201a910506670dece4cc48877ca27121f3c97db899c2.',
 'Archive integrity is not scientific validation or evidence that every file was reread. Checkpoint01\'s219 manifest entries and Rerun19\'s213 were verified; all21 ZIPs passed CRC checks. The five Python replay tests and12 new exact controls pass. The161 Rust passes are verified historical logs, not new Rust execution by this synthesis.',
 'This is a complete final-synthesis and continuation package for work actually preserved here, not a complete download of every historical source or weather field. The atlas includes finite measures and selected paths but not its337MB upstream weather binary or all original sampler runs. Some third-party literature remains retrieval references, not bundled full text.',
 'Run code/verify_bundle.py before replay. Then code/audit_and_stage.py reproduces the new arithmetic and Python fuel checks; code/build_reports.py regenerates reports from shipped archives. Consult each nested REPRODUCE for older analyses. No surviving process is assumed. Preserve source files; work in a new candidate directory.',
 'No third-party correspondence was sent. No new physical flight simulation, acoustic assimilation or validated impact PDF was completed in this final synthesis. Publication receipts, hashes and the remaining tasks distinguish actual work from future intent.'],ids=['S5','P19','PM'])
page('Sources and claim boundaries',[
 f'<b>{escape(s["id"])}.</b> <link href="{escape(s["url"])}" color="#21687a">{escape(s["title"])}</link> - {escape(s.get("use",""))}' for s in sources])
pdf('MH370_Resolution_final_detailed.pdf',story,True)
summary_md='''# MH370 Resolution - final milestone summary

19 September 2026. Provisional research; no confirmed wreckage location.

## Best-supported working region

34-36 S near the seventh-arc corridor, emphasizing roughly35 S. This is unchanged as a qualitative synthesis of published flight/satellite and debris/surface-search evidence. No exact coordinate, calibrated probability or residual post-search maximum is established.

## Next 7,500 km2

Completion of the official7,428.54 km2 remainder is a practical candidate, not a demonstrated scientific optimum. The71.46 km2 arithmetic balance remains unallocated. Actual contract boundaries, AUV swaths, quality masks and contact dispositions are still required. The NW2024 proposal sketch is not established as the remainder. The operational GeoJSON is intentionally empty; reference layers are not tasking geometry.

## Principal changes

- Corrected earlier overstatement that finishing the contract is necessarily optimal.
- Corrected checkpoint14: the94% legacy detection rating is a uniform-area average, not a lower bound for every cell. Nominal cellwise miss rates are5%,30%,100% for the three report categories; these are not blind calibration results.
- Integrated the three-model conditional drift mixture and provisional IGOGU paths, without treating overlap as independent evidence or impact probability.
- Updated estimator progress to Rerun19's feed-resolved no-reset boundary; full stochastic bridge remains unvalidated.
- Preserved the A/E/F and CL/DG acoustic request as pending, without inventing bearings, intersections or impact predictions.

## What was actually completed

Final synthesis assembled21 dependency archives, verified the initial hash and source manifests, replayed five independent Python fuel tests, and passed12 new exact correction controls. The161 Rust passes belong to the archived checkpoint19 log and were not rerun here. No new physical sampler or impact/acoustic simulation was run. This is not18 hours of uninterrupted computation.

Read output/pdf/MH370_Resolution_final_summary.pdf and the illustrated detailed report. Machine-readable decisions, change comparison, priorities, inventory and failure records are in data/. See REPRODUCE.md for portable replay and missing upstream inputs.
'''
(R/'START-HERE_final.md').write_text(summary_md)
(R/'SUMMARY_final.md').write_text(summary_md)
(R/'REPRODUCE.md').write_text('''# Portable final milestone

Verify before running: `python code/verify_bundle.py` from this directory.
Run `python code/audit_and_stage.py` to verify archive CRCs, reproduce12 exact controls and replay five independent Python fuel tests from the included Rerun19 source.
Run `python code/build_reports.py` to regenerate the two PDFs and reference outputs using only shipped ZIP inputs. Python packages: matplotlib, reportlab, pillow. Additional nested analyses have their own requirements and REPRODUCE files. No random sampling occurs in the new final report code; random_seed is null.

The ZIP contains all Resolution checkpoint01-18 snapshots, first milestone, conditional map package, Rerun19 and this final synthesis. Their code/configs/seeds/outputs are retained as published. Nested archives intentionally preserve previous versions. New report PDFs are deterministic with invariant metadata; compare numerical assertions if library versions differ.

The snapshot is complete for this synthesis and its recorded calculations, NOT for every historical project run. The337MB weather binary and full original IGOGU inference runs require the upstream IGOGU conditional archive; source ID is in the nested assessment. Raw current sonar masks, primary radar and validated aircraft/impact inference are unavailable. Referenced third-party literature may require fresh retrieval. Do not confuse archive integrity with full content inspection or scientific validation.

Continue from data/research_priorities.json and the newest provider checkpoint. Keep baseline00:11 BTO/BFO,00:19 timing-only and no jettison. Conditional terminal R600, drift, P627/IGOGU and acoustic studies stay separate. Never treat operational reference layers as a7,500km2 tasking polygon. Never treat prior totals or AIS as sonar coverage. Do not contact third parties without separate authorization.

Publication receipts are added after document creation and stored outside the immutable bundle to avoid self-referential hashes.
''')
dump('actual_work_log.json',{'started_utc':'2026-09-19T20:19:01Z','report_build_finished_utc':datetime.now(timezone.utc).isoformat(),'work':'Recovery, fresh official-source checks, synthesis, exact arithmetic correction, archive integrity, Python fuel replay, PDF build and visual QA. Not continuous18-hour compute.', 'physical_inference_runs_this_synthesis':0})
print('Built final summary and detailed report.')
