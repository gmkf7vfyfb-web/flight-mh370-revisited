"""Per-impact hydroacoustic likelihood L_hyd for the hydroacoustic test of the Pleiades hypothesis.

STAND-IN WRAPPER (architecture stand-in for hydroacoustics, 10 Oct 2026). NOT module code. Pre-registered in
results/hydroacoustics-pleiades-test-preregistration.md; its sha256 is recorded there. Changes after the first R_hyd
are amendments and are disclosed.

It imports the hydroacoustics module's prepare/ scripts READ-ONLY (f35a_eta_calibration, imos_stageB_map,
imos_preregistration, kadri_table1_test) and repeats the per-sample arithmetic of
prepare/exploratory/near_limits_eof289.py (sha256 da86a5e4...) for received SNR at the IMOS loggers and at H01W/H08S.
Two numerical changes, declared: (1) band_fraction(fc, 1/tau) is tabulated on 600 log-spaced tau values and
interpolated (it is a function of tau only; the direct form needs n x 4000 memory); (2) arrival time uses the mean
group speed with its spread carried as a timing sd, as kadri_table1_test.py does, instead of one c draw per row.

LIKELIHOOD (near-limit protocol, results/hydroacoustics-near-limits-planning.md; Pete ~20:30 UTC 10 Oct):
  For station s with observed event list {(t_k, b_k)} over its scored coverage, background events a Poisson process
  of density lambda_s, and the impact producing at most one event with probability q_s,i = cov_s,i x P_D,s,i:
      L_s,i = (1 - q_s,i) + q_s,i x sum_k f_s,i(t_k, b_k) / lambda_s(t_k, b_k)
  (the factor exp(-Lambda_s) common to every impact is dropped). L_hyd,i = prod_s L_s,i, with ONE nuisance draw per
  row shared by every station (C_site, tau, z_s), so detections are correlated through the source as in the module.
  False alarms and chance coincidence are inside L through lambda_s; no hard detect/no-detect cut is made.
  f_s,i(t, b) = N(t; t_arr,i, sd_t,i) [x t3(b - baz_i; sd 3.3 deg) where bearings exist].
"""
import json, pathlib, sys
import numpy as np, pandas as pd

DAY0_UNIX = 1394236800.0          # 2014-03-08 00:00:00 UTC
C_MEAN, C_SD, PICK_S = 1.482, 0.006, 10.0
ALPHA = 0.05                       # loose per-50 s false-alarm rate (near-limit protocol)
WIN_S = 50.0
TRIAD_GAIN_DB = 4.8
NU_T, SD_BEAR = 3.0, 3.3
KADRI_SPAN = (27 * 60.0, 57 * 60.0)                         # Fig. 9 panels a-c, H01W, s after 00:00 UTC
KADRI_LAMBDA = 18.0 / (998.0 * (343.16 - 234.67))          # module's leave-one-out background density (per s.deg)
RAW_REQ = {"H01W": (25 * 60.0, 2 * 3600 + 20 * 60.0), "H08S": (45 * 60.0, 2 * 3600 + 50 * 60.0)}  # outstanding raw request
TAU_GRID = np.logspace(np.log10(0.05), np.log10(10.0), 600)


class Model:
    raw_events = {}      # scenario C only: synthetic raw-triad events {"H01W": (k,2) [t_s, bearing], "H08S": ...}

    def __init__(self, module_dir, imos_events_json, kadri_csv):
        self.P = pathlib.Path(module_dir)
        sys.path.insert(0, str(self.P / "prepare"))
        import f35a_eta_calibration as F, imos_stageB_map as B, imos_preregistration as PR, kadri_table1_test as K
        from pyproj import Geod
        self.F, self.B, self.PR, self.K = F, B, PR, K
        self.geod = Geod(ellps="WGS84")
        H = self.P
        self.fits = json.loads((H / "results-data/stageA/summary_union.json").read_text())["fits"]
        self.bmed = json.loads((H / "results-data/imos2b/summary.json").read_text())["background_spl_median"]
        meta = PR.parse_meta(); recs = pd.read_csv(H / "data/imos/recordings.csv", parse_dates=["start_logger"])
        self.meta = meta
        self.teff = B.t_eff(meta, recs, None)["T_C2"]
        req = json.loads((H / "data/ocean_paths/request.json").read_text())
        qlat = {p["name"][3:6]: p["a"][1] for p in req["paths"] if p["name"].startswith("imp")}
        self.qs = sorted(qlat, key=lambda k: qlat[k]); self.xs = np.array([qlat[k] for k in self.qs])
        cal = pd.read_csv(H / "results-data/ram_check/eta_cal_ramcorr.csv"); self.etab = F.eta_cal_lookup(cal, 2)
        self.Sb = {fc: B.band_fraction(fc, 1 / TAU_GRID, 2) for fc in F.BANDS}
        tl = pd.read_csv(H / "results-data/ram_check/imos_tl_ramcorr.csv", dtype={"quantile": str, "logger": str})
        self.tl_imos = {}
        for lg in B.LOGGERS:
            g = tl[tl.logger == lg]
            self.tl_imos[lg] = {(fc, z): g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("quantile").tl_db[self.qs].values
                                for fc in F.BANDS for z in F.SRC}
        kt = pd.read_csv(H / "results-data/near_limits/ims_tl_kraken.csv", dtype={"quantile": str})
        rd = pd.read_csv(H / "results-data/near_limits/ims_ram_delta.csv")
        self.tl_ims = {}
        for stn in ("H01W", "H08S"):
            g = kt[kt.station == stn]; dd = rd[rd.path == f"imp500_{stn}"]; tab = {}
            for fc in F.BANDS:
                for z in F.SRC:
                    zz = 30.0 if z >= 30 else 10.0; h = dd[np.isclose(dd.src_depth_m, zz)].set_index("fc_hz").delta_db
                    delta = float(np.interp(np.log10(fc), np.log10(h.index.values), h.values))
                    tab[(fc, z)] = g[(g.fc_hz == fc) & np.isclose(g.src_depth_m, z)].set_index("quantile").tl_db[self.qs].values - delta
            self.tl_ims[stn] = tab
        st = pd.read_csv(H / "data/stations.csv", comment="#")
        self.rx = {t: (float(g.latitude_deg.mean()), float(g.longitude_deg.mean())) for t, g in st.groupby("triad")}
        for lg in B.LOGGERS:
            self.rx[lg] = (meta[lg]["lat"], meta[lg]["lon"])
        ev = json.loads(pathlib.Path(imos_events_json).read_text())
        self.imos_scored = {lg: np.array(ev[lg]["scored_segments"]) for lg in B.LOGGERS}
        self.imos_recorded = {lg: np.array(ev[lg]["recorded_segments"]) for lg in B.LOGGERS}
        self.imos_events = {lg: np.array([t for t, _ in ev[lg]["events"]["loose"]]) for lg in B.LOGGERS}
        kd = pd.read_csv(kadri_csv); kd["t_s"] = kd.time_utc.map(K.secs)
        self.kadri = kd[["t_s", "bearing_deg"]].to_numpy(float)

    # ---------------- per-row source and SNR (near_limits_eof289.py arithmetic) ----------------
    @staticmethod
    def nuisance(rng, n):
        tau = 10 ** rng.uniform(np.log10(0.05), np.log10(10), n)
        zs = rng.choice([2.0, 10.0, 30.0], n)
        c_site, c_rcv = rng.normal(0, 10, n), rng.normal(0, 10, n)
        c_ims = rng.normal(0, 3, n)
        return dict(tau=tau, zs=zs, c_site=c_site, c_rcv=c_rcv, c_ims=c_ims)

    def _se(self, lat, E, nu, tab):
        F, B = self.F, self.B
        n = len(lat); eta = np.zeros(n)
        for z, (lx, ly) in self.etab.items():
            m = nu["zs"] == z; eta[m] = 10 ** np.interp(np.log10(nu["tau"][m]), lx, ly)
        SE1 = eta * E * B.RHO_C / (2 * np.pi)
        ltau = np.log10(nu["tau"]); SE = np.zeros(n); la = np.clip(lat, self.xs.min(), self.xs.max())
        for fc in F.BANDS:
            sb = np.interp(ltau, np.log10(TAU_GRID), self.Sb[fc]); tlb = np.zeros(n)
            for z in F.SRC:
                mz = nu["zs"] == z; tlb[mz] = np.interp(la[mz], self.xs, tab[(fc, z)])
            SE += SE1 * sb * np.nan_to_num(10 ** (-tlb / 10), nan=0.0)
        return SE

    def _snr0(self, lat, E, nu, tab, noise_key):
        bm = self.bmed[noise_key] if noise_key in self.bmed else self.bmed[str(int(noise_key))]
        return 10 * np.log10(np.maximum(self._se(lat, E, nu, tab), 1e-300) / self.teff / 1e-12) - bm

    def _pd(self, snr, lg):
        f = self.fits[f"{lg}|T_C2|or|{ALPHA}"]; s = max((f["snr90"] - f["snr50"]) / np.log(9), 0.05)
        return 1 / (1 + np.exp(-(snr - f["snr50"]) / s))

    def geometry(self, lat, lon, name):
        rl, ro = self.rx[name]; n = len(lat)
        az, _, d = self.geod.inv(np.full(n, ro), np.full(n, rl), lon, lat)
        return np.mod(az, 360.0), d / 1000.0

    # ---------------- per-row station terms ----------------
    @staticmethod
    def _cov(t, segs):
        c = np.zeros(len(t), bool)
        for a, b in segs:
            c |= (t >= a) & (t <= b)
        return c

    def _mix(self, q, t_arr, sd_t, ev_t, lam, baz=None, ev_b=None):
        s = np.zeros(len(q))
        for k in range(len(ev_t)):
            lf = -0.5 * np.log(2 * np.pi * sd_t ** 2) - 0.5 * ((ev_t[k] - t_arr) / sd_t) ** 2
            if baz is not None:
                db = (ev_b[k] - baz + 180.0) % 360.0 - 180.0
                lf = lf + self.K.log_t(db, SD_BEAR, NU_T)
            s += np.exp(lf) / lam
        return (1 - q) + q * s

    def station_terms(self, t_imp_unix, lat, lon, E, rng, scenario="A"):
        """ln L per station and in total, per row.
        A = data held and scored (PRIMARY). B = A with every RECORDED IMOS segment scored and assumed event-free
        except the events already found (data held, not yet scored; planning only). C = A plus raw H01W and H08S
        triads over the outstanding request windows, with bearings, in place of Kadri's H01W table (data NOT held;
        planning only; events from Model.raw_events)."""
        n = len(lat); nu = self.nuisance(rng, n); out = {}
        t0 = t_imp_unix - DAY0_UNIX
        C = nu["c_site"] + nu["c_rcv"]
        for lg in self.B.LOGGERS:
            _, d = self.geometry(lat, lon, lg); t_arr = t0 + d / C_MEAN
            sd_t = np.sqrt(PICK_S ** 2 + (d * C_SD / C_MEAN ** 2) ** 2)
            segs = self.imos_recorded[lg] if scenario == "B" else self.imos_scored[lg]
            snr = self._snr0(lat, E, nu, self.tl_imos[lg], lg) + C
            q = self._cov(t_arr, segs) * self._pd(snr, self.B.TARGET[lg])
            out[lg] = np.log(self._mix(q, t_arr, sd_t, self.imos_events[lg], ALPHA / WIN_S))
        Cs = nu["c_site"] + nu["c_ims"]
        snr_ims = {stn: self._snr0(lat, E, nu, self.tl_ims[stn], "3376") + Cs + TRIAD_GAIN_DB for stn in ("H01W", "H08S")}
        for stn in ("H01W", "H08S"):
            if stn == "H08S" and scenario != "C":
                continue                                   # Kadri's H08S trace: excluded (shot train, P_D unknown)
            baz, d = self.geometry(lat, lon, stn); t_arr = t0 + d / C_MEAN
            sd_t = np.sqrt(PICK_S ** 2 + (d * C_SD / C_MEAN ** 2) ** 2)
            pdv = self._pd(snr_ims[stn], "3274")
            if scenario == "C":
                lo, hi = RAW_REQ[stn]; ev = self.raw_events.get(stn, np.zeros((0, 2)))
                lam = ALPHA / WIN_S / 360.0
            else:
                lo, hi = KADRI_SPAN; ev = self.kadri; lam = KADRI_LAMBDA
            q = ((t_arr >= lo) & (t_arr <= hi)) * pdv
            out[stn] = np.log(self._mix(q, t_arr, sd_t, ev[:, 0], lam, baz, ev[:, 1]))
        out["total"] = sum(v for v in out.values())
        return out

    # ---------------- predictive quantities (power check) ----------------
    def predict(self, t_imp_unix, lat, lon, E, rng):
        """Per row: arrival time (s after 00:00 UTC), timing sd, bearing, and P_D (coverage excluded) per station."""
        n = len(lat); nu = self.nuisance(rng, n); t0 = t_imp_unix - DAY0_UNIX; res = {}
        C = nu["c_site"] + nu["c_rcv"]; Cs = nu["c_site"] + nu["c_ims"]
        for name in list(self.B.LOGGERS) + ["H01W", "H08S", "H08N"]:
            baz, d = self.geometry(lat, lon, name)
            r = dict(t=t0 + d / C_MEAN, sd=np.sqrt(PICK_S ** 2 + (d * C_SD / C_MEAN ** 2) ** 2), baz=baz)
            if name in self.B.LOGGERS:
                r["pd"] = self._pd(self._snr0(lat, E, nu, self.tl_imos[name], name) + C, self.B.TARGET[name])
            elif name in ("H01W", "H08S"):
                r["pd"] = self._pd(self._snr0(lat, E, nu, self.tl_ims[name], "3376") + Cs + TRIAD_GAIN_DB, "3274")
            res[name] = r
        return res
