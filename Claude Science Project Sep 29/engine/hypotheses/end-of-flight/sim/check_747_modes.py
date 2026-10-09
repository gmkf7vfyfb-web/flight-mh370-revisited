"""Fly the 747 itself in the 6-DOF at CR-2144 conditions and compare the bare-airframe modes with the printed
ones (Tables IX-5 and IX-9). This tests the derivative recovery, the axis conventions and the equations at once."""
import numpy as np
import aero747 as A, cr2144_747 as C
from model import schedules, default_params, trim, linearise, LB, SLUG, FT2
from sixdof import FT, isa

sched = schedules()
rows = []
for fc in (5, 6, 7, 8, 9, 10):
    i = fc - 1; d = A.nondim(i)
    mass = C.W_LB[i] * LB
    h = C.H_FT[i] * FT
    I = np.array([C.IX[i], C.IY[i], C.IZ[i], C.IXZ[i]]) * SLUG * FT2
    h = C.H_FT[i] * FT; tas = C.VT_FPS[i] * FT
    from sixdof import coeff
    mh, vh, sh, ml, vl, sl = sched
    CLa = coeff(0, C.MACH[i], h, mh, vh, sh, ml, vl, sl); cl0 = coeff(20, C.MACH[i], h, mh, vh, sh, ml, vl, sl)
    a0 = np.radians(C.ALPHA_DEG[i]) - (d["CL_trim"] - cl0) / CLa
    P = default_params(mass=mass, Ix=I[0], Iy=I[1], Iz=I[2], Ixz=I[3], S=C.S_FT2 * FT2, b=C.B_FT * FT,
                       c=C.CBAR_FT * FT, alpha0L=a0, alpha_ref=np.radians(C.ALPHA_DEG[i]), CD0=0.018, k_ind=0.045,
                       kw=0.0, wind_sl=0.0, wind_slope=0.0, y_eng=0.0, dCD_wm=0.0, dCD_rat=0.0)
    al, de, T, ok = trim(h, tas, 180.0, P, sched)
    from model import state
    x0 = state(h, tas, 180.0, al, P)
    ctl = np.array([de, 0, 0, T, T, 0.0])
    J = linearise(x0, ctl, P, sched)
    ev = np.linalg.eigvals(J[3:13, 3:13])
    cx = sorted([e for e in ev if e.imag > 1e-6], key=lambda e: abs(e))
    re = sorted([e.real for e in ev if abs(e.imag) <= 1e-6 and abs(e.real) > 1e-5], key=abs)
    zw = [(-e.real / abs(e), abs(e)) for e in cx]
    rows.append((fc, np.degrees(al), ok, zw, re, C.DEN[fc], C.DEN_LAT[fc]))
    if __name__ == "__main__": print(f"FC{fc}: trim alpha {np.degrees(al):.2f} deg (CR-2144 {C.ALPHA_DEG[i]}) ok={ok}")
    if __name__ == "__main__": print("  complex (zeta, omega):", [(round(z, 4), round(w, 4)) for z, w in zw])
    if __name__ == "__main__": print("  real roots (s^-1):", [round(r, 5) for r in re])
    if __name__ == "__main__": print("  printed lon (z_ph, w_ph, z_sp, w_sp):", C.DEN[fc], " lat (1/Ts, 1/Tr, z_dr, w_dr):", C.DEN_LAT[fc])
