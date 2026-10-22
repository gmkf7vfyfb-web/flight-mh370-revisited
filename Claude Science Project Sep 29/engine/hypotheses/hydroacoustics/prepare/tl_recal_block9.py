"""PRE-REGISTRATION (committed before any number below is computed): transmission-loss recalibration, work order
2026-10-21 block 9 = brief Refresh v2 section 9 steps (a), (b), (d). Hydroacoustic Module, overnight track, 22 Oct 2026.

DISCLOSURE (not blind). The author of this file has read air9_ew0112.py and its results (verdicts_amendment1.json):
  the H-ref and H-flat rescoring were NOT SUPPORTED, and an EXPLORATORY post hoc model "H-flat + near-field Ball
  factor + far-field array factor" gave slopes +2.33 (H01W) and -0.43 dB/oct (H08S) at the nominal geometry and
  passed the slope grade on 0.778 of the geometry grid (label POST HOC). The confirmatory test on independent sites
  (airgun_sites_confirm.py) was NOT TESTABLE (2 testable pairs, 3 required). Route 1 below is therefore a
  CONFIRMATORY RE-SCORING of a model fixed in advance, in the forward (source + TL -> received level) form the work
  order asks for, under the audit's C1 criteria (criteria.md 940f1a3), with the decision rule fixed here. A pass is
  fit-consistency on the training case (air9), NOT an independent confirmation; it cannot lift caveat C1 on its own.
  Nothing in the model is fitted to Fig. 23; every parameter comes from EW0112, OFR 95-228 or geometry.

ROUTE 1 - EW0112 near-source calibrated recordings (step a, first route).
  Observation. Blackman et al. (2004) Fig. 23 "observed TL" (digitised, +/-2 dB; air9 third-octave band means at
    H01W 12.5/16-63 Hz and H08S 5-63 Hz as in results/hydroacoustics-audit/data/air9_residuals.csv, model M1) is
    TL_obs,b = SL_B - RL_obs,b with a FLAT source level SL_B. Blackman quote the array as 230-240 dB re 1 uPa at 1 m.
    Hence RL_obs,b = SL_B - TL_obs,b with SL_B = 235 dB (midpoint; 230 and 240 reported as the range).
  Source. Ball(f) = dB mean over the two Fig. 2 shots of the third-octave Ball spectrum at the receiver
    (results-data/air9_ew0112/ew0112_fig2_ball_spectra_bands_DIGITISED.csv), scaled to 1 m by 20 log10 R1m with
    R1m = 25.75 m (ew0112_fig2_scaling.json). A band is used only if BOTH shots are READABLE (so 40 Hz is excluded).
    Delta_ref,b = 10 log10 <|sum_g w_g (e^{ik r1g}/r1g - e^{ik r2g}/r2g) / sum_g w_g|^2>_b R1m^2, the near-field
    reference factor at the Ball for the OFR 95-228 20-gun layout (ewing_20gun_layout_ofr95228.csv) with weights
    w_g proportional to V_g^(1/3) (primary) and equal (sensitivity); r1g/r2g = direct/surface-image paths from gun g
    to the Ball; band mean over 200 log-spaced frequencies inside f_b 2^(+/-1/6); c = 1500 m/s.
    S0,b = Ball,b + 20 log10 R1m - Delta_ref,b: the far-field notional MONOPOLE source spectrum level
    (dB re 1 uPa^2/Hz at 1 m) which KRAKEN's point source at z_s (free surface included) then propagates.
    AF_b(station) = 10 log10 of the band-mean |sum_g w_g e^{-i k u.x_g}|^2 / (sum_g w_g)^2 at elevation 0 deg toward
    the station (bearing from the air9 midpoint minus the ship heading 111.2 deg; across-track sign +1 primary,
    -1 reported), the module's air9_farfield_array_factor.csv values.
  Geometry prior (unchanged from air9_ew0112.py): z_s in {9, 10, 12} m (10 nominal), Ball x_h in {20, 30, 40} m
    ahead of the array centre (30 nominal), Ball depth z_h in {5, 10, 15, 20, 30} m (15 nominal): 45 grid points.
  Propagation. TL_model,b recomputed here with the module chain unchanged (air9_tl_validation.build_profiles +
    kraken_tl.tl_path: profiles every 5 km, hard bottom cp 1650 / rho 1.9 / 0.5 dB per wavelength, Francois-Garrison,
    incoherent adiabatic modes, spherical correction, receiver at the triad centroid depth H01W 1,055 m, H08S 1,376 m)
    on the SHARED ocean-transport sections (products/hydro-paths-2001-10, GEBCO_2026 + WOA23 95A4 October),
    converted by shared_paths.convert, for z_s in {9, 10, 12} m, third octaves 5-80 Hz. Pipeline check: the 10 m
    values must agree with the audit's M1 model_tl_db to within 1.0 dB in every band (else STOP and report).
  Prediction and residual. RL_pred,b = S0,b + AF_b - TL_model,b.  r_b = RL_obs,b - RL_pred,b  (dB; r > 0 means the
    model under-predicts the signal). Over the bands in both the Fig. 23 span at the station and the readable Fig. 2
    set: H01W 12.5-63 Hz without 40 (8 bands), H08S 5-63 Hz without 40 (11 bands).
  AMENDMENT 1 (22 Oct 2026 02:50 UTC, before any residual was computed; raised by the reviewer): the band COUNTS
    above were mis-stated. 12.5-63 Hz without 40 Hz is 7 bands, and the audit's H08S rows run 6.3-63 Hz, so H08S
    without 40 Hz is 10 bands. The RULE (Fig. 23 span at the station, intersected with the Fig. 2 readable set) is
    unchanged and is what the code applies; no threshold or definition changed.
  Statistics (criteria.md definitions): LEVEL = median r_b (graded at SL_B = 235; also given at 230 and 240);
    SLOPE = OLS slope of r_b on log2 f_b, dB/oct, with standard error; SHAPE = RMS of r_b after the level-and-slope fit.
    Grades: LEVEL PASS <= 3, PARTIAL <= 6; SLOPE PASS <= 1.5, PARTIAL <= 3; SHAPE PASS <= 3, PARTIAL <= 5.
  Common-mode removal (the second view the work order asks for): over the bands shared by both stations
    (12.5-63 without 40, 7 bands), c_b = mean of r_b over the two stations; r~_b = r_b - c_b. LEVEL/SLOPE/SHAPE of r~_b
    per station (= half the station difference, the path-only view, audit C2), and LEVEL/SLOPE/SHAPE of c_b itself
    (what remains on the shared, source-side term after the EW0112 source is applied).
  Sensitivities, reported, not graded: each Fig. 2 shot alone as Ball(f); equal gun weights; across-track sign -1;
    the retired stub sections in place of the shared sections.
  DECISION RULE (route 1), at z_s = 10 m, nominal geometry (x_h 30, z_h 15), V^(1/3) weights, sign +1, SL_B = 235:
    EXPLAINED        SLOPE PASS or PARTIAL at BOTH stations AND SHAPE PASS or PARTIAL at both AND LEVEL not FAIL at
                     both for at least one SL_B in {230, 235, 240}; AND the slope condition holds on >= 2/3 of the 45
                     geometry grid points (z_s x x_h x z_h).
    PARTLY EXPLAINED the nominal conditions hold but the grid fraction is < 2/3, OR slope passes at one station only
                     with the other station's slope <= 4.5 dB/oct (half-way to the uncorrected tilt).
    NOT EXPLAINED    otherwise.
  Consequence fixed now. EXPLAINED -> the air9 absolute received-level chain is labelled "PARTLY CALIBRATED in
    slope, conditional on the EW0112 source model (training case; no independent site)"; caveat C1 stays on every
    MH370 number, re-worded to name the remaining common-mode slope c_b, until an independent airgun site or the
    F-35A route confirms. PARTLY / NOT EXPLAINED -> C1 unchanged, the tilt stays attributed to near-source coupling.

ROUTE 2 - F-35A spectral shape (step a, second route; Brown et al. 2026, arXiv:2604.12723).
  Purpose. An independent near-surface source of a different kind (an aircraft impact, 9 Apr 2019, 40.64 N 142.96 E)
    seen at H11 (3,341 km). If the module's engine tilts the spectrum of a near-surface source (near-source coupling
    the flat half-space cannot represent), the F-35A implied source spectrum will show a tilt of the same sign as the
    air9 common mode; if the air9 tilt was the airgun source, the F-35A implied source will sit inside the module's
    impact source-shape envelope.
  Data. The F-35A received spectrum (PSD or spectrogram slice at H11) digitised from the Brown et al. 2026 figure by
    the Digitisation track (results-data/digitised/brown2026/, polled every 30 min); if absent by hour 3 (05:20 UTC),
    digitised here from the arXiv PDF (declared as a substitution; the module branch has no papers folder).
    Third-octave band means over 5-40 Hz where the trace is readable and the paper's noise floor is exceeded by 3 dB.
  Implied source. S_F35,b = RL_b + TL_model,b, TL from results-data/f35a_cal/f35a_tl.csv (H11S and H11N, z_s 10 m,
    the same chain), RAM-corrected TL (ram_check/h11_tl_ramcorr.csv) as a sensitivity.
  Expectation. The module's impact source shape 10 log10 S_b(tau, slope) (imos_stageB_map.band_fraction) over
    tau in the F-35A grid (0.05-10 s, 25 log-spaced points) and slope in {2, 4}: envelope [s_min, s_max] of its OLS
    slopes on log2 f over the same bands.
  Statistic. s_F35 = OLS slope of S_F35,b on log2 f (dB/oct) with standard error; excess e = distance from s_F35 to
    the envelope (0 if inside).
  DECISION RULE (route 2): CONSISTENT if e <= 3 dB/oct (the PARTIAL slope threshold); INCONSISTENT otherwise, and
    then e is the lower bound of the engine-side tilt for a near-surface source and C1 is re-stated with it.
    Route 2 is DESCRIPTIVE: one event, one receiver, a figure-read PSD whose band and processing Brown may not state;
    it cannot by itself lift or confirm C1. If no usable figure exists in the paper, route 2 is reported as NOT
    AVAILABLE with the reason.

STEP (b) - air8 negative control under the same source model (only if route 1 is EXPLAINED or PARTLY EXPLAINED;
  otherwise reported as not re-run and why).
  The source spectrum S0 is common to air8 and air9 (same array, same tow-depth range; EW0112 p. 5), so it cancels in
  the within-station difference; only the array factor changes with heading. Heading of air8 from
  data/blackman/blackman_shot_lines.csv (two segments, shot-count weighted). Predicted received-level difference
  D_st,b = [AF_air8,b - TL_air8,b] - [AF_air9,b - TL_air9,b] at each station, TL on sections built by the audit path
  builder (results/hydroacoustics-audit/scripts/paths.py; GEBCO_2026 3x3 median, WOA23 95A4 October) for BOTH sites
  (same builder on both sides of the difference), z_s 10 m, bands 16-50 Hz (the air8 pre-registered set).
  Rule (unchanged from air8_negative_control.py, in received-level form): H01W FOLLOWS if median D <= -10 dB;
  DOES NOT if >= -3 dB; INCONCLUSIVE between. H08S CONSISTENT if |median D| <= 5 dB. Verdict "still holds" if
  H01W FOLLOWS and H08S CONSISTENT.

STEP (d) - air7 -> H01W, the ridge path (gap G22).
  Source: air7 shot-weighted mean position of the two EW0112 segments (data/blackman/blackman_shot_lines.csv:
    segment 1, 16 shots, 22 55.5 S 87 02.8 E to 22 54.6 S 87 00.7 E; segment 2, 14 shots, to 22 54.3 S 87 00.0 E).
    Receiver H01W triad centroid (-34.890303, 114.142637), depth 1,055 m. z_s = 10 m only (budget; declared).
  (d1) N x 2D: nx2d.py unchanged (17 Fresnel-corridor members, u in -2..2 step 0.25, weights exp(-u^2), GEBCO_2026
    3x3 median at 0.5 km, sound speed from the geodesic's own section built by the audit path builder), bands
    16, 20, 25, 31.5, 40, 50, 63 Hz (the observed air7 span at H01W is 31.5-80 Hz; 16-25 Hz are carried for the air9
    comparison; 80 Hz is omitted as the Fig. 2 source is unreadable there and the cost is highest).
  (d2) 3-D proxy (horizontal refraction around the 1,190 m feature at 28.8-29.0 S, 98.0-98.5 E): single-section TL
    along paths displaced laterally from the geodesic by d(s) = d_max sin(pi s / R), d_max in {-20, -10, -5, 0, +5,
    +10, +20} km (positive = to the right of the forward azimuth), same bands; the least-loss corridor is the minimum
    TL over d_max per band (an optimistic bound: it assumes the energy finds the deepest corridor within +/-20 km).
  (d3) If wall time allows after (d1)-(d2) (budget: 4 processes, finish by 09:00 UTC): a RAM (pyram) coupled
    solution on the geodesic at 31.5, 40 and 63 Hz, ram_tl_check.py settings (dr 2 lambda, dz lambda/20, 9
    frequencies per band, no absorption in either model), as a mode-coupling cross-check; reported, not graded.
  Observation: Fig. 23 CL air7 and air9 digitised band means (results-data/airgun_sites_confirm/
    fig23_CL_air7_bands_DIGITISED.csv, fig23_CL_air9_bands_DIGITISED.csv): the observed difference
    dTL_obs,b = TL_obs(air7) - TL_obs(air9) at H01W (about 0 +/- 2 dB at 31.5-63 Hz), which cancels the flat source.
  Statistic: dTL_model,b = TL(air7 -> H01W) - TL(air9 -> H01W) per band, for the geodesic, the N x 2D corridor and the
    least-loss corridor; the primary is the MEDIAN over 31.5, 40, 50, 63 Hz of dTL_model - dTL_obs.
  DECISION RULE (step d): REPRODUCED if |median| <= 10 dB for the N x 2D corridor; REPRODUCED AS AN UPPER BOUND if
    only the least-loss corridor is within 10 dB; NOT REPRODUCED otherwise. The absolute comparison with the module
    source model (S0 + AF - TL against SL_B - TL_obs) is reported beside it.
  G22 status text proposed to the architect: REPRODUCED -> "explained (lateral corridor, N x 2D)"; UPPER BOUND ->
    "explained only as an upper bound (3-D proxy); 3-D model needed"; NOT -> "still open: single-section, corridor and
    +/-20 km proxy all exceed the observation by > 10 dB; mode-coupling (PE/3-D) is the next test".

AMENDMENT 2 (22 Oct 2026 02:45 UTC, after the +/-20 km result was seen; EXPLORATORY, labelled, outside the
  pre-registered rule). The least-loss TL falls steadily with offset to the right of the geodesic (crest 1,199 m at
  0 km, 1,420 m at +20 km), and a bathymetry scan shows the feature cleared at +40 to +50 km (crest >= 1,572 m, the
  H01W slope itself). Offsets +30, +40, +50 km are added as an extension of the 3-D proxy. They are reported as an
  exploratory upper bound only; the step (d) verdict is taken from the registered +/-20 km set. The RAM (d3) runs are
  placed on the geodesic and on the +20 km path at 31.5 and 40 Hz.
AMENDMENT 3 (22 Oct 2026 02:50 UTC, after the first RAM result; EXPLORATORY, labelled). RAM at 31.5 and 40 Hz on the
  geodesic cut the air7 - air9 excess from about 43-53 dB (adiabatic) to about 20 dB, so the RAM set is extended to 50
  and 63 Hz and to the +50 km path (the ridge-clearing corridor), with air9 -> H01W at the same bands as the reference.
  Reported beside the registered result; the step (d) verdict stays on the registered adiabatic set.
OUTPUTS. results-data/tl_recal_block9/: route1_tl_model.csv, route1_residuals.csv (per station, z_s, geometry,
  weights, sign, SL_B, band: RL_obs, RL_pred, r, r~), route1_grades.csv, route1_verdict.json; route2_*.csv/json;
  air8_recal.csv + air8_recal_verdict.json; air7_corridor.csv, air7_offsets.csv, air7_verdict.json; wall.json.
  Charts (PNG + PDF, two footnotes) and the addendum go to results/ on claude-science-sep29. Caveats C1 and C2 on
  every number. KRAKEN scratch under /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal/ (deleted
  after use). Thread budget 4 processes (one KRAKEN/FIELD run per process).
"""
# IMPLEMENTATION is appended after the pre-registration commit (method exactly as registered; any change is an
# amendment with its own commit and reason).
# Usage:
#   python tl_recal_block9.py sections <audit_scripts_dir> <shared_products_dir> <sections_out>
#   python tl_recal_block9.py tl <sections_dir> <at_bin> <scratch> <out> [nproc]        (air9 shared+builder, air8, air7 offsets)
#   python tl_recal_block9.py route1 <audit_residuals.csv> <ew0112_results_dir> <out>
#   python tl_recal_block9.py air8 <out>
#   python tl_recal_block9.py air7 <out> <nx2d_corridor.csv> <airgun_sites_confirm_dir>
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

sys.path.insert(0, str(Path(__file__).resolve().parent))
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402
from air9_ew0112 import score as ew_score  # noqa: E402  (C1 grading: level/slope/shape, same thresholds)

G = Geod(ellps="WGS84")
C_REF = 1500.0
STATIONS = {"H01W": ((-34.890303, 114.142637), 1055.0), "H08S": ((-7.639380, 72.483828), 1376.0)}
SITES = {  # shot-count weighted mean positions (data/blackman/blackman_shot_lines.csv; air9 = EW0112 p. 5 midpoint)
    "air9": dict(pos=(-27.5612, 98.8821), heading=111.2),
    "air8": dict(segs=[((-23.416667, 88.188333), (-23.426667, 88.221667), 11), ((-23.426667, 88.225), (-23.428333, 88.231667), 7)]),
    "air7": dict(segs=[((-22.925, 87.046667), (-22.91, 87.011667), 16), ((-22.91, 87.011667), (-22.905, 87.0), 14)]),
}
ALL_BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0]
AIR7_BANDS = [16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
AIR8_BANDS = [16.0, 20.0, 25.0, 31.5, 40.0, 50.0]
OFFSETS_KM = [-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0]
ZS = [9.0, 10.0, 12.0]


def site_pos_heading(site):
    s = SITES[site]
    if "pos" in s:
        return s["pos"], s["heading"]
    w = np.array([n for _, _, n in s["segs"]], float)
    mids = np.array([((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b, _ in s["segs"]])
    az = np.array([G.inv(a[1], a[0], b[1], b[0])[0] % 360 for a, b, _ in s["segs"]])
    return tuple((mids * w[:, None]).sum(0) / w.sum()), float((az * w).sum() / w.sum())


# ----------------------------------------------------------------------------------------------- sections
def offset_section(src, rcv, d_max_km, ds_km=0.5):
    """Bathymetry along the geodesic displaced laterally by d(s) = d_max sin(pi s / R) (positive = right of azimuth)."""
    import nx2d as N
    az12, _, R = G.inv(src[1], src[0], rcv[1], rcv[0])
    n = int(R / 1000.0 / ds_km) + 1
    s = np.linspace(0.0, R, n)
    lon, lat, _ = G.fwd(np.full(n, src[1]), np.full(n, src[0]), np.full(n, az12), s)
    az_loc = np.array(G.inv(lon[:-1], lat[:-1], lon[1:], lat[1:])[0]); az_loc = np.append(az_loc, az_loc[-1])
    d = d_max_km * 1000.0 * np.sin(np.pi * s / R)
    lo2, la2, _ = G.fwd(lon, lat, az_loc + 90.0, d)
    return pd.DataFrame(dict(range_km=s / 1000.0, lat=la2, lon=lo2, elevation_m=N.elevation(la2, lo2), offset_m=d,
                             tid=np.nan, corridor_max_elevation_m=np.nan)), R / 1000.0


def cmd_sections(audit_scripts, shared_products, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, audit_scripts); import paths as AP  # audit path builder (GEBCO 3x3 median, WOA23 95A4)
    import shared_paths as SP
    log = {}
    (out / "shared").mkdir(parents=True, exist_ok=True)
    for st in STATIONS:
        log[f"shared_air9_{st}"] = SP.convert(Path(shared_products), out / "shared", f"air9-{st}")
    for site in ("air9", "air8", "air7"):
        pos, hd = site_pos_heading(site)
        log[f"{site}_pos_heading"] = (pos, hd)
        for st, (rpos, _) in STATIONS.items():
            if site == "air7" and st != "H01W":
                continue
            L, sh = AP.build(f"{site}_{st}", pos, rpos, "95A4", 10, out / "builder")
            log[f"builder_{site}_{st}"] = dict(range_km=L, shallowest_m=sh)
    pos, _ = site_pos_heading("air7")
    for d in OFFSETS_KM:
        b, R = offset_section(pos, STATIONS["H01W"][0], d)
        b.to_csv(out / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", index=False)
        log[f"air7_offset_{d:+.0f}"] = dict(range_km=R, shallowest_m=float(b.elevation_m.max()),
                                           crest_lat=float(b.lat[b.elevation_m.idxmax()]), crest_lon=float(b.lon[b.elevation_m.idxmax()]))
    json.dump(log, open(out / "sections.json", "w"), indent=1, default=str)
    print(json.dumps(log, indent=1, default=str))


# ----------------------------------------------------------------------------------------------- TL jobs
def tl_job(a):
    tag, bathy_csv, ssp_csv, fc, zs, rd, work, at = a
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    bathy = pd.read_csv(bathy_csv); ssp = pd.read_csv(ssp_csv)
    rprof, profiles = A.build_profiles(bathy, ssp)
    L = float(rprof[-1]); root = f"{tag}_f{fc:g}".replace(".", "p")
    t0 = time.time()
    try:
        K.tl_path(work, root, fc, profiles, rprof, np.array([L]), zs, [rd], A.BOTTOMS["hard"], at, fg=A.FG)
        s = K.read_shd(Path(work) / f"{root}.shd"); x = L / 6371.0; sph = 10 * np.log10(x / np.sin(x))
        import re
        nm = [int(v) for v in re.findall(r"Number of modes\s*=\s*(\d+)", (Path(work) / f"{root}.prt").read_text(errors="replace"))]
        rows = [dict(tag=tag, fc_hz=fc, src_depth_m=float(z), rcv_depth_m=rd, range_km=L, tl_db=float(-20 * np.log10(np.abs(s["p"][0, j, 0, -1])) + sph),
                     blocked=False, n_modes_min=min(nm) if nm else -1, min_profile_depth_m=float(min(p[0] for p in profiles)), wall_s=time.time() - t0) for j, z in enumerate(s["sz"])]
    except RuntimeError as e:
        why = "no modes" if "No modes" in str(e) else str(e).splitlines()[0][:80]
        rows = [dict(tag=tag, fc_hz=fc, src_depth_m=float(z), rcv_depth_m=rd, range_km=L, tl_db=np.inf, blocked=True, n_modes_min=0,
                     min_profile_depth_m=float(min(p[0] for p in profiles)), wall_s=time.time() - t0, reason=why) for z in zs]
    for p in Path(work).glob(f"{root}.*"):
        if p.suffix in (".shd", ".mod"):
            p.unlink()
    return rows


def cmd_tl(sections, at, scratch, out, nproc=4):
    sec = Path(sections); out = Path(out); out.mkdir(parents=True, exist_ok=True); Path(scratch).mkdir(parents=True, exist_ok=True)
    jobs = []
    for st, (_, rd) in STATIONS.items():
        for fc in ALL_BANDS:   # route 1: shared sections, 3 source depths
            jobs.append((f"shared_air9_{st}", sec / "shared" / f"bathy_air9_{st}.csv", sec / "shared" / f"ssp_air9_{st}.csv", fc, ZS, rd, scratch, at))
        for fc in sorted(set(AIR8_BANDS) | {12.5}):   # step b: builder sections, both sites, 10 m (+ 12.5 Hz pipeline check)
            for site in ("air9", "air8"):
                jobs.append((f"builder_{site}_{st}", sec / "builder" / f"bathy_{site}_{st}.csv", sec / "builder" / f"ssp_{site}_{st}.csv", fc, [10.0], rd, scratch, at))
    rd = STATIONS["H01W"][1]
    for d in OFFSETS_KM:   # step d2: air7 offset paths (d = 0 is the geodesic), 10 m
        for fc in AIR7_BANDS:
            jobs.append((f"air7off{d:+.0f}_H01W", sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", sec / "builder" / f"ssp_air7_H01W.csv", fc, [10.0], rd, scratch, at))
    for fc in AIR7_BANDS:   # air9 -> H01W on the builder at the air7 bands (for the difference), 10 m
        jobs.append((f"builder_air9_H01W_a7b", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, [10.0], rd, scratch, at))
    t0 = time.time(); rows = []
    with Pool(int(nproc)) as P:
        for i, r in enumerate(P.imap_unordered(tl_job, jobs)):
            rows += r
            if i % 20 == 0:
                print(f"{i + 1}/{len(jobs)} {time.time() - t0:.0f} s", flush=True)
    T = pd.DataFrame(rows); T.to_csv(out / "tl_runs.csv", index=False)
    json.dump(dict(n_jobs=len(jobs), wall_s=time.time() - t0, nproc=int(nproc)), open(out / "wall_tl.json", "w"), indent=1)
    print(T.groupby("tag").agg(n=("fc_hz", "size"), blocked=("blocked", "sum"), wall=("wall_s", "sum")).to_string())


# ----------------------------------------------------------------------------------------------- route 1
def array_layout(csv):
    L = pd.read_csv(csv)
    return L.ahead_m.values, L.across_m.values, L.vol.values.astype(float)


def dref_array(fc, zs, xh, zh, R1m, xg, yg, w):
    f = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 200); k = 2 * np.pi * f / C_REF
    p = 0
    for ax, ay, wg in zip(xg, yg, w):
        r1 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh - zs) ** 2); r2 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh + zs) ** 2)
        p = p + wg * (np.exp(1j * k * r1) / r1 - np.exp(1j * k * r2) / r2)
    return 10 * np.log10(np.mean(np.abs(p / w.sum()) ** 2) * R1m ** 2)


def array_factor(fc, phi_deg, xg, yg, w, sign=1):
    f = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 200); k = 2 * np.pi * f / C_REF
    phi = np.radians(phi_deg); u = (np.cos(phi), sign * np.sin(phi))
    af = np.abs(sum(wg * np.exp(-1j * k * (u[0] * ax + u[1] * ay)) for ax, ay, wg in zip(xg, yg, w))) ** 2 / w.sum() ** 2
    return 10 * np.log10(np.mean(af))


def ols(fc, r):
    x = np.log2(fc); Am = np.vstack([x, np.ones_like(x)]).T; c, res, _, _ = np.linalg.lstsq(Am, r, rcond=None); e = r - Am @ c
    se = np.sqrt(e @ e / max(len(r) - 2, 1) / ((x - x.mean()) ** 2).sum()) if len(r) > 2 else np.nan
    return float(c[0]), float(se), e


def cmd_route1(resid_csv, ew_dir, out):
    out = Path(out); ew = Path(ew_dir)
    T = pd.read_csv(out / "tl_runs.csv")
    Rr = pd.read_csv(resid_csv); M1 = Rr[Rr.model == "M1"]
    ball = pd.read_csv(ew / "ew0112_fig2_ball_spectra_bands_DIGITISED.csv")
    R1m = float(json.load(open(ew / "ew0112_fig2_scaling.json"))["R1m_mean_m"])
    xg, yg, vol = array_layout(ew / "ewing_20gun_layout_ofr95228.csv")
    weights = {"V^(1/3)": vol ** (1 / 3), "equal": np.ones_like(vol)}
    readable = ball.groupby("fc_hz").readable.all()
    lvl = ball.pivot(index="fc_hz", columns="shot", values="level_db_re_1upa2_hz_at_receiver")
    ball_sets = {"both": lvl.mean(axis=1), **{f"shot {c}": lvl[c] for c in lvl.columns}}
    pos9, hd9 = site_pos_heading("air9")
    # pipeline check: shared 10 m against the audit M1 model TL
    chk = []
    for st in STATIONS:
        m = T[(T.tag == f"shared_air9_{st}") & (T.src_depth_m == 10.0)].set_index("fc_hz").tl_db
        a = M1[(M1.station == st) & (M1.src_depth_m == 10.0)].set_index("fc_hz").model_tl_db
        d = (m.reindex(a.index) - a); chk.append(dict(station=st, max_abs_diff_db=float(d.abs().max()), bands=len(a)))
    model_tl = T[T.tag.str.startswith("shared_air9")].copy(); model_tl["station"] = model_tl.tag.str[-4:]
    model_tl.to_csv(out / "route1_tl_model.csv", index=False)
    rows, grades = [], []
    for st, (rpos, _) in STATIONS.items():
        bearing = G.inv(pos9[1], pos9[0], rpos[1], rpos[0])[0] % 360; phi = bearing - hd9
        obs = M1[(M1.station == st) & (M1.src_depth_m == 10.0)].set_index("fc_hz").obs_tl_db
        fcs = np.array([f for f in obs.index if readable.get(f, False)])
        for zs in ZS:
            tl = T[(T.tag == f"shared_air9_{st}") & (T.src_depth_m == zs)].set_index("fc_hz").tl_db.reindex(fcs).values
            for wname, w in weights.items():
                for sign in (1, -1):
                    af = np.array([array_factor(f, phi, xg, yg, w, sign) for f in fcs])
                    for xh in (20, 30, 40):
                        for zh in (5, 10, 15, 20, 30):
                            dref = np.array([dref_array(f, zs, xh, zh, R1m, xg, yg, w) for f in fcs])
                            for bname, bs in ball_sets.items():
                                S0 = bs.reindex(fcs).values + 20 * np.log10(R1m) - dref
                                rl_pred = S0 + af - tl
                                for slb in (230.0, 235.0, 240.0):
                                    rl_obs = slb - obs.reindex(fcs).values; r = rl_obs - rl_pred
                                    nominal = (zs == 10.0 and wname == "V^(1/3)" and sign == 1 and xh == 30 and zh == 15 and bname == "both" and slb == 235.0)
                                    for f_, o_, p_, r_, s0_, af_, d_ in zip(fcs, rl_obs, rl_pred, r, S0, af, dref):
                                        rows.append(dict(station=st, zs=zs, weights=wname, sign=sign, xh=xh, zh=zh, ball=bname, SL_B=slb, fc_hz=f_,
                                                         rl_obs_db=o_, rl_pred_db=p_, r_db=r_, S0_db=s0_, af_db=af_, dref_db=d_, nominal=nominal))
                                    sc = ew_score(r, fcs); sl, se, _ = ols(fcs, r)
                                    grades.append(dict(station=st, zs=zs, weights=wname, sign=sign, xh=xh, zh=zh, ball=bname, SL_B=slb, nominal=nominal, slope_se=se, **sc))
    Rw = pd.DataFrame(rows); Gd = pd.DataFrame(grades)
    # common-mode removal on shared bands (every configuration)
    keys = ["zs", "weights", "sign", "xh", "zh", "ball", "SL_B"]
    cm_rows, cm_grades = [], []
    for kv, g in Rw.groupby(keys):
        pv = g.pivot(index="fc_hz", columns="station", values="r_db").dropna()
        c = pv.mean(axis=1); fcs = pv.index.values
        for st in pv.columns:
            rt = (pv[st] - c).values
            cm_grades.append(dict(**dict(zip(keys, kv)), station=st, view="common-mode removed", **ew_score(rt, fcs), slope_se=ols(fcs, rt)[1]))
            for f_, v_ in zip(fcs, rt):
                cm_rows.append(dict(**dict(zip(keys, kv)), station=st, fc_hz=f_, r_tilde_db=v_, common_mode_db=float(c[f_])))
        cm_grades.append(dict(**dict(zip(keys, kv)), station="both", view="common mode c_b", **ew_score(c.values, fcs), slope_se=ols(fcs, c.values)[1]))
    CM = pd.DataFrame(cm_grades); CMr = pd.DataFrame(cm_rows)
    Rw.to_csv(out / "route1_residuals.csv", index=False); Gd.to_csv(out / "route1_grades.csv", index=False)
    CMr.to_csv(out / "route1_common_mode_residuals.csv", index=False); CM.to_csv(out / "route1_common_mode_grades.csv", index=False)
    # decision rule
    nom = Gd[Gd.nominal].set_index("station")
    both_slope = all(nom.loc[s, "g_slope"] != "FAIL" for s in STATIONS)
    both_shape = all(nom.loc[s, "g_shape"] != "FAIL" for s in STATIONS)
    base = Gd[(Gd.weights == "V^(1/3)") & (Gd.sign == 1) & (Gd.ball == "both")]
    level_ok = all(((base[(base.station == s) & (base.zs == 10.0) & (base.xh == 30) & (base.zh == 15)].g_level != "FAIL").any()) for s in STATIONS)
    grid = base[base.SL_B == 235.0].groupby(["zs", "xh", "zh"]).g_slope.apply(lambda s: (s != "FAIL").all())
    frac = float(grid.mean())
    one_only = (sum(nom.loc[s, "g_slope"] != "FAIL" for s in STATIONS) == 1) and all(abs(nom.loc[s, "slope"]) <= 4.5 for s in STATIONS)
    if both_slope and both_shape and level_ok and frac >= 2 / 3:
        verdict = "EXPLAINED"
    elif (both_slope and both_shape and level_ok) or one_only:
        verdict = "PARTLY EXPLAINED"
    else:
        verdict = "NOT EXPLAINED"
    V = dict(verdict=verdict, nominal={s: {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in nom.loc[s].items() if k in ("n", "level", "slope", "slope_se", "shape", "g_level", "g_slope", "g_shape")} for s in STATIONS},
             grid_fraction_slope_both_ok=frac, n_grid=int(len(grid)), level_not_fail_some_SLB=level_ok, pipeline_check=chk,
             common_mode_nominal=CM[(CM.zs == 10.0) & (CM.weights == "V^(1/3)") & (CM.sign == 1) & (CM.xh == 30) & (CM.zh == 15) & (CM.ball == "both") & (CM.SL_B == 235.0)][["station", "view", "n", "level", "slope", "slope_se", "shape", "g_level", "g_slope", "g_shape"]].to_dict("records"),
             R1m_m=R1m, bands={s: [float(f) for f in Rw[(Rw.station == s) & Rw.nominal].fc_hz] for s in STATIONS})
    json.dump(V, open(out / "route1_verdict.json", "w"), indent=1, default=float)
    print(json.dumps(V, indent=1, default=float))


# ----------------------------------------------------------------------------------------------- step b
def cmd_air8(out, ew_dir):
    out = Path(out); T = pd.read_csv(out / "tl_runs.csv"); ew = Path(ew_dir)
    xg, yg, vol = array_layout(ew / "ewing_20gun_layout_ofr95228.csv"); w = vol ** (1 / 3)
    rows = []
    for st, (rpos, _) in STATIONS.items():
        d = {}
        for site in ("air9", "air8"):
            pos, hd = site_pos_heading(site); phi = (G.inv(pos[1], pos[0], rpos[1], rpos[0])[0] % 360) - hd
            tl = T[(T.tag == f"builder_{site}_{st}") & (T.src_depth_m == 10.0)].set_index("fc_hz").tl_db
            d[site] = dict(tl=tl, af={f: array_factor(f, phi, xg, yg, w) for f in AIR8_BANDS}, phi=phi, heading=hd)
        for f in AIR8_BANDS:
            D = (d["air8"]["af"][f] - d["air8"]["tl"][f]) - (d["air9"]["af"][f] - d["air9"]["tl"][f])
            rows.append(dict(station=st, fc_hz=f, tl_air9_db=d["air9"]["tl"][f], tl_air8_db=d["air8"]["tl"][f], af_air9_db=d["air9"]["af"][f], af_air8_db=d["air8"]["af"][f],
                             rl_diff_air8_minus_air9_db=D, tl_diff_only_db=-(d["air8"]["tl"][f] - d["air9"]["tl"][f]), heading_air8=d["air8"]["heading"], heading_air9=d["air9"]["heading"]))
    R = pd.DataFrame(rows); R.to_csv(out / "air8_recal.csv", index=False)
    med = R.groupby("station").rl_diff_air8_minus_air9_db.median()
    h01 = "FOLLOWS" if med["H01W"] <= -10 else ("DOES NOT" if med["H01W"] >= -3 else "INCONCLUSIVE")
    h08 = "CONSISTENT" if abs(med["H08S"]) <= 5 else "INCONSISTENT"
    V = dict(median_rl_diff_db=med.to_dict(), H01W=h01, H08S=h08, still_holds=(h01 == "FOLLOWS" and h08 == "CONSISTENT"),
             median_tl_diff_only_db=(-R.groupby("station").tl_diff_only_db.median()).to_dict(), headings=dict(air8=float(R.heading_air8.iloc[0]), air9=float(R.heading_air9.iloc[0])))
    json.dump(V, open(out / "air8_recal_verdict.json", "w"), indent=1, default=float); print(json.dumps(V, indent=1, default=float))


# ----------------------------------------------------------------------------------------------- step d
def cmd_air7(out, corridor_csv, confirm_dir):
    out = Path(out); T = pd.read_csv(out / "tl_runs.csv"); cf = Path(confirm_dir)
    o7 = pd.read_csv(cf / "fig23_CL_air7_bands_DIGITISED.csv").set_index("fc_hz").tl_obs_db
    o9 = pd.read_csv(cf / "fig23_CL_air9_bands_DIGITISED.csv").set_index("fc_hz").tl_obs_db
    a9 = T[(T.tag == "builder_air9_H01W_a7b")].set_index("fc_hz").tl_db
    off = T[T.tag.str.startswith("air7off")].copy(); off["d_km"] = off.tag.str.extract(r"air7off([+-]\d+)_")[0].astype(float)
    pv = off.pivot(index="fc_hz", columns="d_km", values="tl_db")
    cor = pd.read_csv(corridor_csv) if corridor_csv and Path(corridor_csv).exists() else None
    rows = []
    for f in AIR7_BANDS:
        least = float(pv.loc[f].min()); dmin = float(pv.loc[f].idxmin())
        r = dict(fc_hz=f, tl_geo_db=float(pv.loc[f, 0.0]), tl_least_loss_db=least, d_least_km=dmin, tl_air9_H01W_db=float(a9[f]),
                 dtl_obs_db=float(o7.get(f, np.nan) - o9.get(f, np.nan)), tl_obs_air7_db=float(o7.get(f, np.nan)))
        for d in OFFSETS_KM:
            r[f"tl_off{d:+.0f}_db"] = float(pv.loc[f, d])
        if cor is not None and (cor.fc_hz == f).any():
            c = cor[(cor.fc_hz == f) & (cor.src_depth_m == 10.0)].iloc[0]
            r.update(tl_nx2d_db=float(c.tl_nx2d_db), open_weight=float(c.open_weight))
        rows.append(r)
    R = pd.DataFrame(rows)
    for col in ("tl_geo_db", "tl_least_loss_db", "tl_nx2d_db"):
        if col in R:
            R["dmodel_" + col] = R[col] - R.tl_air9_H01W_db
            R["excess_" + col] = R["dmodel_" + col] - R.dtl_obs_db
    R.to_csv(out / "air7_corridor.csv", index=False)
    prim = R[R.fc_hz.isin([31.5, 40.0, 50.0, 63.0])]
    med = {c: float(prim["excess_" + c].median()) for c in ("tl_geo_db", "tl_least_loss_db", "tl_nx2d_db") if "excess_" + c in prim}
    if "tl_nx2d_db" in med and abs(med["tl_nx2d_db"]) <= 10:
        verdict = "REPRODUCED"
    elif abs(med["tl_least_loss_db"]) <= 10:
        verdict = "REPRODUCED AS AN UPPER BOUND"
    else:
        verdict = "NOT REPRODUCED"
    V = dict(verdict=verdict, median_excess_db_31p5_to_63=med, bands_primary=[31.5, 40.0, 50.0, 63.0],
             least_loss_offsets_km=prim.set_index("fc_hz").d_least_km.to_dict())
    json.dump(V, open(out / "air7_verdict.json", "w"), indent=1, default=float); print(R.round(1).to_string()); print(json.dumps(V, indent=1, default=float))


def cmd_tl_ext(sections, at, scratch, out, nproc=3):
    """Amendment 2: +30, +40, +50 km offset paths for air7 -> H01W (exploratory extension)."""
    sec = Path(sections); out = Path(out); pos, _ = site_pos_heading("air7"); rd = STATIONS["H01W"][1]
    jobs = []
    for d in (30.0, 40.0, 50.0):
        b, R = offset_section(pos, STATIONS["H01W"][0], d); b.to_csv(sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", index=False)
        for fc in AIR7_BANDS:
            jobs.append((f"air7off{d:+.0f}_H01W", sec / "builder" / f"bathy_air7off{d:+.0f}_H01W.csv", sec / "builder" / "ssp_air7_H01W.csv", fc, [10.0], rd, scratch, at))
    rows = []
    with Pool(int(nproc)) as P:
        for r in P.imap_unordered(tl_job, jobs):
            rows += r
    E = pd.DataFrame(rows); E["extension"] = True; E.to_csv(out / "tl_runs_ext.csv", index=False)
    print(E.pivot(index="fc_hz", columns="tag", values="tl_db").round(1).to_string())


def ram_job(a):
    """RAM (pyram) band TL at the path end, ram_tl_check settings (dr 2 lambda, dz lambda/20, 9 frequencies, no absorption)."""
    tag, bathy_csv, ssp_csv, fc, zs, rd = a
    from pyram.PyRAM import PyRAM
    b = pd.read_csv(bathy_csv); s = pd.read_csv(ssp_csv)
    rprof, prof = A.build_profiles(b, s); nodes = A.node_profiles(s); keys = sorted(nodes)
    nr = np.array([nodes[k][0] for k in keys]); z = nodes[keys[0]][1]; Cm = np.vstack([nodes[k][2] for k in keys]).T
    D = np.array([p[0] for p in prof])
    if D.max() >= z[-1]:
        z = np.append(z, D.max() + 100.0); Cm = np.vstack([Cm, Cm[-1:]])
    L = rprof[-1] * 1e3; t0 = time.time(); I = []
    for f in fc * 2 ** (np.linspace(-1, 1, 9) / 6):
        lam = 1500.0 / f
        m = PyRAM(f, zs, rd, z, nr * 1e3, Cm, np.array([0.0]), np.array([0.0]), np.array([[A.BOTTOMS["hard"]["cp"]]]), np.array([[A.BOTTOMS["hard"]["rho"]]]),
                  np.array([[A.BOTTOMS["hard"]["ap"]]]), np.column_stack([rprof * 1e3, D]), rmax=L, zmplt=D.max(), dr=2 * lam, dz=lam / 20, ndr=1, ndz=1)
        r = m.run(); rr, tl = r["Ranges"], r["TL Line"]; k = rr >= rr[-1] - 500.0
        I.append(np.mean(10 ** (-tl[k] / 10)))
    x = L / 1000.0 / 6371.0
    return dict(tag=tag, fc_hz=fc, src_depth_m=zs, tl_ram_db=float(-10 * np.log10(np.mean(I)) + 10 * np.log10(x / np.sin(x))), wall_s=time.time() - t0)


def cmd_ram(sections, at, scratch, out, nproc=4, ext=False):
    sec = Path(sections); out = Path(out); rd = STATIONS["H01W"][1]
    if not ext:
        paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv"}
        jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (31.5, 40.0)]
        jobs += [("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, 10.0, rd) for fc in (31.5, 40.0)]
    else:   # amendment 3
        paths = {"air7off+0_H01W": sec / "builder" / "bathy_air7off+0_H01W.csv", "air7off+20_H01W": sec / "builder" / "bathy_air7off+20_H01W.csv", "air7off+50_H01W": sec / "builder" / "bathy_air7off+50_H01W.csv"}
        jobs = [(tag, p, sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for tag, p in paths.items() for fc in (50.0, 63.0)]
        jobs += [("air7off+50_H01W", paths["air7off+50_H01W"], sec / "builder" / "ssp_air7_H01W.csv", fc, 10.0, rd) for fc in (31.5, 40.0)]
        jobs += [("builder_air9_H01W", sec / "builder" / "bathy_air9_H01W.csv", sec / "builder" / "ssp_air9_H01W.csv", fc, 10.0, rd) for fc in (50.0, 63.0)]
    # matched KRAKEN without absorption (same convention as ram_tl_check: no Francois-Garrison in either model)
    krows = []
    for tag, p, sspc, fc, zs, rdd in jobs:
        bth = pd.read_csv(p); ssp = pd.read_csv(sspc); rprof, profiles = A.build_profiles(bth, ssp); L = float(rprof[-1]); root = f"noabs_{tag}_f{fc:g}".replace(".", "p")
        try:
            K.tl_path(scratch, root, fc, profiles, rprof, np.array([L]), [zs], [rdd], A.BOTTOMS["hard"], at, fg=None)
            sh = K.read_shd(Path(scratch) / f"{root}.shd"); x = L / 6371.0
            krows.append(dict(tag=tag, fc_hz=fc, tl_kraken_noabs_db=float(-20 * np.log10(np.abs(sh["p"][0, 0, 0, -1])) + 10 * np.log10(x / np.sin(x)))))
        except RuntimeError:
            krows.append(dict(tag=tag, fc_hz=fc, tl_kraken_noabs_db=np.inf))
    with Pool(int(nproc)) as P:
        R = pd.DataFrame(list(P.imap_unordered(ram_job, jobs)))
    R = R.merge(pd.DataFrame(krows), on=["tag", "fc_hz"])
    f = out / ("air7_ram_ext.csv" if ext else "air7_ram.csv"); R.to_csv(f, index=False); print(R.round(1).to_string(index=False))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sections":
        cmd_sections(*sys.argv[2:5])
    elif cmd == "tl":
        cmd_tl(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))
    elif cmd == "route1":
        cmd_route1(*sys.argv[2:5])
    elif cmd == "air8":
        cmd_air8(*sys.argv[2:4])
    elif cmd == "air7":
        cmd_air7(*sys.argv[2:5])
    elif cmd == "tl_ext":
        cmd_tl_ext(*sys.argv[2:6], *(sys.argv[6:7] or ["3"]))
    elif cmd == "ram":
        cmd_ram(*sys.argv[2:6], *(sys.argv[6:7] or ["4"]))
    elif cmd == "ram_ext":
        cmd_ram(*sys.argv[2:6], int(sys.argv[6]) if len(sys.argv) > 6 else 4, ext=True)
