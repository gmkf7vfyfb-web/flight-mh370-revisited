import sys, numpy as np, json
sys.path.insert(0, "tlchain/tl-chain-2026-10-27")
from tlchain import paths as P
sys.path.insert(0, ".")
from build_sections_now import arc_points
out = []
for lat, lon in arc_points([-20.0,-25.0,-30.0,-35.0,-40.0]):
    z, c = P.sound_speed_profile(lat, lon, "A5B4", 3)
    D = float(-P.elevation(lat, lon, "med3")[0])
    cb = float(np.interp(D, z, c)); cs = float(c[0]); m = z < 3000; ia = np.argmin(c[m])
    th = float(np.degrees(np.arccos(cs/cb))) if cb > cs else 0.0
    zz = z[z<=D]; cc = c[z<=D]
    out.append(dict(lat=lat, lon=lon, water_depth_m=D, c_surface=cs, c_axis=float(c[m][ia]), z_axis=float(z[m][ia]), c_bottom=cb,
                    theta_max_deg=th, z=zz.tolist(), c=cc.tolist()))
json.dump(out, open("arc_ssp.json","w"))
for o in out: print({k: (round(v,2) if isinstance(v,float) else v) for k,v in o.items() if k not in ('z','c')})
