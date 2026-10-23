import sys, importlib
MODP=os.path.abspath('hyd/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare')
for p in [MODP+'/composition_run_j', MODP]:
    if p not in sys.path: sys.path.insert(0,p)
import prereg as RR
print(RR.RD, RR.TL_TABLE_DIR_RAMGRID, RR.IMOS_TL_FILE_RAMGRID, RR.BANDS_HZ, RR.RECEIVERS, RR.METHOD, RR.ALPHAS, RR.TRIAD_GAIN_DB, RR.RHO_C, RR.TAU_CLIP)
import common as Cm
M=Cm.Machinery(imos_ramgrid=True)
print(M.bmed, M.ramgrid_covered_share)