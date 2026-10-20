"""Boeing 747 data transcribed from NASA CR-2144 (Heffley and Jewell, *Aircraft Handling Qualities Data*,
December 1972; NTRS 19730003312; US Government work, public use permitted), Section IX.

Transcribed by eye from page images (the scan's text layer is unusable). Printed page numbers:
  Table IX-3 (p. 229)  dimensional, mass and flight-condition parameters
  Table IX-4 (p. 230)  longitudinal dimensional derivatives, body axes (US units: ft, s, rad)
  Table IX-5 (p. 231)  elevator transfer-function factors (used here only as a transcription check)
  Table IX-8 (p. 234)  lateral-directional dimensional derivatives, body axes (primed: Ixz-coupled)
Geometry (Fig. IX-2, p. 213): S = 5500 ft^2, b = 195.68 ft, cbar = 27.31 ft.
Every value is checked against the page image before use; see check_longitudinal().
"""
import numpy as np

S_FT2, B_FT, CBAR_FT = 5500.0, 195.68, 27.31
FC = list(range(1, 11))
# Table IX-3
H_FT = [0, 0, 0, 0, 20000, 20000, 20000, 40000, 40000, 40000]
MACH = [.198, .249, .450, .650, .500, .650, .800, .700, .800, .900]
VT_FPS = [221, 278, 502, 726, 518, 674, 830, 678, 774, 871]
W_LB = [564032, 564032] + [636636] * 8
IX = [.142e8, .142e8] + [.182e8] * 8
IY = [.323e8, .323e8] + [.331e8] * 8
IZ = [.454e8, .454e8] + [.497e8] * 8
IXZ = [870050, 870050] + [970056] * 8
Q_PSF = [58.1, 92.2, 300, 626, 170, 298, 436, 135, 177, 224]
ALPHA_DEG = [8.50, 5.70, 3.10, 0., 6.80, 2.50, 0., 7.30, 4.60, 2.40]
GAMMA_DEG = [0.] * 10
# Table IX-4 (body axis). Asterisked rows (XU, ZU, MU) as printed.
LON = {
 "XU":  [-.0209, -.0108, -.00499, -.00777, -.00247, -.00280, -.00643, .00187, -.00276, -.0200],
 "ZU":  [-.202, -.150, -.0807, -.126, -.0679, -.0832, -.0941, -.0696, -.0650, -.0424],
 "MU":  [.000117, .000181, .000146, -.000199, .000247, .885e-4, -.000222, .000259, .000193, -.623e-4],
 "XW":  [.122, .106, .0743, .0345, .0782, .0482, .0253, .0263, .0389, .0159],
 "ZW":  [-.512, -.613, -.736, -.963, -.433, -.539, -.624, -.292, -.317, -.401],
 "MW":  [-.00177, -.00193, -.00262, -.00239, -.00170, -.00190, -.00153, -.00101, -.00105, -.00190],
 "ZWD": [.0334, .0338, .0297, .0293, .0157, .0156, .0144, .00704, .00556, .00614],
 "ZQ":  [-6.22, -7.58, -10.4, -12.8, -6.39, -8.09, -9.98, -4.32, -5.16, -6.71],
 "MWD": [-.000246, -.000240, -.000221, -.000228, -.000125, -.000155, -.000212, -.905e-4, -.000116, -.000160],
 "MQ":  [-.357, -.437, -.699, -.925, -.421, -.535, -.659, -.284, -.339, -.401],
 "XDE": [.959, .971, 1.18, 0., 2.02, 1.15, 0., 1.93, 1.44, .781],
 "ZDE": [-6.42, -9.73, -21.8, -32.4, -16.9, -26.4, -32.7, -15.1, -17.9, -18.6],
 "MDE": [-.378, -.574, -1.40, -2.07, -1.09, -1.69, -2.08, -.970, -1.16, -1.22],
}
# Table IX-5 denominators: (zeta, omega) phugoid then short period, as printed
DEN = {1: (.0417, .152, .616, .771), 2: (.0228, .127, .629, .910), 3: (.0319, .0753, .575, 1.37),
       4: (.110, .0368, .637, 1.63), 5: (.0241, .0823, .446, 1.04), 6: (.0264, .0653, .473, 1.26),
       7: (.323, .00984, .567, 1.30), 8: (.0636, .0781, .357, .879), 9: (.0489, .0673, .387, .964),
       10: (.304, .0311, .351, 1.35)}
# Table IX-8 (body axis, primed L and N include the Ixz coupling)
LAT = {
 "YV":  [-.0890, -.0997, -.143, -.197, -.0822, -.104, -.120, -.0488, -.0558, -.0606],
 "YB":  [-19.7, -27.8, -71.7, -143., -42.6, -70.4, -99.4, -33.1, -43.2, -52.8],
 "LB":  [-1.33, -1.63, -3.19, -5.45, -2.05, -2.96, -4.12, -1.45, -3.05, -1.32],
 "NB":  [.168, .247, .810, 1.82, .419, .923, 1.62, .404, .598, .971],
 "LP":  [-.975, -1.10, -1.12, -1.47, -.652, -.804, -.974, -.404, -.465, -.459],
 "NP":  [-.166, -.125, -.0706, -.0214, -.0701, -.0531, -.0157, -.0366, -.0316, .00284],
 "LR":  [.327, .198, .379, .256, .376, .317, .292, .312, .388, .280],
 "NR":  [-.217, -.229, -.246, -.344, -.140, -.193, -.232, -.0963, -.115, -.141],
 "LDA": [.227, .318, .229, .372, .128, .210, .310, .0964, .143, .186],
 "NDA": [.0264, .0300, .0285, .0371, .0177, .0199, .0127, .00875, .00775, -.00611],
 "YDR": [.0148, .0182, .0226, .0213, .0131, .0142, .0124, .00777, .00729, .00464],
 "LDR": [.0636, .110, .254, .318, .148, .211, .183, .115, .153, .100],
 "NDR": [-.151, -.233, -.614, -.970, -.391, -.616, -.922, -.331, -.475, -.442],
}
G_FPS2 = 32.174


def lon_matrix(i):
    """Body-axis longitudinal A matrix, state [u, w, q, theta], flight condition index i (0-based)."""
    d = {k: v[i] for k, v in LON.items()}
    a = np.radians(ALPHA_DEG[i]); th0 = a + np.radians(GAMMA_DEG[i])
    U0, W0 = VT_FPS[i] * np.cos(a), VT_FPS[i] * np.sin(a); g = G_FPS2
    den = 1 - d["ZWD"]
    zu, zw, zq, zt = d["ZU"] / den, d["ZW"] / den, (U0 + d["ZQ"]) / den, -g * np.sin(th0) / den
    A = np.array([[d["XU"], d["XW"], -W0, -g * np.cos(th0)],
                  [zu, zw, zq, zt],
                  [d["MU"] + d["MWD"] * zu, d["MW"] + d["MWD"] * zw, d["MQ"] + d["MWD"] * zq, d["MWD"] * zt],
                  [0, 0, 1, 0]])
    return A


def modes(A):
    ev = np.linalg.eigvals(A); out = []
    for e in ev[np.imag(ev) > 0]:
        w = abs(e); out.append((float(-e.real / w), float(w)))
    return sorted(out, key=lambda x: x[1])


def check_longitudinal():
    rows = []
    for i, fc in enumerate(FC):
        m = modes(lon_matrix(i))
        rows.append((fc, m, DEN[fc]))
    return rows


if __name__ == "__main__":
    for fc, m, ref in check_longitudinal():
        print(fc, [tuple(round(x, 4) for x in t) for t in m], ref)

# Table IX-9 (p. 235) aileron transfer-function denominators, SAS off: (1/T spiral, 1/T roll, zeta_DR, omega_DR)
DEN_LAT = {1: (.0427, 1.11, .0878, .735), 2: (.0465, 1.23, .107, .746), 3: (.0194, 1.23, .126, 1.06),
           4: (.0203, 1.56, .153, 1.40), 5: (.00903, .745, .0693, .863), 6: (.0108, .913, .0823, 1.07),
           7: (.0103, 1.06, .0981, 1.31), 8: (-.00234, .462, .0568, .788), 9: (.00730, .562, .0349, .947),
           10: (-.00777, .478, .0929, 1.02)}


def lat_matrix(i):
    """Body-axis lateral A matrix, state [beta, p, r, phi]; primed L', N' already include Ixz."""
    d = {k: v[i] for k, v in LAT.items()}
    a = np.radians(ALPHA_DEG[i]); th0 = a + np.radians(GAMMA_DEG[i]); V = VT_FPS[i]
    U0, W0 = V * np.cos(a), V * np.sin(a)
    return np.array([[d["YV"], W0 / V, -U0 / V, G_FPS2 * np.cos(th0) / V],
                     [d["LB"], d["LP"], d["LR"], 0],
                     [d["NB"], d["NP"], d["NR"], 0],
                     [0, 1, np.tan(th0), 0]])


def lat_modes(A):
    ev = np.linalg.eigvals(A); real = sorted(ev[np.abs(ev.imag) < 1e-9].real, key=abs)
    cx = ev[ev.imag > 1e-9]
    zw = [(float(-e.real / abs(e)), float(abs(e))) for e in cx]
    return [float(-r) for r in real], zw


def check_lateral():
    return [(fc, lat_modes(lat_matrix(i)), DEN_LAT[fc]) for i, fc in enumerate(FC)]
