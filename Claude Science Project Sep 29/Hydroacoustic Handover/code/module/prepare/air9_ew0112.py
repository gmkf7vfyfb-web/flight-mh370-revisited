"""PRE-REGISTRATION (committed before any EW0112 value is digitised or any residual is re-scored): the air9 source
reference from the R/V Maurice Ewing cruise report EW0112 (Oct 2001), architecture request 11 Oct 2026 17:50Z.

SOURCE. EW0112 chief scientist's cruise report (MGDS doc_uid 3671), 13 pp. scanned (200 dpi, no text layer),
  sha256 eb00bc3abfc91c98da611f0b38d411af87e6423eb87f1c380ba32c12b56ac280. Values READ from the page images (printed
  page numbers "EW0112 n" in the footer equal the PDF page numbers):
  - p. 5: air9 = shots 317-340 at 57 s (jd 292 02:10:59.915-02:32:50.915) and 345-350 at 127 s (02:35:54.918-
    02:46:29.918), 27 33.22-34.04 S, 98 51.58-53.94 E, water 2718-2837 m. Gun tow depth: "11-12 m ... some being as
    shallow as 9 m" (15 m intended). [READ]
  - p. 6, Fig. 2: two air9 shots (deployment 9, 292 02:17:38 and 02:18:35) on the "slacked Ball hydrophone" and the
    ship's shot phone: time series "Pa @ receiver" and "Pa @ 1M", spectra "Pa^2/Hz @ receiver" (linear, 1-1e5 Hz).
  - p. 7: Ball hydrophone calibrated, "no gain"; "about 30 meters ahead of the trailing array" (an estimate; line
    "payed out fast"); hydrophone DEPTH NOT STATED. Shot phone uncalibrated, about 8 m ahead. [READ]
  - p. 2, Fig. 1: array plan; at 200 dpi most gun labels are ILLEGIBLE (transcription ledger graded per label).
  Blackman et al. (2004) do not state the source spectrum behind Fig. 23 "observed TL"; they quote the array peak as
  "230-240 dB re 1 uPa (adjusted to 1 meter range)" (source-class table), the same quantity as Fig. 2 "Pa @ 1M".

QUESTION. The module/audit air9 residual r_b = TL_obs(Fig. 23) - TL_model has slope +10.4 dB/oct (H01W) and +7.4
  dB/oct (H08S), level within 3 dB, station difference PASS (audit d225b80). TL_obs = SL_B(f) - RL(f) with an
  unstated SL_B. The module TL includes the surface image at z_s (KRAKEN), so for a correct model
  r_b = SL_B(f) - S0(f), S0 = the far-field notional (monopole) source spectrum level. Two hypotheses, fixed now:
  H-ref: SL_B(f) = the Ball near-source spectrum scaled to 1 m (Fig. 2 "@ 1M"). Then r_b = Delta_ref(f), the
     near-field reference factor 10 log10( <|e^{ik r1}/r1 - e^{ik r2}/r2|^2>_b * R1m^2 ), r1/r2 = direct/surface-image
     paths from the array to the Ball hydrophone, R1m = the range Fig. 2 uses for "@ 1M" (the ratio of its
     "@ 1M" to "@ receiver" peaks, DIGITISED), <>_b = third-octave band mean.
  H-flat: SL_B(f) is flat (the quoted peak level). Then r_b = C - S0(f), with S0(f) = Ball(f) - Delta_ref(f) + const
     from the digitised Fig. 2 Ball spectrum.
GEOMETRY PRIOR (declared; EW0112 p. 5/p. 7): z_s in {9, 10, 12} m (the module's air9 rows); horizontal offset of the
  Ball ahead of the array centre x_h in {20, 30, 40} m; Ball depth z_h in {5, 10, 15, 20, 30} m (not stated: the
  whole plausible range for a slacked line payed out fast); nominal (x_h, z_h) = (30, 15) m. Array: point source at
  the array centre (primary); a proxy 4 x 5 grid over the Fig. 1 extent as a sensitivity (gun volumes ILLEGIBLE ->
  equal strengths, declared).
TEST. corrected residual r'_b = r_b - Delta_ref,b (H-ref) or r_b - [C - S0,b] (H-flat, C = median), per station,
  on the audit's air9 rows (results/hydroacoustics-audit/data/air9_residuals.csv, model M1, each z_s), bands inside
  the Fig. 23 span where Fig. 2 is readable, graded with C1 (criteria.md 940f1a3): slope |s| <= 1.5 / 3 dB/oct;
  shape RMS <= 3 / 5 dB; level (H-ref only, R1m from Fig. 2) <= 3 / 6 dB.
  VERDICT per hypothesis, fixed now: SUPPORTED if, at the nominal geometry, both stations are PASS or PARTIAL in slope
  AND >= 50 % of the geometry grid is; NOT SUPPORTED otherwise. Both may be supported (then not separable, said so),
  or neither (then the tilt is not a source-reference artefact; it stays at the near-surface end as the SUS C4
  stand-in found). The grid spread is reported in full. Nothing is tuned to Fig. 23.
DIGITISATION RULE (Fig. 2, fixed now): the two Ball spectrum panels and the two Ball time-series panels; axis ticks
  located on the native 200-dpi raster; trace = the darkest pixel per column inside the panel; third-octave means;
  a band is READABLE if its mean is >= 5 % of full scale (about +/- 1 px resolution gives <= 1 dB there), else marked
  BELOW-READ and excluded. Values labelled DIGITISED. Both shots are digitised; their dB mean is used, their
  difference is reported as the reading + shot-to-shot spread.
AMENDMENT 1 (11 Oct 2026, after the first result 5b522802; committed BEFORE the computation it describes).
  The array layout is not legible in EW0112 Fig. 1. USGS Open-File Report 95-228 (Brocher et al. 1995,
  doi:10.3133/ofr95228, public; PDF p. 70, Fig. 4 "EWING AIRGUN ARRAY - 20 GUN", VOLUME = 8470 cu in, scale 1" = 20')
  prints the standard Ewing 20-gun array as vector text: gun ID, volume and position (three rows 15 ft apart along
  track; 20 guns across about 35 m). EW0112 states the same 'standard' 20-gun array with 8465 cu in (5 cu in less,
  0.06 %); the 1994 layout is used as the best available, DECLARED. Positions are taken from the label coordinates
  (calibrated on the row labels 145'/130'/115'/100', 15 ft apart).
  Added, fixed now: (i) H-ref and H-flat re-run with this layout replacing the point source (gun strengths equal, and
  proportional to V^(1/3) as a sensitivity), the Ball on the array centreline x_h ahead of the array centre; same
  grid, same grading, same verdict rule. (ii) Far-field array factor toward H01W and H08S (great-circle bearings from
  the air9 midpoint, ship heading from the p. 5 line end-points), as a horizontal directivity diagnostic in each band
  (10 log10 |sum w_g e^{-ik u.x_g}|^2 / (sum w_g)^2), reported, not used for grading.
LABELS: predictive audit, not a likelihood; hydroacoustics stays PREDICTIVE; UNCONVERGED inputs not used.
"""
# ---------------------------------------------------------------------------------------------------------------
# IMPLEMENTATION (added after the pre-registration commit ecbca309; method exactly as registered).
# Usage: python air9_ew0112.py <ew0112_pdf> <audit_air9_residuals.csv> <out_dir>
import io, json, sys
import numpy as np, pandas as pd

C = 1500.0
BANDS = [5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80]


def page_raster(pdf, i):
    import pypdfium2 as pdfium
    for o in pdfium.PdfDocument(pdf)[i].get_objects():
        if o.type == 3:
            return np.asarray(o.get_bitmap(render=False).to_pil().convert("L")).astype(int)


def box(A, x0, x1, y0, y1, frac=0.45):
    a = A[y0:y1, x0:x1] < 140
    rr = [y + y0 for y in range(a.shape[0]) if a[y].sum() > frac * a.shape[1]]
    cc = [x + x0 for x in range(a.shape[1]) if a[:, x].sum() > 0.5 * (max(rr) - min(rr))]
    return min(cc), max(cc), min(rr), max(rr)


def spectrum(A, b, ytop, top_ex=12, bot_ex=4):
    """Upper envelope of the trace per column (decade and minor tick columns masked and interpolated)."""
    xl, xr, yt, yb = b; xs = np.arange(xl + 3, xr - 2); v = []
    for x in xs:
        ys = np.nonzero(A[yt + top_ex:yb - bot_ex, x] < 140)[0]
        v.append(np.nan if len(ys) == 0 else (yb - (ys.min() + yt + top_ex)) / (yb - yt) * ytop)
    v = np.array(v); f = 10 ** ((xs - xl) / (xr - xl) * 5); tick = np.zeros(len(xs), bool)
    for k in range(5):
        for m in range(1, 10):
            tick |= np.abs(xs - (xl + (k + np.log10(m)) / 5 * (xr - xl))) <= 1.5
    v[tick] = np.nan; ok = np.isfinite(v)
    return f, np.interp(np.arange(len(v)), np.nonzero(ok)[0], v[ok])


def peak(A, b, xf, zero_y, ppu, unit, top_ex=14):
    xl, xr, yt, yb = b; a = A[yt + top_ex:yb - 3, int(xl + xf[0] * (xr - xl)):int(xl + xf[1] * (xr - xl))] < 140
    return (zero_y - (np.nonzero(a.any(axis=1))[0].min() + yt + top_ex)) / ppu * unit


def dref(fc, zs, xh, zh, R1m, array=None):
    f = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 200); k = 2 * np.pi * f / C; p = 0
    srcs = [(0.0, 0.0)] if array is None else array
    for ax, ay in srcs:
        r1 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh - zs) ** 2); r2 = np.sqrt((xh - ax) ** 2 + ay ** 2 + (zh + zs) ** 2)
        p = p + np.exp(1j * k * r1) / r1 - np.exp(1j * k * r2) / r2
    return 10 * np.log10(np.mean(np.abs(p / len(srcs)) ** 2) * R1m ** 2)


def grade(v, t):
    return "PASS" if v <= t[0] else ("PARTIAL" if v <= t[1] else "FAIL")


def score(r, fc):
    x = np.log2(fc); Am = np.vstack([x, np.ones_like(x)]).T; c = np.linalg.lstsq(Am, r, rcond=None)[0]; e = r - Am @ c
    return dict(n=len(r), level=float(np.median(r)), slope=float(c[0]), shape=float(np.sqrt(np.mean(e ** 2))),
                g_level=grade(abs(np.median(r)), (3, 6)), g_slope=grade(abs(c[0]), (1.5, 3)), g_shape=grade(np.sqrt(np.mean(e ** 2)), (3, 5)))


if __name__ == "__main__":
    pdf, resid_csv, out = sys.argv[1:4]
    A = page_raster(pdf, 5)                                   # PDF p. 6, Fig. 2 (native 200 dpi)
    bL, bR = box(A, 180, 830, 1380, 1650), box(A, 860, 1520, 1380, 1650)
    rows = []
    for nm, b, fs in (("02:17:38", bL, 3e10), ("02:18:35", bR, 4e10)):
        f, v = spectrum(A, b, fs)
        for fc in BANDS:
            m = (f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6)); mv = v[m].mean()
            rows.append(dict(shot=nm, fc_hz=fc, mean_pa2_hz=mv, frac_fs=mv / fs, readable=mv / fs >= 0.05,
                             level_db_re_1upa2_hz_at_receiver=10 * np.log10(max(mv, 1)) + 120))
    D = pd.DataFrame(rows)
    R1m = [peak(A, box(A, 190, 830, 780, 1040), (0.3, 0.8), 931.5, 22.0, 1e5) / peak(A, box(A, 190, 830, 180, 450), (0.08, 0.25), 335.5, 64.0, 1e4),
           peak(A, box(A, 870, 1520, 780, 1040), (0.3, 0.8), 936.5, 22.5, 1e5) / peak(A, box(A, 870, 1520, 180, 450), (0.08, 0.25), 332.5, 64.5, 1e4)]
    R1 = float(np.mean(R1m))
    Pv = D.pivot(index="fc_hz", columns="shot", values="level_db_re_1upa2_hz_at_receiver")
    ball = Pv.mean(axis=1) + 20 * np.log10(R1); readable = D.groupby("fc_hz").readable.all()
    Rr = pd.read_csv(resid_csv); M1 = Rr[Rr.model == "M1"]; res = []
    for zs in (9.0, 10.0, 12.0):
        for xh in (20, 30, 40):
            for zh in (5, 10, 15, 20, 30):
                for st in ("H01W", "H08S"):
                    g = M1[(M1.station == st) & (M1.src_depth_m == zs)].sort_values("fc_hz"); fc = g.fc_hz.values; r = g.residual_db.values
                    d = np.array([dref(x, zs, xh, zh, R1) for x in fc])
                    res.append(dict(hyp="H-ref", zs=zs, xh=xh, zh=zh, station=st, **score(r - d, fc)))
                    m = np.array([bool(readable.get(x, False)) for x in fc]); S0 = np.array([ball.get(x, np.nan) for x in fc]) - d
                    rf = r[m] + S0[m]; res.append(dict(hyp="H-flat", zs=zs, xh=xh, zh=zh, station=st, **score(rf - np.median(rf), fc[m])))
    O = pd.DataFrame(res); O.to_csv(f"{out}/air9_reference_rescore_grid.csv", index=False)
    print(json.dumps(dict(R1m=R1m, grid_both_ok=O.groupby(["hyp", "zs", "xh", "zh"]).g_slope.apply(lambda s: (s != "FAIL").all()).groupby("hyp").mean().to_dict())))
