"""Unit tests on synthetic data for reverse_detectors (run: pytest -q)."""
import os
import sys

import numpy as np
import pytest
from scipy import signal as sps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import reverse_detectors as rd  # noqa: E402

FS = 10.0


def noise_env(n, rng, corr_s=0.5):
    """Rayleigh-like envelope with a short correlation time (smoothed complex
    Gaussian), similar in form to a band envelope at 10 samples/s."""
    z = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    k = max(1, int(corr_s * FS))
    z = np.convolve(z, np.ones(k) / k, mode="same")
    return np.abs(z)


# --- helpers -----------------------------------------------------------------

def test_empirical_p_never_zero():
    null = np.arange(100.0)
    assert rd.empirical_p(1e9, null) == pytest.approx(1 / 101)
    assert rd.empirical_p(-1e9, null) == pytest.approx(1.0)


def test_gpd_tail_extrapolates_beyond_range():
    rng = np.random.default_rng(0)
    null = rng.exponential(1.0, 20000)
    p, flag = rd.gpd_tail_p(15.0, null)
    assert flag == "extrapolated"
    assert 1e-8 < p < 1e-5  # exact exp tail = 3.1e-7


def test_bh_fdr():
    disc, q = rd.bh_fdr([0.001, 0.01, 0.04, 0.5], q=0.1)
    assert disc.tolist() == [True, True, True, False]


def test_vertices_to_envelope_removes_sign_alternation():
    rng = np.random.default_rng(1)
    t = np.sort(rng.uniform(0, 60, 900))
    x = np.where(np.arange(t.size) % 2 == 0, 1, -1) * (1 + 0.1 * rng.standard_normal(t.size))
    r1_signed = np.corrcoef(x[1:], x[:-1])[0, 1]
    tg, env, filled = rd.vertices_to_envelope(t, x, fs_out=10, t0=0.0, t1=60.0)
    assert r1_signed < -0.8
    assert np.all(env > 0) and env.size == 601


def test_decorrelation_lag_tracks_smoothing():
    rng = np.random.default_rng(2)
    a = rd.decorrelation_lag(noise_env(20000, rng, 0.1))
    b = rd.decorrelation_lag(noise_env(20000, rng, 1.0))
    assert a <= 2 and 4 <= b <= 12


# --- S1, S2, S3 ----------------------------------------------------------------

def test_energy_excess_detects_and_is_calibrated():
    rng = np.random.default_rng(3)
    env = noise_env(int(1800 * FS), rng)
    out0 = rd.energy_excess(env, FS, win_s=10)
    frac = np.nanmean(out0["z"] >= 2)
    assert 0.005 < frac < 0.08  # near-Gaussian tail of window levels
    sh = rd.impulsive_shape(FS, 1.0, 5.0)
    env1 = rd.inject_envelope(env, FS, 900.0, sh, snr_db=3.0)
    out1 = rd.energy_excess(env1, FS, win_s=10)
    k = np.nanargmax(out1["z"])
    assert abs(out1["t"][k] - 900) <= 10 and out1["z"][k] > 4


def test_persistence_binomial_valid_after_thinning():
    rng = np.random.default_rng(4)
    env = noise_env(int(3600 * FS), rng, corr_s=1.0)
    lag = rd.decorrelation_lag(20 * np.log10(env))
    thin = rd.persistence(env, FS, win_s=20, lag=lag)
    raw = rd.persistence(env, FS, win_s=20, lag=1)
    fa_thin = np.nanmean(thin["p_bin"] <= 0.05)
    fa_raw = np.nanmean(raw["p_bin"] <= 0.05)
    assert fa_thin < 0.07          # close to nominal 0.05
    assert fa_raw > fa_thin        # unthinned iid assumption is anti-conservative


def test_persistence_detects_weak_long_signal():
    rng = np.random.default_rng(5)
    env = noise_env(int(1800 * FS), rng)
    sh = np.ones(int(20 * FS))
    env1 = rd.inject_envelope(env, FS, 900.0, sh, snr_db=-3.0, win_s=20)
    out = rd.persistence(env1, FS, win_s=20)
    k = np.nanargmax(out["T2"])
    assert abs(out["t"][k] - 900) <= 10 and out["p_bin"][k] < 1e-3
    assert out["z_run"][k] < 0


def test_fisher_combination_monotone():
    assert rd.fisher_combine(0.01, 0.01) > rd.fisher_combine(0.1, 0.01)


# --- S4 ----------------------------------------------------------------------

def test_page_cusum_onset():
    rng = np.random.default_rng(6)
    env = noise_env(int(600 * FS), rng)
    env1 = rd.inject_envelope(env, FS, 300.0, np.ones(int(30 * FS)), snr_db=0.0, win_s=30)
    y = 20 * np.log10(env[: int(250 * FS)])
    m, s = rd.robust_loc_scale(y)
    g, last0 = rd.page_cusum(env1, FS, m, s, delta_sigma=1.0)
    i = int(np.argmax(g))
    assert abs(last0[i] / FS - 300.0) < 5.0


# --- S5, S6 (raw) ---------------------------------------------------------------

def test_teager_kaiser_sinusoid():
    n = np.arange(2000)
    A, w = 2.0, 0.1
    psi = rd.teager_kaiser(A * np.cos(w * n))
    assert np.allclose(psi[5:-5], A ** 2 * np.sin(w) ** 2, rtol=1e-6)


def test_spectral_kurtosis_impulsive_vs_gaussian():
    rng = np.random.default_rng(7)
    fs = 1000.0
    x = rng.standard_normal(int(60 * fs))
    z0, _ = rd.sk_statistic(x, fs, nperseg=256, fmin=8, fmax=100)
    y = x.copy()
    i0 = int(30 * fs)
    burst = sps.sosfiltfilt(rd.bandpass_sos(fs, 20, 40), rng.standard_normal(int(0.5 * fs))) * 30
    y[i0:i0 + burst.size] += burst
    z1, f1 = rd.sk_statistic(y, fs, nperseg=256, fmin=8, fmax=100)
    assert z0 < 4.5 and z1 > 10 and 15 <= f1 <= 45


def test_excess_power_finds_tile():
    rng = np.random.default_rng(8)
    fs = 500.0
    x = rng.standard_normal(int(120 * fs))
    f, P = sps.welch(x, fs, nperseg=125)
    lp0, _ = rd.excess_power(x, fs, f, P, fmin=8, fmax=100)
    y = rd.inject_raw(x, fs, 60.0, rd.impulsive_shape(10.0, 0.5, 2.0), snr_db=-3.0, band=(20, 40), rng=1)
    lp1, tile = rd.excess_power(y, fs, f, P, fmin=8, fmax=100)
    assert lp1 > lp0 + 5 and abs(tile[0] - 60.0) < 8


# --- S7 shot population ---------------------------------------------------------

def make_shots(rng, n_shots=60, period=9.98, contaminate=None, snr_db=0.0):
    T = n_shots * period + 20
    env = noise_env(int(T * FS), rng)
    sh = rd.impulsive_shape(FS, 0.3, 1.0, dur_s=4.0)
    onsets = 5 + period * np.arange(n_shots)
    for t in onsets:
        env = rd.inject_envelope(env, FS, t, sh * (1 + 0.05 * rng.standard_normal()), snr_db=15, noise_ref=env)
    if contaminate is not None:
        env = rd.inject_envelope(env, FS, onsets[contaminate] + 1.5, rd.impulsive_shape(FS, 0.5, 3.0, 6.0), snr_db=snr_db)
    return env, onsets


def test_segment_shots_measures_interval():
    rng = np.random.default_rng(9)
    env, onsets = make_shots(rng)
    s = rd.segment_shots(env, FS)
    assert abs(s.interval_s_median - 9.98) < 0.15
    assert abs(s.interval_s_acf - 9.98) < 0.25
    assert abs(len(s.onsets) - len(onsets)) <= 2


def test_shot_population_flags_contaminated_shot():
    rng = np.random.default_rng(10)
    env, onsets = make_shots(rng, contaminate=30, snr_db=8.0)
    s = rd.segment_shots(env, FS)
    feats, M = rd.shot_features(env, FS, s)
    res = rd.shot_population_test(feats, M, FS, n_mc=60, rng=0)
    i = int(np.argmin(res["p_global"]))
    c0 = feats["cycle_start_s"][i]
    assert c0 <= onsets[30] + 1.5 < c0 + feats["period_s_fit"]
    assert res["p_global"][i] < 0.05
    assert abs(feats["period_s_fit"] - 9.98) < 0.05


def test_shot_population_null_not_significant():
    env, _ = make_shots(np.random.default_rng(21))
    s = rd.segment_shots(env, FS)
    feats, M = rd.shot_features(env, FS, s)
    res = rd.shot_population_test(feats, M, FS, n_mc=60, rng=1)
    assert res["p_global"].min() > 0.05


# --- S8 picks -----------------------------------------------------------------

def test_scan_statistic_cluster():
    rng = np.random.default_rng(11)
    t = np.sort(rng.uniform(0, 3600, 20))
    k0 = rd.scan_count(t, 0, 3600, 60)
    t1 = np.r_[t, 1800 + rng.uniform(0, 30, 6)]
    k1 = rd.scan_count(t1, 0, 3600, 60)
    assert k1 >= 6 and k1 > k0
    p = rd.scan_p_poisson(k1, 20 / 3600, 3600, 60, n_mc=3000, rng=0)
    assert p < 0.01


# --- geometry ------------------------------------------------------------------

def test_arc_point_on_small_circle_and_offset():
    lat, lon = rd.arc_point(-35.0)
    c = rd._xyz(*rd.ARC_CENTRE)
    d = np.degrees(np.arccos(c @ rd._xyz(lat, lon)))
    assert abs(d - rd.ARC_RADIUS_DEG) < 1e-6 and 85 < lon < 110
    lat2, lon2 = rd.arc_point(-35.0, offset_nm=50)
    d2 = np.degrees(np.arccos(c @ rd._xyz(lat2, lon2)))
    assert abs((d2 - rd.ARC_RADIUS_DEG) * 60 - 50 * 6371.0088 / 6366.7) < 0.5


# --- B1, C1 -------------------------------------------------------------------

def _two_station_setup(rng, with_signal):
    T = 1800.0
    st = {"A": (0.0, T), "B": (0.0, T)}
    trig = {s: {"t": rng.uniform(0, T, 12), "z": rng.uniform(2, 3, 12)} for s in st}
    cells = []
    for t0 in np.arange(100, 400, 10.0):
        cells.append({"A": (t0 + 600, t0 + 620), "B": (t0 + 900, t0 + 920)})
    if with_signal:
        trig["A"]["t"] = np.r_[trig["A"]["t"], 810.0]
        trig["A"]["z"] = np.r_[trig["A"]["z"], 3.5]
        trig["B"]["t"] = np.r_[trig["B"]["t"], 1110.0]
        trig["B"]["z"] = np.r_[trig["B"]["z"], 3.5]
    return trig, cells, st


def test_time_slide_coincidence():
    rng = np.random.default_rng(12)
    trig, cells, span = _two_station_setup(rng, True)
    obs, ci, ns = rd.grid_coincidence_max(trig, cells)
    null = rd.time_slide_null(trig, cells, span, min_shift=60, n_slides=400, rng=1)
    p = rd.empirical_p(obs, null)
    assert ns == 2 and abs(list(cells[ci].values())[0][0] - 810) <= 20 and p < 0.05
    trig0, cells0, span0 = _two_station_setup(np.random.default_rng(13), False)
    obs0 = rd.grid_coincidence_max(trig0, cells0)[0]
    null0 = rd.time_slide_null(trig0, cells0, span0, min_shift=60, n_slides=400, rng=2)
    assert rd.empirical_p(obs0, null0) > 0.05


def test_stack_brightness():
    t = np.arange(0, 1800, 1.0)
    za, zb = np.zeros_like(t), np.zeros_like(t)
    za[810], zb[1110] = 3.0, 3.0
    cells = [{"A": (t0 + 600, t0 + 620), "B": (t0 + 900, t0 + 920)} for t0 in np.arange(100, 400, 10.0)]
    B, N = rd.stack_brightness({"A": (t, za), "B": (t, zb)}, cells)
    assert B.max() == 6.0 and N.min() == 2


# --- C2, C3, C4 -------------------------------------------------------------------

def test_discord_and_repeats():
    rng = np.random.default_rng(14)
    per = np.tile(np.r_[np.hanning(20), np.zeros(80)], 30) + 0.05 * rng.standard_normal(3000)
    y = per.copy()
    y[1520:1560] += np.linspace(0, 1, 40) ** 2
    nn_rep, rep_rep = rd.discord_and_repeats(y, 300, 60)
    nn_new, rep_new = rd.discord_and_repeats(y, 1510, 60)
    assert nn_new > 2 * nn_rep and rep_rep > rep_new


def test_template_ncc_peak():
    rng = np.random.default_rng(15)
    tmpl = rd.impulsive_shape(FS, 1.0, 3.0, 15.0)
    y = 0.2 * rng.standard_normal(2000)
    y[1200:1200 + tmpl.size] += tmpl
    r = rd.template_ncc(y, tmpl)
    assert abs(int(np.argmax(r)) - 1200) <= 1 and r.max() > 0.7


def test_pelt_mean():
    rng = np.random.default_rng(16)
    y = np.r_[rng.normal(0, 1, 300), rng.normal(3, 1, 200), rng.normal(0, 1, 300)]
    cps = rd.pelt_mean(y, penalty=2 * np.log(y.size) * 3, sigma=1.0)
    assert len(cps) == 2 and abs(cps[0] - 300) <= 5 and abs(cps[1] - 500) <= 5


# --- known events, injection -----------------------------------------------------

def test_association_probability():
    assert rd.association_probability(100.0, 100.0, 2.0, 1 / 300) > 0.95
    assert rd.association_probability(130.0, 100.0, 2.0, 1 / 300) < 0.01


def test_inject_envelope_snr_definition():
    rng = np.random.default_rng(17)
    env = noise_env(20000, rng)
    sh = np.ones(100)
    e1 = rd.inject_envelope(env, FS, 1000.0, sh, snr_db=0.0, win_s=10)
    added = np.mean(e1[10000:10100] ** 2 - env[10000:10100] ** 2)
    assert added == pytest.approx(np.median(env ** 2), rel=1e-6)
