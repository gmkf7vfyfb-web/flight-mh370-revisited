*** WARNING (23 Oct 2026, amendment A4): THE COLUMNS IN THIS DIRECTORY ARE ON THE OLD IMOS TL TABLE (imos_tl_ramcorr_arc.csv, constant
*** rule-2 RAM correction, gap G-TL1). The RAM-along-grid track has since issued the corrected table imos_tl_ram_arc.csv (run-j-tl-grid/tables/).
*** The per-row columns here MUST BE REWRITTEN with the corrected table before any composer use. They are internally consistent with this
*** README and READY stays. The corrected STATISTICS (upper limits, evidence, Bayes factors; not columns) are in stats-ramgrid/ and in the
*** addendum of results/hydroacoustics-composition-run-j.md. Rewrite recipe: B11_IMOS_RAMGRID=1 python driver.py (writes to run-j-gated.staging, ~6.3 GB, needs >= 28 GiB free).

Hydroacoustics block 11 (composition) on end of flight run J, all four strata (74 seeds). Written 2026-10-22T06:43:25Z.
Pre-registration prepare/composition_run_j/prereg.py (module branch, commit 90d7181); worker.py / driver.py; 4 single-thread workers.
Rows 313,599,968; not_computed (NaN) 0; the marginalised IMOS column (proposed default) is present for every seed; per-seed checks (rows equal end of flight's, float32, NaN only where inputs non-finite and identical
across columns, finite elsewhere, quantiles in _parts/*.json): all pass. Seeds with fewer than five columns (another process held the disk below the 20 GiB floor during the run; the marginalised IMOS
column was written, the other four were not): 10 ["run-j-free/seed-2: ['hydro-lnL-imos-margeta']", "run-j-free/seed-3: ['hydro-lnL-imos-margeta']", "run-j-free/seed-10: ['hydro-lnL-imos-margeta']", "run-j-free/seed-11: ['hydro-lnL-imos-margeta']", "run-j-free/seed-12: ['hydro-lnL-imos-margeta']", "run-j-free/seed-13: ['hydro-lnL-imos-margeta']", "run-j-free/seed-14: ['hydro-lnL-imos-margeta']", "run-j-free/seed-15: ['hydro-lnL-imos-margeta']", "run-j-free/seed-16: ['hydro-lnL-imos-margeta']", "run-j-free/seed-17: ['hydro-lnL-imos-margeta']"]
TOP-UP RECIPE (when >= 22 GiB free): B11_TOPUP=1 python worker.py <stratum> <seed> <this dir>  then  python driver.py  (finaliser only).

COLUMNS (float32, row i = row i of end-of-flight/run-j/<stratum>/seed-N/impacts32.npy):
  hydro-lnL-imos-eta1e-3.npy      ln L of the IMOS-gated term at coupling efficiency eta = 1e-3
  hydro-lnL-imos-eta2.1e-4.npy    ... at eta = 2.1e-4 (F-35A upper anchor, Brown et al. 2026)
  hydro-lnL-imos-eta1e-4.npy      ... at eta = 1e-4
  hydro-lnL-imos-margeta.npy      ... marginalised over a log-uniform prior on eta in [1e-6, 1e-2] (41 points, equal weights)  <- PROPOSED DEFAULT
  hydro-lnL-ims-proxy-margeta.npy SENSITIVITY: IMOS-gated term x H01W/H08S PROXY-background terms, eta marginalised. PREDICTIVE for IMS.
NaN = not computed (impact time, position, energy or tau not finite); never a default. 0.0 = computed, no information (no scored window at
any receiver). Rows south of 41 S carry TL clamped at the table edge (labelled; < 0.2 % of mass).

LABELS: GATE PASSED AT IMOS ONLY (3376, 3315, 3274, 3275: own real backgrounds, block 7). IMS PROXY = SENSITIVITY (H01W/H08S backgrounds
are IMOS 3376 shaped to Blackman 2003 medians, digitised; single hydrophone + 4.8 dB triad gain label). PREDICTIVE, NOT CALIBRATED.
Caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta over
four decades, F-35A upper anchor). Both Kadri times carried: text time 00:52:03, caption time 00:54:30. Detector M1b, false-alarm
level alpha = 0.05 per 55 s window (report level), beta = alpha / 55 s; matched candidates from the block 5 pre-registered tables
(IMOS M1b p <= 0.05: 3275 01:20:35 and 01:07:47, both louder than any impact could be at Portland, eta_needed 30 / 19 -- matching is
amplitude-blind, gap G11-1; H01W M1b p <= 0.05: 00:52:04 text time; H08S residual: none). TL = block 2 arc grid (41-20 S, offset 0,
10 m source; IMOS RAM-corrected, G-TL1; IMS raw KRAKEN minus imp500 RAM delta). tau = end of flight tau90 (method 1). E = contact
kinetic energy (sidecar energy_transferred_j, an upper anchor). Calibration error N(0, 10 dB) per row shared by receivers.

RULING REQUEST (architecture, composer, Pete): may hydro-lnL-imos-margeta enter the composer as the module's likelihood (default), with
hydro-lnL-ims-proxy-margeta as the labelled sensitivity? Until ruled, the composer default remains lnL_gated = 0.0 in
mh370-exchange/hydroacoustics/run-j/primary-tau-eof (unchanged by this block).

Per-seed summary (rows, not_computed, columns written, free GiB at write, quantiles 0.1/1/50/99/99.9 %, share non-zero, scored share, seconds):
{
 "run-j-descent-climb/seed-1": {
  "stratum": "run-j-descent-climb",
  "seed": 1,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.60205078125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.721054077148438,
    -8.563989639282227,
    -0.21375542879104614,
    3.118823528289795,
    3.5288639068603516
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.468430519104004,
    -6.1067657470703125,
    -0.04612046107649803,
    2.7928764820098877,
    3.4927077293395996
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.98452091217041,
    -5.063615798950195,
    -0.021683502942323685,
    2.5529441833496094,
    3.4583346843719482
   ],
   "hydro-lnL-imos-margeta": [
    -4.4139580726623535,
    -2.366452217102051,
    -0.15342092514038086,
    2.576838731765747,
    3.285256862640381
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.48520040512085,
    -3.18593430519104,
    -0.24286103248596191,
    1.459549903869629,
    1.9289054870605469
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.872525,
   "hydro-lnL-imos-eta2.1e-4": 0.872525,
   "hydro-lnL-imos-eta1e-4": 0.872525,
   "hydro-lnL-imos-margeta": 0.872525,
   "hydro-lnL-ims-proxy-margeta": 0.9148825
  },
  "scored_any_share": 0.9148825,
  "seconds": 291.13892102241516,
  "impacts32_sha": "0e4c7f4f1398ea09e81dbcab94f25bbd41ffa454a5c01a47248e2d3044fa786c",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-1.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-10": {
  "stratum": "run-j-descent-climb",
  "seed": 10,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.86907958984375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.364487648010254,
    -8.916543006896973,
    -0.2186782956123352,
    3.169482469558716,
    3.524324893951416
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.096835136413574,
    -6.389069080352783,
    -0.04693511128425598,
    2.871272087097168,
    3.4922800064086914
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.563203811645508,
    -5.308084964752197,
    -0.02200249768793583,
    2.644019603729248,
    3.461737632751465
   ],
   "hydro-lnL-imos-margeta": [
    -4.628663539886475,
    -2.462879180908203,
    -0.15577274560928345,
    2.6300151348114014,
    3.292681932449341
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.72674560546875,
    -3.2990639209747314,
    -0.2500336468219757,
    1.4560191631317139,
    1.8479948043823242
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8788933985660143,
   "hydro-lnL-imos-eta2.1e-4": 0.8788933985660143,
   "hydro-lnL-imos-eta1e-4": 0.8788933985660143,
   "hydro-lnL-imos-margeta": 0.8788933985660143,
   "hydro-lnL-ims-proxy-margeta": 0.9150164748352516
  },
  "scored_any_share": 0.9150164748352516,
  "seconds": 132.40563201904297,
  "impacts32_sha": "995f2476ba9d578835ead68866ff759fe6d0af24bc1e02cf321e3e9b6c78d5d9",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-10.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-11": {
  "stratum": "run-j-descent-climb",
  "seed": 11,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.79278564453125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.703508377075195,
    -8.421266555786133,
    -0.2798178791999817,
    3.0149426460266113,
    3.5151593685150146
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.437729835510254,
    -6.102169990539551,
    -0.06108040362596512,
    2.6252596378326416,
    3.473048686981201
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.952946662902832,
    -5.116893768310547,
    -0.02870834618806839,
    2.3457281589508057,
    3.43394136428833
   ],
   "hydro-lnL-imos-margeta": [
    -4.535085678100586,
    -2.505767822265625,
    -0.18246890604496002,
    2.4608047008514404,
    3.2454047203063965
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.908287048339844,
    -3.4227993488311768,
    -0.27856993675231934,
    1.407540202140808,
    1.8648749589920044
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.896508125,
   "hydro-lnL-imos-eta2.1e-4": 0.896508125,
   "hydro-lnL-imos-eta1e-4": 0.896508125,
   "hydro-lnL-imos-margeta": 0.896508125,
   "hydro-lnL-ims-proxy-margeta": 0.928864375
  },
  "scored_any_share": 0.928864375,
  "seconds": 136.9945991039276,
  "impacts32_sha": "0895448eaeb03bf661b15aef088a3041fa1b9e9f5810e8bad16bbbe3b9bde780",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-11.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-12": {
  "stratum": "run-j-descent-climb",
  "seed": 12,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.5257568359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.899535179138184,
    -8.636492729187012,
    -0.25544166564941406,
    3.2049849033355713,
    3.522406816482544
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.659900665283203,
    -6.263189315795898,
    -0.055402129888534546,
    2.9373066425323486,
    3.4926280975341797
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.16905403137207,
    -5.244739532470703,
    -0.026004184037446976,
    2.7301840782165527,
    3.464566946029663
   ],
   "hydro-lnL-imos-margeta": [
    -4.6144022941589355,
    -2.524045705795288,
    -0.1723923683166504,
    2.679037094116211,
    3.3016014099121094
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.979964256286621,
    -3.454406261444092,
    -0.26665031909942627,
    1.4674324989318848,
    1.8156923055648804
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.898263125,
   "hydro-lnL-imos-eta2.1e-4": 0.898263125,
   "hydro-lnL-imos-eta1e-4": 0.898263125,
   "hydro-lnL-imos-margeta": 0.898263125,
   "hydro-lnL-ims-proxy-margeta": 0.9282415625
  },
  "scored_any_share": 0.9282415625,
  "seconds": 189.7072548866272,
  "impacts32_sha": "36228a4e733c841f0acb193c8a395f4f0fceb91351d94a2afb4053ba17e37451",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-12.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-13": {
  "stratum": "run-j-descent-climb",
  "seed": 13,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.6865234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.706298828125,
    -8.5811185836792,
    -0.2241596281528473,
    3.1208701133728027,
    3.530661106109619
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.447429656982422,
    -6.126323699951172,
    -0.04862847924232483,
    2.7864389419555664,
    3.4914534091949463
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.969850540161133,
    -5.079519748687744,
    -0.022899892181158066,
    2.5387582778930664,
    3.456164598464966
   ],
   "hydro-lnL-imos-margeta": [
    -4.424571990966797,
    -2.356111526489258,
    -0.15794634819030762,
    2.57128643989563,
    3.27533221244812
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.423320293426514,
    -3.1334919929504395,
    -0.24841119349002838,
    1.4830917119979858,
    1.9115952253341675
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8771834375,
   "hydro-lnL-imos-eta2.1e-4": 0.8771834375,
   "hydro-lnL-imos-eta1e-4": 0.8771834375,
   "hydro-lnL-imos-margeta": 0.8771834375,
   "hydro-lnL-ims-proxy-margeta": 0.9174371875
  },
  "scored_any_share": 0.9174371875,
  "seconds": 193.12296104431152,
  "impacts32_sha": "fc725f4c2bf77839203610747259f0d4041f5730c6d276814885709cde26c8fb",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-13.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-14": {
  "stratum": "run-j-descent-climb",
  "seed": 14,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.56390380859375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.173724174499512,
    -8.716854095458984,
    -0.22189560532569885,
    3.3055410385131836,
    3.530437707901001
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.898933410644531,
    -6.246535301208496,
    -0.04786686599254608,
    3.101013422012329,
    3.5105807781219482
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.38968276977539,
    -5.194410800933838,
    -0.022461190819740295,
    2.937990427017212,
    3.4914023876190186
   ],
   "hydro-lnL-imos-margeta": [
    -4.543471813201904,
    -2.437953472137451,
    -0.1571412831544876,
    2.8119699954986572,
    3.3547582626342773
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.701446056365967,
    -3.3039886951446533,
    -0.2502964735031128,
    1.549742579460144,
    1.8789712190628052
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8974585254147458,
   "hydro-lnL-imos-eta2.1e-4": 0.8974585254147458,
   "hydro-lnL-imos-eta1e-4": 0.8974585254147458,
   "hydro-lnL-imos-margeta": 0.8974585254147458,
   "hydro-lnL-ims-proxy-margeta": 0.9288060244397556
  },
  "scored_any_share": 0.9288060244397556,
  "seconds": 193.08909702301025,
  "impacts32_sha": "f657efff058a9f3214c5e9ad33a92e2ff1eebc9bd6a12e36ed245913bde7d6f5",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-14.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-15": {
  "stratum": "run-j-descent-climb",
  "seed": 15,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.48760986328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.178244590759277,
    -8.7891845703125,
    -0.23353266716003418,
    3.1560139656066895,
    3.521394968032837
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.895186424255371,
    -6.2814836502075195,
    -0.050530318170785904,
    2.8494956493377686,
    3.4901528358459473
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.38477897644043,
    -5.221489906311035,
    -0.023717042058706284,
    2.617685079574585,
    3.4584338665008545
   ],
   "hydro-lnL-imos-margeta": [
    -4.564915180206299,
    -2.4421610832214355,
    -0.16260287165641785,
    2.6133882999420166,
    3.2883718013763428
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.772064208984375,
    -3.3087849617004395,
    -0.2557786703109741,
    1.4472386837005615,
    1.857930064201355
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8846975,
   "hydro-lnL-imos-eta2.1e-4": 0.8846975,
   "hydro-lnL-imos-eta1e-4": 0.8846975,
   "hydro-lnL-imos-margeta": 0.8846975,
   "hydro-lnL-ims-proxy-margeta": 0.91793875
  },
  "scored_any_share": 0.91793875,
  "seconds": 193.61792373657227,
  "impacts32_sha": "f05658e6e80b3e375cdc8a3eacd5264b36769365fd645d8391ef278264a68285",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-15.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-16": {
  "stratum": "run-j-descent-climb",
  "seed": 16,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.41131591796875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.362013816833496,
    -8.87969970703125,
    -0.23406937718391418,
    3.20473313331604,
    3.522641181945801
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.081883430480957,
    -6.359255313873291,
    -0.05048881471157074,
    2.9353761672973633,
    3.492753028869629
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.554767608642578,
    -5.29005241394043,
    -0.023687753826379776,
    2.723871946334839,
    3.465099811553955
   ],
   "hydro-lnL-imos-margeta": [
    -4.597823619842529,
    -2.468424081802368,
    -0.16279640793800354,
    2.677924871444702,
    3.29878830909729
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.8882975578308105,
    -3.378866195678711,
    -0.26068997383117676,
    1.4755219221115112,
    1.8183120489120483
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8968934375,
   "hydro-lnL-imos-eta2.1e-4": 0.8968934375,
   "hydro-lnL-imos-eta1e-4": 0.8968934375,
   "hydro-lnL-imos-margeta": 0.8968934375,
   "hydro-lnL-ims-proxy-margeta": 0.928655
  },
  "scored_any_share": 0.928655,
  "seconds": 197.65755796432495,
  "impacts32_sha": "6194d4980914d303f00c5466a750a30f1b8a1f173f7fd47e980560bf16fcf7d2",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-16.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-2": {
  "stratum": "run-j-descent-climb",
  "seed": 2,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.5257568359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.765559196472168,
    -8.564699172973633,
    -0.23982074856758118,
    3.1878886222839355,
    3.52937912940979
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.515471458435059,
    -6.17277193069458,
    -0.05179136246442795,
    2.89778995513916,
    3.4983813762664795
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.051325798034668,
    -5.1534295082092285,
    -0.024311132729053497,
    2.681567668914795,
    3.469982624053955
   ],
   "hydro-lnL-imos-margeta": [
    -4.530015468597412,
    -2.459739923477173,
    -0.16562364995479584,
    2.6510086059570312,
    3.3056182861328125
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.802313327789307,
    -3.370012044906616,
    -0.2623591125011444,
    1.4492151737213135,
    1.9159666299819946
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8961882256177438,
   "hydro-lnL-imos-eta2.1e-4": 0.8961882256177438,
   "hydro-lnL-imos-eta1e-4": 0.8961882256177438,
   "hydro-lnL-imos-margeta": 0.8961882256177438,
   "hydro-lnL-ims-proxy-margeta": 0.930709130408696
  },
  "scored_any_share": 0.930709130408696,
  "seconds": 273.2525589466095,
  "impacts32_sha": "54a9d4114c59dc6a27b68fca5c1fac7c72c3deb89051fd86cb21b44620e5c00b",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-2.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-3": {
  "stratum": "run-j-descent-climb",
  "seed": 3,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.449462890625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.972647666931152,
    -9.268799781799316,
    -0.20497509837150574,
    3.004796266555786,
    3.508753776550293
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.690998077392578,
    -6.580539226531982,
    -0.04334188252687454,
    2.6187918186187744,
    3.4665651321411133
   ],
   "hydro-lnL-imos-eta1e-4": [
    -10.138205528259277,
    -5.448199272155762,
    -0.020209092646837234,
    2.3365511894226074,
    3.4269745349884033
   ],
   "hydro-lnL-imos-margeta": [
    -4.762413024902344,
    -2.5159387588500977,
    -0.14995694160461426,
    2.454500198364258,
    3.2379887104034424
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.032256603240967,
    -3.42535662651062,
    -0.23376914858818054,
    1.3399643898010254,
    1.8041484355926514
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8419259375,
   "hydro-lnL-imos-eta2.1e-4": 0.8419259375,
   "hydro-lnL-imos-eta1e-4": 0.8419259375,
   "hydro-lnL-imos-margeta": 0.8419259375,
   "hydro-lnL-ims-proxy-margeta": 0.8668475
  },
  "scored_any_share": 0.8668475,
  "seconds": 259.02347898483276,
  "impacts32_sha": "dd0ef3bd2d9b41e9cb0b3c97ceeebd9053cc82f72de1a426c183142e1968c71d",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-3.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-4": {
  "stratum": "run-j-descent-climb",
  "seed": 4,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 30.32684326171875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.85966968536377,
    -8.654173851013184,
    -0.183376744389534,
    2.911468267440796,
    3.5259079933166504
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.600590705871582,
    -6.119498252868652,
    -0.03910958021879196,
    2.4949445724487305,
    3.474349021911621
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.093738555908203,
    -5.062294960021973,
    -0.018350645899772644,
    2.2034735679626465,
    3.427786111831665
   ],
   "hydro-lnL-imos-margeta": [
    -4.393389701843262,
    -2.353861093521118,
    -0.138588547706604,
    2.3727805614471436,
    3.2330129146575928
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.989779949188232,
    -2.947366237640381,
    -0.20455747842788696,
    1.3826311826705933,
    1.905938982963562
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8191653791537915,
   "hydro-lnL-imos-eta2.1e-4": 0.8191653791537915,
   "hydro-lnL-imos-eta1e-4": 0.8191653791537915,
   "hydro-lnL-imos-margeta": 0.8191653791537915,
   "hydro-lnL-ims-proxy-margeta": 0.8532647826478265
  },
  "scored_any_share": 0.8532647826478265,
  "seconds": 120.51926398277283,
  "impacts32_sha": "4ad0d103edebd4785166f29f6cb10a5eac4fb31ec5c7643d2c189761492b27f2",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-4.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-5": {
  "stratum": "run-j-descent-climb",
  "seed": 5,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 30.25054931640625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.879681587219238,
    -9.375584602355957,
    -0.24029541015625,
    3.1879732608795166,
    3.5246429443359375
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.60056209564209,
    -6.6785101890563965,
    -0.0521685816347599,
    2.9058175086975098,
    3.492671489715576
   ],
   "hydro-lnL-imos-eta1e-4": [
    -10.073982238769531,
    -5.536352634429932,
    -0.024513889104127884,
    2.691540241241455,
    3.4636099338531494
   ],
   "hydro-lnL-imos-margeta": [
    -4.762536525726318,
    -2.511342763900757,
    -0.1656603217124939,
    2.6559603214263916,
    3.3012020587921143
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.874194622039795,
    -3.3527615070343018,
    -0.26404571533203125,
    1.4811536073684692,
    1.8822407722473145
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8993525,
   "hydro-lnL-imos-eta2.1e-4": 0.8993525,
   "hydro-lnL-imos-eta1e-4": 0.8993525,
   "hydro-lnL-imos-margeta": 0.8993525,
   "hydro-lnL-ims-proxy-margeta": 0.9384928125
  },
  "scored_any_share": 0.9384928125,
  "seconds": 122.29496502876282,
  "impacts32_sha": "c079ac6cf0c08cf0ff84ee2793d67a04dc03ca4e15b174f9e684468f2e6c951e",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-5.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-6": {
  "stratum": "run-j-descent-climb",
  "seed": 6,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 30.17425537109375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.938039779663086,
    -8.624045372009277,
    -0.23108196258544922,
    3.1404879093170166,
    3.524303436279297
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.669779777526855,
    -6.171548366546631,
    -0.05007048323750496,
    2.8216705322265625,
    3.489185094833374
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.154132843017578,
    -5.1302947998046875,
    -0.0235123448073864,
    2.5803298950195312,
    3.45520281791687
   ],
   "hydro-lnL-imos-margeta": [
    -4.455528736114502,
    -2.404202938079834,
    -0.1615738868713379,
    2.595338821411133,
    3.2820396423339844
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.689794063568115,
    -3.288867473602295,
    -0.2599099278450012,
    1.4671673774719238,
    1.893723964691162
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8931053125,
   "hydro-lnL-imos-eta2.1e-4": 0.8931053125,
   "hydro-lnL-imos-eta1e-4": 0.8931053125,
   "hydro-lnL-imos-margeta": 0.8931053125,
   "hydro-lnL-ims-proxy-margeta": 0.93488125
  },
  "scored_any_share": 0.93488125,
  "seconds": 122.03075528144836,
  "impacts32_sha": "94bf8b57ebd87c12fddebbce07aeaa75dea75c7a7071bf08ee7119947a0e0283",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-6.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-7": {
  "stratum": "run-j-descent-climb",
  "seed": 7,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 30.09796142578125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.702783584594727,
    -9.028013229370117,
    -0.2198774814605713,
    3.0704832077026367,
    3.519669771194458
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.427364349365234,
    -6.451738357543945,
    -0.04719734564423561,
    2.7259411811828613,
    3.48238205909729
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.89455509185791,
    -5.36303186416626,
    -0.022119464352726936,
    2.4660165309906006,
    3.4473512172698975
   ],
   "hydro-lnL-imos-margeta": [
    -4.735755443572998,
    -2.502089738845825,
    -0.15640632808208466,
    2.5264840126037598,
    3.2703070640563965
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.970468997955322,
    -3.3575215339660645,
    -0.24127592146396637,
    1.396676778793335,
    1.8492727279663086
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8625271875,
   "hydro-lnL-imos-eta2.1e-4": 0.8625271875,
   "hydro-lnL-imos-eta1e-4": 0.8625271875,
   "hydro-lnL-imos-margeta": 0.8625271875,
   "hydro-lnL-ims-proxy-margeta": 0.89503625
  },
  "scored_any_share": 0.89503625,
  "seconds": 119.48590612411499,
  "impacts32_sha": "33a8bdd3336aab9bbdc021033f94e3e6f15e40b7cb522556c7304a58b7a87fc9",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-7.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-8": {
  "stratum": "run-j-descent-climb",
  "seed": 8,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 30.02166748046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.66833209991455,
    -9.0717191696167,
    -0.19294878840446472,
    3.1001832485198975,
    3.5178470611572266
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.379425048828125,
    -6.452343463897705,
    -0.0410761833190918,
    2.7737462520599365,
    3.4798147678375244
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.847247123718262,
    -5.340839862823486,
    -0.019233468919992447,
    2.5307998657226562,
    3.4463436603546143
   ],
   "hydro-lnL-imos-margeta": [
    -4.628738880157471,
    -2.4393815994262695,
    -0.1435927152633667,
    2.561060667037964,
    3.2717971801757812
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.763126850128174,
    -3.270097017288208,
    -0.22928842902183533,
    1.399726152420044,
    1.8136454820632935
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.845289375,
   "hydro-lnL-imos-eta2.1e-4": 0.845289375,
   "hydro-lnL-imos-eta1e-4": 0.845289375,
   "hydro-lnL-imos-margeta": 0.845289375,
   "hydro-lnL-ims-proxy-margeta": 0.878326875
  },
  "scored_any_share": 0.878326875,
  "seconds": 122.50370383262634,
  "impacts32_sha": "65e3e288ef14f3984ad14adfc0bbae6c55be62d93ddadc2bb7bda67b922f9c6a",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-8.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-descent-climb/seed-9": {
  "stratum": "run-j-descent-climb",
  "seed": 9,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.94537353515625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.773999214172363,
    -8.564311027526855,
    -0.2102041244506836,
    3.159963369369507,
    3.5314676761627197
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.521040916442871,
    -6.129486083984375,
    -0.04517911374568939,
    2.8545291423797607,
    3.496626615524292
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.027544021606445,
    -5.084947109222412,
    -0.021221928298473358,
    2.6227705478668213,
    3.4669442176818848
   ],
   "hydro-lnL-imos-margeta": [
    -4.447778224945068,
    -2.3756136894226074,
    -0.15190643072128296,
    2.6189699172973633,
    3.2969324588775635
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.449020862579346,
    -3.1748955249786377,
    -0.24068045616149902,
    1.4826394319534302,
    1.9073034524917603
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.87267875,
   "hydro-lnL-imos-eta2.1e-4": 0.87267875,
   "hydro-lnL-imos-eta1e-4": 0.87267875,
   "hydro-lnL-imos-margeta": 0.87267875,
   "hydro-lnL-ims-proxy-margeta": 0.910903125
  },
  "scored_any_share": 0.910903125,
  "seconds": 127.7449209690094,
  "impacts32_sha": "d365f47e55074fc09fea68a12305a4b13cb20bae063ef6362574baf0f0500be8",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/descent-climb.toml",
    "config/sensitivity/run-j/size-dc.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-9.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-1": {
  "stratum": "run-j-free",
  "seed": 1,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 32.31048583984375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.333208084106445,
    -8.339407920837402,
    -0.18207493424415588,
    3.0814895629882812,
    3.5273685455322266
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.097965240478516,
    -5.978526592254639,
    -0.03895141929388046,
    2.732419967651367,
    3.490217924118042
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.675040245056152,
    -4.961569786071777,
    -0.0183224156498909,
    2.471953868865967,
    3.455131769180298
   ],
   "hydro-lnL-imos-margeta": [
    -4.346973419189453,
    -2.3321495056152344,
    -0.1376628577709198,
    2.5327510833740234,
    3.2750039100646973
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.356805324554443,
    -3.1184632778167725,
    -0.23664845526218414,
    1.456695795059204,
    1.9093904495239258
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8618458059580596,
   "hydro-lnL-imos-eta2.1e-4": 0.8618458059580596,
   "hydro-lnL-imos-eta1e-4": 0.8618458059580596,
   "hydro-lnL-imos-margeta": 0.8618458059580596,
   "hydro-lnL-ims-proxy-margeta": 0.9323683861838619
  },
  "scored_any_share": 0.9323683861838619,
  "seconds": 79.17954897880554,
  "impacts32_sha": "d19960483b01f5535b18f3de0325b39ebfabaa8ec9f190f3f06119a2a3147d8e",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-1.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-10": {
  "stratum": "run-j-free",
  "seed": 10,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 17.0135498046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.853723526000977,
    -8.608736038208008,
    -0.22694694995880127,
    3.1774730682373047,
    3.527953624725342
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.581473350524902,
    -6.171959400177002,
    -0.04904605448246002,
    2.888552665710449,
    3.4944567680358887
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.107531547546387,
    -5.130161762237549,
    -0.023032251745462418,
    2.6659188270568848,
    3.465118408203125
   ],
   "hydro-lnL-imos-margeta": [
    -4.4432172775268555,
    -2.4005022048950195,
    -0.15952745079994202,
    2.643296957015991,
    3.2983384132385254
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.549502849578857,
    -3.2471699714660645,
    -0.25590062141418457,
    1.4851689338684082,
    1.927312970161438
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8888478125,
   "hydro-lnL-imos-eta2.1e-4": 0.8888478125,
   "hydro-lnL-imos-eta1e-4": 0.8888478125,
   "hydro-lnL-imos-margeta": 0.8888478125,
   "hydro-lnL-ims-proxy-margeta": 0.9289315625
  },
  "scored_any_share": 0.9289315625,
  "seconds": 363.90479612350464,
  "impacts32_sha": "1d49fca63046539bc73f9d9d00dcbf1d13059d983c8e6bf0c3542fb7826ed568",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-10.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-11": {
  "stratum": "run-j-free",
  "seed": 11,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 17.0135498046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.114134788513184,
    -8.799449920654297,
    -0.22434523701667786,
    3.1373143196105957,
    3.5286808013916016
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.857810020446777,
    -6.269408226013184,
    -0.048395849764347076,
    2.819999933242798,
    3.4953625202178955
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.362604141235352,
    -5.18654203414917,
    -0.02273988164961338,
    2.585691452026367,
    3.4629762172698975
   ],
   "hydro-lnL-imos-margeta": [
    -4.48876953125,
    -2.390667676925659,
    -0.15855523943901062,
    2.595202922821045,
    3.2922492027282715
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.540776252746582,
    -3.222637891769409,
    -0.24840128421783447,
    1.4685003757476807,
    1.9089508056640625
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8776774732252678,
   "hydro-lnL-imos-eta2.1e-4": 0.8776774732252678,
   "hydro-lnL-imos-eta1e-4": 0.8776774732252678,
   "hydro-lnL-imos-margeta": 0.8776774732252678,
   "hydro-lnL-ims-proxy-margeta": 0.9142496075039249
  },
  "scored_any_share": 0.9142496075039249,
  "seconds": 358.2832612991333,
  "impacts32_sha": "70a57a5676fb562f908d9f5730778cf65594c078cd2959c6306401e63bcb1c2a",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-11.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-12": {
  "stratum": "run-j-free",
  "seed": 12,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 18.95904541015625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.689098358154297,
    -9.285972595214844,
    -0.24384716153144836,
    3.1465823650360107,
    3.5210394859313965
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.404330253601074,
    -6.584989547729492,
    -0.052946992218494415,
    2.8395185470581055,
    3.4875686168670654
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.868399620056152,
    -5.456182479858398,
    -0.024901658296585083,
    2.606577157974243,
    3.455439567565918
   ],
   "hydro-lnL-imos-margeta": [
    -4.653619289398193,
    -2.488189697265625,
    -0.16711118817329407,
    2.607736349105835,
    3.283409357070923
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.056625843048096,
    -3.4541475772857666,
    -0.2624816298484802,
    1.4385972023010254,
    1.8327205181121826
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.890310625,
   "hydro-lnL-imos-eta2.1e-4": 0.890310625,
   "hydro-lnL-imos-eta1e-4": 0.890310625,
   "hydro-lnL-imos-margeta": 0.890310625,
   "hydro-lnL-ims-proxy-margeta": 0.921633125
  },
  "scored_any_share": 0.921633125,
  "seconds": 360.11292695999146,
  "impacts32_sha": "97120916f38a4fc9cbd3a9da90fc3521d0570cd9253c84cc529991b20242d578",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-12.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-13": {
  "stratum": "run-j-free",
  "seed": 13,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 18.9208984375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.555619239807129,
    -8.430350303649902,
    -0.21775095164775848,
    3.199669361114502,
    3.527656078338623
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.300381660461426,
    -6.055805206298828,
    -0.04673056676983833,
    2.915886878967285,
    3.4958221912384033
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.844525337219238,
    -5.033710479736328,
    -0.02190200611948967,
    2.700314521789551,
    3.4664065837860107
   ],
   "hydro-lnL-imos-margeta": [
    -4.405281066894531,
    -2.3662378787994385,
    -0.15526539087295532,
    2.663283348083496,
    3.3001105785369873
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.500258922576904,
    -3.2024636268615723,
    -0.2540397644042969,
    1.4862182140350342,
    1.85810387134552
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89391125,
   "hydro-lnL-imos-eta2.1e-4": 0.89391125,
   "hydro-lnL-imos-eta1e-4": 0.89391125,
   "hydro-lnL-imos-margeta": 0.89391125,
   "hydro-lnL-ims-proxy-margeta": 0.9314296875
  },
  "scored_any_share": 0.9314296875,
  "seconds": 363.1335070133209,
  "impacts32_sha": "b7735f86e34b4ce86e26f5d2e569f041914d740f1cc60aab14d9d6b28208c2be",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-13.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-14": {
  "stratum": "run-j-free",
  "seed": 14,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 16.937255859375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.33699893951416,
    -8.83968448638916,
    -0.1840784102678299,
    3.0893983840942383,
    3.5240347385406494
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.057206153869629,
    -6.312280178070068,
    -0.03901515156030655,
    2.7495429515838623,
    3.4857397079467773
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.538564682006836,
    -5.226591110229492,
    -0.018240952864289284,
    2.494629383087158,
    3.4498043060302734
   ],
   "hydro-lnL-imos-margeta": [
    -4.5473408699035645,
    -2.411276340484619,
    -0.13914752006530762,
    2.544273614883423,
    3.2728497982025146
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.435794353485107,
    -3.152353048324585,
    -0.21878871321678162,
    1.4295763969421387,
    1.8614200353622437
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.836240075099249,
   "hydro-lnL-imos-eta2.1e-4": 0.836240075099249,
   "hydro-lnL-imos-eta1e-4": 0.836240075099249,
   "hydro-lnL-imos-margeta": 0.836240075099249,
   "hydro-lnL-ims-proxy-margeta": 0.8697213027869721
  },
  "scored_any_share": 0.8697213027869721,
  "seconds": 354.8637659549713,
  "impacts32_sha": "47320a80d0be8d72d128fcef49047b0eb8ecbf1abad337812238ac79807911ec",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-14.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-15": {
  "stratum": "run-j-free",
  "seed": 15,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 16.89910888671875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.935713768005371,
    -8.54565715789795,
    -0.1937016248703003,
    3.152784585952759,
    3.5237619876861572
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.669116973876953,
    -6.0532546043396,
    -0.0407186821103096,
    2.850383996963501,
    3.4880778789520264
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.151881217956543,
    -4.99838399887085,
    -0.018970197066664696,
    2.616882085800171,
    3.457139253616333
   ],
   "hydro-lnL-imos-margeta": [
    -4.391394138336182,
    -2.3093559741973877,
    -0.14440423250198364,
    2.6118710041046143,
    3.279161214828491
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.760383605957031,
    -3.3528523445129395,
    -0.24822039902210236,
    1.4382123947143555,
    1.9627670049667358
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8686125638743613,
   "hydro-lnL-imos-eta2.1e-4": 0.8686125638743613,
   "hydro-lnL-imos-eta1e-4": 0.8686125638743613,
   "hydro-lnL-imos-margeta": 0.8686125638743613,
   "hydro-lnL-ims-proxy-margeta": 0.9080477945220548
  },
  "scored_any_share": 0.9080477945220548,
  "seconds": 367.3734450340271,
  "impacts32_sha": "4a559b472ad16f4bbdaf3cf281332cdd8ba09464c7c95de100519d86ab64192c",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-15.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-16": {
  "stratum": "run-j-free",
  "seed": 16,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 17.89093017578125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -15.16547966003418,
    -9.452552795410156,
    -0.19003234803676605,
    3.067502021789551,
    3.5223891735076904
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.88453483581543,
    -6.676969528198242,
    -0.04038694500923157,
    2.695298194885254,
    3.4822211265563965
   ],
   "hydro-lnL-imos-eta1e-4": [
    -10.339303970336914,
    -5.503750801086426,
    -0.018895093351602554,
    2.4178173542022705,
    3.444088935852051
   ],
   "hydro-lnL-imos-margeta": [
    -4.7528862953186035,
    -2.4322898387908936,
    -0.14195823669433594,
    2.5108680725097656,
    3.2609963417053223
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.764800548553467,
    -3.2811214923858643,
    -0.23983412981033325,
    1.4386619329452515,
    1.9307233095169067
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8518382058820588,
   "hydro-lnL-imos-eta2.1e-4": 0.8518382058820588,
   "hydro-lnL-imos-eta1e-4": 0.8518382058820588,
   "hydro-lnL-imos-margeta": 0.8518382058820588,
   "hydro-lnL-ims-proxy-margeta": 0.9061190611906119
  },
  "scored_any_share": 0.9061190611906119,
  "seconds": 355.6535499095917,
  "impacts32_sha": "2114e4ad4a8193de382f7816a2eadc5bc13f152d8d3c5e3824d2939f16593934",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-16.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-17": {
  "stratum": "run-j-free",
  "seed": 17,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 17.852783203125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.866637229919434,
    -8.653468132019043,
    -0.20343980193138123,
    3.231639862060547,
    3.531687021255493
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.612763404846191,
    -6.188063621520996,
    -0.04376735910773277,
    2.9812841415405273,
    3.497084617614746
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.115306854248047,
    -5.141759395599365,
    -0.020577700808644295,
    2.78531813621521,
    3.4701027870178223
   ],
   "hydro-lnL-imos-margeta": [
    -4.4756903648376465,
    -2.3991732597351074,
    -0.14848710596561432,
    2.7109873294830322,
    3.3122706413269043
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.475644111633301,
    -3.194382905960083,
    -0.24108809232711792,
    1.50606107711792,
    1.8881356716156006
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8834715625,
   "hydro-lnL-imos-eta2.1e-4": 0.8834715625,
   "hydro-lnL-imos-eta1e-4": 0.8834715625,
   "hydro-lnL-imos-margeta": 0.8834715625,
   "hydro-lnL-ims-proxy-margeta": 0.928365
  },
  "scored_any_share": 0.928365,
  "seconds": 376.828351020813,
  "impacts32_sha": "7b4d771a6635a4ecd402ea1fd67c0688a60686cf7fb1faad87dc61c7f156909b",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-17.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-18": {
  "stratum": "run-j-free",
  "seed": 18,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.71649169921875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.38563060760498,
    -8.345934867858887,
    -0.1919810175895691,
    3.121673107147217,
    3.534703493118286
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.130147933959961,
    -5.968978404998779,
    -0.04108849912881851,
    2.7972569465637207,
    3.498936176300049
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.68954849243164,
    -4.956335544586182,
    -0.019281335175037384,
    2.5535190105438232,
    3.465250015258789
   ],
   "hydro-lnL-imos-margeta": [
    -4.341597080230713,
    -2.3457796573638916,
    -0.14278605580329895,
    2.57993745803833,
    3.2891483306884766
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.336667537689209,
    -3.1232399940490723,
    -0.23555125296115875,
    1.4703789949417114,
    1.921695351600647
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8647629148708513,
   "hydro-lnL-imos-eta2.1e-4": 0.8647629148708513,
   "hydro-lnL-imos-eta1e-4": 0.8647629148708513,
   "hydro-lnL-imos-margeta": 0.8647629148708513,
   "hydro-lnL-ims-proxy-margeta": 0.9212976620233798
  },
  "scored_any_share": 0.9212976620233798,
  "seconds": 294.6835572719574,
  "impacts32_sha": "326655a8c2d99a697d8820bbd41d3efe31bb6e16beef05c04686e5417423fd1f",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-18.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-2": {
  "stratum": "run-j-free",
  "seed": 2,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 18.463134765625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.866544723510742,
    -8.561982154846191,
    -0.22955763339996338,
    3.191539764404297,
    3.5265464782714844
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.60906982421875,
    -6.143714904785156,
    -0.04979192465543747,
    2.9046523571014404,
    3.494976758956909
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.117888450622559,
    -5.108536243438721,
    -0.023460395634174347,
    2.684077739715576,
    3.4646074771881104
   ],
   "hydro-lnL-imos-margeta": [
    -4.453028202056885,
    -2.3989946842193604,
    -0.16056209802627563,
    2.6558706760406494,
    3.297191619873047
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.590970993041992,
    -3.2661328315734863,
    -0.2622188329696655,
    1.4876716136932373,
    1.878981113433838
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.896959467905321,
   "hydro-lnL-imos-eta2.1e-4": 0.896959467905321,
   "hydro-lnL-imos-eta1e-4": 0.896959467905321,
   "hydro-lnL-imos-margeta": 0.896959467905321,
   "hydro-lnL-ims-proxy-margeta": 0.9400880991190088
  },
  "scored_any_share": 0.9400880991190088,
  "seconds": 380.03541564941406,
  "impacts32_sha": "9573821a28d82974dfae5fd1327e5f23e1dd0d829aa004658639fd31e6055538",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-2.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-3": {
  "stratum": "run-j-free",
  "seed": 3,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-margeta"
  ],
  "free_gib_at_write": 19.4549560546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.595586776733398,
    -8.580218315124512,
    -0.23350758850574493,
    3.214468002319336,
    3.5261929035186768
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.352389335632324,
    -6.190030097961426,
    -0.05097576230764389,
    2.9502029418945312,
    3.4946541786193848
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.906048774719238,
    -5.175970077514648,
    -0.024048250168561935,
    2.7491228580474854,
    3.4658539295196533
   ],
   "hydro-lnL-imos-margeta": [
    -4.4840288162231445,
    -2.44758939743042,
    -0.16222521662712097,
    2.6886579990386963,
    3.29740047454834
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.597947120666504,
    -3.2950222492218018,
    -0.2598589062690735,
    1.5018359422683716,
    1.877587914466858
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9070840625,
   "hydro-lnL-imos-eta2.1e-4": 0.9070840625,
   "hydro-lnL-imos-eta1e-4": 0.9070840625,
   "hydro-lnL-imos-margeta": 0.9070840625,
   "hydro-lnL-ims-proxy-margeta": 0.943935
  },
  "scored_any_share": 0.943935,
  "seconds": 402.7642459869385,
  "impacts32_sha": "68db42ed4e081ddb2c27f605315d46decd08a8bb92849d6d58f6c269e28b033f",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-3.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-4": {
  "stratum": "run-j-free",
  "seed": 4,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 20.44677734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.79922103881836,
    -8.566462516784668,
    -0.23240900039672852,
    3.1541101932525635,
    3.5351624488830566
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.552861213684082,
    -6.136998176574707,
    -0.050554484128952026,
    2.8474721908569336,
    3.4999141693115234
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.06305980682373,
    -5.104983329772949,
    -0.023805854842066765,
    2.620328903198242,
    3.467757225036621
   ],
   "hydro-lnL-imos-margeta": [
    -4.451130390167236,
    -2.4027957916259766,
    -0.16177445650100708,
    2.6159446239471436,
    3.2951691150665283
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.507978439331055,
    -3.2072694301605225,
    -0.2538793683052063,
    1.4862641096115112,
    1.9268724918365479
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8892728125,
   "hydro-lnL-imos-eta2.1e-4": 0.8892728125,
   "hydro-lnL-imos-eta1e-4": 0.8892728125,
   "hydro-lnL-imos-margeta": 0.8892728125,
   "hydro-lnL-ims-proxy-margeta": 0.9290409375
  },
  "scored_any_share": 0.9290409375,
  "seconds": 387.9652478694916,
  "impacts32_sha": "279e0d455eb85446f7b134a59aed62f0405c205b21db64557e399a621992442f",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-4.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-5": {
  "stratum": "run-j-free",
  "seed": 5,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 21.3623046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.54817008972168,
    -8.450465202331543,
    -0.22658583521842957,
    3.163203716278076,
    3.532158374786377
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.302901268005371,
    -6.067593574523926,
    -0.04918844252824783,
    2.857684373855591,
    3.498417854309082
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.829602241516113,
    -5.042699813842773,
    -0.023191599175333977,
    2.623857021331787,
    3.46842622756958
   ],
   "hydro-lnL-imos-margeta": [
    -4.405595302581787,
    -2.3784313201904297,
    -0.15918093919754028,
    2.6229569911956787,
    3.298844814300537
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.5149993896484375,
    -3.2017297744750977,
    -0.2549227476119995,
    1.4879460334777832,
    1.929965615272522
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8892421875,
   "hydro-lnL-imos-eta2.1e-4": 0.8892421875,
   "hydro-lnL-imos-eta1e-4": 0.8892421875,
   "hydro-lnL-imos-margeta": 0.8892421875,
   "hydro-lnL-ims-proxy-margeta": 0.933895
  },
  "scored_any_share": 0.933895,
  "seconds": 395.9464120864868,
  "impacts32_sha": "0e986deba9e33fabde092d16ce37f7374dc36064c41fa740559afac7d6d5968e",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-5.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-6": {
  "stratum": "run-j-free",
  "seed": 6,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 22.23968505859375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.82514762878418,
    -8.665035247802734,
    -0.2622157335281372,
    3.1546411514282227,
    3.5163469314575195
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.56521224975586,
    -6.194590091705322,
    -0.05777788162231445,
    2.8499014377593994,
    3.4842543601989746
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.077213287353516,
    -5.142741680145264,
    -0.027343492954969406,
    2.6188197135925293,
    3.4564099311828613
   ],
   "hydro-lnL-imos-margeta": [
    -4.448728084564209,
    -2.415705919265747,
    -0.1749853491783142,
    2.6148154735565186,
    3.2888009548187256
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.735750198364258,
    -3.3645806312561035,
    -0.2697458863258362,
    1.4466792345046997,
    1.8414729833602905
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9050559375,
   "hydro-lnL-imos-eta2.1e-4": 0.9050559375,
   "hydro-lnL-imos-eta1e-4": 0.9050559375,
   "hydro-lnL-imos-margeta": 0.9050559375,
   "hydro-lnL-ims-proxy-margeta": 0.9409203125
  },
  "scored_any_share": 0.9409203125,
  "seconds": 333.397079706192,
  "impacts32_sha": "57802370d38a6e7f6bdbf9dfb28d3b1587011fe6b736fb2feb6dfb7667fc4762",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-6.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-7": {
  "stratum": "run-j-free",
  "seed": 7,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.193359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.684877395629883,
    -8.55207633972168,
    -0.21364450454711914,
    3.122685432434082,
    3.532454252243042
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.44172191619873,
    -6.109776020050049,
    -0.04616592824459076,
    2.7995665073394775,
    3.4964773654937744
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.951971054077148,
    -5.074187278747559,
    -0.021700279787182808,
    2.5533759593963623,
    3.4630556106567383
   ],
   "hydro-lnL-imos-margeta": [
    -4.416205406188965,
    -2.385197401046753,
    -0.15338458120822906,
    2.58062481880188,
    3.2879583835601807
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.452157497406006,
    -3.1965434551239014,
    -0.2429891675710678,
    1.464674711227417,
    1.9403424263000488
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8751409375,
   "hydro-lnL-imos-eta2.1e-4": 0.8751409375,
   "hydro-lnL-imos-eta1e-4": 0.8751409375,
   "hydro-lnL-imos-margeta": 0.8751409375,
   "hydro-lnL-ims-proxy-margeta": 0.91848
  },
  "scored_any_share": 0.91848,
  "seconds": 333.72836923599243,
  "impacts32_sha": "b2396feafecea7698370fd229e198a304f230aa5a66a0c5ee2e44fac5d8482a1",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-7.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-8": {
  "stratum": "run-j-free",
  "seed": 8,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.07891845703125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.935513496398926,
    -8.633770942687988,
    -0.20108887553215027,
    3.0983963012695312,
    3.525808095932007
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.676203727722168,
    -6.151811599731445,
    -0.04312504455447197,
    2.761826992034912,
    3.487241506576538
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.181730270385742,
    -5.100306034088135,
    -0.020249471068382263,
    2.5117061138153076,
    3.4519705772399902
   ],
   "hydro-lnL-imos-margeta": [
    -4.457566261291504,
    -2.3787975311279297,
    -0.1474098265171051,
    2.555293083190918,
    3.2753560543060303
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.504545211791992,
    -3.1710379123687744,
    -0.23358428478240967,
    1.4404574632644653,
    1.9059977531433105
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.85796375,
   "hydro-lnL-imos-eta2.1e-4": 0.85796375,
   "hydro-lnL-imos-eta1e-4": 0.85796375,
   "hydro-lnL-imos-margeta": 0.85796375,
   "hydro-lnL-ims-proxy-margeta": 0.898010625
  },
  "scored_any_share": 0.898010625,
  "seconds": 331.3710820674896,
  "impacts32_sha": "510057739b97f8cea916b10781b1a3b558e67496b571895eb2ded894b703e263",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-8.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-free/seed-9": {
  "stratum": "run-j-free",
  "seed": 9,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.1170654296875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.682363510131836,
    -9.101234436035156,
    -0.18747633695602417,
    3.1805880069732666,
    3.522780418395996
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.398453712463379,
    -6.441011905670166,
    -0.03938746452331543,
    2.906970739364624,
    3.493335723876953
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.870973587036133,
    -5.3269524574279785,
    -0.01829800382256508,
    2.698046922683716,
    3.466090440750122
   ],
   "hydro-lnL-imos-margeta": [
    -4.639368534088135,
    -2.420283079147339,
    -0.14138054847717285,
    2.6578304767608643,
    3.3023791313171387
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.689752101898193,
    -3.24772047996521,
    -0.22585804760456085,
    1.4568384885787964,
    1.7979743480682373
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8472262847628477,
   "hydro-lnL-imos-eta2.1e-4": 0.8472262847628477,
   "hydro-lnL-imos-eta1e-4": 0.8472262847628477,
   "hydro-lnL-imos-margeta": 0.8472262847628477,
   "hydro-lnL-ims-proxy-margeta": 0.8793322308223083
  },
  "scored_any_share": 0.8793322308223083,
  "seconds": 326.5488700866699,
  "impacts32_sha": "78840e233f8cfa12312db345f7a841f52a46dc254d9c799ec54c621a7c5dfcc4",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/free.toml",
    "config/sensitivity/run-j/size-free.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-9.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-1": {
  "stratum": "run-j-repro-radar",
  "seed": 1,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.33502197265625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.964400291442871,
    -8.648301124572754,
    -0.21077102422714233,
    3.1138925552368164,
    3.524996042251587
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.698716163635254,
    -6.170395374298096,
    -0.04548938572406769,
    2.783097267150879,
    3.489330530166626
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.194263458251953,
    -5.121015548706055,
    -0.021401140838861465,
    2.5387401580810547,
    3.4551491737365723
   ],
   "hydro-lnL-imos-margeta": [
    -4.488504886627197,
    -2.3903071880340576,
    -0.15176798403263092,
    2.568730592727661,
    3.278975248336792
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.624544620513916,
    -3.2186789512634277,
    -0.2450028359889984,
    1.443830966949463,
    1.8886356353759766
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8706777692776928,
   "hydro-lnL-imos-eta2.1e-4": 0.8706777692776928,
   "hydro-lnL-imos-eta1e-4": 0.8706777692776928,
   "hydro-lnL-imos-margeta": 0.8706777692776928,
   "hydro-lnL-ims-proxy-margeta": 0.916369476194762
  },
  "scored_any_share": 0.916369476194762,
  "seconds": 194.4853949546814,
  "impacts32_sha": "d60b6cd542e5fcd656db0c7ea4742831503e440f6f1c0c7a5cc8fe609220a1a4",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-1.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-10": {
  "stratum": "run-j-repro-radar",
  "seed": 10,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 25.634765625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.915082931518555,
    -8.573709487915039,
    -0.22083896398544312,
    3.199873208999634,
    3.530877113342285
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.647686004638672,
    -6.147641181945801,
    -0.048000410199165344,
    2.921351432800293,
    3.499321460723877
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.158263206481934,
    -5.115495681762695,
    -0.022637438029050827,
    2.705540418624878,
    3.470551013946533
   ],
   "hydro-lnL-imos-margeta": [
    -4.47704553604126,
    -2.4050731658935547,
    -0.15654143691062927,
    2.668192148208618,
    3.3085110187530518
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.663201808929443,
    -3.259381055831909,
    -0.25503236055374146,
    1.4917550086975098,
    1.8999966382980347
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8947504274957251,
   "hydro-lnL-imos-eta2.1e-4": 0.8947504274957251,
   "hydro-lnL-imos-eta1e-4": 0.8947504274957251,
   "hydro-lnL-imos-margeta": 0.8947504274957251,
   "hydro-lnL-ims-proxy-margeta": 0.9373990635093649
  },
  "scored_any_share": 0.9373990635093649,
  "seconds": 201.15910506248474,
  "impacts32_sha": "9b7a54f203369cb43bdd46957cd6d3b9ed240762328d91b061f03374ca18973b",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-10.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-11": {
  "stratum": "run-j-repro-radar",
  "seed": 11,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 25.5584716796875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.02292251586914,
    -8.664268493652344,
    -0.22652073204517365,
    3.1728765964508057,
    3.527397871017456
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.742263793945312,
    -6.196754455566406,
    -0.04903365671634674,
    2.8756473064422607,
    3.493485689163208
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.236742973327637,
    -5.148106098175049,
    -0.023042280226945877,
    2.6484756469726562,
    3.4625449180603027
   ],
   "hydro-lnL-imos-margeta": [
    -4.480261325836182,
    -2.401984214782715,
    -0.15919923782348633,
    2.6340343952178955,
    3.2910702228546143
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.6214070320129395,
    -3.2630128860473633,
    -0.2557375431060791,
    1.4787935018539429,
    1.8848910331726074
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89068875,
   "hydro-lnL-imos-eta2.1e-4": 0.89068875,
   "hydro-lnL-imos-eta1e-4": 0.89068875,
   "hydro-lnL-imos-margeta": 0.89068875,
   "hydro-lnL-ims-proxy-margeta": 0.9303746875
  },
  "scored_any_share": 0.9303746875,
  "seconds": 201.62165665626526,
  "impacts32_sha": "52c1e4ee885d23e5d297667eea91e0f7b016e625e8b664423d50c6151cd268a2",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-11.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-12": {
  "stratum": "run-j-repro-radar",
  "seed": 12,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.46038818359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.951952934265137,
    -8.623607635498047,
    -0.21580572426319122,
    3.1802945137023926,
    3.528015375137329
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.691452026367188,
    -6.194282054901123,
    -0.04653920233249664,
    2.889214277267456,
    3.49674654006958
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.216862678527832,
    -5.151035785675049,
    -0.021897997707128525,
    2.668890953063965,
    3.4678471088409424
   ],
   "hydro-lnL-imos-margeta": [
    -4.511255741119385,
    -2.4120028018951416,
    -0.15432965755462646,
    2.645958662033081,
    3.3018038272857666
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.631338119506836,
    -3.2533576488494873,
    -0.24858954548835754,
    1.4793543815612793,
    1.8733705282211304
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.881200625,
   "hydro-lnL-imos-eta2.1e-4": 0.881200625,
   "hydro-lnL-imos-eta1e-4": 0.881200625,
   "hydro-lnL-imos-margeta": 0.881200625,
   "hydro-lnL-ims-proxy-margeta": 0.92021375
  },
  "scored_any_share": 0.92021375,
  "seconds": 198.95683312416077,
  "impacts32_sha": "4abca651e95ecc920a24eb6bc2f3004c1620996b5d8d00a4c1035f93299de2de",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-12.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-13": {
  "stratum": "run-j-repro-radar",
  "seed": 13,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.4222412109375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.293893814086914,
    -8.82091236114502,
    -0.1833905279636383,
    3.070847749710083,
    3.523371934890747
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.011545181274414,
    -6.267857551574707,
    -0.0391400083899498,
    2.716369152069092,
    3.484065294265747
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.492813110351562,
    -5.192052364349365,
    -0.01834678463637829,
    2.4583020210266113,
    3.4476125240325928
   ],
   "hydro-lnL-imos-margeta": [
    -4.539974212646484,
    -2.3919336795806885,
    -0.13840189576148987,
    2.5260677337646484,
    3.267348527908325
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.446994304656982,
    -3.141693115234375,
    -0.22363358736038208,
    1.4297131299972534,
    1.8944967985153198
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8428228032280323,
   "hydro-lnL-imos-eta2.1e-4": 0.8428228032280323,
   "hydro-lnL-imos-eta1e-4": 0.8428228032280323,
   "hydro-lnL-imos-margeta": 0.8428228032280323,
   "hydro-lnL-ims-proxy-margeta": 0.8857138571385714
  },
  "scored_any_share": 0.8857138571385714,
  "seconds": 192.1196300983429,
  "impacts32_sha": "8596b83486882d92dd9594eeb69235d5477355aab425faabf97330f93b35ed20",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-13.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-14": {
  "stratum": "run-j-repro-radar",
  "seed": 14,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.345947265625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.813191413879395,
    -8.547271728515625,
    -0.16295531392097473,
    3.166590452194214,
    3.5228447914123535
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.550552368164062,
    -6.098127365112305,
    -0.034274615347385406,
    2.8798367977142334,
    3.4906342029571533
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.064215660095215,
    -5.054845333099365,
    -0.016022827476263046,
    2.661465644836426,
    3.4605259895324707
   ],
   "hydro-lnL-imos-margeta": [
    -4.435347557067871,
    -2.3586068153381348,
    -0.12806865572929382,
    2.636404514312744,
    3.2934114933013916
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.544045925140381,
    -3.1751933097839355,
    -0.21786713600158691,
    1.4555305242538452,
    1.8551148176193237
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8391058910589105,
   "hydro-lnL-imos-eta2.1e-4": 0.8391058910589105,
   "hydro-lnL-imos-eta1e-4": 0.8391058910589105,
   "hydro-lnL-imos-margeta": 0.8391058910589105,
   "hydro-lnL-ims-proxy-margeta": 0.8825610131101311
  },
  "scored_any_share": 0.8825610131101311,
  "seconds": 190.55673694610596,
  "impacts32_sha": "4c46e60ca117147c7bb93e87f58acca39e6cc1b096f9e698f515fd440273c170",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-14.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-15": {
  "stratum": "run-j-repro-radar",
  "seed": 15,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.2696533203125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.999414443969727,
    -8.662191390991211,
    -0.21485087275505066,
    3.163785934448242,
    3.52176570892334
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.726305961608887,
    -6.186434268951416,
    -0.04623711109161377,
    2.864974021911621,
    3.487412929534912
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.233160018920898,
    -5.141045093536377,
    -0.021723547950387,
    2.6392714977264404,
    3.456367254257202
   ],
   "hydro-lnL-imos-margeta": [
    -4.49503231048584,
    -2.4055237770080566,
    -0.153902068734169,
    2.6242642402648926,
    3.2853901386260986
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.711623668670654,
    -3.291987895965576,
    -0.2533206343650818,
    1.4652550220489502,
    1.8641045093536377
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8840905340946591,
   "hydro-lnL-imos-eta2.1e-4": 0.8840905340946591,
   "hydro-lnL-imos-eta1e-4": 0.8840905340946591,
   "hydro-lnL-imos-margeta": 0.8840905340946591,
   "hydro-lnL-ims-proxy-margeta": 0.9263447990520095
  },
  "scored_any_share": 0.9263447990520095,
  "seconds": 193.62876796722412,
  "impacts32_sha": "325d142256a025a53a275a1a4b26ec611f33da50cc5f42736f62ff32e47b13c2",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-15.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-16": {
  "stratum": "run-j-repro-radar",
  "seed": 16,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.956298828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.040215492248535,
    -8.75252628326416,
    -0.1841890960931778,
    3.053015947341919,
    3.5233335494995117
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.777420043945312,
    -6.196354866027832,
    -0.03928925096988678,
    2.6903064250946045,
    3.4818167686462402
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.276998519897461,
    -5.120057582855225,
    -0.018448207527399063,
    2.42458176612854,
    3.444340705871582
   ],
   "hydro-lnL-imos-margeta": [
    -4.4750494956970215,
    -2.347588062286377,
    -0.13898131251335144,
    2.5057854652404785,
    3.261643409729004
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.382684707641602,
    -3.0941708087921143,
    -0.22662796080112457,
    1.4378983974456787,
    1.9241620302200317
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8481281687816878,
   "hydro-lnL-imos-eta2.1e-4": 0.8481281687816878,
   "hydro-lnL-imos-eta1e-4": 0.8481281687816878,
   "hydro-lnL-imos-margeta": 0.8481281687816878,
   "hydro-lnL-ims-proxy-margeta": 0.8954467669676697
  },
  "scored_any_share": 0.8954467669676697,
  "seconds": 151.52058792114258,
  "impacts32_sha": "ffc1526c516585b799b497ee740e64e2a42f16dad06eea5279e9dfd3193db1d9",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-16.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-2": {
  "stratum": "run-j-repro-radar",
  "seed": 2,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.25872802734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.619373321533203,
    -8.47159194946289,
    -0.2093113362789154,
    3.157827854156494,
    3.5289628505706787
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.382952690124512,
    -6.087883472442627,
    -0.045234426856040955,
    2.849113702774048,
    3.4933888912200928
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.921701431274414,
    -5.058074951171875,
    -0.021257609128952026,
    2.614748001098633,
    3.461113691329956
   ],
   "hydro-lnL-imos-margeta": [
    -4.433183670043945,
    -2.37571382522583,
    -0.1510862112045288,
    2.6155142784118652,
    3.2863686084747314
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.522100448608398,
    -3.1943531036376953,
    -0.2509280741214752,
    1.482229471206665,
    1.9202638864517212
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8819266317663177,
   "hydro-lnL-imos-eta2.1e-4": 0.8819266317663177,
   "hydro-lnL-imos-eta1e-4": 0.8819266317663177,
   "hydro-lnL-imos-margeta": 0.8819266317663177,
   "hydro-lnL-ims-proxy-margeta": 0.9322015095150952
  },
  "scored_any_share": 0.9322015095150952,
  "seconds": 201.68592810630798,
  "impacts32_sha": "6cc7a4e6f33fd12ee7ff952baf2b1a881101e26c6f0bb4e082bab788292d12a9",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-2.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-3": {
  "stratum": "run-j-repro-radar",
  "seed": 3,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.2205810546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.072144508361816,
    -8.732929229736328,
    -0.20017221570014954,
    3.161813735961914,
    3.5266592502593994
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.796168327331543,
    -6.217997074127197,
    -0.04285987466573715,
    2.864729166030884,
    3.493623733520508
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.30945110321045,
    -5.151125431060791,
    -0.020129039883613586,
    2.6353678703308105,
    3.4620227813720703
   ],
   "hydro-lnL-imos-margeta": [
    -4.49153470993042,
    -2.3809754848480225,
    -0.1468941569328308,
    2.624507427215576,
    3.2917914390563965
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.521158695220947,
    -3.1760056018829346,
    -0.23777443170547485,
    1.4668279886245728,
    1.8741897344589233
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.862838125,
   "hydro-lnL-imos-eta2.1e-4": 0.862838125,
   "hydro-lnL-imos-eta1e-4": 0.862838125,
   "hydro-lnL-imos-margeta": 0.862838125,
   "hydro-lnL-ims-proxy-margeta": 0.9031734375
  },
  "scored_any_share": 0.9031734375,
  "seconds": 196.4456868171692,
  "impacts32_sha": "13814fb241fd85d7f482c2be24d150b44709cb2e315fad7277fe8c50d66ea2fa",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-3.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-4": {
  "stratum": "run-j-repro-radar",
  "seed": 4,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 24.83367919921875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.747894287109375,
    -8.541675567626953,
    -0.21889576315879822,
    3.163881778717041,
    3.5303795337677
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.499236106872559,
    -6.122451305389404,
    -0.04742987081408501,
    2.8627729415893555,
    3.498483896255493
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.024895668029785,
    -5.086202144622803,
    -0.022319603711366653,
    2.63663387298584,
    3.468093156814575
   ],
   "hydro-lnL-imos-margeta": [
    -4.456953048706055,
    -2.394670009613037,
    -0.15571504831314087,
    2.6268606185913086,
    3.3008604049682617
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.541475772857666,
    -3.2130353450775146,
    -0.2499728500843048,
    1.4901223182678223,
    1.9031684398651123
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.878174375,
   "hydro-lnL-imos-eta2.1e-4": 0.878174375,
   "hydro-lnL-imos-eta1e-4": 0.878174375,
   "hydro-lnL-imos-margeta": 0.878174375,
   "hydro-lnL-ims-proxy-margeta": 0.9221403125
  },
  "scored_any_share": 0.9221403125,
  "seconds": 188.58126711845398,
  "impacts32_sha": "1527a2d0644c966c5a88a9940e82e7e15b8307fa3a0a5a2acb2a96032371f9ef",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-4.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-5": {
  "stratum": "run-j-repro-radar",
  "seed": 5,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 24.60479736328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.87148666381836,
    -8.586051940917969,
    -0.17811815440654755,
    3.0836360454559326,
    3.527946949005127
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.613256454467773,
    -6.117645263671875,
    -0.037975721061229706,
    2.7229864597320557,
    3.489013433456421
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.127458572387695,
    -5.064073085784912,
    -0.017838221043348312,
    2.458181142807007,
    3.4529223442077637
   ],
   "hydro-lnL-imos-margeta": [
    -4.447093963623047,
    -2.3560218811035156,
    -0.13564670085906982,
    2.528463363647461,
    3.272385597229004
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.379253387451172,
    -3.1157824993133545,
    -0.22499710321426392,
    1.4450024366378784,
    1.8950746059417725
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8400584375,
   "hydro-lnL-imos-eta2.1e-4": 0.8400584375,
   "hydro-lnL-imos-eta1e-4": 0.8400584375,
   "hydro-lnL-imos-margeta": 0.8400584375,
   "hydro-lnL-ims-proxy-margeta": 0.8854846875
  },
  "scored_any_share": 0.8854846875,
  "seconds": 183.85602807998657,
  "impacts32_sha": "1cd45212b2b8a9f1f70be71f8fcf8c83b7cd4b4053474b7d2958697ea949fa7a",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-5.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-6": {
  "stratum": "run-j-repro-radar",
  "seed": 6,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 24.10888671875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.945775985717773,
    -8.636436462402344,
    -0.23590344190597534,
    3.1264898777008057,
    3.52278733253479
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.680887222290039,
    -6.194133281707764,
    -0.05144978314638138,
    2.801447868347168,
    3.485398292541504
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.193984985351562,
    -5.154731750488281,
    -0.024231359362602234,
    2.561603307723999,
    3.450252056121826
   ],
   "hydro-lnL-imos-margeta": [
    -4.508234977722168,
    -2.437875509262085,
    -0.1633749008178711,
    2.580333709716797,
    3.273228168487549
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.736180305480957,
    -3.3235092163085938,
    -0.2622048556804657,
    1.4619141817092896,
    1.9251898527145386
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.894028125,
   "hydro-lnL-imos-eta2.1e-4": 0.894028125,
   "hydro-lnL-imos-eta1e-4": 0.894028125,
   "hydro-lnL-imos-margeta": 0.894028125,
   "hydro-lnL-ims-proxy-margeta": 0.9355678125
  },
  "scored_any_share": 0.9355678125,
  "seconds": 186.80939388275146,
  "impacts32_sha": "f875bf4fc2a97dc4aa63d994f10e0fd4f518570ad4243732ff0deef5323a0891",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-6.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-7": {
  "stratum": "run-j-repro-radar",
  "seed": 7,
  "rows": 3199968,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 23.956298828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.103816032409668,
    -8.741275787353516,
    -0.20391888916492462,
    3.185589551925659,
    3.5232656002044678
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.84453296661377,
    -6.237717151641846,
    -0.04363492876291275,
    2.9039418697357178,
    3.4925758838653564
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.327905654907227,
    -5.174077033996582,
    -0.020433533936738968,
    2.6814687252044678,
    3.4641315937042236
   ],
   "hydro-lnL-imos-margeta": [
    -4.503735065460205,
    -2.4039125442504883,
    -0.1487572193145752,
    2.6523187160491943,
    3.2970218658447266
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.639349460601807,
    -3.2488291263580322,
    -0.24637404084205627,
    1.4660186767578125,
    1.8383350372314453
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8775578380783808,
   "hydro-lnL-imos-eta2.1e-4": 0.8775578380783808,
   "hydro-lnL-imos-eta1e-4": 0.8775578380783808,
   "hydro-lnL-imos-margeta": 0.8775578380783808,
   "hydro-lnL-ims-proxy-margeta": 0.9216026535265353
  },
  "scored_any_share": 0.9216026535265353,
  "seconds": 185.94677710533142,
  "impacts32_sha": "3c839245a67c74aacc55d17206f4e5a7e508044c6cf0af32054c5cc357803f6c",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-7.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-8": {
  "stratum": "run-j-repro-radar",
  "seed": 8,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 25.787353515625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.69987678527832,
    -8.493451118469238,
    -0.1886589527130127,
    3.026158094406128,
    3.5205180644989014
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.450247764587402,
    -6.028666973114014,
    -0.04028359055519104,
    2.6475906372070312,
    3.4787707328796387
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.953402519226074,
    -4.976107597351074,
    -0.018907878547906876,
    2.371086835861206,
    3.439765691757202
   ],
   "hydro-lnL-imos-margeta": [
    -4.358327388763428,
    -2.309147357940674,
    -0.14114850759506226,
    2.4746499061584473,
    3.251861095428467
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.336584568023682,
    -3.065176486968994,
    -0.22523939609527588,
    1.4127154350280762,
    1.858237862586975
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8471815625,
   "hydro-lnL-imos-eta2.1e-4": 0.8471815625,
   "hydro-lnL-imos-eta1e-4": 0.8471815625,
   "hydro-lnL-imos-margeta": 0.8471815625,
   "hydro-lnL-ims-proxy-margeta": 0.8887296875
  },
  "scored_any_share": 0.8887296875,
  "seconds": 189.667053937912,
  "impacts32_sha": "957161ffcdbc2bc6c9d47172e9c449deac05b6de992b46d46ef0bbb4a101bdfa",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-8.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-repro-radar/seed-9": {
  "stratum": "run-j-repro-radar",
  "seed": 9,
  "rows": 3200032,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 25.7110595703125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.338703155517578,
    -8.835947036743164,
    -0.21589484810829163,
    3.1718947887420654,
    3.5222649574279785
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.058497428894043,
    -6.311244487762451,
    -0.04632670804858208,
    2.8807449340820312,
    3.4914863109588623
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.534383773803711,
    -5.23913049697876,
    -0.021742943674325943,
    2.658055305480957,
    3.4618377685546875
   ],
   "hydro-lnL-imos-margeta": [
    -4.587281703948975,
    -2.428720235824585,
    -0.15462413430213928,
    2.6368112564086914,
    3.2953996658325195
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.807958602905273,
    -3.3186087608337402,
    -0.24848219752311707,
    1.4452838897705078,
    1.8451040983200073
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8763543614563855,
   "hydro-lnL-imos-eta2.1e-4": 0.8763543614563855,
   "hydro-lnL-imos-eta1e-4": 0.8763543614563855,
   "hydro-lnL-imos-margeta": 0.8763543614563855,
   "hydro-lnL-ims-proxy-margeta": 0.9119483805161949
  },
  "scored_any_share": 0.9119483805161949,
  "seconds": 196.32375812530518,
  "impacts32_sha": "fa62f0b7113f32e4beabcd39464a7ac994d1324c1273a33298b9fb392b68d758",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/run-j/size-repro.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-9.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-1": {
  "stratum": "run-j-waypoints",
  "seed": 1,
  "rows": 6399872,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 31.85272216796875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.688619613647461,
    -9.052913665771484,
    -0.27234214544296265,
    3.1926767826080322,
    3.5214040279388428
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.409018516540527,
    -6.499688148498535,
    -0.05982354283332825,
    2.913252353668213,
    3.491931915283203
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.8733491897583,
    -5.421397686004639,
    -0.02820480428636074,
    2.6980011463165283,
    3.4631459712982178
   ],
   "hydro-lnL-imos-margeta": [
    -4.744081497192383,
    -2.548656702041626,
    -0.1791413426399231,
    2.659904718399048,
    3.298475503921509
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.1872453689575195,
    -3.5546159744262695,
    -0.2834024727344513,
    1.500308632850647,
    1.9156403541564941
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9174755370107402,
   "hydro-lnL-imos-eta2.1e-4": 0.9174755370107402,
   "hydro-lnL-imos-eta1e-4": 0.9174755370107402,
   "hydro-lnL-imos-margeta": 0.9174755370107402,
   "hydro-lnL-ims-proxy-margeta": 0.9491030445608912
  },
  "scored_any_share": 0.9491030445608912,
  "seconds": 267.22334909439087,
  "impacts32_sha": "c61b3f7b8d384e995e960fd845c81905bf7e9ec60970b62efba0c54b4767d59c",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-1.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-10": {
  "stratum": "run-j-waypoints",
  "seed": 10,
  "rows": 6400064,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.18243408203125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.592220306396484,
    -8.39659309387207,
    -0.25177597999572754,
    3.214012861251831,
    3.5251998901367188
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.334454536437988,
    -6.08125114440918,
    -0.054793380200862885,
    2.942640781402588,
    3.495711088180542
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.866341590881348,
    -5.090728282928467,
    -0.02574159950017929,
    2.733691692352295,
    3.4677793979644775
   ],
   "hydro-lnL-imos-margeta": [
    -4.485424518585205,
    -2.4717235565185547,
    -0.1704871952533722,
    2.6820971965789795,
    3.304274082183838
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.982281684875488,
    -3.441582202911377,
    -0.27494651079177856,
    1.5242881774902344,
    1.9685295820236206
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9134249282507175,
   "hydro-lnL-imos-eta2.1e-4": 0.9134249282507175,
   "hydro-lnL-imos-eta1e-4": 0.9134249282507175,
   "hydro-lnL-imos-margeta": 0.9134249282507175,
   "hydro-lnL-ims-proxy-margeta": 0.949835032899671
  },
  "scored_any_share": 0.949835032899671,
  "seconds": 240.15639400482178,
  "impacts32_sha": "e617b4baf1833c892a95846736ea664788a02bbc75e99100940924ff15225b3e",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-10.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-11": {
  "stratum": "run-j-waypoints",
  "seed": 11,
  "rows": 6400064,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.9154052734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.776768684387207,
    -8.537463188171387,
    -0.24689529836177826,
    3.2187111377716064,
    3.5232439041137695
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.514931678771973,
    -6.140866756439209,
    -0.05337359756231308,
    2.9574952125549316,
    3.4936978816986084
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.042271614074707,
    -5.114647388458252,
    -0.025033097714185715,
    2.756868839263916,
    3.4652366638183594
   ],
   "hydro-lnL-imos-margeta": [
    -4.488710880279541,
    -2.4267303943634033,
    -0.16873812675476074,
    2.694354772567749,
    3.3026480674743652
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.949994087219238,
    -3.4204905033111572,
    -0.27454042434692383,
    1.503036379814148,
    1.8709540367126465
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9116360398896011,
   "hydro-lnL-imos-eta2.1e-4": 0.9116360398896011,
   "hydro-lnL-imos-eta1e-4": 0.9116360398896011,
   "hydro-lnL-imos-margeta": 0.9116360398896011,
   "hydro-lnL-ims-proxy-margeta": 0.9457191365586344
  },
  "scored_any_share": 0.9457191365586344,
  "seconds": 241.49200892448425,
  "impacts32_sha": "0c032e352a99eccacfdbc43e1f6b522edacdcf98a7746a5017bee7ea89d83864",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-11.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-12": {
  "stratum": "run-j-waypoints",
  "seed": 12,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.02984619140625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.64304256439209,
    -8.515536308288574,
    -0.23412199318408966,
    3.193918466567993,
    3.5249640941619873
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.407231330871582,
    -6.204588413238525,
    -0.0506974533200264,
    2.903395175933838,
    3.4943597316741943
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.948251724243164,
    -5.203436374664307,
    -0.023826979100704193,
    2.678431510925293,
    3.4638330936431885
   ],
   "hydro-lnL-imos-margeta": [
    -4.565812110900879,
    -2.495230197906494,
    -0.16268405318260193,
    2.6529061794281006,
    3.294633388519287
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.815834045410156,
    -3.3888254165649414,
    -0.26342296600341797,
    1.504228949546814,
    1.8688722848892212
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89460984375,
   "hydro-lnL-imos-eta2.1e-4": 0.89460984375,
   "hydro-lnL-imos-eta1e-4": 0.89460984375,
   "hydro-lnL-imos-margeta": 0.89460984375,
   "hydro-lnL-ims-proxy-margeta": 0.93249640625
  },
  "scored_any_share": 0.93249640625,
  "seconds": 240.53859519958496,
  "impacts32_sha": "2c781c12e10b640de3481c11e93ef9ff2a6b71a04f569499adfe8677f795e19e",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-12.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-13": {
  "stratum": "run-j-waypoints",
  "seed": 13,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.72467041015625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.790284156799316,
    -8.516256332397461,
    -0.2228662222623825,
    3.1754331588745117,
    3.528010129928589
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.530234336853027,
    -6.1260576248168945,
    -0.04790916293859482,
    2.8782687187194824,
    3.4945123195648193
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.036469459533691,
    -5.096807479858398,
    -0.02246759459376335,
    2.6503584384918213,
    3.463974714279175
   ],
   "hydro-lnL-imos-margeta": [
    -4.471400260925293,
    -2.405975818634033,
    -0.15771743655204773,
    2.6349222660064697,
    3.2951974868774414
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.633199691772461,
    -3.2535157203674316,
    -0.2554128170013428,
    1.4923771619796753,
    1.8979874849319458
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89217,
   "hydro-lnL-imos-eta2.1e-4": 0.89217,
   "hydro-lnL-imos-eta1e-4": 0.89217,
   "hydro-lnL-imos-margeta": 0.89217,
   "hydro-lnL-ims-proxy-margeta": 0.93373515625
  },
  "scored_any_share": 0.93373515625,
  "seconds": 303.7972102165222,
  "impacts32_sha": "161d0444be2a407c35870cfc0878d38485b7456b60ab2c76562f7e2e90c25659",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-13.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-14": {
  "stratum": "run-j-waypoints",
  "seed": 14,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.57208251953125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.893199920654297,
    -8.606269836425781,
    -0.23595739901065826,
    3.137854814529419,
    3.5262792110443115
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.637595176696777,
    -6.185511112213135,
    -0.05080351233482361,
    2.8183820247650146,
    3.4916324615478516
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.137859344482422,
    -5.1452789306640625,
    -0.023809395730495453,
    2.578289031982422,
    3.459075927734375
   ],
   "hydro-lnL-imos-margeta": [
    -4.5026469230651855,
    -2.427037239074707,
    -0.1639113575220108,
    2.5926337242126465,
    3.285827875137329
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.742805004119873,
    -3.306744337081909,
    -0.2630212903022766,
    1.478548526763916,
    1.9177535772323608
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8942590625,
   "hydro-lnL-imos-eta2.1e-4": 0.8942590625,
   "hydro-lnL-imos-eta1e-4": 0.8942590625,
   "hydro-lnL-imos-margeta": 0.8942590625,
   "hydro-lnL-ims-proxy-margeta": 0.93233734375
  },
  "scored_any_share": 0.93233734375,
  "seconds": 298.5178859233856,
  "impacts32_sha": "982ec51a3bb8f5d160cec1951a8534c58d9ac33fa67edea7f96598d19c9606ae",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-14.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-15": {
  "stratum": "run-j-waypoints",
  "seed": 15,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.41949462890625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.80643081665039,
    -8.514963150024414,
    -0.243149533867836,
    3.17617130279541,
    3.5307211875915527
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.553176879882812,
    -6.110979080200195,
    -0.052687667310237885,
    2.8772530555725098,
    3.498495101928711
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.065481185913086,
    -5.092188358306885,
    -0.024760138243436813,
    2.6507012844085693,
    3.467132091522217
   ],
   "hydro-lnL-imos-margeta": [
    -4.472740650177002,
    -2.433762788772583,
    -0.16680869460105896,
    2.6355414390563965,
    3.2955617904663086
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.970266819000244,
    -3.4024112224578857,
    -0.2671580910682678,
    1.5029274225234985,
    1.9429607391357422
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90449109375,
   "hydro-lnL-imos-eta2.1e-4": 0.90449109375,
   "hydro-lnL-imos-eta1e-4": 0.90449109375,
   "hydro-lnL-imos-margeta": 0.90449109375,
   "hydro-lnL-ims-proxy-margeta": 0.94362765625
  },
  "scored_any_share": 0.94362765625,
  "seconds": 301.09733605384827,
  "impacts32_sha": "d1c00fca9f102d4c946bae10c2b1f5b8ef9da539de144c512294496ade8f6c70",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-15.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-16": {
  "stratum": "run-j-waypoints",
  "seed": 16,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.3050537109375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.491416931152344,
    -8.352487564086914,
    -0.21828757226467133,
    3.1685264110565186,
    3.5282371044158936
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.249680519104004,
    -5.992953300476074,
    -0.04685745760798454,
    2.864306688308716,
    3.4957001209259033
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.78913402557373,
    -4.981838703155518,
    -0.021964551880955696,
    2.633511543273926,
    3.4642202854156494
   ],
   "hydro-lnL-imos-margeta": [
    -4.402382850646973,
    -2.3707213401794434,
    -0.15579572319984436,
    2.625904083251953,
    3.2932848930358887
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.6464433670043945,
    -3.261350631713867,
    -0.25516006350517273,
    1.4948021173477173,
    1.9012967348098755
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8894821875,
   "hydro-lnL-imos-eta2.1e-4": 0.8894821875,
   "hydro-lnL-imos-eta1e-4": 0.8894821875,
   "hydro-lnL-imos-margeta": 0.8894821875,
   "hydro-lnL-ims-proxy-margeta": 0.9340740625
  },
  "scored_any_share": 0.9340740625,
  "seconds": 300.9738438129425,
  "impacts32_sha": "884bb6dace3c4392d34457dc4c4f501a833fd1f05070b3c5e6ff2967067db609",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-16.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-17": {
  "stratum": "run-j-waypoints",
  "seed": 17,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 28.1524658203125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.404809951782227,
    -8.899374961853027,
    -0.22241075336933136,
    3.209895610809326,
    3.5242984294891357
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.12121295928955,
    -6.360589027404785,
    -0.047639150172472,
    2.9321494102478027,
    3.4946343898773193
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.592979431152344,
    -5.279703140258789,
    -0.022271055728197098,
    2.718670606613159,
    3.466557741165161
   ],
   "hydro-lnL-imos-margeta": [
    -4.581064224243164,
    -2.4417688846588135,
    -0.1578018069267273,
    2.6752610206604004,
    3.3020308017730713
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.815637111663818,
    -3.3307907581329346,
    -0.25455528497695923,
    1.5066075325012207,
    1.9008278846740723
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.892053125,
   "hydro-lnL-imos-eta2.1e-4": 0.892053125,
   "hydro-lnL-imos-eta1e-4": 0.892053125,
   "hydro-lnL-imos-margeta": 0.892053125,
   "hydro-lnL-ims-proxy-margeta": 0.92669484375
  },
  "scored_any_share": 0.92669484375,
  "seconds": 233.95223021507263,
  "impacts32_sha": "b4db59e9e43162d95532387508921fcd52e38bffd1baccf83177e4dfbd09d22c",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-17.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-18": {
  "stratum": "run-j-waypoints",
  "seed": 18,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 27.923583984375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.19066333770752,
    -8.70434856414795,
    -0.2501806616783142,
    3.157453775405884,
    3.5238449573516846
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.926229476928711,
    -6.256939888000488,
    -0.054012373089790344,
    2.848785877227783,
    3.4900565147399902
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.416715621948242,
    -5.220940113067627,
    -0.02528942935168743,
    2.614089250564575,
    3.457937002182007
   ],
   "hydro-lnL-imos-margeta": [
    -4.587832927703857,
    -2.4699432849884033,
    -0.17005285620689392,
    2.615438461303711,
    3.2840089797973633
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.964155197143555,
    -3.395564079284668,
    -0.27050840854644775,
    1.4876950979232788,
    1.9285744428634644
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90444671875,
   "hydro-lnL-imos-eta2.1e-4": 0.90444671875,
   "hydro-lnL-imos-eta1e-4": 0.90444671875,
   "hydro-lnL-imos-margeta": 0.90444671875,
   "hydro-lnL-ims-proxy-margeta": 0.936955
  },
  "scored_any_share": 0.936955,
  "seconds": 237.69545602798462,
  "impacts32_sha": "f99983bf2353b1c689495daf602d027d2792b8140443f33377b986c1e783ec75",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-18.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-19": {
  "stratum": "run-j-waypoints",
  "seed": 19,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 27.73284912109375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.675087928771973,
    -8.408778190612793,
    -0.24368739128112793,
    3.2409887313842773,
    3.5253217220306396
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.428359985351562,
    -6.0760393142700195,
    -0.05260155722498894,
    2.9917960166931152,
    3.4990134239196777
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.97286605834961,
    -5.074618816375732,
    -0.024655580520629883,
    2.793962001800537,
    3.4730522632598877
   ],
   "hydro-lnL-imos-margeta": [
    -4.473262310028076,
    -2.419734239578247,
    -0.16725869476795197,
    2.7194318771362305,
    3.314094066619873
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.8107781410217285,
    -3.3573458194732666,
    -0.2747056484222412,
    1.524360179901123,
    1.8715476989746094
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.91120078125,
   "hydro-lnL-imos-eta2.1e-4": 0.91120078125,
   "hydro-lnL-imos-eta1e-4": 0.91120078125,
   "hydro-lnL-imos-margeta": 0.91120078125,
   "hydro-lnL-ims-proxy-margeta": 0.94545265625
  },
  "scored_any_share": 0.94545265625,
  "seconds": 239.8704550266266,
  "impacts32_sha": "f669d2d7fafa80706c20ad9d6725ae9eae7ba3b3d842be33ae037a02c6a38299",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-19.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-2": {
  "stratum": "run-j-waypoints",
  "seed": 2,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 31.70013427734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.062833786010742,
    -8.690824508666992,
    -0.24574270844459534,
    3.1888961791992188,
    3.526973247528076
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.801555633544922,
    -6.232296943664551,
    -0.05341564118862152,
    2.904888391494751,
    3.496811866760254
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.300606727600098,
    -5.190866470336914,
    -0.02513926662504673,
    2.6902854442596436,
    3.4673991203308105
   ],
   "hydro-lnL-imos-margeta": [
    -4.5431952476501465,
    -2.4573466777801514,
    -0.16796429455280304,
    2.656975507736206,
    3.2988946437835693
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.882525444030762,
    -3.377535820007324,
    -0.265960693359375,
    1.5046929121017456,
    1.9013025760650635
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90464046875,
   "hydro-lnL-imos-eta2.1e-4": 0.90464046875,
   "hydro-lnL-imos-eta1e-4": 0.90464046875,
   "hydro-lnL-imos-margeta": 0.90464046875,
   "hydro-lnL-ims-proxy-margeta": 0.9424871875
  },
  "scored_any_share": 0.9424871875,
  "seconds": 275.23215198516846,
  "impacts32_sha": "0dd049a9ad254ba94c9d7271d92b8a5cb378bacd1c30cd3491ac8e3479a02851",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-2.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-20": {
  "stratum": "run-j-waypoints",
  "seed": 20,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 27.58026123046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.635625839233398,
    -8.440953254699707,
    -0.2340744435787201,
    3.2980496883392334,
    3.532571315765381
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.384024620056152,
    -6.087094783782959,
    -0.05037698522210121,
    3.09312105178833,
    3.5106117725372314
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.920660018920898,
    -5.0840630531311035,
    -0.023607507348060608,
    2.9286389350891113,
    3.4897823333740234
   ],
   "hydro-lnL-imos-margeta": [
    -4.471691608428955,
    -2.437725067138672,
    -0.16299664974212646,
    2.8051977157592773,
    3.3509347438812256
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.811951637268066,
    -3.3737332820892334,
    -0.2614443302154541,
    1.5231122970581055,
    1.8900456428527832
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90530515625,
   "hydro-lnL-imos-eta2.1e-4": 0.90530515625,
   "hydro-lnL-imos-eta1e-4": 0.90530515625,
   "hydro-lnL-imos-margeta": 0.90530515625,
   "hydro-lnL-ims-proxy-margeta": 0.93902390625
  },
  "scored_any_share": 0.93902390625,
  "seconds": 241.59472107887268,
  "impacts32_sha": "3727165c7670a61ef281a1e72d58f1a8d81730506ba83ed56f4a75fd34b6dfbe",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-20.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-21": {
  "stratum": "run-j-waypoints",
  "seed": 21,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 16.17431640625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.694559097290039,
    -8.418290138244629,
    -0.26456743478775024,
    3.1826283931732178,
    3.5207479000091553
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.4353666305542,
    -6.102089881896973,
    -0.057797715067863464,
    2.8964717388153076,
    3.4886317253112793
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.958982467651367,
    -5.112427234649658,
    -0.027168653905391693,
    2.6750969886779785,
    3.4571211338043213
   ],
   "hydro-lnL-imos-margeta": [
    -4.512389183044434,
    -2.4895565509796143,
    -0.1759541928768158,
    2.6462626457214355,
    3.288231372833252
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.085488796234131,
    -3.4965980052948,
    -0.28061771392822266,
    1.4880263805389404,
    1.8717032670974731
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.91279375,
   "hydro-lnL-imos-eta2.1e-4": 0.91279375,
   "hydro-lnL-imos-eta1e-4": 0.91279375,
   "hydro-lnL-imos-margeta": 0.91279375,
   "hydro-lnL-ims-proxy-margeta": 0.94439953125
  },
  "scored_any_share": 0.94439953125,
  "seconds": 424.70550179481506,
  "impacts32_sha": "dfbfa18e20c1503aa33f00054a8cd1ce2f79d1d8a6655c718ef88fcd7e66ba75",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-21.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-22": {
  "stratum": "run-j-waypoints",
  "seed": 22,
  "rows": 6399936,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 16.28875732421875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.556035995483398,
    -8.964364051818848,
    -0.23906078934669495,
    3.209273338317871,
    3.5243453979492188
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.275894165039062,
    -6.4255452156066895,
    -0.05155476555228233,
    2.9387335777282715,
    3.4941418170928955
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.753705978393555,
    -5.3504838943481445,
    -0.024159153923392296,
    2.73248028755188,
    3.465822696685791
   ],
   "hydro-lnL-imos-margeta": [
    -4.666045188903809,
    -2.4995968341827393,
    -0.16513393819332123,
    2.6808648109436035,
    3.3015613555908203
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.005053997039795,
    -3.442913293838501,
    -0.2662818133831024,
    1.4862452745437622,
    1.8792389631271362
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8998818113181132,
   "hydro-lnL-imos-eta2.1e-4": 0.8998818113181132,
   "hydro-lnL-imos-eta1e-4": 0.8998818113181132,
   "hydro-lnL-imos-margeta": 0.8998818113181132,
   "hydro-lnL-ims-proxy-margeta": 0.9329640171401714
  },
  "scored_any_share": 0.9329640171401714,
  "seconds": 421.0369532108307,
  "impacts32_sha": "027fd354c2de65d2c06140e66ed4d2ac443229339a85f96628e7f5613b57a056",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-22.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-23": {
  "stratum": "run-j-waypoints",
  "seed": 23,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 16.05987548828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -15.080982208251953,
    -9.309086799621582,
    -0.2679557204246521,
    3.1589043140411377,
    3.525736093521118
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.805127143859863,
    -6.673870086669922,
    -0.05837765336036682,
    2.8503761291503906,
    3.493034601211548
   ],
   "hydro-lnL-imos-eta1e-4": [
    -10.264534950256348,
    -5.559580326080322,
    -0.0274288859218359,
    2.6169016361236572,
    3.4614593982696533
   ],
   "hydro-lnL-imos-margeta": [
    -4.850032806396484,
    -2.5837018489837646,
    -0.17750060558319092,
    2.615715742111206,
    3.290025472640991
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.231828689575195,
    -3.5126049518585205,
    -0.27931106090545654,
    1.4913902282714844,
    1.9443150758743286
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9132715625,
   "hydro-lnL-imos-eta2.1e-4": 0.9132715625,
   "hydro-lnL-imos-eta1e-4": 0.9132715625,
   "hydro-lnL-imos-margeta": 0.9132715625,
   "hydro-lnL-ims-proxy-margeta": 0.94656875
  },
  "scored_any_share": 0.94656875,
  "seconds": 425.18323802948,
  "impacts32_sha": "be607c3359d3db14526bd0e45135eae483869400d43544dd04eb594fd89f0afb",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-23.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-24": {
  "stratum": "run-j-waypoints",
  "seed": 24,
  "rows": 6399936,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 17.43316650390625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.832845687866211,
    -8.51950454711914,
    -0.2417629063129425,
    3.1535468101501465,
    3.5242981910705566
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.567903518676758,
    -6.142046928405762,
    -0.05214281380176544,
    2.839054584503174,
    3.4897446632385254
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.087335586547852,
    -5.127650260925293,
    -0.02443549409508705,
    2.597597599029541,
    3.4558637142181396
   ],
   "hydro-lnL-imos-margeta": [
    -4.504106521606445,
    -2.437703847885132,
    -0.16636332869529724,
    2.6061642169952393,
    3.2806570529937744
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.79410982131958,
    -3.3310940265655518,
    -0.2669807970523834,
    1.4843029975891113,
    1.8704758882522583
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8981149186491865,
   "hydro-lnL-imos-eta2.1e-4": 0.8981149186491865,
   "hydro-lnL-imos-eta1e-4": 0.8981149186491865,
   "hydro-lnL-imos-margeta": 0.8981149186491865,
   "hydro-lnL-ims-proxy-margeta": 0.9360223289732897
  },
  "scored_any_share": 0.9360223289732897,
  "seconds": 408.43249702453613,
  "impacts32_sha": "c2e5eb169c378636a31545115be3bdbac3aa43f45d41ef32d28a121bf6752454",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-24.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-3": {
  "stratum": "run-j-waypoints",
  "seed": 3,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 31.585693359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.378318786621094,
    -8.845390319824219,
    -0.26072490215301514,
    3.1640853881835938,
    3.521543502807617
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.10312271118164,
    -6.342032432556152,
    -0.05683218687772751,
    2.872218132019043,
    3.489776611328125
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.580859184265137,
    -5.283663272857666,
    -0.026728373020887375,
    2.646003246307373,
    3.4599478244781494
   ],
   "hydro-lnL-imos-margeta": [
    -4.625203609466553,
    -2.5046370029449463,
    -0.17458435893058777,
    2.6304352283477783,
    3.2904696464538574
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.120207786560059,
    -3.507553815841675,
    -0.2719210982322693,
    1.4667012691497803,
    1.862996220588684
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89997890625,
   "hydro-lnL-imos-eta2.1e-4": 0.89997890625,
   "hydro-lnL-imos-eta1e-4": 0.89997890625,
   "hydro-lnL-imos-margeta": 0.89997890625,
   "hydro-lnL-ims-proxy-margeta": 0.9300115625
  },
  "scored_any_share": 0.9300115625,
  "seconds": 278.8161852359772,
  "impacts32_sha": "7568c0f2b3440e459cb99dba39daa2db63e06627d64f070105d4a5f41136d69b",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-3.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-4": {
  "stratum": "run-j-waypoints",
  "seed": 4,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 31.43310546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.677901268005371,
    -8.584281921386719,
    -0.2529756426811218,
    3.2143547534942627,
    3.526071548461914
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.448850631713867,
    -6.217646598815918,
    -0.055001385509967804,
    2.942270517349243,
    3.496687889099121
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.9815034866333,
    -5.201484680175781,
    -0.02586689591407776,
    2.73219633102417,
    3.4681849479675293
   ],
   "hydro-lnL-imos-margeta": [
    -4.548793792724609,
    -2.4837191104888916,
    -0.17123237252235413,
    2.6827640533447266,
    3.301255702972412
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.851576328277588,
    -3.396233558654785,
    -0.26786667108535767,
    1.5039258003234863,
    1.8819224834442139
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.913118125,
   "hydro-lnL-imos-eta2.1e-4": 0.913118125,
   "hydro-lnL-imos-eta1e-4": 0.913118125,
   "hydro-lnL-imos-margeta": 0.913118125,
   "hydro-lnL-ims-proxy-margeta": 0.94487390625
  },
  "scored_any_share": 0.94487390625,
  "seconds": 281.5817711353302,
  "impacts32_sha": "78b14d0851bb31f12eeff578ba1af68d6f533003d8391434483ff9cb08b39061",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-4.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-5": {
  "stratum": "run-j-waypoints",
  "seed": 5,
  "rows": 6400064,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.6783447265625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.661097526550293,
    -8.480441093444824,
    -0.24973136186599731,
    3.178647518157959,
    3.5264103412628174
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.398158073425293,
    -6.111323356628418,
    -0.05428683012723923,
    2.8887810707092285,
    3.4943017959594727
   ],
   "hydro-lnL-imos-eta1e-4": [
    -8.915109634399414,
    -5.10576868057251,
    -0.025507483631372452,
    2.6673924922943115,
    3.4636943340301514
   ],
   "hydro-lnL-imos-margeta": [
    -4.475625038146973,
    -2.4475245475769043,
    -0.16968291997909546,
    2.644394636154175,
    3.2974624633789062
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.904119968414307,
    -3.3848838806152344,
    -0.2676336169242859,
    1.492327094078064,
    1.912775993347168
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9026315986840132,
   "hydro-lnL-imos-eta2.1e-4": 0.9026315986840132,
   "hydro-lnL-imos-eta1e-4": 0.9026315986840132,
   "hydro-lnL-imos-margeta": 0.9026315986840132,
   "hydro-lnL-ims-proxy-margeta": 0.9370059424405756
  },
  "scored_any_share": 0.9370059424405756,
  "seconds": 238.442538022995,
  "impacts32_sha": "87e787d99c2d12538c3786999fcdaf4838cc4f1a1c70cd90e901bd1e283b2896",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-5.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-6": {
  "stratum": "run-j-waypoints",
  "seed": 6,
  "rows": 6399936,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.5257568359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.424070358276367,
    -8.856986045837402,
    -0.2593122124671936,
    3.141838788986206,
    3.522155284881592
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -11.145220756530762,
    -6.36379337310791,
    -0.05634806305170059,
    2.829577684402466,
    3.488071918487549
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.622526168823242,
    -5.313797473907471,
    -0.026477273553609848,
    2.592890739440918,
    3.455714702606201
   ],
   "hydro-lnL-imos-margeta": [
    -4.647118091583252,
    -2.5259392261505127,
    -0.17390987277030945,
    2.599802255630493,
    3.2815237045288086
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.11847448348999,
    -3.484570026397705,
    -0.27325236797332764,
    1.464255928993225,
    1.8414400815963745
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8994041502915029,
   "hydro-lnL-imos-eta2.1e-4": 0.8994041502915029,
   "hydro-lnL-imos-eta1e-4": 0.8994041502915029,
   "hydro-lnL-imos-margeta": 0.8994041502915029,
   "hydro-lnL-ims-proxy-margeta": 0.9323190106901069
  },
  "scored_any_share": 0.9323190106901069,
  "seconds": 237.08286595344543,
  "impacts32_sha": "f161d8f047dc001dd27f4e412feb2eb5c844b586acd7cb8b118284f089b95535",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-6.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-7": {
  "stratum": "run-j-waypoints",
  "seed": 7,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.41131591796875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.130460739135742,
    -8.742599487304688,
    -0.2238577902317047,
    3.271022081375122,
    3.527677536010742
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.853599548339844,
    -6.2211833000183105,
    -0.048332035541534424,
    3.0447776317596436,
    3.5037779808044434
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.329682350158691,
    -5.161488056182861,
    -0.02271113358438015,
    2.8659627437591553,
    3.4808788299560547
   ],
   "hydro-lnL-imos-margeta": [
    -4.506479263305664,
    -2.4191534519195557,
    -0.15815746784210205,
    2.7637014389038086,
    3.3310303688049316
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.811515808105469,
    -3.3479437828063965,
    -0.25211119651794434,
    1.5504004955291748,
    2.0123579502105713
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89208890625,
   "hydro-lnL-imos-eta2.1e-4": 0.89208890625,
   "hydro-lnL-imos-eta1e-4": 0.89208890625,
   "hydro-lnL-imos-margeta": 0.89208890625,
   "hydro-lnL-ims-proxy-margeta": 0.92475296875
  },
  "scored_any_share": 0.92475296875,
  "seconds": 235.82342910766602,
  "impacts32_sha": "88a9da27170057285e393fc9d5b76673fb5f428eec08be14bfe82e9c2c1bbcd0",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-7.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-8": {
  "stratum": "run-j-waypoints",
  "seed": 8,
  "rows": 6400064,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.25872802734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -14.085227966308594,
    -8.677061080932617,
    -0.2637823820114136,
    3.1488394737243652,
    3.5208346843719482
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.818817138671875,
    -6.2468767166137695,
    -0.057312026619911194,
    2.842930316925049,
    3.4866840839385986
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.32059383392334,
    -5.219614505767822,
    -0.02687540277838707,
    2.6110501289367676,
    3.4542460441589355
   ],
   "hydro-lnL-imos-margeta": [
    -4.589235782623291,
    -2.495253086090088,
    -0.17598682641983032,
    2.6091501712799072,
    3.2789199352264404
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -7.097932815551758,
    -3.496971845626831,
    -0.27864766120910645,
    1.4814674854278564,
    1.9626609086990356
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9105027699723003,
   "hydro-lnL-imos-eta2.1e-4": 0.9105027699723003,
   "hydro-lnL-imos-eta1e-4": 0.9105027699723003,
   "hydro-lnL-imos-margeta": 0.9105027699723003,
   "hydro-lnL-ims-proxy-margeta": 0.9414171483285168
  },
  "scored_any_share": 0.9414171483285168,
  "seconds": 237.1732861995697,
  "impacts32_sha": "dabb5d2456ac0ebf9c81e78c035bb152afbf1a3a80e2d3f2be50eae88927d5e3",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-8.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 },
 "run-j-waypoints/seed-9": {
  "stratum": "run-j-waypoints",
  "seed": 9,
  "rows": 6400000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta1e-3",
   "hydro-lnL-imos-eta2.1e-4",
   "hydro-lnL-imos-eta1e-4",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-ims-proxy-margeta"
  ],
  "free_gib_at_write": 29.33502197265625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -13.868407249450684,
    -8.491626739501953,
    -0.23941883444786072,
    3.216539144515991,
    3.5239906311035156
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -10.607440948486328,
    -6.127265453338623,
    -0.051412004977464676,
    2.9508254528045654,
    3.4946420192718506
   ],
   "hydro-lnL-imos-eta1e-4": [
    -9.129405975341797,
    -5.116674423217773,
    -0.0240434892475605,
    2.7441444396972656,
    3.4671719074249268
   ],
   "hydro-lnL-imos-margeta": [
    -4.53521203994751,
    -2.4471781253814697,
    -0.16543713212013245,
    2.688093900680542,
    3.3027920722961426
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -6.9825215339660645,
    -3.4258081912994385,
    -0.26933756470680237,
    1.5009104013442993,
    1.9036303758621216
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90695515625,
   "hydro-lnL-imos-eta2.1e-4": 0.90695515625,
   "hydro-lnL-imos-eta1e-4": 0.90695515625,
   "hydro-lnL-imos-margeta": 0.90695515625,
   "hydro-lnL-ims-proxy-margeta": 0.93859421875
  },
  "scored_any_share": 0.93859421875,
  "seconds": 235.62043738365173,
  "impacts32_sha": "89e3eb6c27872f521a6e609ff1f2bcbf96ab455c313eae4e949426f43eddb329",
  "run_json": {
   "code_revision": "16f2eb1",
   "config_paths": [
    "config/davey2016-inmarsat.toml",
    "config/sensitivity/no-exhaustion-prior.toml",
    "config/sensitivity/fuel-fixes/s1-factor.toml",
    "config/sensitivity/fuel-fixes/s2-temperature.toml",
    "config/sensitivity/fuel-fixes/s3-internal.toml",
    "config/sensitivity/fuel-fixes/s4-ceiling.toml",
    "config/sensitivity/fuel-fixes/s5-hard-reject.toml",
    "config/sensitivity/fuel-fixes/s6-tanks.toml",
    "config/sensitivity/reference-snapshots.toml",
    "config/sensitivity/early-families/radar-full.toml",
    "config/sensitivity/fuel-fixes/s7-single-engine.toml",
    "config/sensitivity/fuel-fixes/s8-hold-taper.toml",
    "config/sensitivity/fuel-fixes/inop-flow-fix.toml",
    "config/sensitivity/early-families/speed-envelope-throughout.toml",
    "config/sensitivity/handoff-lookahead-d.toml",
    "config/sensitivity/run-j/obs-bfo432.toml",
    "config/sensitivity/run-j/kx.toml",
    "config/sensitivity/early-families/route-sampler.toml",
    "config/sensitivity/run-j/size-sampler.toml",
    "hypotheses/end-of-flight/smoke/snapshot-m0011.toml",
    "hypotheses/end-of-flight/smoke/terminal.toml",
    "hypotheses/end-of-flight/full/reference-289.toml",
    "hypotheses/end-of-flight/full/descent-idle-floor.toml",
    "hypotheses/end-of-flight/full/seed-9.toml",
    "hypotheses/end-of-flight/smoke/v2-broad.toml",
    "hypotheses/end-of-flight/full/family-b-ditching.toml",
    "hypotheses/end-of-flight/full/residual-bank-boeing.toml",
    "hypotheses/end-of-flight/smoke/trim-at-loss.toml",
    "hypotheses/end-of-flight/full/pushover.toml",
    "hypotheses/end-of-flight/full/boeing-sequence.toml",
    "hypotheses/end-of-flight/full/b-late-onset-proposal.toml",
    "hypotheses/end-of-flight/full/holland-estimable.toml",
    "hypotheses/end-of-flight/full/a1-aimed-pitchdown.toml",
    "hypotheses/end-of-flight/full/piloted-turns.toml",
    "hypotheses/end-of-flight/full/run-i.toml",
    "hypotheses/end-of-flight/smoke/within-parent-unnormalised.toml",
    "hypotheses/end-of-flight/full/c2-silent-aim.toml",
    "hypotheses/end-of-flight/full/dive-branch.toml",
    "hypotheses/end-of-flight/smoke/children-16.toml",
    "hypotheses/end-of-flight/full/round3-laws.toml",
    "hypotheses/end-of-flight/full/bank-cap-uniform.toml"
   ]
  },
  "logon": {
   "lag_scale_s": 14.875,
   "lag_shape": 8.0,
   "logon_unix_s": 1394237969.416,
   "prior_fuel_exhaustion": 0.5
  }
 }
}
