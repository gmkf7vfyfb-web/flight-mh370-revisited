"""In-memory equivalent of drift's export_per_impact.py for one seed: the same surfaces (score_impacts.surface_arrays), the
same lookup (score_impacts.lookup, unchanged), the same column definitions. Returns the structured array instead of writing it."""
import os, sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'scorer'))
from score_impacts import lookup, surface_arrays
from export_per_impact import MODELS_DEFAULT, BW
REB = '/Users/pete/Downloads/mh370-exchange/debris-drift/runA-rebuilt'
_S = None
def surfs():
    global _S
    if _S is None: _S = {(m, b): surface_arrays(os.path.join(REB, d), c) for m, d in MODELS_DEFAULT.items() for b, c in BW.items()}
    return _S
def columns(lat, lon, parent):
    S = surfs(); fields = [('row', 'u4'), ('parent', 'i4')]
    for b in BW:
        for m in MODELS_DEFAULT: fields += [(f'lnL_{m}_{b}', 'f4'), (f'state_{m}_{b}', 'u1')]
        fields.append((f'lnL_mean_{b}', 'f4'))
    A = np.zeros(lat.size, dtype=fields); A['row'] = np.arange(lat.size, dtype=np.uint32); A['parent'] = parent.astype(np.int32); summ = {}
    for b in BW:
        vals = {}
        for m in MODELS_DEFAULT:
            flag, ll = lookup(*S[(m, b)], lat, lon)
            A[f'lnL_{m}_{b}'] = np.where(flag == 1, ll, np.nan).astype(np.float32); A[f'state_{m}_{b}'] = flag.astype(np.uint8)
            vals[m] = np.where(flag == 1, ll, np.nan); summ[f'{m}_{b}'] = {k: int((flag == v).sum()) for k, v in (('scored', 1), ('outside_support', 0), ('mc_unresolved', 2))}
        a, c = vals['glorys12'], vals['globcurrent']
        with np.errstate(invalid='ignore'):
            A[f'lnL_mean_{b}'] = np.where(np.isfinite(a) & np.isfinite(c), np.logaddexp(a, c) - np.log(2.0), np.nan).astype(np.float32)
    return A, summ
