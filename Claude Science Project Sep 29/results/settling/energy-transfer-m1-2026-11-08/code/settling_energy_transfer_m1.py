"""Ocean settling: mechanical energy-transfer duration at water entry, impact_tau_method = 1.

Owner: ocean settling (Pete's ruling of 8 Nov 2026; work order
threads/work-orders/settling-energy-transfer-duration-2026-11-08.md). Method authority: the end-of-flight
note results/eof-impact-tau-method-oct11.md (11 Oct 2026), ported without change of formula. The settling
method note in results/settling/energy-transfer-m1-2026-11-08/ supersedes it as the owner's note.

Inputs per row (contact state x_Impact only; the family label is never read by the physics):
  v     = sqrt(2 KE / m)                       contact speed, ground-relative (wind included, current not subtracted)
  theta = |flight_path_angle_deg_descent_positive|
  m     = mass_kg
Declared random parameters, one draw per row:
  a_bar ~ U[0.75 g, 3.0 g]       mean longitudinal deceleration of a shallow (ditching-like) entry
  L_eff ~ U[0.5, 1.0] x 63.7 m   effective crush length of a steep entry (777-200ER overall length 63.7 m)
Shallow, theta <= 10 deg: T = v / a_bar, F(t) = 1 - (1 - t/T)^2,
  t05 = (1 - sqrt 0.95) T = 0.0253 T, t95 = (1 - sqrt 0.05) T = 0.776 T, tau90 = 0.751 v / a_bar, P = m a_bar v.
Steep, theta >= 30 deg: linear transfer over L_eff / v,
  t05 = 0.05 L_eff / v, t95 = 0.95 L_eff / v, tau90 = 0.9 L_eff / v, P = KE v / L_eff.
Blend, 10 < theta < 30 deg: w = (theta - 10) / 20; X = exp((1 - w) ln X_shallow + w ln X_steep) for t05, t95 and P.
  The note also states the log-linear blend for tau90 itself. In the band that differs from t95 - t05.
  energy_transfer_tau90_s is t95 - t05 (contract definition of 8 Oct; same as the Run C / Run J sidecars);
  the literal log-blend of tau90 is emitted as energy_transfer_tau90_logblend_s. Outside the band they are equal.
Band-edge sensitivity: same draws, band 5-45 deg (columns with suffix _band5_45).
Other columns: impact_energy_transferred_j = KE (declared upper bound); energy_transfer_n_pulses = 1 (declared
  single-pulse model; float so that NaN can mark a row not computed); kinetic_energy_at_contact_j = KE (a copy,
  never an alias of energy transferred); impact_tau_method = 1; bank_assigned = 1 where family_code in (2, 3)
  and bank_deg == 0.0 (placeholder bank; any attitude-dependent method must treat these rows as not assessed).
NaN means not computed (non-finite or non-positive v or m, or non-finite theta). It is never filled.

Reproducible draws: counter-based hash, independent of chunking and of any later reordering.
  x_k = SALT + route_code * 2^56 + seed * 2^40 + row_index * 4 + k   (uint64, wrapping; k = 0 a_bar, k = 1 L_eff)
  h   = splitmix64(x_k);  u = ((h >> 11) + 0.5) * 2^-53  in (0, 1)
  route_code 1 = Davey model + fuel ('df'), 2 = waypoints ('wp'); row_index = 0-based row in the hand-off file.
"""
import numpy as np

G0 = 9.80665
L777_M = 63.7
A_BAR_G = (0.75, 3.0)
L_EFF_FRAC = (0.5, 1.0)
BAND_DEG = (10.0, 30.0)
BAND_SENS_DEG = (5.0, 45.0)
C05_SH = 1.0 - np.sqrt(0.95)   # 0.02532
C95_SH = 1.0 - np.sqrt(0.05)   # 0.77639
SALT = 0x5E771E0000000001
ROUTE_CODE = {"df": 1, "wp": 2}
METHOD_ID = 1


def splitmix64(x):
    x = np.asarray(x, dtype=np.uint64)
    with np.errstate(over="ignore"):
        z = x + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return z


def uniforms(route_code, seed, row_index, k):
    """u in (0, 1) per row, from (route_code, seed, row_index, stream k)."""
    seed = np.asarray(seed).astype(np.uint64)
    row = np.asarray(row_index).astype(np.uint64)
    with np.errstate(over="ignore"):
        x = (np.uint64(SALT) + np.uint64(route_code) * np.uint64(1 << 56) + seed * np.uint64(1 << 40)
             + row * np.uint64(4) + np.uint64(k))
    h = splitmix64(x)
    return ((h >> np.uint64(11)).astype(np.float64) + 0.5) * (2.0 ** -53)


def draw_parameters(route_code, seed, row_index):
    ua = uniforms(route_code, seed, row_index, 0)
    ul = uniforms(route_code, seed, row_index, 1)
    a_bar = (A_BAR_G[0] + (A_BAR_G[1] - A_BAR_G[0]) * ua) * G0
    l_eff = (L_EFF_FRAC[0] + (L_EFF_FRAC[1] - L_EFF_FRAC[0]) * ul) * L777_M
    return a_bar, l_eff


def regimes(v, m, a_bar, l_eff):
    """Pure-regime quantities (t05, t95, tau90, peak rate) for shallow and for steep entry."""
    with np.errstate(divide="ignore", invalid="ignore"):
        T = v / a_bar
        ke = 0.5 * m * v ** 2
        sh = {"t05": C05_SH * T, "t95": C95_SH * T, "tau90": (C95_SH - C05_SH) * T, "peak": m * a_bar * v}
        tl = l_eff / v
        st = {"t05": 0.05 * tl, "t95": 0.95 * tl, "tau90": 0.90 * tl, "peak": ke / tl}
    return sh, st


def w_steep(theta_deg, band=BAND_DEG):
    lo, hi = band
    return np.clip((np.asarray(theta_deg, dtype=np.float64) - lo) / (hi - lo), 0.0, 1.0)


def logblend(x_sh, x_st, w):
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.exp((1.0 - w) * np.log(x_sh) + w * np.log(x_st))
    return np.where(w <= 0.0, x_sh, np.where(w >= 1.0, x_st, out))   # exact pure-regime values outside the band


def method1(v, theta_deg, m, a_bar, l_eff, band=BAND_DEG):
    v = np.asarray(v, dtype=np.float64); m = np.asarray(m, dtype=np.float64)
    theta = np.abs(np.asarray(theta_deg, dtype=np.float64))
    sh, st = regimes(v, m, a_bar, l_eff)
    w = w_steep(theta, band)
    t05 = logblend(sh["t05"], st["t05"], w)
    t95 = logblend(sh["t95"], st["t95"], w)
    peak = logblend(sh["peak"], st["peak"], w)
    tau_lb = logblend(sh["tau90"], st["tau90"], w)
    ok = np.isfinite(v) & (v > 0) & np.isfinite(m) & (m > 0) & np.isfinite(theta)
    nan = np.nan
    return {"t05": np.where(ok, t05, nan), "t95": np.where(ok, t95, nan), "tau90": np.where(ok, t95 - t05, nan),
            "tau90_logblend": np.where(ok, tau_lb, nan), "peak": np.where(ok, peak, nan),
            "w": np.where(np.isfinite(theta), w, nan), "ok": ok}


SIDECAR_COLUMNS = [
    "row_index", "seed", "impact_energy_transferred_j", "energy_transfer_t05_s", "energy_transfer_t95_s",
    "energy_transfer_tau90_s", "energy_transfer_peak_rate_w", "energy_transfer_n_pulses",
    "kinetic_energy_at_contact_j", "impact_tau_method", "w_steep", "a_bar_mps2", "l_eff_m", "bank_assigned",
    "contact_speed_mps", "energy_transfer_tau90_logblend_s", "w_steep_band5_45", "energy_transfer_t05_s_band5_45",
    "energy_transfer_t95_s_band5_45", "energy_transfer_tau90_s_band5_45", "energy_transfer_peak_rate_w_band5_45"]


def build_sidecar(h, route):
    """h: dict of hand-off arrays (one route model). Returns the row-aligned sidecar columns (hand-off order)."""
    n = len(h["mass_kg"])
    row = np.arange(n, dtype=np.int64)
    ke = h["kinetic_energy_j"].astype(np.float64)
    m = h["mass_kg"].astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        v = np.sqrt(2.0 * ke / m)
    theta = np.abs(h["flight_path_angle_deg_descent_positive"].astype(np.float64))
    a_bar, l_eff = draw_parameters(ROUTE_CODE[route], h["seed"].astype(np.int64), row)
    r = method1(v, theta, m, a_bar, l_eff, BAND_DEG)
    s = method1(v, theta, m, a_bar, l_eff, BAND_SENS_DEG)
    ok = r["ok"]
    fam = h["family_code"].astype(np.int64)
    bank_assigned = ((fam == 2) | (fam == 3)) & (h["bank_deg"] == 0.0)
    f4 = np.float32
    out = {
        "row_index": row.astype(np.int32),
        "seed": h["seed"].astype(np.int16),
        "impact_energy_transferred_j": np.where(ok, ke, np.nan),
        "energy_transfer_t05_s": r["t05"].astype(f4),
        "energy_transfer_t95_s": r["t95"].astype(f4),
        "energy_transfer_tau90_s": r["tau90"].astype(f4),
        "energy_transfer_peak_rate_w": r["peak"].astype(f4),
        "energy_transfer_n_pulses": np.where(ok, 1.0, np.nan).astype(f4),
        "kinetic_energy_at_contact_j": ke.copy(),
        "impact_tau_method": np.full(n, METHOD_ID, dtype=np.int8),
        "w_steep": r["w"].astype(f4),
        "a_bar_mps2": a_bar,
        "l_eff_m": l_eff,
        "bank_assigned": bank_assigned.astype(np.int8),
        "contact_speed_mps": v.astype(f4),
        "energy_transfer_tau90_logblend_s": r["tau90_logblend"].astype(f4),
        "w_steep_band5_45": s["w"].astype(f4),
        "energy_transfer_t05_s_band5_45": s["t05"].astype(f4),
        "energy_transfer_t95_s_band5_45": s["t95"].astype(f4),
        "energy_transfer_tau90_s_band5_45": s["tau90"].astype(f4),
        "energy_transfer_peak_rate_w_band5_45": s["peak"].astype(f4),
    }
    assert list(out) == SIDECAR_COLUMNS
    return out


def weighted_quantiles(x, w, q):
    """Weighted quantiles by midpoint interpolation of the weighted empirical CDF; non-finite x excluded."""
    x = np.asarray(x, dtype=np.float64); w = np.asarray(w, dtype=np.float64)
    k = np.isfinite(x) & (w > 0)
    x, w = x[k], w[k]
    o = np.argsort(x, kind="stable"); x, w = x[o], w[o]
    c = (np.cumsum(w) - 0.5 * w) / w.sum()
    return np.interp(q, c, x)


def ess(w):
    w = np.asarray(w, dtype=np.float64)
    return float(w.sum() ** 2 / (w ** 2).sum()) if w.sum() > 0 else 0.0
