
def scaled(o,f,rot_deg=0.0,label=''):
    c,s=np.cos(np.radians(rot_deg)),np.sin(np.radians(rot_deg))
    return sm.Ocean(label,o.lat,o.lon,o.tt,o.z,f*(c*o.U-s*o.V),f*(s*o.U+c*o.V),o.rho_z,o.rho_vals,o.model_bottom)
sens_o=[]
for lab,f,rot in [('GLORYS12V1 baseline',1,0),('current x0.5',0.5,0),('current x1.5',1.5,0),('current x2',2.0,0),('current rotated +90 deg',1,90),('current rotated 180 deg',1,180)]:
    oc=scaled(glorys,f,rot,lab)
    for cls in CLASSES:
        o=sm.settle(np.full(20000,HX[0]),np.full(20000,HX[1]),T0+rowsH2.t_impact_s.values,rowsH2.vh.values,tr2,fam2,cls,oc,wind,np.random.default_rng(7))
        dx,dy=sm.offsets_km(HX[0],HX[1],o['lat'],o['lon']); D=np.hypot(dx,dy)
        sens_o.append(dict(ocean=lab,cls=cls,p50=np.nanpercentile(D,50),p90=np.nanpercentile(D,90),p99=np.nanpercentile(D,99),mean_dx=np.nanmean(dx),mean_dy=np.nanmean(dy)))
SO=pd.DataFrame(sens_o); print(SO.round(3).to_string())
