cd leg; python - <<'E'
s=open('cond_pred.py').read()
s=s.replace('OBS = {"T": 1.018, "C": 0.668};','OBS = {"T": 1.018, "C": 0.668}; OBS_MS = {"T": 0.1283, "C": 0.0689};   # peak excess (Pa) and max 1 s mean-square excess (Pa^2), digitised Fig 9c, 2-20 Hz\n')
s=s.replace('h = LV.station_levels(e_tr[m], tau[m], r / 1e3, "H01W", T, N, CV)[1e-3]; eta_req = 1e-3 * (OBS[br] / h["ppk"]) ** 2\n            for stn in STN:',
 'h = LV.station_levels(e_tr[m], tau[m], r / 1e3, "H01W", T, N, CV)[1e-3]\n            S_h = h["se"] / np.maximum(np.clip(tau[m], 0.05, 10), 1.0)\n            for anchor, eta_req in (("energy", 1e-3 * OBS_MS[br] / S_h), ("peak", 1e-3 * (OBS[br] / h["ppk"]) ** 2)):\n             for stn in STN:')
# indent the per-station block by one extra space
a,b=s.split('             for stn in STN:\n',1)
blk,rest=b.split('pd.DataFrame(res).to_json',1)
blk='\n'.join((' '+l if l.strip() else l) for l in blk.split('\n'))
s=a+'             for stn in STN:\n'+blk.rstrip(' ')+'pd.DataFrame(res).to_json'+rest
s=s.replace('rec = dict(D=d, branch=br, subset=subset, station=stn, ess=ess,','rec = dict(D=d, branch=br, subset=subset, anchor=anchor, station=stn, ess=ess, eta_req_q=wq(eta_req, wn),')
s=s.replace('cols = [c for c in ["D", "branch", "subset", "station",','cols = [c for c in ["D", "branch", "subset", "anchor", "station",')
open('cond_pred.py','w').write(s)
E
sed -n 38,62p cond_pred.py