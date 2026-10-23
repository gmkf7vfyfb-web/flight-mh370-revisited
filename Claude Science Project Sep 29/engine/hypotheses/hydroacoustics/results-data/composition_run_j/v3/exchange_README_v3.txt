Hydroacoustics block 11 (composition), PRODUCT v3 (amendment A6), end of flight run J, all four strata (74 seeds). Written 2026-10-23T05:40:47Z.
Same inputs, code path and random calibration draws as run-j-gated-v2 (IMOS TL imos_tl_ram_arc.csv, A4); changes (A6, Pete ruling X03 23 Oct 2026):
the coupling prior is log-uniform on [1e-6, 1] (1 = physical limit), 61 grid points at 0.1 decade; the first 41 points equal the v2 grid.
Rows 313,599,968; not_computed (NaN) 0; per-seed checks (rows, float32, NaN pattern identical across columns, finite elsewhere): all pass. 6 workers.
Columns not repeated from v2 (identical there): hydro-lnL-imos-eta1e-3, -eta2.1e-4, -eta1e-4.

COLUMNS (float32, row i = row i of end-of-flight/run-j/<stratum>/seed-N/impacts32.npy):
  hydro-lnL-imos-eta2.26e-3.npy     ln L of the IMOS-gated term at eta = 2.26e-3 (F-35A value under the module definition, Metz 2023 arrival)
  hydro-lnL-imos-margeta.npy        ... marginalised over log-uniform eta on [1e-6, 1] (61 points)  <- v3 default candidate (not ruled for the composer)
  hydro-lnL-imos-margeta-ub1e-1.npy ... on [1e-6, 1e-1] (51 points)       SENSITIVITY (prior upper bound)
  hydro-lnL-imos-margeta-ub1e-2.npy ... on [1e-6, 1e-2] (41 points) = the v2 default column (regression check)
  hydro-lnL-ims-proxy-margeta.npy   SENSITIVITY: IMOS-gated x H01W/H08S PROXY-background terms, eta on [1e-6, 1]. PREDICTIVE for IMS.
  hydro-lnL-imos-amp-margeta.npy    SENSITIVITY (G11-1): amplitude-consistency-weighted match (sigma 1 decade), eta on [1e-6, 1]
NaN = not computed; 0.0 = computed, no information. Accumulators: acc.npz (bound 1), acc_ub0.1.npz, acc_ub0.01.npz per seed.

KNOWN LIMITS (registry defects): D05 detector not validated on real long-range arrivals; D06 IMS stand-in noise (proxy column only);
G11-1 matching is amplitude-blind in every column except -amp-: a match counts whatever coupling it needs. The Portland 3275 matches
01:20:35 and 01:07:47 need coupling about 0.022 and 0.014 at the q99 run J energy (corrected TL; about 9.7x and 6x the F-35A value
2.26e-3; possible, below 1). A higher prior bound gives such matches more weight, so the 1e-2 / 1e-1 / 1 differences partly measure
G11-1, not physics. D25 source depth fixed at 10 m. H01W match 00:52:04 matches Royer icequake A ONLY on the uncorrected Fig. 4 time
base (+21.7 s from the Table-5-based prediction, outside +/-7.0 s); conditional, not a finding (D07).
[CORRECTED 2026-10-23 05:45 UTC after generation: the driver text said "need eta 30 / 19 (above 1, physically impossible)"; that
used the uncorrected pass-A TL and is wrong. See tables potential-signals-2026-10-23-v3 (S001 0.0219).]
PREDICTIVE, NOT CALIBRATED.

Per-seed summary:
{
 "run-j-descent-climb/seed-1": {
  "stratum": "run-j-descent-climb",
  "seed": 1,
  "rows": 3200000,
  "not_computed": 0,
  "E_fallback": 0,
  "columns_written": [
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.38958740234375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.987068176269531,
    -7.90643310546875,
    -0.11827880144119263,
    2.902280330657959,
    3.511064291000366
   ],
   "hydro-lnL-imos-margeta": [
    -3.245089292526245,
    -1.9139338731765747,
    -0.3596852421760559,
    2.6499974727630615,
    3.217271089553833
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0665693283081055,
    -1.7357038259506226,
    -0.19187530875205994,
    2.4497079849243164,
    3.1543478965759277
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8498263359069824,
    -1.5188053846359253,
    -0.05378499627113342,
    2.1207761764526367,
    3.0570101737976074
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.518211364746094,
    -2.95920729637146,
    -0.526787519454956,
    0.687351405620575,
    1.7089883089065552
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2517950534820557,
    -1.9192606210708618,
    -0.3619862496852875,
    2.2392306327819824,
    2.5095314979553223
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8717640625,
   "hydro-lnL-imos-margeta": 0.871811875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8717809375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.871756875,
   "hydro-lnL-ims-proxy-margeta": 0.9147796875,
   "hydro-lnL-imos-amp-margeta": 0.8718040625
  },
  "scored_any_share": 0.9148825,
  "seconds": 453.9564154148102,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.55035400390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.632189750671387,
    -7.667299270629883,
    -0.1056128740310669,
    2.9522182941436768,
    3.5070078372955322
   ],
   "hydro-lnL-imos-margeta": [
    -3.1677191257476807,
    -1.86640465259552,
    -0.3489528298377991,
    2.678267478942871,
    3.2156753540039062
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.990575075149536,
    -1.6885535717010498,
    -0.1821414977312088,
    2.4839348793029785,
    3.1534783840179443
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.773932456970215,
    -1.4721319675445557,
    -0.04884246736764908,
    2.168327569961548,
    3.0578339099884033
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.550047874450684,
    -2.968099355697632,
    -0.5307418704032898,
    0.5953439474105835,
    1.683977723121643
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1772778034210205,
    -1.8725457191467285,
    -0.3514055013656616,
    2.2614665031433105,
    2.4993677139282227
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8783555914440856,
   "hydro-lnL-imos-margeta": 0.8783862161378386,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8783652788472115,
   "hydro-lnL-imos-margeta-ub1e-2": 0.878349966500335,
   "hydro-lnL-ims-proxy-margeta": 0.9149483505164948,
   "hydro-lnL-imos-amp-margeta": 0.8783827786722133
  },
  "scored_any_share": 0.9150164748352516,
  "seconds": 459.384330034256,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.4359130859375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.084732055664062,
    -7.10235071182251,
    -0.11638829112052917,
    2.7405693531036377,
    3.4918570518493652
   ],
   "hydro-lnL-imos-margeta": [
    -3.0104520320892334,
    -1.7822794914245605,
    -0.3597058653831482,
    2.556067943572998,
    3.179032802581787
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.8323724269866943,
    -1.604054570198059,
    -0.19149228930473328,
    2.3307697772979736,
    3.1071434020996094
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.6144473552703857,
    -1.3873308897018433,
    -0.05312512814998627,
    1.9573935270309448,
    2.9989657402038574
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.62677526473999,
    -3.0194497108459473,
    -0.542797327041626,
    0.6133820414543152,
    1.7539219856262207
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.016186237335205,
    -1.787003517150879,
    -0.3614044785499573,
    2.1698250770568848,
    2.4880707263946533
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.896289375,
   "hydro-lnL-imos-margeta": 0.8963028125,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8962925,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8962859375,
   "hydro-lnL-ims-proxy-margeta": 0.9288253125,
   "hydro-lnL-imos-amp-margeta": 0.8963
  },
  "scored_any_share": 0.928864375,
  "seconds": 460.36715173721313,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.359619140625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.149724006652832,
    -7.325206279754639,
    -0.10857124626636505,
    3.029402732849121,
    3.506251096725464
   ],
   "hydro-lnL-imos-margeta": [
    -3.1483359336853027,
    -1.8594672679901123,
    -0.3519262373447418,
    2.722750186920166,
    3.227865695953369
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.970839738845825,
    -1.6817342042922974,
    -0.1848616898059845,
    2.545786142349243,
    3.1692543029785156
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.753176212310791,
    -1.4651974439620972,
    -0.05003943294286728,
    2.2571492195129395,
    3.0822503566741943
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.70797061920166,
    -3.0636677742004395,
    -0.5376304388046265,
    0.5747247338294983,
    1.6896408796310425
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.156773328781128,
    -1.8659478425979614,
    -0.35447341203689575,
    2.2809925079345703,
    2.4907453060150146
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.897976875,
   "hydro-lnL-imos-margeta": 0.8979996875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8979853125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8979703125,
   "hydro-lnL-ims-proxy-margeta": 0.928203125,
   "hydro-lnL-imos-amp-margeta": 0.8979909375
  },
  "scored_any_share": 0.9282415625,
  "seconds": 461.2687129974365,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.32147216796875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.020160675048828,
    -8.005990028381348,
    -0.12452566623687744,
    2.9391820430755615,
    3.5156545639038086
   ],
   "hydro-lnL-imos-margeta": [
    -3.324601650238037,
    -1.9295344352722168,
    -0.3641449511051178,
    2.670511245727539,
    3.222801685333252
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.1475255489349365,
    -1.751685619354248,
    -0.1962333619594574,
    2.476743221282959,
    3.1602156162261963
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.931602716445923,
    -1.534645915031433,
    -0.056108780205249786,
    2.161256790161133,
    3.0636250972747803
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.513215065002441,
    -2.9185776710510254,
    -0.5320411920547485,
    0.7959147691726685,
    1.7254929542541504
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.3347978591918945,
    -1.935071349143982,
    -0.366784930229187,
    2.255796194076538,
    2.508373737335205
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8766971875,
   "hydro-lnL-imos-margeta": 0.87673875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8767090625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8766809375,
   "hydro-lnL-ims-proxy-margeta": 0.9173875,
   "hydro-lnL-imos-amp-margeta": 0.8767321875
  },
  "scored_any_share": 0.9174371875,
  "seconds": 476.45203399658203,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.20703125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.523164749145508,
    -7.558803558349609,
    -0.103243887424469,
    3.1891205310821533,
    3.5211734771728516
   ],
   "hydro-lnL-imos-margeta": [
    -3.1817212104797363,
    -1.8606466054916382,
    -0.34586024284362793,
    2.8414902687072754,
    3.287105083465576
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.004507541656494,
    -1.6832525730133057,
    -0.17961953580379486,
    2.6940805912017822,
    3.240360975265503
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7878167629241943,
    -1.4672389030456543,
    -0.047880806028842926,
    2.4569623470306396,
    3.170788288116455
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.550612926483154,
    -2.990920066833496,
    -0.5307126045227051,
    0.6666601300239563,
    1.7233707904815674
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1951818466186523,
    -1.8696166276931763,
    -0.3490023612976074,
    2.351907253265381,
    2.493773937225342
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.897209777902221,
   "hydro-lnL-imos-margeta": 0.8972313401865981,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8972188403115969,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8972050904490955,
   "hydro-lnL-ims-proxy-margeta": 0.9287557124428756,
   "hydro-lnL-imos-amp-margeta": 0.8972254027459725
  },
  "scored_any_share": 0.9288060244397556,
  "seconds": 475.61696600914,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.1307373046875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.440498352050781,
    -7.5376877784729,
    -0.10798951983451843,
    2.9332854747772217,
    3.5030202865600586
   ],
   "hydro-lnL-imos-margeta": [
    -3.1320815086364746,
    -1.8548684120178223,
    -0.3510546386241913,
    2.6647024154663086,
    3.211540460586548
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.953420639038086,
    -1.6767921447753906,
    -0.18401169776916504,
    2.4680898189544678,
    3.1478464603424072
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.737699270248413,
    -1.4601720571517944,
    -0.0497693195939064,
    2.1438686847686768,
    3.0522336959838867
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.602657318115234,
    -2.9989004135131836,
    -0.5294969081878662,
    0.6083559989929199,
    1.710423231124878
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1416664123535156,
    -1.8601982593536377,
    -0.3533811569213867,
    2.2499639987945557,
    2.4978363513946533
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.88448,
   "hydro-lnL-imos-margeta": 0.8844971875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8844840625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8844740625,
   "hydro-lnL-ims-proxy-margeta": 0.9178978125,
   "hydro-lnL-imos-amp-margeta": 0.8844946875
  },
  "scored_any_share": 0.91793875,
  "seconds": 477.2918059825897,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.054443359375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.316703796386719,
    -7.456199645996094,
    -0.10429820418357849,
    3.0234920978546143,
    3.5065269470214844
   ],
   "hydro-lnL-imos-margeta": [
    -3.116968870162964,
    -1.8461272716522217,
    -0.34748953580856323,
    2.7201550006866455,
    3.2250659465789795
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9408152103424072,
    -1.6683151721954346,
    -0.18093448877334595,
    2.5414021015167236,
    3.1650333404541016
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7255077362060547,
    -1.4522396326065063,
    -0.048296526074409485,
    2.247255325317383,
    3.0738589763641357
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.662627220153809,
    -3.041140079498291,
    -0.5393912196159363,
    0.6173096299171448,
    1.7015697956085205
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.12850284576416,
    -1.852927327156067,
    -0.3501743674278259,
    2.2842485904693604,
    2.4937684535980225
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8966178125,
   "hydro-lnL-imos-margeta": 0.8966359375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.896620625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.896613125,
   "hydro-lnL-ims-proxy-margeta": 0.928619375,
   "hydro-lnL-imos-amp-margeta": 0.8966346875
  },
  "scored_any_share": 0.928655,
  "seconds": 476.88092708587646,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.16070556640625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.29617977142334,
    -7.41624641418457,
    -0.11400504410266876,
    2.9587271213531494,
    3.5064430236816406
   ],
   "hydro-lnL-imos-margeta": [
    -3.1702420711517334,
    -1.8743741512298584,
    -0.3574373722076416,
    2.6820762157440186,
    3.2095696926116943
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9921984672546387,
    -1.6964443922042847,
    -0.18959857523441315,
    2.489936351776123,
    3.1448380947113037
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.774714708328247,
    -1.4796371459960938,
    -0.05222277343273163,
    2.1664488315582275,
    3.0472795963287354
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.702131271362305,
    -3.0626816749572754,
    -0.5410796403884888,
    0.6090170741081238,
    1.7761813402175903
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1764907836914062,
    -1.8798584938049316,
    -0.3596424460411072,
    2.269923210144043,
    2.5064480304718018
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8958576039239607,
   "hydro-lnL-imos-margeta": 0.8958782287177128,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8958647913520865,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8958532289677104,
   "hydro-lnL-ims-proxy-margeta": 0.9306650683493165,
   "hydro-lnL-imos-amp-margeta": 0.8958738537614623
  },
  "scored_any_share": 0.930709130408696,
  "seconds": 449.7955050468445,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.31329345703125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.204604148864746,
    -7.213977813720703,
    -0.07725220918655396,
    2.6649856567382812,
    3.4775397777557373
   ],
   "hydro-lnL-imos-margeta": [
    -2.9536068439483643,
    -1.7577003240585327,
    -0.3197702169418335,
    2.511439561843872,
    3.1507010459899902
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.7748522758483887,
    -1.579236626625061,
    -0.15592223405838013,
    2.2757537364959717,
    3.0766148567199707
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.558159112930298,
    -1.362074851989746,
    -0.03716321289539337,
    1.8750776052474976,
    2.9592607021331787
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.615781307220459,
    -3.0033321380615234,
    -0.4904826879501343,
    0.45470890402793884,
    1.6971999406814575
   ],
   "hydro-lnL-imos-amp-margeta": [
    -2.9585578441619873,
    -1.7615150213241577,
    -0.32151558995246887,
    2.1343889236450195,
    2.4801902770996094
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.841794375,
   "hydro-lnL-imos-margeta": 0.8417990625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8417965625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8417909375,
   "hydro-lnL-ims-proxy-margeta": 0.86682375,
   "hydro-lnL-imos-amp-margeta": 0.8417990625
  },
  "scored_any_share": 0.8668475,
  "seconds": 444.0708248615265,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.1988525390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.141300201416016,
    -8.152032852172852,
    -0.11051154136657715,
    2.676419258117676,
    3.501790761947632
   ],
   "hydro-lnL-imos-margeta": [
    -3.250378370285034,
    -1.9139662981033325,
    -0.353373646736145,
    2.5146610736846924,
    3.1835808753967285
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.072072982788086,
    -1.7355350255966187,
    -0.18595698475837708,
    2.2880494594573975,
    3.1130330562591553
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.854642868041992,
    -1.5181679725646973,
    -0.05073554441332817,
    1.9078600406646729,
    3.0014901161193848
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.128055572509766,
    -2.725634813308716,
    -0.4697189927101135,
    0.5788494944572449,
    1.6936960220336914
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2571442127227783,
    -1.917445421218872,
    -0.35521528124809265,
    2.1188511848449707,
    2.511312246322632
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8186434989349893,
   "hydro-lnL-imos-margeta": 0.8186878743787438,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8186584990849909,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8186328738287383,
   "hydro-lnL-ims-proxy-margeta": 0.8531538440384404,
   "hydro-lnL-imos-amp-margeta": 0.8186825618256183
  },
  "scored_any_share": 0.8532647826478265,
  "seconds": 442.5749671459198,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.00811767578125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.977788925170898,
    -7.9593377113342285,
    -0.11727673560380936,
    2.995272636413574,
    3.507202625274658
   ],
   "hydro-lnL-imos-margeta": [
    -3.230085849761963,
    -1.8987390995025635,
    -0.3594678044319153,
    2.703395366668701,
    3.225612163543701
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0517325401306152,
    -1.7210497856140137,
    -0.19164404273033142,
    2.5184621810913086,
    3.1647140979766846
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8343257904052734,
    -1.5041898488998413,
    -0.0534219890832901,
    2.216686725616455,
    3.073406934738159
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.59776496887207,
    -2.999114751815796,
    -0.5459173917770386,
    0.6092730760574341,
    1.7423580884933472
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.235212802886963,
    -1.9053677320480347,
    -0.36213743686676025,
    2.273336410522461,
    2.4938580989837646
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.898915625,
   "hydro-lnL-imos-margeta": 0.8989534375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8989265625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.898903125,
   "hydro-lnL-ims-proxy-margeta": 0.938408125,
   "hydro-lnL-imos-amp-margeta": 0.8989496875
  },
  "scored_any_share": 0.9384928125,
  "seconds": 449.18802309036255,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.93182373046875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.746933937072754,
    -7.694344520568848,
    -0.12001444399356842,
    2.9252419471740723,
    3.506024122238159
   ],
   "hydro-lnL-imos-margeta": [
    -3.217906951904297,
    -1.8931320905685425,
    -0.3615894913673401,
    2.66084361076355,
    3.211155414581299
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.039883852005005,
    -1.7149609327316284,
    -0.1936246156692505,
    2.463996410369873,
    3.148266315460205
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.822399854660034,
    -1.4984321594238281,
    -0.054467443376779556,
    2.133359432220459,
    3.051344633102417
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.661458969116211,
    -3.026881217956543,
    -0.5446667075157166,
    0.652750551700592,
    1.7272692918777466
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2247886657714844,
    -1.8982750177383423,
    -0.3638674020767212,
    2.2489895820617676,
    2.498431444168091
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8927125,
   "hydro-lnL-imos-margeta": 0.892758125,
   "hydro-lnL-imos-margeta-ub1e-1": 0.892728125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8927028125,
   "hydro-lnL-ims-proxy-margeta": 0.93482375,
   "hydro-lnL-imos-amp-margeta": 0.8927459375
  },
  "scored_any_share": 0.93488125,
  "seconds": 449.51605200767517,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.77923583984375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.576842308044434,
    -7.521451473236084,
    -0.09981641173362732,
    2.820166826248169,
    3.496741533279419
   ],
   "hydro-lnL-imos-margeta": [
    -3.1280112266540527,
    -1.8397982120513916,
    -0.34335339069366455,
    2.5960891246795654,
    3.192887306213379
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.950779914855957,
    -1.6616320610046387,
    -0.17701546847820282,
    2.3854596614837646,
    3.12612247467041
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.733712911605835,
    -1.4446073770523071,
    -0.046515002846717834,
    2.034921169281006,
    3.0247230529785156
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.646938323974609,
    -2.9765055179595947,
    -0.5085428953170776,
    0.5429697036743164,
    1.7042518854141235
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.136320114135742,
    -1.8443777561187744,
    -0.34536024928092957,
    2.198333978652954,
    2.49509334564209
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.86207375,
   "hydro-lnL-imos-margeta": 0.8620915625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8620790625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.862065625,
   "hydro-lnL-ims-proxy-margeta": 0.8949453125,
   "hydro-lnL-imos-amp-margeta": 0.86209125
  },
  "scored_any_share": 0.89503625,
  "seconds": 456.0281112194061,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.7410888671875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.606740951538086,
    -7.633227348327637,
    -0.08903136849403381,
    2.846935987472534,
    3.494478464126587
   ],
   "hydro-lnL-imos-margeta": [
    -3.095367431640625,
    -1.8363926410675049,
    -0.3320256173610687,
    2.6126506328582764,
    3.190150022506714
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9175400733947754,
    -1.658280849456787,
    -0.16701412200927734,
    2.403798818588257,
    3.121157169342041
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7014670372009277,
    -1.4412307739257812,
    -0.04205255210399628,
    2.0554213523864746,
    3.0147578716278076
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.548439979553223,
    -2.9419612884521484,
    -0.5020194053649902,
    0.5664874315261841,
    1.6712157726287842
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1020865440368652,
    -1.841651201248169,
    -0.334333598613739,
    2.212501049041748,
    2.4965977668762207
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.844994375,
   "hydro-lnL-imos-margeta": 0.84501625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8449990625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8449846875,
   "hydro-lnL-ims-proxy-margeta": 0.87827875,
   "hydro-lnL-imos-amp-margeta": 0.84501375
  },
  "scored_any_share": 0.878326875,
  "seconds": 457.09864377975464,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 12.62664794921875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.824972152709961,
    -7.817763328552246,
    -0.11634741723537445,
    2.970557451248169,
    3.514556646347046
   ],
   "hydro-lnL-imos-margeta": [
    -3.2388522624969482,
    -1.9011249542236328,
    -0.3583378195762634,
    2.6911888122558594,
    3.2309775352478027
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.060622215270996,
    -1.722938060760498,
    -0.1906864047050476,
    2.501035213470459,
    3.1709346771240234
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8447797298431396,
    -1.5066593885421753,
    -0.05305735021829605,
    2.1882410049438477,
    3.0796103477478027
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.457000732421875,
    -2.928379535675049,
    -0.5224719643592834,
    0.6550978422164917,
    1.714980959892273
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2472667694091797,
    -1.907598614692688,
    -0.36080610752105713,
    2.266639232635498,
    2.5079619884490967
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8722484375,
   "hydro-lnL-imos-margeta": 0.8722725,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8722559375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8722396875,
   "hydro-lnL-ims-proxy-margeta": 0.910833125,
   "hydro-lnL-imos-amp-margeta": 0.872268125
  },
  "scored_any_share": 0.910903125,
  "seconds": 459.6280541419983,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.2587890625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.84531021118164,
    -7.827272415161133,
    -0.11343406140804291,
    2.8684515953063965,
    3.5095903873443604
   ],
   "hydro-lnL-imos-margeta": [
    -3.258134126663208,
    -1.920377492904663,
    -0.3544018268585205,
    2.629094123840332,
    3.2115297317504883
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.080623149871826,
    -1.7425522804260254,
    -0.1872916966676712,
    2.422407865524292,
    3.1459643840789795
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8666269779205322,
    -1.5255520343780518,
    -0.05177774652838707,
    2.0811727046966553,
    3.047705888748169
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.443817615509033,
    -2.9151816368103027,
    -0.5309795141220093,
    0.6502704620361328,
    1.7102206945419312
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.270892381668091,
    -1.926202416419983,
    -0.35669994354248047,
    2.2220098972320557,
    2.5042216777801514
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8609626721267213,
   "hydro-lnL-imos-margeta": 0.8611286112861128,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8610114226142261,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8608811088110881,
   "hydro-lnL-ims-proxy-margeta": 0.9322568225682257,
   "hydro-lnL-imos-amp-margeta": 0.8611179861798618
  },
  "scored_any_share": 0.9323683861838619,
  "seconds": 507.4780418872833,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.30511474609375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.800025939941406,
    -7.785097122192383,
    -0.12064855545759201,
    2.9828944206237793,
    3.511021137237549
   ],
   "hydro-lnL-imos-margeta": [
    -3.22182297706604,
    -1.90260648727417,
    -0.36179274320602417,
    2.69648814201355,
    3.22430157661438
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.043886661529541,
    -1.7245219945907593,
    -0.19382336735725403,
    2.5091915130615234,
    3.162787675857544
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.826371192932129,
    -1.508569598197937,
    -0.054728567600250244,
    2.201742172241211,
    3.0708577632904053
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.540571689605713,
    -2.987337827682495,
    -0.5421743392944336,
    0.6612774729728699,
    1.750012993812561
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.228367805480957,
    -1.9087963104248047,
    -0.3642650842666626,
    2.2708895206451416,
    2.5029242038726807
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8883153125,
   "hydro-lnL-imos-margeta": 0.8883465625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8883228125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8883040625,
   "hydro-lnL-ims-proxy-margeta": 0.9288665625,
   "hydro-lnL-imos-amp-margeta": 0.888343125
  },
  "scored_any_share": 0.9289315625,
  "seconds": 475.13737416267395,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.22882080078125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.879437446594238,
    -7.890514850616455,
    -0.11684650927782059,
    2.929084539413452,
    3.512230634689331
   ],
   "hydro-lnL-imos-margeta": [
    -3.2207727432250977,
    -1.8951010704040527,
    -0.35912108421325684,
    2.6648101806640625,
    3.2215750217437744
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.042289972305298,
    -1.7171282768249512,
    -0.19125822186470032,
    2.467615842819214,
    3.1597588062286377
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8243203163146973,
    -1.5001450777053833,
    -0.053281575441360474,
    2.141547203063965,
    3.0636916160583496
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.529170513153076,
    -2.9667575359344482,
    -0.5271358489990234,
    0.6960219144821167,
    1.7310537099838257
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2276933193206787,
    -1.9003651142120361,
    -0.3614513874053955,
    2.2483248710632324,
    2.5053205490112305
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8771784157158429,
   "hydro-lnL-imos-margeta": 0.8772084154158458,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8771871656283438,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8771687283127169,
   "hydro-lnL-ims-proxy-margeta": 0.9142017954820452,
   "hydro-lnL-imos-amp-margeta": 0.8772027904720953
  },
  "scored_any_share": 0.9142496075039249,
  "seconds": 478.1999180316925,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.1143798828125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.4937744140625,
    -7.649023532867432,
    -0.1048804298043251,
    2.914475679397583,
    3.501293897628784
   ],
   "hydro-lnL-imos-margeta": [
    -3.0930986404418945,
    -1.8307193517684937,
    -0.3481834828853607,
    2.6509456634521484,
    3.206026077270508
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.914842367172241,
    -1.652788519859314,
    -0.18137428164482117,
    2.4551830291748047,
    3.139981985092163
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.6984729766845703,
    -1.4358100891113281,
    -0.04847606644034386,
    2.128119468688965,
    3.0423858165740967
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.81308126449585,
    -3.1055750846862793,
    -0.5374428033828735,
    0.6889668703079224,
    1.7045855522155762
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.100194215774536,
    -1.8360254764556885,
    -0.3503955602645874,
    2.2367706298828125,
    2.492694139480591
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8900325,
   "hydro-lnL-imos-margeta": 0.890055625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8900378125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.890025625,
   "hydro-lnL-ims-proxy-margeta": 0.9215978125,
   "hydro-lnL-imos-amp-margeta": 0.8900540625
  },
  "scored_any_share": 0.921633125,
  "seconds": 481.36085200309753,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.84735107421875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.547341346740723,
    -7.5956525802612305,
    -0.11763519048690796,
    3.0248703956604004,
    3.511730909347534
   ],
   "hydro-lnL-imos-margeta": [
    -3.2100982666015625,
    -1.8856112957000732,
    -0.3595265746116638,
    2.723041534423828,
    3.2318694591522217
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0321590900421143,
    -1.7076243162155151,
    -0.19186991453170776,
    2.5419976711273193,
    3.1722302436828613
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.815558433532715,
    -1.4912701845169067,
    -0.05358268693089485,
    2.2459092140197754,
    3.080002546310425
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.506974220275879,
    -2.956876516342163,
    -0.5430958271026611,
    0.6287760734558105,
    1.7023452520370483
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.220003128051758,
    -1.8928889036178589,
    -0.3622470200061798,
    2.2885146141052246,
    2.5008347034454346
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8935084375,
   "hydro-lnL-imos-margeta": 0.8935396875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8935153125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.89349875,
   "hydro-lnL-ims-proxy-margeta": 0.9313696875,
   "hydro-lnL-imos-amp-margeta": 0.8935353125
  },
  "scored_any_share": 0.9314296875,
  "seconds": 493.90110993385315,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.9617919921875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.65188217163086,
    -7.7165069580078125,
    -0.0934312492609024,
    2.863396167755127,
    3.5047249794006348
   ],
   "hydro-lnL-imos-margeta": [
    -3.166329860687256,
    -1.8671584129333496,
    -0.3367558419704437,
    2.6248226165771484,
    3.209059953689575
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9879631996154785,
    -1.689411997795105,
    -0.17122256755828857,
    2.416332960128784,
    3.1446921825408936
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7717270851135254,
    -1.4727286100387573,
    -0.043908193707466125,
    2.075777769088745,
    3.0446317195892334
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.345005989074707,
    -2.862396001815796,
    -0.4892479181289673,
    0.5900657176971436,
    1.6895084381103516
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1764469146728516,
    -1.8729965686798096,
    -0.3390425145626068,
    2.2169783115386963,
    2.5017316341400146
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8357916420835791,
   "hydro-lnL-imos-margeta": 0.8358116418835811,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8357972670273297,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8357844546554535,
   "hydro-lnL-ims-proxy-margeta": 0.8696222412775872,
   "hydro-lnL-imos-amp-margeta": 0.8358091419085809
  },
  "scored_any_share": 0.8697213027869721,
  "seconds": 483.3571038246155,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.77105712890625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.055375099182129,
    -7.1454925537109375,
    -0.08118775486946106,
    2.9035372734069824,
    3.5010619163513184
   ],
   "hydro-lnL-imos-margeta": [
    -2.993420362472534,
    -1.7678946256637573,
    -0.3248899579048157,
    2.646047353744507,
    3.1983046531677246
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.815669059753418,
    -1.590078353881836,
    -0.16048356890678406,
    2.445587635040283,
    3.13096022605896
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.5999910831451416,
    -1.373343586921692,
    -0.038938622921705246,
    2.111701250076294,
    3.0296547412872314
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.845489501953125,
    -3.148169755935669,
    -0.5227700471878052,
    0.6358245015144348,
    2.021855115890503
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.00366473197937,
    -1.7733585834503174,
    -0.32700833678245544,
    2.240504503250122,
    2.4982802867889404
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8683841286587134,
   "hydro-lnL-imos-margeta": 0.868409753402466,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8683931910680893,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8683763162368376,
   "hydro-lnL-ims-proxy-margeta": 0.9080052949470505,
   "hydro-lnL-imos-amp-margeta": 0.8684075659243408
  },
  "scored_any_share": 0.9080477945220548,
  "seconds": 488.42048811912537,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.69476318359375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.641278266906738,
    -7.702741622924805,
    -0.0997459888458252,
    2.8158071041107178,
    3.50034761428833
   ],
   "hydro-lnL-imos-margeta": [
    -3.1470274925231934,
    -1.8577120304107666,
    -0.3425067961215973,
    2.599116563796997,
    3.1918156147003174
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.96929931640625,
    -1.679648518562317,
    -0.1763562113046646,
    2.3820719718933105,
    3.1226444244384766
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7524235248565674,
    -1.4629361629486084,
    -0.04640721529722214,
    2.019812822341919,
    3.019366502761841
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.570158958435059,
    -2.980569362640381,
    -0.5224116444587708,
    0.5853372812271118,
    1.8086408376693726
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.156390905380249,
    -1.8625643253326416,
    -0.34465980529785156,
    2.2056806087493896,
    2.496553421020508
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8500978759787597,
   "hydro-lnL-imos-margeta": 0.8502453774537745,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8501363138631386,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8500510005100052,
   "hydro-lnL-ims-proxy-margeta": 0.9059959349593496,
   "hydro-lnL-imos-amp-margeta": 0.8502331898318983
  },
  "scored_any_share": 0.9061190611906119,
  "seconds": 488.7487256526947,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.580322265625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.894131660461426,
    -7.8776984214782715,
    -0.11439984291791916,
    3.0323896408081055,
    3.51499080657959
   ],
   "hydro-lnL-imos-margeta": [
    -3.262383222579956,
    -1.911962628364563,
    -0.35564276576042175,
    2.7264487743377686,
    3.2293710708618164
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0844781398773193,
    -1.7339307069778442,
    -0.18840226531028748,
    2.5474472045898438,
    3.168255090713501
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8667328357696533,
    -1.5173088312149048,
    -0.052204713225364685,
    2.253519296646118,
    3.0757133960723877
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.442437648773193,
    -2.9251348972320557,
    -0.5335879921913147,
    0.6582027077674866,
    1.6929988861083984
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.270934820175171,
    -1.9182956218719482,
    -0.35839778184890747,
    2.292391538619995,
    2.5086286067962646
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.882893125,
   "hydro-lnL-imos-margeta": 0.8829540625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.882916875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8828653125,
   "hydro-lnL-ims-proxy-margeta": 0.9282990625,
   "hydro-lnL-imos-amp-margeta": 0.8829515625
  },
  "scored_any_share": 0.928365,
  "seconds": 492.0012242794037,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 13.5040283203125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.931594848632812,
    -7.872066497802734,
    -0.11818134039640427,
    2.9363813400268555,
    3.520817995071411
   ],
   "hydro-lnL-imos-margeta": [
    -3.2718327045440674,
    -1.930533528327942,
    -0.35928064584732056,
    2.6685969829559326,
    3.238100290298462
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.093677520751953,
    -1.752449631690979,
    -0.19154183566570282,
    2.4755210876464844,
    3.176312208175659
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.875906229019165,
    -1.5357286930084229,
    -0.053688906133174896,
    2.159965753555298,
    3.0843663215637207
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.441767692565918,
    -2.9185421466827393,
    -0.5245623588562012,
    0.6822746992111206,
    1.7155044078826904
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2772631645202637,
    -1.9366817474365234,
    -0.3616204559803009,
    2.2447350025177,
    2.512263774871826
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8643007319926801,
   "hydro-lnL-imos-margeta": 0.8643432315676843,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8643147943520565,
   "hydro-lnL-imos-margeta-ub1e-2": 0.864289794602054,
   "hydro-lnL-ims-proxy-margeta": 0.921209225407746,
   "hydro-lnL-imos-amp-margeta": 0.8643357316426836
  },
  "scored_any_share": 0.9212976620233798,
  "seconds": 487.3921329975128,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.14434814453125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.650215148925781,
    -7.674021244049072,
    -0.1196359246969223,
    3.0038866996765137,
    3.5109152793884277
   ],
   "hydro-lnL-imos-margeta": [
    -3.1928300857543945,
    -1.8884787559509277,
    -0.36050736904144287,
    2.710468053817749,
    3.225681781768799
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0140140056610107,
    -1.7104028463363647,
    -0.19281744956970215,
    2.526817798614502,
    3.166167974472046
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7959208488464355,
    -1.4937338829040527,
    -0.05427411198616028,
    2.22438645362854,
    3.0746638774871826
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.536954879760742,
    -2.994535446166992,
    -0.5506813526153564,
    0.6568377017974854,
    1.7096489667892456
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1973209381103516,
    -1.8953094482421875,
    -0.36300283670425415,
    2.2807390689849854,
    2.5012600421905518
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8961988505114948,
   "hydro-lnL-imos-margeta": 0.8962407250927491,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8962116628833712,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8961866631333687,
   "hydro-lnL-ims-proxy-margeta": 0.9400177873221268,
   "hydro-lnL-imos-amp-margeta": 0.8962376001239988
  },
  "scored_any_share": 0.9400880991190088,
  "seconds": 506.0787799358368,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.06805419921875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.469078063964844,
    -7.642510414123535,
    -0.12160622328519821,
    3.0586464405059814,
    3.511575698852539
   ],
   "hydro-lnL-imos-margeta": [
    -3.240933418273926,
    -1.9129233360290527,
    -0.36151283979415894,
    2.7445926666259766,
    3.233907699584961
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0647006034851074,
    -1.7357689142227173,
    -0.19403401017189026,
    2.5751869678497314,
    3.1762008666992188
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8486948013305664,
    -1.5199865102767944,
    -0.05503028631210327,
    2.3031556606292725,
    3.089116096496582
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.544182777404785,
    -2.9910781383514404,
    -0.5491251945495605,
    0.6445187330245972,
    1.6918091773986816
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2567250728607178,
    -1.9218254089355469,
    -0.36472460627555847,
    2.2997593879699707,
    2.4998037815093994
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.906619375,
   "hydro-lnL-imos-margeta": 0.906658125,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9066275,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9066075,
   "hydro-lnL-ims-proxy-margeta": 0.94387,
   "hydro-lnL-imos-amp-margeta": 0.9066525
  },
  "scored_any_share": 0.943935,
  "seconds": 505.7064621448517,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.99176025390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.886652946472168,
    -7.903327465057373,
    -0.13244815170764923,
    2.964170455932617,
    3.5185353755950928
   ],
   "hydro-lnL-imos-margeta": [
    -3.254984140396118,
    -1.9328665733337402,
    -0.3713356554508209,
    2.6885082721710205,
    3.2311816215515137
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.078186511993408,
    -1.7546511888504028,
    -0.20254938304424286,
    2.4988582134246826,
    3.1686525344848633
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8610007762908936,
    -1.5378530025482178,
    -0.05920263007283211,
    2.187568187713623,
    3.0768544673919678
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.506932258605957,
    -2.9555583000183105,
    -0.5395990610122681,
    0.6774481534957886,
    1.7461867332458496
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.266136884689331,
    -1.9383518695831299,
    -0.3737621307373047,
    2.265109062194824,
    2.511472702026367
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8884484375,
   "hydro-lnL-imos-margeta": 0.8884909375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8884603125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.88843875,
   "hydro-lnL-ims-proxy-margeta": 0.9289759375,
   "hydro-lnL-imos-amp-margeta": 0.888484375
  },
  "scored_any_share": 0.9290409375,
  "seconds": 502.22165298461914,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.8773193359375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.809967041015625,
    -7.788447856903076,
    -0.1304280161857605,
    2.9730024337768555,
    3.5153608322143555
   ],
   "hydro-lnL-imos-margeta": [
    -3.253268241882324,
    -1.9254786968231201,
    -0.36930063366889954,
    2.6925244331359863,
    3.2320396900177
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0756797790527344,
    -1.7472666501998901,
    -0.20075999200344086,
    2.503513813018799,
    3.170027256011963
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8589327335357666,
    -1.5304831266403198,
    -0.05839570611715317,
    2.190237045288086,
    3.078490734100342
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.552906513214111,
    -2.976055383682251,
    -0.5437577962875366,
    0.6741424798965454,
    1.7231618165969849
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2594592571258545,
    -1.930985450744629,
    -0.37167418003082275,
    2.2718093395233154,
    2.5082008838653564
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.888490625,
   "hydro-lnL-imos-margeta": 0.8885446875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.888505625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8884721875,
   "hydro-lnL-ims-proxy-margeta": 0.933816875,
   "hydro-lnL-imos-amp-margeta": 0.88853375
  },
  "scored_any_share": 0.933895,
  "seconds": 502.17141819000244,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.801025390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.620596885681152,
    -7.596791744232178,
    -0.12080897390842438,
    2.915443181991577,
    3.497702121734619
   ],
   "hydro-lnL-imos-margeta": [
    -3.1656041145324707,
    -1.8772227764129639,
    -0.36213546991348267,
    2.6543033123016357,
    3.204725503921509
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9879190921783447,
    -1.6991223096847534,
    -0.1939581334590912,
    2.456068515777588,
    3.139589309692383
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.771082878112793,
    -1.4821505546569824,
    -0.05471200495958328,
    2.126662015914917,
    3.04093074798584
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.784576892852783,
    -3.0977578163146973,
    -0.5411399006843567,
    0.6668365001678467,
    1.6541454792022705
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.172213315963745,
    -1.8827543258666992,
    -0.36428338289260864,
    2.241773843765259,
    2.4937973022460938
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9047040625,
   "hydro-lnL-imos-margeta": 0.9047365625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.90471375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.90469625,
   "hydro-lnL-ims-proxy-margeta": 0.9408609375,
   "hydro-lnL-imos-amp-margeta": 0.9047328125
  },
  "scored_any_share": 0.9409203125,
  "seconds": 503.60699796676636,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.5721435546875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.917818069458008,
    -7.8941650390625,
    -0.12288734316825867,
    2.915390968322754,
    3.5141518115997314
   ],
   "hydro-lnL-imos-margeta": [
    -3.256443738937378,
    -1.9206970930099487,
    -0.3636654019355774,
    2.657737970352173,
    3.22137451171875
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0796632766723633,
    -1.7426987886428833,
    -0.1954953968524933,
    2.4586336612701416,
    3.156592607498169
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8643674850463867,
    -1.5259778499603271,
    -0.055559396743774414,
    2.128998041152954,
    3.0608859062194824
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.495174407958984,
    -2.9557268619537354,
    -0.5263134241104126,
    0.6604856252670288,
    1.72721266746521
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2692203521728516,
    -1.9261682033538818,
    -0.36601635813713074,
    2.2426135540008545,
    2.5105435848236084
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8745409375,
   "hydro-lnL-imos-margeta": 0.874586875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.874554375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.874525625,
   "hydro-lnL-ims-proxy-margeta": 0.9183765625,
   "hydro-lnL-imos-amp-margeta": 0.87458
  },
  "scored_any_share": 0.91848,
  "seconds": 472.5122740268707,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.4195556640625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.72517204284668,
    -7.720279693603516,
    -0.10607235878705978,
    2.8659799098968506,
    3.505021095275879
   ],
   "hydro-lnL-imos-margeta": [
    -3.183182716369629,
    -1.8761212825775146,
    -0.34881794452667236,
    2.6259546279907227,
    3.200455904006958
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.004657745361328,
    -1.6980568170547485,
    -0.18212561309337616,
    2.4214909076690674,
    3.1328659057617188
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7872278690338135,
    -1.48113214969635,
    -0.04899575561285019,
    2.08034086227417,
    3.031578302383423
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.486854076385498,
    -2.916444778442383,
    -0.510770320892334,
    0.617792010307312,
    1.728751540184021
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.192216157913208,
    -1.881232500076294,
    -0.35100069642066956,
    2.221651792526245,
    2.5048439502716064
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.85756375,
   "hydro-lnL-imos-margeta": 0.857596875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8575728125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.85755125,
   "hydro-lnL-ims-proxy-margeta": 0.8979278125,
   "hydro-lnL-imos-amp-margeta": 0.857594375
  },
  "scored_any_share": 0.898010625,
  "seconds": 471.5777339935303,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 14.495849609375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.578267097473145,
    -7.518770217895508,
    -0.08434686064720154,
    2.9914944171905518,
    3.5061850547790527
   ],
   "hydro-lnL-imos-margeta": [
    -3.089799404144287,
    -1.8190052509307861,
    -0.3276519775390625,
    2.700432777404785,
    3.2268309593200684
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9138576984405518,
    -1.6413540840148926,
    -0.16313263773918152,
    2.518200159072876,
    3.167147397994995
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.698077917098999,
    -1.4252554178237915,
    -0.04021146520972252,
    2.2237260341644287,
    3.0774362087249756
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.477716445922852,
    -2.9172356128692627,
    -0.4908835291862488,
    0.5467633605003357,
    1.6598132848739624
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1048972606658936,
    -1.8269470930099487,
    -0.3303821086883545,
    2.2648367881774902,
    2.493866443634033
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8466759667596676,
   "hydro-lnL-imos-margeta": 0.8466987794877949,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8466822168221683,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8466722167221672,
   "hydro-lnL-ims-proxy-margeta": 0.8792922304223042,
   "hydro-lnL-imos-amp-margeta": 0.8466944044440444
  },
  "scored_any_share": 0.8793322308223083,
  "seconds": 469.8214509487152,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.94000244140625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.824348449707031,
    -7.752869606018066,
    -0.11133307218551636,
    2.8920207023620605,
    3.5054407119750977
   ],
   "hydro-lnL-imos-margeta": [
    -3.1996641159057617,
    -1.8809715509414673,
    -0.353049635887146,
    2.6420114040374756,
    3.2061398029327393
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.021117687225342,
    -1.703015685081482,
    -0.1859942376613617,
    2.4387359619140625,
    3.1411468982696533
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8031749725341797,
    -1.4862110614776611,
    -0.051000941544771194,
    2.1067917346954346,
    3.0418522357940674
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.548052787780762,
    -2.952066421508789,
    -0.5278850793838501,
    0.6162115335464478,
    1.7298287153244019
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.206890344619751,
    -1.8863052129745483,
    -0.3553090989589691,
    2.2320339679718018,
    2.5003104209899902
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8702221397213972,
   "hydro-lnL-imos-margeta": 0.870260265102651,
   "hydro-lnL-imos-margeta-ub1e-1": 0.870230577305773,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8702130771307713,
   "hydro-lnL-ims-proxy-margeta": 0.9162960379603796,
   "hydro-lnL-imos-amp-margeta": 0.8702552650526505
  },
  "scored_any_share": 0.916369476194762,
  "seconds": 475.4872570037842,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 21.1334228515625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.602585792541504,
    -7.624948024749756,
    -0.12244972586631775,
    3.014477252960205,
    3.5145230293273926
   ],
   "hydro-lnL-imos-margeta": [
    -3.229353666305542,
    -1.8981354236602783,
    -0.36281898617744446,
    2.7159042358398438,
    3.2331764698028564
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.053309202194214,
    -1.7202078104019165,
    -0.1948724389076233,
    2.5351943969726562,
    3.1761631965637207
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.837661027908325,
    -1.503426432609558,
    -0.05534046143293381,
    2.235154151916504,
    3.086578845977783
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.612484455108643,
    -2.982693672180176,
    -0.5472159385681152,
    0.653236448764801,
    1.7590138912200928
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.245788097381592,
    -1.9035232067108154,
    -0.3652269244194031,
    2.286323070526123,
    2.504762887954712
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8936510634893651,
   "hydro-lnL-imos-margeta": 0.8937420000799992,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8936748132518675,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8936241887581124,
   "hydro-lnL-ims-proxy-margeta": 0.9372953145468546,
   "hydro-lnL-imos-amp-margeta": 0.8937266877331227
  },
  "scored_any_share": 0.9373990635093649,
  "seconds": 470.3684570789337,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 21.05712890625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.822731971740723,
    -7.786776542663574,
    -0.1181819885969162,
    2.9841015338897705,
    3.509965658187866
   ],
   "hydro-lnL-imos-margeta": [
    -3.230814218521118,
    -1.9002054929733276,
    -0.3594801127910614,
    2.696000099182129,
    3.222050428390503
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.052558422088623,
    -1.7223963737487793,
    -0.1918121576309204,
    2.5103070735931396,
    3.159449338912964
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8372271060943604,
    -1.5060585737228394,
    -0.053730558604002,
    2.2007558345794678,
    3.068221092224121
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.585919380187988,
    -2.997054100036621,
    -0.5420989990234375,
    0.6581015586853027,
    1.7282685041427612
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2395684719085693,
    -1.9072514772415161,
    -0.3620203137397766,
    2.270324945449829,
    2.501443386077881
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8898921875,
   "hydro-lnL-imos-margeta": 0.8899234375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.88990375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.889884375,
   "hydro-lnL-ims-proxy-margeta": 0.930285625,
   "hydro-lnL-imos-amp-margeta": 0.88991875
  },
  "scored_any_share": 0.9303746875,
  "seconds": 469.34586811065674,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.9808349609375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.640541076660156,
    -7.631704330444336,
    -0.11322104185819626,
    2.9861650466918945,
    3.5098748207092285
   ],
   "hydro-lnL-imos-margeta": [
    -3.2071313858032227,
    -1.8754268884658813,
    -0.35502126812934875,
    2.6981663703918457,
    3.2249257564544678
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0315356254577637,
    -1.6973620653152466,
    -0.18778160214424133,
    2.5111758708953857,
    3.1644108295440674
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.814117431640625,
    -1.4804612398147583,
    -0.05180278420448303,
    2.204488515853882,
    3.072730779647827
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.526073455810547,
    -2.9595160484313965,
    -0.534887433052063,
    0.6141709685325623,
    1.7347091436386108
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.216362714767456,
    -1.880915641784668,
    -0.3575327396392822,
    2.274005174636841,
    2.4991137981414795
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8807015625,
   "hydro-lnL-imos-margeta": 0.88073875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.880715625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8806871875,
   "hydro-lnL-ims-proxy-margeta": 0.920135,
   "hydro-lnL-imos-amp-margeta": 0.880730625
  },
  "scored_any_share": 0.92021375,
  "seconds": 467.74995708465576,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.86639404296875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.806812286376953,
    -7.755020618438721,
    -0.10130302608013153,
    2.8391783237457275,
    3.5010738372802734
   ],
   "hydro-lnL-imos-margeta": [
    -3.1942477226257324,
    -1.8732357025146484,
    -0.34390953183174133,
    2.610873222351074,
    3.196448564529419
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0163121223449707,
    -1.6949405670166016,
    -0.1776137351989746,
    2.4015164375305176,
    3.1305627822875977
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.801490306854248,
    -1.4779455661773682,
    -0.04704843461513519,
    2.0501489639282227,
    3.029324531555176
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.365099906921387,
    -2.8640739917755127,
    -0.5028693675994873,
    0.5789062976837158,
    1.7343088388442993
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.201687812805176,
    -1.8782620429992676,
    -0.3460986912250519,
    2.2071332931518555,
    2.497891902923584
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.841209662096621,
   "hydro-lnL-imos-margeta": 0.8412768502685027,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8412287247872479,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8411877868778688,
   "hydro-lnL-ims-proxy-margeta": 0.8855841683416834,
   "hydro-lnL-imos-amp-margeta": 0.8412690376903769
  },
  "scored_any_share": 0.8857138571385714,
  "seconds": 462.90362095832825,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.79010009765625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.490777969360352,
    -7.538777828216553,
    -0.08475744724273682,
    2.9597175121307373,
    3.5051844120025635
   ],
   "hydro-lnL-imos-margeta": [
    -3.1889829635620117,
    -1.8642394542694092,
    -0.32637280225753784,
    2.6795971393585205,
    3.2159528732299805
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0110690593719482,
    -1.6862237453460693,
    -0.16229745745658875,
    2.49037504196167,
    3.154553174972534
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7937824726104736,
    -1.4694809913635254,
    -0.040248773992061615,
    2.181400775909424,
    3.0627779960632324
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.452254772186279,
    -2.9243927001953125,
    -0.5054256916046143,
    0.6114242672920227,
    1.6928582191467285
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1954874992370605,
    -1.8703633546829224,
    -0.32906338572502136,
    2.2550878524780273,
    2.498290777206421
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8383418209182092,
   "hydro-lnL-imos-margeta": 0.8383824463244632,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8383530710307103,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8383286957869579,
   "hydro-lnL-ims-proxy-margeta": 0.8824719497194972,
   "hydro-lnL-imos-amp-margeta": 0.8383730712307123
  },
  "scored_any_share": 0.8825610131101311,
  "seconds": 461.62484669685364,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.3704833984375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.46513843536377,
    -7.517717361450195,
    -0.10653290152549744,
    2.9507999420166016,
    3.5019075870513916
   ],
   "hydro-lnL-imos-margeta": [
    -3.14490008354187,
    -1.8588446378707886,
    -0.34904712438583374,
    2.673957586288452,
    3.207353115081787
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9665935039520264,
    -1.6811110973358154,
    -0.18229492008686066,
    2.4827382564544678,
    3.1425869464874268
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7487411499023438,
    -1.4642947912216187,
    -0.049109019339084625,
    2.164902687072754,
    3.0477797985076904
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.600029945373535,
    -3.0075831413269043,
    -0.5392433404922485,
    0.6244744062423706,
    1.7195625305175781
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.151102304458618,
    -1.8642828464508057,
    -0.351434588432312,
    2.257848024368286,
    2.493985891342163
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8833089794102059,
   "hydro-lnL-imos-margeta": 0.8834005409945901,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8833367916320837,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8832708547914521,
   "hydro-lnL-ims-proxy-margeta": 0.9262726122738772,
   "hydro-lnL-imos-amp-margeta": 0.8833886661133389
  },
  "scored_any_share": 0.9263447990520095,
  "seconds": 293.70838499069214,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.294189453125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.091054916381836,
    -8.058035850524902,
    -0.10978713631629944,
    2.8241896629333496,
    3.502258777618408
   ],
   "hydro-lnL-imos-margeta": [
    -3.3425846099853516,
    -1.94036865234375,
    -0.351911723613739,
    2.6017439365386963,
    3.196713924407959
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.163539171218872,
    -1.7621499300003052,
    -0.18490242958068848,
    2.3916361331939697,
    3.129117012023926
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.9460699558258057,
    -1.5448576211929321,
    -0.050403960049152374,
    2.0370874404907227,
    3.0255274772644043
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.389115333557129,
    -2.891171455383301,
    -0.5143545866012573,
    0.6067326664924622,
    1.7346421480178833
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.3472795486450195,
    -1.9449907541275024,
    -0.3542509078979492,
    2.2017874717712402,
    2.499768018722534
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8468372183721837,
   "hydro-lnL-imos-margeta": 0.8469137816378164,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8468609686096861,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8468090930909309,
   "hydro-lnL-ims-proxy-margeta": 0.8952933279332793,
   "hydro-lnL-imos-amp-margeta": 0.8469047190471904
  },
  "scored_any_share": 0.8954467669676697,
  "seconds": 286.72599601745605,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.86370849609375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.739509582519531,
    -7.732793807983398,
    -0.12028475105762482,
    2.9561209678649902,
    3.5101728439331055
   ],
   "hydro-lnL-imos-margeta": [
    -3.259056806564331,
    -1.909078598022461,
    -0.3605921268463135,
    2.6821420192718506,
    3.217865467071533
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0822858810424805,
    -1.731125831604004,
    -0.19290637969970703,
    2.489011287689209,
    3.1544289588928223
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.865602731704712,
    -1.5144177675247192,
    -0.05448642373085022,
    2.173508405685425,
    3.0580227375030518
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.511638641357422,
    -2.9485630989074707,
    -0.5446751117706299,
    0.6406694054603577,
    1.7427724599838257
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2701849937438965,
    -1.9150792360305786,
    -0.3631252646446228,
    2.2627315521240234,
    2.5026919841766357
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8803347408474085,
   "hydro-lnL-imos-margeta": 0.8804559920599206,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8803684911849119,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8802928654286543,
   "hydro-lnL-ims-proxy-margeta": 0.9320624456244563,
   "hydro-lnL-imos-amp-margeta": 0.8804381793817938
  },
  "scored_any_share": 0.9322015095150952,
  "seconds": 482.94255900382996,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.63482666015625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.867555618286133,
    -7.795351982116699,
    -0.10607235133647919,
    2.961569309234619,
    3.5078938007354736
   ],
   "hydro-lnL-imos-margeta": [
    -3.2260162830352783,
    -1.8831545114517212,
    -0.34867584705352783,
    2.6821019649505615,
    3.2176504135131836
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.047166585922241,
    -1.7051914930343628,
    -0.18202003836631775,
    2.493318557739258,
    3.1548590660095215
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8303120136260986,
    -1.488209843635559,
    -0.04896261543035507,
    2.181241035461426,
    3.060328245162964
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.451090335845947,
    -2.916536331176758,
    -0.520695686340332,
    0.5919039845466614,
    1.7160818576812744
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.232957601547241,
    -1.8883817195892334,
    -0.3510206937789917,
    2.259995222091675,
    2.498459577560425
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.862433125,
   "hydro-lnL-imos-margeta": 0.8624715625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.862445,
   "hydro-lnL-imos-margeta-ub1e-2": 0.862423125,
   "hydro-lnL-ims-proxy-margeta": 0.9031,
   "hydro-lnL-imos-amp-margeta": 0.8624653125
  },
  "scored_any_share": 0.9031734375,
  "seconds": 502.6109690666199,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.55853271484375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.880694389343262,
    -7.8499226570129395,
    -0.12345590442419052,
    2.974393844604492,
    3.5139033794403076
   ],
   "hydro-lnL-imos-margeta": [
    -3.257889747619629,
    -1.919385552406311,
    -0.36392515897750854,
    2.693416118621826,
    3.2316837310791016
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.079641819000244,
    -1.7415072917938232,
    -0.19592535495758057,
    2.504164695739746,
    3.1718437671661377
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8626859188079834,
    -1.5247421264648438,
    -0.0557715967297554,
    2.1988978385925293,
    3.0805752277374268
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.545388221740723,
    -2.961118698120117,
    -0.5355801582336426,
    0.6394723057746887,
    1.7247874736785889
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2652175426483154,
    -1.925231695175171,
    -0.3664613366127014,
    2.2664191722869873,
    2.502373695373535
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8776584375,
   "hydro-lnL-imos-margeta": 0.8776965625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8776671875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8776446875,
   "hydro-lnL-ims-proxy-margeta": 0.922071875,
   "hydro-lnL-imos-amp-margeta": 0.8776934375
  },
  "scored_any_share": 0.9221403125,
  "seconds": 504.65567684173584,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.444091796875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.135370254516602,
    -7.929096698760986,
    -0.1037793904542923,
    2.859006881713867,
    3.5081300735473633
   ],
   "hydro-lnL-imos-margeta": [
    -3.311988592147827,
    -1.920973777770996,
    -0.3458596467971802,
    2.625576972961426,
    3.2077760696411133
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.1342430114746094,
    -1.7429932355880737,
    -0.17952975630760193,
    2.41601824760437,
    3.1422536373138428
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.9171977043151855,
    -1.5262675285339355,
    -0.04799345135688782,
    2.068653106689453,
    3.0429065227508545
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.446813583374023,
    -2.902193307876587,
    -0.5112954378128052,
    0.6076738834381104,
    1.7255154848098755
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.3193745613098145,
    -1.9264434576034546,
    -0.3481263518333435,
    2.2240688800811768,
    2.5042548179626465
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8387546875,
   "hydro-lnL-imos-margeta": 0.8388425,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8387834375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8387384375,
   "hydro-lnL-ims-proxy-margeta": 0.8853671875,
   "hydro-lnL-imos-amp-margeta": 0.838825625
  },
  "scored_any_share": 0.8854846875,
  "seconds": 503.92002987861633,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.3677978515625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.689407348632812,
    -7.670107364654541,
    -0.11929753422737122,
    2.9049320220947266,
    3.5021181106567383
   ],
   "hydro-lnL-imos-margeta": [
    -3.199761152267456,
    -1.8842520713806152,
    -0.36075344681739807,
    2.647136688232422,
    3.2011702060699463
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0214948654174805,
    -1.7059675455093384,
    -0.19277304410934448,
    2.4475040435791016,
    3.134824275970459
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8062353134155273,
    -1.488958477973938,
    -0.05415266752243042,
    2.1169724464416504,
    3.0333526134490967
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.664797782897949,
    -3.027289390563965,
    -0.5454786419868469,
    0.6405328512191772,
    1.7972044944763184
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2056257724761963,
    -1.8891003131866455,
    -0.3630165159702301,
    2.238905429840088,
    2.495938539505005
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.893415625,
   "hydro-lnL-imos-margeta": 0.8934659375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8934278125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.893401875,
   "hydro-lnL-ims-proxy-margeta": 0.935486875,
   "hydro-lnL-imos-amp-margeta": 0.893454375
  },
  "scored_any_share": 0.9355678125,
  "seconds": 510.6675820350647,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.29150390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.533539772033691,
    -7.55120849609375,
    -0.10201133787631989,
    2.988535165786743,
    3.5061960220336914
   ],
   "hydro-lnL-imos-margeta": [
    -3.157932996749878,
    -1.856114387512207,
    -0.3445335030555725,
    2.6983110904693604,
    3.221278190612793
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.981005907058716,
    -1.678534746170044,
    -0.17836342751979828,
    2.513232707977295,
    3.1608712673187256
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.762967586517334,
    -1.4622081518173218,
    -0.04735150188207626,
    2.2081058025360107,
    3.0692007541656494
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.5104827880859375,
    -2.9576096534729004,
    -0.5317853689193726,
    0.5884875059127808,
    1.7010719776153564
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1639182567596436,
    -1.863045573234558,
    -0.34712570905685425,
    2.2704644203186035,
    2.4937920570373535
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8769150191501915,
   "hydro-lnL-imos-margeta": 0.8770078325783258,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8769387693876939,
   "hydro-lnL-imos-margeta-ub1e-2": 0.876880643806438,
   "hydro-lnL-ims-proxy-margeta": 0.9215498404984049,
   "hydro-lnL-imos-amp-margeta": 0.8770015825158252
  },
  "scored_any_share": 0.9216026535265353,
  "seconds": 504.52441334724426,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 11.17706298828125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.766863822937012,
    -7.742591857910156,
    -0.10574553906917572,
    2.7733209133148193,
    3.497948169708252
   ],
   "hydro-lnL-imos-margeta": [
    -3.192770481109619,
    -1.8763041496276855,
    -0.34865301847457886,
    2.571875810623169,
    3.1860146522521973
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0150301456451416,
    -1.6983203887939453,
    -0.18179011344909668,
    2.3542842864990234,
    3.1140592098236084
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7979178428649902,
    -1.4814395904541016,
    -0.04883396252989769,
    1.9871443510055542,
    3.0052337646484375
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.383391380310059,
    -2.8577163219451904,
    -0.5035386085510254,
    0.5568951368331909,
    1.6979156732559204
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.201019525527954,
    -1.8811427354812622,
    -0.35072702169418335,
    2.179685115814209,
    2.49918270111084
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8462859375,
   "hydro-lnL-imos-margeta": 0.8464234375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8463228125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.84624,
   "hydro-lnL-ims-proxy-margeta": 0.888558125,
   "hydro-lnL-imos-amp-margeta": 0.8464153125
  },
  "scored_any_share": 0.8887296875,
  "seconds": 500.35256600379944,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 10.986328125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.423989295959473,
    -7.464447975158691,
    -0.10052944719791412,
    2.948530673980713,
    3.5028820037841797
   ],
   "hydro-lnL-imos-margeta": [
    -3.125868082046509,
    -1.8403607606887817,
    -0.344058096408844,
    2.6741979122161865,
    3.211453914642334
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.94791316986084,
    -1.662511944770813,
    -0.17771929502487183,
    2.4814016819000244,
    3.147261619567871
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7324435710906982,
    -1.4457273483276367,
    -0.046833403408527374,
    2.1620712280273438,
    3.052009105682373
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.625791072845459,
    -3.006298303604126,
    -0.5258331298828125,
    0.5916222333908081,
    1.7071409225463867
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1362767219543457,
    -1.8469386100769043,
    -0.3464345335960388,
    2.2578203678131104,
    2.497819423675537
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.875779992200078,
   "hydro-lnL-imos-margeta": 0.8758253042469575,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8757931170688293,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8757624923750762,
   "hydro-lnL-ims-proxy-margeta": 0.911849006509935,
   "hydro-lnL-imos-amp-margeta": 0.8758168668313316
  },
  "scored_any_share": 0.9119483805161949,
  "seconds": 465.51513481140137,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 19.79827880859375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.562541007995605,
    -7.548654556274414,
    -0.11279691010713577,
    3.0230562686920166,
    3.5070347785949707
   ],
   "hydro-lnL-imos-margeta": [
    -3.1865720748901367,
    -1.8628308773040771,
    -0.35501670837402344,
    2.720043897628784,
    3.2367498874664307
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0106630325317383,
    -1.68571138381958,
    -0.18777748942375183,
    2.5442798137664795,
    3.1802234649658203
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.794513463973999,
    -1.4699386358261108,
    -0.05162368714809418,
    2.2562055587768555,
    3.0954220294952393
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.905139446258545,
    -3.167520523071289,
    -0.5604879856109619,
    0.6880706548690796,
    1.9623667001724243
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.201953887939453,
    -1.8719433546066284,
    -0.35772499442100525,
    2.2780089378356934,
    2.485724449157715
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9172708454169083,
   "hydro-lnL-imos-margeta": 0.9172869394887898,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9172747517450349,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9172653765575312,
   "hydro-lnL-ims-proxy-margeta": 0.9490816378827577,
   "hydro-lnL-imos-amp-margeta": 0.9172860019700394
  },
  "scored_any_share": 0.9491030445608912,
  "seconds": 1082.6082272529602,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 18.2342529296875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.35578727722168,
    -7.360024929046631,
    -0.11605967581272125,
    3.0597000122070312,
    3.5124857425689697
   ],
   "hydro-lnL-imos-margeta": [
    -3.1439335346221924,
    -1.8464492559432983,
    -0.35754716396331787,
    2.744920492172241,
    3.245712995529175
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9662537574768066,
    -1.6687753200531006,
    -0.1901153028011322,
    2.573827028274536,
    3.1909046173095703
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7495999336242676,
    -1.452556848526001,
    -0.05292191356420517,
    2.2951138019561768,
    3.108147144317627
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.779082775115967,
    -3.0957460403442383,
    -0.5618422031402588,
    0.7250186204910278,
    2.0153000354766846
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1568102836608887,
    -1.8541191816329956,
    -0.36028555035591125,
    2.295819044113159,
    2.4908578395843506
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9130180573194268,
   "hydro-lnL-imos-margeta": 0.9130330571694283,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9130219635303647,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9130118073819262,
   "hydro-lnL-ims-proxy-margeta": 0.9497959707902921,
   "hydro-lnL-imos-amp-margeta": 0.9130319634303657
  },
  "scored_any_share": 0.949835032899671,
  "seconds": 1070.4753630161285,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 17.96722412109375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.139360427856445,
    -7.318531513214111,
    -0.10739044100046158,
    3.0604171752929688,
    3.509474515914917
   ],
   "hydro-lnL-imos-margeta": [
    -3.1293113231658936,
    -1.8333834409713745,
    -0.35076892375946045,
    2.7451727390289307,
    3.2386345863342285
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.951873779296875,
    -1.6559768915176392,
    -0.18382792174816132,
    2.5752241611480713,
    3.182230234146118
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.735548734664917,
    -1.4398595094680786,
    -0.049580156803131104,
    2.298825740814209,
    3.0992021560668945
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.848644733428955,
    -3.123624086380005,
    -0.5531337261199951,
    0.6858336329460144,
    1.7769219875335693
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.144007921218872,
    -1.8419849872589111,
    -0.3536412715911865,
    2.2943179607391357,
    2.4895007610321045
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.91142541699583,
   "hydro-lnL-imos-margeta": 0.9114397918520815,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9114297919520805,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9114204170458295,
   "hydro-lnL-ims-proxy-margeta": 0.9456891368586314,
   "hydro-lnL-imos-amp-margeta": 0.9114379168708313
  },
  "scored_any_share": 0.9457191365586344,
  "seconds": 1070.1407308578491,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 18.0816650390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.262430191040039,
    -7.426660537719727,
    -0.10989108681678772,
    3.0340921878814697,
    3.5117948055267334
   ],
   "hydro-lnL-imos-margeta": [
    -3.20743465423584,
    -1.8800735473632812,
    -0.35217520594596863,
    2.727181911468506,
    3.236018180847168
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0293335914611816,
    -1.7022805213928223,
    -0.18527385592460632,
    2.5487537384033203,
    3.1780662536621094
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.812490940093994,
    -1.4856833219528198,
    -0.050503429025411606,
    2.256375312805176,
    3.0911684036254883
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.628733158111572,
    -3.0352284908294678,
    -0.5466500520706177,
    0.6556341648101807,
    1.7373391389846802
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.215580463409424,
    -1.8866692781448364,
    -0.35484397411346436,
    2.2900421619415283,
    2.4917075634002686
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.89442890625,
   "hydro-lnL-imos-margeta": 0.8944434375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8944334375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.89442578125,
   "hydro-lnL-ims-proxy-margeta": 0.9324709375,
   "hydro-lnL-imos-amp-margeta": 0.89444078125
  },
  "scored_any_share": 0.93249640625,
  "seconds": 1068.0983788967133,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 17.58575439453125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.861214637756348,
    -7.765377998352051,
    -0.12029647827148438,
    3.0060346126556396,
    3.5141046047210693
   ],
   "hydro-lnL-imos-margeta": [
    -3.271047830581665,
    -1.9127568006515503,
    -0.3615403175354004,
    2.71108078956604,
    3.2364885807037354
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.092761754989624,
    -1.7351438999176025,
    -0.19369655847549438,
    2.5294337272644043,
    3.17829966545105
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8752503395080566,
    -1.518721580505371,
    -0.05457537621259689,
    2.2297306060791016,
    3.0900862216949463
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.595008850097656,
    -2.9902243614196777,
    -0.5444408059120178,
    0.6741370558738708,
    1.724255084991455
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.281536340713501,
    -1.9198870658874512,
    -0.36437487602233887,
    2.2774107456207275,
    2.50225830078125
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8917703125,
   "hydro-lnL-imos-margeta": 0.8918015625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8917803125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8917634375,
   "hydro-lnL-ims-proxy-margeta": 0.9336884375,
   "hydro-lnL-imos-amp-margeta": 0.8917975
  },
  "scored_any_share": 0.93373515625,
  "seconds": 1038.9340379238129,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 17.43316650390625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.891488075256348,
    -7.792348861694336,
    -0.12082117795944214,
    2.9564878940582275,
    3.5120909214019775
   ],
   "hydro-lnL-imos-margeta": [
    -3.2562761306762695,
    -1.90338933467865,
    -0.36281469464302063,
    2.680412530899048,
    3.2311198711395264
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.077570915222168,
    -1.725310206413269,
    -0.19464848935604095,
    2.4907944202423096,
    3.1716244220733643
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8602120876312256,
    -1.5087602138519287,
    -0.054839760065078735,
    2.179912567138672,
    3.083466053009033
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.683802127838135,
    -3.032911777496338,
    -0.5471042394638062,
    0.690055787563324,
    1.7445802688598633
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.264493465423584,
    -1.9097033739089966,
    -0.36528265476226807,
    2.2540767192840576,
    2.5018115043640137
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.89404375,
   "hydro-lnL-imos-margeta": 0.8940590625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8940484375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.89403921875,
   "hydro-lnL-ims-proxy-margeta": 0.9323003125,
   "hydro-lnL-imos-amp-margeta": 0.89405734375
  },
  "scored_any_share": 0.93233734375,
  "seconds": 1038.79496884346,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 17.28057861328125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.045649528503418,
    -7.834954738616943,
    -0.11949188262224197,
    2.9963719844818115,
    3.5177478790283203
   ],
   "hydro-lnL-imos-margeta": [
    -3.259398937225342,
    -1.8990963697433472,
    -0.3609614670276642,
    2.705933094024658,
    3.2380197048187256
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0808539390563965,
    -1.7209882736206055,
    -0.1930813193321228,
    2.521315574645996,
    3.1785311698913574
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.864215850830078,
    -1.5044745206832886,
    -0.054236866533756256,
    2.2198691368103027,
    3.0895981788635254
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.83510160446167,
    -3.1135501861572266,
    -0.555485725402832,
    0.7505287528038025,
    1.7006142139434814
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2687933444976807,
    -1.9050641059875488,
    -0.36349251866340637,
    2.2742063999176025,
    2.5113792419433594
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9042703125,
   "hydro-lnL-imos-margeta": 0.90428671875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.904275,
   "hydro-lnL-imos-margeta-ub1e-2": 0.90426390625,
   "hydro-lnL-ims-proxy-margeta": 0.94359859375,
   "hydro-lnL-imos-amp-margeta": 0.9042846875
  },
  "scored_any_share": 0.94362765625,
  "seconds": 1036.058187007904,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 17.08984375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.58036994934082,
    -7.571174144744873,
    -0.11221638321876526,
    2.999366283416748,
    3.5155234336853027
   ],
   "hydro-lnL-imos-margeta": [
    -3.2070982456207275,
    -1.8721352815628052,
    -0.3546569347381592,
    2.7069592475891113,
    3.2382023334503174
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.029249429702759,
    -1.6943330764770508,
    -0.1873275488615036,
    2.524296522140503,
    3.1805245876312256
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8122024536132812,
    -1.477962851524353,
    -0.051440827548503876,
    2.2220027446746826,
    3.092479705810547
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.638024806976318,
    -3.016139030456543,
    -0.5408601760864258,
    0.6997979879379272,
    1.7456415891647339
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2152183055877686,
    -1.878983497619629,
    -0.357158899307251,
    2.2721784114837646,
    2.502511739730835
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.88880421875,
   "hydro-lnL-imos-margeta": 0.888846875,
   "hydro-lnL-imos-margeta-ub1e-1": 0.88881765625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8887884375,
   "hydro-lnL-ims-proxy-margeta": 0.934010625,
   "hydro-lnL-imos-amp-margeta": 0.8888384375
  },
  "scored_any_share": 0.9340740625,
  "seconds": 1034.3645992279053,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 16.937255859375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.575203895568848,
    -7.593377113342285,
    -0.10367326438426971,
    3.047166585922241,
    3.5106730461120605
   ],
   "hydro-lnL-imos-margeta": [
    -3.153494119644165,
    -1.8535122871398926,
    -0.3474218547344208,
    2.736626148223877,
    3.2383339405059814
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9775147438049316,
    -1.6755470037460327,
    -0.18074128031730652,
    2.5609889030456543,
    3.1809520721435547
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7610950469970703,
    -1.459272027015686,
    -0.048082806169986725,
    2.2713544368743896,
    3.0956170558929443
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.6255903244018555,
    -3.0185317993164062,
    -0.5358340740203857,
    0.7364974021911621,
    1.8455891609191895
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.167619228363037,
    -1.8606643676757812,
    -0.3501507639884949,
    2.29280161857605,
    2.491238594055176
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8918896875,
   "hydro-lnL-imos-margeta": 0.8919053125,
   "hydro-lnL-imos-margeta-ub1e-1": 0.89189609375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8918871875,
   "hydro-lnL-ims-proxy-margeta": 0.92667265625,
   "hydro-lnL-imos-amp-margeta": 0.89190078125
  },
  "scored_any_share": 0.92669484375,
  "seconds": 1035.3510310649872,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 16.7083740234375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.535911560058594,
    -7.525193214416504,
    -0.11390617489814758,
    2.9727964401245117,
    3.50825834274292
   ],
   "hydro-lnL-imos-margeta": [
    -3.1669275760650635,
    -1.8484137058258057,
    -0.3569970726966858,
    2.689577579498291,
    3.2240703105926514
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.988769054412842,
    -1.6705549955368042,
    -0.18928833305835724,
    2.5016891956329346,
    3.163231372833252
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7726404666900635,
    -1.4543876647949219,
    -0.0521714985370636,
    2.1931464672088623,
    3.071525812149048
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.726655006408691,
    -3.0580623149871826,
    -0.5512892007827759,
    0.6873011589050293,
    1.9236152172088623
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.177565574645996,
    -1.8550626039505005,
    -0.3593776226043701,
    2.2622222900390625,
    2.4922285079956055
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.90420328125,
   "hydro-lnL-imos-margeta": 0.904219375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.90420828125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9041978125,
   "hydro-lnL-ims-proxy-margeta": 0.93693109375,
   "hydro-lnL-imos-amp-margeta": 0.90421828125
  },
  "scored_any_share": 0.936955,
  "seconds": 1037.3506591320038,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 16.36505126953125,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.010680198669434,
    -7.211053848266602,
    -0.1084987223148346,
    3.0992252826690674,
    3.513547420501709
   ],
   "hydro-lnL-imos-margeta": [
    -3.101816177368164,
    -1.8253629207611084,
    -0.351832777261734,
    2.7714009284973145,
    3.2524704933166504
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.924651861190796,
    -1.6479347944259644,
    -0.1848430037498474,
    2.6074564456939697,
    3.198870897293091
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7093753814697266,
    -1.431900978088379,
    -0.0500250905752182,
    2.3410630226135254,
    3.1182501316070557
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.665496826171875,
    -3.052765369415283,
    -0.5550252199172974,
    0.6634689569473267,
    1.7799016237258911
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1138863563537598,
    -1.8333966732025146,
    -0.35463616251945496,
    2.312401056289673,
    2.489086389541626
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.91068609375,
   "hydro-lnL-imos-margeta": 0.9107325,
   "hydro-lnL-imos-margeta-ub1e-1": 0.91069921875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9106646875,
   "hydro-lnL-ims-proxy-margeta": 0.94542359375,
   "hydro-lnL-imos-amp-margeta": 0.9107275
  },
  "scored_any_share": 0.94545265625,
  "seconds": 1055.764605998993,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 20.10345458984375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.88989543914795,
    -7.806071758270264,
    -0.11930985003709793,
    3.029550552368164,
    3.5151453018188477
   ],
   "hydro-lnL-imos-margeta": [
    -3.2431132793426514,
    -1.897150993347168,
    -0.360757052898407,
    2.7263975143432617,
    3.2440683841705322
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0654959678649902,
    -1.7197998762130737,
    -0.19289371371269226,
    2.5513505935668945,
    3.1854348182678223
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.848979949951172,
    -1.5033464431762695,
    -0.05416864901781082,
    2.2650043964385986,
    3.0999605655670166
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.740940570831299,
    -3.0659000873565674,
    -0.5496678352355957,
    0.7211940288543701,
    1.7360169887542725
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2545604705810547,
    -1.9048913717269897,
    -0.36339497566223145,
    2.2830779552459717,
    2.5004148483276367
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.90424109375,
   "hydro-lnL-imos-margeta": 0.90426609375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.90424875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.90423625,
   "hydro-lnL-ims-proxy-margeta": 0.94245484375,
   "hydro-lnL-imos-amp-margeta": 0.9042628125
  },
  "scored_any_share": 0.9424871875,
  "seconds": 1077.5503342151642,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 16.21246337890625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.192219734191895,
    -7.297916412353516,
    -0.10535389184951782,
    3.1527421474456787,
    3.519037961959839
   ],
   "hydro-lnL-imos-margeta": [
    -3.100745439529419,
    -1.834384560585022,
    -0.34885287284851074,
    2.812495708465576,
    3.2646758556365967
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.922546625137329,
    -1.656758189201355,
    -0.18207094073295593,
    2.6564738750457764,
    3.2133407592773438
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.705630302429199,
    -1.440394401550293,
    -0.048769596964120865,
    2.402611255645752,
    3.1363039016723633
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.6830244064331055,
    -3.0525741577148438,
    -0.5433908700942993,
    0.6540101170539856,
    1.7822116613388062
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.110154151916504,
    -1.841113805770874,
    -0.3514518141746521,
    2.3409290313720703,
    2.5049149990081787
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.90505890625,
   "hydro-lnL-imos-margeta": 0.9050765625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.905063125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9050540625,
   "hydro-lnL-ims-proxy-margeta": 0.93899203125,
   "hydro-lnL-imos-amp-margeta": 0.90507515625
  },
  "scored_any_share": 0.93902390625,
  "seconds": 1055.9386620521545,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 16.021728515625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.055522918701172,
    -7.121525764465332,
    -0.11049538850784302,
    3.008329391479492,
    3.5053389072418213
   ],
   "hydro-lnL-imos-margeta": [
    -3.061018228530884,
    -1.8052204847335815,
    -0.3531057834625244,
    2.7098755836486816,
    3.2272212505340576
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.883537530899048,
    -1.6277207136154175,
    -0.18599680066108704,
    2.5306508541107178,
    3.1685824394226074
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.6681153774261475,
    -1.411749005317688,
    -0.05074284225702286,
    2.2356064319610596,
    3.082028388977051
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.847871780395508,
    -3.129079580307007,
    -0.5589587688446045,
    0.6448737978935242,
    1.8221473693847656
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.0712902545928955,
    -1.8133013248443604,
    -0.35560014843940735,
    2.2719407081604004,
    2.4861600399017334
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.91265375,
   "hydro-lnL-imos-margeta": 0.9126675,
   "hydro-lnL-imos-margeta-ub1e-1": 0.91265796875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.91265125,
   "hydro-lnL-ims-proxy-margeta": 0.9443759375,
   "hydro-lnL-imos-amp-margeta": 0.91266453125
  },
  "scored_any_share": 0.94439953125,
  "seconds": 1059.3166687488556,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.869140625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.524892807006836,
    -7.524410247802734,
    -0.103854700922966,
    3.030062437057495,
    3.508125066757202
   ],
   "hydro-lnL-imos-margeta": [
    -3.1413538455963135,
    -1.8428847789764404,
    -0.3472279906272888,
    2.724658250808716,
    3.2308831214904785
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9639246463775635,
    -1.6654160022735596,
    -0.18065954744815826,
    2.548795700073242,
    3.1709325313568115
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.747743606567383,
    -1.4490777254104614,
    -0.04813550412654877,
    2.25817608833313,
    3.081829071044922
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.743216514587402,
    -3.078725576400757,
    -0.5472128987312317,
    0.6691656708717346,
    1.8281571865081787
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.155410051345825,
    -1.8506497144699097,
    -0.34998199343681335,
    2.288311719894409,
    2.4921414852142334
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8997275910259103,
   "hydro-lnL-imos-margeta": 0.8997419661696617,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8997311848118481,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8997233722337223,
   "hydro-lnL-ims-proxy-margeta": 0.9329430794307944,
   "hydro-lnL-imos-amp-margeta": 0.899740247402474
  },
  "scored_any_share": 0.9329640171401714,
  "seconds": 1064.37642288208,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.67840576171875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -13.100621223449707,
    -7.918121337890625,
    -0.12378604710102081,
    2.976656913757324,
    3.5104026794433594
   ],
   "hydro-lnL-imos-margeta": [
    -3.242136240005493,
    -1.8914273977279663,
    -0.36548811197280884,
    2.691000461578369,
    3.2280240058898926
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0640203952789307,
    -1.7135474681854248,
    -0.19701695442199707,
    2.5051145553588867,
    3.168736457824707
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.847104072570801,
    -1.4967812299728394,
    -0.056014083325862885,
    2.1977450847625732,
    3.0787625312805176
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.835078716278076,
    -3.104177951812744,
    -0.5607038736343384,
    0.6490253806114197,
    1.9805253744125366
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.251471519470215,
    -1.897507667541504,
    -0.3678106665611267,
    2.262578248977661,
    2.493250608444214
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.91282890625,
   "hydro-lnL-imos-margeta": 0.9128525,
   "hydro-lnL-imos-margeta-ub1e-1": 0.91283671875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.91282171875,
   "hydro-lnL-ims-proxy-margeta": 0.94652484375,
   "hydro-lnL-imos-amp-margeta": 0.91284921875
  },
  "scored_any_share": 0.94656875,
  "seconds": 1064.2892909049988,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 15.52581787109375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.759783744812012,
    -7.6493377685546875,
    -0.11729754507541656,
    2.978623867034912,
    3.5100255012512207
   ],
   "hydro-lnL-imos-margeta": [
    -3.209196090698242,
    -1.8820414543151855,
    -0.3595010042190552,
    2.692929744720459,
    3.225940704345703
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.030789852142334,
    -1.7042452096939087,
    -0.19177106022834778,
    2.5054774284362793,
    3.165839672088623
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8145394325256348,
    -1.4876899719238281,
    -0.05348362401127815,
    2.197819471359253,
    3.076411724090576
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.6415228843688965,
    -3.0292630195617676,
    -0.5503284931182861,
    0.6642736196517944,
    1.6997567415237427
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.216888189315796,
    -1.8883259296417236,
    -0.3619752526283264,
    2.2657113075256348,
    2.4952621459960938
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8978985102351024,
   "hydro-lnL-imos-margeta": 0.8979146041460414,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8979027290272903,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8978925726757268,
   "hydro-lnL-ims-proxy-margeta": 0.9359932661826619,
   "hydro-lnL-imos-amp-margeta": 0.8979111666116661
  },
  "scored_any_share": 0.9360223289732897,
  "seconds": 1063.5777411460876,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 19.95086669921875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.262505531311035,
    -7.343493938446045,
    -0.10620550811290741,
    2.963716745376587,
    3.5047459602355957
   ],
   "hydro-lnL-imos-margeta": [
    -3.0622572898864746,
    -1.8136693239212036,
    -0.3495606780052185,
    2.6805779933929443,
    3.220052719116211
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.884617805480957,
    -1.6362226009368896,
    -0.18265187740325928,
    2.4944374561309814,
    3.1597862243652344
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.6683454513549805,
    -1.4201642274856567,
    -0.04907190799713135,
    2.186582326889038,
    3.0680296421051025
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.855776309967041,
    -3.131466865539551,
    -0.5417766571044922,
    0.6911206841468811,
    1.7791582345962524
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.076314926147461,
    -1.8211292028427124,
    -0.3519858717918396,
    2.255094528198242,
    2.4901301860809326
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.89984734375,
   "hydro-lnL-imos-margeta": 0.89985765625,
   "hydro-lnL-imos-margeta-ub1e-1": 0.89985046875,
   "hydro-lnL-imos-margeta-ub1e-2": 0.89984328125,
   "hydro-lnL-ims-proxy-margeta": 0.929995,
   "hydro-lnL-imos-amp-margeta": 0.899856875
  },
  "scored_any_share": 0.9300115625,
  "seconds": 1078.120351076126,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 19.34051513671875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.568892478942871,
    -7.687821865081787,
    -0.12230125069618225,
    3.062256097793579,
    3.513542652130127
   ],
   "hydro-lnL-imos-margeta": [
    -3.277191162109375,
    -1.9311081171035767,
    -0.36405253410339355,
    2.7467267513275146,
    3.241868495941162
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -3.0999011993408203,
    -1.7530841827392578,
    -0.19585354626178741,
    2.5763320922851562,
    3.184978723526001
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.8829452991485596,
    -1.53655207157135,
    -0.05541325360536575,
    2.2972564697265625,
    3.1006126403808594
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.778954982757568,
    -3.085339069366455,
    -0.5497461557388306,
    0.6556882262229919,
    1.7134824991226196
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.2866218090057373,
    -1.937817096710205,
    -0.36692094802856445,
    2.29921817779541,
    2.497487783432007
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9129578125,
   "hydro-lnL-imos-margeta": 0.91297375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9129634375,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9129528125,
   "hydro-lnL-ims-proxy-margeta": 0.94484609375,
   "hydro-lnL-imos-amp-margeta": 0.91297171875
  },
  "scored_any_share": 0.94487390625,
  "seconds": 1082.2385578155518,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 19.64569091796875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.607779502868652,
    -7.555641174316406,
    -0.11518312990665436,
    3.0077807903289795,
    3.5128250122070312
   ],
   "hydro-lnL-imos-margeta": [
    -3.1571502685546875,
    -1.8545454740524292,
    -0.3572758436203003,
    2.711937665939331,
    3.2381036281585693
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.978792190551758,
    -1.6766160726547241,
    -0.1896597445011139,
    2.5320277214050293,
    3.1805293560028076
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7630503177642822,
    -1.4601905345916748,
    -0.05258363485336304,
    2.234943389892578,
    3.0943071842193604
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.7199578285217285,
    -3.0679211616516113,
    -0.5485439300537109,
    0.6986199617385864,
    1.7903107404708862
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1679372787475586,
    -1.861026644706726,
    -0.35973337292671204,
    2.275829792022705,
    2.501465082168579
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.902020354796452,
   "hydro-lnL-imos-margeta": 0.9020430108198918,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9020261359886401,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9020119173808262,
   "hydro-lnL-ims-proxy-margeta": 0.9369626616233838,
   "hydro-lnL-imos-amp-margeta": 0.9020395733542664
  },
  "scored_any_share": 0.9370059424405756,
  "seconds": 1080.7452111244202,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 19.49310302734375,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.64455509185791,
    -7.604018211364746,
    -0.11386381089687347,
    2.954803228378296,
    3.506857395172119
   ],
   "hydro-lnL-imos-margeta": [
    -3.1696441173553467,
    -1.8614566326141357,
    -0.35653412342071533,
    2.677382707595825,
    3.223750352859497
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.991912364959717,
    -1.6835459470748901,
    -0.18895916640758514,
    2.489518165588379,
    3.1635124683380127
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.775209903717041,
    -1.466713547706604,
    -0.052121601998806,
    2.1795732975006104,
    3.072551727294922
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.794707775115967,
    -3.1012048721313477,
    -0.5493571758270264,
    0.6446892023086548,
    1.7073460817337036
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1800925731658936,
    -1.8678643703460693,
    -0.3589513897895813,
    2.2497012615203857,
    2.4896457195281982
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8991227412274123,
   "hydro-lnL-imos-margeta": 0.8991422726727267,
   "hydro-lnL-imos-margeta-ub1e-1": 0.8991272725227252,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8991130536305363,
   "hydro-lnL-ims-proxy-margeta": 0.9322818228182281,
   "hydro-lnL-imos-amp-margeta": 0.8991403976539766
  },
  "scored_any_share": 0.9323190106901069,
  "seconds": 1079.78581905365,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 18.768310546875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.627480506896973,
    -7.571948051452637,
    -0.10047174990177155,
    3.1383137702941895,
    3.5170600414276123
   ],
   "hydro-lnL-imos-margeta": [
    -3.14113450050354,
    -1.8412803411483765,
    -0.34348219633102417,
    2.80143404006958,
    3.2657954692840576
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9629578590393066,
    -1.6636111736297607,
    -0.1772419512271881,
    2.645740509033203,
    3.2151920795440674
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.746424674987793,
    -1.4474129676818848,
    -0.046711042523384094,
    2.39286470413208,
    3.1408140659332275
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.699784755706787,
    -3.0529372692108154,
    -0.5317443609237671,
    0.7978334426879883,
    2.1030750274658203
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.150911331176758,
    -1.8487334251403809,
    -0.34610000252723694,
    2.3278491497039795,
    2.49472713470459
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.8919109375,
   "hydro-lnL-imos-margeta": 0.891928125,
   "hydro-lnL-imos-margeta-ub1e-1": 0.89191828125,
   "hydro-lnL-imos-margeta-ub1e-2": 0.8919078125,
   "hydro-lnL-ims-proxy-margeta": 0.9247271875,
   "hydro-lnL-imos-amp-margeta": 0.8919234375
  },
  "scored_any_share": 0.92475296875,
  "seconds": 1057.7275099754333,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 18.61572265625,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.064849853515625,
    -7.219659328460693,
    -0.10988101363182068,
    2.940614938735962,
    3.501650810241699
   ],
   "hydro-lnL-imos-margeta": [
    -3.0552525520324707,
    -1.806780219078064,
    -0.3535572290420532,
    2.6676549911499023,
    3.20986270904541
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.878033399581909,
    -1.6290054321289062,
    -0.1861439049243927,
    2.4757606983184814,
    3.1469569206237793
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.6618192195892334,
    -1.4125481843948364,
    -0.05058802664279938,
    2.1603996753692627,
    3.051776885986328
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.857062816619873,
    -3.1318867206573486,
    -0.5539557933807373,
    0.7074984312057495,
    2.0561227798461914
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.066373348236084,
    -1.8134897947311401,
    -0.3558734655380249,
    2.246530771255493,
    2.487653970718384
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.9102443350566495,
   "hydro-lnL-imos-margeta": 0.9102626161238387,
   "hydro-lnL-imos-margeta-ub1e-1": 0.9102479287707123,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9102371476285237,
   "hydro-lnL-ims-proxy-margeta": 0.9413958985410146,
   "hydro-lnL-imos-amp-margeta": 0.9102612098879012
  },
  "scored_any_share": 0.9414171483285168,
  "seconds": 1061.7789301872253,
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
   "hydro-lnL-imos-eta2.26e-3",
   "hydro-lnL-imos-margeta",
   "hydro-lnL-imos-margeta-ub1e-1",
   "hydro-lnL-imos-margeta-ub1e-2",
   "hydro-lnL-ims-proxy-margeta",
   "hydro-lnL-imos-amp-margeta"
  ],
  "free_gib_at_write": 18.42498779296875,
  "quantiles": {
   "hydro-lnL-imos-eta2.26e-3": [
    -12.11870288848877,
    -7.2473673820495605,
    -0.10351221263408661,
    3.050603151321411,
    3.5090274810791016
   ],
   "hydro-lnL-imos-margeta": [
    -3.103686571121216,
    -1.8246153593063354,
    -0.3474569320678711,
    2.737421751022339,
    3.236250162124634
   ],
   "hydro-lnL-imos-margeta-ub1e-1": [
    -2.9269111156463623,
    -1.6471197605133057,
    -0.18079586327075958,
    2.564659595489502,
    3.179691791534424
   ],
   "hydro-lnL-imos-margeta-ub1e-2": [
    -2.7105400562286377,
    -1.43110191822052,
    -0.04806649684906006,
    2.282557964324951,
    3.09576678276062
   ],
   "hydro-lnL-ims-proxy-margeta": [
    -5.78427267074585,
    -3.108403205871582,
    -0.5497053861618042,
    0.6491274833679199,
    1.8850082159042358
   ],
   "hydro-lnL-imos-amp-margeta": [
    -3.1185715198516846,
    -1.832916498184204,
    -0.35018518567085266,
    2.2934350967407227,
    2.4898622035980225
   ]
  },
  "share_nonzero": {
   "hydro-lnL-imos-eta2.26e-3": 0.90678703125,
   "hydro-lnL-imos-margeta": 0.9068009375,
   "hydro-lnL-imos-margeta-ub1e-1": 0.906790625,
   "hydro-lnL-imos-margeta-ub1e-2": 0.9067825,
   "hydro-lnL-ims-proxy-margeta": 0.93857234375,
   "hydro-lnL-imos-amp-margeta": 0.90679890625
  },
  "scored_any_share": 0.93859421875,
  "seconds": 1062.7375631332397,
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
