"""Unit tests: settling energy-transfer duration, impact_tau_method = 1.

Magnitudes are those of results/eof-impact-tau-method-oct11.md section 3:
  ditching at 70 m/s, tau90 about 1.8-7 s; steep entry at 200 m/s, 0.14-0.29 s; at 300 m/s, 0.10-0.19 s.
Row-alignment tests read the hand-off and sidecar files named by the environment variables HANDOFF_DIR and
SIDECAR_DIR (skipped if absent).
"""
import os
import numpy as np
import pytest
import settling_energy_transfer_m1 as m1

M = 174196.0  # zero-fuel mass (kg); tau does not depend on m, the peak rate does


def ends(v, theta):
    a = np.array([m1.A_BAR_G[1], m1.A_BAR_G[0]]) * m1.G0          # fastest, slowest
    L = np.array([m1.L_EFF_FRAC[0], m1.L_EFF_FRAC[1]]) * m1.L777_M  # shortest, longest
    r = m1.method1(np.full(2, v), np.full(2, theta), np.full(2, M), a, L)
    return r["tau90"]


def test_constants():
    assert round(m1.C05_SH, 4) == 0.0253
    assert round(m1.C95_SH, 3) == 0.776
    assert round(m1.C95_SH - m1.C05_SH, 3) == 0.751


def test_ditching_70():
    lo, hi = ends(70.0, 0.0)
    assert round(lo, 1) == 1.8 and round(hi) == 7
    assert np.isclose(lo, 0.751 * 70 / (3 * m1.G0), rtol=1e-3)


def test_steep_200_and_300():
    lo, hi = ends(200.0, 60.0)
    assert (round(lo, 2), round(hi, 2)) == (0.14, 0.29)
    lo, hi = ends(300.0, 89.0)
    assert (round(lo, 2), round(hi, 2)) == (0.10, 0.19)


def test_sampled_draws_inside_note_ranges():
    n = 200000
    a, L = m1.draw_parameters(1, np.full(n, 3), np.arange(n))
    assert a.min() >= 0.75 * m1.G0 and a.max() <= 3.0 * m1.G0
    assert L.min() >= 0.5 * m1.L777_M and L.max() <= m1.L777_M
    t = m1.method1(np.full(n, 70.0), np.zeros(n), np.full(n, M), a, L)["tau90"]
    assert 1.78 < t.min() and t.max() < 7.16
    t = m1.method1(np.full(n, 200.0), np.full(n, 45.0), np.full(n, M), a, L)["tau90"]
    assert 0.143 <= t.min() and t.max() <= 0.2867
    # the uniform draws are close to uniform
    u = m1.uniforms(2, np.full(n, 7), np.arange(n), 0)
    assert abs(u.mean() - 0.5) < 0.005 and abs(u.var() - 1 / 12) < 0.002
    assert abs(np.corrcoef(m1.uniforms(2, np.full(n, 7), np.arange(n), 0),
                           m1.uniforms(2, np.full(n, 7), np.arange(n), 1))[0, 1]) < 0.01


def test_pure_regime_formulas():
    v, a, L = 150.0, 2.0 * m1.G0, 40.0
    r = m1.method1([v], [5.0], [M], np.array([a]), np.array([L]))
    T = v / a
    assert np.allclose([r["t05"][0], r["t95"][0], r["peak"][0]], [0.0253 * T, 0.7764 * T, M * a * v], rtol=1e-3)
    r = m1.method1([v], [35.0], [M], np.array([a]), np.array([L]))
    ke = 0.5 * M * v * v
    assert np.allclose([r["t05"][0], r["t95"][0], r["tau90"][0], r["peak"][0]],
                       [0.05 * L / v, 0.95 * L / v, 0.9 * L / v, ke * v / L], rtol=1e-12)
    assert r["tau90"][0] == pytest.approx(r["tau90_logblend"][0], rel=1e-12)


def test_blend_log_linear_and_band_edges():
    v, a, L = 120.0, 1.5 * m1.G0, 50.0
    sh, st = m1.regimes(np.array([v]), np.array([M]), np.array([a]), np.array([L]))
    r = m1.method1([v], [20.0], [M], np.array([a]), np.array([L]))   # w = 0.5
    assert r["w"][0] == pytest.approx(0.5)
    assert r["t05"][0] == pytest.approx(np.sqrt(sh["t05"][0] * st["t05"][0]), rel=1e-12)
    assert r["tau90_logblend"][0] == pytest.approx(np.sqrt(sh["tau90"][0] * st["tau90"][0]), rel=1e-12)
    assert r["tau90"][0] == pytest.approx(r["t95"][0] - r["t05"][0], rel=1e-12)
    s = m1.method1([v], [20.0], [M], np.array([a]), np.array([L]), m1.BAND_SENS_DEG)
    assert s["w"][0] == pytest.approx(15.0 / 40.0)
    for th, w in [(10.0, 0.0), (30.0, 1.0), (-35.0, 1.0)]:
        assert m1.method1([v], [th], [M], np.array([a]), np.array([L]))["w"][0] == w


def test_nan_means_not_computed():
    r = m1.method1([np.nan, 0.0, 100.0], [10.0, 10.0, np.nan], [M, M, M], np.full(3, 15.0), np.full(3, 40.0))
    assert np.isnan(r["tau90"]).all() and np.isnan(r["peak"]).all()


def test_draws_reproducible_and_chunk_independent():
    seed = np.array([1, 1, 2, 2, 16]); row = np.array([0, 1, 2, 3, 501101])
    a1, l1 = m1.draw_parameters(1, seed, row)
    a2, l2 = m1.draw_parameters(1, seed[::-1], row[::-1])
    assert np.array_equal(a1, a2[::-1]) and np.array_equal(l1, l2[::-1])
    a3, _ = m1.draw_parameters(2, seed, row)
    assert not np.any(a1 == a3)


def test_bank_assigned_rule():
    h = {"mass_kg": np.full(5, M, np.float32), "kinetic_energy_j": np.full(5, 3e9, np.float32),
         "flight_path_angle_deg_descent_positive": np.array([1, 20, 40, 60, 5], np.float32),
         "seed": np.ones(5, np.int16), "family_code": np.array([1, 2, 2, 3, 3], np.int8),
         "bank_deg": np.array([0.0, 0.0, 3.0, 0.0, -0.5], np.float32)}
    s = m1.build_sidecar(h, "wp")
    assert s["bank_assigned"].tolist() == [0, 1, 0, 1, 0]
    assert np.array_equal(s["kinetic_energy_at_contact_j"], h["kinetic_energy_j"].astype(np.float64))
    assert s["kinetic_energy_at_contact_j"] is not s["impact_energy_transferred_j"]


HANDOFF = os.environ.get("HANDOFF_DIR"); SIDECAR = os.environ.get("SIDECAR_DIR")


@pytest.mark.skipif(not (HANDOFF and SIDECAR), reason="HANDOFF_DIR and SIDECAR_DIR not set")
@pytest.mark.parametrize("route", ["df", "wp"])
def test_sidecar_row_alignment(route):
    h = np.load(f"{HANDOFF}/eof-final-handoff-{route}.npz")
    s = np.load(f"{SIDECAR}/settling-energy-transfer-m1-{route}.npz")
    n = h["mass_kg"].shape[0]
    assert {"df": 501102, "wp": 500198}[route] == n
    for k in m1.SIDECAR_COLUMNS:
        assert s[k].shape[0] == n, k
    assert np.array_equal(s["row_index"], np.arange(n))
    assert np.array_equal(s["seed"], h["seed"])
    assert np.array_equal(s["kinetic_energy_at_contact_j"], h["kinetic_energy_j"].astype(np.float64))
    v = np.sqrt(2.0 * h["kinetic_energy_j"].astype(np.float64) / h["mass_kg"].astype(np.float64))
    assert np.allclose(s["contact_speed_mps"], v, rtol=1e-6)
    # recompute a random subset of rows from the hand-off alone; must match the stored row exactly
    idx = np.random.default_rng(0).choice(n, 2000, replace=False)
    sub = {k: h[k][idx] for k in ("mass_kg", "kinetic_energy_j", "flight_path_angle_deg_descent_positive",
                                  "family_code", "bank_deg", "seed")}
    a, L = m1.draw_parameters(m1.ROUTE_CODE[route], sub["seed"].astype(np.int64), idx)
    assert np.array_equal(a, s["a_bar_mps2"][idx]) and np.array_equal(L, s["l_eff_m"][idx])
    r = m1.method1(v[idx], np.abs(sub["flight_path_angle_deg_descent_positive"]), sub["mass_kg"], a, L)
    assert np.array_equal(r["tau90"].astype(np.float32), s["energy_transfer_tau90_s"][idx])
    ba = ((h["family_code"] == 2) | (h["family_code"] == 3)) & (h["bank_deg"] == 0.0)
    assert np.array_equal(s["bank_assigned"].astype(bool), ba)
