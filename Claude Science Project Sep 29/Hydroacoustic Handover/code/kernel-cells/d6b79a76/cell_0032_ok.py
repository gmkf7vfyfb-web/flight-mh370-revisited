importlib.reload(W); del r_old
J='/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-joined-v2'
t0=time.time(); rj=W.process_joined((1,21,J,CORE,'kh/rows_smoke')); print(time.time()-t0)
print(rj['lnZ_seed'], rj['rows'], rj['stored_rows'], rj['n_S1_rows'], rj['n_S2_rows'])
print(rj['geom_rows']); print(rj['min_z2'])
k='D0 joined V2'; P=rj['prior'][k]; print({rn:round(np.exp(v['l1']-P['all']['l1']),5) for rn,v in P.items()})
print({vn:v['all']['l1']-P['all']['l1'] for vn,v in rj['acoustic'][k].items()})
print(open(J+'/summary/joined-s1.txt').read()[:600])