
output = {
 "block": "7 — injection-recovery across the full coupling range at every unblocked receiver (P_D against received level; the rule-2 gate)",
 "status": "done",
 "summary": ("Pre-registered (e816313) and ran injection-recovery of KRAKEN-dispersed one-pole impact pulses into real background at six receivers: "
             "IMOS 3376/3274 (own 14-day sets, 5,376 null windows), IMOS 3315/3275 (own 8 March recordings outside the request window, 380/360 windows), "
             "H01W/H08S (PROXY: IMOS 3376 shaped to Blackman 2004 App. B 2003 medians, digitised, single hydrophone). 26,460 injections, 21 levels (-20..+30 dB re "
             "background median) x 3 tau (run J tau90 5/50/95 %: 0.11/3.30/10.59 s), detectors M1b envelope matched filter (primary), STA/LTA, band energy, "
             "alpha 0.3/0.1/0.05/0.01/0.001 per 60 s window. M1b reaches P_D = 0.5 at +4.0..+7.0 dB (IMOS) and +7.8/+8.5 dB (H01W/H08S proxy) at alpha 0.01; "
             "STA/LTA 10-16 dB; band energy 16-28 dB; alpha 0.001: 11-19 dB. Timing recovered to +-0.3 s (5-95 %) at >= +5 dB, level to +-1 dB (model-matched upper bounds). "
             "Eta mapping (run J energies, IMOS RAM-corrected TL table, block 2 grid pass A for H01W/H08S, +-10 dB calibration draw): eta_50 for P_D(any receiver) = 0.5 "
             "is ~6e-4 under D0' p 0.5 at alpha 0.01 (~3x the F-35A anchor; P_D(any) at the anchor 0.36); 1.9e-4 at alpha 0.05; 4.8e-3 at alpha 0.001. "
             "Gate verdict: P_D(received level) on a declared background = YES at the four IMOS loggers, PROXY-ONLY at H01W/H08S, BLOCKED H08N, NO-INFORMATION 3250. "
             "Likelihood form written with units (m_r matching-detection density per s [per degree], beta_r background candidate rate in the same units = alpha/60 s). "
             "No likelihood column written. PREDICTIVE, NOT CALIBRATED; caveats C1, C2 on every number."),
 "commits": ["e816313 (module: pre-registration, before any statistic)", "0106f51 (module: code)", "d32b14c (module: results-data/injection_run_j + eta_map/charts)",
             "dddd044 (work branch: note, 2 charts PNG+PDF, coordination/architecture.md entry)", "3d787e6 (work branch: note provenance wording)"],
 "results_notes": ["Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md",
                   "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-pd.{png,pdf}",
                   "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-eta.{png,pdf}"],
 "exchange_paths": ["/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/ (214 MB; README.txt, SHA256SUMS; inputs/, templates/, run/, eta/, figs/)",
                    "module branch results-data/injection_run_j/ (1.8 MB: pd_vs_level.csv, fits.json, thresholds.json, errors.csv, summary.json, eta_map.json, eta50_by_lat_band.csv, proxy_check.json, inputs.json)"],
 "key_numbers": ("L50 (M1b, alpha 0.01, tau 3.3 s, dB re background median): 3376 7.0 | 3315 6.6 | 3274 4.8 | 3275 4.0 | H01W-proxy 7.8 | H08S-proxy 8.5. "
                 "L50 at alpha 0.001: 3376 19.2, 3274 11.3, H01W 15.3, H08S 15.7 (3315/3275 not resolvable, p floor 2.6-2.8e-3). "
                 "Background medians (dB re 1 uPa, 5-40 Hz, 1 s): 3376 99.3, 3315 99.6, 3274 103.4, 3275 95.1, H01W 100.6, H08S 94.8. "
                 "p floors: 1.9e-4 (3376, 3274, H01W, H08S), 2.6e-3 (3315), 2.8e-3 (3275). Background set: 1,344 files (3376, 3274, and the proxies; >= 400 target), 95/90 files (3315/3275). "
                 "eta_50 (P_D(any)=0.5), alpha 0.01 with cal error: D0' p0/0.5/1 = 8.8e-4/6.1e-4/4.2e-4; D2 p0.5 6.1e-4; D3 p0.5 5.5e-4 (ESS 31, thin); D4 p0.5 2.5e-4. "
                 "P_D(any) at F-35A anchor 2.1e-4 (D0' p0.5): 0.36 (alpha 0.01), 0.52 (0.05), 0.18 (0.001). By latitude: eta_50 (0.4-1.3)e-3 for 41-36 S (72 % of mass), mostly (1-3)e-3 north of 34 S. "
                 "Timing error 5-95 %: +-0.3 s at >= +5 dB; level error median +1.5 dB at 0 dB, < +0.5 dB above +10 dB. Compute: 25 min wall at <= 4 processes."),
 "gaps": ["G7-1 northern supplement rows not in the eta mapping (D0' share 0.125)",
          "G7-2 one representative deep-water profile for all paths; path-dependent dispersion (Portland shelf, Perth Canyon, H08S ridges) untested beyond +-225-350 km range mismatch",
          "G7-3 AGW branch not injected (no AGW waveform model in the module)",
          "G7-4 per-family (A1/A2/B) eta_50 not separated",
          "G7-5 module RAM-corrected IMOS TL differs 4-27 dB at 20-40 Hz between co-located loggers 13-38 m apart in depth -> per-logger P_D at the anchor differs x4-20 while P_D(level) curves agree within 1 dB; quote any-receiver only until a receiver-depth RAM check",
          "G7-6 3315/3275 own backgrounds are one night (cross-check vs 3376/3274: L50 within 0.8 dB)",
          "G7-7 IMS proxies carry IMOS temporal statistics: conservative for H01W (spread 11.5 dB vs Blackman 2.3-5.5 dB, Kadri panel b 2.9 dB), optimistic for H08S on 8 Mar 2014 (no TGS survey in the 2003 noise)",
          "G7-8 templates model-matched to the injected pulses (weak-signal G-W1 real-arrival test outstanding)",
          "G7-9 IMOS absolute levels +-3 dB (band-average gain)",
          "G7-10 IMOS TL clamped north of 31.64 S (4.6 % of D0' mass); H01W/H08S TL from block 2 grid pass A read from disk before its note landed"],
 "next": ("Block 11 (composition) may take fits.json (M1b logistic in received level per receiver/alpha/tau) once review accepts the IMOS 'yes' and IMS 'proxy-only' labels — "
          "ruling requested in coordination/architecture.md on whether IMOS terms may compose with IMS at zero. Then: receiver-depth RAM check (G7-5); per-receiver bathymetry-following "
          "templates from the block 2 grid; add supplement rows; real-arrival test of M1b."),
 "blocker": "none for this block. IMS gate stays proxy-only until real H01W/H08S recordings (or their real background) are held."
}
r = host.submit_output(output,
    completion_bullets=["Pre-registered and ran 26,460 injections at six receivers on real backgrounds; P_D(level) tables for 3 detectors x 3 tau x 5 alpha",
                        "Mapped received level to coupling: eta_50 ~ 6e-4 (D0' p 0.5, alpha 0.01), ~3x the F-35A anchor; P_D(any) at the anchor 0.36",
                        "Gate verdict written: yes at IMOS loggers, proxy-only at H01W/H08S, blocked H08N; likelihood form with units; no likelihood column written",
                        "Committed note + charts + coordination entry (dddd044, 3d787e6) and code/data (e816313, 0106f51, d32b14c); exchange 214 MB"],
    deviations=["3315/3275 backgrounds = own 8 March recordings outside the request window (95/90 files, ~370 null windows), not the 14 GB set, which holds only 3376/3274/3250; co-located 14-day sets used as cross-check",
                "Run J inputs from a systematic chunk subsample (8 x 50,000 rows per seed, 74 seeds; 1-in-4 thin stored; a further 1-in-8 thin for the eta bisection, 925,000 rows; ESS per option reported; D3 ESS 15-31 thin); northern supplement not included",
                "H01W/H08S TL taken from the block 2 grid pass A on disk (provisional) rather than waiting; IMOS TL from the module's RAM-corrected table; a first eta run (pass A + RAM deltas, contrary to the pre-registration) was discarded and rerun as pre-registered (result within 3 %)",
                "3250 excluded as a declared no-information row; H08N blocked: no P_D for either; triad gain applied only in the eta mapping, not in the P_D curves",
                "Dispersion from one representative deep-water profile at the SOFAR axis for every receiver (as the weak-signal track), not per-receiver bathymetry-following paths",
                "IMOS absolute levels via a 5-40 Hz band-average gain (+-3 dB); IMS absolute levels are Blackman 2003 medians (H08S 2014 survey noise not represented)"])
print(r)
