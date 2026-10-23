rows={}
for st in ["H01W","H08S"]:
    o=pd.read_csv(A+f"observed_bands_{st}.csv").set_index("fc_hz").obs_tl_db
    h=m[(m.station==st)&(m.src_depth_m==10)&(m.bottom=="hard")].set_index("fc_hz").tl_db
    rows[st]=(o,h)
both=[f for f in rows["H01W"][0].index if np.isfinite(rows["H01W"][0][f]) and np.isfinite(rows["H08S"][0][f])]
r1=(rows["H01W"][1]-rows["H01W"][0])[both]; r2=(rows["H08S"][1]-rows["H08S"][0])[both]
print("common bands", both)
print("corr of residuals across stations", round(np.corrcoef(r1,r2)[0,1],3))
cm=(r1+r2)/2; print("common-mode residual", cm.round(1).to_dict())
print("residual after removing common mode: rms H01W", round(np.sqrt(np.mean((r1-cm)**2)),2), "H08S", round(np.sqrt(np.mean((r2-cm)**2)),2))
dobs=(rows["H08S"][0]-rows["H01W"][0])[both]; dmod=(rows["H08S"][1]-rows["H01W"][1])[both]
dres=dmod-dobs
print("obs H08S-H01W", dobs.round(1).to_dict()); print("model H08S-H01W", dmod.round(1).to_dict())
print("EXPLORATORY differential residual: median", round(float(np.median(dres)),2), "rms", round(float(np.sqrt(np.mean(dres**2))),2))
# slope of common-mode residual per octave
lf=np.log2(np.array(both)); b=np.polyfit(lf, cm.values,1); print("common-mode slope dB/octave", round(b[0],2))