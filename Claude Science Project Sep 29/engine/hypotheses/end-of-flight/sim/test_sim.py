"""Physics checks for the 6-DOF reference simulator.  Run: PYTHONPATH=. python -m pytest -q test_sim.py
(or python test_sim.py). The 747 checks fly CR-2144's own aircraft and compare its bare-airframe modes with
the printed Tables IX-5 and IX-9. Tolerances are stated per mode and reflect what the model claims."""
import numpy as np
import cr2144_747 as C
from check_747_modes import sched  # noqa: F401  (builds schedules)
import check_747_modes as K

TOL = dict(spiral=0.10, roll=0.04, dr_w=0.02, dr_z=0.15, sp_w=0.04, ph_w=0.06)


def by_fc():
    return {r[0]: r for r in K.rows}


def test_transcription_reproduces_printed_modes():
    for fc, m, ref in C.check_longitudinal():
        (zp, wp), (zs, ws) = m
        assert abs(wp / ref[1] - 1) < 0.05 and abs(ws / ref[3] - 1) < 0.02, fc
    for fc, (real, zw), ref in C.check_lateral():
        assert abs(real[0] - ref[0]) < 0.0005 and abs(real[1] / ref[1] - 1) < 0.02, fc


def test_lateral_modes_of_the_747_in_the_6dof():
    for fc, r in by_fc().items():
        _, _, _, zw, re, lon, lat = r
        spiral, roll = re[0], re[1]
        assert abs(-spiral - lat[0]) < TOL["spiral"] * abs(lat[0]) + 3e-4, (fc, spiral, lat[0])
        assert abs(-roll / lat[1] - 1) < TOL["roll"], (fc, roll)
        dr = min((t for t in zw if t[0] < 0.2 and t[1] > 0.3), key=lambda t: abs(t[1] - lat[3]))  # light damping
        assert abs(dr[1] / lat[3] - 1) < TOL["dr_w"] and abs(dr[0] / lat[2] - 1) < TOL["dr_z"], (fc, dr)


def test_short_period_and_phugoid_of_the_747_in_the_6dof():
    for fc, r in by_fc().items():
        _, _, _, zw, re, lon, lat = r
        sp = min((t for t in zw if t[0] >= 0.2), key=lambda t: abs(t[1] - lon[3]))  # heavily damped
        assert abs(sp[1] / lon[3] - 1) < TOL["sp_w"], (fc, sp)
        if fc in (5, 6, 8, 9):   # interior nodes; at the tuck-onset nodes (7, 10) Mu crosses zero
            ph = min(zw, key=lambda t: t[1])
            assert abs(ph[1] / lon[1] - 1) < TOL["ph_w"], (fc, ph)


if __name__ == "__main__":
    for f in (test_transcription_reproduces_printed_modes, test_lateral_modes_of_the_747_in_the_6dof,
              test_short_period_and_phugoid_of_the_747_in_the_6dof):
        f(); print("pass", f.__name__)


def test_energy_is_conserved_without_drag_or_thrust():
    """No drag, no thrust, no wind, stick-fixed: lift does no work, so h + V^2/2g is constant."""
    from model import schedules, default_params, trim, state
    from sixdof import simulate, FT, KT, G
    sched = schedules()
    P = default_params(CD0=0.0, k_ind=0.0, kw=0.0, dCD_wm=0.0, dCD_rat=0.0, wind_sl=0.0, wind_slope=0.0,
                       t1=0.0, t2=0.0, t_loss=0.0, law=2, t_end=300.0, dt=0.02)
    h0, tas = 35000 * FT, 450 * KT
    al, de, T, ok = trim(h0, tas, 180.0, P, sched)
    rec = simulate(P, *sched, state(h0, tas, 180.0, al, P), de, 0.0)
    from sixdof import isa
    E = []
    for r in rec:
        h = r[3] * FT; rho, a = isa(h); V = r[5] * a
        E.append(h + V * V / (2 * G))
    E = np.array(E); drift = abs(E[-1] - E[0]) / E[0]
    assert drift < 1e-3, drift


if __name__ == "__main__":
    test_energy_is_conserved_without_drag_or_thrust(); print("pass test_energy_is_conserved_without_drag_or_thrust")
