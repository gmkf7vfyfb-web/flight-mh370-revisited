cat > extract_box.py <<'EOF'
import numpy as np, sys, os
from multiprocessing import Pool
R=os.path.expanduser('~/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints')
cols=open(f'{R}/seed-1/COLUMNS.txt').read().split()
ix={c:i for i,c in enumerate(cols)}
want=['parent','weight','t_impact_s','latitude_deg','longitude_deg','arc_distance_nm','t_realised_flameout_s','latent:onset_mechanism','family4_code',
      'loglik:r600/no-offset','loglik:both/no-offset','loglik:both/startup-offset','latent:impact_heading_deg','latent:circuit_begun','latent:turns_terminal_begun']
def job(k):
    a=np.load(f'{R}/seed-{k}/impacts32.npy',mmap_mode='r'); p=np.load(f'{R}/seed-{k}/parents32.npy')
    out=[]; wsum=None
    par=a[:,ix['parent']] if False else None
    # within-parent normalisation needs sums over all rows of each parent
    n=a.shape[0]; P=p.shape[0]; ws=np.zeros(P)
    sel=[]
    for s in range(0,n,400000):
        b=np.asarray(a[s:s+400000])
        pid=b[:,ix['parent']].astype(np.int64); np.add.at(ws,pid,b[:,ix['weight']].astype(np.float64))
        la,lo=b[:,ix['latitude_deg']],b[:,ix['longitude_deg']]
        m=(la>-29)&(la<-22)&(lo>97)&(lo<105)
        if m.any(): sel.append(b[m][:,[ix[c] for c in want]])
    S=np.concatenate(sel) if sel else np.zeros((0,len(want)),np.float32)
    pid=S[:,0].astype(np.int64)
    whand=p[pid,1].astype(np.float64); wrow=S[:,1]/ws[pid]
    return k,S,whand,wrow,n,float(p[:,1].sum())
if __name__=='__main__':
    p1=np.load(f'{R}/seed-1/parents32.npy'); print('parents32',p1.shape,p1.dtype,p1[:3])
    with Pool(6) as pool: res=pool.map(job,range(1,25))
    S=np.concatenate([r[1] for r in res]); seed=np.concatenate([np.full(len(r[1]),r[0]) for r in res])
    wh=np.concatenate([r[2]/r[5] for r in res]); wr=np.concatenate([r[3] for r in res])
    np.savez('kadri_box.npz',S=S,seed=seed,w_handoff_norm=wh,w_row_norm=wr,cols=np.array(want),nrows=np.array([r[4] for r in res]))
    print('rows in box',len(S),'of',sum(r[4] for r in res))
    w=wh*wr/24; print('approx posterior share in box (00:19 held out, eq per seed):',w.sum())
EOF
time python extract_box.py