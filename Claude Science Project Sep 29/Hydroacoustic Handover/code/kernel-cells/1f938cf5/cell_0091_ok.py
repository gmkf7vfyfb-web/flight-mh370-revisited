
md=md.replace("plus `run-j-joined-v2/J0011` and `J2241`, 21 seeds each).","plus `run-j-joined-v2/J0011` (24 seeds) and `J2241` (22 seeds), all seeds with impacts32.npy present at 18 Oct 2026).")
open('out/README.md','w').write(md)
import shutil
dst='repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/settling'
os.makedirs(dst,exist_ok=True)
for f in os.listdir('out'):
    if f.startswith('_'): continue
    shutil.copy(f'out/{f}',dst)
for f in ('settle_mc.py','extract_L.py'): shutil.copy(f,dst)
print(sorted(os.listdir(dst)), sum(os.path.getsize(os.path.join(dst,f)) for f in os.listdir(dst)))
