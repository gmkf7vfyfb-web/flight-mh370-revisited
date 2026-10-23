m=json.load(open('kh/tgt/smoke-out/run.json')); cols={c:i for i,c in enumerate(m['impact_columns'])}
Xs=np.load('kh/tgt/smoke-out/bto-bfo/seed-1001/impacts.npy'); print(Xs.shape)
sel=json.load(open('kh/tgt/smokeRT/bto-bfo/seed-1001/selection.json'))['parents']
pt=Xs[:,cols['parent']].astype(int); wt=Xs[:,cols['weight']]
st=np.bincount(pt,wt,40)
P32=np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/parents32.npy')
sp=P32[sel,1]; H=np.load('/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/seed-1/handoff-m0011/handoff.npy')
hw=H[sel,0]*np.exp(H[sel,13])
print(np.round(st/sp,3)); print(np.round(sp/hw,3)[:10], np.round(st/hw,3)[:10]); print(st.sum()/sp.sum())
print(m['replicates'][0]['terminal']['children'], m['config']['terminal'].get('children') if 'terminal' in m['config'] else None)