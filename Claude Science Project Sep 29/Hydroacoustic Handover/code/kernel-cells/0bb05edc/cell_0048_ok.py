
import os, re, json, subprocess, collections
# --- Downloads: all PDFs outside obvious run-output trees
pdfs=[]
for root,dirs,files in os.walk('/Users/pete/Downloads'):
    # prune big data trees
    dirs[:] = [d for d in dirs if d not in ('node_modules','.git','run-i','run-j','core','end-of-flight','gebco','woa23','imos') and not d.startswith('next-')]
    for f in files:
        if f.lower().endswith('.pdf'):
            p=os.path.join(root,f)
            try: sz=os.path.getsize(p)
            except: sz=0
            pdfs.append((p,sz))
print('Downloads PDFs (pruned):', len(pdfs))
by_dir=collections.Counter(os.path.dirname(p).replace('/Users/pete/Downloads/','').split('/')[0] for p,_ in pdfs)
print(by_dir.most_common(15))
json.dump(pdfs, open('handoff/downloads_pdfs.json','w'))
# --- repo: PDF/txt names across main branches
out = subprocess.run(['git','-C','/Users/pete/Downloads/flight-mh370-revisited','ls-tree','-r','--name-only','origin/claude-science-sep29'],capture_output=True,text=True).stdout.split('\n')
rp=[x for x in out if x.lower().endswith(('.pdf',))]
print('repo PDFs on sep29:', len(rp))
json.dump(rp, open('handoff/repo_pdfs.json','w'))
dirs=collections.Counter('/'.join(x.split('/')[:3]) for x in rp); print(dirs.most_common(12))
