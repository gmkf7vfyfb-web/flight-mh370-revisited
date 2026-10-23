import hashlib,os
for k in 'ABCDEF':
    r=chart2(k); plt.close('all')
    p=f'cand/cand{k}_2_closeup_map.png'; print(k, os.path.getsize(p), r if not hasattr(r,'__len__') or len(str(r))<120 else '')