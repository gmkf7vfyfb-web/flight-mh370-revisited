
import gsw
E = np.memmap("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026_elevation.i16", dtype="<i2", mode="r", shape=(gj["nlat"], gj["nlon"]))
def depth(la, lo):
    i = int(round((la-gj["lat0"])/gj["step_deg"])); j = int(round((lo-gj["lon0"])/gj["step_deg"])); return -float(E[i,j])
print("PC 3376 check depth (expect ~450 m):", depth(-31.8417,115.0133))
pts = g.npts(mlon, mlat, H01W[1], H01W[0], 200)
dep = np.array([depth(la,lo) for lo,la in pts])
print("path depth to H01W: min %.0f median %.0f max %.0f" % (dep.min(), np.median(dep), dep.max()))
# WOA23 March profile at the path midpoint
wj = json.load(open("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03.json"))
nz=len(wj["depth_m"]); C = np.memmap("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_c_mean.f32", dtype="<f4", mode="r", shape=(nz, wj["nlat"], wj["nlon"]))
SA = np.memmap("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_sa.f32", dtype="<f4", mode="r", shape=(nz, wj["nlat"], wj["nlon"]))
CT = np.memmap("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_ct.f32", dtype="<f4", mode="r", shape=(nz, wj["nlat"], wj["nlon"]))
mid_lo, mid_la = pts[100]
i = int(round((mid_la-wj["lat0"])/wj["step_deg"])); j = int(round((mid_lo-wj["lon0"])/wj["step_deg"]))
z = np.array(wj["depth_m"]); c = np.array(C[:,i,j], float); sa=np.array(SA[:,i,j],float); ct=np.array(CT[:,i,j],float)
v = np.isfinite(c); print("midpoint", round(mid_la,2), round(mid_lo,2), "valid levels", v.sum(), "deepest", z[v].max(), "c min %.1f at %.0f m" % (c[v].min(), z[v][np.argmin(c[v])]))
# extend below deepest valid level holding SA, CT; increase pressure
zd = z[v]; cd = c[v]; zext = np.arange(zd.max()+200, 5600, 200.0)
p = gsw.p_from_z(-zext, mid_la); cext = gsw.sound_speed(np.full_like(zext, sa[v][-1]), np.full_like(zext, ct[v][-1]), p)
zz = np.concatenate([zd, zext]); cc = np.concatenate([cd, cext])
print(len(zz), cc[-3:])
np.savez("handoff_profile.npz", z=zz, c=cc, mid=(mid_la, mid_lo), depth_med=float(np.median(dep)), ranges_km=dict(H01W=2198.1,H08S=3703.5,PC=2376.1), impact=(mlat,mlon))
