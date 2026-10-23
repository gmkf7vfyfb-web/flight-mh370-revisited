PRE="{{artifact:2560bf49-c8d4-4529-af25-0fc170ecca86}}"; GEO="{{artifact:7cc6bf71-1619-464e-8114-7ab7fb34b767}}"; GEOOUT="{{artifact:d17884b2-699d-4021-9157-362977dd5c3b}}"
OHAS="{{artifact:61c00103-2f41-45ac-813b-138c17723940}}"; SMAP="{{artifact:d42b5281-f142-46f6-8900-256e3a6d6283}}"
common = f"""
PROJECT: MH370 Bayesian reconstruction for a Journal of Navigation paper (researcher: Pete). Repo github.com/gmkf7vfyfb-web/flight-mh370-revisited,
work branch claude-science-sep29, live folder 'Claude Science Project Sep 29/'. Clone cheaply: git clone --depth 1 --single-branch -b claude-science-sep29
--filter=blob:none --sparse with the GITHUB_TOKEN as x-access-token; export HOME and XDG_CONFIG_HOME into your workspace; never `git ls-tree -l` (fetches 2.2 GB).
Commit as 'Claude Science <noreply@example.com>'; pull --rebase before push (several sessions push in parallel); audit staged files for *.bin, fuel-tables.json, *.xlsm.
Write results under 'Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/<your-leg>/'. Pete says some module briefs/master prompts and the
architecture thread instructions are OUT OF DATE: use their skills, code and data, but where a brief conflicts with this task or with recent rulings, follow this task.

THIS TASK: a pre-registered conditional hypothesis test of (a) Usama Kadri's 2024 (Sci Rep 14:10102) preferred H01W signal, bearing 306.18 deg, received at
00:52:03 (text branch T) or 00:54:30 (caption branch C) - BOTH branches carried; and (b) the Haixun 01 37.5 kHz contact of 4-5 Apr 2014 at 25.975 S 101.461 E.
Pre-registration (read first, follow it, do not change its statistics; if you must deviate, say so in deviations): {PRE}. Geometry script {GEO}, output {GEOOUT}.
KEY CORRECTED GEOMETRY: the 306.18 deg bearing from H01W (34.8903 S 114.1426 E) crosses the sea-level 7th arc at 25.732 S 101.369 E, R7 = 1,591.3 km.
The figure 26.2 S 101.9 E used in hydro work of 13-14 Oct is WRONG (about 74 km off along the bearing) - anything derived from it must be recomputed.
Haixun is 28.5 km from the crossing, OUTSIDE (south-east of) the arc. Haixun-as-acoustic-source times: 00:34:24 (T) / 00:36:51 (C) at c = 1.48 km/s.

PRIOR: run J. Per-impact rows on Pete's Mac at ~/Downloads/mh370-exchange/end-of-flight/run-j/ (run-j-waypoints 24 seeds P(family) 0.9982, run-j-free 18,
run-j-repro-radar 16, run-j-descent-climb 16; each seed-N/ has impacts32.npy (float32, times in s after T0 = 1394232081, columns in COLUMNS.txt/run.json),
parents32.npy, run.json, terminal.json, SHA256SUMS, tau90_v1.npz, attitude_v1.npz). Summaries in run-j/summary/ (e.g. table-0019-mixture.json). Planned descents
starting before 00:11: end-of-flight/run-j-joined-v2/J0011 and J2241 (seeds 1-21 done). Weights: option_table_0019.seed_terms from
engine/hypotheses/end-of-flight/smoke/ on branch hypothesis/end-of-flight; keep compact-columns.json beside compact_impacts.py; use engine/data/satcom-observations.csv;
core hand-off core/run-j/<family>/bto-bfo/seed-N/handoff-m0011/handoff.npy (needed for D5). Headline key 'D{{d}} total q=0.333 (C2 silent)'. A waypoints seed reduces in
about 11 s. Run J is not formally declared final by end of flight; Pete ruled enough is done to proceed - label every number with the run and the 00:19 option.
Machine: Pete's Mac, 18 cores, 64 GB, no GPU; ~/Downloads is granted rw. Keep at least 25 GiB free on the Mac. Remote compute may be listed via list_compute.

PETE'S RULES: sample the whole feasible 777-200ER space and let evidence select; report what kinds of trajectories are selected; never pre-condition on the answer.
Use standard statistical terms as such (log-likelihood, Bayes factor, 2-sigma...). Charts: titles/axes/legends without project codes; every chart has two short
footnotes - (i) plain ASD-STE100 and (ii) technical - listing source posterior, 00:19 option, physics status, search case, ocean model, exclusions. Posterior maps:
greyscale 50/90/99 % HPD. Source grades: A primary read with pages, B official cited not read, C online/community. Never fabricate a number; a quantity from
partial coverage is 'not assessed at this depth', never an absence. Pete gives standing permission to reach public websites/data the work needs.
Return: a results markdown committed to the repo AND saved as an artifact, plus figures saved as artifacts, and the structured output.
"""
schema = {"type":"object","properties":{
  "summary":{"type":"string","description":"6-12 sentence plain summary of findings for both branches T and C where relevant"},
  "key_numbers":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"value":{"type":"string"},"unit":{"type":"string"},"branch_or_case":{"type":"string"},"source_file":{"type":"string"}},"required":["name","value"]}},
  "likelihood_terms":{"type":"array","items":{"type":"object","properties":{"hypothesis":{"type":"string"},"term":{"type":"string"},"log_bayes_factor_or_ratio":{"type":"string"},"caveats":{"type":"string"}}}},
  "artifacts":{"type":"array","items":{"type":"string"},"description":"filename + version_id of each saved artifact"},
  "commit":{"type":"string"},
  "open_issues":{"type":"array","items":{"type":"string"}}},
 "required":["summary","key_numbers","artifacts","open_issues"]}

legs = [
 ("Flight","END_OF_FLIGHT_MODULE", """LEG: FLIGHT (pre-registration Q1-Q3). (1) On run J, all four families plus joined-v2 J0011/J2241, compute posterior mass in the locality L (strip and 50/100/200/400 km discs
around both centres), per 00:19 option (the four priority options), per family A1/A2/B and per log-on cause; effective sample size and distinct parents in L.
(2) Compute the pre-registered per-row acoustic likelihood L_i (H01W arrival time and bearing, s_b 0.5 and 1.0 deg) for EVERY run J impact row - not only rows
in L - for branches T and C, and report the Bayes factor against the pre-registered background and the conditional impact PDF given each branch (greyscale HPD map).
(3) Characterise the top 1 % of rows by w_i*L_i: BTO/BFO residuals at every arc incl. 00:19 options (use the run J residual/sigma convention), fuel-exhaustion time,
minutes aloft after exhaustion, turn count, family, impact speed/angle/energy/tau90/attitude, and where they sit relative to the arc (Kadri's eq. 4 implies
inside the arc for along-bearing flight; Haixun is outside). Explicitly test whether a ~15-17 min post-00:19 flight ending near 25.7 S is in the feasible set and
how it is achieved (powered flight with log-on cause other than exhaustion, piloted glide with turns, arrested dive after a steep 00:19:37 descent).
(4) Undersampling: if ESS in L is small (say <200) or the feasible region near the bearing is thin, design an importance-sampled targeted run aimed at L with exact
prior/proposal weights; run it if it fits in about 2 h locally, else write the run spec and say so. Also report fuel-exhaustion time distributions for trajectories ending in L."""),
 ("Hydro signals","HYDROACOUSTIC_MODULE", """LEG: HYDROACOUSTIC SIGNALS (pre-registration Q2 support and Q4). (1) Recompute predicted 95 % arrival windows at Perth Canyon IMOS 3376/3315, H08S and every
OHASISBIO mooring for sources at the CORRECTED arc crossing and along the bearing strip (impact times from Kadri eq. 4 with v 0-250 m/s) and at Haixun, for both
branches T and C; the old windows were built on the wrong 26.2 S 101.9 E point. State which recomputed windows the earlier 13-14 Oct searches (H08S span
1,346-1,710 s; Perth Canyon) did or did not cover, then run the existing pre-registered statistics (levels 0.3/0.1/0.05, background null) on data in hand for any
window not covered. (2) Royer: read LDO-201608 (summary in {OHAS}; full report via Google Drive file id 1oNz_mS9YlpcV7ONudQNp_HwsUBvhNLmc; royer_table5.json in
results/evidence-sweep-2026-10-17/). Answer: which 2014 OHASISBIO moorings were recording at the predicted arrival times, are their paths from L blocked
(GEBCO), do any of Royer's 20 events/6 candidates fit L under T or C, and does the possible 16 s GPS-UTC misapplication to H01W matter here. (3) Predicted
received level at each station across the impact range in run J rows within L (energy, tau90) and the coupling sweep (three decades), giving a detectability
statement per station and branch, with the two standing caveats (propagation slope misfit, coupling) attached. (4) Is Kadri's 306 deg arrival level consistent with
the predicted level at H01W for impacts in L? Do not redo the Haixun 37.5 kHz beacon physics - a parallel leg owns it."""),
 ("Beacon physics","HYDROACOUSTIC_MODULE", """LEG: HAIXUN 01 BEACON PHYSICS (pre-registration Q5) - high-frequency acoustics, separate from the sound-channel work. Establish from graded sources and compute:
(1) the recorder ULB specification (Dukane DK100 or the unit actually fitted to 9M-MRO's CVR/FDR per the Malaysian SIR 2018 / interim report 2015; frequency
37.5 +/- 1 kHz, pulse length, rate, source level, battery: FDR ULB expired Dec 2012, CVR in date); day 27-28 after 8 Mar; (2) the Haixun 01 equipment (Benthos
hand-held hydrophone, 5-80 kHz, practical range about 2,000 m, used from a rescue boat; ATSB 2017 pp.38-39) - its bandwidth, sensitivity, any directional
gain; (3) the sonar equation at 37.5 kHz from a seabed beacon at the local depth (GEBCO/AusSeabed at 25.975 S 101.461 E; settling leg will also report depth)
to a near-surface hydrophone: spherical spreading, Francois-Garrison absorption with a WOA23 March T/S profile, refraction/shadowing, ambient noise at the
reported sea state, boat self-noise; give P(detect) versus horizontal offset. (4) Geometry test: can a single fixed beacon at that depth produce a 15-min
contact and a 90-s contact the next day 2-3 km apart, given the practical range? (5) Follow-up searches: HMS Echo (6 and 8 Apr), the submarine (HMS Tireless),
any TPL/sonobuoy/Ocean Shield work near the Haixun position - positions, dates, equipment detection ranges (ATSB June 2014 Definition of Underwater Search
Areas: TPL effective 3 km, max 10 km) - and P(miss | beacon present). (6) Alternative explanations (ship equipment, other 37.5 kHz sources, marine life,
Doppler/aliasing). Report B_H = P(data | H_H)/P(data | not H_H) with an explicit prior-free statement and a sensitivity range."""),
 ("Search coverage","SEARCHED_AREAS_MODULE", """LEG: SEARCHED AREAS (pre-registration Q6) for the locality L and the Haixun point. (1) Surface/air 2014: which GA/AMSA daily boxes (387 polygons, GA ArcGIS
Search_And_Rescue_Search_Area2014; see map {SMAP}) cover L and when; apply the CSIRO-style POD treatment and the drift of floating debris from impact to each
search day (coordinate with nothing - compute it with the module's own approach, or state the drift assumption) to give a surface-search likelihood for H_K^T/H_K^C.
(2) Seabed: was the Haixun coordinate and L covered by high-resolution sonar (ATSB Phase 2, OI 2018 incl. any northern extension along the arc, OI 2025-26)?
Pete recalls a narrow +/-25 NM strip along the 7th arc searched up to about this latitude at some point (perhaps Fugro or OI 2018) - find out exactly what it
was, with primary sources, and whether it reached 25.7-26 S. Also the 2014-16 bathymetry survey (Fugro Equator, Zhu Kezhen etc.) coverage here; and whether
the data for this area is online (AusSeabed / Geoscience Australia MH370 bathymetry and backscatter, OI data). Map the coverage over L and Haixun.
(3) Seabed likelihood terms for H_K and H_H, with OI inferred areas included per Pete's 13/17 Oct rulings (grade C, labelled), rho sensitivity."""),
 ("Drift","OCEAN_DRIFT_MODULE", """LEG: DRIFT (pre-registration Q7). (1) Releases on 8 Mar 2014 at the impact times of each branch at points of L (arc crossing; strip points at 50, 100, 150,
200 km inside along the bearing; Haixun) under the module's ocean models with windage/Stokes marginalised: finds likelihood for the flaperon and other recovered
items with beaching windows, Western Australia populated-coast non-detection, and Indonesia / northern-coast non-detection, compared with the run J reference
release and with arc latitudes 20-40 S where already computed (this is a natural subset of Pete's proposed arc-latitude scan; do not run the full scan unless it
is cheap - say what you did). (2) Forward drift from L to 4-5 Apr 2014: where would floating debris be relative to Haixun and to the reported white objects
'about 90 km from the detection area' (JACC/Houston 5 Apr 2014)? Also backward drift from a 70-110 km ring around Haixun on 5 Apr to 8 Mar: does it reach
L at the branch times? The exact sighting position may come later from a sources leg - make the ring test now and leave a hook for a position. (3) Report the
log-likelihood ratios for H_K^T, H_K^C relative to the run J reference with Monte Carlo noise."""),
 ("Settling","OCEAN_SETTLING_MODULE", """LEG: SETTLING (pre-registration Q8). (1) Seabed depth (AusSeabed 150 m inside coverage, GEBCO_2026 outside, with provenance flag) at the Haixun contact,
at the second contact about 2-3 km west, at the corrected arc crossing and along the bearing strip. (2) For impacts in L (from run J rows or synthetic impacts at
the branch times with the run J impact-condition spread), the horizontal displacement on the seabed of the recorders (CVR/FDR in the aft fuselage; dense compact
objects) and of heavy parts, under GLORYS12 baseline and HYCOM sensitivity. (3) The inverse: the region of surface impact points consistent with a beacon on
the seabed within 2 km of the Haixun contact, and whether that region intersects the Kadri strip and the feasible run J impacts. Keep results small and fast."""),
 ("Sources","PAPER_CITATIONS_MODULE", """LEG: SOURCES AND SIGHTINGS. Build a graded source dossier (A/B/C with pages) answering Pete's questions: (1) Haixun 01: everything public - dates/times
(ATSB says 4 Apr first contact and next-day second about 3 km west 90 s; press says Friday/Saturday and within 2 km), exact coordinates of both contacts,
equipment, crew statements, China Maritime Search and Rescue Centre statements, JACC releases 5-8 Apr 2014, HMS Echo / HMS Tireless follow-up and their
conclusions, ATSB 2014 'Definition of Underwater Search Areas' and ATSB 2017 'The Operational Search for MH370' pp.38-39, Malaysian 2015 interim / 2018 SIR on ULB
batteries and type. (2) The white objects reported about 90 km from the detection area: who sighted them (ship, aircraft), date/time, position, how many,
were they investigated/recovered and with what outcome. (3) Satellite coverage of the locality (25-26.5 S, 100-102.5 E) after 8 Mar 2014: which optical/SAR
satellites were tasked or could have imaged it (e.g. Pleiades, SPOT, WorldView/GeoEye, TerraSAR-X, COSMO-SkyMed, RADARSAT-2, Gaofen-1, THEOS, Sentinel-1A launched
3 Apr 2014), what the 2014 search tasked where and when, and whether any archived imagery of this area for 8 Mar - mid Apr 2014 is listed in public catalogues.
Existing notes to build on (do not repeat): results/evidence-sweep-2026-10-17/research-satellite-imagery-2014.md, research-beacons-tpl-simulator-barnacles.md,
research-surface-search-pod.md. Add BibTeX entries for every source to the paper bibliography mechanism the module uses."""),
]
reqs=[{"task": common + "\n" + t, "name": n, "profile": p, "output_schema": schema} for n,p,t in legs]
res = host.delegate(reqs, wait=False)
import json; json.dump(res, open('handoff_kadri_dispatch.json','w'))
for r in (res if isinstance(res,list) else [res]): print(r.get('name'), r.get('frame_id'), r.get('status'))