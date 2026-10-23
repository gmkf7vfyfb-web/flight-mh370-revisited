ps = Y[:,ci["latent:profile_shape"]]
print("profile_shape:", dict(zip(*[a.tolist() for a in np.unique(ps, return_counts=True)])))
fam3 = (fam4==3)
t0 = Y[:,ci["t_onset_s"]]
for lab,msk in [("ALL",np.ones(len(Y),bool)),("family4=3 (deliberate)",fam3),("fam4=1",fam4==1),("fam4=2",fam4==2)]:
    for o in ["none","both/no-offset"]:
        pw = P[o]*msk
        if pw.sum()==0: continue
        at = (t0 < 659.0+30.0)
        print(f"{lab:24s} {o:16s} wt-share={pw.sum()/P[o].sum():.4f}  P(onset within 30s of 00:11 boundary)={pw[at].sum()/pw.sum():.4f}  onset q05/50={wq(t0,pw)[0]:.0f}/{wq(t0,pw)[2]:.0f}")

print("\nbank point mass at 0 (weighted, option none):",
      float(P['none'][np.abs(Y[:,ci['latent:impact_bank_deg']])<1e-6].sum()/P['none'].sum()))
print("|bank| quantiles (none):", [round(x,1) for x in wq(np.abs(Y[:,ci['latent:impact_bank_deg']]),P['none'])])
print("heading spread (none) q05..q95:", [round(x,1) for x in wq(Y[:,ci['latent:impact_heading_deg']],P['none'])])

# parent-level degeneracy
par = Y[:,ci["parent"]]
for o in ["none","r600/no-offset","both/no-offset"]:
    pw = P[o]
    agg = pd.Series(pw).groupby(par).sum().values
    agg = agg/agg.sum()
    print(f"{o:18s} parents>0={int((agg>0).sum()):6d}  ESS_parents={1/np.sum(agg**2):10.1f}  top1={agg.max():.4f} top10={np.sort(agg)[-10:].sum():.4f}")

# tau sidecar
tz = np.load(f"{S}/tau90_v1.npz")
print("\ntau90_v1.npz keys:", list(tz.keys()), {k: (tz[k].shape, str(tz[k].dtype)) for k in tz.keys()})
