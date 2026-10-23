import importlib; r_old=r; importlib.reload(W)
t0=time.time(); r=W.process(('run-j-waypoints',1,0.9982,24,EOF,CORE,'kh/rows_smoke')); print(time.time()-t0)
for k in [W.KEYS[0], W.KEYS[9]]:
  for rn in ['all','strip','X200','H400']:
    a,b=r_old['prior'][k][rn], r['prior'][k][rn]
    print(k[:12],rn, a['l1']-b['l1'], a['l2']-b['l2'], a['par2']-b['par2'], a['npar'], b['npar'], np.array(a['fam1'])-np.array(b['fam1']))
  print(r_old['acoustic'][k]['T1.0']['all']['l1']-r['acoustic'][k]['T1.0']['all']['l1'])