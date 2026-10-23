
import os, sys, json, time, numpy as np, pandas as pd
os.environ["OMP_NUM_THREADS"]="4"
WS=os.getcwd()
MOD=f"{WS}/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sys.path.insert(0, MOD+"/prepare/composition_run_j"); sys.path.insert(0, MOD+"/prepare"); sys.path.insert(0, MOD+"/prepare/ranked_candidates")
import importlib, prereg as R  # composition prereg
import common as Cm
PR = importlib.import_module("ranked_candidates.prereg") if False else None
import importlib.util
spec=importlib.util.spec_from_file_location("rprereg", MOD+"/prepare/ranked_candidates/prereg.py"); P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
t0=time.time(); M=Cm.Machinery(imos_ramgrid=True); print("machinery", time.time()-t0, M.ramgrid_covered_share, M.pd_missing[:5])
EX="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches"
S=np.load(f"{EX}/geometry/sample.npz"); S={k:S[k] for k in S}
anyw=(S["w_D0"]>0)|(S["w_D2"]>0)|(S["w_D3"]>0)|(S["w_D4"]>0)
print(len(anyw), anyw.sum(), {o:(S[f"w_{o}"]>0).sum() for o in ["D0","D2","D3","D4"]})
