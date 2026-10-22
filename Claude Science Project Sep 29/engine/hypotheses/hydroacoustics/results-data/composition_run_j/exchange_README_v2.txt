Hydroacoustics block 11 (composition) on end of flight run J, all four strata (74 seeds). Written 2026-10-22T12:34:15Z.
PRODUCT v2 (amendment A4, prereg e13a32e): IMOS TL from the RAM-along-grid drop-in imos_tl_ram_arc.csv (G-TL1 closed on the offset-0 line); supersedes run-j-gated (old IMOS table).
Pre-registration prepare/composition_run_j/prereg.py (module branch, commit 90d7181 + A4 e13a32e); worker.py / driver.py; 4 single-thread workers.
Rows 313,599,968; not_computed (NaN) 0; the marginalised IMOS column (proposed default) is present for every seed; per-seed checks (rows equal end of flight's, float32, NaN only where inputs non-finite and identical
across columns, finite elsewhere, quantiles in _parts/*.json): all pass. Seeds with fewer than five columns (another process held the disk below the 20 GiB floor during the run; the marginalised IMOS
column was written, the other four were not): 0 []
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
10 m source; IMOS RAM along the grid, imos_tl_ram_arc.csv; IMS raw KRAKEN minus imp500 RAM delta). tau = end of flight tau90 (method 1). E = contact
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
  "free_gib_at_write": 30.517578125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.259078979492188,
    -6.4996442794799805,
    -0.05276989936828613,
    2.6812710762023926,
    3.483673095703125
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.051886558532715,
    -4.138726234436035,
    -0.010856863111257553,
    2.0066335201263428,
    3.3737030029296875
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.63500452041626,
    -3.1704559326171875,
    -0.005094045307487249,
    1.5797415971755981,
    3.2726144790649414
   ],
   "hydro-lnL-imos-margeta": [
    -2.8498263359069824,
    -1.5188053846359253,
    -0.05378499627113342,
    2.1207761764526367,
    3.0570101737976074
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.120909690856934,
    -2.5619056224823,
    -0.15380394458770752,
    0.8893405199050903,
    2.0019376277923584
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.871755,
   "hydro-lnL-imos-eta2.1e-4": 0.8717365625,
   "hydro-lnL-imos-eta1e-4": 0.8717253125,
   "hydro-lnL-imos-margeta": 0.871756875,
   "hydro-lnL-ims-proxy-margeta": 0.91477125
  },
  "scored_any_share": 0.9148825,
  "seconds": 112.23101496696472,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -10.912601470947266,
    -6.316457748413086,
    -0.04686702415347099,
    2.735607385635376,
    3.481431484222412
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.757480621337891,
    -4.024302005767822,
    -0.009584366343915462,
    2.081507921218872,
    3.3735241889953613
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.402604579925537,
    -3.0707266330718994,
    -0.004484889097511768,
    1.656009316444397,
    3.2761785984039307
   ],
   "hydro-lnL-imos-margeta": [
    -2.773932456970215,
    -1.4721319675445557,
    -0.04884246736764908,
    2.168327569961548,
    3.0578339099884033
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.152746200561523,
    -2.5707991123199463,
    -0.1569681614637375,
    0.819353461265564,
    1.9553353786468506
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.87834965400346,
   "hydro-lnL-imos-eta2.1e-4": 0.8783396541034589,
   "hydro-lnL-imos-eta1e-4": 0.8783340291597084,
   "hydro-lnL-imos-margeta": 0.878349966500335,
   "hydro-lnL-ims-proxy-margeta": 0.9149421005789942
  },
  "scored_any_share": 0.9150164748352516,
  "seconds": 105.85262298583984,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -10.385029792785645,
    -5.8126220703125,
    -0.05172806233167648,
    2.470855712890625,
    3.4589931964874268
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.262632369995117,
    -3.655827522277832,
    -0.010601678863167763,
    1.7132107019424438,
    3.325632333755493
   ],
   "hydro-lnL-imos-eta1e-4": [
    -5.973755359649658,
    -2.766080141067505,
    -0.004970744252204895,
    1.269287109375,
    3.203251838684082
   ],
   "hydro-lnL-imos-margeta": [
    -2.6144473552703857,
    -1.3873308897018433,
    -0.05312512814998627,
    1.9573935270309448,
    2.9989657402038574
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.22947359085083,
    -2.622148036956787,
    -0.16612458229064941,
    0.8307324647903442,
    2.025637149810791
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8962878125,
   "hydro-lnL-imos-eta2.1e-4": 0.89628,
   "hydro-lnL-imos-eta1e-4": 0.8962765625,
   "hydro-lnL-imos-margeta": 0.8962859375,
   "hydro-lnL-ims-proxy-margeta": 0.9288228125
  },
  "scored_any_share": 0.928864375,
  "seconds": 113.40235495567322,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.71649169921875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.449539184570312,
    -6.058603286743164,
    -0.04818403720855713,
    2.837310552597046,
    3.4840354919433594
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.409473419189453,
    -3.8992841243743896,
    -0.00983787328004837,
    2.2492728233337402,
    3.388366937637329
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.122237682342529,
    -3.0002827644348145,
    -0.004605579189956188,
    1.850044846534729,
    3.2996304035186768
   ],
   "hydro-lnL-imos-margeta": [
    -2.753176212310791,
    -1.4651974439620972,
    -0.05003943294286728,
    2.2571492195129395,
    3.0822503566741943
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.3106689453125,
    -2.6663658618927,
    -0.16205626726150513,
    0.8220887184143066,
    1.9516711235046387
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.897968125,
   "hydro-lnL-imos-eta2.1e-4": 0.89796,
   "hydro-lnL-imos-eta1e-4": 0.8979565625,
   "hydro-lnL-imos-margeta": 0.8979703125,
   "hydro-lnL-ims-proxy-margeta": 0.9282
  },
  "scored_any_share": 0.9282415625,
  "seconds": 113.86487603187561,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.64019775390625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.300405502319336,
    -6.6161065101623535,
    -0.05574123188853264,
    2.721987009048462,
    3.488644599914551
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.105944633483887,
    -4.2522053718566895,
    -0.011495801620185375,
    2.0876986980438232,
    3.3821933269500732
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.705197334289551,
    -3.2737860679626465,
    -0.005393265746533871,
    1.6771503686904907,
    3.2824807167053223
   ],
   "hydro-lnL-imos-margeta": [
    -2.931602716445923,
    -1.534645915031433,
    -0.056108780205249786,
    2.161256790161133,
    3.0636250972747803
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.115913391113281,
    -2.5212888717651367,
    -0.15794283151626587,
    0.9707383513450623,
    2.0097992420196533
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.876681875,
   "hydro-lnL-imos-eta2.1e-4": 0.876660625,
   "hydro-lnL-imos-eta1e-4": 0.8766521875,
   "hydro-lnL-imos-margeta": 0.8766809375,
   "hydro-lnL-ims-proxy-margeta": 0.917383125
  },
  "scored_any_share": 0.9174371875,
  "seconds": 114.02997827529907,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -10.811105728149414,
    -6.220757484436035,
    -0.04582824558019638,
    3.0486903190612793,
    3.50774884223938
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.687612056732178,
    -3.9593615531921387,
    -0.009372450411319733,
    2.592345714569092,
    3.446058511734009
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.353092670440674,
    -3.031017303466797,
    -0.004393824376165867,
    2.255108118057251,
    3.385981798171997
   ],
   "hydro-lnL-imos-margeta": [
    -2.7878167629241943,
    -1.4672389030456543,
    -0.047880806028842926,
    2.4569623470306396,
    3.170788288116455
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.153311252593994,
    -2.593618392944336,
    -0.15653792023658752,
    0.937560498714447,
    1.9996366500854492
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8972038404615954,
   "hydro-lnL-imos-eta2.1e-4": 0.8971929030709693,
   "hydro-lnL-imos-eta1e-4": 0.8971875906240938,
   "hydro-lnL-imos-margeta": 0.8972050904490955,
   "hydro-lnL-ims-proxy-margeta": 0.9287522749772502
  },
  "scored_any_share": 0.9288060244397556,
  "seconds": 114.60008502006531,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -10.72749137878418,
    -6.196496486663818,
    -0.047978632152080536,
    2.7084712982177734,
    3.476410150527954
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.615678310394287,
    -3.936222553253174,
    -0.009819835424423218,
    2.0454840660095215,
    3.3691158294677734
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.258602619171143,
    -3.0110204219818115,
    -0.0045952945947647095,
    1.6137380599975586,
    3.268886089324951
   ],
   "hydro-lnL-imos-margeta": [
    -2.737699270248413,
    -1.4601720571517944,
    -0.0497693195939064,
    2.1438686847686768,
    3.0522336959838867
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.205355644226074,
    -2.6015987396240234,
    -0.15610234439373016,
    0.8338180184364319,
    1.9890998601913452
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.884475625,
   "hydro-lnL-imos-eta2.1e-4": 0.8844653125,
   "hydro-lnL-imos-eta1e-4": 0.88446,
   "hydro-lnL-imos-margeta": 0.8844740625,
   "hydro-lnL-ims-proxy-margeta": 0.9178953125
  },
  "scored_any_share": 0.91793875,
  "seconds": 106.00097608566284,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -10.603631019592285,
    -6.136406421661377,
    -0.0463218055665493,
    2.8296098709106445,
    3.482969045639038
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.509335041046143,
    -3.9062094688415527,
    -0.009475959464907646,
    2.233154773712158,
    3.3865556716918945
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.182104587554932,
    -2.98931884765625,
    -0.004440444987267256,
    1.8327662944793701,
    3.2946484088897705
   ],
   "hydro-lnL-imos-margeta": [
    -2.7255077362060547,
    -1.4522396326065063,
    -0.048296526074409485,
    2.247255325317383,
    3.0738589763641357
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.265325546264648,
    -2.6438381671905518,
    -0.16375982761383057,
    0.8584326505661011,
    1.9739739894866943
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8966134375,
   "hydro-lnL-imos-eta2.1e-4": 0.896605625,
   "hydro-lnL-imos-eta1e-4": 0.8966040625,
   "hydro-lnL-imos-margeta": 0.896613125,
   "hydro-lnL-ims-proxy-margeta": 0.9286134375
  },
  "scored_any_share": 0.928655,
  "seconds": 106.00085377693176,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.4412841796875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.605351448059082,
    -6.12473726272583,
    -0.05059407651424408,
    2.7365000247955322,
    3.4795103073120117
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.4856791496276855,
    -3.943631887435913,
    -0.010316401720046997,
    2.0699713230133057,
    3.3669955730438232
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.167673110961914,
    -3.034679651260376,
    -0.0048270695842802525,
    1.635504126548767,
    3.2635583877563477
   ],
   "hydro-lnL-imos-margeta": [
    -2.774714708328247,
    -1.4796371459960938,
    -0.05222277343273163,
    2.1664488315582275,
    3.0472795963287354
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.3048295974731445,
    -2.6653800010681152,
    -0.16491596400737762,
    0.8289309144020081,
    2.050771951675415
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8958529164708353,
   "hydro-lnL-imos-eta2.1e-4": 0.8958432290677093,
   "hydro-lnL-imos-eta1e-4": 0.8958416665833342,
   "hydro-lnL-imos-margeta": 0.8958532289677104,
   "hydro-lnL-ims-proxy-margeta": 0.9306606933930661
  },
  "scored_any_share": 0.930709130408696,
  "seconds": 112.76501798629761,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.364990234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.503257751464844,
    -5.863560199737549,
    -0.03391294181346893,
    2.3717195987701416,
    3.439915657043457
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.352626323699951,
    -3.628073215484619,
    -0.006852420512586832,
    1.5661545991897583,
    3.288712739944458
   ],
   "hydro-lnL-imos-eta1e-4": [
    -5.9881272315979,
    -2.7201836109161377,
    -0.0032004988752305508,
    1.1211094856262207,
    3.1503021717071533
   ],
   "hydro-lnL-imos-margeta": [
    -2.558159112930298,
    -1.362074851989746,
    -0.03716321289539337,
    1.8750776052474976,
    2.9592607021331787
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.218480110168457,
    -2.6060304641723633,
    -0.12679950892925262,
    0.6674351096153259,
    1.9677319526672363
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8417909375,
   "hydro-lnL-imos-eta2.1e-4": 0.8417890625,
   "hydro-lnL-imos-eta1e-4": 0.841786875,
   "hydro-lnL-imos-margeta": 0.8417909375,
   "hydro-lnL-ims-proxy-margeta": 0.8668225
  },
  "scored_any_share": 0.8668475,
  "seconds": 102.58096885681152,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.2886962890625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.410737037658691,
    -6.677393436431885,
    -0.049233537167310715,
    2.4041707515716553,
    3.4660613536834717
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.1705322265625,
    -4.214653968811035,
    -0.010074780322611332,
    1.6582822799682617,
    3.326878786087036
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.730165004730225,
    -3.211076021194458,
    -0.004721592180430889,
    1.2180559635162354,
    3.20092511177063
   ],
   "hydro-lnL-imos-margeta": [
    -2.854642868041992,
    -1.5181679725646973,
    -0.05073554441332817,
    1.9078600406646729,
    3.0014901161193848
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -4.7307538986206055,
    -2.32835054397583,
    -0.11264343559741974,
    0.7907602190971375,
    1.9995530843734741
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8186331863318633,
   "hydro-lnL-imos-eta2.1e-4": 0.8186191236912369,
   "hydro-lnL-imos-eta1e-4": 0.8186091235912359,
   "hydro-lnL-imos-margeta": 0.8186328738287383,
   "hydro-lnL-ims-proxy-margeta": 0.8531432189321894
  },
  "scored_any_share": 0.8532647826478265,
  "seconds": 100.82717514038086,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.21240234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.259225845336914,
    -6.537034511566162,
    -0.052238743752241135,
    2.7935879230499268,
    3.4832510948181152
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.066498756408691,
    -4.155642509460449,
    -0.010724732652306557,
    2.1790432929992676,
    3.3838329315185547
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.6399946212768555,
    -3.1784555912017822,
    -0.005028457380831242,
    1.764447808265686,
    3.292741298675537
   ],
   "hydro-lnL-imos-margeta": [
    -2.8343257904052734,
    -1.5041898488998413,
    -0.0534219890832901,
    2.216686725616455,
    3.073406934738159
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.20046329498291,
    -2.6018457412719727,
    -0.16900759935379028,
    0.8412703275680542,
    2.0097289085388184
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.898905,
   "hydro-lnL-imos-eta2.1e-4": 0.898883125,
   "hydro-lnL-imos-eta1e-4": 0.89887,
   "hydro-lnL-imos-margeta": 0.898903125,
   "hydro-lnL-ims-proxy-margeta": 0.9383990625
  },
  "scored_any_share": 0.9384928125,
  "seconds": 104.22897696495056,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -11.024714469909668,
    -6.33422327041626,
    -0.05360502004623413,
    2.6950578689575195,
    3.4789884090423584
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.839134216308594,
    -4.04998254776001,
    -0.01101558469235897,
    2.0228261947631836,
    3.368156671524048
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.447694301605225,
    -3.109307289123535,
    -0.0051698945462703705,
    1.594020128250122,
    3.2650065422058105
   ],
   "hydro-lnL-imos-margeta": [
    -2.822399854660034,
    -1.4984321594238281,
    -0.054467443376779556,
    2.133359432220459,
    3.051344633102417
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.264157295227051,
    -2.6295793056488037,
    -0.16806873679161072,
    0.8634668588638306,
    2.00691819190979
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.892703125,
   "hydro-lnL-imos-eta2.1e-4": 0.8926884375,
   "hydro-lnL-imos-eta1e-4": 0.8926803125,
   "hydro-lnL-imos-margeta": 0.8927028125,
   "hydro-lnL-ims-proxy-margeta": 0.934815
  },
  "scored_any_share": 0.93488125,
  "seconds": 104.46018671989441,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.059814453125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.866965293884277,
    -6.168630123138428,
    -0.044211529195308685,
    2.5720160007476807,
    3.466953992843628
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.705300807952881,
    -3.894670248031616,
    -0.009036261588335037,
    1.8522157669067383,
    3.3469038009643555
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.319567680358887,
    -2.963216543197632,
    -0.00422505009919405,
    1.4098018407821655,
    3.234497547149658
   ],
   "hydro-lnL-imos-margeta": [
    -2.733712911605835,
    -1.4446073770523071,
    -0.046515002846717834,
    2.034921169281006,
    3.0247230529785156
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.249636650085449,
    -2.5792293548583984,
    -0.14010967314243317,
    0.7660961151123047,
    1.9751205444335938
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8620696875,
   "hydro-lnL-imos-eta2.1e-4": 0.8620578125,
   "hydro-lnL-imos-eta1e-4": 0.862055,
   "hydro-lnL-imos-margeta": 0.862065625,
   "hydro-lnL-ims-proxy-margeta": 0.89493625
  },
  "scored_any_share": 0.89503625,
  "seconds": 103.925133228302,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.9835205078125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.884112358093262,
    -6.24977445602417,
    -0.03931671380996704,
    2.6010582447052,
    3.4626402854919434
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.701941967010498,
    -3.9308063983917236,
    -0.007999012246727943,
    1.8892639875411987,
    3.340876817703247
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.313478469848633,
    -2.9814260005950928,
    -0.0037438953295350075,
    1.4444130659103394,
    3.2236344814300537
   ],
   "hydro-lnL-imos-margeta": [
    -2.7014670372009277,
    -1.4412307739257812,
    -0.04205255210399628,
    2.0554213523864746,
    3.0147578716278076
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.1511383056640625,
    -2.544659376144409,
    -0.13514173030853271,
    0.7743300795555115,
    1.9337539672851562
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.844985625,
   "hydro-lnL-imos-eta2.1e-4": 0.844976875,
   "hydro-lnL-imos-eta1e-4": 0.8449725,
   "hydro-lnL-imos-margeta": 0.8449846875,
   "hydro-lnL-ims-proxy-margeta": 0.8782734375
  },
  "scored_any_share": 0.878326875,
  "seconds": 104.2152271270752,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -11.096443176269531,
    -6.447211265563965,
    -0.05182463303208351,
    2.758843421936035,
    3.490908145904541
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.9046630859375,
    -4.1114044189453125,
    -0.010610201396048069,
    2.1272594928741455,
    3.3897604942321777
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.524050235748291,
    -3.1534066200256348,
    -0.004964263178408146,
    1.7054845094680786,
    3.2968356609344482
   ],
   "hydro-lnL-imos-margeta": [
    -2.8447797298431396,
    -1.5066593885421753,
    -0.05305735021829605,
    2.1882410049438477,
    3.0796103477478027
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.059698581695557,
    -2.531101942062378,
    -0.15040123462677002,
    0.8675680756568909,
    2.0014235973358154
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.872243125,
   "hydro-lnL-imos-eta2.1e-4": 0.8722271875,
   "hydro-lnL-imos-eta1e-4": 0.87222125,
   "hydro-lnL-imos-margeta": 0.8722396875,
   "hydro-lnL-ims-proxy-margeta": 0.9108275
  },
  "scored_any_share": 0.910903125,
  "seconds": 106.17346501350403,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.77642822265625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.118810653686523,
    -6.45266580581665,
    -0.050724245607852936,
    2.6299474239349365,
    3.4819283485412598
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.925279140472412,
    -4.134662628173828,
    -0.010486731305718422,
    1.9368047714233398,
    3.3664121627807617
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.517833709716797,
    -3.181591749191284,
    -0.004927872680127621,
    1.4994031190872192,
    3.2565956115722656
   ],
   "hydro-lnL-imos-margeta": [
    -2.8666269779205322,
    -1.5255520343780518,
    -0.05177774652838707,
    2.0811727046966553,
    3.047705888748169
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.046515941619873,
    -2.5179433822631836,
    -0.15727132558822632,
    0.8452521562576294,
    1.9973238706588745
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.860910171601716,
   "hydro-lnL-imos-eta2.1e-4": 0.8607967329673297,
   "hydro-lnL-imos-eta1e-4": 0.8607364198641987,
   "hydro-lnL-imos-margeta": 0.8608811088110881,
   "hydro-lnL-ims-proxy-margeta": 0.9322458849588496
  },
  "scored_any_share": 0.9323683861838619,
  "seconds": 104.74494481086731,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-10": {
  "stratum": "run-j-free",
  "seed": 10,
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
  "free_gib_at_write": 31.1279296875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.073192596435547,
    -6.4162187576293945,
    -0.05381624773144722,
    2.7755720615386963,
    3.486180543899536
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.896116733551025,
    -4.107752323150635,
    -0.011053959839046001,
    2.1495847702026367,
    3.383985996246338
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.508882522583008,
    -3.150336265563965,
    -0.005179830361157656,
    1.7332656383514404,
    3.286306619644165
   ],
   "hydro-lnL-imos-margeta": [
    -2.826371192932129,
    -1.508569598197937,
    -0.054728567600250244,
    2.201742172241211,
    3.0708577632904053
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.143270015716553,
    -2.590036153793335,
    -0.1659860908985138,
    0.8725395798683167,
    2.028231143951416
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8883071875,
   "hydro-lnL-imos-eta2.1e-4": 0.8882865625,
   "hydro-lnL-imos-eta1e-4": 0.8882790625,
   "hydro-lnL-imos-margeta": 0.8883040625,
   "hydro-lnL-ims-proxy-margeta": 0.928859375
  },
  "scored_any_share": 0.9289315625,
  "seconds": 107.43678379058838,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-11": {
  "stratum": "run-j-free",
  "seed": 11,
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
  "free_gib_at_write": 31.0516357421875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.154085159301758,
    -6.483917713165283,
    -0.05207841098308563,
    2.703322649002075,
    3.4861319065093994
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.9597320556640625,
    -4.113717079162598,
    -0.010673506185412407,
    2.0451836585998535,
    3.37815260887146
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.558403015136719,
    -3.1443934440612793,
    -0.005003808066248894,
    1.6131939888000488,
    3.2789571285247803
   ],
   "hydro-lnL-imos-margeta": [
    -2.8243203163146973,
    -1.5001450777053833,
    -0.053281575441360474,
    2.141547203063965,
    3.0636916160583496
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.131869792938232,
    -2.569455862045288,
    -0.15396392345428467,
    0.8968311548233032,
    2.0164828300476074
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8771702907970921,
   "hydro-lnL-imos-eta2.1e-4": 0.8771565409345906,
   "hydro-lnL-imos-eta1e-4": 0.8771502909970901,
   "hydro-lnL-imos-margeta": 0.8771687283127169,
   "hydro-lnL-ims-proxy-margeta": 0.9141983580164198
  },
  "scored_any_share": 0.9142496075039249,
  "seconds": 107.37228894233704,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-12": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 31.01348876953125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.777070999145508,
    -6.2538042068481445,
    -0.04668241739273071,
    2.68872332572937,
    3.473526954650879
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.629299163818359,
    -3.9175970554351807,
    -0.00958854891359806,
    2.022753953933716,
    3.361783266067505
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.256581783294678,
    -2.9640636444091797,
    -0.004506418481469154,
    1.5930904150009155,
    3.255138397216797
   ],
   "hydro-lnL-imos-margeta": [
    -2.6984729766845703,
    -1.4358100891113281,
    -0.04847606644034386,
    2.128119468688965,
    3.0423858165740967
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.4157795906066895,
    -2.70827317237854,
    -0.16219548881053925,
    0.9126944541931152,
    1.9708997011184692
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.890026875,
   "hydro-lnL-imos-eta2.1e-4": 0.890019375,
   "hydro-lnL-imos-eta1e-4": 0.8900153125,
   "hydro-lnL-imos-margeta": 0.890025625,
   "hydro-lnL-ims-proxy-margeta": 0.9215965625
  },
  "scored_any_share": 0.921633125,
  "seconds": 107.79330682754517,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-13": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 30.93719482421875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.820235252380371,
    -6.2749924659729,
    -0.052337005734443665,
    2.8278191089630127,
    3.488023281097412
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.70860481262207,
    -4.029116630554199,
    -0.010672483593225479,
    2.2235493659973145,
    3.3920538425445557
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.3496809005737305,
    -3.0968852043151855,
    -0.004988707602024078,
    1.8171396255493164,
    3.298737049102783
   ],
   "hydro-lnL-imos-margeta": [
    -2.815558433532715,
    -1.4912701845169067,
    -0.05358268693089485,
    2.2459092140197754,
    3.080002546310425
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.1097002029418945,
    -2.559574842453003,
    -0.16670268774032593,
    0.8535972237586975,
    1.9769573211669922
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.893500625,
   "hydro-lnL-imos-eta2.1e-4": 0.8934875,
   "hydro-lnL-imos-eta1e-4": 0.893481875,
   "hydro-lnL-imos-margeta": 0.89349875,
   "hydro-lnL-ims-proxy-margeta": 0.9313634375
  },
  "scored_any_share": 0.9314296875,
  "seconds": 103.67479395866394,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-14": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 30.86090087890625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.930008888244629,
    -6.333988189697266,
    -0.04128297418355942,
    2.622645616531372,
    3.4771218299865723
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.746306419372559,
    -4.012035369873047,
    -0.008387530222535133,
    1.928817868232727,
    3.363848924636841
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.371284484863281,
    -3.0598459243774414,
    -0.003917127847671509,
    1.49696946144104,
    3.2574446201324463
   ],
   "hydro-lnL-imos-margeta": [
    -2.7717270851135254,
    -1.4727286100387573,
    -0.043908193707466125,
    2.075777769088745,
    3.0446317195892334
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -4.947704315185547,
    -2.4650943279266357,
    -0.12571990489959717,
    0.8093568086624146,
    1.9730702638626099
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8357872671273288,
   "hydro-lnL-imos-eta2.1e-4": 0.8357728922710773,
   "hydro-lnL-imos-eta1e-4": 0.8357678923210768,
   "hydro-lnL-imos-margeta": 0.8357844546554535,
   "hydro-lnL-ims-proxy-margeta": 0.8696141163588365
  },
  "scored_any_share": 0.8697213027869721,
  "seconds": 101.03441214561462,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-15": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 30.78460693359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.345619201660156,
    -5.842368125915527,
    -0.03551706671714783,
    2.6717193126678467,
    3.472099781036377
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.254249572753906,
    -3.6432950496673584,
    -0.007117174565792084,
    1.9777992963790894,
    3.353339672088623
   ],
   "hydro-lnL-imos-eta1e-4": [
    -5.931607246398926,
    -2.739928722381592,
    -0.0033075744286179543,
    1.5384972095489502,
    3.240290880203247
   ],
   "hydro-lnL-imos-margeta": [
    -2.5999910831451416,
    -1.373343586921692,
    -0.038938622921705246,
    2.111701250076294,
    3.0296547412872314
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.448187351226807,
    -2.7508678436279297,
    -0.1506149172782898,
    0.8682523369789124,
    2.2137041091918945
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8683791287087129,
   "hydro-lnL-imos-eta2.1e-4": 0.8683675663243368,
   "hydro-lnL-imos-eta1e-4": 0.8683628788712113,
   "hydro-lnL-imos-margeta": 0.8683763162368376,
   "hydro-lnL-ims-proxy-margeta": 0.9079996700033
  },
  "scored_any_share": 0.9080477945220548,
  "seconds": 102.688805103302,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-16": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 30.70831298828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.92357349395752,
    -6.318094730377197,
    -0.04428611695766449,
    2.555051565170288,
    3.4683327674865723
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.7596354484558105,
    -3.9848451614379883,
    -0.009057736024260521,
    1.8102020025253296,
    3.3432607650756836
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.373285293579102,
    -3.034346580505371,
    -0.004240790847688913,
    1.3610568046569824,
    3.2283599376678467
   ],
   "hydro-lnL-imos-margeta": [
    -2.7524235248565674,
    -1.4629361629486084,
    -0.04640721529722214,
    2.019812822341919,
    3.019366502761841
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.172857284545898,
    -2.5832674503326416,
    -0.1509781777858734,
    0.8055095076560974,
    2.0614354610443115
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8500635006350064,
   "hydro-lnL-imos-eta2.1e-4": 0.8499956874568746,
   "hydro-lnL-imos-eta1e-4": 0.8499650621506215,
   "hydro-lnL-imos-margeta": 0.8500510005100052,
   "hydro-lnL-ims-proxy-margeta": 0.9059843723437234
  },
  "scored_any_share": 0.9061190611906119,
  "seconds": 102.69010090827942,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-17": {
  "stratum": "run-j-free",
  "seed": 17,
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
  "free_gib_at_write": 30.63201904296875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.175483703613281,
    -6.487265110015869,
    -0.05110982805490494,
    2.837433338165283,
    3.4904491901397705
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.990869998931885,
    -4.144721984863281,
    -0.01051389891654253,
    2.2365808486938477,
    3.3898937702178955
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.609898567199707,
    -3.1794304847717285,
    -0.0049368105828762054,
    1.8323529958724976,
    3.2935025691986084
   ],
   "hydro-lnL-imos-margeta": [
    -2.8667328357696533,
    -1.5173088312149048,
    -0.052204713225364685,
    2.253519296646118,
    3.0757133960723877
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.045135974884033,
    -2.5278332233428955,
    -0.1593092530965805,
    0.8641934990882874,
    1.9720172882080078
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.882873125,
   "hydro-lnL-imos-eta2.1e-4": 0.8828371875,
   "hydro-lnL-imos-eta1e-4": 0.882815,
   "hydro-lnL-imos-margeta": 0.8828653125,
   "hydro-lnL-ims-proxy-margeta": 0.9282934375
  },
  "scored_any_share": 0.928365,
  "seconds": 111.32568192481995,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 30.55572509765625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.204238891601562,
    -6.490174770355225,
    -0.05273343622684479,
    2.7230618000030518,
    3.4964330196380615
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.989358425140381,
    -4.157129287719727,
    -0.010843014344573021,
    2.0847761631011963,
    3.3975675106048584
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.5888566970825195,
    -3.2039103507995605,
    -0.005085811950266361,
    1.6697407960891724,
    3.302326202392578
   ],
   "hydro-lnL-imos-margeta": [
    -2.875906229019165,
    -1.5357286930084229,
    -0.053688906133174896,
    2.159965753555298,
    3.0843663215637207
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.044507026672363,
    -2.5212669372558594,
    -0.15218493342399597,
    0.886224627494812,
    1.9957342147827148
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8642922945770543,
   "hydro-lnL-imos-eta2.1e-4": 0.8642760447395526,
   "hydro-lnL-imos-eta1e-4": 0.8642666698333017,
   "hydro-lnL-imos-margeta": 0.864289794602054,
   "hydro-lnL-ims-proxy-margeta": 0.9212011004889951
  },
  "scored_any_share": 0.9212976620233798,
  "seconds": 110.45376372337341,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-2": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 31.73828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.938590049743652,
    -6.322725296020508,
    -0.053455986082553864,
    2.800170660018921,
    3.4860148429870605
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.791746139526367,
    -4.036157131195068,
    -0.011013297364115715,
    2.183290481567383,
    3.3866758346557617
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.425132751464844,
    -3.096639394760132,
    -0.005174707621335983,
    1.7746902704238892,
    3.2932381629943848
   ],
   "hydro-lnL-imos-margeta": [
    -2.7959208488464355,
    -1.4937338829040527,
    -0.05427411198616028,
    2.22438645362854,
    3.0746638774871826
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.139652729034424,
    -2.597233772277832,
    -0.17289790511131287,
    0.8755825161933899,
    1.9883559942245483
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.896189788102119,
   "hydro-lnL-imos-eta2.1e-4": 0.8961660383396166,
   "hydro-lnL-imos-eta1e-4": 0.8961591634083659,
   "hydro-lnL-imos-margeta": 0.8961866631333687,
   "hydro-lnL-ims-proxy-margeta": 0.9400112248877511
  },
  "scored_any_share": 0.9400880991190088,
  "seconds": 105.21394920349121,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 },
 "run-j-free/seed-3": {
  "stratum": "run-j-free",
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
  "free_gib_at_write": 31.6619873046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.749921798706055,
    -6.326813697814941,
    -0.05448572710156441,
    2.8844053745269775,
    3.488553524017334
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.632733345031738,
    -4.102141380310059,
    -0.011240911670029163,
    2.353393077850342,
    3.3963711261749268
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.311395645141602,
    -3.168431043624878,
    -0.00528098177164793,
    2.0055174827575684,
    3.3089380264282227
   ],
   "hydro-lnL-imos-margeta": [
    -2.8486948013305664,
    -1.5199865102767944,
    -0.05503028631210327,
    2.3031556606292725,
    3.089116096496582
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.146881103515625,
    -2.5937764644622803,
    -0.17153649032115936,
    0.8807953596115112,
    1.9795631170272827
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9066109375,
   "hydro-lnL-imos-eta2.1e-4": 0.9065925,
   "hydro-lnL-imos-eta1e-4": 0.9065859375,
   "hydro-lnL-imos-margeta": 0.9066075,
   "hydro-lnL-ims-proxy-margeta": 0.9438646875
  },
  "scored_any_share": 0.943935,
  "seconds": 106.47161078453064,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.585693359375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.167952537536621,
    -6.518051624298096,
    -0.05933307111263275,
    2.7564568519592285,
    3.4927289485931396
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.971549034118652,
    -4.181980609893799,
    -0.012218751013278961,
    2.128464698791504,
    3.38835072517395
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.5531392097473145,
    -3.226984977722168,
    -0.005734553560614586,
    1.7147406339645386,
    3.293910264968872
   ],
   "hydro-lnL-imos-margeta": [
    -2.8610007762908936,
    -1.5378530025482178,
    -0.05920263007283211,
    2.187568187713623,
    3.0768544673919678
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.109630584716797,
    -2.5582566261291504,
    -0.16385102272033691,
    0.8764514327049255,
    2.0214104652404785
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.888439375,
   "hydro-lnL-imos-eta2.1e-4": 0.8884246875,
   "hydro-lnL-imos-eta1e-4": 0.888415,
   "hydro-lnL-imos-margeta": 0.88843875,
   "hydro-lnL-ims-proxy-margeta": 0.9289684375
  },
  "scored_any_share": 0.9290409375,
  "seconds": 106.07279109954834,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.47125244140625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.086480140686035,
    -6.438421249389648,
    -0.05850456655025482,
    2.7615718841552734,
    3.4918808937072754
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.898852348327637,
    -4.134150505065918,
    -0.012085538357496262,
    2.122969150543213,
    3.3919074535369873
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.500589370727539,
    -3.1913976669311523,
    -0.005672126077115536,
    1.7004368305206299,
    3.296999931335449
   ],
   "hydro-lnL-imos-margeta": [
    -2.8589327335357666,
    -1.5304831266403198,
    -0.05839570611715317,
    2.190237045288086,
    3.078490734100342
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.155604839324951,
    -2.5787546634674072,
    -0.1673402190208435,
    0.8815711736679077,
    2.008498430252075
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.888475625,
   "hydro-lnL-imos-eta2.1e-4": 0.888453125,
   "hydro-lnL-imos-eta1e-4": 0.8884440625,
   "hydro-lnL-imos-margeta": 0.8884721875,
   "hydro-lnL-ims-proxy-margeta": 0.93380875
  },
  "scored_any_share": 0.933895,
  "seconds": 112.95403003692627,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.43310546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.903264999389648,
    -6.24387264251709,
    -0.05418628454208374,
    2.690603017807007,
    3.471273183822632
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.737157821655273,
    -3.969740152359009,
    -0.011277368292212486,
    2.011183261871338,
    3.361593246459961
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.347481727600098,
    -3.0398309230804443,
    -0.005328378640115261,
    1.5744045972824097,
    3.254941940307617
   ],
   "hydro-lnL-imos-margeta": [
    -2.771082878112793,
    -1.4821505546569824,
    -0.05471200495958328,
    2.126662015914917,
    3.04093074798584
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.387275218963623,
    -2.700455904006958,
    -0.16542139649391174,
    0.8677342534065247,
    1.9245141744613647
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90469875,
   "hydro-lnL-imos-eta2.1e-4": 0.904683125,
   "hydro-lnL-imos-eta1e-4": 0.90467625,
   "hydro-lnL-imos-margeta": 0.90469625,
   "hydro-lnL-ims-proxy-margeta": 0.940855
  },
  "scored_any_share": 0.9409203125,
  "seconds": 113.18339681625366,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.3568115234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.195791244506836,
    -6.495604515075684,
    -0.05487525090575218,
    2.6880581378936768,
    3.4878523349761963
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.981954574584961,
    -4.146327972412109,
    -0.011277532204985619,
    2.021469831466675,
    3.376223564147949
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.563110828399658,
    -3.1877267360687256,
    -0.005289987660944462,
    1.5924651622772217,
    3.2742037773132324
   ],
   "hydro-lnL-imos-margeta": [
    -2.8643674850463867,
    -1.5259778499603271,
    -0.055559396743774414,
    2.128998041152954,
    3.0608859062194824
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.097872734069824,
    -2.558424949645996,
    -0.15353268384933472,
    0.8643037676811218,
    2.0219805240631104
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8745275,
   "hydro-lnL-imos-eta2.1e-4": 0.8745015625,
   "hydro-lnL-imos-eta1e-4": 0.87448875,
   "hydro-lnL-imos-margeta": 0.874525625,
   "hydro-lnL-ims-proxy-margeta": 0.9183665625
  },
  "scored_any_share": 0.91848,
  "seconds": 114.68649792671204,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.280517578125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.997353553771973,
    -6.3383870124816895,
    -0.04713600128889084,
    2.6288344860076904,
    3.4730000495910645
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.8289971351623535,
    -4.014677047729492,
    -0.00966884195804596,
    1.9342777729034424,
    3.3528387546539307
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.456636905670166,
    -3.0655527114868164,
    -0.004528758581727743,
    1.4983932971954346,
    3.2434723377227783
   ],
   "hydro-lnL-imos-margeta": [
    -2.7872278690338135,
    -1.48113214969635,
    -0.04899575561285019,
    2.08034086227417,
    3.031578302383423
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.089552402496338,
    -2.5191428661346436,
    -0.1416507065296173,
    0.8280097246170044,
    2.006561517715454
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.85755375,
   "hydro-lnL-imos-eta2.1e-4": 0.8575290625,
   "hydro-lnL-imos-eta1e-4": 0.8575178125,
   "hydro-lnL-imos-margeta": 0.85755125,
   "hydro-lnL-ims-proxy-margeta": 0.8979190625
  },
  "scored_any_share": 0.898010625,
  "seconds": 114.14624094963074,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.2042236328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.861444473266602,
    -6.1535539627075195,
    -0.03705210238695145,
    2.7956836223602295,
    3.483013868331909
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.702149868011475,
    -3.8589296340942383,
    -0.007476784288883209,
    2.1989996433258057,
    3.388284206390381
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.302330017089844,
    -2.925455093383789,
    -0.0034740399569272995,
    1.7982810735702515,
    3.2950384616851807
   ],
   "hydro-lnL-imos-margeta": [
    -2.698077917098999,
    -1.4252554178237915,
    -0.04021146520972252,
    2.2237260341644287,
    3.0774362087249756
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.080414772033691,
    -2.5199663639068604,
    -0.1264948546886444,
    0.791043758392334,
    1.9129364490509033
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8466725292252922,
   "hydro-lnL-imos-eta2.1e-4": 0.846659716597166,
   "hydro-lnL-imos-eta1e-4": 0.8466553415534155,
   "hydro-lnL-imos-margeta": 0.8466722167221672,
   "hydro-lnL-ims-proxy-margeta": 0.8792862928629286
  },
  "scored_any_share": 0.8793322308223083,
  "seconds": 107.5847978591919,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.3731689453125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.100780487060547,
    -6.37580680847168,
    -0.04965098574757576,
    2.658291816711426,
    3.4769318103790283
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.915093898773193,
    -4.048293113708496,
    -0.010207895189523697,
    1.9770468473434448,
    3.360084295272827
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.508683204650879,
    -3.094291925430298,
    -0.004788088612258434,
    1.5432335138320923,
    3.250903606414795
   ],
   "hydro-lnL-imos-margeta": [
    -2.8031749725341797,
    -1.4862110614776611,
    -0.051000941544771194,
    2.1067917346954346,
    3.0418522357940674
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.150750637054443,
    -2.55476450920105,
    -0.1548224836587906,
    0.826419472694397,
    2.001277446746826
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8702155771557716,
   "hydro-lnL-imos-eta2.1e-4": 0.8701946394463944,
   "hydro-lnL-imos-eta1e-4": 0.8701827643276433,
   "hydro-lnL-imos-margeta": 0.8702130771307713,
   "hydro-lnL-ims-proxy-margeta": 0.9162894753947539
  },
  "scored_any_share": 0.916369476194762,
  "seconds": 104.42883777618408,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.72467041015625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.882869720458984,
    -6.273407936096191,
    -0.05486873909831047,
    2.8120174407958984,
    3.4915621280670166
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.745169162750244,
    -4.016213893890381,
    -0.0113642867654562,
    2.1982128620147705,
    3.3934543132781982
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.384278774261475,
    -3.089689254760742,
    -0.005344611592590809,
    1.7870128154754639,
    3.304687738418579
   ],
   "hydro-lnL-imos-margeta": [
    -2.837661027908325,
    -1.503426432609558,
    -0.05534046143293381,
    2.235154151916504,
    3.086578845977783
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.215182781219482,
    -2.5853917598724365,
    -0.169993594288826,
    0.8632655143737793,
    2.0232362747192383
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8936310636893631,
   "hydro-lnL-imos-eta2.1e-4": 0.8935879391206087,
   "hydro-lnL-imos-eta1e-4": 0.8935663768362316,
   "hydro-lnL-imos-margeta": 0.8936241887581124,
   "hydro-lnL-ims-proxy-margeta": 0.9372815646843532
  },
  "scored_any_share": 0.9373990635093649,
  "seconds": 111.42717003822327,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.64837646484375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.100882530212402,
    -6.416620254516602,
    -0.052782975137233734,
    2.7750234603881836,
    3.4844958782196045
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.916511058807373,
    -4.10202169418335,
    -0.010853868909180164,
    2.1451284885406494,
    3.3815174102783203
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.527711391448975,
    -3.1500093936920166,
    -0.005095051601529121,
    1.7288528680801392,
    3.2841546535491943
   ],
   "hydro-lnL-imos-margeta": [
    -2.8372271060943604,
    -1.5060585737228394,
    -0.053730558604002,
    2.2007558345794678,
    3.068221092224121
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.18861722946167,
    -2.599752187728882,
    -0.16592036187648773,
    0.867457926273346,
    2.0002434253692627
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.88988375,
   "hydro-lnL-imos-eta2.1e-4": 0.889865,
   "hydro-lnL-imos-eta1e-4": 0.88985875,
   "hydro-lnL-imos-margeta": 0.889884375,
   "hydro-lnL-ims-proxy-margeta": 0.9302771875
  },
  "scored_any_share": 0.9303746875,
  "seconds": 105.71779870986938,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.57208251953125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.92505931854248,
    -6.289820671081543,
    -0.05046318098902702,
    2.7768378257751465,
    3.48557448387146
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.783450603485107,
    -4.006764888763428,
    -0.010337108746170998,
    2.1559669971466064,
    3.3826775550842285
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.432640075683594,
    -3.0652334690093994,
    -0.004844541661441326,
    1.740346908569336,
    3.291591167449951
   ],
   "hydro-lnL-imos-margeta": [
    -2.814117431640625,
    -1.4804612398147583,
    -0.05180278420448303,
    2.204488515853882,
    3.072730779647827
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.1287713050842285,
    -2.5622143745422363,
    -0.16013020277023315,
    0.833233654499054,
    1.996091604232788
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8806890625,
   "hydro-lnL-imos-eta2.1e-4": 0.8806684375,
   "hydro-lnL-imos-eta1e-4": 0.88065875,
   "hydro-lnL-imos-margeta": 0.8806871875,
   "hydro-lnL-ims-proxy-margeta": 0.9201284375
  },
  "scored_any_share": 0.92021375,
  "seconds": 104.05773282051086,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.49578857421875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.090421676635742,
    -6.366313457489014,
    -0.04499904066324234,
    2.591672658920288,
    3.470181703567505
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.901939392089844,
    -4.019478797912598,
    -0.009199784137308598,
    1.8856511116027832,
    3.3498854637145996
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.489409446716309,
    -3.066718339920044,
    -0.004307283088564873,
    1.4490221738815308,
    3.240821123123169
   ],
   "hydro-lnL-imos-margeta": [
    -2.801490306854248,
    -1.4779455661773682,
    -0.04704843461513519,
    2.0501489639282227,
    3.029324531555176
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -4.967797756195068,
    -2.4667720794677734,
    -0.13590389490127563,
    0.8037606477737427,
    2.0123589038848877
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8411880993809938,
   "hydro-lnL-imos-eta2.1e-4": 0.8411562240622407,
   "hydro-lnL-imos-eta1e-4": 0.8411418489184892,
   "hydro-lnL-imos-margeta": 0.8411877868778688,
   "hydro-lnL-ims-proxy-margeta": 0.8855735432354324
  },
  "scored_any_share": 0.8857138571385714,
  "seconds": 103.72975516319275,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.41949462890625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.767629623413086,
    -6.209588527679443,
    -0.03744509443640709,
    2.7501654624938965,
    3.4798474311828613
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.6242876052856445,
    -3.955000638961792,
    -0.007614299654960632,
    2.1135692596435547,
    3.373173713684082
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.288793563842773,
    -3.0265398025512695,
    -0.003560307901352644,
    1.691544771194458,
    3.2775611877441406
   ],
   "hydro-lnL-imos-margeta": [
    -2.7937824726104736,
    -1.4694809913635254,
    -0.040248773992061615,
    2.181400775909424,
    3.0627779960632324
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.054953098297119,
    -2.5270912647247314,
    -0.1375395953655243,
    0.8382257223129272,
    1.9675523042678833
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8383333833338333,
   "hydro-lnL-imos-eta2.1e-4": 0.8383155706557066,
   "hydro-lnL-imos-eta1e-4": 0.8383058830588306,
   "hydro-lnL-imos-margeta": 0.8383286957869579,
   "hydro-lnL-ims-proxy-margeta": 0.8824628871288713
  },
  "scored_any_share": 0.8825610131101311,
  "seconds": 104.41163301467896,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.11431884765625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.74435043334961,
    -6.177140712738037,
    -0.047401946038007736,
    2.7340967655181885,
    3.475170135498047
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.620458602905273,
    -3.9211668968200684,
    -0.009726926684379578,
    2.082016706466675,
    3.365525484085083
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.255837917327881,
    -2.9984242916107178,
    -0.004562633112072945,
    1.653576374053955,
    3.2598540782928467
   ],
   "hydro-lnL-imos-margeta": [
    -2.7487411499023438,
    -1.4642947912216187,
    -0.049109019339084625,
    2.164902687072754,
    3.0477797985076904
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.202728271484375,
    -2.610281467437744,
    -0.16375070810317993,
    0.8402709364891052,
    1.9939298629760742
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8832805421945781,
   "hydro-lnL-imos-eta2.1e-4": 0.8832089804101959,
   "hydro-lnL-imos-eta1e-4": 0.8831730432695674,
   "hydro-lnL-imos-margeta": 0.8832708547914521,
   "hydro-lnL-ims-proxy-margeta": 0.9262666748332516
  },
  "scored_any_share": 0.9263447990520095,
  "seconds": 91.39263224601746,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.03802490234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.3582181930542,
    -6.625337600708008,
    -0.048843204975128174,
    2.574828863143921,
    3.4717745780944824
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.136104583740234,
    -4.212998867034912,
    -0.010014579631388187,
    1.855222463607788,
    3.347259521484375
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.702620506286621,
    -3.2416038513183594,
    -0.004691701382398605,
    1.4182252883911133,
    3.232529878616333
   ],
   "hydro-lnL-imos-margeta": [
    -2.9460699558258057,
    -1.5448576211929321,
    -0.050403960049152374,
    2.0370874404907227,
    3.0255274772644043
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -4.9918131828308105,
    -2.493914842605591,
    -0.14453339576721191,
    0.8107841610908508,
    2.010197877883911
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8468169056690567,
   "hydro-lnL-imos-eta2.1e-4": 0.8467775302753028,
   "hydro-lnL-imos-eta1e-4": 0.8467531550315504,
   "hydro-lnL-imos-margeta": 0.8468090930909309,
   "hydro-lnL-ims-proxy-margeta": 0.8952805153051531
  },
  "scored_any_share": 0.8954467669676697,
  "seconds": 88.8867359161377,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.296875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.016436576843262,
    -6.379410266876221,
    -0.053793229162693024,
    2.740723133087158,
    3.483961343765259
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.860590934753418,
    -4.089531421661377,
    -0.011096697300672531,
    2.0969889163970947,
    3.3757495880126953
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.4895172119140625,
    -3.1441400051116943,
    -0.005207391455769539,
    1.671486735343933,
    3.2746896743774414
   ],
   "hydro-lnL-imos-margeta": [
    -2.865602731704712,
    -1.5144177675247192,
    -0.05448642373085022,
    2.173508405685425,
    3.0580227375030518
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.1143364906311035,
    -2.5512726306915283,
    -0.1682879775762558,
    0.853299081325531,
    2.0198476314544678
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8803053655536556,
   "hydro-lnL-imos-eta2.1e-4": 0.8802391148911489,
   "hydro-lnL-imos-eta1e-4": 0.880209427094271,
   "hydro-lnL-imos-margeta": 0.8802928654286543,
   "hydro-lnL-ims-proxy-margeta": 0.9320536955369554
  },
  "scored_any_share": 0.9322015095150952,
  "seconds": 105.4075562953949,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
    -11.147705078125,
    -6.401527404785156,
    -0.047156549990177155,
    2.7504751682281494,
    3.4825072288513184
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.9437575340271,
    -4.05169677734375,
    -0.00965842418372631,
    2.102348804473877,
    3.3758606910705566
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.537557601928711,
    -3.0955495834350586,
    -0.00452351663261652,
    1.6740117073059082,
    3.2760376930236816
   ],
   "hydro-lnL-imos-margeta": [
    -2.8303120136260986,
    -1.488209843635559,
    -0.04896261543035507,
    2.181241035461426,
    3.060328245162964
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.053788185119629,
    -2.519265651702881,
    -0.14924240112304688,
    0.8188432455062866,
    1.9882738590240479
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.862425,
   "hydro-lnL-imos-eta2.1e-4": 0.862408125,
   "hydro-lnL-imos-eta1e-4": 0.8624028125,
   "hydro-lnL-imos-margeta": 0.862423125,
   "hydro-lnL-ims-proxy-margeta": 0.9030934375
  },
  "scored_any_share": 0.9031734375,
  "seconds": 103.83618211746216,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.144287109375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.162766456604004,
    -6.466630458831787,
    -0.0552026703953743,
    2.7673048973083496,
    3.4900190830230713
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.96534538269043,
    -4.1351823806762695,
    -0.011359183117747307,
    2.145782947540283,
    3.390343427658081
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.557703495025635,
    -3.1802878379821777,
    -0.0053349873051047325,
    1.7365031242370605,
    3.298689365386963
   ],
   "hydro-lnL-imos-margeta": [
    -2.8626859188079834,
    -1.5247421264648438,
    -0.0557715967297554,
    2.1988978385925293,
    3.0805752277374268
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.148086071014404,
    -2.563817024230957,
    -0.16078749299049377,
    0.8609485626220703,
    2.0115530490875244
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8776478125,
   "hydro-lnL-imos-eta2.1e-4": 0.8776271875,
   "hydro-lnL-imos-eta1e-4": 0.8776190625,
   "hydro-lnL-imos-margeta": 0.8776446875,
   "hydro-lnL-ims-proxy-margeta": 0.9220653125
  },
  "scored_any_share": 0.9221403125,
  "seconds": 105.67549800872803,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 29.0679931640625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.416502952575684,
    -6.510347843170166,
    -0.046161115169525146,
    2.6123859882354736,
    3.479712963104248
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.187260627746582,
    -4.148594379425049,
    -0.009470396675169468,
    1.9079113006591797,
    3.3617818355560303
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.766209602355957,
    -3.1878089904785156,
    -0.004440227523446083,
    1.4668710231781006,
    3.2556138038635254
   ],
   "hydro-lnL-imos-margeta": [
    -2.9171977043151855,
    -1.5262675285339355,
    -0.04799345135688782,
    2.068653106689453,
    3.0429065227508545
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.049511909484863,
    -2.5048980712890625,
    -0.14205656945705414,
    0.8160643577575684,
    1.9964964389801025
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.838734375,
   "hydro-lnL-imos-eta2.1e-4": 0.838695,
   "hydro-lnL-imos-eta1e-4": 0.8386778125,
   "hydro-lnL-imos-margeta": 0.8387384375,
   "hydro-lnL-ims-proxy-margeta": 0.8853584375
  },
  "scored_any_share": 0.8854846875,
  "seconds": 105.72527289390564,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.99169921875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.968759536743164,
    -6.307584762573242,
    -0.05333954840898514,
    2.6764681339263916,
    3.472365617752075
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.798684120178223,
    -4.0205535888671875,
    -0.011002490296959877,
    1.9981672763824463,
    3.3548989295959473
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.403195381164551,
    -3.079026699066162,
    -0.0051690200343728065,
    1.5652740001678467,
    3.2444698810577393
   ],
   "hydro-lnL-imos-margeta": [
    -2.8062353134155273,
    -1.488958477973938,
    -0.05415266752243042,
    2.1169724464416504,
    3.0333526134490967
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.267496109008789,
    -2.6299877166748047,
    -0.16875089704990387,
    0.8556938171386719,
    2.059339761734009
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8934009375,
   "hydro-lnL-imos-eta2.1e-4": 0.893379375,
   "hydro-lnL-imos-eta1e-4": 0.89337,
   "hydro-lnL-imos-margeta": 0.893401875,
   "hydro-lnL-ims-proxy-margeta": 0.9354790625
  },
  "scored_any_share": 0.9355678125,
  "seconds": 108.6932213306427,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.9154052734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.824604034423828,
    -6.211440086364746,
    -0.0452166423201561,
    2.7848048210144043,
    3.4825639724731445
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.672412872314453,
    -3.941256523132324,
    -0.00924838799983263,
    2.1560702323913574,
    3.3815205097198486
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.296985626220703,
    -3.008667230606079,
    -0.0043355366215109825,
    1.7391420602798462,
    3.286957263946533
   ],
   "hydro-lnL-imos-margeta": [
    -2.762967586517334,
    -1.4622081518173218,
    -0.04735150188207626,
    2.2081058025360107,
    3.0692007541656494
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.113181114196777,
    -2.560307741165161,
    -0.15786011517047882,
    0.819707453250885,
    1.961836338043213
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8768890813908139,
   "hydro-lnL-imos-eta2.1e-4": 0.8768387683876839,
   "hydro-lnL-imos-eta1e-4": 0.8768197056970569,
   "hydro-lnL-imos-margeta": 0.876880643806438,
   "hydro-lnL-ims-proxy-margeta": 0.9215442154421544
  },
  "scored_any_share": 0.9216026535265353,
  "seconds": 112.74831485748291,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.839111328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.042065620422363,
    -6.350466728210449,
    -0.046955522149801254,
    2.5110607147216797,
    3.465471029281616
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.8518452644348145,
    -4.013440132141113,
    -0.009587157517671585,
    1.7698705196380615,
    3.333173990249634
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.438419818878174,
    -3.0579121112823486,
    -0.004482798743993044,
    1.323432445526123,
    3.2078380584716797
   ],
   "hydro-lnL-imos-margeta": [
    -2.7979178428649902,
    -1.4814395904541016,
    -0.04883396252989769,
    1.9871443510055542,
    3.0052337646484375
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -4.986089706420898,
    -2.4604218006134033,
    -0.13644832372665405,
    0.7666870355606079,
    1.9762989282608032
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8462525,
   "hydro-lnL-imos-eta2.1e-4": 0.84619875,
   "hydro-lnL-imos-eta1e-4": 0.846175,
   "hydro-lnL-imos-margeta": 0.84624,
   "hydro-lnL-ims-proxy-margeta": 0.88854375
  },
  "scored_any_share": 0.8887296875,
  "seconds": 110.8233368396759,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 28.80096435546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.705774307250977,
    -6.136733055114746,
    -0.04455925524234772,
    2.7293639183044434,
    3.4767351150512695
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.586043357849121,
    -3.886169910430908,
    -0.009091699495911598,
    2.073009490966797,
    3.36869740486145
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.236716270446777,
    -2.9647021293640137,
    -0.0042536621913313866,
    1.6467554569244385,
    3.266439437866211
   ],
   "hydro-lnL-imos-margeta": [
    -2.7324435710906982,
    -1.4457273483276367,
    -0.046833403408527374,
    2.1620712280273438,
    3.052009105682373
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.228489398956299,
    -2.608996629714966,
    -0.1531572937965393,
    0.8166131973266602,
    1.9796024560928345
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8757637423625764,
   "hydro-lnL-imos-eta2.1e-4": 0.8757387426125739,
   "hydro-lnL-imos-eta1e-4": 0.8757256177438225,
   "hydro-lnL-imos-margeta": 0.8757624923750762,
   "hydro-lnL-ims-proxy-margeta": 0.911840881591184
  },
  "scored_any_share": 0.9119483805161949,
  "seconds": 111.02160120010376,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 35.20965576171875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.85730266571045,
    -6.222487449645996,
    -0.05029559135437012,
    2.8339827060699463,
    3.4859442710876465
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.741461277008057,
    -3.9708621501922607,
    -0.01037211250513792,
    2.2509474754333496,
    3.3979525566101074
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.390607833862305,
    -3.0456225872039795,
    -0.004877908155322075,
    1.8577723503112793,
    3.314345598220825
   ],
   "hydro-lnL-imos-margeta": [
    -2.794513463973999,
    -1.4699386358261108,
    -0.05162368714809418,
    2.2562055587768555,
    3.0954220294952393
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.507837772369385,
    -2.770218849182129,
    -0.18058201670646667,
    0.930253803730011,
    2.1208934783935547
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.917267407848157,
   "hydro-lnL-imos-eta2.1e-4": 0.9172599076981539,
   "hydro-lnL-imos-eta1e-4": 0.9172566263825277,
   "hydro-lnL-imos-margeta": 0.9172653765575312,
   "hydro-lnL-ims-proxy-margeta": 0.9490800753515071
  },
  "scored_any_share": 0.9491030445608912,
  "seconds": 202.1363389492035,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.83636474609375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.644440650939941,
    -6.074194431304932,
    -0.05176081880927086,
    2.8805809020996094,
    3.4923853874206543
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.520603179931641,
    -3.8688907623291016,
    -0.010625890456140041,
    2.323377847671509,
    3.406841278076172
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.180843353271484,
    -2.964345693588257,
    -0.004981285892426968,
    1.9389641284942627,
    3.326707363128662
   ],
   "hydro-lnL-imos-margeta": [
    -2.7495999336242676,
    -1.452556848526001,
    -0.05292191356420517,
    2.2951138019561768,
    3.108147144317627
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.381780624389648,
    -2.6984546184539795,
    -0.18184936046600342,
    0.945959210395813,
    2.227649450302124
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9130125886241137,
   "hydro-lnL-imos-eta2.1e-4": 0.9130055574444256,
   "hydro-lnL-imos-eta1e-4": 0.9130002449975501,
   "hydro-lnL-imos-margeta": 0.9130118073819262,
   "hydro-lnL-ims-proxy-margeta": 0.9497928458215418
  },
  "scored_any_share": 0.949835032899671,
  "seconds": 224.8345992565155,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.68377685546875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.44144058227539,
    -6.036875247955322,
    -0.0476551279425621,
    2.8839495182037354,
    3.487943172454834
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.3939409255981445,
    -3.849140167236328,
    -0.00972829945385456,
    2.32889723777771,
    3.399303436279297
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.10363245010376,
    -2.944563865661621,
    -0.004553935490548611,
    1.946600079536438,
    3.3171439170837402
   ],
   "hydro-lnL-imos-margeta": [
    -2.735548734664917,
    -1.4398595094680786,
    -0.049580156803131104,
    2.298825740814209,
    3.0992021560668945
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.451343059539795,
    -2.7263221740722656,
    -0.17455357313156128,
    0.9269366264343262,
    2.0339746475219727
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9114210420395796,
   "hydro-lnL-imos-eta2.1e-4": 0.9114136983630163,
   "hydro-lnL-imos-eta1e-4": 0.9114085421645783,
   "hydro-lnL-imos-margeta": 0.9114204170458295,
   "hydro-lnL-ims-proxy-margeta": 0.9456856993930061
  },
  "scored_any_share": 0.9457191365586344,
  "seconds": 224.31424379348755,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.53118896484375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.55895709991455,
    -6.163651943206787,
    -0.048897989094257355,
    2.8399388790130615,
    3.490093469619751
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.506636142730713,
    -3.9885454177856445,
    -0.010008938610553741,
    2.2448983192443848,
    3.3978888988494873
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.207726955413818,
    -3.074559211730957,
    -0.0046911695972085,
    1.845514178276062,
    3.3122315406799316
   ],
   "hydro-lnL-imos-margeta": [
    -2.812490940093994,
    -1.4856833219528198,
    -0.050503429025411606,
    2.256375312805176,
    3.0911684036254883
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.231431484222412,
    -2.6379268169403076,
    -0.1694650948047638,
    0.8933374285697937,
    2.0122690200805664
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.894425625,
   "hydro-lnL-imos-eta2.1e-4": 0.89441765625,
   "hydro-lnL-imos-eta1e-4": 0.894414375,
   "hydro-lnL-imos-margeta": 0.89442578125,
   "hydro-lnL-ims-proxy-margeta": 0.9324684375
  },
  "scored_any_share": 0.93249640625,
  "seconds": 222.35743832588196,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.416748046875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.138738632202148,
    -6.41217041015625,
    -0.05356034263968468,
    2.8074114322662354,
    3.4907124042510986
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.954416751861572,
    -4.1203742027282715,
    -0.010957984253764153,
    2.2041311264038086,
    3.3964874744415283
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.559493541717529,
    -3.170044183731079,
    -0.005128839053213596,
    1.8022111654281616,
    3.3086602687835693
   ],
   "hydro-lnL-imos-margeta": [
    -2.8752503395080566,
    -1.518721580505371,
    -0.05457537621259689,
    2.2297306060791016,
    3.0900862216949463
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.197706699371338,
    -2.592923641204834,
    -0.1676933467388153,
    0.8927444815635681,
    1.9992488622665405
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8917634375,
   "hydro-lnL-imos-eta2.1e-4": 0.89174734375,
   "hydro-lnL-imos-eta1e-4": 0.8917390625,
   "hydro-lnL-imos-margeta": 0.8917634375,
   "hydro-lnL-ims-proxy-margeta": 0.93368296875
  },
  "scored_any_share": 0.93373515625,
  "seconds": 208.9281141757965,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.26416015625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.174278259277344,
    -6.4278178215026855,
    -0.05376677215099335,
    2.7472352981567383,
    3.4880306720733643
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.995831489562988,
    -4.1185994148254395,
    -0.010993290692567825,
    2.1223576068878174,
    3.390944480895996
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.607967853546143,
    -3.163703203201294,
    -0.005139945074915886,
    1.715661644935608,
    3.300204038619995
   ],
   "hydro-lnL-imos-margeta": [
    -2.8602120876312256,
    -1.5087602138519287,
    -0.054839760065078735,
    2.179912567138672,
    3.083466053009033
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.286500453948975,
    -2.6356101036071777,
    -0.16987191140651703,
    0.9074543118476868,
    2.022550344467163
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89403953125,
   "hydro-lnL-imos-eta2.1e-4": 0.89403234375,
   "hydro-lnL-imos-eta1e-4": 0.8940290625,
   "hydro-lnL-imos-margeta": 0.89403921875,
   "hydro-lnL-ims-proxy-margeta": 0.93229734375
  },
  "scored_any_share": 0.93233734375,
  "seconds": 212.1124610900879,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.14971923828125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.318798065185547,
    -6.4394731521606445,
    -0.05329684540629387,
    2.792694091796875,
    3.4952473640441895
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.108922004699707,
    -4.083934307098389,
    -0.010965237393975258,
    2.1820201873779297,
    3.3983535766601562
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.681775093078613,
    -3.1281754970550537,
    -0.005149269010871649,
    1.7757529020309448,
    3.307051420211792
   ],
   "hydro-lnL-imos-margeta": [
    -2.864215850830078,
    -1.5044745206832886,
    -0.054236866533756256,
    2.2198691368103027,
    3.0895981788635254
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.437799453735352,
    -2.7162482738494873,
    -0.1765879988670349,
    0.9555612206459045,
    1.9755178689956665
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90426515625,
   "hydro-lnL-imos-eta2.1e-4": 0.9042559375,
   "hydro-lnL-imos-eta1e-4": 0.9042521875,
   "hydro-lnL-imos-margeta": 0.90426390625,
   "hydro-lnL-ims-proxy-margeta": 0.94359375
  },
  "scored_any_share": 0.94362765625,
  "seconds": 212.6306209564209,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.99713134765625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.870800018310547,
    -6.240907669067383,
    -0.04988141730427742,
    2.797140598297119,
    3.4928531646728516
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.726846694946289,
    -3.9777462482452393,
    -0.010220149531960487,
    2.189838171005249,
    3.3984525203704834
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.378378391265869,
    -3.0465455055236816,
    -0.004788067191839218,
    1.7818232774734497,
    3.3112576007843018
   ],
   "hydro-lnL-imos-margeta": [
    -2.8122024536132812,
    -1.477962851524353,
    -0.051440827548503876,
    2.2220027446746826,
    3.092479705810547
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.24072265625,
    -2.618837356567383,
    -0.164752796292305,
    0.9173921346664429,
    2.0174849033355713
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.88879,
   "hydro-lnL-imos-eta2.1e-4": 0.8887678125,
   "hydro-lnL-imos-eta1e-4": 0.88875859375,
   "hydro-lnL-imos-margeta": 0.8887884375,
   "hydro-lnL-ims-proxy-margeta": 0.93400234375
  },
  "scored_any_share": 0.9340740625,
  "seconds": 210.81942892074585,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.92083740234375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.8673734664917,
    -6.253142833709717,
    -0.04586295038461685,
    2.8561832904815674,
    3.4891269207000732
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.716186046600342,
    -3.9709713459014893,
    -0.009334178641438484,
    2.2771294116973877,
    3.3998680114746094
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.354365348815918,
    -3.0344274044036865,
    -0.004357585683465004,
    1.883560299873352,
    3.315960168838501
   ],
   "hydro-lnL-imos-margeta": [
    -2.7610950469970703,
    -1.459272027015686,
    -0.048082806169986725,
    2.2713544368743896,
    3.0956170558929443
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.228288650512695,
    -2.621230125427246,
    -0.16079704463481903,
    0.9589754939079285,
    2.0661003589630127
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89188609375,
   "hydro-lnL-imos-eta2.1e-4": 0.8918784375,
   "hydro-lnL-imos-eta1e-4": 0.89187484375,
   "hydro-lnL-imos-margeta": 0.8918871875,
   "hydro-lnL-ims-proxy-margeta": 0.92667046875
  },
  "scored_any_share": 0.92669484375,
  "seconds": 219.47875905036926,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.76824951171875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.82723617553711,
    -6.190918922424316,
    -0.05054564028978348,
    2.7649338245391846,
    3.4838926792144775
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.695882320404053,
    -3.9341607093811035,
    -0.010297666303813457,
    2.1386971473693848,
    3.3846237659454346
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.350059509277344,
    -3.0055527687072754,
    -0.004815402440726757,
    1.7231839895248413,
    3.291187286376953
   ],
   "hydro-lnL-imos-margeta": [
    -2.7726404666900635,
    -1.4543876647949219,
    -0.0521714985370636,
    2.1931464672088623,
    3.071525812149048
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.329352855682373,
    -2.6607606410980225,
    -0.17308293282985687,
    0.9139769673347473,
    2.0988221168518066
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90419859375,
   "hydro-lnL-imos-eta2.1e-4": 0.90419046875,
   "hydro-lnL-imos-eta1e-4": 0.904185625,
   "hydro-lnL-imos-margeta": 0.9041978125,
   "hydro-lnL-ims-proxy-margeta": 0.93692703125
  },
  "scored_any_share": 0.936955,
  "seconds": 223.589693069458,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.65380859375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.320242881774902,
    -5.966585159301758,
    -0.04809259623289108,
    2.9314382076263428,
    3.4948532581329346
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.2988200187683105,
    -3.821263074874878,
    -0.009790735319256783,
    2.395099639892578,
    3.414492130279541
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.032387733459473,
    -2.9244301319122314,
    -0.004578231833875179,
    2.0233888626098633,
    3.3383371829986572
   ],
   "hydro-lnL-imos-margeta": [
    -2.7093753814697266,
    -1.431900978088379,
    -0.0500250905752182,
    2.3410630226135254,
    3.1182501316070557
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.268195152282715,
    -2.655517339706421,
    -0.17619001865386963,
    0.9113560318946838,
    2.0288846492767334
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.91066921875,
   "hydro-lnL-imos-eta2.1e-4": 0.9106396875,
   "hydro-lnL-imos-eta1e-4": 0.9106221875,
   "hydro-lnL-imos-margeta": 0.9106646875,
   "hydro-lnL-ims-proxy-margeta": 0.94542109375
  },
  "scored_any_share": 0.94545265625,
  "seconds": 223.1726861000061,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 35.09521484375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.166752815246582,
    -6.425477981567383,
    -0.05330171808600426,
    2.8431894779205322,
    3.4941463470458984
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.970364570617676,
    -4.093836307525635,
    -0.010984161868691444,
    2.2692627906799316,
    3.404890537261963
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.573025703430176,
    -3.1386899948120117,
    -0.005158154293894768,
    1.8784888982772827,
    3.3190741539001465
   ],
   "hydro-lnL-imos-margeta": [
    -2.848979949951172,
    -1.5033464431762695,
    -0.05416864901781082,
    2.2650043964385986,
    3.0999605655670166
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.343638896942139,
    -2.6685984134674072,
    -0.17170068621635437,
    0.9344514608383179,
    2.015467643737793
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90423546875,
   "hydro-lnL-imos-eta2.1e-4": 0.90422421875,
   "hydro-lnL-imos-eta1e-4": 0.904219375,
   "hydro-lnL-imos-margeta": 0.90423625,
   "hydro-lnL-ims-proxy-margeta": 0.94245046875
  },
  "scored_any_share": 0.9424871875,
  "seconds": 207.1814591884613,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.501220703125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.480605125427246,
    -6.014565467834473,
    -0.04668298363685608,
    2.9990358352661133,
    3.501641273498535
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.40913200378418,
    -3.8265230655670166,
    -0.009524840861558914,
    2.493250846862793,
    3.426847219467163
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.099333763122559,
    -2.9269375801086426,
    -0.004453127272427082,
    2.130971670150757,
    3.3540706634521484
   ],
   "hydro-lnL-imos-margeta": [
    -2.705630302429199,
    -1.440394401550293,
    -0.048769596964120865,
    2.402611255645752,
    3.1363039016723633
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.285722732543945,
    -2.6552724838256836,
    -0.16664588451385498,
    0.8976173400878906,
    2.0309195518493652
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.90505484375,
   "hydro-lnL-imos-eta2.1e-4": 0.90504640625,
   "hydro-lnL-imos-eta1e-4": 0.905043125,
   "hydro-lnL-imos-margeta": 0.9050540625,
   "hydro-lnL-ims-proxy-margeta": 0.9389896875
  },
  "scored_any_share": 0.93902390625,
  "seconds": 221.22986888885498,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.3486328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.357121467590332,
    -5.864138126373291,
    -0.04914344847202301,
    2.815042495727539,
    3.4816715717315674
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.291884899139404,
    -3.721109390258789,
    -0.010083654895424843,
    2.211785078048706,
    3.3867406845092773
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.009481430053711,
    -2.838165283203125,
    -0.004727629013359547,
    1.8064996004104614,
    3.2999331951141357
   ],
   "hydro-lnL-imos-margeta": [
    -2.6681153774261475,
    -1.411749005317688,
    -0.05074284225702286,
    2.2356064319610596,
    3.082028388977051
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.450570106506348,
    -2.7317779064178467,
    -0.1793968677520752,
    0.8934581875801086,
    2.0474624633789062
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.912650625,
   "hydro-lnL-imos-eta2.1e-4": 0.91264578125,
   "hydro-lnL-imos-eta1e-4": 0.91264296875,
   "hydro-lnL-imos-margeta": 0.91265125,
   "hydro-lnL-ims-proxy-margeta": 0.94437359375
  },
  "scored_any_share": 0.94439953125,
  "seconds": 222.46383571624756,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.196044921875,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.81557559967041,
    -6.192165374755859,
    -0.04600486904382706,
    2.8393919467926025,
    3.4853506088256836
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.688662528991699,
    -3.9304072856903076,
    -0.009375197812914848,
    2.253145933151245,
    3.393407106399536
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.333690166473389,
    -2.996009111404419,
    -0.004384971223771572,
    1.8561149835586548,
    3.301882743835449
   ],
   "hydro-lnL-imos-margeta": [
    -2.747743606567383,
    -1.4490777254104614,
    -0.04813550412654877,
    2.25817608833313,
    3.081829071044922
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.345914840698242,
    -2.681427240371704,
    -0.169806569814682,
    0.9068357348442078,
    2.0483996868133545
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.899724778497785,
   "hydro-lnL-imos-eta2.1e-4": 0.8997196221962219,
   "hydro-lnL-imos-eta1e-4": 0.8997172784227843,
   "hydro-lnL-imos-margeta": 0.8997233722337223,
   "hydro-lnL-ims-proxy-margeta": 0.9329404231542315
  },
  "scored_any_share": 0.9329640171401714,
  "seconds": 223.0466170310974,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 32.08160400390625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.38770580291748,
    -6.517002105712891,
    -0.05519362911581993,
    2.771279811859131,
    3.485980749130249
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -8.184907913208008,
    -4.1488566398620605,
    -0.01130589097738266,
    2.1450040340423584,
    3.3883419036865234
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.772051811218262,
    -3.174619674682617,
    -0.00529550202190876,
    1.7311041355133057,
    3.296985626220703
   ],
   "hydro-lnL-imos-margeta": [
    -2.847104072570801,
    -1.4967812299728394,
    -0.056014083325862885,
    2.1977450847625732,
    3.0787625312805176
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.437777042388916,
    -2.706876277923584,
    -0.18057997524738312,
    0.8814605474472046,
    2.0989623069763184
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.91282203125,
   "hydro-lnL-imos-eta2.1e-4": 0.912810625,
   "hydro-lnL-imos-eta1e-4": 0.91280515625,
   "hydro-lnL-imos-margeta": 0.91282171875,
   "hydro-lnL-ims-proxy-margeta": 0.94652078125
  },
  "scored_any_share": 0.94656875,
  "seconds": 227.27568101882935,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 31.9671630859375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -11.03130054473877,
    -6.308378219604492,
    -0.052152760326862335,
    2.773770570755005,
    3.485630750656128
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.865561485290527,
    -4.031998634338379,
    -0.010644007474184036,
    2.1391358375549316,
    3.385524272918701
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.4932074546813965,
    -3.09333872795105,
    -0.004978138953447342,
    1.726894736289978,
    3.2941160202026367
   ],
   "hydro-lnL-imos-margeta": [
    -2.8145394325256348,
    -1.4876899719238281,
    -0.05348362401127815,
    2.197819471359253,
    3.076411724090576
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.244221210479736,
    -2.631962299346924,
    -0.17244185507297516,
    0.8909437656402588,
    1.9843798875808716
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8978938226882269,
   "hydro-lnL-imos-eta2.1e-4": 0.897885072600726,
   "hydro-lnL-imos-eta1e-4": 0.8978821038210382,
   "hydro-lnL-imos-margeta": 0.8978925726757268,
   "hydro-lnL-ims-proxy-margeta": 0.9359901411514115
  },
  "scored_any_share": 0.9360223289732897,
  "seconds": 223.10784912109375,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.942626953125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.557567596435547,
    -6.019255638122559,
    -0.047223448753356934,
    2.7569828033447266,
    3.4803473949432373
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.4522881507873535,
    -3.7911558151245117,
    -0.00970481988042593,
    2.134601593017578,
    3.3807499408721924
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.121203422546387,
    -2.880150079727173,
    -0.004556885454803705,
    1.7229669094085693,
    3.2866575717926025
   ],
   "hydro-lnL-imos-margeta": [
    -2.6683454513549805,
    -1.4201642274856567,
    -0.04907190799713135,
    2.186582326889038,
    3.0680296421051025
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.458474636077881,
    -2.7341654300689697,
    -0.16539767384529114,
    0.926302433013916,
    2.0249948501586914
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89984421875,
   "hydro-lnL-imos-eta2.1e-4": 0.8998396875,
   "hydro-lnL-imos-eta1e-4": 0.899836875,
   "hydro-lnL-imos-margeta": 0.89984328125,
   "hydro-lnL-ims-proxy-margeta": 0.929993125
  },
  "scored_any_share": 0.9300115625,
  "seconds": 210.26263403892517,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.82818603515625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.860260009765625,
    -6.374195575714111,
    -0.054502472281455994,
    2.882190704345703,
    3.4927282333374023
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.751722812652588,
    -4.146088600158691,
    -0.011179761961102486,
    2.320915699005127,
    3.4048354625701904
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.412097454071045,
    -3.213536500930786,
    -0.005237969569861889,
    1.939341425895691,
    3.3198440074920654
   ],
   "hydro-lnL-imos-margeta": [
    -2.8829452991485596,
    -1.53655207157135,
    -0.05541325360536575,
    2.2972564697265625,
    3.1006126403808594
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.381653308868408,
    -2.688037157058716,
    -0.17175400257110596,
    0.8988669514656067,
    2.002849578857422
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.91295234375,
   "hydro-lnL-imos-eta2.1e-4": 0.91294515625,
   "hydro-lnL-imos-eta1e-4": 0.91294203125,
   "hydro-lnL-imos-margeta": 0.9129528125,
   "hydro-lnL-ims-proxy-margeta": 0.9448425
  },
  "scored_any_share": 0.94487390625,
  "seconds": 209.62558794021606,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.52301025390625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.888752937316895,
    -6.203941345214844,
    -0.05132000893354416,
    2.8115224838256836,
    3.490285634994507
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.720125198364258,
    -3.935166120529175,
    -0.010542958974838257,
    2.2167158126831055,
    3.398055076599121
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.355319499969482,
    -3.0033230781555176,
    -0.004948166199028492,
    1.8151510953903198,
    3.313490152359009
   ],
   "hydro-lnL-imos-margeta": [
    -2.7630503177642822,
    -1.4601905345916748,
    -0.05258363485336304,
    2.234943389892578,
    3.0943071842193604
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.32265567779541,
    -2.670619487762451,
    -0.17067950963974,
    0.9209495186805725,
    2.046213388442993
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9020142611073889,
   "hydro-lnL-imos-eta2.1e-4": 0.9020034799652004,
   "hydro-lnL-imos-eta1e-4": 0.9019980112698873,
   "hydro-lnL-imos-margeta": 0.9020119173808262,
   "hydro-lnL-ims-proxy-margeta": 0.936959380406196
  },
  "scored_any_share": 0.9370059424405756,
  "seconds": 266.32764506340027,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.37042236328125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.935352325439453,
    -6.252572059631348,
    -0.05062246322631836,
    2.7478506565093994,
    3.4825143814086914
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.7772216796875,
    -3.965000867843628,
    -0.01036752201616764,
    2.122690200805664,
    3.382782220840454
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.406610012054443,
    -3.032000780105591,
    -0.004858840256929398,
    1.71531343460083,
    3.2896878719329834
   ],
   "hydro-lnL-imos-margeta": [
    -2.775209903717041,
    -1.466713547706604,
    -0.052121601998806,
    2.1795732975006104,
    3.072551727294922
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.397405624389648,
    -2.703915596008301,
    -0.17134112119674683,
    0.8824318051338196,
    1.9748057126998901
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.8991152411524115,
   "hydro-lnL-imos-eta2.1e-4": 0.8991016472664727,
   "hydro-lnL-imos-eta1e-4": 0.8990969597195972,
   "hydro-lnL-imos-margeta": 0.8991130536305363,
   "hydro-lnL-ims-proxy-margeta": 0.9322777602776028
  },
  "scored_any_share": 0.9323190106901069,
  "seconds": 265.29102897644043,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.2559814453125,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.910280227661133,
    -6.208801746368408,
    -0.04463299363851547,
    2.9843878746032715,
    3.5001027584075928
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.743002414703369,
    -3.909531354904175,
    -0.009162470698356628,
    2.487229824066162,
    3.427180767059326
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.354370594024658,
    -2.975043773651123,
    -0.004302755929529667,
    2.1297760009765625,
    3.357821464538574
   ],
   "hydro-lnL-imos-margeta": [
    -2.746424674987793,
    -1.4474129676818848,
    -0.046711042523384094,
    2.39286470413208,
    3.1408140659332275
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.302483081817627,
    -2.6556355953216553,
    -0.1574409008026123,
    0.9842774868011475,
    2.3629534244537354
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.89190671875,
   "hydro-lnL-imos-eta2.1e-4": 0.89189796875,
   "hydro-lnL-imos-eta1e-4": 0.89189234375,
   "hydro-lnL-imos-margeta": 0.8919078125,
   "hydro-lnL-ims-proxy-margeta": 0.9247253125
  },
  "scored_any_share": 0.92475296875,
  "seconds": 261.3113250732422,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 34.14154052734375,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.361983299255371,
    -5.936303615570068,
    -0.04873228445649147,
    2.726876735687256,
    3.4755935668945312
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.309346675872803,
    -3.7650387287139893,
    -0.009938535280525684,
    2.0841190814971924,
    3.3670125007629395
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.009596347808838,
    -2.8668508529663086,
    -0.004648993723094463,
    1.6625703573226929,
    3.2672154903411865
   ],
   "hydro-lnL-imos-margeta": [
    -2.6618192195892334,
    -1.4125481843948364,
    -0.05058802664279938,
    2.1603996753692627,
    3.051776885986328
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.459761142730713,
    -2.734591484069824,
    -0.17524735629558563,
    0.9279691576957703,
    2.266641855239868
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9102394913550864,
   "hydro-lnL-imos-eta2.1e-4": 0.9102279289707103,
   "hydro-lnL-imos-eta1e-4": 0.9102227727722723,
   "hydro-lnL-imos-margeta": 0.9102371476285237,
   "hydro-lnL-ims-proxy-margeta": 0.9413929298207018
  },
  "scored_any_share": 0.9414171483285168,
  "seconds": 260.9134018421173,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
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
  "free_gib_at_write": 33.9508056640625,
  "quantiles": {
   "hydro-lnL-imos-eta1e-3": [
    -10.421688079833984,
    -5.981213569641113,
    -0.04578135535120964,
    2.8677117824554443,
    3.4872446060180664
   ],
   "hydro-lnL-imos-eta2.1e-4": [
    -7.367404937744141,
    -3.818178415298462,
    -0.009293769486248493,
    2.299124002456665,
    3.3977859020233154
   ],
   "hydro-lnL-imos-eta1e-4": [
    -6.0718674659729,
    -2.9190421104431152,
    -0.004336129408329725,
    1.911144495010376,
    3.313375949859619
   ],
   "hydro-lnL-imos-margeta": [
    -2.7105400562286377,
    -1.43110191822052,
    -0.04806649684906006,
    2.282557964324951,
    3.09576678276062
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.3869709968566895,
    -2.7111146450042725,
    -0.1718015968799591,
    0.9021639227867126,
    2.071178913116455
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta1e-3": 0.9067834375,
   "hydro-lnL-imos-eta2.1e-4": 0.90677796875,
   "hydro-lnL-imos-eta1e-4": 0.90677515625,
   "hydro-lnL-imos-margeta": 0.9067825,
   "hydro-lnL-ims-proxy-margeta": 0.938570625
  },
  "scored_any_share": 0.93859421875,
  "seconds": 222.19417023658752,
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
  },
  "imos_tl": "imos_tl_ram_arc.csv (A4)",
  "ramgrid_covered_share": {
   "3376": 1.0,
   "3315": 1.0,
   "3274": 1.0,
   "3275": 1.0
  }
 }
}
