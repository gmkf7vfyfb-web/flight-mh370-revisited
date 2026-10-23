
sys.path=[p for p in sys.path if not p.endswith("ranked_candidates")]
for m in ["prereg","common"]: sys.modules.pop(m,None)
import prereg as R; import common as Cm
assert hasattr(R,"RD")
t0=time.time(); M=Cm.Machinery(imos_ramgrid=True); print("machinery", round(time.time()-t0,1), M.ramgrid_covered_share, M.pd_missing[:5], M.taus)
EX="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches"
S=np.load(f"{EX}/geometry/sample.npz"); S={k:S[k] for k in S}
anyw=(S["w_D0"]>0)|(S["w_D2"]>0)|(S["w_D3"]>0)|(S["w_D4"]>0)
print(len(anyw), anyw.sum(), {o:int((S[f"w_{o}"]>0).sum()) for o in ["D0","D2","D3","D4"]}, {o:float(S[f"w_{o}"].sum()) for o in ["D0","D2","D3","D4"]})
