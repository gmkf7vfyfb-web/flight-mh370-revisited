import datetime as dt
def wq(v, ww, qs=(0.05,0.25,0.5,0.75,0.95)):
    m = np.isfinite(v) & np.isfinite(ww) & (ww>0)
    v2, w2 = v[m], ww[m]
    o = np.argsort(v2); v2, w2 = v2[o], w2[o]
    cw = np.cumsum(w2)/w2.sum()
    return [float(np.interp(q, cw, v2)) for q in qs]

# evidence-weighted posterior weights for key options
def post_w(opt):
    ll = Y[:, ci[f"loglik:{opt}"]] if opt!="none" else np.zeros(len(Y))
    ll = np.where(np.isfinite(ll), ll, -np.inf)
    lw = np.log(np.maximum(w,1e-300)) + ll
    lw -= lw.max()
    return np.exp(lw)

opts = ["none","r600/no-offset","r1200/no-offset","both/no-offset","both/startup-offset"]
P = {o: post_w(o) for o in opts}
for o in opts:
    pw = P[o]; print(f"{o:24s} ESS_rows={pw.sum()**2/np.sum(pw**2):12.1f}  n_pos={int((pw>0).sum())}")

print("\n--- t_onset_s (s after 00:11) ---")
for o in opts: print(f"{o:24s}", [round(x,1) for x in wq(Y[:,ci['t_onset_s']], P[o])])
print("min/max t_onset:", np.nanmin(Y[:,ci['t_onset_s']]), np.nanmax(Y[:,ci['t_onset_s']]))
print("\n--- t_takeover_s, t_realised_flameout_s, t_impact_s (prior wt) ---")
for c in ["t_takeover_s","t_realised_flameout_s","t_impact_s"]:
    print(f"{c:24s}", [round(x,1) for x in wq(Y[:,ci[c]], w)])
print("\n--- takeover_altitude_ft ---")
for o in opts: print(f"{o:24s}", [round(x) for x in wq(Y[:,ci['takeover_altitude_ft']], P[o])])
