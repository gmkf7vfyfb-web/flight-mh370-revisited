#!/usr/bin/env python3
"""Bundle pinned inputs, source, weighted samples and audit records."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 selected=[]
 for pattern in ['*.py','README.md','requirements.txt']:
  selected.extend(ROOT.glob(pattern))
 selected.append(ROOT/'src/engine.cpp')
 for name in ['inputs','reference']:
  selected.extend(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.so','.pyc'])
 selected.extend(p for p in (ROOT/'qa').glob('*') if p.suffix in ['.json','.npz'])
 selected.extend(p for p in OUT.glob('*') if p.is_file() and p.suffix in ['.json','.npz','.pdf','.png'] and p.name!='package_result.json')
 runs=['run_a','run_b','importance_a','importance_b','refined_a','refined_b','refined_pilot',
       'proposals_gn','proposals_final','proposals_refined']
 runs += [f'proposal_training_{i}' for i in range(4)]+[f'proposals_adapt_{i}' for i in range(1,5)]
 for name in runs:
  selected.extend(p for p in (OUT/name).glob('*') if p.suffix in ['.json','.npz'])
 selected=sorted(set(selected))
 manifest={'description':'Conditional IGOGU Bayesian trajectory analysis; weights and limitations in README/PDF',
           'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in selected]}
 mf=ROOT/'SOURCE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2)+'\n');selected.append(mf)
 target=OUT/'mh370_igogu_reproducible.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for p in selected:
   # zipfile.write follows the full weather input symlink, making this archive
   # self-contained rather than dependent on the original scratch directory.
   z.write(p,'mh370_igogu_conditional/'+str(p.relative_to(ROOT)))
 with zipfile.ZipFile(target) as z:
  bad=z.testzip()
  if bad:raise RuntimeError('Archive CRC failure: '+bad)
  assert z.getinfo('mh370_igogu_conditional/inputs/weather.bin').file_size==337328648
 print(json.dumps({'archive':str(target),'bytes':target.stat().st_size,'files':len(selected),'sha256':sha(target)}))

if __name__=='__main__':main()
