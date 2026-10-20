"""Non-dimensional 747 stability and control derivatives recovered from CR-2144's dimensional tables.

Standard small-perturbation relations (Etkin and Reid; Nelson, *Flight Stability and Automatic Control*),
applied in STABILITY axes after rotating CR-2144's body-axis longitudinal derivatives by alpha0 (the lateral
ones stay in body axes, which is the simulator's own convention), with U0 = VT. Longitudinal (CL and CD at trim from the module's polar are not needed here):
  CL_alpha = -Zw m U0 / (q S) - CD0_trim        Cm_alpha = Mw Iy U0 / (q S c)
  Cm_q     = Mq 2 Iy U0 / (q S c^2)               Cm_alphadot = Mwd 2 Iy U0^2 / (q S c^2)
  Cm_M     = Mu Iy U0 / (q S c M)                 CL_M = (-Zu m U0 / (q S) - 2 CL) / M
  CL_q     = -Zq 2 m U0 / (q S c)                 Cm_de = Mde Iy / (q S c), CL_de = -Zde m / (q S)
Lateral (body axes; CR-2144's primed L', N' include the Ixz coupling, undone first):
  [L, N] solves L' = (L + Ixz/Ix N) / D, N' = (N + Ixz/Iz L) / D, D = 1 - Ixz^2 / (Ix Iz)
  Cy_beta = Yv m VT / (q S)
  Cl_beta = Lbeta Ix / (q S b)          Cl_p = Lp 2 Ix VT / (q S b^2)      Cl_r = Lr 2 Ix VT / (q S b^2)
  Cn likewise with Iz; Cl_da = Lda Ix / (q S b), and similarly for the other control derivatives.
Which convention is right is tested, not assumed: sixdof.linearise() at each 747 condition must reproduce
CR-2144's printed modes (tests in test_sim.py).
"""
import numpy as np
from cr2144_747 import (S_FT2, B_FT, CBAR_FT, MACH, VT_FPS, W_LB, IX, IY, IZ, IXZ, Q_PSF, ALPHA_DEG, LON, LAT,
                        H_FT, G_FPS2)


def nondim(i, cd_trim=0.025):
    m = W_LB[i] / G_FPS2; q = Q_PSF[i]; V = VT_FPS[i]; a = np.radians(ALPHA_DEG[i]); U0 = V
    M = MACH[i]; S, b, c = S_FT2, B_FT, CBAR_FT; Ix, Iy, Iz, Ixz = IX[i], IY[i], IZ[i], IXZ[i]
    lo = {k: v[i] for k, v in LON.items()}; la = {k: v[i] for k, v in LAT.items()}
    # CR-2144's longitudinal derivatives are body-axis; the relations below are stability-axis. Rotate by
    # alpha0: velocities and forces both rotate, so D_s = R D_b R^T for [[Xu, Xw], [Zu, Zw]] and
    # [Mu, Mw]_s = [Mu, Mw]_b R^T, with R = [[cos a, sin a], [-sin a, cos a]].
    R = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    Db = np.array([[lo["XU"], lo["XW"]], [lo["ZU"], lo["ZW"]]]); Ds = R @ Db @ R.T
    Ms = np.array([lo["MU"], lo["MW"]]) @ R.T
    lo.update(XU=Ds[0, 0], XW=Ds[0, 1], ZU=Ds[1, 0], ZW=Ds[1, 1], MU=Ms[0], MW=Ms[1])
    CL = W_LB[i] / (q * S)
    out = dict(fc=i + 1, h_ft=H_FT[i], mach=M, CL_trim=CL, alpha0_deg=ALPHA_DEG[i],
               CL_alpha=-lo["ZW"] * m * U0 / (q * S) - cd_trim,
               Cm_alpha=lo["MW"] * Iy * U0 / (q * S * c),
               Cm_q=lo["MQ"] * 2 * Iy * U0 / (q * S * c ** 2),
               Cm_alphadot=lo["MWD"] * 2 * Iy * U0 ** 2 / (q * S * c ** 2),
               Cm_M=lo["MU"] * Iy * U0 / (q * S * c * M),
               CL_M=(-lo["ZU"] * m * U0 / (q * S) - 2 * CL) / M,
               CL_q=-lo["ZQ"] * 2 * m * U0 / (q * S * c),
               Cm_de=lo["MDE"] * Iy / (q * S * c), CL_de=-lo["ZDE"] * m / (q * S))
    D = 1 - Ixz ** 2 / (Ix * Iz)
    A = np.array([[1.0, Ixz / Ix], [Ixz / Iz, 1.0]])
    def unprime(Lp_, Np_):
        L, N = np.linalg.solve(A, np.array([Lp_, Np_]) * D); return L, N
    Lb, Nb = unprime(la["LB"], la["NB"]); Lp, Np = unprime(la["LP"], la["NP"]); Lr, Nr = unprime(la["LR"], la["NR"])
    Lda, Nda = unprime(la["LDA"], la["NDA"]); Ldr, Ndr = unprime(la["LDR"], la["NDR"])
    k1, k2 = q * S * b, q * S * b ** 2 / (2 * V)
    out.update(Cy_beta=la["YV"] * m * V / (q * S), Cy_dr=la["YDR"] * m * V / (q * S),
               Cl_beta=Lb * Ix / k1, Cn_beta=Nb * Iz / k1, Cl_p=Lp * Ix / k2, Cn_p=Np * Iz / k2,
               Cl_r=Lr * Ix / k2, Cn_r=Nr * Iz / k2, Cl_da=Lda * Ix / k1, Cn_da=Nda * Iz / k1,
               Cl_dr=Ldr * Ix / k1, Cn_dr=Ndr * Iz / k1)
    return out


def table():
    return [nondim(i) for i in range(10)]


if __name__ == "__main__":
    for d in table():
        print(d["fc"], d["h_ft"], d["mach"], {k: round(v, 4) for k, v in d.items() if k not in ("fc", "h_ft", "mach")})
