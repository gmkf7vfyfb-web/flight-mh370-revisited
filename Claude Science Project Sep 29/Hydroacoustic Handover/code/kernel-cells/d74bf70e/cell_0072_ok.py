B0,B1 = 492, 755; DEP = lambda y: (y-B0)/(B1-B0)*7000
mask_leg_bot = np.zeros((H,W),bool); mask_leg_bot[550:615, 560:730] = True
mag = (im[...,0]>200)&(im[...,1]<80)&(im[...,2]>150)   # magenta source marker
out=[]
for name,a in [("MH370",aB),("F35",aO)]:
    m = (a>=0.6) & ~mask_leg_bot & ~mag
    m[:B0+1]=False; m[B1:]=False; m[:,:X0+1]=False; m[:,X1:]=False
    for x in range(X0+2, X1-1):
        ys = np.nonzero(m[:,x])[0]
        if len(ys)==0: out.append((name,KM(x),np.nan,np.nan)); continue
        # split into vertical clusters
        cl = np.split(ys, np.where(np.diff(ys)>3)[0]+1)
        cen = [DEP(c.mean()) for c in cl]
        axis = depth = np.nan
        if len(cl)>=2: axis, depth = cen[0], cen[-1]
        elif cen[0] > 1400: depth = cen[0]
        else: axis = cen[0]
        out.append((name,KM(x),depth,axis))
bot = pd.DataFrame(out, columns=["path","range_km","water_depth_m","dsc_axis_depth_m"])
# a lone "axis" pick in the dashed band deeper than the bathymetry is impossible: drop
for p in ["MH370","F35"]:
    d = bot[bot.path==p]
    print(p, "depth picks", d.water_depth_m.notna().sum(), "axis picks", d.dsc_axis_depth_m.notna().sum(),
          "depth range", d.water_depth_m.min().round(), d.water_depth_m.max().round(),
          "axis range", d.dsc_axis_depth_m.min().round(), d.dsc_axis_depth_m.max().round())
# where does the seafloor rise above the channel axis?
for p in ["MH370","F35"]:
    d = bot[bot.path==p].copy(); d["axis_i"]=d.dsc_axis_depth_m.interpolate(limit_direction="both"); d["dep_i"]=d.water_depth_m.interpolate(limit_direction="both")
    blk = d[d.dep_i < d.axis_i + 500]
    print(p, "seafloor within 500 m of axis at km:", np.round(blk.range_km.values[::4]).astype(int)[:40])
