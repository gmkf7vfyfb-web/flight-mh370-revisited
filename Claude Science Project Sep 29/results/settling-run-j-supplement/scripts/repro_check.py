import numpy as np, json
A="/Users/pete/Downloads/mh370-exchange/settling/run-j/run-j-waypoints/rj_waypoints"; B="/Users/pete/Downloads/mh370-exchange/settling/run-j-supplement/ruleB-waypoints/rjs"
red=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz", mmap_mode="r")
TA=np.fromfile(A+"_impacts.f64","<f8").reshape(-1,14); TB=np.fromfile(B+"_impacts.f64","<f8").reshape(-1,14)
sB=np.load(B+"_source.npy"); tech=np.asarray(red["technique"])[sB[:,2]]; seedB=np.asarray(red["seed"])[sB[:,2]]
kA={ (int(r[13]),int(r[10]),r[0],r[1]):i for i,r in enumerate(TA)}
pairs=[(kA[k],j) for j,k in enumerate(zip(seedB.astype(int),TB[:,10].astype(int),TB[:,0],TB[:,1])) if tech[j]==0 and k in kA]
print("production rows in new table", int((tech==0).sum()), "matched to run J table", len(pairs))
EA=np.memmap(A+"_elements.f64","<f8","r").reshape(-1,8); EB=np.memmap(B+"_elements.f64","<f8","r").reshape(-1,8)
def els(E,rows):
    key=E[:,0].astype(np.int64)*(1<<20)+E[:,1].astype(np.int64); o=np.argsort(key,kind="stable"); return key[o], o
kAe,oA=els(EA,None); kBe,oB=els(EB,None)
rng=np.random.default_rng(1); sel=[pairs[i] for i in rng.choice(len(pairs),min(2000,len(pairs)),replace=False)]
same=0; diff=0; colsdiff=0
for ia,ib in sel:
    if np.any(TA[ia,:12]!=TB[ib,:12]): colsdiff+=1
    a=oA[slice(*np.searchsorted(kAe,[ia*(1<<20),ia*(1<<20)+1]))]; b=oB[slice(*np.searchsorted(kBe,[ib*(1<<20),ib*(1<<20)+1]))]
    xa=np.asarray(EA[a][:,2:]); xb=np.asarray(EB[b][:,2:])
    if xa.shape==xb.shape and np.array_equal(np.nan_to_num(xa),np.nan_to_num(xb)): same+=1
    else: diff+=1
print("sampled", len(sel), "impact columns differ", colsdiff, "draw-0 element sets identical", same, "different", diff)
