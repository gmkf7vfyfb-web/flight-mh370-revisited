import glob
cnt={}
for k in range(1,25):
    z=np.load(f'kh/out/rows/run-j-waypoints-seed-{k}.npz')
    par=z['parent'].astype(int)
    acc=(z['z2|T1.0']<36)|(z['z2|C1.0']<36)
    loc=z['in_strip']|z['in_X200']
    # rows' share of the conditional numerator under D0 T1.0
    cnt[k]=dict(stored=len(par), par_acc=len(np.unique(par[acc])), par_loc=len(np.unique(par[loc])), par_union=len(np.unique(par[acc|loc])), par_acc_strip=len(np.unique(par[acc|z['in_strip']])))
c=pd.DataFrame(cnt).T; print(c.describe().round(0).to_string()); print(list(z.keys())[:12])