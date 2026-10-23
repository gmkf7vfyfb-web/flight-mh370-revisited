import types
pm=types.ModuleType('pyram'); pm2=types.ModuleType('pyram.PyRAM'); pm2.PyRAM=None; pm.PyRAM=pm2
sys.modules['pyram']=pm; sys.modules['pyram.PyRAM']=pm2   # only imported by ram_tl_check; no RAM run is made here
import common as Cm
M=Cm.Machinery(imos_ramgrid=True)
print({k:round(v,1) for k,v in M.bmed.items()}, M.ramgrid_covered_share, M.xs.min(), M.xs.max())