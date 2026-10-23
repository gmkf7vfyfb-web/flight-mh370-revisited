
A = raw.reshape(90,140,nz); SAa = np.fromfile("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_sa.f32", dtype="<f4").reshape(90,140,nz); CTa = np.fromfile("/Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/woa23_95A4_m03_ct.f32", dtype="<f4").reshape(90,140,nz)
c = A[i,j].astype(float); sa = SAa[i,j].astype(float); ct = CTa[i,j].astype(float); v = np.isfinite(c)
print("valid", v.sum(), "deepest valid", z[v].max(), "axis c_min %.1f at %.0f m" % (c[v].min(), z[v][np.argmin(c[v])]))
zd=z[v]; cd=c[v]
zext = np.arange(zd.max()+100, 5700, 100.0); p = gsw.p_from_z(-zext, mid_la)
cext = gsw.sound_speed(np.full_like(zext, sa[v][-1]), np.full_like(zext, ct[v][-1]), p)
zz = np.concatenate([zd, zext]); cc = np.concatenate([cd, cext]); print(np.round(cc[-6:],1), zz[-1])
np.savez("handoff_profile.npz", z=zz, c=cc, mid=(mid_la, mid_lo), depth_med=float(np.median(dep)), impact=(mlat,mlon))
json.dump(dict(impact_lat=mlat, impact_lon=mlon, mid_lat=mid_la, mid_lon=mid_lo, depth_med_m=float(np.median(dep)), depth_min_m=float(dep.min()), ranges_km=dict(H01W=2198.1,H08S=3703.5,PC3376=2376.1), woa="woa23_95A4_m03 (March), layout (nlat,nlon,nz)"), open("handoff_geom.json","w"), indent=1)
