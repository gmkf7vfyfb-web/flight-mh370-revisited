import sys, os, json, numpy as np
sys.argv=["haixun_beacon.py","out"]
import io, contextlib
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(open("haixun_beacon.py").read())
# sonobuoy check: hydrophone at 300 m, seabed source; calibrate to 4,000 m capability with new source
def path_TL(zs, zr):
    i0,i1=int(zr),int(zs); s=(zs-zr); A=np.trapezoid(ag[i0:i1+1],dx=1)/1000
    return 20*np.log10(s)+A, A
TLb,Ab=path_TL(Z_BED,300); TLref,_=path_TL(4300,300)   # 4,000 m vertical reference path
SE_buoy={d: float(SL_spec(d)-TLb-(160.5-TLref)) for d in (29.3,31.3,35.0)}
# sensitivity grid for calibration A: B_H by f1 band x reacquisition miss product band
cal="A"
se1=SE_offset(cal,o1,DAY1,U1,idx); se2=SE_offset(cal,o2,DAY2,U2,idx)
sig=draw["sigma"][idx]; ptx=draw["P_tx"][idx]
p1=norm.cdf(se1/sig); p2=norm.cdf(se2/sig)
PD1=1-(1-p1)*(1-f1); PD2=1-(1-p2)*(1-f2); tt_=p1*p2/np.maximum(PD1*PD2,1e-300)
PDw=tt_*logistic((se1-se2-3)/2)+(1-tt_)*0.5
f_edges=np.array([0.02,0.035,0.05,0.1,0.2,0.35,0.5]); q_vals=np.array([0.02,0.05,0.1,0.2,0.4,0.7,1.0])
grid=np.zeros((len(q_vals),len(f_edges)-1))
for i,qp in enumerate(q_vals):
    PNq=pidie+(1-pidie)*qp
    for j in range(len(f_edges)-1):
        m=(f1>=f_edges[j])&(f1<f_edges[j+1])
        den=f1[m]*f2[m]*0.5
        grid[i,j]=(ptx[m]*PD1[m]*PD2[m]*PDw[m]*PNq[m]+(1-ptx[m])*den).mean()/den.mean()
print({k:round(v,2) for k,v in SE_buoy.items()}, round(TLb,1), round(Ab,1))
print(np.round(grid,2))
summ["sonobuoy_check"]={"TL_bed_to_300m_dB":float(TLb),"absorption_dB":float(Ab),"SE_vs_day_dB":SE_buoy,
   "note":"SE=0 defined at 4,000 m vertical slant with a new 160.5 dB source (ATSB capability statement)"}
summ["sensitivity_grid_A"]={"f1_edges":f_edges.tolist(),"q_product":q_vals.tolist(),"B_H":grid.round(4).tolist()}
json.dump(summ,open("out/bh_summary.json","w"),indent=1)