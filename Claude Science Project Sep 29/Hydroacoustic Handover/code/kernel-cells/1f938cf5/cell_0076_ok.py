
for br in ('T','C'):
    o=RES[f'kadri_{br}']['recorder-detached']; _,ia_,tid=sm.seabed(o['lat'],o['lon'],with_src=True)
    print(br,'AusSeabed share',ia_.mean().round(3),'GEBCO TID shares',{int(k):round(float(v),3) for k,v in zip(*np.unique(tid,return_counts=True)) if v/len(tid)>0.005} )
    m=RES[f'kadri_{br}']['meta']; print(' v-dr check', np.percentile(m['dr'],[0,50,100]).round(1))
o=RES['runJ_L']['recorder-detached']; _,ia_,_=sm.seabed(o['lat'],o['lon'],with_src=True); print('runJ_L AusSeabed share',ia_.mean().round(3))
