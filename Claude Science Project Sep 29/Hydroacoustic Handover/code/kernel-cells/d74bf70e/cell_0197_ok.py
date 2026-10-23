fx=lambda x:10**((x-134.5)/148.8); py=lambda y:8+(287-y)/15.1
pts=[]
for x in range(137,536):
    ys=np.where(cr[206:285,x]<130)[0]+206
    if len(ys): pts.append((fx(x), 10*py(np.median(ys)), 10*py(ys.min()), 10*py(ys.max())))
psd=pd.DataFrame(pts,columns=["f_hz","psd_db_re_1pa2hz","upper","lower"])
band=[]
for fc in [5,6.3,8,10,12.5,16,20,25,31.5,40,50,63]:
    a,b=fc/2**(1/6),fc*2**(1/6); v=psd[(psd.f_hz>=a)&(psd.f_hz<b)].psd_db_re_1pa2hz
    band.append((fc, v.mean() if len(v) else np.nan, len(v)))
band=pd.DataFrame(band,columns=["fc_hz","psd_db","n"]).set_index("fc_hz")
print(band.round(1).T.to_string())
# Exploratory hypothesis H-flat: obs TL computed against a flat source level, so a spectrum-corrected obs TL is obs - (PSD(f)-PSD_ref).
for st in ["H01W","H08S"]:
    o,h=rows[st]; f=[x for x in o.index if np.isfinite(o[x])]
    ref=band.psd_db[f].max()
    corr=o[f]-(band.psd_db[f]-ref)
    r=(h[f]-corr); r0=h[f]-o[f]
    print(st, "residual median/rms as registered", round(float(np.median(r0)),2), round(float(np.sqrt(np.mean(r0**2))),2),
          "| H-flat corrected: median", round(float(np.median(r)),2), "rms", round(float(np.sqrt(np.mean(r**2))),2), "| slope dB/oct", round(np.polyfit(np.log2(f), r.values,1)[0],2))