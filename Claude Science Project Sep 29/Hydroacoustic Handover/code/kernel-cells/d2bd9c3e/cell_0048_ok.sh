cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/windows_run_j"
python - <<'EOF'
import csv, json, time
rows=list(csv.DictReader(open('windows.csv'))); cov=list(csv.DictReader(open('coverage.csv'))); req=list(csv.DictReader(open('request_windows.csv')))
ess=json.load(open('ess.json')); run=json.load(open('run.json'))
ON={"D0":"00:19 Held Out (D0′)","D2":"00:19 R600 BTO + BFO (D2)","D3":"00:19 both BFOs as recorded (D3, Holland H2 data)","D4":"00:19 both BFOs, shared start-up offset (D4, Holland H1 data)"}
RXL={r['receiver']:r['receiver_label'] for r in rows}
def R(rx,o,p,b): return [r for r in rows if r['receiver']==rx and r['option']==o and float(r['p'])==p and r['branch']==b][0]
def C(rx,o,p,b): return [c for c in cov if c['receiver']==rx and c['option']==o and float(c['p'])==p and c['branch']==b][0]
def Q(rx,o,p,b): return [r for r in req if r['receiver']==rx and r['option' if False else 'branch']==b and float(r['p'])==p][0]
L=[]; w=L.append
w("# Hydroacoustics: arrival windows on run J (block 3, timing half; block 6 timeline charts)\n")
w(f"*Hydroacoustic Module (run J windows track), {time.strftime('%d %b %Y %H:%M UTC', time.gmtime())}. Unattended overnight run of work order 2026-10-21. "
  "Pre-registration `prepare/run_j_windows.py` committed at bc99b07 before any run; amendment 1 (plumbing only: subprocess workers instead of a process pool, "
  "the sandbox forbids POSIX semaphores) disclosed in the docstring. Data: `results-data/windows_run_j/` on `hypothesis/hydroacoustics` (windows.csv, coverage.csv, "
  "request_windows.csv, ess.json, run.json); per-seed histograms in `mh370-exchange/hydroacoustics/run-j-windows/` (153 MB).*\n")
w("**Status: PREDICTIVE, NOT CALIBRATED.** These are timing windows only. No level, no detection and no likelihood is claimed; caveats C1 (propagation slope misfit, "
  "+10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; η swept over four decades) apply to any level statement built on them. "
  "The level/power-screen half of block 3 waits for the TL grid of the parallel track. Both Kadri times are carried everywhere: \"text time 00:52:03\" and \"caption time 00:54:30\".\n")
w("## Inputs and method\n")
w(f"- Impact set: end of flight **run J**, four strata, 74 seeds, {run['rows']:,} rows (seeds used: {run['seeds_used']}), impacts32 SHA256 recorded in run.json; "
  "convergence accepted as a pass by project ruling, 16 Oct 2026. Plus the **northern supplement** `run-j-supplement/reduced/impacts-ruleB.npz` "
  f"({run['supplement']['rows_in_file']:,} rows; the {run['supplement']['rows_used']:,} rows with technique ≥ 1 used; technique 0 rows are the production set already covered by the strata).")
w("- 00:19 options and weights: end of flight's two-factor table (`smoke/option_table_0019.py`), \"total q = 1/3 (C2 silent)\" cells, re-implemented from the stored columns: "
  "ln w = ln(weight/Σ) + ln(1 − P_breakup) + loglik_D + ln(0.75·e^{C1} + 0.25·e^{C2}); C1 = Erlang log-on lag density + `unpowered` constraint, C2 = −ln W + `unpowered` + no-later-log-on survival. "
  "D0′ holds the 00:19 values out but keeps the log-on-cause and survival factors, exactly as EoF's D0 cell and the supplement's `lnw:comb/D0`. "
  "Strata mixed by p_core (0.9982/0.0013/0.0003/0.0002) × Ẑ_D, seeds pooled by evidence (EoF's pooling). Supplement share s_D = its `lnw:comb` mass: "
  + ", ".join(f"{o} {run['supplement']['share'][o]['supplement']:.3f}" for o in ON) + ".")
w("- Dive probability p ∈ {0, 0.5, 1}: the module's existing push-over re-weighting (×2p where pushover_to_surface = 1, ×2(1−p) where drawn but not to the surface, ×1 where not drawn). "
  "Supplement rows keep their native weights at every p (no pushover_to_surface column: **gap**, size s_D).")
w("- Arrival = impact time + WGS84 geodesic / c. SOFAR c ~ N(1.482, 0.006) km/s; AGW c ~ U(1.40, 1.50) km/s (assumed, not modelled). No refraction, blockage or path lengthening. "
  "2 s grid, 23:00 7 Mar to 06:00 8 Mar; mass beyond the grid: 0 in every row. Quantiles 0.5/5/25/50/75/95/99.5 %; request window [q0.5 − 10 min, q99.5 + 20 min] rounded to 5 min; "
  "UNCONVERGED flag when the per-seed q0.5 or q99.5 spread over the 24 waypoints seeds exceeds 5 min (then the window is widened to the seed envelope).")
w("- Receivers: H01W, H08S, H08N (triad means), IMOS 3315, 3376, 3274, 3275, 3250 (Scott Reef: declared no-information row), and the six OHASISBIO 2014 sites (chart rows, nothing held).\n")
w("## Impact time (pooled, p = 0.5)\n")
w("| Option | q0.5 | q5 | q50 | q95 | q99.5 | 99th-pct northern latitude | Kish ESS |\n|---|---|---|---|---|---|---|---|")
for o in ON:
    r=R('impact',o,0.5,'-'); w(f"| {ON[o]} | {r['q0.5']} | {r['q5']} | {r['q50']} | {r['q95']} | {r['q99.5']} | {float(r['lat99_north_deg']):.1f}°S | {float(r['ess']):,.0f} |")
w("\nThe 99th-percentile contour sits at 27–28.5°S in every option, so the operating note's rule 7 makes **20°S** the latitude span for every spatial product.\n")
w("## Arrival windows, SOFAR branch, p = 0.5 (median; 90 % interval = q5–q95; request window)\n")
w("| Receiver | " + " | ".join(ON[o].split(' (')[0] for o in ON) + " |\n|---|" + "---|"*4)
for rx in ["H01W","H08S","H08N","3315","3376","3274","3275","3250","NEAMS","SWAMS","SSEIR","MAD","WKER","NCRO"]:
    cells=[]
    for o in ON:
        r=R(rx,o,0.5,'SOFAR'); cells.append(f"{r['q50']} ({r['q5']}–{r['q95']}); req {r['window_start'][:5]}–{r['window_end'][:5]}" + (" ⚠tail" if r['unconverged']=='1' else ""))
    w(f"| {RXL[rx]} | " + " | ".join(cells) + " |")
w("\n⚠tail = UNCONVERGED upper or lower tail (per-seed spread of q0.5 or q99.5 > 5 min over the 24 waypoints seeds); the request window is widened to the seed envelope. "
  "These are the distant receivers (Scott Reef, the OHASISBIO sites) and the low-ESS D3 rows; the H01W/H08S rows under D0′ and D2 are converged.\n")
w("## Dive probability sensitivity (H01W and H08S, SOFAR, D0′): median and 90 % interval\n")
w("| p | H01W | H08S | Perth Canyon 3376 |\n|---|---|---|---|")
for p in (0.0,0.5,1.0):
    w(f"| {p:g} | " + " | ".join(f"{R(rx,'D0',p,'SOFAR')['q50']} ({R(rx,'D0',p,'SOFAR')['q5']}–{R(rx,'D0',p,'SOFAR')['q95']})" for rx in ('H01W','H08S','3376')) + " |")
w("\nThe AGW branch (c ~ U(1.40, 1.50) km/s, assumed) ends 0–5 min later than SOFAR at every receiver; its rows are in windows.csv (branch = AGW).\n")
w("## Recommended request windows (union over options with ESS ≥ 1,000, padded −10/+20 min, p = 0.5; ticks for p = 0, 1 on the chart)\n")
w("| Receiver | SOFAR | AGW |\n|---|---|---|")
for rx in ["H01W","H08S","H08N","3315","3376","3274","3275","3250"]:
    qs=[r for r in req if r['receiver']==rx and float(r['p'])==0.5]
    w(f"| {RXL[rx]} | " + " | ".join(f"{[q for q in qs if q['branch']==b][0]['start'][:5]}–{[q for q in qs if q['branch']==b][0]['end'][:5]}" for b in ('SOFAR','AGW')) + " |")
w("\nAll four options clear the ESS ≥ 1,000 gate at p = 0.5 (D3 at 5,671 is the lowest), so the unions include Holland H1/H2 data treatments for the first time on run J. "
  "Against the module's earlier raw-data request to Pete (H01W 00:25–02:20, H08S/H08N 00:45–02:50): the run J windows lie inside it; no change to the request is needed.\n")
w("## Held-data coverage: fraction of the predicted SOFAR arrival mass inside a recording the module holds (p = 0.5)\n")
w("| Receiver | held | " + " | ".join(ON[o].split(' (')[0] for o in ON) + " |\n|---|---|" + "---|"*4)
for rx in ["H01W","H08S","H08N","3315","3376","3274","3275","3250"]:
    c0=C(rx,'D0',0.5,'SOFAR'); w(f"| {RXL[rx]} | {c0['held_source']} ({int(float(c0['held_seconds'])/60)} min) | " + " | ".join(f"{100*float(C(rx,o,0.5,'SOFAR')['held_fraction']):.0f} %" for o in ON) + " |")
w("\n- H01W: Kadri's three published 10-min panels (00:27–00:57, digitised) cover 54 % of the predicted arrival under D0′ and 84–88 % under the Holland data treatments, which pull the impact earlier. "
  "The whole of the 99 % window is 00:39–01:14, so the published traces do not reach the late half of the held-out window.")
w("- H08S: panels d–e (01:00–01:20) cover 69 % (D0′) to 99 % (D4). H08N: nothing held. OHASISBIO: nothing held; NEAMS, nearest the arc, was lost on recovery.")
w("- IMOS: 307 s records every 15 min give a 34 % duty cycle; the phase of the schedule relative to the arrival matters (3315 at 42 % vs 3376 at 27 % under D0′, loggers 100 m apart with offset start times). "
  "Blackman et al. (2004) is 2003 data: n/a.")
w("- Royer's H01W picks (Table 5): event B 00:35:45–00:35:55 falls before the 0.5 % quantile of every option's H01W arrival (00:38–00:39); C2/D1/D2 picks at 01:29–01:35 fall after the 99.5 % quantile (01:14). "
  "On timing alone none of the four Royer events is consistent with a run J impact by the deep sound channel (the 16 s H01W clock question in the evidence sweep does not change this).\n")
w("## Charts (results/, PNG + PDF, two footnotes each)\n")
w("- `hydroacoustics-run-j-timelines`: per receiver, impact-time bands, arrival intervals per option (SOFAR filled, AGW hollow), recordings held, poster boxes, both Kadri times, Royer picks, held fraction.")
w("- `hydroacoustics-run-j-timelines-ohasisbio`: the six 2014 sites, \"no recordings held\", Royer picks.")
w("- `hydroacoustics-run-j-request-windows`: panel-(c)-style request windows per receiver.")
w("- `hydroacoustics-run-j-publication-coverage`: impact-time densities per option and the Fig. 9 spans converted to impact time along the arc 38→20°S. "
  "The earlier chart of this name could not be located in the repository or the artifact store by title; this one is built from its description in the work order (declared).\n")
w("## COVERAGE\n")
w("- **(a) Feasible set:** every impact that end of flight's run J prior reaches, from 00:19:37 to 01:15:56 and north to the supplement's extent; both log-on causes; both existence constraints as EoF's total cell.")
w("- **(b) Model's reach:** straight-line (geodesic) arrival with a single group speed per row; AGW speed assumed. Reach gaps: no refraction or bathymetric path lengthening (G-N2 ridge paths), no blockage "
  "(H08N is BLOCKED for arc impacts even in the N×2D corridor, K4; its windows are geometric only), no modal dispersion. These shift arrivals by at most a few minutes on open paths and do not affect the ±10/+20 min padding.")
w("- **(c) Proposal's coverage (Kish ESS, mixture incl. supplement; per family share/ESS):**")
w("\n| Option / p | ESS | strata-only ESS | supplement ESS | supplement share | A1 share/ESS | A2 | B | outside B |\n|---|---|---|---|---|---|---|---|---|")
for k,v in ess.items():
    f=v['family']; w(f"| {k} | {v['ess']:,.0f} | {v['ess_strata_only']:,.0f} | {v['ess_supplement']:,.0f} | {v['supplement_share']:.3f} | " + " | ".join(f"{f[n]['share']:.3f} / {f[n]['ess']:,.0f}" for n in ('A1','A2','B','outside B')) + " |")
w("\n- Gaps and status: (G-W1) supplement rows not re-weighted for p ≠ 0.5 (no pushover_to_surface column) — open, size 10.5–12.5 % of the mass; fix = ask end of flight to add the column to the reduced file. "
  "(G-W2) D3 at p = 1 has ESS 2,944 and family A1 ESS ≈ 410 under D3 — estimable but thin; report as such. (G-W3) tails UNCONVERGED at the distant receivers and in low-ESS rows (flagged per row). "
  "(G-W4) the stratum mixture rests on p_core from core's hand-off (waypoints 0.998): the free/descent-climb/repro strata carry 0.1 % of the mass, so the result is effectively conditional on the waypoints family. "
  "(G-W5) AGW speed is an assumption. (G-W6) the IMOS held intervals use the logger clock start times (start_logger) without drift correction. "
  "(G-W7) the level/power-screen half of block 3 is not in this note (TL grid pending).")
w("- Parameter bounds with sources: c_SOFAR 1.482 ± 0.006 km/s (module standard, search_windows.py prereg 55eb191); AGW 1.40–1.50 km/s (stated allowance); q = 1/3 and W = 3,898 s (EoF rulings 12 Oct); "
  "Erlang lag (shape 8, scale 14.875 s, log-on 1394237969.416) from each seed's run.json.\n")
w("## done / next / blocker\n")
w("- done: pre-registered and computed run J arrival windows (4 options × 3 p × 2 branches × 14 receivers), held-data coverage, request windows, four charts, this note.")
w("- next: level/power-screen half of block 3 when the TL grid arrives; then block 4 pre-registration of searches using these windows.")
w("- blocker: TL grid from the parallel track (block 2) for the level half; nothing else.")
open('/tmp/run_j_windows_note.md','w').write("\n".join(L)+"\n")
print(len(L))
EOF
cp /tmp/run_j_windows_note.md "../../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-run-j-windows.md"
sed -n 1,30p /tmp/run_j_windows_note.md | cut -c1-250