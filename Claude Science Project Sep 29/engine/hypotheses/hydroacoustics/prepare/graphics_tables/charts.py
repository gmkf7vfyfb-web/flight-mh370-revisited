"""Charts 1-4 for the potential-signal tables 1 (multi-site) and 2 (single-site). Pete's request M108 (22 Oct 2026, thread a35831fe).

Chart 1  hydrophone records, each panel moved back by its travel time so that the x axis is implied impact time (+/- 20 s around the
         member's own implied time); detection time marked; a coded visibility check per member (check a).
Chart 2  close-up map at the arc position: all-evidence PDF (composer v3.2, D0', layer D0|DS), searched areas, Pleiades objects and the
         Pleiades-conditional PDF (layer D0|P); 50 % and 90 % HPD regions and median latitudes, cross-checked against products-v3.csv
         and the Pleiades module summary (check b).
Chart 3  run J route samples south of the equator; routes that reach the row's position highlighted (check d).
Chart 4  predicted received level at each receiver against the receiver's background noise, for coupling 1e-4, 1e-3, 2.26e-3
         (F-35A value under the module definition, Metz 2023; pending ruling), 1e-2, 1e-1 and the coupling needed for this row (check c).

Data are read through the hydroacoustic registry (registry/registry.py) where an entry exists; other modules' products are read from
mh370-exchange with their README named in the footnote. Usage:
    python charts.py --table1 <table1_multisite.csv> --table2 <table2_single_site.csv> --out <dir> [--top 10 | --all]
Environment: HYDRO_MOD = module root that holds registry/ (default: the read-only checkout named below); HYDRO_WORK = work-branch
checkout (for the Pleiades object files).
"""
from __future__ import annotations
import argparse, io, json, os, re, subprocess, sys, textwrap, time, types, warnings, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

warnings.simplefilter("ignore")
WS = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/a6559afa-0c43-4302-86d9-0e2798dcb1c7"
MOD = Path(os.environ.get("HYDRO_MOD", WS + "/src/mod/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"))
WORK = Path(os.environ.get("HYDRO_WORK", WS + "/src/work"))
EXR = Path("/Users/pete/Downloads/mh370-exchange")
T0 = 1394236800.0
C_KMS, C_SD = 1.482, 0.006
COUPLINGS = [("1e-4", 1e-4), ("1e-3", 1e-3), ("2.26e-3 (F-35A value, Metz 2023)", 2.26e-3), ("1e-2", 1e-2), ("1e-1", 1e-1)]
PANEL_RX = ["H01W", "H08S", "3315", "3376", "3274", "3275"]
RX_NAME = {"H01W": "Cape Leeuwin H01W", "H08S": "Diego Garcia South H08S", "3315": "Perth Canyon 3315", "3376": "Perth Canyon 3376",
           "3274": "Portland 3274", "3275": "Portland 3275", "3250": "Scott Reef 3250"}
VIS_EXCESS_DB, VIS_P_LOCAL, PEAK_WIN_S, NULL_HALF_S = 3.0, 0.05, 3.0, 150.0   # display rule for check a (stated in every footnote)

for p in [MOD / "registry", MOD / "prepare" / "composition_run_j", MOD / "prepare", MOD / "prepare" / "searches_run_j"]:
    if str(p) not in sys.path: sys.path.insert(0, str(p))
pm = types.ModuleType("pyram"); pm2 = types.ModuleType("pyram.PyRAM"); pm2.PyRAM = None; pm.PyRAM = pm2
sys.modules.setdefault("pyram", pm); sys.modules.setdefault("pyram.PyRAM", pm2)   # only ram_tl_check imports it; no RAM run here
from registry import Registry
from pyproj import Geod
from scipy import signal as sg

G = Geod(ellps="WGS84")
REG = Registry()
INPUTS = {}   # id -> (path, status, defects, definition quote head)


def reg_use(id_):
    e = REG.entry(id_)
    q = (e.get("definition") or {}).get("quote") or (e.get("definition") or {}).get("note") or ""
    INPUTS[id_] = dict(path=str(REG.path(id_)), status=e["status"], defects=e.get("defects") or [], definition=str(q)[:300])
    return REG.path(id_)


def ext_use(key, path, readme, layer):
    INPUTS[key] = dict(path=str(path), status="other module (not in the hydro registry)", defects=[], definition=f"README {readme}; {layer}")
    return Path(path)


def hms(s):
    h, m, x = str(s).split(":"); return int(h) * 3600 + int(m) * 60 + float(x)


def fmt(t, d=1):
    t = t % 86400; s = t % 60
    return f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{s:0{3 + d if d else 2}.{d}f}"


def parse_members(s):
    out = []
    for part in str(s).split(" | "):
        m = re.match(r"(\w+) (\d\d:\d\d:\d\d) \[(.+)\]", part.strip()); out.append(dict(rx=m.group(1), t=m.group(2), band=m.group(3)))
    return out


def band_of(b):
    m = re.match(r"([\d.]+)-([\d.]+)", str(b)); return (float(m.group(1)), float(m.group(2))) if m else (5.0, 40.0)


# ------------------------------------------------------------------------------------------------------------------ data
class Data:
    def __init__(self):
        geo = reg_use("in.geometry_sample"); self.RX = json.load(open(geo / "run.json"))["receivers"]
        tlg = reg_use("ex.tl_grid")
        tpj = json.load(open(MOD / "results-data" / "tl_grid_run_j" / "table_points.json"))
        arc = sorted([(v["lat"], v["lon"]) for v in tpj.values() if v["offset_nm"] == 0])
        self.arc_la = np.array([a for a, b in arc]); self.arc_lo = np.array([b for a, b in arc])
        # --- searches detections (statistic, p) for each member
        srch = reg_use("ex.searches")
        ic = pd.read_csv(srch / "imos" / "imos_candidates.csv", dtype={"receiver": str}); pc = pd.read_csv(srch / "panels" / "panel_candidates.csv")
        ic["src"] = "IMOS raw"; pc["src"] = "Kadri Fig. 9 panel " + pc.panel.astype(str)
        self.cands = pd.concat([ic[["receiver", "time_utc", "detector", "band_hz", "statistic", "p", "src"]],
                                pc[["receiver", "time_utc", "detector", "band_hz", "statistic", "p", "src"]]], ignore_index=True)
        # --- Kadri digitised panels and H08S shots
        md = reg_use("in.module_data"); self.kadri = {}
        for pnl, st in [("a", "H01W"), ("b", "H01W"), ("c", "H01W"), ("d", "H08S"), ("e", "H08S")]:
            d = pd.read_csv(md / "kadri_fig9_digitised" / f"kadri-2024-figure9-panel-{pnl}-{st}.csv")
            t = pd.to_datetime(d.utc).astype("int64").values / 1e9 - T0
            self.kadri.setdefault(st, []).append((pnl, t, d.pressure_pa.values))
        self.shots = pd.read_csv(reg_use("in.h08s_shots")).t.values
        # --- IMOS raw
        self.imos_root = reg_use("in.imos_raw")
        import imos_noise as NN, imos_preregistration as PP
        self.NN, self.PP = NN, PP; self.meta = PP.parse_meta()
        self.recs = pd.read_csv(md / "imos" / "recordings.csv"); self.recs["logger"] = self.recs.logger.astype(str)
        self.cal = pd.read_csv(MOD / "results-data" / "imos1d" / "calibration_gain.csv"); self.cal["logger"] = self.cal.logger.astype(str)
        INPUTS["module.results-data/imos1d/calibration_gain.csv"] = dict(path=str(MOD / "results-data/imos1d/calibration_gain.csv"),
            status="module results-data file, no registry entry of its own", defects=[], definition="per-logger band gain (dB) used by the module IMOS chain")
        self._ri = {}; self._seg = {}
        # --- levels (module chain, block 11 Machinery, RAM-grid IMOS TL) + energy sample
        import prereg as RR, common as Cm
        self.RR = RR; self.M = Cm.Machinery(imos_ramgrid=True)
        inj = json.load(open(RR.RD / "injection_run_j" / "summary.json"))
        self.noise = {rx: {q: inj["bg_level_stats"][rx][q] + inj["abs_offset_db"][rx] for q in ("median", "q10", "q90", "q99")} for rx in RR.RECEIVERS}
        self.noise_label = {rx: inj["bg_level_stats"][rx].get("label") for rx in RR.RECEIVERS}
        INPUTS["module.results-data/injection_run_j/summary.json"] = dict(path=str(RR.RD / "injection_run_j/summary.json"),
            status="module results-data file read by the module chain (registry ex.injection is the exchange copy: CURRENT_WITH_CAVEATS D05 D06 D22)",
            defects=["D05", "D06"], definition="bg_level_stats (median, q10, q90, q99 of 1 s background level) + abs_offset_db")
        reg_use("ex.injection")
        S = np.load(geo / "sample.npz"); k = S["w_D0"] > 0
        self.g = {c: S[c][k] for c in ("lat", "lon", "t_unix", "E_j", "tau90_s", "w_D0")}
        # --- maps (composer v3.2), searched areas, Pleiades
        comp = ext_use("composer.maps-v3", EXR / "composer/run-j-views-v3.2/maps-v3.npz", "composer/run-j-views-v3.2/README.md + results-note.md",
                       "layers D0|DS (ALL: core + drift + searched areas, settled seabed) and D0|P (core + Pleiades objects, conditional on H); grid views_common.py (equal-area 0.25 deg)")
        MP = np.load(comp); self.NY, self.NX = int(MP["NY"]), int(MP["NX"])
        self.layers = {k: MP[k].astype(float).reshape(self.NY, self.NX) / MP[k].astype(float).sum() for k in ("D0|DS", "D0|P", "D0|S", "D0|core")}
        A_ = 0.00669437999014; Ee = np.sqrt(A_)
        aq = lambda la: (1 - A_) * (np.sin(np.radians(la)) / (1 - A_ * np.sin(np.radians(la)) ** 2)
                                    - np.log((1 - Ee * np.sin(np.radians(la))) / (1 + Ee * np.sin(np.radians(la)))) / (2 * Ee))
        QS = aq(0.25) - aq(0.0); Q0 = aq(-50.0)
        lo_, hi_ = np.full(self.NY + 1, -90.0), np.full(self.NY + 1, 90.0); qq = Q0 + np.arange(self.NY + 1) * QS
        for _ in range(80):
            mid = 0.5 * (lo_ + hi_); up = aq(mid) < qq; lo_ = np.where(up, mid, lo_); hi_ = np.where(up, hi_, mid)
        self.row_e = 0.5 * (lo_ + hi_); self.lon_e = 78.0 + np.arange(self.NX + 1) * 0.25
        assert self.NY == int(np.ceil((aq(-6.0) - Q0) / QS)) and self.NX == 152, "composer grid differs from views_common.py"
        self.cell_km2 = 0.5 * 6378.137 ** 2 * np.radians(0.25) * QS
        self.products = pd.read_csv(EXR / "composer/run-j-views-v3.2/products-v3.csv")
        ext_use("searched-areas.fields-v2", EXR / "searched-areas/spatial-fields-v2/fields.npz", "searched-areas/spatial-fields-v2/README.md",
                "p2 (Phase 2 coverage), oi2018, oi2025 (Ocean Infinity coverage) per 0.005 deg cell; drawn at 0.5")
        F = np.load(EXR / "searched-areas/spatial-fields-v2/fields.npz")
        self.sf = dict(s=float(F["south"]), w=float(F["west"]), st=float(F["step"]), p2=F["p2"], oi18=F["oi2018"], oi25=F["oi2025"])
        self.plei_tab = json.load(open(ext_use("pleiades.run-j-table", EXR / "pleiades/run-j/pleiades-runj-table.json", "pleiades/run-j/README.md",
                                               "headline gcrel-0.25, D0 x total q=1/3 (C2 silent): mean impact latitude given H")))
        self.plei_obj, self.cosmo = self._pleiades_objects()
        # --- routes (core run J waypoints)
        ext_use("core.run-j-waypoints.routes", EXR / "core/run-j/run-j-waypoints/bto-bfo/seed-*/routes.npy", "core/run-j/run-j-waypoints/run.json",
                "routes.npy: 2,000 route samples per seed, 10 min points from 18:01:49; filter stop epoch m0019b; NOT reweighted to a 00:19 option")
        rr = []
        for sd in sorted((EXR / "core/run-j/run-j-waypoints/bto-bfo").glob("seed-*")):
            rr.append(np.load(sd / "routes.npy"))
        self.routes = np.concatenate(rr); self.n_route_seeds = len(rr)
        rj = json.load(open(EXR / "core/run-j/run-j-waypoints/run.json")); self.route_dt = float(rj["config"]["output"]["route_interval_s"])
        p1, p2 = self.routes[:, -2, :], self.routes[:, -1, :]
        az, _, dd = G.inv(p1[:, 1], p1[:, 0], p2[:, 1], p2[:, 0])
        t_last = hms("18:01:49") + (self.routes.shape[1] - 1) * self.route_dt - 86400   # s after 00:00 8 Mar
        self.route_t_last = t_last
        ext_s = hms("00:19:29") - t_last
        elo, ela, _ = G.fwd(p2[:, 1], p2[:, 0], az, dd * (ext_s / self.route_dt))
        self.route_end = np.c_[ela, elo]
        # --- coastline (GEBCO 2026, coarse)
        gb = reg_use("in.gebco_2026"); gm = json.load(open(gb / "gebco_2026.json"))
        el = np.memmap(gb / gm["elevation_file"], dtype="<i2", mode="r", shape=(gm["nlat"], gm["nlon"]))
        self.cl_lat = np.arange(-48, 10, 0.1); self.cl_lon = np.arange(60, 150, 0.1)
        ii = np.round((self.cl_lat - gm["lat0"]) / gm["step_deg"]).astype(int); jj = np.round((self.cl_lon - gm["lon0"]) / gm["step_deg"]).astype(int)
        oki = (ii >= 0) & (ii < gm["nlat"]); okj = (jj >= 0) & (jj < gm["nlon"])
        E = np.full((len(self.cl_lat), len(self.cl_lon)), -4000, dtype=np.int16); E[np.ix_(oki, okj)] = el[np.ix_(ii[oki], jj[okj])]
        self.elev = E
        self.sigma_extra = (RR.SIGMA_INJ_S, RR.SIGMA_CLOCK_S)

    def _pleiades_objects(self):
        rel = "Claude Science Project Sep 29/engine/hypotheses/pleiades/data/"
        def read(name):
            p = WORK / rel / name
            if p.exists(): return pd.read_csv(p)
            txt = subprocess.run(["git", "-C", str(WORK), "show", "HEAD:" + rel + name], capture_output=True, text=True).stdout
            return pd.read_csv(io.StringIO(txt))
        o = read("ga-rec2017-13-objects.csv"); c = read("cosmo-contacts.csv")
        INPUTS["pleiades.objects"] = dict(path=str(WORK / rel), status="other module data (work branch claude-science-sep29)", defects=[],
                                          definition="ga-rec2017-13-objects.csv (rating 5 objects drawn) and cosmo-contacts.csv (F1-F4)")
        return o[o.rating == 5].copy(), c

    # IMOS ---------------------------------------------------------------------------------------------------------------
    def rec_index(self, lg):
        if lg not in self._ri:
            out = []
            for _, r in self.recs[self.recs.logger == lg].iterrows():
                f = self.imos_root / r.file
                fs, first, n, _ = self.PP.header(f)
                tail = open(f, "rb").read()[-1000:].decode("latin1")
                sub = int(re.search(r"First Data-\S+ \S+ - (\d+)", tail).group(1)) / 65536
                ts = first.timestamp() + sub - self.PP.clock_err(self.meta[lg], first) - T0
                out.append((str(f), fs, ts, ts + n / fs))
            self._ri[lg] = out
        return self._ri[lg]

    def imos(self, lg, t_lo, t_hi, band):
        """Calibrated, band-passed pressure (Pa) of the record covering [t_lo, t_hi] (s after 00:00 UTC 8 Mar). None if no record."""
        for f, fs, a, b in self.rec_index(lg):
            if a <= t_hi and b >= t_lo:
                key = (f, band)
                if key not in self._seg:
                    g = self.cal[self.cal.logger == lg]; lo, hi = band; hi = min(hi, 0.45 * fs); lo = max(lo, 1.0)
                    use = [bb for bb in g.band if float(bb.split("-")[0]) < hi and float(bb.split("-")[1]) > lo]
                    Gd = 10 * np.log10(np.mean([10 ** (g[g.band == bb].gain_db.iloc[0] / 10) for bb in use]))
                    v = self.NN.read_volts(f); x = v / np.sqrt(10 ** ((Gd + self.meta[lg]["sens_db"]) / 10)) * 1e-6
                    y = sg.sosfiltfilt(sg.butter(4, [lo, hi], btype="band", fs=fs, output="sos"), x)
                    dec = 10; y = y[::dec]   # plot/envelope only: 600 Hz after filtering (band <= 40 Hz)
                    keep = dict(list(self._seg.items())[-6:])
                    keep[key] = (a + np.arange(len(y)) * dec / fs, y, fs / dec, os.path.relpath(f, str(self.imos_root)), (a, b))
                    self._seg = keep
                return self._seg[key]
        return None

    def nearest_records(self, lg, t):
        ri = self.rec_index(lg); pr = [b for _, _, a, b in ri if b < t]; nx = [a for _, _, a, b in ri if a > t]
        return (max(pr) if pr else None), (min(nx) if nx else None)

    # geometry -----------------------------------------------------------------------------------------------------------
    def rng_km(self, lat, lon, rx):
        la, lo = self.RX[rx]; return G.inv(lon, lat, lo, la)[2] / 1000

    def sigma_t(self, d_km):
        return float(np.sqrt((d_km * C_SD / C_KMS ** 2) ** 2 + self.sigma_extra[0] ** 2 + self.sigma_extra[1] ** 2))

    def detection(self, rx, t, band):
        c = self.cands[(self.cands.receiver.astype(str) == str(rx)) & (self.cands.time_utc == t)]
        cb = c[c.band_hz.astype(str) == str(band)]
        c = cb if len(cb) else c
        if not len(c): return None
        r = c.sort_values("p").iloc[0]
        return dict(detector=r.detector, statistic=float(r.statistic), p=float(r.p), band=str(r.band_hz), src=r.src, n_rows=len(c))


# ------------------------------------------------------------------------------------------------------------------ rows
def _txt(v):
    return v.strip() if isinstance(v, str) and v.strip() else None


def rows_from_tables(t1, t2, top):
    rows = []
    for r in (t1 if top is None else t1.head(top)).itertuples():
        mem = parse_members(r.members)
        for i, m in enumerate(mem):
            for k in ("shot_check", "shot_dt_s", "shot_residual", "band_check"):
                v = getattr(r, f"m{i + 1}_{k}", None); m[k] = None if (v is None or (isinstance(v, float) and np.isnan(v))) else v
        rows.append(dict(table="table1", id=r.table1_id, kind=r.set_type, lat=float(r.locus_lat), lon=float(r.locus_lon), t0=hms(r.implied_impact_utc),
                         t0_txt=r.implied_impact_utc, members=mem, eta_needed=float(r.eta_at_q99E), x_metz=float(r[t1.columns.get_loc("x_metz_2.26e-3") + 1]),
                         p_prior=float(r.p_prior_eta_ge_needed), lnLR=float(r.lnLR), rank=int(r.rank_lnLR), flags=str(r.flags), E_q99=float(r.E_q99_at_locus_J),
                         pos_kind="arc locus of the time lag between the first two members (table1)", n_arc_loci=int(r.n_arc_loci),
                         lag_s=float(r.lag_s) if np.isfinite(r.lag_s) else np.nan,
                         royer_tb=_txt(r[t1.columns.get_loc("royer_timebase_dependent") + 1]) if "royer_timebase_dependent" in t1.columns else None))
    for r in (t2 if top is None else t2.head(top)).itertuples():
        la, lo = re.match(r"([\d.]+)S\s+([\d.]+)E", r.implied_source).groups()
        m = dict(rx=str(r.rx), t=r.time_utc, band=r.band, det=r.det, p=float(r.p), shot_check=r.shot_check if isinstance(r.shot_check, str) else None,
                 shot_dt_s=r.shot_dt_s, shot_residual=r.shot_residual if isinstance(r.shot_residual, str) else None, band_check=r.band_check)
        rows.append(dict(table="table2", id=r.table2_id, kind="single", lat=-float(la), lon=float(lo), t0=hms(r.implied_impact_utc), t0_txt=r.implied_impact_utc,
                         members=[m], eta_needed=float(r.eta_at_q99E), x_metz=float(r[t2.columns.get_loc("x_metz_2.26e-3") + 1]),
                         p_prior=float(r.p_prior_eta_ge_needed), lnLR=float(r.lnLR), rank=int(r.rank_lnLR), flags=str(r.flags), E_q99=float(r.E_q99_at_src_J),
                         pos_kind="posterior-weighted mean of run J impacts that match the arrival time (table2 implied_source)", n_arc_loci=None, lag_s=np.nan,
                         royer_tb=_txt(r[t2.columns.get_loc("royer_timebase_dependent") + 1]) if "royer_timebase_dependent" in t2.columns else None))
    return rows


# ------------------------------------------------------------------------------------------------------------------ style
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

BASE, ANN, TICK = 8, 7, 6
plt.rcParams.update({"font.size": BASE, "axes.titlesize": BASE, "axes.labelsize": BASE, "xtick.labelsize": TICK, "ytick.labelsize": TICK,
                     "legend.fontsize": ANN, "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.direction": "out", "ytick.direction": "out", "savefig.dpi": 220, "font.family": "DejaVu Sans"})
C_IMPACT, C_DET, C_TRACE, C_ENV = "#d95f02", "#1b9e77", "#4d4d4d", "#1f78b4"


def footnote(fig, plain, tech, y=None, width=165):
    txt = "Plain words: " + plain + "\nTechnical: " + tech
    lines = "\n".join(textwrap.fill(p, width) for p in txt.split("\n"))
    fig.text(0.01, -0.005 if y is None else y, lines, fontsize=5.4, va="top", ha="left")


def row_title(row):
    kind = {"pair": "two-receiver", "triple": "three-receiver", "single": "one-receiver"}[row["kind"]]
    return f"Table {row['table'][-1]} row {row['id']} ({kind} set, register rank {row['rank']} by log-likelihood ratio, ln LR {row['lnLR']:.2f})"


# ------------------------------------------------------------------------------------------------------------------ chart 1
def envelope(t, p, dt=0.05, win=1.0):
    """1 s RMS envelope on a uniform grid (dt). Non-uniform input (digitised traces) is linearly interpolated first."""
    tg = np.arange(t[0], t[-1], dt); pg = np.interp(tg, t, p); n = max(1, int(round(win / dt)))
    return tg, np.sqrt(np.convolve(pg ** 2, np.ones(n) / n, mode="same"))


def visibility(tg, eg, t_det):
    """check a: peak of the 1 s envelope within +/-3 s of the detection vs (i) the median envelope over +/-20 s and (ii) the
    maxima of 6 s windows over +/-150 s (excluding the detection window): p_local = share of null windows whose max >= peak."""
    w = np.abs(tg - t_det) <= PEAK_WIN_S; pan = np.abs(tg - t_det) <= 20.0
    if w.sum() < 3 or pan.sum() < 10: return None
    peak = float(eg[w].max()); t_peak = float(tg[w][np.argmax(eg[w])]); med = float(np.median(eg[pan]))
    nul = (np.abs(tg - t_det) <= NULL_HALF_S) & ~w
    dt = np.median(np.diff(tg)); n = int(round(2 * PEAK_WIN_S / dt)); idx = np.where(nul)[0]
    mx = []
    if len(idx) > n:
        seg = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        for s in seg:
            for a in range(0, len(s) - n + 1, n): mx.append(eg[s[a:a + n]].max())
    mx = np.array(mx); pl = float((np.sum(mx >= peak) + 1) / (len(mx) + 1)) if len(mx) else np.nan
    exc = 20 * np.log10(peak / med) if med > 0 else np.nan
    vis = bool(np.isfinite(exc) and exc >= VIS_EXCESS_DB and np.isfinite(pl) and pl <= VIS_P_LOCAL)
    return dict(peak_excess_db=round(exc, 2), t_peak_minus_det_s=round(t_peak - t_det, 2), p_local=round(pl, 4) if np.isfinite(pl) else None,
                n_null_windows=int(len(mx)), null_span_s=round(float(nul.sum() * dt), 1), visible=vis)


def chart1(D, row, outdir):
    L, Lo, t0 = row["lat"], row["lon"], row["t0"]
    fig, axs = plt.subplots(len(PANEL_RX), 1, figsize=(7.2, 1.42 * len(PANEL_RX) + 0.6))
    checks = []; any_shift = False
    for ax, rx in zip(axs, PANEL_RX):
        d = D.rng_km(L, Lo, rx); tt = d / C_KMS; sig = D.sigma_t(d)
        mem = [m for m in row["members"] if m["rx"] == rx]
        m = mem[0] if mem else None
        band = band_of(m["band"]) if m else (5.0, 40.0)
        x_det = (hms(m["t"]) - tt - t0) if m else None
        xc = 0.0 if (x_det is None or abs(x_det) <= 15) else x_det
        if xc: any_shift = True
        lo, hi = xc - 20, xc + 20
        a_lo, a_hi = t0 + tt + lo, t0 + tt + hi                    # arrival-time window at this receiver
        got = False; src = ""; tg = eg = None; ck_cov = 0.0
        if rx in ("H01W", "H08S"):
            parts = [(pn, t, p) for pn, t, p in D.kadri[rx] if t[0] <= a_hi + NULL_HALF_S and t[-1] >= a_lo - NULL_HALF_S]
            if parts:
                t = np.concatenate([q[1] for q in parts]); p = np.concatenate([q[2] for q in parts]); o = np.argsort(t); t, p = t[o], p[o]
                mk = (t >= a_lo) & (t <= a_hi)
                if mk.any():
                    got = True; src = "Kadri (2024) Fig. 9 panel " + "+".join(q[0] for q in parts) + ", digitised"
                    ax.plot(t[mk] - tt - t0, p[mk], color=C_TRACE, lw=0.4)
                    tg, eg = envelope(t, p)
            unit = "Pa (digitised)"
        else:
            seg = D.imos(rx, a_lo, a_hi, band)
            if seg is not None:
                t, p, fs, fn, (ra, rb) = seg; mk = (t >= a_lo) & (t <= a_hi)
                if mk.any():
                    got = True; src = f"IMOS raw {fn}, {band[0]:g}-{band[1]:g} Hz"
                    ax.plot(t[mk] - tt - t0, p[mk], color=C_TRACE, lw=0.25)
                    tg, eg = envelope(t, p, dt=0.02)
            unit = "Pa"
        if got:
            me = (tg >= a_lo) & (tg <= a_hi)
            cov = float((tg[me].max() - tg[me].min()) / (a_hi - a_lo)) if me.sum() > 1 else 0.0
            ck_cov = round(cov, 3)
            if cov < 0.9:
                ax.text(0.5, 0.06, f"record covers {100 * cov:.0f} % of this window; no data held for the rest", transform=ax.transAxes,
                        ha="center", va="bottom", fontsize=TICK, color="#636363")
            ax.plot(tg[me] - tt - t0, eg[me], color=C_ENV, lw=0.9)
            yl = np.nanmax(np.abs(ax.get_ylim())); ax.set_ylim(-yl, yl)
        ax.axvspan(-sig, sig, color="#fdd0a2", lw=0, zorder=0)
        ax.axvline(0, color=C_IMPACT, lw=0.9, zorder=1)
        if rx == "H08S":
            sh = D.shots[(D.shots >= a_lo) & (D.shots <= a_hi)] - tt - t0
            for s in sh: ax.axvline(s, ymin=0.9, ymax=1.0, color="#7570b3", lw=0.8)
        ck = dict(rx=rx, member=bool(m), range_km=round(d, 1), travel_s=round(tt, 2), sigma_t_s=round(sig, 2), data=got, source=src,
                  window_coverage=(ck_cov if got else 0.0))
        head = f"{RX_NAME[rx]}: {d:,.0f} km, travel time {tt:,.1f} s"
        if m:
            det = D.detection(rx, m["t"], m["band"])
            ax.axvline(x_det, color=C_DET, lw=1.1, ls="--", zorder=3)
            ck.update(det_time=m["t"], band=m["band"], x_det_s=round(x_det, 2), detector=det)
            dtxt = f"{det['detector']} statistic {det['statistic']:.3g}, p {det['p']:.3g}" if det else "detector row not found in the searches tables"
            head += f" | detection {m['t']} UTC, {m['band']} Hz, {dtxt}"
            if m.get("shot_check") == "COINCIDENT_WITH_SHOT":
                head += f" | airgun shot {float(m['shot_dt_s']):+.2f} s"
            if rx == "H01W" and row.get("royer_tb"):
                ax.text(0.01, 0.22, textwrap.fill("Royer 2016 time-base dependent: matches a Royer event only on the uncorrected Fig. 4 time base, "
                        "not on Table 5 / bias-corrected marks: " + row["royer_tb"], 150), transform=ax.transAxes, ha="left", va="bottom", fontsize=TICK,
                        color="#6a3d9a", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
                ck["royer_timebase_dependent"] = row["royer_tb"]
            if got:
                v = visibility(tg, eg, hms(m["t"])); ck["visibility"] = v
                if v is None or not v["visible"]:
                    ax.text(0.98, 0.84, "detection not visible at this scale", transform=ax.transAxes, ha="right", va="top", fontsize=ANN, color="#b2182b")
                vt = "visibility check not computable" if v is None else (f"envelope peak {v['peak_excess_db']:+.1f} dB over the panel median, "
                                                                          f"local p {v['p_local']} ({v['n_null_windows']} windows of 6 s)")
                ax.text(0.01, 0.84, vt, transform=ax.transAxes, ha="left", va="top", fontsize=TICK, color="#333333")
        if not got:
            if rx in ("H01W", "H08S"):
                nx = " (outside the published Fig. 9 panels: H01W 00:27-00:57, H08S 01:00-01:20 UTC)"
            else:
                pr, nx_ = D.nearest_records(rx, a_lo)
                nx = f" (record before ends {fmt(pr, 0) if pr else '-'}, next starts {fmt(nx_, 0) if nx_ else '-'} UTC)"
            ax.text(0.5, 0.5, "no data held at this time" + nx, transform=ax.transAxes, ha="center", va="center", fontsize=ANN, color="#636363")
            ax.set_yticks([])
        else:
            ax.set_ylabel(unit, fontsize=TICK)
        if xc:
            head += f" | panel re-centred on the member ({xc:+.0f} s from the row impact time)"
        ax.set_title(head, loc="left", fontsize=TICK, pad=2)
        ax.set_xlim(lo, hi)
        tk = np.arange(np.ceil(lo / 5) * 5, hi + 0.1, 5); ax.set_xticks(tk)
        ax.set_xticklabels([f"{x:+.0f}" for x in tk])
        checks.append(ck)
    axs[-1].set_xlabel(f"seconds from the implied impact time {fmt(t0)} UTC 8 March 2014 (each record moved back by its own travel time)")
    fig.suptitle(row_title(row) + f"\nRecords at each hydrophone aligned to an impact at {abs(L):.2f} S {Lo:.2f} E, {fmt(t0)} UTC",
                 x=0.01, ha="left", fontsize=BASE)
    h = [Line2D([0], [0], color=C_TRACE, lw=0.6), Line2D([0], [0], color=C_ENV, lw=0.9), Line2D([0], [0], color=C_IMPACT, lw=0.9),
         Patch(color="#fdd0a2"), Line2D([0], [0], color=C_DET, lw=1.1, ls="--"), Line2D([0], [0], color="#7570b3", lw=0.8)]
    lab = ["pressure record", "1 s RMS envelope", "implied impact time", "timing uncertainty, 1 sigma", "detection time (table member)", "airgun shot (Diego Garcia)"]
    fig.legend(h, lab, ncol=6, loc="upper left", bbox_to_anchor=(0.01, 0.955), fontsize=TICK, handlelength=1.6)
    nvis = [c for c in checks if c.get("member") and c.get("data")]
    plain = ("Each panel is one hydrophone. We moved each record back by the time that sound needs to go from the position on the map to "
             "that hydrophone. If the sound came from that position at that time, it would show at zero in every panel. The green dashed line "
             "is the detection that put this row in the table. Red text says when the detection is not clear on this plot. Grey text says when "
             "we hold no record for that time. This chart does not show that any detection comes from the aircraft.")
    tech = (f"Position: {row['pos_kind']}, {abs(L):.3f} S {Lo:.3f} E; implied impact {row['t0_txt']} (table). Travel time = WGS-84 geodesic range / "
            f"{C_KMS} km/s; sigma = sqrt((range x {C_SD}/c^2)^2 + {D.sigma_extra[0]:g}^2 + {D.sigma_extra[1]:g}^2) s (sound speed, injection, clock; "
            f"block 11 values). IMOS: raw .DAT, module clock correction and band gains (calibration_gain.csv), 4th-order Butterworth zero-phase in the "
            f"member's detection band (5-40 Hz on other panels). Kadri: digitised Fig. 9 polylines (~14.5 points/s; his 5 Hz high-pass + 2-40 Hz "
            f"band-pass), no extra filter, envelope resolution only. Visibility rule (display only, not a detection test): 1 s RMS envelope peak "
            f"within +/-{PEAK_WIN_S:g} s of the detection >= {VIS_EXCESS_DB:g} dB over the median of the +/-20 s window AND local p <= {VIS_P_LOCAL} "
            f"against 6 s window maxima over +/-{NULL_HALF_S:g} s of the held record. Detector, statistic and p: lowest-p row at that receiver, time and band in run-j-searches "
            f"(ex.searches, defects D06 D24 D26). H08S shots from h08s_template_shots.csv; a shot coincidence is a label, not an exclusion. Scott Reef 3250 not "
            f"shown (blocked path, no information). OHASISBIO: no waveform data held. Flags: {row['flags']}. "
            + (f"Royer time-base dependent (table column royer_timebase_dependent): the H01W member matches a Royer 2016 event only on the "
               f"UNCORRECTED Fig. 4 time base; on Table 5 / bias-corrected marks it does not ({row['royer_tb']}). " if row.get("royer_tb") else "")
            + "PREDICTIVE, NOT CALIBRATED; C1, C2.")
    footnote(fig, plain, tech)
    fig.subplots_adjust(hspace=0.62, top=0.885, bottom=0.07, left=0.08, right=0.99)
    fn = Path(outdir) / "chart1.png"; fig.savefig(fn, bbox_inches="tight"); plt.close(fig)
    return str(fn), dict(panels=checks, recentred=any_shift,
                         members_visible=sum(1 for c in nvis if c.get("visibility") and c["visibility"]["visible"]), members_with_data=len(nvis),
                         members_total=len(row["members"]))


# ------------------------------------------------------------------------------------------------------------------ chart 2
def hpd_mask(m, q):
    v = np.sort(m.ravel())[::-1]; c = np.cumsum(v); thr = v[min(np.searchsorted(c, q), len(v) - 1)]; return m >= thr


def med_lat(D, m):
    rm = m.sum(1); c = np.cumsum(rm); i = int(np.searchsorted(c, 0.5)); f = (0.5 - (c[i - 1] if i > 0 else 0)) / rm[i]
    return float(D.row_e[i] + f * (D.row_e[i + 1] - D.row_e[i]))


def hpd_level_at(D, m, lat, lon):
    """smallest HPD level (mass share) whose region contains the point."""
    i = int(np.searchsorted(D.row_e, lat) - 1); j = int((lon - 78.0) // 0.25)
    if not (0 <= i < D.NY and 0 <= j < D.NX): return None
    v = m[i, j]; return float(m[m > v].sum() + v)


def check_b(D):
    """check b: map medians/HPD areas vs composer products-v3.csv and the Pleiades module summary. Raises on disagreement."""
    ph = D.products[(D.products.variant == "head") & (D.products.option == "D0") & (D.products.family == "all") & (D.products.context == "mix")].set_index("product")
    out = {}
    for key, pk in [("D0|DS", "DS"), ("D0|P", "P")]:
        m = D.layers[key]
        out[key] = dict(product=ph.loc[pk, "product_name"], median_lat_map=round(med_lat(D, m), 3), median_lat_products=round(float(ph.loc[pk, "median_lat"]), 3),
                        hpd50_km2_map=round(hpd_mask(m, .5).sum() * D.cell_km2), hpd50_km2_products=round(float(ph.loc[pk, "hpd50_km2"])),
                        hpd90_km2_map=round(hpd_mask(m, .9).sum() * D.cell_km2), hpd90_km2_products=round(float(ph.loc[pk, "hpd90_km2"])))
    pl = D.plei_tab["variants"]["head"]["D0 x total q=1/3 (C2 silent)"]["gcrel-0.25"]["mean_lat"]
    out["pleiades_module_mean_impact_lat_given_H"] = round(float(pl), 3)
    PM = np.load(EXR / "pleiades/run-j/maps/map-D0.npz"); post = PM["post"].astype(float); plat = -44.975 + np.arange(post.shape[0]) * 0.05
    out["pleiades_map_D0_post_median_lat_FLIGHT_ONLY"] = round(float(np.interp(0.5, np.cumsum(post.sum(1)) / post.sum(), plat)), 3)
    ok = all(abs(out[k]["median_lat_map"] - out[k]["median_lat_products"]) < 0.05 and abs(out[k]["hpd90_km2_map"] / out[k]["hpd90_km2_products"] - 1) < 0.02
             for k in ("D0|DS", "D0|P")) and abs(out["D0|P"]["median_lat_map"] - out["pleiades_module_mean_impact_lat_given_H"]) < 0.3
    out["pass"] = bool(ok)
    out["rule"] = "map median within 0.05 deg and 90 % HPD area within 2 % of products-v3.csv; Pleiades-conditional median within 0.3 deg of the Pleiades module mean (mean impact vs median seabed)"
    if not ok: raise RuntimeError("check b failed: " + json.dumps(out))
    return out


def arc_sigma_deg(D, row):
    """along-arc 1-sigma of the locus from the first two members' timing sigmas (multi-site rows only)."""
    if row["table"] != "table1": return None
    m1, m2 = row["members"][:2]; fla = np.linspace(D.arc_la.min(), D.arc_la.max(), 4001); flo = np.interp(fla, D.arc_la, D.arc_lo)
    d1 = np.array([D.rng_km(a, b, m1["rx"]) for a, b in zip(fla[::20], flo[::20])]); d2 = np.array([D.rng_km(a, b, m2["rx"]) for a, b in zip(fla[::20], flo[::20])])
    lag = (d2 - d1) / C_KMS; dl = np.gradient(lag, fla[::20]); g = float(np.interp(row["lat"], fla[::20], dl))
    s = np.hypot(D.sigma_t(D.rng_km(row["lat"], row["lon"], m1["rx"])), D.sigma_t(D.rng_km(row["lat"], row["lon"], m2["rx"])))
    return float(s / abs(g)) if g != 0 else None, float(s), g


def chart2(D, row, outdir, CB):
    L, Lo = row["lat"], row["lon"]
    la0, la1 = max(-49.5, L - 3.5), min(-6.5, L + 3.5); lo0, lo1 = max(78.5, Lo - 4.5), min(115.5, Lo + 4.5)
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    DS = D.layers["D0|DS"]; P = D.layers["D0|P"]
    dens = DS / DS.max()
    pc = ax.pcolormesh(D.lon_e, D.row_e, np.ma.masked_less(dens, 1e-3), cmap="Blues", vmin=0, vmax=1, shading="flat", zorder=0)
    yc = 0.5 * (D.row_e[1:] + D.row_e[:-1]); xc = 0.5 * (D.lon_e[1:] + D.lon_e[:-1])
    for q, lw in [(0.5, 1.4), (0.9, 0.8)]:
        ax.contour(xc, yc, hpd_mask(DS, q).astype(float), levels=[0.5], colors=["#08306b"], linewidths=lw, zorder=3)
    near = [(r.latitude, r.longitude) for r in D.plei_obj.itertuples() if lo0 <= r.longitude <= lo1 and la0 <= r.latitude <= la1]
    dmin = float(np.min(G.inv(D.plei_obj.longitude.values, D.plei_obj.latitude.values, np.full(len(D.plei_obj), Lo), np.full(len(D.plei_obj), L))[2]) / 1000)
    show_p = len(near) > 0
    if show_p:
        for q, lw in [(0.5, 1.4), (0.9, 0.8)]:
            ax.contour(xc, yc, hpd_mask(P, q).astype(float), levels=[0.5], colors=["#7a0177"], linewidths=lw, linestyles="--", zorder=3)
        ax.scatter(D.plei_obj.longitude, D.plei_obj.latitude, s=6, c="k", marker="o", zorder=5, lw=0)
        ax.scatter(D.cosmo.longitude, D.cosmo.latitude, s=22, facecolors="none", edgecolors="k", marker="^", zorder=5, lw=0.7)
    sf = D.sf; k = 10
    flat = sf["s"] + (np.arange(sf["p2"].shape[0])[::k] + 0.5) * sf["st"]; flon = sf["w"] + (np.arange(sf["p2"].shape[1])[::k] + 0.5) * sf["st"]
    ax.contourf(flon, flat, (sf["p2"][::k, ::k] > 0.5).astype(float), levels=[0.5, 1.5], colors=["#bdbdbd"], alpha=0.55, zorder=1)
    ax.contour(flon, flat, sf["oi18"][::k, ::k], levels=[0.5], colors=["#238b45"], linewidths=0.8, zorder=2)
    ax.contour(flon, flat, sf["oi25"][::k, ::k], levels=[0.5], colors=["#e7298a"], linewidths=0.8, zorder=2)
    ax.plot(D.arc_lo, D.arc_la, color="k", lw=0.7, zorder=4)
    sa = arc_sigma_deg(D, row)
    if sa and sa[0]:
        for ns, lw in [(2, 1.5), (1, 3.5)]:
            ll = np.linspace(L - ns * sa[0], L + ns * sa[0], 50); ax.plot(np.interp(ll, D.arc_la, D.arc_lo), ll, color="#e31a1c", lw=lw, alpha=0.55 if ns == 2 else 0.9, zorder=6, solid_capstyle="butt")
    ax.scatter([Lo], [L], marker="*", s=140, c="#e31a1c", edgecolors="k", lw=0.5, zorder=7)
    ax.set_xlim(lo0, lo1); ax.set_ylim(la0, la1); ax.set_aspect(1 / np.cos(np.radians(L)))
    ax.set_xlabel("longitude (deg E)"); ax.set_ylabel("latitude (deg; negative = south)")
    ax.set_title(row_title(row) + f"\nPosition {abs(L):.2f} S {Lo:.2f} E against the sea-floor probability map, searched areas and Pleiades objects",
                 loc="left", fontsize=BASE)
    h = [Patch(color=plt.cm.Blues(0.6)), Line2D([0], [0], color="#08306b", lw=1.4), Line2D([0], [0], color="#08306b", lw=0.8),
         Patch(color="#bdbdbd", alpha=0.55), Line2D([0], [0], color="#238b45", lw=0.8), Line2D([0], [0], color="#e7298a", lw=0.8),
         Line2D([0], [0], color="k", lw=0.7), Line2D([0], [0], marker="*", color="w", markerfacecolor="#e31a1c", markeredgecolor="k", markersize=10)]
    lab = ["probability, all evidence (darker = higher)", "50 % region, all evidence", "90 % region, all evidence", "searched 2014-17 (Phase 2)",
           "searched 2018 (Ocean Infinity)", "searched 2025 (Ocean Infinity)", "7th arc", "position in this row"]
    if sa and sa[0]:
        h.append(Line2D([0], [0], color="#e31a1c", lw=3.5)); lab.append("position 1 sigma / 2 sigma along the arc")
    if show_p:
        h += [Line2D([0], [0], color="#7a0177", lw=1.4, ls="--"), Line2D([0], [0], color="#7a0177", lw=0.8, ls="--"),
              Line2D([0], [0], marker="o", color="w", markerfacecolor="k", markersize=4), Line2D([0], [0], marker="^", color="w", markerfacecolor="w", markeredgecolor="k", markersize=6)]
        lab += ["50 % region if the Pleiades objects are debris", "90 % region if the Pleiades objects are debris", "Pleiades objects (rating 5)", "COSMO-SkyMed contacts"]
    ax.legend(h, lab, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=TICK)
    lvDS = hpd_level_at(D, DS, L, Lo); lvP = hpd_level_at(D, P, L, Lo)
    b = CB
    plain = ("Blue shows where the aircraft is most likely on the sea floor when we use all the evidence except the hydrophones. "
             "The lines show the smallest areas that hold 50 % and 90 % of that probability. Grey and the coloured outlines are areas searched before. "
             + ("The dashed purple lines show the same areas if the Pleiades satellite objects are debris from the aircraft. " if show_p else
                f"The Pleiades objects are not in this map area (nearest {dmin:,.0f} km), so their map is not shown. ")
             + "The red star is the position for this row. It is not a find.")
    tech = (f"Map: composer v3.2 maps-v3.npz, 00:19 option D0' (data held out), settled sea floor, equal-area 0.25 deg cells; layer D0|DS = "
            f"'{b['D0|DS']['product']}': median {abs(b['D0|DS']['median_lat_map']):.2f} S, 50 % HPD {b['D0|DS']['hpd50_km2_map']/1e3:,.0f}k km2, "
            f"90 % HPD {b['D0|DS']['hpd90_km2_map']/1e3:,.0f}k km2 (products-v3.csv: {abs(b['D0|DS']['median_lat_products']):.2f} S, "
            f"{b['D0|DS']['hpd50_km2_products']/1e3:,.0f}k / {b['D0|DS']['hpd90_km2_products']/1e3:,.0f}k). Layer D0|P = '{b['D0|P']['product']}': median "
            f"{abs(b['D0|P']['median_lat_map']):.2f} S, 50 % HPD {b['D0|P']['hpd50_km2_map']/1e3:,.0f}k km2, 90 % HPD {b['D0|P']['hpd90_km2_map']/1e3:,.0f}k km2; "
            f"Pleiades module mean impact latitude given H {abs(b['pleiades_module_mean_impact_lat_given_H']):.2f} S (pleiades-runj-table.json, gcrel-0.25, "
            f"D0 total q=1/3). Hydroacoustics has zero weight in these maps. Position lies at the {100*lvDS:.0f} % HPD level of D0|DS"
            + (f" and the {100*lvP:.0f} % level of D0|P" if lvP is not None else "") + ". "
            + (f"Along-arc 1 sigma {sa[0]:.2f} deg from lag sigma {sa[1]:.1f} s (timing sigmas of members 1-2; across-arc position fixed by the arc line). "
               if sa and sa[0] else f"Position: {row['pos_kind']}; no position uncertainty is given in the table. ")
            + (f"Arc loci for this lag: {row['n_arc_loci']} (table keeps the one with most D0 mass within 1 deg). " if row["n_arc_loci"] else "")
            + "Searched areas: searched-areas/spatial-fields-v2 fields.npz (p2, oi2018, oi2025 drawn at 0.5). Pleiades objects: "
              "pleiades/data/ga-rec2017-13-objects.csv rating 5, cosmo-contacts.csv. 7th arc: TL grid table points, offset 0.")
    footnote(fig, plain, tech, y=0.13, width=150)
    fig.subplots_adjust(left=0.09, right=0.66, top=0.9, bottom=0.2)
    fn = Path(outdir) / "chart2.png"; fig.savefig(fn, bbox_inches="tight"); plt.close(fig)
    return str(fn), dict(pleiades_shown=show_p, nearest_pleiades_object_km=round(dmin, 1), hpd_level_DS=round(lvDS, 3) if lvDS else None,
                         hpd_level_P=round(lvP, 3) if lvP else None, along_arc_sigma_deg=(round(sa[0], 3) if sa and sa[0] else None),
                         lag_sigma_s=(round(sa[1], 2) if sa else None), check_b_pass=CB["pass"])


# ------------------------------------------------------------------------------------------------------------------ chart 3
def chart3(D, row, outdir, radius_km=50.0):
    L, Lo = row["lat"], row["lon"]
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    R = D.routes
    pts = R.reshape(-1, 2); keep = pts[:, 0] <= 0
    H, xe, ye = np.histogram2d(pts[keep, 1], pts[keep, 0], bins=[np.arange(60, 126, 0.5), np.arange(-46, 0.01, 0.5)])
    ax.pcolormesh(xe, ye, np.ma.masked_equal(np.log10(H.T + 1), 0), cmap="Greys", vmin=0, vmax=np.log10(H.max() + 1) * 1.1, zorder=0)
    d = G.inv(D.route_end[:, 1], D.route_end[:, 0], np.full(len(R), Lo), np.full(len(R), L))[2] / 1000
    sel = np.where(d <= radius_km)[0]
    rng = np.random.default_rng(1)
    show = sel if len(sel) <= 300 else rng.choice(sel, 300, replace=False)
    for i in show:
        r = R[i]; m = r[:, 0] <= 0.5
        ax.plot(np.r_[r[m, 1], D.route_end[i, 1]], np.r_[r[m, 0], D.route_end[i, 0]], color="#d95f02", lw=0.35, alpha=0.5, zorder=2)
    ax.contour(D.cl_lon, D.cl_lat, D.elev, levels=[0], colors=["#525252"], linewidths=0.6, zorder=3)
    ax.plot(D.arc_lo, D.arc_la, color="k", lw=0.7, zorder=3)
    ax.scatter([Lo], [L], marker="*", s=150, c="#e31a1c", edgecolors="k", lw=0.5, zorder=6)
    for rx in ["H01W", "3315", "3274"]:
        la, lo = D.RX[rx]
        if lo <= 125: ax.scatter([lo], [la], marker="v", s=22, c="#1f78b4", zorder=5)
    ax.set_xlim(60, 125); ax.set_ylim(-46, 0); ax.set_aspect(1 / np.cos(np.radians(-23)))
    ax.set_xlabel("longitude (deg E)"); ax.set_ylabel("latitude (deg; negative = south)")
    ax.set_title(row_title(row) + f"\nFlight paths from the satellite-data model that end within {radius_km:.0f} km of {abs(L):.2f} S {Lo:.2f} E",
                 loc="left", fontsize=BASE)
    h = [Patch(color="#969696"), Line2D([0], [0], color="#d95f02", lw=1), Line2D([0], [0], color="k", lw=0.7),
         Line2D([0], [0], marker="*", color="w", markerfacecolor="#e31a1c", markeredgecolor="k", markersize=10),
         Line2D([0], [0], marker="v", color="w", markerfacecolor="#1f78b4", markersize=6)]
    ax.legend(h, ["all sampled paths, density (log)", f"paths that reach this position ({len(sel):,} of {len(R):,})", "7th arc", "position in this row",
                  "hydrophone (Cape Leeuwin, Perth Canyon)"], loc="lower left", fontsize=TICK)
    plain = ("Grey shows where the sampled flight paths go south of the equator. Orange paths are the ones that end near the red star at the time "
             "of the last satellite log-on. The map shows only the satellite and flight model, not the hydrophone data.")
    tech = (f"Route samples: core run J, run-j-waypoints stratum (0.998 of the mixture), bto-bfo, {D.n_route_seeds} seeds x {R.shape[0]//D.n_route_seeds:,} "
            f"route samples (routes.npy; {R.shape[1]} points every {D.route_dt:.0f} s from 18:01:49 to {fmt(D.route_t_last, 0)} UTC; run.json stop epoch "
            f"m0019b). Each path is extended along its last leg at constant speed to 00:19:29 UTC; 'reach' = extended end within {radius_km:.0f} km. "
            f"The route samples carry equal weight and are NOT reweighted to the 00:19 option D0' (the composer maps are). "
            f"{'Up to 300 of the selected paths drawn at random (seed 1). ' if len(sel) > 300 else ''}"
            f"{'FEW PATHS (<20): read the orange set as indicative only. ' if len(sel) < 20 else ''}Coast: GEBCO 2026 elevation 0 m at 0.1 deg.")
    footnote(fig, plain, tech, width=165)
    fn = Path(outdir) / "chart3.png"; fig.savefig(fn, bbox_inches="tight"); plt.close(fig)
    return str(fn), dict(n_routes_total=int(len(R)), n_routes_reaching=int(len(sel)), radius_km=radius_km, posterior="core run J waypoints route samples, not reweighted to D0'",
                         route_last_point_utc=fmt(D.route_t_last, 0), extended_to="00:19:29")


# ------------------------------------------------------------------------------------------------------------------ chart 4
def chart4(D, row, outdir, n_draw=20000):
    L, Lo = row["lat"], row["lon"]; g = D.g
    m = np.abs(g["lat"] - L) <= 1.0; idx = np.where(m)[0]; w = g["w_D0"][idx]
    E_sorted = np.sort(g["E_j"][idx]); ww = w[np.argsort(g["E_j"][idx])]; cw = np.cumsum(ww) / ww.sum()
    Eq99 = float(E_sorted[min(np.searchsorted(cw, 0.99), len(cw) - 1)]); Eq50 = float(E_sorted[min(np.searchsorted(cw, 0.5), len(cw) - 1)])
    rng = np.random.default_rng(20261023); pick = rng.choice(idx, size=n_draw, p=w / w.sum(), replace=True)
    tau = np.nan_to_num(g["tau90_s"][pick], nan=3.3)
    base, ti = D.M.level_base(g["lat"][pick], g["E_j"][pick], tau)
    RXS = ["H01W", "H08S", "3315", "3376", "3274", "3275"]
    etas = COUPLINGS + [(f"{row['eta_needed']:.2g} (needed for this row at the 99th-percentile energy)", row["eta_needed"])]
    cols = ["#c6dbef", "#9ecae1", "#4292c6", "#2171b5", "#08306b", "#e31a1c"]   # light -> dark with coupling; row value red
    fig, ax = plt.subplots(figsize=(7.4, 4.6)); wb = 0.12; res = {}
    members = {mm["rx"] for mm in row["members"]}
    for i, rx in enumerate(RXS):
        nz = D.noise[rx]; assert abs(nz["median"] - D.M.bmed[rx]) < 0.01, "noise median differs from the level chain"
        ax.fill_between([i - 0.45, i + 0.45], nz["q10"], nz["q90"], color="#fee391", lw=0, zorder=0)
        ax.plot([i - 0.45, i + 0.45], [nz["median"]] * 2, color="#cc4c02", lw=1.2, zorder=1)
        ax.plot([i - 0.45, i + 0.45], [nz["q99"]] * 2, color="#cc4c02", lw=0.7, ls=":", zorder=1)
        b = base[rx]; fin = np.isfinite(b); res[rx] = dict(blocked_share=round(float(1 - fin.mean()), 4), noise=nz, noise_set=D.noise_label[rx], levels={})
        if fin.mean() < 0.5:
            ax.text(i, nz["median"] + 3, "no sound path\nin the model", ha="center", fontsize=TICK); continue
        for j, ((lab, eta), cc) in enumerate(zip(etas, cols)):
            lv = b[fin] + D.M.bmed[rx] + 10 * np.log10(eta); q = np.quantile(lv, [0.05, 0.5, 0.95])
            x = i + (j - 2.5) * wb
            ax.bar(x, q[2] - q[0], bottom=q[0], width=wb * 0.9, color=cc, edgecolor="k" if j in (2, 5) else "none", lw=1.1 if j == 2 else 0.6, zorder=2)
            ax.plot([x - wb * 0.45, x + wb * 0.45], [q[1]] * 2, color="w" if j in (3, 4) else "k", lw=1.0, zorder=3)
            res[rx]["levels"][lab.split(" ")[0]] = dict(q05=round(q[0], 1), q50=round(q[1], 1), q95=round(q[2], 1),
                                                          share_above_noise_median=round(float((lv > nz["median"]).mean()), 3))
    ax.set_xticks(range(len(RXS)))
    ax.set_xticklabels([RX_NAME[r].replace(" H0", "\nH0").replace(" 33", "\n33").replace(" 32", "\n32") + ("\n(detected here)" if r in members else "") for r in RXS], fontsize=TICK)
    ax.set_ylabel("received level, dB re 1 uPa^2\n(5-40 Hz, mean over the signal duration)")
    ax.margins(y=0.05)
    ax.set_title(row_title(row) + f"\nPredicted loudness at each hydrophone for an impact at {abs(L):.2f} S {Lo:.2f} E, against background noise", loc="left", fontsize=BASE)
    h = [Patch(color=c) for c in cols] + [Line2D([0], [0], color="#cc4c02", lw=1.2), Patch(color="#fee391"), Line2D([0], [0], color="#cc4c02", lw=0.7, ls=":")]
    lab = ["share of impact energy that becomes sound " + etas[0][0]] + [e[0] for e in etas[1:]] + ["noise median", "noise 10-90 %", "noise 99 %"]
    h[5] = Patch(facecolor=cols[5], edgecolor="k"); h[2] = Patch(facecolor=cols[2], edgecolor="k", lw=1.1)
    ax.legend(h, lab, ncol=2, loc="upper left", bbox_to_anchor=(0, -0.2), fontsize=TICK)
    plain = ("Each bar shows how loud an impact at this place would be at each hydrophone, for one value of the share of impact energy that becomes "
             "sound. The bar runs from the 5 % to the 95 % value over the possible impacts; the line in the bar is the middle value. Yellow is the "
             "normal background noise. The red bar uses the share that this row needs. A bar above the yellow does not mean that a detector finds the signal.")
    tech = (f"Impacts: run J geometry sample (in.geometry_sample), D0 weights, within +/-1 deg latitude of {abs(L):.2f} S ({len(idx):,} rows), {n_draw:,} "
            f"weighted draws (seed 20261023); E median {Eq50/1e9:.2f} GJ, q99 {Eq99/1e9:.2f} GJ (table {row['E_q99']/1e9:.2f} GJ). Level = module block 11 "
            f"chain (Machinery, RAM-grid IMOS TL, TL grid offset 0, source depth 10 m (D25), one-pole f^-2 source spectrum with tau90, energy flux / T_eff; "
            f"H01W/H08S include the 4.8 dB triad gain). Noise = injection_run_j bg_level_stats + abs_offset (1 s level; 3376/3274 own 14 days, 3315/3275 "
            f"own 8 Mar outside the window, H01W/H08S IMOS 3376 noise shaped to Blackman medians = stand-in, D06); the module summary gives q10/q90/q99, "
            f"not q05/q95. H08S level ignores the airgun survey; Kadri's 5 Hz high-pass + 2-40 Hz band-pass is not applied. Coupling 2.26e-3 is the "
            f"F-35A value under the module definition (Metz 2023, pending ruling); it is one point in the prior range. Needed coupling "
            f"{row['eta_needed']:.3g} = {row['x_metz']:.3g} x 2.26e-3; P(coupling >= needed) under log-uniform [1e-6, 1] = {row['p_prior']:.2f} (table). "
            f"Detection power not shown (model-template P_D is optimistic by about 4-10 dB, D05). PREDICTIVE, NOT CALIBRATED; C1, C2.")
    footnote(fig, plain, tech, y=-0.12, width=165)
    fig.subplots_adjust(left=0.11, right=0.99, top=0.86, bottom=0.2)
    fn = Path(outdir) / "chart4.png"; fig.savefig(fn, bbox_inches="tight"); plt.close(fig)
    labels_txt = " ".join(lab)
    return str(fn), dict(n_rows_within_1deg=int(len(idx)), E_q50_GJ=round(Eq50 / 1e9, 3), E_q99_GJ=round(Eq99 / 1e9, 3), E_q99_table_GJ=round(row["E_q99"] / 1e9, 3),
                         E_q99_rel_diff=round(Eq99 / row["E_q99"] - 1, 4), couplings=[e[1] for e in etas], old_2p1e4_absent=("2.1e-4" not in labels_txt + tech),
                         receivers=res)


# ------------------------------------------------------------------------------------------------------------------ main
def contact_sheet(table_dir, ids, out_png, title):
    import matplotlib.image as mpimg
    n = len(ids); fig, axs = plt.subplots(n, 4, figsize=(12, 2.9 * n))
    axs = np.atleast_2d(axs)
    for i, rid in enumerate(ids):
        for j in range(4):
            ax = axs[i, j]; ax.axis("off"); p = Path(table_dir) / rid / f"chart{j + 1}.png"
            if p.exists(): ax.imshow(mpimg.imread(p))
            if j == 0: ax.set_title(rid, loc="left", fontsize=9)
    fig.suptitle(title, x=0.01, y=0.999, ha="left", fontsize=11); fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(out_png, dpi=110); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--table1", required=True); ap.add_argument("--table2", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=10); ap.add_argument("--all", action="store_true"); ap.add_argument("--only", default=""); ap.add_argument("--extra", default="")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True); t_start = time.time()
    t1 = pd.read_csv(a.table1); t2 = pd.read_csv(a.table2, dtype={"rx": str})
    D = Data(); CB = check_b(D)
    rows = rows_from_tables(t1, t2, None if a.all else a.top)
    if a.extra:
        have = {r["id"] for r in rows}; ex = [x for x in a.extra.split(",") if x and x not in have]
        allr = rows_from_tables(t1, t2, None); rows += [r for r in allr if r["id"] in ex]
        missing = set(ex) - {r["id"] for r in rows}
        if missing: raise SystemExit(f"--extra ids not in the tables: {sorted(missing)}")
    if a.only: rows = [r for r in rows if r["id"] in a.only.split(",")]
    checks = dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), table1=a.table1, table2=a.table2, check_b=CB, rows={}, failed=[])
    for r in rows:
        d = out / r["table"] / r["id"]; d.mkdir(parents=True, exist_ok=True); ck = dict(lat=r["lat"], lon=r["lon"], implied_impact=r["t0_txt"], members=r["members"])
        for k, fnc in [("chart1", lambda: chart1(D, r, d)), ("chart2", lambda: chart2(D, r, d, CB)), ("chart3", lambda: chart3(D, r, d)), ("chart4", lambda: chart4(D, r, d))]:
            try:
                fn, c = fnc(); ck[k] = dict(file=fn, **c)
            except Exception as e:
                ck[k] = dict(error=repr(e)); checks["failed"].append(f"{r['id']} {k}: {e!r}")
        c1 = ck.get("chart1", {})
        if c1.get("members_with_data", 0) and c1.get("members_visible", 0) < c1.get("members_with_data", 0):
            ck["note_chart1"] = "at least one member detection is not visible at this scale (see panels)"
        c4 = ck.get("chart4", {})
        if c4 and "E_q99_rel_diff" in c4 and abs(c4["E_q99_rel_diff"]) > 0.05: checks["failed"].append(f"{r['id']} chart4: E_q99 differs from table by {c4['E_q99_rel_diff']:+.1%}")
        checks["rows"][r["id"]] = ck; print(r["id"], f"{time.time() - t_start:.0f}s", flush=True)
    checks["inputs"] = INPUTS; checks["wall_s"] = round(time.time() - t_start, 1)
    json.dump(checks, open(out / "CHECKS.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    for tb in ("table1", "table2"):
        ids = [r["id"] for r in rows if r["table"] == tb]
        if ids: contact_sheet(out / tb, ids, out / f"contact-sheet-{tb}.png", f"{'Table 1 multi-site' if tb == 'table1' else 'Table 2 single-site'}: charts 1-4 per row")
    print(json.dumps(dict(failed=checks["failed"], wall_s=checks["wall_s"])))


if __name__ == "__main__":
    main()
